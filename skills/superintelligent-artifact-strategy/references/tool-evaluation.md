# Verktygsutvärdering

Skalan är relativ: stark, möjlig med komplettering eller svag. Kostnad avser total operativ kostnad, inte ett pris som snabbt blir inaktuellt.

| Alternativ | Styrka | Begränsning | Roll i systemet |
|---|---|---|---|
| Ren HTML/CSS/JavaScript | Full kontroll, semantik, Git-diff, lokal/offline och valfri hosting utan ramverksruntime. | Kräver egen komponentdisciplin, presenter mode och QA. | Vald pilotbas för narrativ webb och begränsad slide-runtime. |
| Reveal.js | Moget presenter mode, notes, timer, tangentbord och PDF-export. | Node/npm eller vendoring; webbramverkets flexibilitet kan ge inkonsekvent design. | Rekommenderad uppgradering för avancerade live-deck när beroendet motiveras. |
| Marp | Enkel Markdown, deterministisk CLI och export till HTML/PDF/PPTX. | Mindre fritt komponent- och interaktionssystem; PPTX-export måste testas för redigerbarhet. | Bra för textnära, reproducerbara deck. |
| Slidev | Stark utvecklarupplevelse, presenterfunktioner och export. | Större frontend-/Playwright-beroende; PPTX-exporten kan vara bildbaserad. | Specialistval för kod- och demotunga presentationer. |
| Codex Sites | Snabb build-to-publish och enkel delning i stödd miljö. | Kontotillgänglighet, region, betaegenskaper och hostingkontroll gör det olämpligt som kanoniskt format. | Valfri publiceringsadapter efter separat kontroll av åtkomst och livscykel. |
| Leverantörsneutral statisk hosting | Billig, portabel, cachebar och lätt att koppla till egen domän. | Åtkomstkontroll, formulär, analytics och drift varierar mellan adapters. | Standard för publicering när webb är valt. |
| Gamma | Snabb layout, webbdelning, PDF/PPTX-export och analytics i vissa planer. | Konto-/planberoende, begränsad Git-reproducerbarhet, svagare kontroll och export som kräver QA. | Behåll som valfritt undantag under pilot. |
| PowerPoint | Starkast scenläge, notes, offline och redigerbar kundöverlämning i Microsoft-miljö. | Binär diff, konverteringsrisk och svagare semantik/mobil webbupplevelse. | Standard när redigerbar PPTX eller PowerPoint Live krävs. |
| Google Slides | Stark samredigering, presenter view och enkel länkdelning/export. | Moln- och Workspace-beroende; offline och exakt layout kräver verifiering. | Standard när kunden arbetar vidare i Google Workspace. |

## Tvärgående bedömning

- **Visuell kvalitet och brand:** kodbaserade tokens ger bäst kontroll men kräver designkompetens; Gamma ger snabbare baseline men mindre determinism.
- **Tillgänglighet och maskinläsbarhet:** semantisk webb har högst potential, men endast när komponenterna faktiskt använder korrekta element och fokusordning.
- **Mobil:** narrativ webb vinner. Slides bör ge en separat handout eller webbversion i stället för att utge sig för att vara responsiva.
- **PDF/print:** Chromium-baserad export är reproducerbar men måste render-testas. PowerPoint har mogen print/export men plattformsvariationer finns.
- **Git/reproducerbarhet:** JSON, CSS, JS och Markdown är diffbara; binära deck och SaaS-original är svagare.
- **Sekretess/GDPR:** egen statisk hosting utan analytics minimerar dataflöden. SaaS-delning och analytics kräver avtal, ändamål, retention och åtkomstgranskning.
- **Kostnad/kompetens:** statisk webb har låg driftkostnad men högre initial systemkompetens; SaaS har låg starttröskel men återkommande licens och exitkostnad.
- **Låsning:** separera källa från renderer och hosting. Exportmöjlighet är inte samma sak som reversibel redigering.

