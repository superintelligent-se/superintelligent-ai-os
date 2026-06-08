#!/bin/bash
# setup_sandbox_credentials.sh — Exporterar credentials till .secret/credentials.json
#
# Kör EN gång från repo-roten:
#     bash scripts/outlook/setup_sandbox_credentials.sh
#
# Vad skriptet gör:
#   1. Läser MSAL-token från macOS Keychain
#   2. Läser Microsoft-konfiguration från ~/.config/superintelligent/outlook-bridge/config.json
#   3. Läser Telegram bot-token från Keychain och chat_id från telegram.json
#   4. Skriver allt till .secret/credentials.json (600-rättigheter, gitignorerat)
#
# Hur länge håller det?
#   Microsoft refresh tokens är giltiga i 14 dagar utan användning,
#   men förnyas automatiskt av sandbox-skripten vid varje körning.
#   Om scheduled task kör dagligen behöver du aldrig köra detta igen.
#
# Kräver: venv med msal + keyring installerat (skapas av auth_setup.py)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV_PY="$HOME/.config/superintelligent/outlook-bridge/venv/bin/python3"
SECRET_DIR="$REPO_ROOT/.secret"

echo "=== Exporterar sandbox-credentials ==="
echo "Repo: $REPO_ROOT"

if [ ! -f "$VENV_PY" ]; then
  echo "FEL: venv saknas på $VENV_PY"
  echo "Kör python scripts/outlook/auth_setup.py för att skapa den."
  exit 1
fi

mkdir -p "$SECRET_DIR"
chmod 700 "$SECRET_DIR"

REPO_ROOT="$REPO_ROOT" "$VENV_PY" - << 'PYTHON'
import json, os, sys, stat
from pathlib import Path
from datetime import datetime, timezone, timedelta

REPO_ROOT = Path(os.environ["REPO_ROOT"])
SECRET_DIR = REPO_ROOT / ".secret"
CREDS_FILE = SECRET_DIR / "credentials.json"

try:
    import keyring
    import msal
except ImportError as e:
    print(f"FEL: Saknar {e.name}. Kontrollera att venv är korrekt installerat.", file=sys.stderr)
    sys.exit(1)

# ── Microsoft Graph ───────────────────────────────────────────────────────────
GRAPH_SERVICE = "superintelligent-outlook-bridge"
GRAPH_ACCOUNT = "token-cache"
CONFIG_PATH   = Path.home() / ".config/superintelligent/outlook-bridge/config.json"

if not CONFIG_PATH.exists():
    print(f"FEL: {CONFIG_PATH} saknas. Kör auth_setup.py.", file=sys.stderr)
    sys.exit(1)

config    = json.loads(CONFIG_PATH.read_text())
client_id = config["client_id"]
tenant_id = config.get("tenant_id", "common")
scopes    = config.get("scopes", ["Mail.ReadWrite", "Mail.Send", "User.Read"])

cached_data = keyring.get_password(GRAPH_SERVICE, GRAPH_ACCOUNT)
if not cached_data:
    print("FEL: Ingen MSAL token-cache i keychain. Kör auth_setup.py.", file=sys.stderr)
    sys.exit(1)

cache = msal.SerializableTokenCache()
cache.deserialize(cached_data)

app      = msal.PublicClientApplication(
    client_id=client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}",
    token_cache=cache,
)
accounts = app.get_accounts()
if not accounts:
    print("FEL: Inga konton i MSAL-cache. Kör auth_setup.py.", file=sys.stderr)
    sys.exit(1)

# Tyst token-hämtning (förnyar automatiskt om det behövs)
result = app.acquire_token_silent(scopes, account=accounts[0])
if not result or "access_token" not in result:
    print("FEL: Kunde inte hämta token tyst. Kör auth_setup.py.", file=sys.stderr)
    sys.exit(1)

expires_in    = result.get("expires_in", 3600)
token_expires = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()

# Extrahera refresh token ur MSAL-cache
cache_obj     = json.loads(cache.serialize())
refresh_token = ""
for rt in cache_obj.get("RefreshToken", {}).values():
    if rt.get("client_id") == client_id:
        refresh_token = rt.get("secret", "")
        break

if not refresh_token:
    print("VARNING: Ingen refresh_token hittades. Token måste förnyas inom ~1h.", file=sys.stderr)

# ── Telegram ──────────────────────────────────────────────────────────────────
TG_SERVICE  = "superintelligent-telegram-bridge"
TG_ACCOUNT  = "bot-token"
TG_CFG_PATH = Path.home() / ".config/superintelligent/outlook-bridge/telegram.json"

tg_token = keyring.get_password(TG_SERVICE, TG_ACCOUNT)
if not tg_token:
    print("FEL: Telegram bot-token saknas i keychain.", file=sys.stderr)
    sys.exit(1)

if not TG_CFG_PATH.exists():
    print(f"FEL: {TG_CFG_PATH} saknas.", file=sys.stderr)
    sys.exit(1)

tg_cfg  = json.loads(TG_CFG_PATH.read_text())
chat_id = tg_cfg.get("chat_id")
if not chat_id:
    print("FEL: chat_id saknas i telegram.json.", file=sys.stderr)
    sys.exit(1)

# ── Skriv credentials ─────────────────────────────────────────────────────────
creds = {
    "graph": {
        "client_id":     client_id,
        "tenant_id":     tenant_id,
        "access_token":  result["access_token"],
        "refresh_token": refresh_token,
        "token_expires": token_expires,
    },
    "telegram": {
        "bot_token": tg_token,
        "chat_id":   str(chat_id),
    },
}

SECRET_DIR.mkdir(exist_ok=True)
CREDS_FILE.write_text(json.dumps(creds, indent=2, ensure_ascii=False))
os.chmod(CREDS_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 600

print(f"✓ Credentials sparade till {CREDS_FILE}")
print(f"  Graph token gäller till: {token_expires}")
print(f"  Refresh token: {'✓ Hittad' if refresh_token else '✗ Saknas'}")
print(f"  Telegram chat_id: {chat_id}")
PYTHON

echo ""
echo "✓ Klart. .secret/credentials.json är redo för sandbox-körningar."
echo "  Kom ihåg: kör detta skript igen om du loggar ut från Microsoft."
