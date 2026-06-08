#!/usr/bin/env python3
# Auto-bootstrap: byter automatiskt till venv-Python om nödvändigt.
# Kräver ingen manuell aktivering av virtual environment.
import sys, os as _os
from pathlib import Path as _Path
_VENV_DIR = _Path.home() / ".config/superintelligent/outlook-bridge/venv"
_VENV_PY = _VENV_DIR / "bin/python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    _os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)
"""
create_draft.py — Skapa ett nytt Outlook-draft via Microsoft Graph.

Usage:
    python create_draft.py --to "anna@example.com" --subject "Ämne" --body "Text"
    python create_draft.py --to "anna@example.com,bob@example.com" \\
        --cc "charlotte@example.com" --subject "Ämne" --body "Text"
    python create_draft.py --to "anna@example.com" \\
        --subject "HTML-mejl" --body "<p>Text</p>" --body-type html

Skapar draft i Outlook Drafts-mapp och registrerar kort ID (D42, D43...)
i lokal state-fil. Skickar aldrig. Lagrar aldrig mejlinnehåll i state eller repo.

Beroenden: pip install msal keyring requests
"""

import argparse
import sys
from pathlib import Path

# Lägg till scripts/outlook/ i sökväg för delade moduler
sys.path.insert(0, str(Path(__file__).parent))

from _graph_client import GraphClient
from _state import DraftState

CONFIG_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "config.json"
STATE_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "drafts.json"


def parse_addresses(raw: str) -> list:
    """Parsar kommaseparerade e-postadresser till Graph-format."""
    if not raw:
        return []
    result = []
    for addr in raw.split(","):
        addr = addr.strip()
        if addr:
            result.append({"emailAddress": {"address": addr}})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Skapa ett nytt Outlook-draft via Microsoft Graph."
    )
    parser.add_argument("--to", required=True, help="To-adresser, kommaseparerade")
    parser.add_argument("--cc", default="", help="CC-adresser, kommaseparerade")
    parser.add_argument("--bcc", default="", help="BCC-adresser, kommaseparerade")
    parser.add_argument("--subject", required=True, help="Ämnesrad")
    parser.add_argument("--body", required=True, help="Brödtext")
    parser.add_argument(
        "--body-type",
        choices=["text", "html"],
        default="text",
        help="Innehållstyp för brödtext (standard: text)",
    )
    args = parser.parse_args()

    to = parse_addresses(args.to)
    cc = parse_addresses(args.cc)
    bcc = parse_addresses(args.bcc)

    if not to:
        print("FEL: --to kräver minst en e-postadress.", file=sys.stderr)
        sys.exit(1)

    # Bygg Graph-payload — skickar aldrig automatiskt
    payload: dict = {
        "subject": args.subject,
        "isDraft": True,
        "body": {
            "contentType": args.body_type,
            "content": args.body,
        },
        "toRecipients": to,
    }
    if cc:
        payload["ccRecipients"] = cc
    if bcc:
        payload["bccRecipients"] = bcc

    client = GraphClient(CONFIG_PATH)

    try:
        message = client.post("/me/messages", payload)
    except Exception as exc:
        print(f"FEL vid skapande av draft: {exc}", file=sys.stderr)
        sys.exit(1)

    graph_id = message["id"]
    recipient_count = len(to) + len(cc) + len(bcc)
    has_attachment = message.get("hasAttachments", False)

    # Registrera i lokal state (inget mejlinnehåll lagras)
    state = DraftState(STATE_PATH)
    draft_id = state.register_draft(
        graph_message_id=graph_id,
        recipient_count=recipient_count,
        has_attachment=has_attachment,
    )

    print(f"✓ Draft skapad: {draft_id}")
    print(f"  Mottagare: {recipient_count}")
    print(f"  Bilaga: {'Ja' if has_attachment else 'Nej'}")
    print(f"\nNästa steg:")
    print(f"  python scripts/outlook/review_draft.py --id {draft_id}")


if __name__ == "__main__":
    main()
