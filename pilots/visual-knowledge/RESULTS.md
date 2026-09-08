# Pilotresultat

Datum: 2026-09-08  
Systemversion: 0.2.0
Omfattning: lokal vanilla HTML/CSS/JavaScript-renderer, tre artefakter och en PDF-backup. Ingen Gamma-, PowerPoint-, Google Slides- eller hostingpublicering genomfördes i denna pilot.

## Sammanfattning

Piloten visar att ett begränsat, Git-versionerat system kan producera en talarledd keynote, en asynkron strategiberättelse och ett interaktivt kundförslag från samma innehållsmodell, officiella logotypassets och brand tokens utan nätverksberoende. Resultatet räcker för att införa HTML-first-routing och fortsätta pilotera. Det räcker inte för att fasa ut Gamma eller ersätta PPTX/Google Slides vid redigerbar överlämning.

## Mätresultat

Skala för kvalitativa värden: 1 = otillräckligt, 3 = användbart med tydliga begränsningar, 5 = verifierat starkt för pilotens krav.

| Dimension | Resultat | Evidens och avgränsning |
|---|---:|---|
| Produktionstid | cirka 2 h 30 min | Omfattar research, ADR, systemimplementation, tre piloter och två visuella korrigeringsvarv. Ren omrendering av alla tre HTML-artefakter tog 0,04 s. |
| Visuell kvalitet | 4/5 | Clear Intelligent Premium, tydlig typografi, whitespace, officiell wordmark/Picture Mark och kontrollerad lila accent. Bedömd via samtliga åtta slides, webb-screenshots och fyra PDF-sidor. Ingen jämförelse med professionell designer eller Gamma gjordes. |
| Konsekvens mellan leveranser | 5/5 | Alla använder samma `content.json`, normaliserade logoassets, tokens, komponentrenderer och källhash. Webb och slides har separata layout-CSS. |
| Mobil användbarhet | 4/5 | Exakt 390x844 emulering gav `scrollWidth=390` och inga element utanför viewport för båda webbartefakterna. Navigationen bryts till två rader; vidare test på fysisk enhet återstår. |
| Offline-funktion | 5/5 | HTML öppnades via `file://`; inga remote runtime-assets hittades. Interaktion och presenterfunktion är lokal JavaScript. |
| PDF-fidelitet | 4/5 | Taggad A4-PDF, fyra sidor, inga clip/overlap efter korrigering och full text kunde extraheras. Interaktiv kalkyl ersätts av ett statiskt, begripligt exempel. |
| Presenter experience | 4/5 | Arrow/Page/Home/End, blank med `B`, separat presenterläge, notes, nästa slide och timer verifierades. Multi-monitor, fysisk projektor och fullskärm testades inte. |
| Tillgänglighet | 4/5 | Semantiska landmarks, skip-link, rubrikhierarki, labels, `aria-live`, synligt fokus, reduced motion och tangentbordsflöde. Ingen extern WCAG-audit eller skärmläsartest genomfördes. |
| Redigerbarhet | 3/5 internt, 1/5 Office-handoff | JSON/CSS/JS är diffbart och enkelt att ändra i Git. Piloten producerar inte ett nativt redigerbart PPTX-/Google Slides-original. |
| Delningsfriktion | 4/5 lokalt | En statisk katalog och en PDF räcker. Canonical URL, åtkomstflöde och mottagartest kräver vald hostingadapter. |
| Drift- och hostingkostnad | Ej belastad | Ingen hosting köptes eller aktiverades. Runtime har ingen licensierad dependency; statisk hosting, domän, access och analytics prissätts först när adapter väljs. |
| Reproducerbarhet för annan agent | 5/5 | README-kommandot renderades i en separat `/tmp`-katalog på 0,04 s; SHA-256 för alla tre HTML-filer var identiska med pilotens `dist/`. |

## QA-protokoll

- Automatiska viewportkontroller: varje keynote-slide separat i 1440x900; 1440x1200 och 500x844 för narrative sites. macOS Chrome har en headless-minimibredd på 500 px.
- Separat browseremulering: 390x844 för strategiwebb och kundförslag, utan horisontell overflow.
- Screenshots granskades för hierarki, whitespace, clipping, logotypens kontrast/frizon, komponentflöde och mobile stacking. De ligger i `/tmp` och versionshanteras inte enligt repots policy för testartefakter.
- Förslagets kalkyl ändrades till 50 deltagare och gav väntat resultat: 120 frigjorda timmar per månad.
- Keynote navigerade från `keynote-open` till `keynote-shift` via tangentbord. Blankläge och presenterpanelen verifierades; rätt notes och nästa slide visades.
- QA hittade och korrigerade två faktiska fel: missvisande mobil screenshot på grund av Chromes minimiviewport samt processinnehåll som föll i numreringskolumnen i PDF.
- Slutlig maskinrapport: inga overflow-fel, brutna eller remote runtime-assets; logoassets och SVG-favicon laddades; en `main`-landmark per artefakt; Raleway och Inter tillgängliga i testmiljön.
- PDF: 4 A4-sidor, 265 749 byte, taggad, okrypterad och visuellt verifierad efter logotypintegrationen.

## Beroenden och kostnader

Produktion och normalisering av logotypassets kräver Python 3-standardbiblioteket. Visning kräver endast en modern webbläsare. QA och PDF-export kräver en lokal Chromium/Chrome; Poppler används för PDF-inspektion men inte för att visa leveransen. Inga npm-paket, CDN:er, externa fontanrop, konton eller betalda tjänster krävs.

Det flyttar kostnad från SaaS-licens till systemförvaltning: komponentutveckling, browser-QA, tillgänglighet och publiceringslivscykel. Statisk hosting kan vara låg kostnad men är inte kostnadsfri när egen domän, accesskontroll, loggning, support och långtidsägarskap räknas in.

## Kända begränsningar

- Komponentbiblioteket är medvetet litet och saknar avancerad media, tabeller, video, komplexa diagram och sökindex.
- Presenterläget är en pilot-runtime, inte lika moget som PowerPoint eller Reveal.js.
- Typsnitt levereras inte som fontfiler. Raleway/Inter användes lokalt; andra enheter får definierad systemfontfallback om organisationen inte väljer att paketera licensierade fontassets.
- PDF-export är Chromium-beroende och behöver omtestas vid browseruppgradering.
- Ingen fysisk iOS-/Android-, skärmläsar-, projektor- eller utskriftstest genomfördes.
- Ingen canonical URL, accesskontroll, analytics, domän, redirect eller avpubliceringsrutin implementerades; det tillhör hostingadaptern.
- Ingen verklig sekretess-/GDPR-bedömning gjordes eftersom piloterna inte innehåller person- eller kunddata och inte publicerades.
- Ingen redigerbar PPTX/Google Slides producerades; skillen routar sådana krav till respektive målformat.
- SVG är kanoniskt logoformat. PNG-, ICO- och plattformsspecifika appikoner produceras först när en faktisk publiceringsadapter kräver dem.

## Rekommendation för Gamma

**Behåll Gamma som valfritt undantag under en kontrollerad pilot.** Det nya systemet är starkare för lokal drift, brandkontroll, Git-versionering, semantisk webb, reproducerbarhet och hostingportabilitet. Denna pilot har däremot inte visat att det är snabbare eller bättre än Gamma för alla verkliga presentationsuppdrag, och har inte jämfört exportfidelitet eller redaktörsupplevelse sida vid sida.

Nästa beslutspunkt bör komma efter minst tre verkliga, informationsklassade leveranser där samma brief produceras i båda spåren och bedöms av talare, mottagare och den som ska förvalta materialet. Fasa ut Gamma först om den kodbaserade vägen vinner på total produktionstid och mottagarkvalitet utan att skapa ohållbar specialistkostnad.
