# Connector: GitHub

Ger AI-agenten möjlighet att arbeta med GitHub-repositories via GitHub CLI och MCP.

## Förutsättningar

- Git installerat (`git --version`)
- GitHub CLI installerat (`brew install gh`)
- Inloggad på GitHub (`gh auth login`)

## Vad du kan göra

- Skapa och hantera repositories
- Läsa och skapa issues
- Hantera pull requests
- Visa commit-historik
- Hantera branches

## Säkerhetsprinciper i detta repo

- Agenten frågar alltid innan commit eller push
- Kör `scripts/safety-check.sh` innan varje commit
- Privata tokens committas aldrig (blockeras av `.gitignore`)
- GitHub-tokens lagras via `gh auth` — aldrig i klartext i filer

## Exempel på kommandon

```
Visa status för lokala ändringar
```
```
Gör en commit med meddelandet: [ditt meddelande]
```
```
Skapa ett publikt repo som heter [namn]
```

## Begränsningar

- Force push till main kräver explicit godkännande
- Destruktiva operationer (branch -D, reset --hard) frågas alltid om
