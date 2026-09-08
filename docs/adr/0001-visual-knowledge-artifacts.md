# ADR 0001: HTML-first, inte HTML-only

- Status: Accepterad för pilot
- Datum: 2026-09-08

## Kontext

AI Daily Brief argumenterar för webbplatsen som kunskapsarbetets nya ankare: en kanonisk, navigerbar och uppdateringsbar URL i stället för versionshanterade bilagor. Tesens styrka är asynkron konsumtion, semantisk HTML, interaktivitet och uppdaterbarhet. Den överskattar däremot webbformatets lämplighet för talarledd dramaturgi, offline-säkerhet, arkivbeständighet och redigerbar överlämning.

Repots nuvarande Claude-regel gör Gamma obligatoriskt för alla presentationer. Det blandar ihop livepresentation, narrativ webb, dokumentdistribution och redigerbar överlämning samt skapar leverantörslåsning.

## Beslut

Vi inför **HTML-first, inte HTML-only**:

1. Narrativ, asynkron eller levande kunskap levereras normalt som semantisk statisk webb.
2. Talarledda liveframföranden levereras som slides med fast sekvens, speaker notes, presenter mode och verifierad offline-drift.
3. Viktiga externa leveranser är hybrider: aktuell webb, deterministisk PDF-backup och vid behov separata slides.
4. PPTX eller Google Slides används när mottagaren måste kunna redigera i sitt etablerade verktyg.
5. Gamma behålls som valfritt undantag under en verifierad pilot. Det får inte vara obligatorisk renderer eller kanonisk källa.
6. Kanoniskt innehåll lagras strukturerat och skiljs från webbens informationsarkitektur, slide-sekvens, design tokens, komponenter, rendering, publicering, export och QA.
7. Grundsystemet är lokal statisk HTML/CSS/JavaScript utan runtime-beroende på nätverk. Hosting är en utbytbar adapter.

Tre skills implementerar beslutet:

- `superintelligent-artifact-strategy`: tunn router och gemensamt innehålls-/renderingssystem.
- `superintelligent-presentations`: livepresentationsspecifik dramaturgi, presenter experience och slide-QA.
- `superintelligent-narrative-sites`: informationsarkitektur, responsivitet, semantik, tillgänglighet och webbpublicering.

`superintelligent-brand` förblir kanonisk källa för språk och varumärke. Bygg-skillsen läser den; de kopierar inte dess regler.

## Konsekvenser

- Webb och slides kan dela innehåll och tokens utan att dela layoutmodell.
- Git lagrar reproducerbar källa; PDF och publicerade URL:er är härledda leveranser.
- Statisk hosting kan bytas utan innehållsmigrering. Åtkomstkontroll, analytics, samtycke, retention och avpublicering måste däremot beslutas per adapter.
- En canonical URL minskar bilageversioner men eliminerar inte versionsstyrning. Varje release ska kunna kopplas till en Git-revision och arkiverad PDF.
- Webben tillför livscykelansvar: domän, länkkontroll, ägarskap, GDPR-bedömning, drift och avpublicering.
- PPTX-export från webbslides betraktas inte automatiskt som redigerbar överlämning; redigerbarhet måste verifieras i målverktyget.

## Alternativ som avvisades

- **HTML-only:** brister för presenter mode, offline-risk, reglerade arkiv och redigerbar överlämning.
- **Gamma-first:** snabb produktion men otillräcklig reproducerbarhet och kontroll som generell grundmodell.
- **Slides-first:** passar scenen men gör självstyrd läsning, mobil, sökbarhet och levande innehåll sämre.
- **En catch-all-skill:** otydlig aktivering och sammanblandad QA.

## Evidens

- [AI Daily Brief: 10+ Things You Should Build With AI Instead of Sending Files](https://aidailybrief.ai/e/2026-06-07)
- [Reveal.js: speaker view](https://revealjs.com/speaker-view/) och [PDF export](https://revealjs.com/pdf-export/)
- [Marp: Markdown Presentation Ecosystem](https://marp.app/)
- [Slidev: exporting](https://sli.dev/guide/exporting)
- [Microsoft: PowerPoint Presenter View](https://support.microsoft.com/en-us/office/present-on-multiple-monitors-and-view-speaker-notes-privately-ccfa1894-e3ef-4955-9c3a-444d58248093)
- [Google: present and export Slides](https://support.google.com/a/users/answer/9310270?hl=en)
- [Gamma plans and capabilities](https://gamma.app/pricing)

