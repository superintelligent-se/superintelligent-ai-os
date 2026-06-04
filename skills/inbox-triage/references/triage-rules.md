# Triageringsregler

Operativa regler för hur Claude ska tolka och klassificera inkommande e-post.

## Grundprinciper

1. **Läs alltid hela ämnesraden och minst de första raderna** innan klassificering.
2. **Tveka inte att eskalera** — hellre Akut än missat en deadline.
3. **Vid osäkerhet:** markera som "Behöver mänsklig bedömning" snarare än att gissa.
4. **Kontextkänslighet:** avsändare väger tungt. En VD-direktör är alltid Akut. Ett nyhetsbrev från okänd avsändare är alltid Låg.
5. **Aggregera trådar:** om en e-posttråd innehåller flera meddelanden, triagera baserat på det senaste mejlet i tråden.

## Signaler som höjer prioritet

| Signal | Exempel |
|---|---|
| Deadline nämns explicit | "senast imorgon", "before EOD", "fredag" |
| Ekonomisk åtgärd krävs | faktura, betalning, avtal, offert som förfaller |
| Kundrisk | klagomål, avslut, eskalering från kund |
| Beslutsförfrågan | "kan du godkänna", "behöver ditt svar för att gå vidare" |
| Mötesbegäran med tydlig tid | kalenderbegäran, "kan vi ses imorgon" |
| Avsändare är chef, styrelsemedlem, nyckelkund | prioritera oavsett innehåll |
| Juridisk eller compliance-relevant | avtal, GDPR, revision, tillstånd |

## Signaler som sänker prioritet

| Signal | Exempel |
|---|---|
| Nyhetsbrev eller massutskick | unsubscribe-länk, "Vi vill informera alla..." |
| Automatisk bekräftelse | orderbekräftelse, bokningsbekräftelse, kvitto |
| CC utan tydlig handling | du är bara cc:ad och texten riktar sig till annan |
| Systemnotis | automatiserade varningar från system, digests |
| Intern information utan deadline | interna uppdateringar, protokoll, FYI-mejl |

## Tolkningsregler för ostrukturerade mejl

- Mejl utan ämnesrad: klassificera som Medelprioritet och flagga.
- Mejl på okänt språk: klassificera som "Behöver mänsklig bedömning".
- Vidarebefordrade mejl: triagera baserat på det vidarebefordrade innehållet, inte omslagskommentaren.
- Bilagor: om bilagan nämns som kritisk (avtal, faktura) — höj prioritet.

## Tidsgränser

- **Akut:** kräver svar eller handling inom 4 timmar.
- **Bör hanteras idag:** kräver svar eller handling innan arbetsdagens slut.
- **Väntar på andra:** ingen omedelbar handling, men bevaka.
- **Endast information:** kan läsas när tid finns, ingen deadline.

## Vad som aldrig ska klassificeras som Låg

- Mejl från kunder (oavsett innehåll).
- Mejl som nämner ett namn Claude vet är nyckelkontakt.
- Mejl med bilagor märkta "Avtal", "Kontrakt", "Invoice".
