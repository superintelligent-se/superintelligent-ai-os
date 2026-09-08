# Logotypsystem

## Roller

- **Wordmark** är primär avsändare när namnet behöver etableras: sidhuvud, öppnings-/avslutningsslide, omslag och första PDF-sida.
- **Picture Mark** används när avsändaren redan är tydlig eller ytan är begränsad: favicon, appikon, intern slide-markör och diskret signatur.
- Kvadratiska Picture Mark-assets tillför transparent frizon runt originalformen. De ändrar aldrig symbolens proportioner.

## Godkända kombinationer

| Yta | Primärt val | Alternativ |
|---|---|---|
| Vit | Svart wordmark | Lila Picture Mark |
| Super Purple `#6F00FF` | Vit wordmark | Vit Picture Mark |
| Monokrom/teknisk begränsning | Svart eller vit originalvariant | Ingen egen toning |

Lila full wordmark är inte en standardvariant. Ändra inte färg, rotation, proportioner, path-data eller inbördes avstånd. Lägg inte skugga, kontur, gradient, ram eller annan effekt på logotypen.

## Placering och skala

- Bevara alltid SVG:ns `viewBox` och `preserveAspectRatio`.
- Ge logotypen tydlig frizon; låt den inte konkurrera med rubrik eller CTA.
- Använd wordmark endast när den kan läsas utan att förstoras. Byt till Picture Mark på små eller kvadratiska ytor.
- Ett deck använder normalt wordmark på öppning och avslutning samt Picture Mark diskret på innehållsslides. Upprepa inte full wordmark på varje slide.
- En narrativ sajt använder normalt svart wordmark i ljust sidhuvud, lila Picture Mark som favicon och en diskret Picture Mark i sidfoten.
- I print/PDF ska avsändaren finnas på första sidan och därefter endast där den hjälper orientering eller ägarskap.

## Tillgänglighet

- Länkad wordmark som ensam uttrycker avsändaren får `alt="Superintelligent"`.
- Logotyp som upprepas där namnet redan finns är dekorativ och får tom `alt` samt vid behov `aria-hidden="true"`.
- Lägg aldrig viktig information enbart i Picture Mark.

## Kanoniska assets

Assets finns i `../assets/logos/`:

- `superintelligent-logo-black.svg`
- `superintelligent-logo-white.svg`
- `superintelligent-logo-picturemark-6F00FF.svg`
- `superintelligent-logo-picturemark-black.svg`
- `superintelligent-logo-picturemark-white.svg`
- tre motsvarande `*-square.svg` för kvadratiska digitala ytor

Originalexporter normaliseras med `../scripts/normalize-logo-assets.py`. Scriptet tar bort leverantörsmetadata, kräver outline-paths och dokumenterar källhashar i `manifest.json`. Rasterformat skapas först när målkanalen kräver det; SVG är masterformat.
