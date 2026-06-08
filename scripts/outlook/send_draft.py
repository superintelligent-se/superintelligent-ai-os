#!/usr/bin/env python3
# Auto-bootstrap: byter automatiskt till venv-Python om nödvändigt.
import sys, os as _os
from pathlib import Path as _Path
_VENV_DIR = _Path.home() / ".config/superintelligent/outlook-bridge/venv"
_VENV_PY = _VENV_DIR / "bin/python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    _os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)
"""
send_draft.py — Skicka ett Outlook-draft efter strikt OK-validering.

Usage:
    python send_draft.py "OK D42"
    python send_draft.py "OK D42 B"
    python send_draft.py "OK D42 FM"
    python send_draft.py "OK D42 B FM"

Valideringsordning (alla steg måste passera):
  1. Parsa OK-kommandot (strikt grammar)
  2. Kontrollera att draft-ID finns i lokal state
  3. Kontrollera att review har visats (reviewed_at är satt)
  4. Re-hämta draft från Microsoft Graph
  5. Verifiera review_hash (detekterar ändringar sedan review)
  6. Räkna mottagare på nytt från Graph-svaret
  7. Kontrollera hasAttachments på nytt från Graph-svaret
  8. Validera tokens (B om bilaga, FM om >3 mottagare)
  9. Skicka: POST /me/messages/{id}/send

Loggar åtgärder till ~/.config/superintelligent/outlook-bridge/activity.log.
Lagrar aldrig mejlinnehåll i logg eller repo.

Beroenden: pip install msal keyring requests
"""

import hashlib
import json
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _graph_client import GraphClient
from _state import DraftState
from _validation import parse_ok_command, validate_tokens

CONFIG_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "config.json"
STATE_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "drafts.json"
LOG_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "activity.log"


# ------------------------------------------------------------------ #
#  Loggning — aldrig mejlinnehåll                                     #
# ------------------------------------------------------------------ #

def setup_logger() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("outlook-bridge")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter('{"ts": "%(asctime)s", %(message)s}', datefmt="%Y-%m-%dT%H:%M:%SZ")
        )
        logger.addHandler(handler)
    return logger


def log_action(logger: logging.Logger, action: str, draft_id: str, **kwargs) -> None:
    """Loggar en åtgärd. Lagrar aldrig mejlinnehåll."""
    parts = [f'"action": "{action}", "draft_id": "{draft_id}"']
    for k, v in kwargs.items():
        if isinstance(v, bool):
            parts.append(f'"{k}": {str(v).lower()}')
        elif isinstance(v, int):
            parts.append(f'"{k}": {v}')
        else:
            parts.append(f'"{k}": "{v}"')
    logger.info(", ".join(parts))


# ------------------------------------------------------------------ #
#  review_hash-beräkning (måste matcha review_draft.py)               #
# ------------------------------------------------------------------ #

def compute_review_hash(message: dict) -> str:
    to = sorted(
        r["emailAddress"]["address"].lower()
        for r in message.get("toRecipients", [])
    )
    cc = sorted(
        r["emailAddress"]["address"].lower()
        for r in message.get("ccRecipients", [])
    )
    bcc = sorted(
        r["emailAddress"]["address"].lower()
        for r in message.get("bccRecipients", [])
    )
    canonical = json.dumps(
        {
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "subject": message.get("subject", ""),
            "body": message.get("body", {}).get("content", ""),
            "has_attachments": message.get("hasAttachments", False),
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ #
#  Huvudlogik                                                          #
# ------------------------------------------------------------------ #

def abort(msg: str, logger: logging.Logger = None, draft_id: str = None, reason: str = None) -> None:
    """Skriv felmeddelande och avsluta. Logga om möjligt."""
    print(f"\nFEL: {msg}\n", file=sys.stderr)
    if logger and draft_id:
        log_action(logger, "send_rejected", draft_id, reason=reason or msg[:60])
    sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python send_draft.py \"OK D42\"\n"
            "       python send_draft.py \"OK D42 B\"\n"
            "       python send_draft.py \"OK D42 FM\"\n"
            "       python send_draft.py \"OK D42 B FM\"",
            file=sys.stderr,
        )
        sys.exit(1)

    ok_command = sys.argv[1]
    logger = setup_logger()

    # ── Steg 1: Parsa OK-kommandot ────────────────────────────────── #
    is_valid, draft_id, tokens, error = parse_ok_command(ok_command)
    if not is_valid:
        abort(error, logger=logger, draft_id="?", reason="invalid_command")

    log_action(
        logger, "send_attempted", draft_id,
        tokens=" ".join(sorted(tokens)) if tokens else "none",
    )

    # ── Steg 2: Kontrollera att draft-ID finns i state ───────────── #
    state = DraftState(STATE_PATH)
    state_entry = state.get_draft(draft_id)
    if not state_entry:
        active = [d["draft_id"] for d in state.list_active()]
        hint = f"Aktiva drafts: {', '.join(active)}" if active else "Inga aktiva drafts."
        abort(
            f"Inget aktivt draft med ID {draft_id}. {hint}",
            logger=logger, draft_id=draft_id, reason="draft_not_found",
        )

    # ── Steg 3: Kontrollera att review har visats ────────────────── #
    if not state_entry.get("reviewed_at") or not state_entry.get("review_hash"):
        abort(
            f"Review har inte visats för {draft_id}.\n"
            f"Kör först: python scripts/outlook/review_draft.py --id {draft_id}",
            logger=logger, draft_id=draft_id, reason="review_not_shown",
        )

    graph_id = state_entry["graph_message_id"]

    # ── Steg 4: Re-hämta draft från Graph ────────────────────────── #
    client = GraphClient(CONFIG_PATH)
    try:
        message = client.get(f"/me/messages/{graph_id}")
    except Exception as exc:
        abort(
            f"Kunde inte hämta draft från Graph: {exc}",
            logger=logger, draft_id=draft_id, reason="graph_fetch_failed",
        )

    # Verifiera att det är ett draft (inte redan skickat)
    if not message.get("isDraft", False):
        abort(
            f"Meddelandet {draft_id} har redan skickats eller är inte ett draft.",
            logger=logger, draft_id=draft_id, reason="not_a_draft",
        )

    # ── Steg 5: Verifiera review_hash ────────────────────────────── #
    current_hash = compute_review_hash(message)
    stored_hash = state_entry["review_hash"]
    if current_hash != stored_hash:
        abort(
            f"Draften har ändrats sedan senaste review.\n"
            f"Kör review på nytt: python scripts/outlook/review_draft.py --id {draft_id}",
            logger=logger, draft_id=draft_id, reason="hash_mismatch",
        )

    # ── Steg 6 & 7: Räkna mottagare och kontrollera bilagor på nytt ─ #
    to = message.get("toRecipients", [])
    cc = message.get("ccRecipients", [])
    bcc = message.get("bccRecipients", [])
    recipient_count = len(to) + len(cc) + len(bcc)
    has_attachment = message.get("hasAttachments", False)

    # ── Steg 8: Validera tokens ───────────────────────────────────── #
    token_valid, token_error = validate_tokens(
        draft_id=draft_id,
        tokens=tokens,
        has_attachment=has_attachment,
        recipient_count=recipient_count,
    )
    if not token_valid:
        abort(token_error, logger=logger, draft_id=draft_id, reason="missing_tokens")

    # ── Steg 9: Skicka ───────────────────────────────────────────── #
    try:
        client.post_empty(f"/me/messages/{graph_id}/send")
    except Exception as exc:
        abort(
            f"Graph-sändning misslyckades: {exc}",
            logger=logger, draft_id=draft_id, reason="graph_send_failed",
        )

    log_action(
        logger, "send_completed", draft_id,
        recipient_count=recipient_count,
        has_attachment=has_attachment,
    )

    print(f"✓ Mejl skickat ({draft_id})")


if __name__ == "__main__":
    main()
