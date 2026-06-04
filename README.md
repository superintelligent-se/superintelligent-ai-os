# Superintelligent AI OS

> **Ny här? Vet inte vad GitHub är eller vad det här är?**
> Börja här istället: [START-HERE.md](START-HERE.md) — ingen teknisk kunskap krävs.

---

**Vi demokratiserar AI.**

Superintelligent AI OS är ett publikt arbets-OS för AI-experter, konsulter och organisationer som vill arbeta strukturerat med AI-agenter — utan att behöva uppfinna hjulet varje gång.

Det här repot innehåller metodbank, skills, workflows, templates och connector-guider som fungerar med Claude Code och Claude Cowork.

---

## Vad finns här?

| Mapp | Innehåll |
|---|---|
| `/skills` | Återanvändbara AI-beteenden och brandprofiler |
| `/workflows` | Återkommande arbetsprocesser med AI |
| `/templates` | Outputformat för dokument, poster och rapporter |
| `/connectors` | Setup-guider för externa verktyg |
| `/scripts` | Hjälpskript för installation och säkerhetskontroll |

---

## Kom igång på 10 minuter

### 1. Klona eller forka repot

```bash
git clone https://github.com/Superintelligent/superintelligent-ai-os.git
cd superintelligent-ai-os
```

Eller klicka **Fork** uppe till höger på GitHub för att skapa din egen kopia.

### 2. Öppna i Claude Code

```bash
claude .
```

Eller öppna mappen direkt i Claude Code-appen.

### 3. Öppna i Claude Cowork

Starta Claude Cowork och välj **Open project folder** — peka på `superintelligent-ai-os/`.

### 4. Installera skills

```bash
bash scripts/install.sh
```

Skriptet kopierar skills till rätt plats och bekräftar vad som installerats.

### 5. Koppla dina connectors

Läs guiden i `/connectors/` för det verktyg du vill ansluta, t.ex.:

```
connectors/microsoft-365.md
connectors/outlook.md
connectors/github.md
```

Följ stegen i respektive fil för att autentisera och konfigurera.

### 6. Kör säkerhetskontroll

Innan du commitar, kör alltid:

```bash
bash scripts/safety-check.sh
```

---

## Viktigt — privat data hör inte hit

> **Lägg aldrig in privat data, kunddata, mejl, kalenderdata, transkriberingar, API-nycklar, tokens eller .env-filer i detta repo.**

Det är en metodbank, inte ett datalager. Privat data stannar lokalt på din maskin eller i ditt privata moln.

---

## Bidra

Läs [CONTRIBUTING.md](CONTRIBUTING.md) om du vill bidra med workflows, templates eller connector-guider.

---

## Licens

[MIT](LICENSE) — fri att använda, modifiera och dela.

---

*Superintelligent — Vi demokratiserar AI.*
