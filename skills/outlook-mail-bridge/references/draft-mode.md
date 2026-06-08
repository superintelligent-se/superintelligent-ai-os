# Draft Mode — Skapa och hantera drafts (v0.1)

## Lokal state-fil

Drafts spåras i: `~/.config/superintelligent/outlook-bridge/drafts.json`

Filen ligger **utanför repot** och committas aldrig.

### Tillåtna fält i state-filen

```json
{
  "drafts": {
    "D42": {
      "draft_id": "D42",
      "graph_message_id": "AAMkAGZj...",
      "created_at": "2026-06-04T10:23:44Z",
      "reviewed_at": "2026-06-04T10:24:12Z",
      "has_attachment": false,
      "recipient_count": 2,
      "review_hash": "sha256:a3b4c5...",
      "expires_at": "2026-06-07T10:23:44Z"
    }
  },
  "next_counter": 43
}
```

### Förbjudna fält — lagras ALDRIG i state-filen

- Mejltext / brödtext
- Ämnesrad
- Mottagaradresser
- Bilagsnamn eller bilagsinnehåll
- Kunddata eller personuppgifter av något slag

`review_hash` är ett SHA256-fingeravtryck av draft-innehållet vid review-tillfället. Det kan inte reverseras till klartext. Det används enbart för att detektera om draften ändrats efter review.

### TTL

Drafts försvinner automatiskt ur state-filen efter **72 timmar** (`expires_at`). Draften finns kvar i Outlook Drafts-mapp tills du tar bort den manuellt.

---

## Skapa nytt draft

```bash
python scripts/outlook/create_draft.py \
  --to "anna@example.com" \
  --subject "Ämne" \
  --body "Brödtext"

# Med CC och BCC:
python scripts/outlook/create_draft.py \
  --to "anna@example.com,bob@example.com" \
  --cc "charlotte@example.com" \
  --bcc "david@example.com" \
  --subject "Ämne" \
  --body "Brödtext"

# HTML-body:
python scripts/outlook/create_draft.py \
  --to "anna@example.com" \
  --subject "Ämne" \
  --body "<p>Brödtext</p>" \
  --body-type html
```

Scriptet:
1. Anropar `POST /me/messages` med `isDraft: true`
2. Registrerar `graph_message_id` i state-filen
3. Genererar nästa korta ID (`D42`, `D43`, ...)
4. Skriver ut draft-ID och instruktion om att köra review

### Output (exempel)

```
✓ Draft skapad: D42
  Mottagare: 2
  Bilaga: Nej
  Kör: python review_draft.py --id D42
```

---

## Skapa reply-draft

```bash
python scripts/outlook/create_reply_draft.py \
  --message-id "AAMkAGZj..." \
  --body "Tack för din återkoppling..."
```

Scriptet:
1. Anropar `POST /me/messages/{id}/createReply`
2. PATCHar reply-draften med svarstext
3. Registrerar i state och skriver ut draft-ID

Originalmejlets `toRecipients` + `from` blir automatiskt `toRecipients` i reply. Verifiera alltid via review att mottagarlistan är korrekt.

---

## Bilagehantering i v0.1

**Bilageuppladdning är inte implementerat i v0.1.**

Scripten detekterar `hasAttachments: true` på befintliga drafts och kräver `B`-token i OK-kommandot om bilaga finns. Om användaren vill lägga till en ny bilaga ska de göra det manuellt i Outlook och sedan använda `review_draft.py` för att uppdatera review-hash.

---

## Draft-radering i v0.1

**Draft-radering är inte implementerat i v0.1.** Drafts som inte skickas finns kvar i Outlook Drafts-mapp och kan tas bort manuellt. Lokal state-post försvinner automatiskt efter TTL.

---

## Diagram: Draft-livscykel

```
create_draft.py
      │
      ▼
  [Graph: POST /me/messages]
      │
      ▼
  state: D42 registered
  reviewed_at: null
  review_hash: null
      │
      ▼
review_draft.py
      │
      ▼
  [Graph: GET /me/messages/{id}]
      │
      ▼
  Review visas för användaren
  state: reviewed_at set
  state: review_hash set
      │
      ▼
  Användaren skriver OK D42 [B] [FM]
      │
      ▼
send_draft.py
      │
      ▼
  [Graph: GET /me/messages/{id}]  ← re-fetch alltid
  Validering: hash, mottagare, bilagor
      │
      ▼
  [Graph: POST /me/messages/{id}/send]
      │
      ▼
  Mejlet skickat
  state: draft kvarstår till TTL
```
