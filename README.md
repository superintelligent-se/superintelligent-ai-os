# Superintelligent AI OS

**Vi demokratiserar AI.**

En metodbank med skills, workflows och templates som gör att din AI-assistent arbetar strukturerat, konsekvent och professionellt — oavsett om du är tekniker eller inte.

---

## Hur vill du komma igång?

### Alternativ 1 — Direkt i webbläsaren, ingen installation

Bläddra bland filerna här på GitHub. Öppna till exempel `skills/` eller `workflows/`, kopiera innehållet i en fil och klistra in det i Claude. Du behöver inget konto och inget program.

### Alternativ 2 — Automatisk sync till din Mac (rekommenderat)

Du får en lokal kopia av alla skills på din dator som uppdateras automatiskt var 30:e minut när Superintelligent publicerar nytt material. Kräver en Mac och ungefär 5 minuter.

**Steg 1 — Öppna Terminal**

Terminal är ett program som finns på alla Mac-datorer. Det ser ut som ett svart eller vitt fönster där du skriver kommandon. Du behöver inte förstå hur det fungerar — du ska bara kopiera och klistra in en rad text.

Så här öppnar du Terminal:
1. Tryck `Command (⌘) + Mellanslag` samtidigt — en sökruta öppnas
2. Skriv `Terminal`
3. Tryck `Enter`

Ett fönster öppnas med en blinkande markör. Det är rätt.

**Steg 2 — Kopiera och klistra in installationskommandot**

Klicka på knappen **Copy** som visas när du håller musen över kodrutan nedan. Klicka sedan i Terminal-fönstret och tryck `Command (⌘) + V` för att klistra in. Tryck sedan `Enter`.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/superintelligent-se/superintelligent-ai-os/main/scripts/install-sync-readonly.sh)
```

Text kommer att rulla förbi i fönstret — det är normalt. Vänta tills det slutar och du ser ett meddelande som börjar med **"Klar!"**

Om din Mac frågar om du vill installera utvecklarverktyg — klicka **Installera** och kör sedan kommandot igen.

**Steg 3 — Koppla mappen till Claude Cowork**

När skriptet är klart visar det en mappsökväg, ungefär så här:
```
/Users/dittnamn/Documents/Superintelligent/superintelligent-ai-os
```

1. Starta **Claude** på din Mac
2. Klicka på **Cowork** i menyn
3. Klicka på **Open folder** (eller **Välj mapp**)
4. Navigera till `Documents` → `Superintelligent` → `superintelligent-ai-os` och klicka **Öppna**

Klart. Claude känner nu till alla skills och uppdaterar dem automatiskt var 30:e minut.

---

### Alternativ 3 — Full installation för utvecklare

```bash
git clone https://github.com/superintelligent-se/superintelligent-ai-os.git
cd superintelligent-ai-os
bash scripts/install.sh
```

Öppna sedan i Claude Code med `claude .` eller peka Cowork på mappen.

För att sätta upp automatisk commit och push till GitHub (för team som bidrar till repot), se [`scripts/install-sync.sh`](scripts/install-sync.sh).

---

## Vad finns i repot?

| Mapp | Innehåll |
|---|---|
| `/skills` | Återanvändbara AI-beteenden och brandprofiler |
| `/workflows` | Återkommande arbetsprocesser med AI |
| `/templates` | Outputformat för dokument, poster och rapporter |
| `/connectors` | Setup-guider för externa verktyg (M365, Outlook, GitHub m.fl.) |
| `/scripts` | Installationsskript och säkerhetskontroll |

---

## Personliga skills

Vill du bygga egna skills som inte ska delas med andra? Skapa en mapp som heter `skills/personal/` — den synkas aldrig till GitHub och syns bara på din maskin.

---

## Viktigt — privat data hör inte hit

Lägg aldrig in privat data, kunddata, mejl, kalenderdata, transkriberingar, API-nycklar eller .env-filer i detta repo. Det är en metodbank, inte ett datalager.

---

## Bidra

Läs [CONTRIBUTING.md](CONTRIBUTING.md) om du vill bidra med workflows, templates eller connector-guider.

---

## Licens

[MIT](LICENSE) — fri att använda, modifiera och dela.

---

*Superintelligent — Vi demokratiserar AI.*
