#!/usr/bin/env python3
# Auto-bootstrap: byter automatiskt till venv-Python om nödvändigt.
import sys, os as _os
from pathlib import Path as _Path
_VENV_DIR = _Path.home() / ".config/superintelligent/outlook-bridge/venv"
_VENV_PY = _VENV_DIR / "bin/python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    _os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)

"""
create_and_send.py — Skapa och skicka ett mejl direkt via Microsoft Graph.

Körs av assistant_bot.py på Mac mini när Thomas bekräftar ett draft via Telegram.
Använder Keychain-autentisering (MSAL) — kräver att autentisering gjorts minst en gång.

Usage:
    python scripts/outlook/create_and_send.py \\
        --to "mottagare@example.com" \\
        --subject "Ämnesrad" \\
        --body "Hela brödtexten här"

Krav:
    - ~/.config/superintelligent/outlook-bridge/config.json
    - Token i macOS Keychain (service: superintelligent-outlook-bridge)
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _graph_client import GraphClient

CONFIG_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "config.json"
LOG_PATH    = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "activity.log"


def setup_logger() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("outlook-bridge")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter('{"ts": "%(asctime)s", %(message)s}', datefmt="%Y-%m-%dT%H:%M:%SZ")
        )
        logger.addHandler(handler)
    return logger


def parse_addresses(raw: str) -> list:
    return [
        {"emailAddress": {"address": a.strip()}}
        for a in raw.split(",") if a.strip()
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Skapa och skicka ett mejl via Microsoft Graph (använder Keychain-auth)."
    )
    parser.add_argument("--to",        required=True, help="Mottagare, kommaseparerade")
    parser.add_argument("--cc",        default="",    help="CC-mottagare")
    parser.add_argument("--subject",   required=True, help="Ämnesrad")
    parser.add_argument("--body",      required=True, help="Brödtext (plain text)")
    parser.add_argument("--body-type", choices=["text", "html"], default="text")
    args = parser.parse_args()

    logger = setup_logger()

    to  = parse_addresses(args.to)
    cc  = parse_addresses(args.cc)

    if not to:
        print("FEL: --to kräver minst en e-postadress.", file=sys.stderr)
        sys.exit(1)

    recipient_count = len(to) + len(cc)

    try:
        client = GraphClient(CONFIG_PATH)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"FEL: Kunde inte initiera GraphClient: {exc}", file=sys.stderr)
        sys.exit(1)

    payload = {
        "message": {
            "subject": args.subject,
            "body": {
                "contentType": "HTML" if args.body_type == "html" else "Text",
                "content": args.body,
            },
            "toRecipients": to,
        },
        "saveToSentItems": True,
    }
    if cc:
        payload["message"]["ccRecipients"] = cc

    try:
        client.post("/me/sendMail", payload)
    except Exception as exc:
        print(f"FEL: Kunde inte skicka mejlet: {exc}", file=sys.stderr)
        logger.error(
            '"action": "send_failed", "to": "%s", "subject": "%s", "error": "%s"',
            args.to[:80], args.subject[:80], str(exc)[:120],
        )
        sys.exit(1)

    logger.info(
        '"action": "send_completed", "to": "%s", "subject": "%s", "recipient_count": %d',
        args.to[:80], args.subject[:80], recipient_count,
    )
    print(f"✓ Mejl skickat till {args.to}")


if __name__ == "__main__":
    main()
