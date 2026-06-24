# Migration till Mac mini

Checklista att gå igenom EFTER att Migration Assistant är klar.
De flesta saker fungerar direkt — det är bara tre saker som kräver en aktiv åtgärd.

---

## Steg 1 — Verifiera arkitektur (kritiskt)

Öppna Terminal på Mac mini och kör:
```bash
python3 -c "import platform; print(platform.machine())"
```

- Om svaret är **`arm64`** på båda maskinerna → venv fungerar direkt, gå vidare till steg 2.
- Om svaret **skiljer sig** (t.ex. `arm64` på MacBook, `x86_64` på Mac mini) → venv måste byggas om:

```bash
cd ~/.config/superintelligent/outlook-bridge
rm -rf venv
python3 -m venv venv
venv/bin/pip install -r ~/Github/Superintelligent/superintelligent-ai-os/scripts/telegram/requirements.txt
# Lägg också till outlook-beroenden:
venv/bin/pip install msal keyring requests
```

---

## Steg 2 — Återregistrera LaunchAgent

Migration Assistant kopierar plist-filen men den behöver laddas om:

```bash
PLIST="$HOME/Library/LaunchAgents/se.superintelligent.telegram-bot.plist"
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
```

Verifiera att agenten körs:
```bash
launchctl list | grep superintelligent
```

Du ska se `se.superintelligent.telegram-bot` i listan.

---

## Steg 3 — Testa boten

Kör manuellt en gång för att se eventuella fel:
```bash
python3 ~/Github/Superintelligent/superintelligent-ai-os/scripts/telegram/assistant_bot.py
```

Skriv `/help` i Telegram och verifiera att boten svarar.

---

## Steg 4 — Microsoft Graph (om token har gått ut)

MSAL-tokens migreras med Keychain men kan ha gått ut om migrationen tar tid.
Om outlook-scripten klagar på autentisering, kör device code flow:
```bash
python3 ~/Github/Superintelligent/superintelligent-ai-os/scripts/outlook/create_draft.py --help
```
Det startar om autentiseringen automatiskt.

---

## Vad som INTE behöver göras

- ❌ Inga API-nycklar behöver läggas in igen — Keychain migreras
- ❌ Ingen konfiguration i repot behöver ändras — alla paths använder `Path.home()`
- ❌ Ingen kod behöver skrivas om — samma username, samma katalogstruktur

---

## Om något inte fungerar

Kontrollera loggarna:
```bash
tail -50 ~/.config/superintelligent/outlook-bridge/bot.log
tail -50 ~/.config/superintelligent/outlook-bridge/bot-error.log
```
