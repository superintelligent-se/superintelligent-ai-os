# Pilot: visuella kunskapsleveranser

Tre generiska, personuppgiftsfria artefakter renderas från samma innehållsmodell, design tokens, komponentbibliotek och runtime:

1. `keynote.html` - talarledd 16:9-presentation med notes och presenter mode.
2. `strategy-story.html` - asynkron strategiberättelse med självstyrd navigation.
3. `client-proposal.html` - interaktivt kundförslag med `client-proposal.pdf` som statisk backup.

## Rendera lokalt

```bash
python3 skills/superintelligent-artifact-strategy/scripts/render.py \
  pilots/visual-knowledge/content.json \
  --output pilots/visual-knowledge/dist
```

Öppna HTML-filerna direkt eller servera den statiska katalogen:

```bash
python3 -m http.server 8000 --directory pilots/visual-knowledge/dist
```

Ingen nätverksanslutning behövs för rendering eller användning. Hosting är en separat adapter.

## QA och PDF

Skriv screenshots och maskinrapport till `/tmp`:

```bash
python3 skills/superintelligent-artifact-strategy/scripts/qa.py \
  pilots/visual-knowledge/content.json \
  --output pilots/visual-knowledge/dist \
  --qa-dir /tmp/superintelligent-visual-qa \
  --report /tmp/superintelligent-visual-qa/report.json \
  --pdf-artifact client-proposal
```

Granska alltid screenshots och den renderade PDF:n visuellt. Den maskinella Chrome-kontrollen använder 1440 px och 500 px eftersom Chrome på macOS har en minsta headless layoutviewport. Testa dessutom den beslutade 390 px-brytpunkten i en webbläsare med viewportemulering. Maskinkontrollen ersätter inte designbedömning, tangentbordstest eller GDPR-/publiceringsbeslut.
