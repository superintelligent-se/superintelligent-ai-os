#!/usr/bin/env python3
"""Normalize approved Superintelligent SVG exports into canonical brand assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SOURCE_FILES = (
    "superintelligent-logo-black.svg",
    "superintelligent-logo-white.svg",
    "superintelligent-logo-picturemark-6F00FF.svg",
    "superintelligent-logo-picturemark-black.svg",
    "superintelligent-logo-picturemark-white.svg",
)
PICTUREMARK_FILES = SOURCE_FILES[2:]
SVG_OPEN = re.compile(r"<svg\b[^>]*>")
VIEW_BOX = re.compile(r'viewBox="([\d.\-]+) ([\d.\-]+) ([\d.]+) ([\d.]+)"')


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalize(source: Path) -> tuple[str, str]:
    raw = source.read_bytes()
    text = raw.decode("utf-8")
    if "<text" in text or "<image" in text:
        raise ValueError(f"{source.name} must contain outlined vector geometry only")
    if not SVG_OPEN.search(text) or not VIEW_BOX.search(text):
        raise ValueError(f"{source.name} is missing an SVG root or viewBox")

    text = re.sub(r"<\?xml[^>]*>\s*", "", text, count=1)
    text = re.sub(r"<metadata>.*?</metadata>", "", text, flags=re.DOTALL)
    text = re.sub(r"\s+id=\"Layer_[^\"]+\"", "", text, count=1)
    text = re.sub(r">\s+<", "><", text).strip()
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{text}\n', sha256(raw)


def square_viewbox(svg: str, safe_zone: float = 0.08) -> str:
    match = VIEW_BOX.search(svg)
    if not match:
        raise ValueError("normalized SVG is missing viewBox")
    x, y, width, height = (float(value) for value in match.groups())
    side = max(width, height) / (1 - 2 * safe_zone)
    square_x = x - (side - width) / 2
    square_y = y - (side - height) / 2
    replacement = f'viewBox="{square_x:.2f} {square_y:.2f} {side:.2f} {side:.2f}"'
    return VIEW_BOX.sub(replacement, svg, count=1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {"schema_version": 1, "assets": {}}

    normalized: dict[str, str] = {}
    for name in SOURCE_FILES:
        source = args.source_dir / name
        if not source.is_file():
            raise FileNotFoundError(source)
        svg, source_hash = normalize(source)
        normalized[name] = svg
        destination = args.output / name
        destination.write_text(svg, encoding="utf-8")
        manifest["assets"][name] = {
            "source": name,
            "source_sha256": source_hash,
            "sha256": sha256(svg.encode("utf-8")),
            "variant": "native",
        }

    for name in PICTUREMARK_FILES:
        square_name = name.removesuffix(".svg") + "-square.svg"
        svg = square_viewbox(normalized[name])
        destination = args.output / square_name
        destination.write_text(svg, encoding="utf-8")
        manifest["assets"][square_name] = {
            "source": name,
            "sha256": sha256(svg.encode("utf-8")),
            "variant": "square-transparent-8-percent-safe-zone",
        }

    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"normalized {len(manifest['assets'])} assets in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
