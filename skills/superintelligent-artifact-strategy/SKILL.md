---
name: superintelligent-artifact-strategy
description: Välj leveransform för Superintelligents visuella kunskapsartefakter när webb, slides, PDF eller redigerbar överlämning behöver vägas mot varandra. Använd inte för att bygga artefakten efter att formatet redan är bestämt.
---

# Artifact strategy

Välj format innan verktyg. Läs `../superintelligent-brand/SKILL.md` för varumärket och [formatpolicyn](references/format-policy.md) för beslutskriterierna.

## Routing

- Talarledd sekvens, scenläge eller speaker notes: använd `superintelligent-presentations`.
- Självstyrd, sökbar, responsiv eller levande kunskap: använd `superintelligent-narrative-sites`.
- Viktig extern leverans: välj normalt webb plus PDF; lägg till slides om den också framförs live.
- Mottagaren ska redigera i Office eller Workspace: leverera PPTX eller Google Slides, även om en webb-/PDF-version också finns.

Välj inte hosting innan åtkomst, sekretess, livslängd, domänägarskap, analytics och avpublicering är beslutade. Gamma och Codex Sites är valfria adapters, inte grundformat.

## Gemensamt system

Kanoniskt innehåll följer [innehållsmodellen](references/content-model.md). Rendera med `scripts/render.py`; kör `scripts/qa.py` före leverans. Renderern accepterar endast det begränsade komponentbiblioteket och producerar lokala artefakter utan nätverksberoende.

