# Send Mode — OK-kommando grammar och validering (v0.1)

## Grammar

```
OK <draft_id> [B] [FM]
```

- `draft_id`: kort ID på formen `D` följt av ett positivt heltal, t.ex. `D1`, `D42`, `D100`
- `B`: obligatorisk token om draften har bilaga
- `FM`: obligatorisk token om totalt antal mottagare (To + CC + BCC) är fler än 3
- `B` ska komma före `FM` om båda anges (kanonisk ordning)
- Case-insensitivt: `ok d42 b fm` normaliseras internt till `OK D42 B FM`

### Giltiga kommandon

| Situation | Exakt kommando |
|---|---|
| Ingen bilaga, ≤3 mottagare | `OK D42` |
| Bilaga, ≤3 mottagare | `OK D42 B` |
| Ingen bilaga, >3 mottagare | `OK D42 FM` |
| Bilaga + >3 mottagare | `OK D42 B FM` |

---

## Avvisade fraser

Dessa avvisas alltid med felmeddelande, oavsett kontext:

| Inmatning | Svar |
|---|---|
| `OK` | "Ange draft-ID. Använd: OK D\<nummer\>" |
| `ok` | "Ange draft-ID. Använd: OK D\<nummer\>" |
| `skicka` | "Okänt kommando. Bekräfta med: OK D\<nummer\>" |
| `ja` | "Okänt kommando. Bekräfta med: OK D\<nummer\>" |
| `kör` | "Okänt kommando. Bekräfta med: OK D\<nummer\>" |
| `ser bra ut` | "Okänt kommando. Bekräfta med: OK D\<nummer\>" |
| `yes` | "Okänt kommando. Bekräfta med: OK D\<nummer\>" |
| `send` | "Okänt kommando. Bekräfta med: OK D\<nummer\>" |
| `OK B` (utan ID) | "Ange draft-ID. Använd: OK D\<nummer\> B" |
| `OK FM` (utan ID) | "Ange draft-ID. Använd: OK D\<nummer\> FM" |
| `OK D99` (fel ID) | "Inget aktivt draft med ID D99. Aktiva drafts: D42" |
| `OK D42` när B krävs | "Draften har bilaga. Bekräfta med: OK D42 B" |
| `OK D42` när FM krävs | "Draften har 4 mottagare. Bekräfta med: OK D42 FM" |
| `OK D42 B` när FM krävs | "Draften har 4 mottagare. Bekräfta med: OK D42 B FM" |

---

## Valideringsordning i send_draft.py

`send_draft.py` utför valideringsstegen i denna ordning:

1. **Parsa OK-kommandot** — regex fullmatch, normalisera till versaler
2. **Kontrollera att draft-ID finns** i lokal state-fil
3. **Kontrollera att review har visats** (`reviewed_at` är satt)
4. **Re-hämta draft från Graph** — `GET /me/messages/{id}`
5. **Verifiera review_hash** — beräkna ny hash, jämför med lagrad hash
6. **Räkna mottagare på nytt** från Graph-svaret
7. **Kontrollera bilaga på nytt** från Graph-svaret (`hasAttachments`)
8. **Validera tokens** mot aktuella värden (B, FM)
9. **Skicka** — `POST /me/messages/{id}/send`

Varje steg kan stoppa processen med ett tydligt felmeddelande. Sending sker enbart om alla steg passerar.

---

## Varför re-fetch före send?

Draften kan ha ändrats manuellt i Outlook mellan review och send. Re-fetch fångar:
- Tillagda mottagare (FM-krav kan ha förändrats)
- Tillagda bilagor (B-krav kan ha förändrats)
- Ändrad brödtext (hash stämmer inte längre)

Om re-fetch visar förändring stoppas sending och användaren ombeds granska på nytt.

---

## Flöde i Cowork-chatten

```
Användare:  Skriv ett mejl till anna@company.com om projektuppdateringen.

Cowork:     [kör create_draft.py]
            [kör review_draft.py — visar full review]

            📧 Draft D42 — Redo för granskning
            ...
            För att skicka: OK D42

Användare:  OK D42

Cowork:     [kör send_draft.py "OK D42"]
            ✓ Mejl skickat (D42)
```

---

## Cowork-regler

- Cowork presenterar aldrig OK-alternativet utan att ha visat review.
- Cowork avvisar vaga fraser utan att fråga "menade du OK D42?" — kräv exakt format.
- Cowork förklarar aldrig varför den inte skickar med meningar som "jag kan skicka om du..." — avvisa bara med exakt felmeddelande och korrekt format.
