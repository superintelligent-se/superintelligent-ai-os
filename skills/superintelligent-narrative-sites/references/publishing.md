# Publicering som adapter

Publicera först efter beslut om:

- informationsklassning och vilka som får åtkomst
- organisationens domän och ansvarig ägare
- canonical URL, release-ID och redirects
- analytics, cookies, personuppgifter, retention och GDPR-rättslig grund
- driftansvar, kostnad, backup, incidentväg och avpublicering
- schemalagd länkkontroll och granskning av innehållets aktualitet

Standardoutput är en statisk katalog som kan serveras av valfri HTTP-server. Adapter får kopiera denna katalog men inte göra sin konfiguration till kanonisk innehållskälla.

Codex Sites, Vercel, GitHub Pages, Cloudflare Pages och annan statisk hosting kan användas efter separat lämplighetsbedömning. Välj inte adapter enbart för att den är snabbast i byggögonblicket; bedöm export, redirects, domänflytt, åtkomstkontroll och avveckling.

