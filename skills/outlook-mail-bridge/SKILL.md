# Skill: Outlook Mail Bridge v0.1

Skapar, granskar och skickar Outlook-mejl via Microsoft Graph — direkt från Cowork, utan att öppna Outlook.

## Aktivering

Läs denna skill när användaren ber om:

- "Skriv ett mejl till [person]"
- "Svara på mejlet från [person]"
- "Skicka ett mail om [ämne]"
- "Skapa ett utkast till [mottagare]"
- "Visa draft D42" / "Granska D42"
- "OK D42" / "OK D42 B" / "OK D42 FM" / "OK D42 B FM"

## Scripts och verktyg

| Script | Syfte |
|---|---|
| `scripts/outlook/create_draft.py` | Skapa nytt draft via Graph |
| `scripts/outlook/create_reply_draft.py` | Skapa reply-draft på befintligt mejl |
| `scripts/outlook/review_draft.py` | Hämta draft från Graph och visa full review |
| `scripts/outlook/send_draft.py` | Skicka draft efter strikt OK-validering |
| `scripts/outlook/list_drafts.py` | Lista aktiva drafts med korta ID:n |

Se `references/` för Graph-endpoints, permissions, flödesbeskrivningar och OK-kommandospecifikation.

---

## Flöde: Skapa nytt mejl

### Steg 1 — Extrahera fält
Identifiera från användarens instruktion:
- **To** (obligatoriskt) — en eller flera adresser
- **CC** (valfritt)
- **BCC** (valfritt)
- **Subject** — fråga om det saknas
- **Body** — fråga om det saknas eller är vagt

Fråga om oklara fält innan du kör något script.

### Steg 2 — Skapa draft
```bash
python scripts/outlook/create_draft.py \
  --to "anna@example.com" \
  --subject "Ämne" \
  --body "Brödtext"
```
Scriptet returnerar ett kort draft-ID (t.ex. `D42`) och skriver det till lokal state-fil utanför repot.

### Steg 3 — Visa review (obligatoriskt)
```bash
python scripts/outlook/review_draft.py --id D42
```
Visa alltid full review innan du presenterar OK-alternativet. Review måste visas i samma session innan OK accepteras.

### Steg 4 — Vänta på OK
Presentera exakt vilket kommando som krävs (scriptet skriver det). Vänta. Acceptera inget annat.

Se [send-mode.md](references/send-mode.md) för exakt grammar och vad som ska avvisas.

### Steg 5 — Skicka
```bash
python scripts/outlook/send_draft.py "OK D42"
# eller med tokens:
python scripts/outlook/send_draft.py "OK D42 B"
python scripts/outlook/send_draft.py "OK D42 FM"
python scripts/outlook/send_draft.py "OK D42 B FM"
```
Scriptet hämtar draften på nytt från Graph, verifierar review-hash, räknar mottagare och validerar tokens innan det skickar.

---

## Flöde: Reply-draft

1. Identifiera original-mejlets message-ID (från inbox-triage eller Graph-sökning).
2. Kör `create_reply_draft.py --message-id <graph_id> --body "Svarstext"`.
3. Visa review med `review_draft.py --id D43`.
4. Vänta på OK-kommando.
5. Skicka med `send_draft.py`.

---

## Säkerhetsregler — ABSOLUTA

1. **Skicka aldrig automatiskt.** Inte från scheduled tasks, inte från notiser, inte från implicita kommandon.
2. **Visa alltid full review** innan OK-alternativet presenteras. Inget undantag.
3. **Acceptera bara exakt OK-kommando** enligt grammatiken i [send-mode.md](references/send-mode.md).
4. **Dessa fraser triggar aldrig sending:** `ok`, `skicka`, `ja`, `kör`, `ser bra ut`, `yes`, `send`, `looks good`, `go ahead`.
5. **Skapa aldrig privat data i repot.** Inga mejladresser, ingen brödtext, inga kunduppgifter, inga tokens.
6. **Ingen commit, ingen push** utan explicit godkännande från användaren.
7. **Radera aldrig drafts** i v0.1 — funktionen är ej implementerad.
8. **Ladda aldrig upp bilagor** i v0.1 — funktionen är ej implementerad. Detektera och flagga befintliga bilagor.

---

## Vad v0.1 stöder och inte stöder

| Funktion | v0.1 |
|---|---|
| Skapa nytt draft | ✓ |
| Skapa reply-draft | ✓ |
| Visa full review | ✓ |
| Skicka med OK-kommando | ✓ |
| Detektera bilaga (kräv B-token) | ✓ |
| Hantera fler än 3 mottagare (kräv FM-token) | ✓ |
| Lista aktiva drafts | ✓ |
| Radera draft | ✗ (fas 2) |
| Ladda upp bilaga | ✗ (fas 2) |
| Telegram/mobil-godkännande | ✗ (fas 2) |
