"""
_state.py — Lokal state-hantering för Outlook Mail Bridge drafts.

State-fil: ~/.config/superintelligent/outlook-bridge/drafts.json
Ligger utanför repot och committas aldrig.

Vad som lagras: draft-ID, graph_message_id, tidsstämplar, booleaner, räknare, hash.
Vad som ALDRIG lagras: mejltext, ämnesrad, adresser, bilagsnamn, kunddata.
"""

import json
import os
import stat
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

DRAFT_TTL_HOURS = 72


class DraftState:
    """
    Hanterar lokal state-fil för aktiva drafts.

    Filen sparas med restriktiva rättigheter (600) så att bara
    ägaren kan läsa den.
    """

    def __init__(self, state_path: Path):
        self.path = state_path
        self._data = self._load()

    # ------------------------------------------------------------------ #
    #  Intern läsning och skrivning                                        #
    # ------------------------------------------------------------------ #

    def _load(self) -> dict:
        if self.path.exists():
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        return {"drafts": {}, "next_counter": 1}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Skriv atomärt via tempfil
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        tmp.replace(self.path)
        # Sätt restriktiva rättigheter: enbart ägaren kan läsa/skriva
        os.chmod(self.path, stat.S_IRUSR | stat.S_IWUSR)

    def _next_id(self) -> str:
        n = self._data.get("next_counter", 1)
        self._data["next_counter"] = n + 1
        return f"D{n}"

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def register_draft(
        self,
        graph_message_id: str,
        recipient_count: int,
        has_attachment: bool,
    ) -> str:
        """
        Registrerar ett nytt draft och returnerar kort ID (t.ex. D42).
        Lagrar aldrig mejlinnehåll.
        """
        draft_id = self._next_id()
        now = datetime.now(timezone.utc).isoformat()
        expires = (
            datetime.now(timezone.utc) + timedelta(hours=DRAFT_TTL_HOURS)
        ).isoformat()

        self._data["drafts"][draft_id] = {
            "draft_id": draft_id,
            "graph_message_id": graph_message_id,
            "created_at": now,
            "reviewed_at": None,
            "has_attachment": has_attachment,
            "recipient_count": recipient_count,
            "review_hash": None,
            "expires_at": expires,
        }
        self._save()
        return draft_id

    def mark_reviewed(
        self,
        draft_id: str,
        review_hash: str,
        has_attachment: bool,
        recipient_count: int,
    ) -> None:
        """
        Markerar draft som granskad och lagrar review-hash.
        Uppdaterar även has_attachment och recipient_count med färska värden från Graph.
        """
        if draft_id not in self._data["drafts"]:
            raise KeyError(f"Draft {draft_id} finns inte i state.")
        now = datetime.now(timezone.utc).isoformat()
        entry = self._data["drafts"][draft_id]
        entry["reviewed_at"] = now
        entry["review_hash"] = review_hash
        entry["has_attachment"] = has_attachment
        entry["recipient_count"] = recipient_count
        self._save()

    def get_draft(self, draft_id: str) -> Optional[dict]:
        """Hämtar state-post för ett draft-ID. None om det inte finns."""
        return self._data["drafts"].get(draft_id)

    def get_graph_id(self, draft_id: str) -> Optional[str]:
        """Hämtar Graph message-ID för ett kort draft-ID."""
        draft = self.get_draft(draft_id)
        return draft["graph_message_id"] if draft else None

    def list_active(self) -> list:
        """Listar ej-utgångna drafts, sorterade på created_at."""
        now = datetime.now(timezone.utc)
        active = []
        for draft in self._data["drafts"].values():
            expires = datetime.fromisoformat(draft["expires_at"])
            if expires > now:
                active.append(draft)
        return sorted(active, key=lambda d: d["created_at"])

    def purge_expired(self) -> list:
        """
        Tar bort utgångna state-poster (påverkar inte Outlook Drafts-mapp).
        Returnerar lista med borttagna draft-ID:n.
        """
        now = datetime.now(timezone.utc)
        to_remove = [
            did
            for did, d in self._data["drafts"].items()
            if datetime.fromisoformat(d["expires_at"]) <= now
        ]
        for did in to_remove:
            del self._data["drafts"][did]
        if to_remove:
            self._save()
        return to_remove
