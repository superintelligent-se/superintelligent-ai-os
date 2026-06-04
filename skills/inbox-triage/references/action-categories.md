# Handlingskategorier

Varje mejl i rapporten placeras i exakt en primär kategori. En sekundär kategori kan anges om relevant.

---

## Kategori 1: Akut / Kräver min action

Mejl som kräver ett aktivt beslut, svar eller handling inom 4 timmar.

**Undertyper:**
- `Beslut` — du måste ta ställning eller godkänna något
- `Svar krävs` — avsändaren väntar på ditt svar för att kunna gå vidare
- `Ekonomisk åtgärd` — faktura, betalning, offert, avtal som förfaller
- `Bokning/möte` — inbjudan eller förfrågan som kräver svar
- `Kundrisk` — klagomål, eskalering, hot om avslut
- `Juridisk/compliance` — avtal, GDPR, revision, tillstånd

---

## Kategori 2: Bör hanteras idag

Mejl som bör adresseras under dagen utan omedelbar kritisk tidspress.

**Undertyper:**
- `Uppföljning` — nästa steg i ett pågående ärende
- `Intern förfrågan` — kollega, team eller partner behöver input
- `Informationsinsamling` — du behöver läsa för att kunna fatta kommande beslut
- `Relationsbygge` — mejl från kontakter där ett svar håller relationen varm

---

## Kategori 3: Väntar på andra

Mejl som visar att bollen för tillfället ligger hos en annan person.

**Undertyper:**
- `Väntar på svar` — du har svarat och väntar på återkoppling
- `Väntar på leverans` — du förväntar dig ett dokument, en offert eller ett beslut
- `Bevaka` — inga åtgärder nu, men återkom om inget hänt inom X dagar

---

## Kategori 4: Endast information

Mejl du bör känna till men som inte kräver handling.

**Undertyper:**
- `FYI` — intern information, protokoll, uppdateringar
- `Bekräftelse` — orderbekräftelse, bokningsbekräftelse, kvitto
- `Nyhetsbrev/marknadsföring` — prenumererad information
- `CC` — du är kopierad men inte primär mottagare
- `Systemnotis` — automatisk notis från system, plattform eller tjänst

---

## Sekundära actiontaggar

Dessa taggar kan läggas till som komplement till primärkategorin:

| Tagg | Innebörd |
|---|---|
| `→ Svar` | Föreslaget svarutkast finns i sektion 5 |
| `→ Kalender` | Förslag på kalenderhändelse finns i sektion 6 |
| `→ Task` | Bör bli en uppgift i task-systemet |
| `→ Uppföljning [datum]` | Bör följas upp vid ett specifikt datum |
| `→ Mänsklig bedömning` | Osäker klassificering, kräver Thomas eget omdöme |

---

## Exempel på kombinationer

```
📌 Offert förfaller imorgon — Leverantör AB
Kategori: Akut → Ekonomisk åtgärd → Svar
Handling: Bekräfta eller avböj offerten
→ Svar (utkast i sektion 5)
```

```
⏳ Re: Projektplan v2 — Anna Eriksson
Kategori: Väntar på andra → Väntar på leverans
Väntar på: Annas reviderade version
→ Uppföljning 2026-06-09
```
