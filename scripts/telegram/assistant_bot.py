#!/usr/bin/env python3
# Auto-bootstrap: byter automatiskt till venv-Python om nödvändigt.
import sys, os as _os
from pathlib import Path as _Path

_VENV_DIR = _Path.home() / ".config/superintelligent/outlook-bridge/venv"
_VENV_PY = _VENV_DIR / "bin/python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    _os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)

"""
assistant_bot.py — Conversational Telegram assistant powered by Claude.

En enda bot som hanterar allt:
  - Fri konversation via Claude
  - Röstmeddelanden via Whisper → Claude
  - Mejlbekräftelse via naturligt språk (inte /ok-kommandon)
  - Notiser från schemalagda jobb dyker upp i samma chat och konversationshistorik

Bekräftelseflöde (ersätter /okD1):
  Bot:    "Draft D1 redo — Till: anna@..., Ämne: Möte. Ska jag skicka?"
  Thomas: "ja" / "skicka" / "looks good" → boten skickar
  Thomas: "nej" / "avbryt"              → boten avbryter
  Thomas: [annat]                        → Claude hanterar, pending bevaras

Kommandon som fortfarande stöds:
  /list    Lista aktiva mejl-drafts
  /new     Återställ konversationshistorik
  /help    Hjälp

Credentials (alla i macOS Keychain, aldrig i repot):
  Service: superintelligent-telegram-bridge   Account: bot-token
  Service: superintelligent-telegram-bridge   Account: anthropic-api-key
  Service: superintelligent-telegram-bridge   Account: openai-api-key  (valfri, för röst)
  Config:  ~/.config/superintelligent/outlook-bridge/telegram.json     (chat_id)
"""

import json
import os
import re
import subprocess
import tempfile
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import keyring
import requests

# Verktyg — importeras för tool-calling
from tools import TOOL_DEFINITIONS, execute_tool

# ── Konstanter ────────────────────────────────────────────────────────────────

KEYCHAIN_SERVICE    = "superintelligent-telegram-bridge"
CONFIG_DIR          = _Path.home() / ".config/superintelligent/outlook-bridge"
TELEGRAM_CONFIG     = CONFIG_DIR / "telegram.json"
HISTORY_FILE        = CONFIG_DIR / "conversation_history.json"
TELEGRAM_API        = "https://api.telegram.org"
ANTHROPIC_API       = "https://api.anthropic.com/v1/messages"
REPO_ROOT           = _Path(__file__).parent.parent.parent
OUTLOOK_SCRIPTS     = REPO_ROOT / "scripts" / "outlook"
# pending_action.json lives in .secret/ so both the sandbox (scheduled task)
# and this bot (Mac mini) can read/write the same file via the shared repo.
PENDING_FILE        = REPO_ROOT / ".secret" / "pending_action.json"

MAX_HISTORY_MSGS    = 20
MAX_TELEGRAM_LEN    = 4000
PENDING_EXPIRY_HOURS = 24
CLAUDE_MODEL        = "claude-sonnet-4-6"
MAX_TOOL_ITERATIONS = 8   # Max antal tool-anrop per svar (skyddar mot oändliga loopar)

# ── System-prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Du heter Mini och är Thomas Dalebring personliga AI-assistent. Du körs på Thomas Mac mini och är alltid tillgänglig via Telegram.

Thomas är grundare och VD för Superintelligent — ett bolag som demokratiserar AI för svenska organisationer. Han arbetar med kunder, content, produkt och strategi.

Du har direkt tillgång till Thomas Microsoft 365-miljö via verktyg. Använd dem proaktivt och utan att fråga om lov:
- get_calendar_events — hämta möten och kalender
- get_emails — läsa inkorgen
- get_tasks — hämta uppgifter från To Do
- search_people — slå upp en person i katalogen
- send_email — skicka ett mejl direkt (till, ämne, brödtext)

Beteende:
- Svara alltid på svenska om Thomas inte skriver på annat språk
- Var direkt och konkret — inga onödiga omskrivningar
- Hämta alltid relevant data med verktygen istället för att säga att du inte kan se det
- Du har konversationshistoriken för kontext — inklusive notiser från schemalagda jobb
- När Thomas ber dig skicka ett mejl: använd send_email direkt — fråga inte om lov i onödan
- Tonen: professionell, mänsklig, varm — du är Mini, inte en generisk bot"""

# ── Credentials ───────────────────────────────────────────────────────────────

def _load_from_secret_file() -> dict:
    """Fallback: läs bot-token och chat_id från .secret/credentials.json i repot."""
    secret = REPO_ROOT / ".secret" / "credentials.json"
    if secret.exists():
        try:
            return json.loads(secret.read_text()).get("telegram", {})
        except Exception:
            pass
    return {}


def load_credentials() -> tuple:
    # Läs från .secret/credentials.json först — fungerar alltid, även när
    # Keychain är låst (t.ex. när LaunchAgent startar vid boot).
    tg = _load_from_secret_file()
    token       = tg.get("bot_token") or keyring.get_password(KEYCHAIN_SERVICE, "bot-token")
    anthropic_key = tg.get("anthropic_api_key") or keyring.get_password(KEYCHAIN_SERVICE, "anthropic-api-key")
    chat_id     = str(tg.get("chat_id", "")) or keyring.get_password(KEYCHAIN_SERVICE, "chat_id") or ""

    # Fallback för chat_id: telegram.json
    if not chat_id and TELEGRAM_CONFIG.exists():
        try:
            cfg = json.loads(TELEGRAM_CONFIG.read_text())
            chat_id = str(cfg.get("chat_id", ""))
        except Exception:
            pass

    if not token:
        sys.exit("FEL: bot-token saknas i .secret/credentials.json och Keychain")
    if not anthropic_key:
        sys.exit("FEL: anthropic-api-key saknas i .secret/credentials.json och Keychain")
    if not chat_id:
        sys.exit("FEL: chat_id saknas i .secret/credentials.json, telegram.json och Keychain")

    return token, chat_id, anthropic_key


# ── Telegram-helpers ──────────────────────────────────────────────────────────

def send(token: str, chat_id: str, text: str) -> None:
    if len(text) > MAX_TELEGRAM_LEN:
        text = text[:MAX_TELEGRAM_LEN - 30] + "\n\n…[svar trunkerat]"
    try:
        requests.post(
            f"{TELEGRAM_API}/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=15,
        )
    except Exception as exc:
        print(f"VARNING: send misslyckades: {exc}", file=sys.stderr)


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


def download_file(token: str, file_id: str) -> Optional[bytes]:
    try:
        resp = requests.get(
            f"{TELEGRAM_API}/bot{token}/getFile",
            params={"file_id": file_id},
            timeout=15,
        )
        if not resp.ok:
            return None
        file_path = resp.json()["result"]["file_path"]
        r = requests.get(f"https://api.telegram.org/file/bot{token}/{file_path}", timeout=30)
        return r.content if r.ok else None
    except Exception as exc:
        print(f"VARNING: Filnedladdning misslyckades: {exc}", file=sys.stderr)
        return None


# ── Konversationshistorik ─────────────────────────────────────────────────────

def load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_history(history: list) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        print(f"VARNING: Kunde inte spara historik: {exc}", file=sys.stderr)


def trim_history(history: list) -> list:
    if len(history) > MAX_HISTORY_MSGS:
        return history[-MAX_HISTORY_MSGS:]
    return history


# ── Pending action (bekräftelsetillstånd) ─────────────────────────────────────

def load_pending() -> Optional[dict]:
    """Läs eventuell väntande åtgärd. Returnerar None om ingen finns eller den gått ut."""
    if not PENDING_FILE.exists():
        return None
    try:
        data = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        expires = datetime.fromisoformat(data["expires_at"])
        if datetime.now(timezone.utc) > expires:
            PENDING_FILE.unlink(missing_ok=True)
            return None
        return data
    except Exception:
        return None


def clear_pending() -> None:
    try:
        PENDING_FILE.unlink(missing_ok=True)
    except Exception:
        pass


# ── Bekräftelselogik ──────────────────────────────────────────────────────────

_AFFIRMATIVE = {
    "ja", "yes", "ok", "okej", "okay", "skicka", "send", "kör", "gör det",
    "go ahead", "looks good", "ser bra ut", "yep", "absolut", "sänd",
    "självklart", "visst", "sure", "klart", "👍",
}
_NEGATIVE = {
    "nej", "no", "nope", "cancel", "avbryt", "stopp", "stop", "skip",
    "hoppa", "aldrig", "not",
}
# Ord som gör ett ja-ord villkorligt ("skicka inte", "ja men ändra")
_COMPLICATORS = {"inte", "not", "men", "but", "fast", "dock", "ändra", "först", "before"}


def classify_confirmation(text: str) -> str:
    """
    Klassificerar ett meddelande i förhållande till en väntande åtgärd.
    Returnerar 'yes', 'no' eller 'unclear'.
    """
    words = set(text.lower().strip().split())

    # Negation + ja-ord → nej ("skicka inte", "not yet")
    if words & _COMPLICATORS and words & _AFFIRMATIVE:
        return "no"

    if words & _AFFIRMATIVE:
        return "yes"
    if words & _NEGATIVE:
        return "no"
    return "unclear"


# ── Claude API ────────────────────────────────────────────────────────────────

def call_claude(anthropic_key: str, history: list) -> str:
    """
    Agentic loop: skickar historik till Claude, kör tool-anrop tills Claude
    svarar med text. Returnerar det slutliga textsvaret.

    Tool-anrop sparas INTE i den persistenta historiken — bara user-text och
    Claudes slutliga textsvar sparas. Håller historiken ren och token-effektiv.
    """
    # Arbeta på en lokal kopia — påverkar inte den persistenta historiken
    messages = list(history)

    for iteration in range(MAX_TOOL_ITERATIONS):
        try:
            resp = requests.post(
                ANTHROPIC_API,
                headers={
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": CLAUDE_MODEL,
                    "max_tokens": 2048,
                    "system": SYSTEM_PROMPT,
                    "tools": TOOL_DEFINITIONS,
                    "messages": messages,
                },
                timeout=90,
            )
            resp.raise_for_status()
        except requests.HTTPError as exc:
            body = exc.response.text[:300] if exc.response else ""
            print(f"FEL: Claude HTTP {exc.response.status_code}: {body}", file=sys.stderr)
            return "⚠️ Kunde inte nå Claude just nu. Försök igen."
        except Exception as exc:
            print(f"FEL: Claude API: {exc}", file=sys.stderr)
            return "⚠️ Något gick fel. Försök igen."

        data        = resp.json()
        stop_reason = data.get("stop_reason")
        content     = data.get("content", [])

        if stop_reason == "end_turn":
            # Extrahera textsvaret
            text_blocks = [b["text"] for b in content if b.get("type") == "text"]
            return "\n\n".join(text_blocks) or "⚠️ Inget textsvar från Claude."

        if stop_reason == "tool_use":
            # Lägg till assistentens svar (inkl. tool_use-block) i den lokala historiken
            messages.append({"role": "assistant", "content": content})

            # Kör varje verktyg och samla resultat
            tool_results = []
            for block in content:
                if block.get("type") != "tool_use":
                    continue
                tool_name  = block["name"]
                tool_input = block.get("input", {})
                print(f"  🔧 {tool_name}({tool_input})")
                result = execute_tool(tool_name, tool_input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": result,
                })

            # Skicka tillbaka resultaten
            messages.append({"role": "user", "content": tool_results})
            continue  # Nästa iteration

        # Oväntat stop_reason — returnera vad vi har
        text_blocks = [b["text"] for b in content if b.get("type") == "text"]
        return "\n\n".join(text_blocks) or f"⚠️ Oväntat svar (stop_reason={stop_reason})."

    return "⚠️ Max antal verktygsanrop nåtts. Försök igen med en enklare fråga."


# ── Whisper (lokal) ───────────────────────────────────────────────────────────

_whisper_model = None


def _get_whisper_model():
    """Lazy-laddar Whisper-modellen vid första anrop (sparas sedan i minnet)."""
    global _whisper_model
    if _whisper_model is None:
        import whisper  # noqa: PLC0415
        print("⏳ Laddar Whisper-modellen (sker bara en gång)…")
        _whisper_model = whisper.load_model("small")
        print("✓ Whisper-modellen laddad.")
    return _whisper_model


def transcribe_voice(ogg_bytes: bytes) -> Optional[str]:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(ogg_bytes)
            tmp_path = tmp.name
        model = _get_whisper_model()
        result = model.transcribe(tmp_path, language="sv")
        return result["text"].strip() or None
    except Exception as exc:
        print(f"FEL: Transkribering: {exc}", file=sys.stderr)
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ── Outlook-scripts ───────────────────────────────────────────────────────────

def _outlook_python() -> str:
    venv_py = _Path.home() / ".config/superintelligent/outlook-bridge/venv/bin/python3"
    return str(venv_py) if venv_py.exists() else sys.executable


def run_outlook_script(script_name: str, args: list = None) -> tuple:
    script = OUTLOOK_SCRIPTS / script_name
    cmd = [_outlook_python(), str(script)] + (args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "FEL: Script tog för lång tid."
    except Exception as exc:
        return False, f"FEL: {exc}"


def execute_send_draft(token: str, chat_id: str, pending: dict) -> list:
    """
    Skapar och skickar mejlet baserat på pending_action.
    Använder create_and_send.py som har full nätverksåtkomst på Mac mini.
    Returnerar historikposter att lägga till.
    """
    to_address = pending.get("to_address") or pending.get("to_summary", "")
    subject    = pending.get("subject", "")
    draft_body = pending.get("draft_body", "")
    draft_id   = pending.get("draft_id", "?")

    if not to_address or not subject or not draft_body:
        reply = "❌ Ofullständig draft-info — kan inte skicka. Kontrollera pending_action.json."
        send(token, chat_id, reply)
        return [{"role": "assistant", "content": reply}]

    send(token, chat_id, "⏳ Skickar…")
    success, output = run_outlook_script("create_and_send.py", [
        "--to",      to_address,
        "--subject", subject,
        "--body",    draft_body,
    ])

    if success:
        reply = f"✅ Mejlet skickat till {to_address}."
    else:
        reply = f"❌ Kunde inte skicka.\n<pre>{output}</pre>"

    send(token, chat_id, reply)
    return [{"role": "assistant", "content": reply}]


# ── Meddelandehanterare ───────────────────────────────────────────────────────

def handle_message(
    token: str,
    chat_id: str,
    anthropic_key: str,
    history: list,
    message: dict,
) -> list:

    text  = (message.get("text") or "").strip()
    voice = message.get("voice")
    lower = text.lower()

    # ── /new ──────────────────────────────────────────────────────────────────
    if lower == "/new":
        clear_pending()
        save_history([])
        send(token, chat_id, "🔄 Konversation återställd.")
        return []

    # ── /help / /start ────────────────────────────────────────────────────────
    if lower in ("/help", "/start"):
        send(token, chat_id,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 <b>Mini — Thomas assistent</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Skriv vad som helst — jag svarar via Claude.\n"
            "Skicka 🎙 röstmeddelanden för att prata.\n\n"
            "<b>Mejl-bekräftelse:</b>\n"
            "När inkorgen triageras får du ett meddelande med ett färdigt svar.\n"
            "  <i>ja / skicka / looks good</i> → skickar mejlet\n"
            "  <i>nej / avbryt / skip</i>       → avbryter\n\n"
            "<b>Kommandon:</b>\n"
            "<code>/new</code>    Återställ konversation\n"
            "<code>/help</code>   Denna hjälp"
        )
        return history

    # ── /list ─────────────────────────────────────────────────────────────────
    if lower == "/list":
        _, output = run_outlook_script("list_drafts.py")
        send(token, chat_id, f"<pre>{output or 'Inga aktiva drafts.'}</pre>")
        return history

    # ── Röstmeddelande → transkribera, sedan behandla som text ────────────────
    if voice:
        send(token, chat_id, "🎙 Transkriberar…")
        ogg = download_file(token, voice["file_id"])
        if not ogg:
            send(token, chat_id, "❌ Kunde inte ladda ned röstmeddelandet.")
            return history
        transcribed = transcribe_voice(ogg)
        if not transcribed:
            send(token, chat_id, "❌ Transkribering misslyckades.")
            return history
        send(token, chat_id, f"🎙 <i>{transcribed}</i>")
        text = transcribed
        lower = text.lower()

    if not text:
        return history

    # ── Bekräftelsetillstånd: kontrollera om ett draft väntar ─────────────────
    pending = load_pending()
    if pending:
        verdict = classify_confirmation(text)

        if verdict == "yes":
            clear_pending()
            history += execute_send_draft(token, chat_id, pending)
            save_history(trim_history(history))
            return history

        elif verdict == "no":
            clear_pending()
            reply = f"OK, draftet skickas inte."
            send(token, chat_id, reply)
            history.append({"role": "user", "content": text})
            history.append({"role": "assistant", "content": reply})
            save_history(trim_history(history))
            return history

        else:
            # Oklart svar — låt Claude hantera men injicera kontext om pending
            pending_context = (
                f"[OBS: Det finns ett mejl-draft som väntar på bekräftelse — "
                f"Draft {pending['draft_id']}, Till: {pending.get('to_summary','?')}, "
                f"Ämne: {pending.get('subject','?')}. "
                f"Om Thomas menar att bekräfta eller avbryta detta, tala om det tydligt.]"
            )
            text_with_context = f"{text}\n\n{pending_context}"
            history.append({"role": "user", "content": text_with_context})

    else:
        history.append({"role": "user", "content": text})

    # ── Claude ────────────────────────────────────────────────────────────────
    history = trim_history(history)
    response = call_claude(anthropic_key, history)
    history.append({"role": "assistant", "content": response})
    save_history(trim_history(history))
    send(token, chat_id, response)
    return history


# ── Polling-loop ──────────────────────────────────────────────────────────────

def main():
    token, chat_id, anthropic_key = load_credentials()

    try:
        resp = requests.get(f"{TELEGRAM_API}/bot{token}/getMe", timeout=10)
        if not resp.ok:
            sys.exit(f"FEL: Telegram API svarar inte: {resp.text}")
        bot_name = resp.json()["result"]["username"]
    except Exception as exc:
        sys.exit(f"FEL: {exc}")

    print(f"✓ Bot:   @{bot_name}")
    print(f"✓ Model: {CLAUDE_MODEL}")
    print(f"✓ Röst:  aktiverat (lokal Whisper)")
    print(f"✓ Chat:  {chat_id}")
    print("Skriv /help i Telegram. Stoppa med Ctrl+C.\n")

    history = load_history()
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
                    continue
                log = message.get("text") or ("[röst]" if message.get("voice") else "[?]")
                print(f"← {log}")
                history = handle_message(token, chat_id, anthropic_key, history, message)

        except KeyboardInterrupt:
            print("\nBot stoppad.")
            break
        except Exception as exc:
            print(f"FEL i loop: {exc}", file=sys.stderr)
            time.sleep(5)


if __name__ == "__main__":
    main()
