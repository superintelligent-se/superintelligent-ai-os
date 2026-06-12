---
name: hourly-inbox-triage
description: Triagerar inkorgen varje timme 07:00–22:00, skapar drafts för email som kräver svar och skickar Telegram-notis.
---

Du kör en schemalagd inbox-triage för thomas@superintelligent.se. Exekvera stegen nedan i ordning utan att be om bekräftelse.

## Steg 1 — Hämta email parallellt

Kör dessa två sökningar samtidigt:

A) Inkorgen — senaste 90 minuter:
- Verktyg: `mcp__8e9ab852-acf5-4d08-9dee-77614af25683__outlook_email_search`
- folderName: "Inbox", afterDateTime: "90 minutes ago", order: "newest", limit: 25

B) Skickat — senaste 48 timmar (för kontext):
- Verktyg: `mcp__8e9ab852-acf5-4d08-9dee-77614af25683__outlook_email_search`
- folderName: "Sent Items", afterDateTime: "48 hours ago", order: "newest", limit: 25

Om inkorgen är tom: avsluta utan att göra något. Skicka ingen Telegram-notis.

## Steg 2 — Korsavstämning

För varje inbox-email som verkar kräva svar: kontrollera om det finns ett skickat mejl till samma avsändare i Skickat-listan. Om svar redan skickats → klassificera som "Väntar på andra" eller "Endast information". Skapa ALDRIG draft för ett email som redan besvarats.

## Steg 3 — Triagera enligt prioritetsmodell

Klassificera varje inbox-email i exakt en kategori:

**Nivå 1 — Akut (kräver svar inom 4h)** — minst ett kriterium uppfyllt:
- Explicit deadline inom 24 timmar
- Ekonomisk åtgärd (faktura, avtal, offert)
- Kund uttrycker missnöje eller eskalering
- Avsändaren kan inte gå vidare utan ditt svar
- Mötesbegäran som kräver omedelbart svar
- Juridisk eller säkerhetsrelevant fråga
- Avsändare är VD, styrelseledamot, nyckelkund eller extern partner

**Nivå 2 — Bör hanteras idag** — relevant men inte brådskande:
- Fråga eller förfrågan utan explicit deadline
- Intern kommunikation som kräver svar
- Uppföljning på pågående ärenden
- Mötesinbjudan utan tidspress

**Nivå 3 / Väntar / Info** — allt annat:
- Nyhetsbrev, massutskick, kampanjer
- Automatiska bekräftelser (ordrar, leveranser, bokningar)
- CC-mejl där Thomas inte är primär mottagare
- Systemnotiser
- Email som redan besvarats (från korsavstämning)

## Steg 4 — Skapa drafts och skicka Telegram-notiser

För varje email på Nivå 1 eller Nivå 2 som INTE redan besvarats:

**a) Förbered variablerna:**
```bash
PRIORITY="NIVÅ 1 — AKUT"       # eller "NIVÅ 2 — BÖR HANTERAS IDAG"
ORIGINAL_FROM="avsändare@example.com"
ORIGINAL_SUBJECT="Originalämne"
ORIGINAL_SUMMARY="2-3 meningar som sammanfattar vad avsändaren vill/frågar. Fokus på det beslutsrelevanta."
DRAFT_SUBJECT="Sv: Originalämne"
DRAFT_BODY="Hela utkasttexten här — inkludera hälsningsfras, brödtext och avslutning."
```

**b) Skapa draft:**
```bash
# Hitta repot dynamiskt — fungerar oavsett session-ID eller maskin
REPO=$(find /sessions -maxdepth 4 -name "superintelligent-ai-os" -type d 2>/dev/null | head -1)
if [[ -z "$REPO" ]]; then
  REPO="$HOME/Github/Superintelligent/superintelligent-ai-os"
fi
cd "$REPO"

OUTPUT=$(python3 scripts/outlook/sandbox/create_draft.py \
  --to "$ORIGINAL_FROM" \
  --subject "$DRAFT_SUBJECT" \
  --body "$DRAFT_BODY" 2>&1)

echo "$OUTPUT"
DRAFT_ID=$(echo "$OUTPUT" | grep '^DRAFT_ID=' | cut -d= -f2)
RECIPIENT_COUNT=$(echo "$OUTPUT" | grep '^RECIPIENT_COUNT=' | cut -d= -f2)
HAS_ATTACHMENT=$(echo "$OUTPUT" | grep '^HAS_ATTACHMENT=' | cut -d= -f2)
```

**c) Om DRAFT_ID är tomt:** logga felet och fortsätt med nästa email.

**d) Skicka Telegram-notis:**
```bash
ATTACH_FLAG=""
[ "$HAS_ATTACHMENT" = "true" ] && ATTACH_FLAG="--has-attachment"

python3 scripts/outlook/sandbox/telegram_notify.py \
  --id "$DRAFT_ID" \
  --priority "$PRIORITY" \
  --original-from "$ORIGINAL_FROM" \
  --original-subject "$ORIGINAL_SUBJECT" \
  --original-summary "$ORIGINAL_SUMMARY" \
  --draft-subject "$DRAFT_SUBJECT" \
  --draft-body "$DRAFT_BODY" \
  --recipient-count "${RECIPIENT_COUNT:-1}" \
  $ATTACH_FLAG
```

Skapa max 5 drafts per körning. Om fler än 5 email kvalificerar: prioritera Nivå 1 och de mest tidskritiska Nivå 2.

## Riktlinjer för ORIGINAL_SUMMARY

- Max 3 meningar
- Inkludera: vad avsändaren vill, eventuell deadline, vad som blockeras om inget svar ges
- Exkludera: hälsningsfraser och metadata
- Exempel: "Willis Towers Watson skickar erbjudande och faktura för dolda felförsäkring (Grophuset 4, ref 31809). Försäkringen aktiveras genom betalning. Erbjudandet annulleras automatiskt om fakturan inte betalas."

## Riktlinjer för DRAFT_BODY

- Inkludera hela utkastet: hälsning, brödtext och avslutning
- Tonen: varm, tydlig, mänsklig — ej robotaktig
- Skriv på svenska om inte avsändaren skrivit på annat språk

## Säkerhetsregler — absoluta

- Skicka ALDRIG email automatiskt. Endast drafts.
- Skapa ALDRIG draft för email som redan besvarats.
- Skapa ALDRIG draft för nyhetsbrev, massutskick eller automatiska notiser.
- Skriv ALDRIG mejlinnehåll till filer i repot.
- Ingen commit, ingen push.
- Om sandbox-skriptet returnerar "FEL: .secret/credentials.json saknas": logga tydligt och avbryt körningen.
- Om ett steg misslyckas tekniskt: fortsätt med nästa email.
