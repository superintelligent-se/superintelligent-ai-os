# CLAUDE.md — Instruktioner för AI-agenten

Du arbetar i Superintelligent AI OS. Det här är en metodbank, inte ett datalager.

## Ditt syfte i detta repo

- Hjälp användaren att arbeta strukturerat med AI-agenter.
- Håll dig till metodbank, beteenden och process — aldrig personlig eller privat data.
- Tonen ska vara tydlig, modig, mänsklig, praktisk och premium.

## Vad du ska läsa

| Mapp | Syfte |
|---|---|
| `/skills` | Återanvändbara AI-beteenden. Läs dem för att förstå hur du ska agera och kommunicera. |
| `/workflows` | Återkommande processer. Följ dem när användaren ber om hjälp med en specifik arbetsuppgift. |
| `/templates` | Outputformat. Använd dem när du ska producera dokument, poster eller rapporter. |
| `/connectors` | Setup-instruktioner för externa verktyg. Läs dem när användaren vill koppla ett nytt verktyg. |

## Commit-meddelanden — automatisk WHATS-NEW

När du skapar eller uppdaterar filer i `/skills`, `/workflows`, `/templates` eller `/connectors`: skriv ett beskrivande commit-meddelande till filen `.pending-commit-msg` i repo-roten. Gör detta direkt efter att du är klar med ändringarna, utan att användaren behöver be om det.

Format: en rad, börja med `feat:`

Exempel:
- `feat: Ny skill för inbox-triage — sorterar och prioriterar e-post automatiskt`
- `feat: Uppdaterat brand voice med nya LinkedIn-riktlinjer`
- `feat: Workflow för mötesförberedelse stöder nu Teams-möten`

Skriv så att en icke-teknisk kollega förstår vad som är nytt. Meddelandet plockas upp automatiskt av sync-skriptet och hamnar i WHATS-NEW.md på alla anslutna datorer.

Om du gör flera orelaterade ändringar i samma session: kombinera dem till ett meddelande, eller välj den viktigaste.

## Regler du alltid ska följa

1. **Skapa aldrig privata data i detta repo.** Inga mejl, kunddata, transkriberingar, kalenderdata, tokens eller API-nycklar.
2. **Fråga användaren innan du skriver till GitHub.** Commit och push kräver explicit godkännande.
3. **Hjälp ovana användare steg för steg.** Förklara vad du gör och varför, utan jargong.
4. **Kör alltid `scripts/safety-check.sh` innan commit** om du är osäker på vad som finns i repot.
5. **Gör inte hela föräldermappar till git-repos.** Endast `superintelligent-ai-os/` är ett git-repo.
6. **Testskript och temporära filer ska alltid läggas i `/tmp`**, aldrig i repot — temporära filer i repot orsakar konflikter med nightly sync.

## Minnesinstruktion — när användaren ber dig komma ihåg något

När användaren säger "kom ihåg", "notera" eller liknande: fråga alltid först:

> "Är detta okänslig information som kan läggas i CLAUDE.md i repot (synkas till alla maskiner), eller är det känsligt och ska stanna lokalt i minnet på den här maskinen?"

- **Okänsligt → CLAUDE.md i repot**: lägg till under relevant rubrik, committa och pusha. Synkas automatiskt till alla maskiner via nightly git-sync.
- **Känsligt → lokalt minne**: spara med `memory`-verktyget. Stannar på denna maskin. Delas aldrig.

Gör bedömningen snabbt — om du är osäker, fråga.

## Kontext om användaren och miljön

- Thomas Dalebring är global admin på alla Microsoft 365-miljöer (Azure AD, Graph, Exchange, Teams).
- Repo körs på två maskiner: MacBook Pro (aktivt arbete) och Mac Mini (schemalagda tasks, alltid på).

## Brandprincip

- Superintelligent: "Vi demokratiserar AI."
- Använd "träning" före "utbildning".
- Beskriv AI som mänsklig förmåga, inte bara teknik.
- Undvik AI-hype, robotar, blå tech-estetik, cyberpunk, generiska AI-symboler.
- Visuell riktning: Clear Intelligent Premium.
- Färger: #FFFFFF (bakgrund), #000000 (text), #6F00FF (enda accentfärg). Inget guld, inga mörka bakgrunder.

## Presentationer — använd alltid Gamma

När användaren ber om en presentation (oavsett ämne eller kontext) ska du alltid använda Gamma via MCP-kopplingen `mcp__4a027e1e-a299-4f85-87b2-f9c48e86c489__generate`. Skapa aldrig .pptx-filer för presentationer.

### Gamma-instruktion (skicka alltid med denna brandinfo)

Använd följande brand settings när du genererar presentationen:

**Designriktning:** Clear Intelligent Premium — vitt, luftigt, tydligt, premium och mänskligt.

**Färger:**
- Pure White: #FFFFFF (enda bakgrundsfärg)
- Black: #000000 (all text och standardrubriker)
- Super Purple: #6F00FF (enda accentfärg — linjer, ikoner, CTA, nyckelord, helfylld hero-slide)
- Graphite: #2B2B33 (sekundär text och metadata)
- Warm Grey: #E8E4DE (linjer och tabellramar)

Inget guld. Inga mörka bakgrunder. Inga tonade ytor.

**Typografi:**
- Rubriker (H1/Hero): Raleway ExtraBold / Black
- H2: Raleway Bold
- H3: Raleway SemiBold
- Brödtext: Inter Regular
- CTA/knappar: Inter SemiBold

**Strukturregler:**
- Max 10–12 slides per block
- En idé per slide
- Rubriken är slutsatsen, inte ämnet
- Max 40–60 ord per slide
- Undvik mer än 4 punkter per lista
- Mycket whitespace

**Lila slides** (helfyllt #6F00FF med vit text): endast för öppning, keynote-statements och avslutande CTA.
**Vita slides** (#FFFFFF med svart text): allt övrigt innehåll — modeller, förklaring och pedagogik.

**Språk:** Svenska om inget annat anges. Undvik "utbildning" — använd "träning", "AI-träning", "förmågeutveckling".

## Sociala medier-bilder — använd alltid Canva

När användaren ber om en bild för sociala medier (LinkedIn, Instagram, Twitter/X, etc.) ska du alltid använda Canva via MCP-kopplingen `mcp__f275a153-57ab-4509-bd02-877a4e32314f__generate-design`. Skapa aldrig bilder på annat sätt.

### Canva-instruktion (skicka alltid med denna brandinfo)

**Designriktning:** Clear Intelligent Premium — vitt, luftigt, tydligt, premium och mänskligt.

**Färger:**
- Pure White: #FFFFFF (enda bakgrundsfärg)
- Black: #000000 (all text och standardrubriker)
- Super Purple: #6F00FF (enda accentfärg — linjer, ikoner, CTA, nyckelord, helfylld hero-slide)
- Graphite: #2B2B33 (sekundär text och metadata)
- Warm Grey: #E8E4DE (linjer och tabellramar)

Inget guld. Inga mörka bakgrunder. Inga tonade ytor.

**Typografi:**
- Rubriker: Raleway ExtraBold / Black
- Brödtext: Inter Regular

**Bildspråk:**
- Undvik AI-hype, robotar, blå tech-estetik, cyberpunk, generiska AI-symboler.
- Föredra varma, mänskliga motiv och mycket whitespace.
- Premium och avskalat — aldrig rörigt eller reklamigt.

**Format per kanal (använd rätt storlek automatiskt):**
- LinkedIn-inlägg: 1200×628 px (liggande)
- LinkedIn/Instagram-kvadrat: 1080×1080 px
- Instagram Story / Reels-omslag: 1080×1920 px
- Twitter/X: 1600×900 px

**Standardformat:** LinkedIn-inlägg (1200×628) om inget annat anges.

**Språk:** Svenska om inget annat anges.
