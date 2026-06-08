# Skill: Inbox Triage

Triagerar inkommande e-post via Microsoft 365-connectorn och producerar en strukturerad rapport med prioriteringar, föreslagen handling och utkast till svar.

## Aktivering

Läs denna skill när användaren ber om:
- "Triagera min inbox"
- "Gå igenom min e-post"
- "Vad kräver min handling idag?"
- "Sammanfatta mina mejl"
- "Inbox-genomgång"

## Verktyg som används

- `mcp__plugin_productivity_ms365__*` — Outlook-e-post via Microsoft 365-connectorn
- Alternativt: `mcp__8e9ab852-acf5-4d08-9dee-77614af25683__outlook_email_search` om M365-connectorn inte är tillgänglig

## Exekvering steg för steg

1. **Hämta mejl från inkorgen** — Senaste 1 timme vid schemalagd körning, senaste 24 timmar vid manuell körning (eller tidsperiod användaren anger). Använd `folderName: "Inbox"`.

2. **Hämta Skickat för kontext** — Läs alltid `folderName: "Sent Items"` för de senaste 48 timmarna parallellt med steg 1. Detta är obligatoriskt — utan Skickat-kontext kan triage inte avgöra om ett svar redan skickats.

3. **Korsavstämning** — För varje mejl i inkorgen som verkar kräva svar: kontrollera om det finns ett skickat mejl till samma avsändare i samma tidsperiod. Om svar redan skickats: klassificera som "Väntar på andra" eller "Endast information" — skapa aldrig draft.

4. **Triagera** — Klassificera varje mejl enligt [priority-model.md](references/priority-model.md).

5. **Kategorisera** — Dela upp i [action-categories.md](references/action-categories.md).

6. **Identifiera actions** — Beslut, svar, bokningar, uppföljningar, ekonomiska åtgärder.

7. **Skapa drafts automatiskt (schemalagd körning)** — För mejl på Nivå 1 och Nivå 2 som inte redan har besvarats: skapa draft via `python scripts/outlook/create_draft.py`. Skapa aldrig draft om svar finns i Skickat. Skicka aldrig automatiskt.

8. **Producera rapport** — Följ outputformatet nedan. Inkludera vilka drafts som skapades och deras ID.

9. **Skicka Telegram-notis (schemalagd körning)** — Om drafts skapades: skicka notis via `python scripts/outlook/telegram_notify.py` för varje draft. Om inga nya mejl kräver handling: skicka ingen notis.

## Outputformat

```
## Inkorgsrapport — [datum] [tidpunkt]

### 1. Akut / Kräver min action
[Mejl som behöver beslut, svar eller åtgärd omgående]

### 2. Bör hanteras idag
[Mejl med tydlig deadline eller hög relevans, men inte akuta]

### 3. Väntar på andra
[Mejl där du har bollen men väntar på input eller bekräftelse]

### 4. Endast information
[Mejl du bör känna till men som inte kräver handling]

### 5. Föreslagna svar
[Utkast till svar — aldrig skickade automatiskt]

### 6. Föreslagna kalenderåtgärder
[Möten, deadlines, påminnelser — aldrig skapade utan godkännande]

### 7. Notistext (om kritiskt)
[Kort text för Telegram/desktop-notis, om någon post är kritisk]
```

## Säkerhetsregler

- **Skicka aldrig svar automatiskt.**
- **Radera aldrig mejl.**
- **Flytta aldrig mejl utan godkännande.**
- **Skapa aldrig kalenderhändelse utan godkännande.**
- **Skriv aldrig mejlinnehåll i repot** — triagerapporten visas i chatten, inte sparas som fil.
- Om klassificering är osäker: markera som "Behöver mänsklig bedömning".

## Referensfiler

- [Triageringsregler](references/triage-rules.md) — operativa regler för tolkning och klassificering
- [Prioritetsmodell](references/priority-model.md) — tre nivåer med konkreta kriterier
- [Handlingskategorier](references/action-categories.md) — definitioner av varje kategori
- [Svarsmallar](references/response-drafting.md) — hur utkast till svar ska formuleras
- [Notisformat](references/notification-format.md) — format för kritiska notiser
