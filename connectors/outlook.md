# Connector: Outlook

Specifik guide för att använda Outlook-integrationen via Microsoft 365 MCP.

## Förutsättningar

Följ installations-stegen i `connectors/microsoft-365.md` först.

## Vad du kan göra

- Söka e-post på avsändare, ämne eller nyckelord
- Läsa enskilda e-postmeddelanden
- Hitta e-post inom ett datumintervall
- Identifiera olästa meddelanden som kräver svar

## Exempel på kommandon till agenten

```
Visa mig olästa e-postmeddelanden från idag
```
```
Sök efter e-post från [namn] under de senaste 7 dagarna
```
```
Vilka e-postmeddelanden kräver svar idag?
```

## Begränsningar

- Agenten kan läsa men inte skicka e-post (med standardkonfiguration)
- Bifogade filer kräver separat hantering
- Stora brevlådor kan ge långsammare svar

## Säkerhet

- Läs aldrig känsliga mejl högt i en delad session
- Agenten ska aldrig spara mejlinnehåll i detta repo
- Privata e-postdata committas aldrig
