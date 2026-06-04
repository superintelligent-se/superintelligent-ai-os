# Notisformat

Format för kritiska notiser som kan användas för Telegram-meddelanden eller desktop-notiser. Notifieringsinfrastruktur byggs inte ännu — detta är förberedande specifikation.

---

## Syfte

När inkorgsrapporten innehåller ett eller flera mejl klassificerade som Akut, ska Claude förbereda en kort notistext. Denna text är avsedd för att skickas till Thomas via Telegram eller desktop-notis i ett framtida steg.

**Claude skickar aldrig notisen själv.** Texten förbereds och visas i rapporten under sektion 7.

---

## Notisformat — standard

```
🔴 INKORG: [antal] akuta mejl kräver action

[Ämnesrad 1] — [Avsändare] ([tidsstämpel])
[Ämnesrad 2] — [Avsändare] ([tidsstämpel])
...

Öppna inkorgsrapporten för detaljer.
```

**Exempel:**
```
🔴 INKORG: 2 akuta mejl kräver action

Offert förfaller imorgon — Leverantör AB (09:14)
Kundeskalering — Kund X (10:02)

Öppna inkorgsrapporten för detaljer.
```

---

## Notisformat — enskilt kritiskt mejl

Om ett enskilt mejl är extremt brådskande (t.ex. kundeskalering, ekonomisk kris, juridisk notis):

```
🔴 KRITISKT: [Ämnesrad]
Från: [Avsändare]
Tid: [Tidsstämpel]
Handling: [En mening om vad som krävs]
```

**Exempel:**
```
🔴 KRITISKT: Avtal kräver signatur senast 12:00
Från: Advokat AB
Tid: 08:47
Handling: Signera eller kontakta advokaten omgående.
```

---

## Notisformat — ingen akut post

Om inkorgsrapporten inte innehåller något på nivå 1:

```
✅ INKORG: Inget akut. [X] mejl totalt — [Y] kräver handling idag.
```

**Exempel:**
```
✅ INKORG: Inget akut. 14 mejl totalt — 3 kräver handling idag.
```

---

## Teknisk specifikation (för framtida implementation)

När notifieringssystem byggs, ska följande parametrar stödjas:

| Parameter | Värde |
|---|---|
| Kanal | Telegram (primär), Desktop-notis (sekundär) |
| Trigger | Manuell körning av inbox-triage, eller schemalagd task |
| Frekvens | Max 1 notis per körning, sammanslagen om flera akuta |
| Format | Ren text, max 3 rader + handlingstext |
| Prioritetströskel | Skicka notis om minst 1 mejl på Nivå 1 finns |
| Innehåll | Aldrig mejlinnehåll, alltid metadata (ämne, avsändare, tid) |

---

## Integritetsprinciper för notiser

- Notistexten innehåller **aldrig mejlinnehåll**, bara metadata (ämnesrad, avsändare, tid).
- Notistexten skickas **aldrig till tredje part**.
- Om avsändarens namn är känsligt (t.ex. personuppgifter, intern HR) — ersätt med generisk beskrivning.
