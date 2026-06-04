# Connector: Gamma

Ger AI-agenten möjlighet att skapa presentationer, dokument och webbsidor via Gamma MCP-servern.

## Förutsättningar

- Gamma-konto (gamma.app)
- Claude Code eller Claude Cowork med Gamma MCP konfigurerat

## Vad du kan göra

- Skapa presentationer från en brief eller ett textunderlag
- Generera dokument och webbsidor
- Läsa och granska befintliga Gamma-presentationer
- Använda Gamma-templates som startpunkt

## Kom igång

1. Fyll i `templates/gamma-presentation.md`
2. Be agenten: "Skapa en Gamma-presentation baserat på den här briefen"
3. Agenten genererar presentationen och ger dig en länk

## Tips

- Gamma har smarta defaults — ju mer specifik brief, desto bättre resultat
- Du kan alltid redigera presentationen direkt i Gamma-editorn efter att den skapats
- Agenten kan inte redigera en redan skapad Gamma-presentation — gör ändringar manuellt i editorn

## Begränsningar

- Gamma MCP kan skapa men inte direkt redigera befintliga presentationer
- Bilder genereras automatiskt av Gamma baserat på innehållet
