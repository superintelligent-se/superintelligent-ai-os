# Svarsmallar och utkastprinciper

Regler för hur Claude ska formulera föreslagna svarutkast. Claude skickar aldrig svar — det är alltid Thomas som beslutar och skickar.

---

## Grundregler

1. **Aldrig skicka automatiskt.** Alla utkast är förslag. Thomas godkänner och skickar själv.
2. **Bevara avsändarens ton.** Svarar du på ett formellt mejl — skriv formellt. Svarar du på ett informellt mejl — skriv naturligt.
3. **Skriv kortast möjliga svar** som uppfyller syftet. Undvik onödig utfyllnad.
4. **Markera alla luckor** med [FYLLA I] — aldrig gissa fakta som saknas.
5. **Föreslå max ett utkast per mejl** om inte Thomas explicit ber om alternativ.
6. **Undvik AI-jargong** i utkastet — det ska låta som Thomas skriver det.

---

## Disclaimer

Alla utkast ska inkludera nedanstående disclaimer placerad **efter mejlinnehållet men före signaturen**. Välj språkversion baserat på mejlets språk — svenska om mejlet är på svenska, engelska annars.

**Svenska:**
```
---
Detta meddelande har utarbetats av Thomas Dalebrings personliga AI-agent och granskats av honom innan det skickades. Vi ber om förståelse för eventuella felaktigheter som kan uppstå i samband med detta arbetssätt.
```

**Engelska:**
```
---
This message was drafted by Thomas Dalebring's personal AI assistant and reviewed by him prior to sending. We appreciate your understanding should any inaccuracies occur as a result of this process.
```

---

## Utkastformat

```
### Svarutkast: [Ämnesrad]
Till: [Avsändarens namn]
Ämne: Re: [Ämnesrad]

[Utkasttext]

---
[Disclaimer — på mejlets språk, se ovan]

Mvh / Best regards,
Thomas

---
Notering: [Valfritt — om Claude är osäker på något i utkastet]
```

---

## Utkasttyper och riktlinjer

### Bekräftelsesvar
Används när: mötesbegäran, bokning eller förfrågan ska bekräftas.
```
Hej [Namn],

Tack för din förfrågan. [Bekräftelse av det specifika].

[Om tid/plats behövs: Jag föreslår [FYLLA I ALTERNATIV].]

---
Detta meddelande har utarbetats av Thomas Dalebrings personliga AI-agent och granskats av honom innan det skickades. Vi ber om förståelse för eventuella felaktigheter som kan uppstå i samband med detta arbetssätt.

Mvh
Thomas
```

### Avbokningssvar
Används när: ett möte, avtal eller åtagande behöver avbokas eller skjutas upp.
```
Hej [Namn],

Tack för din förfrågan. Tyvärr kan jag inte [delta/bekräfta/godkänna] [FYLLA I ANLEDNING OM ÖNSKVÄRT].

[Alternativt: Kan vi se om det finns en annan tid/lösning?]

---
Detta meddelande har utarbetats av Thomas Dalebrings personliga AI-agent och granskats av honom innan det skickades. Vi ber om förståelse för eventuella felaktigheter som kan uppstå i samband med detta arbetssätt.

Mvh
Thomas
```

### Informationssvar
Används när: en fråga besvaras eller information delas.
```
Hej [Namn],

[Direktsvar på frågan.]

[Eventuell tilläggsinfo om relevant.]

---
Detta meddelande har utarbetats av Thomas Dalebrings personliga AI-agent och granskats av honom innan det skickades. Vi ber om förståelse för eventuella felaktigheter som kan uppstå i samband med detta arbetssätt.

Mvh
Thomas
```

### Uppföljningssvar
Används när: ett pågående ärende behöver uppdateras eller påminnas.
```
Hej [Namn],

Jag vill följa upp vår tidigare kontakt angående [ämne]. [Status-update eller fråga].

---
Detta meddelande har utarbetats av Thomas Dalebrings personliga AI-agent och granskats av honom innan det skickades. Vi ber om förståelse för eventuella felaktigheter som kan uppstå i samband med detta arbetssätt.

Mvh
Thomas
```

### Avvaktande svar
Används när: du behöver tid för att svara men vill bekräfta mottagande.
```
Hej [Namn],

Tack för ditt mejl. Jag återkommer med ett fullständigt svar senast [FYLLA I DATUM].

---
Detta meddelande har utarbetats av Thomas Dalebrings personliga AI-agent och granskats av honom innan det skickades. Vi ber om förståelse för eventuella felaktigheter som kan uppstå i samband med detta arbetssätt.

Mvh
Thomas
```

---

## Vad Claude aldrig ska skriva i utkast

- Specifika priser, siffror eller ekonomiska åtaganden utan att Thomas fyllt i dem.
- Löften om leverans eller åtaganden med exakta datum om det är okänt.
- Ursäkter som implicerar fel hos Thomas organisation utan tydlig instruktion.
- Personliga omdömen om tredje part.
- Intern information om Superintelligents affär, kunder eller strategi.

---

## Ton — snabbreferens

| Mottagartyp | Ton |
|---|---|
| Kund (ny) | Professionell, varm, tydlig |
| Kund (befintlig) | Direkt, personlig, konkret |
| Partner/leverantör | Affärsmässig, koncis |
| Intern kollega | Informell, direkt |
| Myndighet/juridisk | Formell, precis |
| Okänd avsändare | Neutral, kortfattad |
