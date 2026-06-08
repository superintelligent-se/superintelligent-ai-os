# Dispatch / Telegram — Mobilt godkännande (fas 2)

> **Status: Ej implementerat i v0.1.** Detta dokument beskriver den planerade arkitekturen för fas 2.

## Syfte

Möjliggöra granskning och godkännande av drafts från mobilen via Telegram, utan att öppna datorn.

---

## Arkitektur (fas 2)

### Komponenter

1. **Telegram Bot** — körs lokalt på din Mac som bakgrundsprocess (`telegram_bot.py`)
2. **Lokal webhook-socket** — bot och Cowork kommunicerar via Unix socket eller lokal fil
3. **Approval store** — liten lokal fil (`~/.config/superintelligent/outlook-bridge/approvals.json`) som bot skriver till och Cowork läser från

### Flöde

```
review_draft.py körs
      │
      ▼
Bot skickar review-sammanfattning till Telegram:

  📧 Draft D42
  Till: Anna Svensson (+1)
  Ämne: Projektuppdatering v3
  Bilaga: Nej  |  Mottagare: 2
  
  Svara /okD42 för att godkänna

      │
      ▼
Användaren svarar /okD42 på telefonen
      │
      ▼
Bot skriver till approvals.json:
  {"D42": {"approved_at": "...", "command": "OK D42"}}
      │
      ▼
Cowork läser approvals.json (polling eller inotify)
      │
      ▼
send_draft.py körs med godkänt kommando
```

### Telegram-kommandon

| Situation | Telegramkommando |
|---|---|
| Standard | `/okD42` |
| Bilaga | `/okD42B` |
| Fler än 3 mottagare | `/okD42FM` |
| Bilaga + fler än 3 mottagare | `/okD42BFM` |

Samma valideringslogik som i Cowork-chatten tillämpas av boten.

---

## Säkerhetsregler för fas 2

- Telegram-bottoken lagras i Keychain, aldrig i repot
- Bot accepterar kommandon enbart från din Telegram user-ID (konfigureras i `config.json`)
- Approvals.json innehåller aldrig mejlinnehåll — enbart draft-ID, kommando och tidsstämpel
- Bot kan enbart trigga send för drafts som redan är reviewade (reviewed_at är satt)
- Bot kan aldrig skapa drafts — enbart godkänna befintliga

---

## Alternativ: ntfy.sh (enklare)

Om Telegram-bot känns för komplext kan `ntfy.sh` användas för push-notiser:

```bash
curl -d "Draft D42 redo. Öppna Cowork för att godkänna." ntfy.sh/mitt-unika-kanal-id
```

Godkännandet sker fortfarande i Cowork — notisen är bara en påminnelse. Enklare att sätta upp, kräver inget bot-script.

---

## Implementationssteg för fas 2

1. Registrera Telegram-bot via @BotFather
2. Spara bottoken i Keychain
3. Konfigurera tillåten user-ID i config.json
4. Skriv `scripts/outlook/telegram_bot.py`
5. Implementera approvals.json-läsning i Cowork
6. Testa med self-approval
