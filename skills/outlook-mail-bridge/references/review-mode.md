# Review Mode — Granskning innan sending (v0.1)

## Regel

**Review måste alltid visas innan ett OK-kommando kan accepteras.**

Cowork presenterar aldrig ett OK-alternativ utan att ha kört `review_draft.py` och visat fullständigt review i samma session. Om review saknas för ett draft-ID ignoreras OK-kommandot med felmeddelande.

---

## Köra review

```bash
python scripts/outlook/review_draft.py --id D42
```

Scriptet:
1. Hämtar draften från Graph: `GET /me/messages/{id}`
2. Läser lokal state för D42
3. Beräknar review_hash av hämtat innehåll
4. Skriver review_hash och reviewed_at till state-filen
5. Skriver ut fullständig review till stdout

---

## Review-format

```
────────────────────────────────────────────────────
📧 Draft D42 — Redo för granskning
────────────────────────────────────────────────────

Till:      anna@company.com
           bob@company.com
CC:        charlotte@company.com
BCC:       —
Ämne:      Projektuppdatering v3 — klar för granskning
Bilagor:   Inga

────────────────────────────────────────────────────
[Brödtext visas här i sin helhet]
────────────────────────────────────────────────────

Mottagare totalt: 3  (Till: 2 · CC: 1 · BCC: 0)
Bilagor: Nej

För att skicka: OK D42
────────────────────────────────────────────────────
```

### Review med bilaga (kräver B-token)

```
Bilagor:   Q2-rapport.pdf  [bilaga detekterad — v0.1 kan ej visa filnamn]

Mottagare totalt: 2  (Till: 2 · CC: 0 · BCC: 0)
Bilagor: Ja

För att skicka: OK D42 B
```

### Review med fler än 3 mottagare (kräver FM-token)

```
Mottagare totalt: 5  (Till: 3 · CC: 2 · BCC: 0)
Bilagor: Nej

För att skicka: OK D42 FM
```

### Review med bilaga + fler än 3 mottagare (kräver B FM)

```
Mottagare totalt: 4  (Till: 2 · CC: 1 · BCC: 1)
Bilagor: Ja

För att skicka: OK D42 B FM
```

---

## review_hash

`review_hash` beräknas som SHA256 av en kanonisk JSON-sträng innehållande:
- Sorterade To-adresser (lowercase)
- Sorterade CC-adresser (lowercase)
- Sorterade BCC-adresser (lowercase)
- Subject-string
- Body-string
- hasAttachments-boolean

Hashen lagras i state-filen som `sha256:<hex>`. Den avslöjar inte innehållet — den är ett integritetsavtryck.

`send_draft.py` hämtar draften på nytt från Graph, beräknar hashen igen och jämför med lagrad hash. Om de inte matchar (draften har ändrats sedan review) stoppas sending med felmeddelande:

```
FEL: Draften har ändrats sedan senaste review.
Kör: python review_draft.py --id D42
```

---

## Vad review INTE visar i v0.1

- Exakta bilagsnamn och storlekar (Graph returnerar dessa i ett separat anrop som inte görs i v0.1 — `hasAttachments: true` används i stället)

Detta innebär att om en draft har bilagor visas "bilaga detekterad" utan filnamn. Bilagsnamn kan visas i fas 2.
