#!/usr/bin/env python3
"""
telegram_notify.py (sandbox) — Skickar draft-notis till Telegram.

Kräver inga externa beroenden — bara Python stdlib (urllib, json, pathlib).
Credentials läses från .secret/credentials.json i repo-roten (gitignorerat).

Meddelandeformat:
  🔴 NIVÅ 1 — AKUT
  ──────────────────
  📨 Från: avsändare@example.com
  Ämne: Originalämne

  Sammanfattning av originalmejlet (2-3 meningar)...
  ──────────────────
  📝 Draft D4

  Hela drafttexten här...
  ──────────────────
  Skicka: /okD4

Usage:
    python3 scripts/outlook/sandbox/telegram_notify.py \\
        --id D4 \\
        --priority "NIVÅ 1 — AKUT" \\
        --original-from "anna@example.com" \\
        --original-subject "Originalämne" \\
        --original-summary "2-3 meningar ur originalmejlet." \\
        --draft-subject "Sv: Originalämne" \\
        --draft-body "Hej,\\n\\nSvar här.\\n\\nMvh Thomas" \\
        --recipient-count 1
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

TELEGRAM_API  = "https://api.telegram.org"
MAX_MSG_CHARS = 4000  # Telegram-gräns är 4096, lite marginal

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT  = SCRIPT_DIR.parent.parent.parent  # sandbox/ -> outlook/ -> scripts/ -> repo root
CREDS_FILE = REPO_ROOT / ".secret" / "credentials.json"


# ── Credentials ───────────────────────────────────────────────────────────────

def load_creds() -> dict:
    if not CREDS_FILE.exists():
        print(
            f"FEL: {CREDS_FILE} saknas.\n"
            "Kör: bash scripts/outlook/setup_sandbox_credentials.sh",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.loads(CREDS_FILE.read_text())


# ── Telegram ──────────────────────────────────────────────────────────────────

def send_message(token: str, chat_id: str, text: str) -> bool:
    url  = f"{TELEGRAM_API}/bot{token}/sendMessage"
    data = json.dumps({
        "chat_id": chat_id, "text": text, "parse_mode": "HTML"
    }).encode()
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as exc:
        print(f"VARNING: Telegram-anrop misslyckades: {exc}", file=sys.stderr)
        return False


# ── Meddelandeformat ──────────────────────────────────────────────────────────

def priority_emoji(priority: str) -> str:
    p = priority.upper()
    if "1" in p or "AKUT" in p:
        return "🔴"
    if "2" in p:
        return "🟡"
    return "🔵"


def build_ok_command(draft_id: str, has_attachment: bool, recipient_count: int) -> str:
    cmd = f"/ok{draft_id}"
    if has_attachment:
        cmd += "B"
    if recipient_count > 3:
        cmd += "FM"
    return cmd


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 3] + "..."


def build_message(
    draft_id:         str,
    priority:         str,
    original_from:    str,
    original_subject: str,
    original_summary: str,
    draft_subject:    str,
    draft_body:       str,
    recipient_count:  int,
    has_attachment:   bool,
) -> str:
    SEP = "━━━━━━━━━━━━━━━━━━━━━"
    ok_cmd = build_ok_command(draft_id, has_attachment, recipient_count)

    warnings = []
    if has_attachment:   warnings.append("📎 Bilaga")
    if recipient_count > 3: warnings.append(f"⚠️ {recipient_count} mottagare")
    warning_line = "  ·  ".join(warnings) if warnings else ""

    parts = [
        f"{priority_emoji(priority)} <b>{priority}</b>",
        SEP,
        f"📨 <b>Från:</b> {original_from}",
        f"<b>Ämne:</b> {original_subject}",
        "",
        original_summary.strip(),
        SEP,
        f"📝 <b>Draft {draft_id}</b>",
        f"<b>{draft_subject}</b>",
        "",
        draft_body.strip(),
    ]

    if warning_line:
        parts += ["", warning_line]

    parts += [
        SEP,
        f"Skicka: <code>{ok_cmd}</code>",
    ]

    msg = "\n".join(parts)

    # Säkerhetstrunkering om mejlet är extremt långt
    if len(msg) > MAX_MSG_CHARS:
        # Trunkera draft_body och bygg om
        overhead   = len(msg) - len(draft_body)
        max_body   = MAX_MSG_CHARS - overhead - 6
        truncated  = truncate(draft_body, max(max_body, 100))
        parts_idx  = parts.index(draft_body.strip())
        parts[parts_idx] = truncated
        msg = "\n".join(parts)

    return msg


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Skicka draft-notis till Telegram (sandbox, kräver .secret/credentials.json)."
    )
    parser.add_argument("--id",               required=True,  help="Draft-ID, t.ex. D4")
    parser.add_argument("--priority",         required=True,  help="T.ex. 'NIVÅ 1 — AKUT'")
    parser.add_argument("--original-from",    required=True,  help="Avsändarens e-post")
    parser.add_argument("--original-subject", required=True,  help="Originalämnesrad")
    parser.add_argument("--original-summary", required=True,  help="2-3 meningar ur originalmejlet")
    parser.add_argument("--draft-subject",    required=True,  help="Utkastets ämnesrad")
    parser.add_argument("--draft-body",       required=True,  help="Hela utkaststexten")
    parser.add_argument("--recipient-count",  type=int, required=True)
    parser.add_argument("--has-attachment",   action="store_true")
    args = parser.parse_args()

    creds   = load_creds()
    tg      = creds["telegram"]
    token   = tg["bot_token"]
    chat_id = str(tg["chat_id"])

    draft_id = args.id.upper()

    text = build_message(
        draft_id         = draft_id,
        priority         = args.priority,
        original_from    = args.original_from,
        original_subject = args.original_subject,
        original_summary = args.original_summary,
        draft_subject    = args.draft_subject,
        draft_body       = args.draft_body,
        recipient_count  = args.recipient_count,
        has_attachment   = args.has_attachment,
    )

    ok = send_message(token, chat_id, text)
    if ok:
        print(f"📱 Telegram-notis skickad (Draft {draft_id})")
    else:
        print("VARNING: Telegram-notis misslyckades.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
