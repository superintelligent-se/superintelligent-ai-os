#!/usr/bin/env python3
# Auto-bootstrap: byter automatiskt till venv-Python om nödvändigt.
import sys, os as _os
from pathlib import Path as _Path
_VENV_DIR = _Path.home() / ".config/superintelligent/outlook-bridge/venv"
_VENV_PY = _VENV_DIR / "bin/python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    _os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)
"""
telegram_bot.py — Polling-bot för godkännande av Outlook-drafts via Telegram.

Starta:
    python scripts/outlook/telegram_bot.py

Stoppa: Ctrl+C

Kommandon du skickar till boten i Telegram:
    /okD1          Skicka draft D1
    /okD1B         Skicka draft D1 (bekräfta bilaga)
    /okD1FM        Skicka draft D1 (bekräfta fler än 3 mottagare)
    /okD1BFM       Skicka draft D1 (bilaga + fler än 3 mottagare)
    /list          Lista aktiva drafts
    /help          Visa hjälp

Säkerhet:
    Boten svarar ENBART på meddelanden från ditt konfigurerade chat_id.
    Alla andra avsändare ignoreras tyst.
    Token och chat_id läses från Keychain och telegram.json — aldrig från repot.
"""

import json
import re
import subprocess
import sys
import time
import keyring
import requests
from pathlib import Path

KEYCHAIN_SERVICE = "superintelligent-telegram-bridge"
KEYCHAIN_ACCOUNT = "bot-token"
TELEGRAM_CONFIG = Path.home() / ".config/superintelligent/outlook-bridge/telegram.json"
TELEGRAM_API = "https://api.telegram.org"
REPO_ROOT = Path(__file__).parent.parent.parent  # superintelligent-ai-os/

# Regex: /okD42, /okD42B, /okD42FM, /okD42BFM (case-insensitive)
OK_PATTERN = re.compile(r"^/ok(D\d+)(B)?(FM)?$", re.IGNORECASE)


def load_credentials():
    token = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT)
    if not token:
        print("FEL: Bot-token saknas i Keychain.", file=sys.stderr)
        sys.exit(1)
    if not TELEGRAM_CONFIG.exists():
        print(f"FEL: {TELEGRAM_CONFIG} saknas.", file=sys.stderr)
        sys.exit(1)
    config = json.loads(TELEGRAM_CONFIG.read_text())
    chat_id = str(config.get("chat_id", ""))
    if not chat_id:
        print("FEL: chat_id saknas i telegram.json.", file=sys.stderr)
        sys.exit(1)
    return token, chat_id


def send(token: str, chat_id: str, text: str) -> None:
    try:
        requests.post(
            f"{TELEGRAM_API}/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=15,
        )
    except Exception as exc:
        print(f"VARNING: Kunde inte skicka svar: {exc}", file=sys.stderr)


def get_updates(token: str, offset: int) -> list:
    try:
        resp = requests.get(
            f"{TELEGRAM_API}/bot{token}/getUpdates",
            params={"offset": offset, "timeout": 30},
            timeout=40,
        )
        if resp.ok:
            return resp.json().get("result", [])
    except Exception:
        pass
    return []


def parse_ok_command(text: str):
    """
    Parsar /okD42, /okD42B, /okD42FM, /okD42BFM.
    Returnerar (draft_id, tokens) eller (None, None) om ogiltigt format.
    """
    text = text.strip().split()[0]  # ta bara första ordet (ignorera @botnamn)
    m = OK_PATTERN.match(text)
    if not m:
        return None, None
    draft_id = m.group(1).upper()
    tokens = set()
    if m.group(2):
        tokens.add("B")
    if m.group(3):
        tokens.add("FM")
    return draft_id, tokens


def build_send_command(draft_id: str, tokens: set) -> str:
    """Bygger OK-strängen som send_draft.py förväntar sig."""
    parts = ["OK", draft_id]
    if "B" in tokens:
        parts.append("B")
    if "FM" in tokens:
        parts.append("FM")
    return " ".join(parts)


def run_send_draft(ok_command: str) -> tuple:
    """
    Kör send_draft.py med givet OK-kommando.
    Returnerar (success: bool, output: str).
    """
    script = REPO_ROOT / "scripts" / "outlook" / "send_draft.py"
    venv_py = _Path.home() / ".config/superintelligent/outlook-bridge/venv/bin/python3"
    python = str(venv_py) if venv_py.exists() else sys.executable

    try:
        result = subprocess.run(
            [python, str(script), ok_command],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "FEL: send_draft.py tog för lång tid."
    except Exception as exc:
        return False, f"FEL: {exc}"


def run_list_drafts() -> str:
    """Kör list_drafts.py och returnerar outputen."""
    script = REPO_ROOT / "scripts" / "outlook" / "list_drafts.py"
    venv_py = _Path.home() / ".config/superintelligent/outlook-bridge/venv/bin/python3"
    python = str(venv_py) if venv_py.exists() else sys.executable

    try:
        result = subprocess.run(
            [python, str(script)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout.strip() or result.stderr.strip() or "Inga aktiva drafts."
    except Exception as exc:
        return f"FEL: {exc}"


def handle_message(token: str, chat_id: str, text: str) -> None:
    text = text.strip()
    lower = text.lower()

    # /help
    if lower in ("/help", "/start"):
        send(token, chat_id,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📧 <b>Outlook Mail Bridge</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>Skicka draft:</b>\n"
            "<code>/okD1</code>      → Skicka D1\n"
            "<code>/okD1B</code>     → Skicka D1 med bilaga\n"
            "<code>/okD1FM</code>    → Skicka D1 fler än 3 mott.\n"
            "<code>/okD1BFM</code>   → Skicka D1 bilaga + fler mott.\n\n"
            "<b>Övrigt:</b>\n"
            "<code>/list</code>      → Lista aktiva drafts\n"
            "<code>/help</code>      → Visa den här hjälpen"
        )
        return

    # /list
    if lower == "/list":
        output = run_list_drafts()
        send(token, chat_id, f"<pre>{output}</pre>")
        return

    # /okD* kommandon
    if lower.startswith("/ok"):
        draft_id, tokens = parse_ok_command(text)
        if draft_id is None:
            send(token, chat_id,
                "❌ Okänt format.\n\n"
                "Exempel: <code>/okD1</code>, <code>/okD1B</code>, "
                "<code>/okD1FM</code>, <code>/okD1BFM</code>"
            )
            return

        ok_command = build_send_command(draft_id, tokens)
        send(token, chat_id, f"⏳ Skickar <b>{draft_id}</b>…")

        success, output = run_send_draft(ok_command)
        if success:
            send(token, chat_id,
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ <b>Mejl skickat</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Draft <b>{draft_id}</b> har skickats."
            )
        else:
            send(token, chat_id,
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"❌ <b>Misslyckades</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<pre>{output}</pre>"
            )
        return

    # Okänt kommando
    send(token, chat_id,
        "Förstod inte kommandot. Skriv <code>/help</code> för hjälp."
    )


def main():
    token, chat_id = load_credentials()

    # Verifiera att boten svarar
    try:
        resp = requests.get(f"{TELEGRAM_API}/bot{token}/getMe", timeout=10)
        if resp.ok:
            name = resp.json().get("result", {}).get("username", "okänd")
            print(f"✓ Bot ansluten: @{name}")
        else:
            print(f"FEL: Kunde inte ansluta till Telegram API: {resp.text}", file=sys.stderr)
            sys.exit(1)
    except Exception as exc:
        print(f"FEL: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Lyssnar på chat_id: {chat_id}")
    print("Skicka /help i Telegram för att testa. Stoppa med Ctrl+C.\n")

    offset = 0
    while True:
        try:
            updates = get_updates(token, offset)
            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message") or update.get("edited_message")
                if not message:
                    continue

                sender_id = str(message.get("chat", {}).get("id", ""))
                if sender_id != chat_id:
                    # Ignorera tysta meddelanden från okända avsändare
                    continue

                text = message.get("text", "")
                if not text:
                    continue

                print(f"← {text}")
                handle_message(token, chat_id, text)

        except KeyboardInterrupt:
            print("\nBot stoppad.")
            break
        except Exception as exc:
            print(f"FEL i polling-loop: {exc}", file=sys.stderr)
            time.sleep(5)


if __name__ == "__main__":
    main()
