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
from datetime import datetime, timedelta, timezone
import keyring
import requests
from pathlib import Path

KEYCHAIN_SERVICE  = "superintelligent-telegram-bridge"
KEYCHAIN_ACCOUNT  = "bot-token"
CONFIG_DIR        = Path.home() / ".config/superintelligent/outlook-bridge"
TELEGRAM_CONFIG   = CONFIG_DIR / "telegram.json"
HISTORY_FILE      = CONFIG_DIR / "conversation_history.json"
PENDING_FILE      = CONFIG_DIR / "pending_action.json"
TELEGRAM_API      = "https://api.telegram.org"
MAX_HISTORY_MSGS  = 20
PENDING_EXPIRY_HOURS = 24


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


def _append_to_history(role: str, content: str) -> None:
    """
    Lägg till ett meddelande i konversationshistoriken som assistant_bot.py delar.
    Gör att Claude har kontext om notiser när Thomas svarar.
    Non-blocking — kastar aldrig exception.
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        history = []
        if HISTORY_FILE.exists():
            try:
                history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        history.append({"role": role, "content": content})
        if len(history) > MAX_HISTORY_MSGS:
            history = history[-MAX_HISTORY_MSGS:]
        HISTORY_FILE.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        print(f"VARNING: Kunde inte uppdatera historik: {exc}", file=sys.stderr)


def _write_pending_action(
    draft_id: str,
    subject: str,
    to_summary: str,
    has_attachment: bool,
    recipient_count: int,
) -> None:
    """
    Skriv pending_action.json så att assistant_bot.py vet att ett draft väntar
    på bekräftelse via naturligt språk. Non-blocking.
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        data = {
            "type": "send_draft",
            "draft_id": draft_id,
            "subject": subject,
            "to_summary": to_summary,
            "has_attachment": has_attachment,
            "recipient_count": recipient_count,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=PENDING_EXPIRY_HOURS)).isoformat(),
        }
        PENDING_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        print(f"VARNING: Kunde inte skriva pending_action: {exc}", file=sys.stderr)


def notify_draft_ready(
    draft_id: str,
    subject: str,
    to_summary: str,
    recipient_count: int,
    has_attachment: bool,
    silent: bool = False,
) -> bool:
    """
    Skickar en draft-notis till Telegram med naturligt bekräftelseflöde.
    Skriver också till konversationshistorik och pending_action.json.
    Returnerar True om det lyckades, False annars.
    Kastar aldrig exception — är alltid non-blocking.
    """
    try:
        token, chat_id = load_credentials()
    except SystemExit:
        return False

    flags = []
    if has_attachment:
        flags.append("📎 Bilaga")
    if recipient_count > 3:
        flags.append(f"⚠️ {recipient_count} mottagare")
    flag_line = "  ·  ".join(flags) if flags else "✓ Inga varningar"

    text = (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📧 <b>Draft {draft_id} är redo</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Till:</b> {to_summary}\n"
        f"<b>Ämne:</b> {subject}\n\n"
        f"{flag_line}\n\n"
        f"Ska jag skicka detta? Svara <b>ja</b> eller <b>nej</b>."
    )

    ok = send_message(token, chat_id, text)

    if ok:
        # Spara notisen i konversationshistoriken så Claude har kontext
        _append_to_history("assistant", text)
        # Registrera att ett draft väntar på bekräftelse
        _write_pending_action(draft_id, subject, to_summary, has_attachment, recipient_count)

    if not silent:
        if ok:
            print(f"📱 Telegram-notis skickad (Draft {draft_id})")
        else:
            print("VARNING: Telegram-notis misslyckades — godkänn via /list i Telegram.", file=sys.stderr)
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
