#!/usr/bin/env python3
# Auto-bootstrap: byter automatiskt till venv-Python om nödvändigt.
import sys, os as _os
from pathlib import Path as _Path
_VENV_DIR = _Path.home() / ".config/superintelligent/outlook-bridge/venv"
_VENV_PY = _VENV_DIR / "bin/python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    _os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)
"""
list_drafts.py — Lista aktiva drafts med korta ID:n från lokal state.

Usage:
    python list_drafts.py
    python list_drafts.py --purge-expired

Visar: draft-ID, skapad, granskad (reviewed), antal mottagare, bilaga.
Visar aldrig: mejltext, ämne, adresser, bilagsnamn.

Flaggan --purge-expired rensar utgångna poster från state-filen.
Påverkar inte Outlook Drafts-mapp.

Beroenden: pip install msal keyring requests
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _state import DraftState

STATE_PATH = Path.home() / ".config" / "superintelligent" / "outlook-bridge" / "drafts.json"


def fmt_ts(ts: str | None) -> str:
    """Formaterar ISO-tidsstämpel till läsbar form."""
    if not ts:
        return "—"
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return ts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lista aktiva Outlook-drafts med korta ID:n."
    )
    parser.add_argument(
        "--purge-expired",
        action="store_true",
        help="Ta bort utgångna poster från state-filen",
    )
    args = parser.parse_args()

    state = DraftState(STATE_PATH)

    if args.purge_expired:
        removed = state.purge_expired()
        if removed:
            print(f"Rensade {len(removed)} utgångna poster: {', '.join(removed)}")
        else:
            print("Inga utgångna poster att rensa.")

    drafts = state.list_active()

    if not drafts:
        print("Inga aktiva drafts.")
        return

    # Kolumnbredder
    col_id = 6
    col_created = 17
    col_reviewed = 17
    col_rcpt = 11
    col_attach = 8

    header = (
        f"{'ID':<{col_id}}  "
        f"{'Skapad':<{col_created}}  "
        f"{'Granskad':<{col_reviewed}}  "
        f"{'Mottagare':<{col_rcpt}}  "
        f"{'Bilaga':<{col_attach}}"
    )
    sep = "─" * len(header)

    print(sep)
    print(header)
    print(sep)

    for d in drafts:
        reviewed = fmt_ts(d.get("reviewed_at"))
        attach = "Ja" if d.get("has_attachment") else "Nej"
        print(
            f"{d['draft_id']:<{col_id}}  "
            f"{fmt_ts(d['created_at']):<{col_created}}  "
            f"{reviewed:<{col_reviewed}}  "
            f"{str(d.get('recipient_count', '?')):<{col_rcpt}}  "
            f"{attach:<{col_attach}}"
        )

    print(sep)
    print(f"\nAnvändning:")
    print(f"  python scripts/outlook/review_draft.py --id <ID>")
    print(f"  python scripts/outlook/send_draft.py \"OK <ID>\"")


if __name__ == "__main__":
    main()
