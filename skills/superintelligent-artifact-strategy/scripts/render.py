#!/usr/bin/env python3
"""Render constrained Superintelligent visual artifacts from canonical JSON."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
BRAND_ROOT = SKILL_ROOT.parent / "superintelligent-brand"
ALLOWED_TYPES = {
    "hero", "section", "key_insight", "evidence", "comparison", "process",
    "timeline", "data_visualization", "quote", "case_study", "decision",
    "calculator", "cta", "appendix",
}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def validate(data: dict[str, Any]) -> None:
    if not isinstance(data.get("system_version"), str):
        raise ValueError("system_version must be a string")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("artifacts must be a non-empty list")
    seen: set[str] = set()
    for artifact in artifacts:
        for field in ("id", "mode", "title", "audience", "purpose", "components"):
            if field not in artifact:
                raise ValueError(f"artifact missing {field}")
        if artifact["id"] in seen:
            raise ValueError(f"duplicate artifact id: {artifact['id']}")
        seen.add(artifact["id"])
        if artifact["mode"] not in {"slides", "site", "hybrid"}:
            raise ValueError(f"unsupported mode: {artifact['mode']}")
        for component in artifact["components"]:
            for field in ("id", "type", "title"):
                if field not in component:
                    raise ValueError(f"component missing {field} in {artifact['id']}")
            if component["type"] not in ALLOWED_TYPES:
                raise ValueError(f"unsupported component: {component['type']}")
            if any(key in component for key in ("html", "css", "javascript", "script")):
                raise ValueError(f"free-form code is not allowed in {component['id']}")


def render_items(items: list[Any], ordered: bool = False) -> str:
    tag = "ol" if ordered else "div"
    class_name = "process-list" if ordered else "component-grid"
    parts = [f'<{tag} class="{class_name}">']
    for item in items:
        if isinstance(item, dict):
            title = esc(item.get("title", item.get("label", "")))
            body = esc(item.get("body", item.get("value", "")))
        else:
            title, body = esc(item), ""
        inner = f"<h3>{title}</h3>" + (f"<p>{body}</p>" if body else "")
        parts.append(f"<li><div>{inner}</div></li>" if ordered else f'<article class="card">{inner}</article>')
    parts.append(f"</{tag}>")
    return "".join(parts)


def render_component_body(component: dict[str, Any]) -> str:
    kind = component["type"]
    title = esc(component["title"])
    body = esc(component.get("body", ""))
    eyebrow = esc(component.get("eyebrow", kind.replace("_", " ")))
    lead = f'<p class="lede">{body}</p>' if body else ""
    heading = f'<p class="eyebrow">{eyebrow}</p><h2>{title}</h2>{lead}'

    if kind == "hero":
        return f'<p class="eyebrow">{eyebrow}</p><h1>{title}</h1>{lead}'
    if kind in {"section", "key_insight", "case_study", "appendix"}:
        return heading + render_items(component.get("items", []))
    if kind == "evidence":
        metric = esc(component.get("metric", ""))
        return heading + (f'<span class="metric">{metric}</span>' if metric else "") + render_items(component.get("items", []))
    if kind == "comparison":
        columns = component.get("items", [])
        cards = "".join(f'<article class="card"><h3>{esc(item.get("title", ""))}</h3><p>{esc(item.get("body", ""))}</p></article>' for item in columns)
        return heading + f'<div class="comparison-grid">{cards}</div>'
    if kind in {"process", "timeline"}:
        return heading + render_items(component.get("items", []), ordered=True)
    if kind == "data_visualization":
        rows = []
        for item in component.get("items", []):
            value = max(0, min(100, float(item.get("value", 0))))
            rows.append(f'<div class="bar-row"><span>{esc(item.get("label", ""))}</span><span class="bar-track" aria-hidden="true"><span class="bar-fill" style="width:{value:g}%"></span></span><strong>{value:g}%</strong></div>')
        return heading + f'<div class="bar-list">{"".join(rows)}</div>'
    if kind == "quote":
        cite = esc(component.get("cite", ""))
        return heading + f'<blockquote>{body}</blockquote>' + (f"<p>{cite}</p>" if cite else "")
    if kind == "decision":
        return heading + f'<div class="decision-box"><strong>{esc(component.get("decision", body))}</strong></div>'
    if kind == "calculator":
        fields = []
        for item in component.get("inputs", []):
            fields.append(
                f'<label>{esc(item["label"])}<input type="number" min="0" value="{esc(item["value"])}" data-factor="{esc(item["factor"])}"></label>'
            )
        fallback = esc(component.get("fallback", "Interaktiv beräkning finns i webbversionen."))
        return heading + f'<div class="calculator" data-calculator>{"".join(fields)}<output class="calculator-output" data-result aria-live="polite"></output></div><p class="print-fallback">{fallback}</p>'
    if kind == "cta":
        action = esc(component.get("action", "Nästa steg"))
        href = esc(component.get("href", "#"))
        return heading + f'<p><a href="{href}">{action}</a></p>'
    raise ValueError(f"renderer missing component: {kind}")


def source_list(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return ""
    items = "".join(f'<li><a href="{esc(item["url"])}">{esc(item["title"])}</a></li>' for item in sources)
    return f'<section class="site-section" id="sources"><div class="site-section__inner"><p class="eyebrow">Källor</p><h2>Fördjupning och evidens</h2><ol class="source-list">{items}</ol></div></section>'


def page_head(artifact: dict[str, Any], digest: str, stylesheet: str) -> str:
    description = esc(artifact["purpose"])
    return f'''<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description}">
  <meta name="generator" content="superintelligent-visual-system">
  <meta name="source-sha256" content="{digest}">
  <title>{esc(artifact['title'])} - Superintelligent</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="assets/design-tokens.css">
  <link rel="stylesheet" href="assets/components.css">
  <link rel="stylesheet" href="assets/{stylesheet}">
</head>'''


def render_site(artifact: dict[str, Any], digest: str, version: str, sources: list[dict[str, Any]]) -> str:
    nav = "".join(f'<a href="#{esc(component["id"])}">{esc(component.get("nav", component["title"]))}</a>' for component in artifact["components"] if component["type"] not in {"appendix"})
    sections = []
    for component in artifact["components"]:
        classes = ["site-section", f'site-section--{component["type"].replace("_", "-")}']
        if component["type"] in {"hero", "cta"} and component.get("purple", component["type"] == "hero"):
            classes.append("site-section--purple")
        sections.append(f'<section class="{" ".join(classes)}" id="{esc(component["id"])}"><div class="site-section__inner">{render_component_body(component)}</div></section>')
    return page_head(artifact, digest, "site.css") + f'''
<body>
  <a class="skip-link" href="#main">Hoppa till innehållet</a>
  <header class="site-header"><div class="site-header__inner"><a class="site-brand" href="#main">Superintelligent</a><nav class="site-nav" aria-label="Innehåll">{nav}</nav></div></header>
  <main id="main">{"".join(sections)}{source_list(sources)}</main>
  <footer class="site-footer"><span>Vi demokratiserar AI.</span><span>System {esc(version)} · Källa {digest[:12]}</span></footer>
  <script src="assets/runtime.js" defer></script>
</body>
</html>'''


def render_slides(artifact: dict[str, Any], digest: str, version: str) -> str:
    slides = []
    for component in artifact["components"]:
        classes = ["slide", f'slide--{component["type"].replace("_", "-")}']
        if component["type"] in {"hero", "cta"} and component.get("purple", True):
            classes.append("slide--purple")
        notes = esc(component.get("notes", ""))
        slides.append(f'<section class="{" ".join(classes)}" id="{esc(component["id"])}" aria-label="{esc(component["title"])}"><div class="slide__inner">{render_component_body(component)}</div><aside class="notes" hidden>{notes}</aside></section>')
    return page_head(artifact, digest, "slides.css") + f'''
<body>
  <main class="deck" data-deck>{"".join(slides)}</main>
  <nav class="deck-controls" aria-label="Presentationskontroller"><button type="button" data-prev aria-label="Föregående slide">←</button><span class="slide-count" data-slide-count aria-live="polite"></span><button type="button" data-next aria-label="Nästa slide">→</button><button type="button" data-presenter>Presenter</button></nav>
  <aside class="presenter-panel" aria-label="Presenter view"><div><strong>Presenter view</strong><div class="presenter-timer" data-presenter-timer>00:00</div></div><div class="presenter-notes" data-presenter-notes></div><div><strong>Nästa</strong><div class="next-preview" data-next-preview></div></div></aside>
  <script src="assets/runtime.js" defer></script>
</body>
</html>'''


def copy_assets(output: Path) -> None:
    target = output / "assets"
    target.mkdir(parents=True, exist_ok=True)
    files = {
        BRAND_ROOT / "assets" / "design-tokens.css": target / "design-tokens.css",
        SKILL_ROOT / "assets" / "components.css": target / "components.css",
        SKILL_ROOT / "assets" / "site.css": target / "site.css",
        SKILL_ROOT / "assets" / "slides.css": target / "slides.css",
        SKILL_ROOT / "assets" / "runtime.js": target / "runtime.js",
    }
    for source, destination in files.items():
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copyfile(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact", action="append", help="Render only matching artifact id; repeatable")
    args = parser.parse_args()

    raw = args.source.read_bytes()
    data = json.loads(raw)
    validate(data)
    digest = hashlib.sha256(raw).hexdigest()
    args.output.mkdir(parents=True, exist_ok=True)
    copy_assets(args.output)

    selected = set(args.artifact or [])
    rendered = 0
    for artifact in data["artifacts"]:
        if selected and artifact["id"] not in selected:
            continue
        if artifact["mode"] == "slides":
            document = render_slides(artifact, digest, data["system_version"])
        else:
            document = render_site(artifact, digest, data["system_version"], data.get("sources", []))
        destination = args.output / f'{artifact["id"]}.html'
        destination.write_text(document, encoding="utf-8")
        print(f"rendered {destination}")
        rendered += 1
    if selected and rendered != len(selected):
        missing = selected - {item["id"] for item in data["artifacts"]}
        raise ValueError(f"unknown artifact ids: {sorted(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
