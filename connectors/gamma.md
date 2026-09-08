# Connector: Gamma

Ger AI-agenten möjlighet att skapa presentationer, dokument och webbsidor via Gamma MCP-servern. Gamma är en valfri leveransadapter; välj först format enligt `skills/superintelligent-artifact-strategy/SKILL.md`.

## Förutsättningar

- Gamma-konto (gamma.app)
- Claude Code eller Claude Cowork med Gamma MCP konfigurerat

## Vad du kan göra

- Skapa presentationer från en brief eller ett textunderlag
- Generera dokument och webbsidor
- Läsa och granska befintliga Gamma-presentationer
- Använda Gamma-templates som startpunkt

## Kom igång

1. Bekräfta att Gamma passar konsumtionssätt, redigeringsbehov, sekretess, offlinekrav och livscykel.
2. Fyll i `templates/gamma-presentation.md`.
3. Be agenten: "Skapa en Gamma-presentation baserat på den här briefen".
4. Verifiera webb-, PDF- och eventuell PPTX-output mot briefen innan leverans.

Använd de kanoniska SVG-filerna i `skills/superintelligent-brand/assets/logos/`. Wordmark ska importeras som asset, inte återskapas som text. Om vald Gamma-template inte kan bevara proportioner, frizon och rätt variant ska logotypen appliceras efter export eller adaptern väljas bort.

## Tips

- Gamma har smarta defaults — ju mer specifik brief, desto bättre resultat
- Du kan alltid redigera presentationen direkt i Gamma-editorn efter att den skapats
- Agenten kan inte redigera en redan skapad Gamma-presentation — gör ändringar manuellt i editorn

## Begränsningar

- Gamma MCP kan skapa men inte direkt redigera befintliga presentationer
- Bilder genereras automatiskt av Gamma baserat på innehållet
- Kanoniskt innehåll och källor bör behållas utanför Gamma så att leveransen kan reproduceras eller migreras
- Offline, PDF-fidelitet, presenter experience och verklig PPTX-redigerbarhet måste testas per leverans
- Custom fonts, analytics, domän och avancerad delning kan bero på plan; kontrollera aktuella villkor före val
