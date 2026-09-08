# Inventering: visuella kunskapsleveranser

Inventeringen är en ögonblicksbild från 2026-09-08. Den omfattar namn, beskrivningar och installationslänkar - inga credentials, pluginsessioner eller personliga data.

## Repo-skills före förändringen

| Skill | Beskrivning | Format |
|---|---|---|
| `superintelligent-brand` | Styr språk, tonalitet och visuell riktning för innehåll i Superintelligents namn. | Äldre rubrikbaserad `SKILL.md`, ingen YAML-frontmatter. |
| `inbox-triage` | Triagerar Microsoft 365-e-post och producerar en prioriterad rapport med utkast. | Äldre rubrikbaserad `SKILL.md`, ingen YAML-frontmatter. |
| `outlook-mail-bridge` | Skapar, granskar och skickar Outlook-mejl via Microsoft Graph med strikt godkännandeflöde. | Äldre rubrikbaserad `SKILL.md`, ingen YAML-frontmatter. |

## Lokal installation och Codex-discovery

Samtliga tre repo-skills var lokalt installerade som symlänkar från `~/.codex/skills/` till repots `skills/`-mappar. `scripts/install-codex.sh` installerar varje direkt undermapp som innehåller `SKILL.md` utan att skriva över befintliga mål.

Den aktiva Codex-miljön upptäckte dessutom system- och plugin-skills som inte tillhör repot, bland annat verktyg för skill/plugin-hantering, dokument, PDF, presentationer, kalkylblad, Sites, browserkontroll, bildgenerering och visualisering. De är miljöförmågor, inte kanoniskt Superintelligent-innehåll, och kopieras därför inte till repot.

Efter förändringen kan Codex upptäcka de tre nya skillsen när `scripts/install-codex.sh` körs igen och Codex startas om. Claude använder samma kanoniska `SKILL.md`-filer via repo-instruktionerna. `agents/openai.yaml` behövs inte för funktion och utelämnas för att hålla kärnan AI-agnostisk.

## Befintlig presentationsmodell

- `CLAUDE.md` gjorde Gamma obligatoriskt för varje begäran som kallades presentation och förbjöd PPTX.
- `templates/gamma-presentation.md` gav en bra briefstruktur men antog Gamma som renderer.
- `connectors/gamma.md` dokumenterade skapande och delning men även att MCP-flödet inte kan redigera en redan skapad presentation direkt.
- `skills/superintelligent-brand/references/presentation-rules.md` innehöll i huvudsak verktygsneutrala brandregler trots en Gamma-orienterad ingress.

Modellen var snabb men sammanblandade fyra skilda behov: liveframförande, asynkron webb, hybridleverans och redigerbar överlämning. Den ersätts därför av formatrouting medan Gamma-stödet bevaras som valfritt pilotspår.

