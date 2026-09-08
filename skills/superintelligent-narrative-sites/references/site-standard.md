# Standard för narrativ webb

## Informationsarkitektur

- Öppna med tes, mottagarnytta och orientering.
- Låt navigation och rubrikhierarki stödja både snabb sammanfattning och fördjupning.
- Lägg evidens, invändningar, beslut och appendix där de kan länkas direkt.
- Ge interaktion ett tydligt syfte. Visa alltid en statisk motsvarighet för print och no-JS.

## Responsivitet och tillgänglighet

- Använd semantiska `header`, `nav`, `main`, `section`, `figure`, `table` och `footer` när de beskriver innehållet.
- Ha skip-link, synlig tangentbordsfokus, logisk DOM-/rubrikordning och tillräcklig kontrast.
- Testa minst 390 px mobilbredd och 1440 px desktop. Ingen horisontell scroll får krävas för huvudflödet.
- Undvik layout som bygger på hover, fast höjd eller text inbakad i bilder.
- Respektera reduced motion och låt grundinnehållet fungera utan JavaScript.

## Varumärkesavsändare

- Använd svart wordmark i ljust sidhuvud och lila kvadratisk Picture Mark som favicon.
- Använd Picture Mark diskret i sidfoten; duplicera inte full wordmark i varje sektion.
- Säkerställ att första print-/PDF-sidan bär wordmark även när webbens navigation döljs.
- Alla logotypassets ska vara lokala, vektorbaserade och följa `superintelligent-brand/references/logo-system.md`.

## Print och offline

Alla runtime-assets ska finnas lokalt. Print-CSS ska ta bort navigation och interaktionskontroller, expandera detaljer, visa URL:er där det hjälper och undvika brutna rubriker/kort. PDF:n ska bära titel, versionsmärkning och källhash.
