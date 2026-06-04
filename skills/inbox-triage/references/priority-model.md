# Prioritetsmodell

Tre nivåer med tydliga kriterier. Varje mejl tilldelas exakt en nivå.

---

## Nivå 1 — Akut / Kräver min action

**Definition:** Kräver ett beslut, svar eller handling inom 4 timmar. Konsekvensen av att inte agera är påtaglig (ekonomisk, relationell, juridisk eller operativ).

**Kriterier — minst ett ska uppfyllas:**
- Explicit deadline inom 24 timmar
- Ekonomisk åtgärd krävs (faktura förfaller, avtal ska signeras, offert svaras)
- Kund uttrycker missnöje, hot om avslut eller eskalering
- Beslutsförfrågan från person i beroendeposition (de kan inte gå vidare utan svar)
- Mötesbegäran som kräver svar för att hålla eller boka tid
- Juridisk, compliance- eller säkerhetsrelevant fråga
- Avsändare är VD, styrelseledamot, nyckelkund eller extern partner på hög nivå

**Outputformat för varje mejl på nivå 1:**
```
📌 [Ämnesrad] — [Avsändare]
Kräver: [vad som behöver göras]
Deadline: [om känd]
Föreslagen handling: [konkret nästa steg]
```

---

## Nivå 2 — Bör hanteras idag

**Definition:** Bör läsas och hanteras under arbetsdagen, men konsekvensen av att vänta några timmar är begränsad.

**Kriterier:**
- Relevant fråga eller förfrågan utan explicit deadline
- Intern kommunikation som kräver ett svar men inte är brådskande
- Uppföljning på pågående ärenden
- Mötesinbjudan utan omedelbar tidspress
- Information som är relevant för beslut som ska fattas inom 1–2 dagar

**Outputformat för varje mejl på nivå 2:**
```
📋 [Ämnesrad] — [Avsändare]
Handling: [vad som bör göras]
Förslag: [hur hantera det]
```

---

## Nivå 3 — Låg prioritet

**Definition:** Kan läsas när tid finns. Kräver ingen handling eller handling kan skjutas upp utan konsekvens.

**Kriterier:**
- Nyhetsbrev, massutskick, abonnemang
- Automatiska bekräftelser (bokningar, ordrar, kvitton)
- CC-mejl där du inte är primär mottagare
- Systemnotiser och automatiska digests
- Interna informationsutskick utan deadline
- Uppdateringar av typ "för kännedom"

**Outputformat för varje mejl på nivå 3:**
```
ℹ️ [Ämnesrad] — [Avsändare]
```
(Ingen ytterligare kommentar om inget är anmärkningsvärt.)

---

## Specialfall

### Väntar på andra
Mejl där du är primär mottagare men handlingen ligger hos en annan person — du väntar på deras svar, bekräftelse eller leverans.

```
⏳ [Ämnesrad] — [Avsändare]
Väntar på: [vem / vad]
Uppföljning: [om relevant — när du bör återkomma]
```

### Behöver mänsklig bedömning
Mejl som Claude inte kan klassificera med tillräcklig säkerhet.

```
❓ [Ämnesrad] — [Avsändare]
Anledning: [varför osäker klassificering]
```
