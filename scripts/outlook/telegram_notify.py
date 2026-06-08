#!/usr/bin/env python3
# Auto-bootstrap: byter automatiskt till venv-Python om nödvändigt.
import sys, os as _os
from pathlib import Path as _Path
_VENV_DIR = _Path.home() / ".config/superintelligent/outlook-bridge/venv"
_VENV_PY = _VENV_DIR / "bin/python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    _os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)
"""
telegram_notify.py — Skicka draft-notis till Telegram.

Anropas automatiskt från review_draft.py efter att review visats.
Kan också köras manuellt:

    python telegram_notify.py --id D1 --subject "Ämne" \\
        --to-summary "anna@example.com" --recipient-count 1

Kräver:
    - Bot-token i Keychain: superintelligent-telegram-bridge / bot-token
    - ~/.config/superintelligent/outlook-bridge/telegram.json med chat_id
"""

import argparse
import json
import sys
import keyring
import requests
from pathlib import Path

KEYCHAIN_SERVICE = "superintelligent-telegram-bridge"
KEYCHAIN_ACCOUNT = "bot-token"
TELEGRAM_CONFIG = Path.home() / ".config/superintelligent/outlook-bridge/telegram.json"
TELEGRAM_API = "https://api.telegram.org"


def load_credentials():
    token = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT)
    if not token:
        print("FEL: Telegram bot-token saknas. Kör setup-kommandot i auth_setup.md.", file=sys.stderr)
        sys.exit(1)
    if not TELEGRAM_CONFIG.exists():
        print(f"FEL: {TELEGRAM_CONFIG} saknas.", file=sys.stderr)
        sys.exit(1)
    config = json.loads(TELEGRAM_CONFIG.read_text())
    chat_id = config.get("chat_id")
    if not chat_id:
        print("FEL: chat_id saknas i telegram.json.", file=sys.stderr)
        sys.exit(1)
    return token, chat_id


def send_message(token: str, chat_id: str, text: str) -> bool:
    try:
        resp = requests.post(
            f"{TELEGRAM_API}/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=15,
        )
        return resp.ok
    except Exception as exc:
        print(f"VARNING: Telegram-anrop misslyckades: {exc}", file=sys.stderr)
        return False


def build_ok_command(draft_id: str, has_attachment: bool, recipient_count: int) -> str:
    cmd = f"/ok{draft_id}"
    if has_attachment:
        cmd += "B"
    if recipient_count > 3:
        cmd += "FM"
    return cmd


def notify_draft_ready(
    draft_id: str,
    subject: str,
    to_summary: str,
    recipient_count: int,
    has_attachment: bool,
    silent: bool = False,
) -> bool:
    """
    Skickar en draft-notis till Telegram.
    Returnerar True om det lyckades, False annars.
    Kastar aldrig exception — är alltid non-blocking.
    """
    try:
        token, chat_id = load_credentials()
    except SystemExit:
        return False

    ok_cmd = build_ok_command(draft_id, has_attachment, recipient_count)

    flags = []
    if has_attachment:
        flags.append("📎 Bilaga")
    if recipient_count > 3:
        flags.append(f"⚠️ {recipient_count} mottagare")
    flag_line = "  ·  ".join(flags) if flags else "✓ Inga varningar"

    text = (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📧 <b>Draft {draft_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Till:</b> {to_summary}\n"
        f"<b>Ämne:</b> {subject}\n\n"
        f"{flag_line}\n\n"
        f"Skicka:\n"
        f"<code>{ok_cmd}</code>"
    )

    ok = send_message(token, chat_id, text)
    if not silent:
        if ok:
            print(f"📱 Telegram-notis skickad (Draft {draft_id})")
        else:
            print("VARNING: Telegram-notis misslyckades — fortsätt godkänna i Cowork.", file=sys.stderr)
    return ok


def main():
    parser = argparse.ArgumentParser(description="Skicka draft-notis till Telegram.")
    parser.add_argument("--id", required=True, help="Kort draft-ID, t.ex. D1")
    parser.add_argument("--subject", required=True, help="Ämnesrad")
    parser.add_argument("--to-summary", required=True, help="Kort mottagarbeskrivning")
    parser.add_argument("--recipient-count", type=int, required=True)
    parser.add_argument("--has-attachment", action="store_true")
    args = parser.parse_args()

    notify_draft_ready(
        draft_id=args.id.upper(),
        subject=args.subject,
        to_summary=args.to_summary,
        recipient_count=args.recipient_count,
        has_attachment=args.has_attachment,
    )


if __name__ == "__main__":
    main()
