#!/usr/bin/env python3
# Auto-bootstrap venv
import sys, os as _os
from pathlib import Path as _Path
_VENV_DIR = _Path.home() / ".config/superintelligent/outlook-bridge/venv"
_VENV_PY  = _VENV_DIR / "bin/python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    _os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)

"""
reauth.py — Uppdatera Microsoft Graph-scopes och omautentisera.

Kör detta EN GÅNG efter att du lagt till nya API-behörigheter i Azure Portal.
Scriptet:
  1. Uppdaterar scopes i ~/.config/superintelligent/outlook-bridge/config.json
  2. Rensar den cachade token i Keychain
  3. Startar Device Code Flow med alla nya scopes
  4. Du loggar in via webbläsaren — nytt token sparas automatiskt

Kör: python scripts/outlook/reauth.py
"""

import json
import keyring
from pathlib import Path

CONFIG_PATH       = Path.home() / ".config/superintelligent/outlook-bridge/config.json"
KEYCHAIN_SERVICE  = "superintelligent-outlook-bridge"
KEYCHAIN_ACCOUNT  = "token-cache"

# Alla scopes som Mini behöver — komplett lista
ALL_SCOPES = [
    # Mejl
    "Mail.ReadWrite",
    "Mail.Send",
    "MailboxSettings.ReadWrite",
    # Kalender
    "Calendars.ReadWrite",
    "OnlineMeetings.ReadWrite",
    "OnlineMeetingTranscript.Read.All",
    "OnlineMeetingArtifact.Read.All",
    # Teams
    "Chat.ReadWrite.All",
    "ChannelMessage.Read.All",
    "ChannelMessage.Send",
    "Team.ReadBasic.All",
    "TeamMember.Read.All",
    "Presence.Read.All",
    # Uppgifter och grupper
    "Tasks.ReadWrite",
    "Group.ReadWrite.All",
    # Filer
    "Files.ReadWrite.All",
    "Sites.ReadWrite.All",
    "Notes.ReadWrite.All",
    # Katalog och personer
    "Directory.Read.All",
    "User.Read",
    "User.Read.All",
    "Contacts.ReadWrite",
    "People.Read",
    "People.Read.All",
    # Analys
    "Analytics.Read",
]


def main():
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Microsoft Graph — Omautentisering")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # 1. Läs befintlig config
    if not CONFIG_PATH.exists():
        print(f"FEL: Config saknas: {CONFIG_PATH}")
        print("Kör auth_setup.md-stegen för att skapa den.")
        sys.exit(1)

    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)

    # 2. Uppdatera scopes
    old_scopes = config.get("scopes", [])
    config["scopes"] = ALL_SCOPES

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Scopes uppdaterade: {len(old_scopes)} → {len(ALL_SCOPES)}")

    # 3. Rensa cachad token så att Device Code Flow triggas
    try:
        keyring.delete_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT)
        print("  ✓ Cachad token rensad")
    except keyring.errors.PasswordDeleteError:
        print("  ℹ  Ingen cachad token att rensa")

    print()
    print("  Startar autentisering med nya scopes...")
    print("  Du kommer få en URL och en kod — öppna URL:en i webbläsaren.")
    print()

    # 4. Trigga Device Code Flow via GraphClient
    from _graph_client import GraphClient
    try:
        g = GraphClient(CONFIG_PATH)
        g.get_token()  # Detta startar Device Code Flow om ingen token finns
        print()
        print("  ✓ Autentisering klar — token sparat i Keychain")
        print()
        print("  Mini kan nu använda kalender, To Do, Teams och alla andra verktyg.")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    except Exception as exc:
        print(f"\nFEL: Autentisering misslyckades: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
