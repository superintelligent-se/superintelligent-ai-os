# Innehållsmodell och komponenter

Källfilen är JSON med `system_version` och en lista `artifacts`. Varje artefakt anger `id`, `mode`, `title`, `audience`, `purpose` och `components`. Tillåtna mode är `slides`, `site` och `hybrid`.

Komponentbiblioteket är avsiktligt begränsat:

- `hero`
- `section`
- `key_insight`
- `evidence`
- `comparison`
- `process`
- `timeline`
- `data_visualization`
- `quote`
- `case_study`
- `decision`
- `calculator`
- `cta`
- `appendix`

Alla komponenter kräver `type`, `title` och stabilt `id`. Textinnehåll anges i `body`; strukturerat innehåll i `items`. Slides kan dessutom ha `notes`. `calculator` använder explicita numeriska `inputs` och ska ha ett statiskt `fallback` för utskrift.

Innehållet får inte bädda in fri HTML, CSS eller JavaScript. Nya komponenttyper ska införas i schema, renderer, båda layoutmodellerna och QA tillsammans. Lägg inte till en komponent enbart för att lösa en enstaka visuell avvikelse.

Källor hör till `sources` med `title`, `url` och vid behov `accessed`. Renderad output ska ange källfilens SHA-256 så att en release kan reproduceras.

Webb och slides delar innehåll och design tokens men inte layout:

- Slide-renderern gör varje komponent till en scen med fast viewport och kontrollerad informationsmängd.
- Webb-renderern placerar samma komponenter i semantiska sektioner som kan omflöda, länkas, sökas och skrivas ut.

