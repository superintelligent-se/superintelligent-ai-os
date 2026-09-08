# Formatpolicy

## Beslutsordning

Bedöm syfte, publik, konsumtionssätt, livslängd, interaktivitet, sekretess, framförandesituation och redigeringsbehov innan verktyg väljs.

| Signal | Primär leverans | Komplettering |
|---|---|---|
| Talaren styr ordning, tempo och uppmärksamhet | Slides | Speaker notes, presenter mode, lokal kopia och PDF-backup. |
| Mottagaren navigerar själv | Narrativ webb | PDF när innehållet behöver arkiveras, skrivas ut eller användas offline. |
| Materialet ska hållas aktuellt | Narrativ webb med canonical URL | Versionsmärkt release och arkiverad PDF. |
| Viktigt externt förslag eller beslutsunderlag | Hybrid | Webb + PDF; slides bara när det finns ett liveframförande. |
| Mottagaren ska fortsätta redigera | PPTX eller Google Slides | Separat webb/PDF får finnas men ersätter inte originalet. |
| Åtkomst eller drift kan inte garanteras | Lokal slides/PDF | Publicerad webb är sekundär. |

Om signalerna står mot varandra, prioritera i denna ordning: nödvändig redigerbarhet, sekretess/åtkomst, liveframförande, offline/arkiv, därefter interaktivitet och analytics.

## Minimikrav per leverans

### Livepresentation

- Fast, övad sekvens och 16:9-layout.
- Speaker notes, nuvarande/nästa slide, timer och tangentbordsstyrning.
- Full funktion utan nätverk.
- PDF-backup och fontkontroll.

### Narrativ webb

- Semantisk HTML, skip-link, logisk rubrikhierarki och tangentbordsnavigering.
- Separat informationsarkitektur för desktop och mobil genom responsiv layout, inte förminskade slides.
- Inga remote runtime-assets i grundleveransen.
- Canonical URL, ägare, versionsmärkning, åtkomst och avpubliceringsplan innan publicering.

### Hybrid

- Webb är aktuell version; PDF är en märkt snapshot.
- Innehåll och källor delas, men webb- och printlayout QA:as var för sig.
- Interaktiv information måste få en begriplig statisk representation i PDF.

### Redigerbar överlämning

- Testa faktisk text-, form- och anteckningsredigering i målverktyget.
- Bildbaserad PPTX-export räknas inte som redigerbar.
- Dokumentera typsnitt, master/theme, externa länkar och eventuella konverteringsförluster.

## Livscykel och governance

Varje publicerad artefakt ska ha en ansvarig ägare, informationsklassning, release-ID eller Git-revision, granskningsdatum och avpubliceringsvillkor. Analytics är av som standard. Aktivera endast efter ändamåls-, personuppgifts- och samtyckesbedömning. Undvik tredjepartsskript när aggregerade serverloggar räcker.

En URL löser inte långsiktigt ägarskap. Bevara källan i Git, använd organisationens domän, kontrollera interna och externa länkar och arkivera viktiga releaser som PDF.

