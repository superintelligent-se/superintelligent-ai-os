# Standard för livepresentationer

## Dramaturgi

- Definiera vad publiken ska tänka, känna eller göra efter framförandet.
- Låt rubriker bära slutsatser och bygg en kontrollerad sekvens.
- En komponent motsvarar normalt en slide; dela hellre än att krympa.
- Lägg resonemang, övergång och källkontext i notes, inte på scenytan.

## Presenter experience

Före leverans ska följande fungera utan nätverk:

- framåt/bakåt, Home/End och direkt val av slide
- nuvarande slide, nästa slide och privata notes
- timer samt tydlig paus/blank funktion
- fullskärm och läsbarhet i 16:9 på 1280x720 och 1920x1080
- lokal fontfallback och inga remote assets
- officiell wordmark på öppning/avslutning och diskret Picture Mark på innehållsslides

HTML-runtime passar när Git-reproducerbarhet och specialinteraktion väger tungt. Reveal.js är förstahandskandidat om mer mogen presenterfunktion motiverar beroendet. PowerPoint eller Google Slides är förstahandsval när kunden ska redigera originalet.

## QA

Kontrollera visuellt varje slide, inklusive logotypens kontrast/frizon, längsta rubrik, data, sista CTA och notes. PDF ska ha en sida per slide utan clipping. Öva även failure mode: stäng nätverket, ladda om, byt display och öppna PDF-backupen.
