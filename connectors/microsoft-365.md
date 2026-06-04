# Connector: Microsoft 365

Ger AI-agenten åtkomst till Outlook, Teams, SharePoint och OneDrive via Microsoft 365 MCP-servern.

## Förutsättningar

- Microsoft 365-konto (personal eller organisationskonto)
- Claude Code eller Claude Cowork installerat
- MCP-servern `ms365` konfigurerad (se nedan)

## Installation

### 1. Lägg till MCP-servern i Claude Code

Öppna `~/.claude/settings.json` och lägg till:

```json
{
  "mcpServers": {
    "ms365": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-ms365"]
    }
  }
}
```

### 2. Autentisera

Kör Claude Code och ge kommandot:
```
Anslut Microsoft 365
```

Agenten guidar dig genom OAuth-flödet i webbläsaren.

## Vad du kan göra

- Söka och läsa e-post i Outlook
- Söka i kalender och möten
- Söka i SharePoint-dokument
- Hitta tillgänglighet för möten

## Säkerhet

- Tokens lagras lokalt, committas aldrig
- Ge aldrig agenten instruktioner att vidarebefordra e-postinnehåll till externa system
- All data stannar på din maskin under sessionens gång
