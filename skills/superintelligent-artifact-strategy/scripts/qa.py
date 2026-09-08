#!/usr/bin/env python3
"""Render, screenshot, inspect and optionally export visual artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlencode


SCRIPT_ROOT = Path(__file__).resolve().parent
DEFAULT_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=True, timeout=30)


def chrome_base(chrome: Path, profile: Path) -> list[str]:
    return [str(chrome), "--headless", "--disable-gpu", "--no-first-run", "--run-all-compositor-stages-before-draw"]


def page_url(page: Path, params: dict[str, str] | None = None) -> str:
    return page.resolve().as_uri() + (f"?{urlencode(params)}" if params else "")


def inspect_dom(chrome: Path, profile: Path, page: Path, size: tuple[int, int], params: dict[str, str] | None = None) -> dict[str, object]:
    query = {"qa": "1", **(params or {})}
    url = page_url(page, query)
    result = run(chrome_base(chrome, profile) + ["--virtual-time-budget=2000", f"--window-size={size[0]},{size[1]}", "--dump-dom", url], capture=True)
    match = re.search(r'<script id="qa-result" type="application/json">(.*?)</script>', result.stdout, re.DOTALL)
    if not match:
        raise RuntimeError(f"QA payload missing from {page}")
    return json.loads(match.group(1))


def screenshot(chrome: Path, profile: Path, page: Path, size: tuple[int, int], destination: Path, params: dict[str, str] | None = None) -> None:
    url = page_url(page, params)
    run(chrome_base(chrome, profile) + ["--virtual-time-budget=1500", f"--window-size={size[0]},{size[1]}", f"--screenshot={destination}", url])


def export_pdf(chrome: Path, profile: Path, page: Path, destination: Path) -> None:
    url = page.resolve().as_uri() + "?print=1"
    run(chrome_base(chrome, profile) + ["--virtual-time-budget=2000", "--no-pdf-header-footer", f"--print-to-pdf={destination}", url])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--qa-dir", type=Path, required=True)
    parser.add_argument("--chrome", type=Path, default=DEFAULT_CHROME)
    parser.add_argument("--pdf-artifact", action="append", default=[])
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if not args.chrome.exists():
        raise FileNotFoundError(f"Chrome not found: {args.chrome}")
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    run([sys.executable, str(SCRIPT_ROOT / "render.py"), str(args.source), "--output", str(args.output)])

    data = json.loads(args.source.read_text(encoding="utf-8"))
    report: dict[str, object] = {"artifacts": {}, "passed": True}
    with tempfile.TemporaryDirectory(prefix="si-visual-qa-") as profile_name:
        profile = Path(profile_name)
        for artifact in data["artifacts"]:
            artifact_id = artifact["id"]
            page = args.output / f"{artifact_id}.html"
            if artifact["mode"] == "slides":
                cases = [
                    ((1440, 900), {"slide": str(index)}, f"1440x900-slide-{index:02d}")
                    for index in range(1, len(artifact["components"]) + 1)
                ]
            else:
                cases = [((1440, 1200), None, "1440x1200"), ((500, 844), None, "500x844")]
            checks = []
            for (width, height), params, label in cases:
                current = inspect_dom(args.chrome, profile, page, (width, height), params)
                screenshot_path = args.qa_dir / f"{artifact_id}-{label}.png"
                screenshot(args.chrome, profile, page, (width, height), screenshot_path, params)
                current["screenshot"] = str(screenshot_path)
                current["passed"] = (
                    not current["overflow"]
                    and not current["brokenAssets"]
                    and not current["remoteAssets"]
                    and current["landmarks"]["main"] == 1
                    and current["brandAssets"]["logos"] > 0
                    and current["brandAssets"]["favicon"]
                )
                report["passed"] = bool(report["passed"] and current["passed"])
                checks.append(current)
            if artifact_id in args.pdf_artifact:
                pdf_path = args.output / f"{artifact_id}.pdf"
                export_pdf(args.chrome, profile, page, pdf_path)
            report["artifacts"][artifact_id] = checks

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
