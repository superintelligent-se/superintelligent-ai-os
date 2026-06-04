# Säkerhetspolicy

## Vad som aldrig ska finnas i detta repo

Det här repot är en **metodbank**, inte ett datalager. Följande typer av data ska **aldrig** committtas:

- `.env`-filer eller filer med API-nycklar, tokens eller lösenord
- Privat kunddata eller affärsdata
- E-postmeddelanden eller e-postexporter
- Kalenderdata eller mötestranskriberingar
- Privata filer eller interna dokument
- Certifikatfiler (`.pem`, `.p12`, `.pfx`, `.key`)
- Konfigurationsfiler med verkliga credentials

## Om du hittar känslig data i repot

1. Lägg **inte** till fler commits ovanpå.
2. Kontakta repo-ägaren omedelbart.
3. Använd GitHubs guide för att ta bort känslig data från historiken: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

## Säkerhetskontroll innan commit

Kör alltid:

```bash
bash scripts/safety-check.sh
```

## Rapportera en säkerhetsbrist

Skicka ett privat meddelande till repo-ägaren via GitHub. Öppna inte en publik issue för säkerhetsbrister.
