#!/usr/bin/env python3
# Auto-bootstrap: byter automatiskt till venv-Python om nödvändigt.
import sys, os as _os
from pathlib import Path as _Path
_VENV_DIR = _Path.home() / ".config/superintelligent/outlook-bridge/venv"
_VENV_PY = _VENV_DIR / "bin/python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    _os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)
"""
create_reply_draft.py — Skapa ett reply-draft på ett befintligt Outlook-mejl.

Usage:
    python create_reply_draft.py \\
        --message-id "AAMkAGZj..." \\
        --body "Tack för din återkoppling. Vi återkommer..."

    # Svar till alla (reply-all):
    python create_reply_draft.py \\
        --message-id "AAMkAGZj..." \\
        --body "Svarstext" \\
        --reply-all

Skapar reply-draft via Graph createReply-endpoint, PATCHar med svarstext,
och registrerar kort draft-ID i lokal state.
Skickar aldrig. Lagrar aldrig mejlinnehåll i state eller repo.

Beroenden: pip install msal keyring requests
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _graph_client import GraphClient
from _state import DraftState

CONFIG_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "config.json"
STATE_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "drafts.json"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Skapa ett reply-draft på ett befintligt Outlook-mejl."
    )
    parser.add_argument(
        "--message-id",
        required=True,
        help="Graph message-ID för mejlet som ska besvaras (AAMkAGZj...)",
    )
    parser.add_argument("--body", required=True, help="Svarstext")
    parser.add_argument(
        "--body-type",
        choices=["text", "html"],
        default="text",
        help="Innehållstyp för svarstext (standard: text)",
    )
    parser.add_argument(
        "--reply-all",
        action="store_true",
        help="Svara till alla mottagare (reply-all)",
    )
    args = parser.parse_args()

    client = GraphClient(CONFIG_PATH)

    # Steg 1: Skapa reply-draft via Graph
    # createReply kopierar originalmejlets From → To automatiskt
    endpoint = (
        f"/me/messages/{args.message_id}/createReplyAll"
        if args.reply_all
        else f"/me/messages/{args.message_id}/createReply"
    )

    try:
        reply_message = client.post(endpoint, {})
    except Exception as exc:
        print(f"FEL vid skapande av reply-draft: {exc}", file=sys.stderr)
        sys.exit(1)

    reply_id = reply_message["id"]

    # Steg 2: Uppdatera reply-draften med svarstext
    try:
        updated = client.patch(
            f"/me/messages/{reply_id}",
            {
                "body": {
                    "contentType": args.body_type,
                    "content": args.body,
                }
            },
        )
    except Exception as exc:
        print(f"FEL vid uppdatering av reply-draft: {exc}", file=sys.stderr)
        sys.exit(1)

    # Hämta aktuell mottagarinformation från den färdiga draften
    to = updated.get("toRecipients", [])
    cc = updated.get("ccRecipients", [])
    bcc = updated.get("bccRecipients", [])
    recipient_count = len(to) + len(cc) + len(bcc)
    has_attachment = updated.get("hasAttachments", False)

    # Registrera i lokal state (inget mejlinnehåll lagras)
    state = DraftState(STATE_PATH)
    draft_id = state.register_draft(
        graph_message_id=reply_id,
        recipient_count=recipient_count,
        has_attachment=has_attachment,
    )

    reply_type = "Reply-all draft" if args.reply_all else "Reply draft"
    print(f"✓ {reply_type} skapad: {draft_id}")
    print(f"  Mottagare: {recipient_count}")
    print(f"  Bilaga: {'Ja' if has_attachment else 'Nej'}")
    print(f"\nObs: Verifiera mottagarlistan i review — originalmejlets adresser")
    print(f"     fylls i automatiskt av Graph.")
    print(f"\nNästa steg:")
    print(f"  python scripts/outlook/review_draft.py --id {draft_id}")


if __name__ == "__main__":
    main()
