#!/usr/bin/env python3
# Auto-bootstrap: byter automatiskt till venv-Python om nödvändigt.
import sys, os as _os
from pathlib import Path as _Path
_VENV_DIR = _Path.home() / ".config/superintelligent/outlook-bridge/venv"
_VENV_PY = _VENV_DIR / "bin/python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    _os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)
"""
review_draft.py — Hämta ett draft från Graph och visa fullständig review.

Usage:
    python review_draft.py --id D42

Hämtar aktuellt innehåll från Microsoft Graph, beräknar review_hash
och uppdaterar lokal state. Visar mottagare, ämne, brödtext och bilagor.
Anger exakt vilket OK-kommando som krävs för att skicka.

Skickar aldrig. Ändrar aldrig draften.

Beroenden: pip install msal keyring requests
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _graph_client import GraphClient
from _state import DraftState
from _validation import _expected_command

CONFIG_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "config.json"
STATE_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "drafts.json"

# Brödtextens maximala visningslängd i review (tecken)
BODY_PREVIEW_MAX = 3000


def compute_review_hash(message: dict) -> str:
    """
    Beräknar SHA256-fingeravtryck av draft-innehållet.
    Hashen kan inte reverseras till klartext.
    Lagras i state för att detektera ändringar mellan review och send.
    """
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


def format_recipients(recipients: list) -> str:
    """Formaterar mottagarlista för visning. Döljer aldrig någon adress."""
    if not recipients:
        return "—"
    lines = []
    for i, r in enumerate(recipients):
        addr = r["emailAddress"]["address"]
        name = r["emailAddress"].get("name", "")
        display = f"{name} <{addr}>" if name and name != addr else addr
        if i == 0:
            lines.append(display)
        else:
            # Indentera ytterligare rader för att motsvara "Till:      "
            lines.append("           " + display)
    return "\n".join(lines)


def format_body(body: str, content_type: str) -> str:
    """Returnerar brödtext för visning. Trunkerar om längre än BODY_PREVIEW_MAX."""
    if content_type.lower() == "html":
        # Enkel HTML-strippning för terminal-visning
        import re
        text = re.sub(r"<[^>]+>", "", body)
        text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    else:
        text = body

    text = text.strip()
    if len(text) > BODY_PREVIEW_MAX:
        return text[:BODY_PREVIEW_MAX] + f"\n\n[... {len(text) - BODY_PREVIEW_MAX} tecken till ...]"
    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Visa fullständig review av ett draft innan sending."
    )
    parser.add_argument("--id", required=True, help="Kort draft-ID, t.ex. D42")
    args = parser.parse_args()

    draft_id = args.id.upper()

    # Kontrollera att draft finns i state
    state = DraftState(STATE_PATH)
    state_entry = state.get_draft(draft_id)
    if not state_entry:
        print(
            f"FEL: Draft {draft_id} finns inte i lokal state.\n"
            f"Lista aktiva drafts: python scripts/outlook/list_drafts.py",
            file=sys.stderr,
        )
        sys.exit(1)

    graph_id = state_entry["graph_message_id"]

    # Hämta aktuellt innehåll från Graph
    client = GraphClient(CONFIG_PATH)
    try:
        message = client.get(f"/me/messages/{graph_id}")
    except Exception as exc:
        print(f"FEL vid hämtning av draft från Graph: {exc}", file=sys.stderr)
        sys.exit(1)

    # Verifiera att det faktiskt är ett draft
    if not message.get("isDraft", False):
        print(
            f"VARNING: Meddelandet {draft_id} har redan skickats eller är inte ett draft.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Extrahera fält
    to = message.get("toRecipients", [])
    cc = message.get("ccRecipients", [])
    bcc = message.get("bccRecipients", [])
    subject = message.get("subject", "(Inget ämne)")
    body_obj = message.get("body", {})
    body_content = body_obj.get("content", "")
    body_type = body_obj.get("contentType", "text")
    has_attachment = message.get("hasAttachments", False)

    recipient_count = len(to) + len(cc) + len(bcc)

    # Beräkna review_hash och uppdatera state
    review_hash = compute_review_hash(message)
    state.mark_reviewed(
        draft_id=draft_id,
        review_hash=review_hash,
        has_attachment=has_attachment,
        recipient_count=recipient_count,
    )

    # Bygg och skriv ut review
    sep = "─" * 60
    print(f"\n{sep}")
    print(f"📧 Draft {draft_id} — Redo för granskning")
    print(sep)
    print()
    print(f"Till:      {format_recipients(to)}")
    print(f"CC:        {format_recipients(cc)}")
    print(f"BCC:       {format_recipients(bcc)}")
    print(f"Ämne:      {subject}")

    if has_attachment:
        print(f"Bilagor:   [Bilaga detekterad — v0.1 visar ej filnamn]")
    else:
        print(f"Bilagor:   Inga")

    print()
    print(sep)
    print(format_body(body_content, body_type))
    print(sep)
    print()
    print(
        f"Mottagare totalt: {recipient_count}"
        f"  (Till: {len(to)} · CC: {len(cc)} · BCC: {len(bcc)})"
    )
    print(f"Bilagor: {'Ja' if has_attachment else 'Nej'}")
    print()

    expected = _expected_command(draft_id, has_attachment, recipient_count)
    print(f"För att skicka: {expected}")
    print(sep)
    print()

    # Skicka Telegram-notis om konfigurerat (non-blocking — misslyckas tyst)
    try:
        from telegram_notify import notify_draft_ready
        to_summary = to[0]["emailAddress"]["address"] if to else "—"
        if len(to) + len(cc) + len(bcc) > 1:
            extra = recipient_count - 1
            to_summary += f" (+{extra})"
        notify_draft_ready(
            draft_id=draft_id,
            subject=subject,
            to_summary=to_summary,
            recipient_count=recipient_count,
            has_attachment=has_attachment,
        )
    except Exception:
        pass  # Telegram-notis är aldrig blocking


if __name__ == "__main__":
    main()
