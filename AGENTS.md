# Superintelligent AI OS — gemensamma agentinstruktioner

Detta repository är en AI-agnostisk metodbank för återanvändbara skills, workflows, templates och integrationsguider. `AGENTS.md` är den gemensamma basen för agenter som stöder formatet. Agentspecifika bryggor, exempelvis `CLAUDE.md` och `.codex/config.toml`, får komplettera men ska inte skapa en parallell metodbank.

## Syfte och gränser

- Förvalta återanvändbara metoder, beteenden och processer.
- Lägg aldrig personlig data, kunddata, mejl, kalenderdata, transkriberingar, tokens eller credentials i repot.
- Behåll källmaterial i `skills/`, `workflows/`, `templates/` och `connectors/` verktygsagnostiskt när det är praktiskt möjligt.
- Lägg agentspecifika installationsdetaljer i tydligt namngivna konfigurationsfiler eller scripts.

## Struktur

- `skills/`: kanoniska återanvändbara skills, inklusive Superintelligent-brand.
- `workflows/`: återkommande arbetsprocesser.
- `templates/`: återanvändbara leveransformat.
- `connectors/`: dokumentation för externa tjänster och verktyg.
- `scripts/`: säkra, återkörbara installationer, synkningar och kontroller.
- `.codex/`: endast projektspecifik Codex-konfiguration; aldrig credentials eller lokal state.

## Ändringsregler

- Läs närmaste relevanta skill, workflow eller template innan den ändras.
- Bevara stöd för befintliga användare och AI-klienter om en brytande ändring inte uttryckligen är beställd.
- Gör små, granskbara ändringar och uppdatera dokumentation och installationsskript tillsammans med strukturella förändringar.
- Kör `bash scripts/safety-check.sh` före commit.
- Kasta aldrig bort lokala ändringar och force-pusha aldrig `main`.
- Lös Git-konflikter semantiskt och verifiera resultatet.

## Publicering

När filer i `skills/`, `workflows/`, `templates/` eller `connectors/` ändras, skriv en begriplig sammanfattning i `.pending-commit-msg` enligt formatet i `CLAUDE.md`. Regeln gäller oavsett vilken agent som gör ändringen.

Commit och push får automatiseras när användaren har gett uttryckligt mandat för arbetsflödet. Annars ska agenten stanna före extern publicering.
