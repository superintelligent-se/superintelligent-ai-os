"""
tools.py — Graph API-verktyg för Mini (Telegram-assistenten).

Innehåller:
  TOOL_DEFINITIONS  — Anthropic tool-schema som skickas till Claude
  execute_tool()    — dispatcher som kör rätt funktion
  _get_calendar_events(), _get_emails(), _get_tasks(), _search_people()

Importerar GraphClient från scripts/outlook/_graph_client.py.
Alla funktioner returnerar en sträng som Claude kan läsa direkt.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# Lägg till outlook-katalogen i path så vi kan importera GraphClient
_OUTLOOK_DIR = Path(__file__).parent.parent / "outlook"
if str(_OUTLOOK_DIR) not in sys.path:
    sys.path.insert(0, str(_OUTLOOK_DIR))

from _graph_client import GraphClient  # noqa: E402

_CONFIG_PATH = Path.home() / ".config/superintelligent/outlook-bridge/config.json"

# Stockholm-tidszon (undviker zoneinfo-beroende, använder UTC-offset)
_STOCKHOLM_OFFSET_SUMMER = timedelta(hours=2)   # CEST (mars–oktober)
_STOCKHOLM_OFFSET_WINTER = timedelta(hours=1)   # CET  (oktober–mars)


def _stockholm_offset() -> timedelta:
    """Returnerar aktuell UTC-offset för Stockholm (hanterar sommartid manuellt)."""
    now = datetime.now(timezone.utc)
    # Sommartid: sista söndagen i mars till sista söndagen i oktober (approximation)
    month = now.month
    if 4 <= month <= 9:
        return _STOCKHOLM_OFFSET_SUMMER
    if month == 3 and now.day >= 25:
        return _STOCKHOLM_OFFSET_SUMMER
    if month == 10 and now.day < 25:
        return _STOCKHOLM_OFFSET_SUMMER
    return _STOCKHOLM_OFFSET_WINTER


def _to_stockholm(dt_str: str) -> str:
    """Konverterar en ISO-8601 datetime-sträng till lokal Stockholm-tid (HH:MM)."""
    try:
        # Hantera både 'Z' och '+00:00' suffix
        dt_str = dt_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local = dt + _stockholm_offset()
        return local.strftime("%H:%M")
    except Exception:
        return dt_str[:16]


def _graph() -> GraphClient:
    return GraphClient(_CONFIG_PATH)


# ─────────────────────────────────────────────────────────────────────────────
# Tool definitions (Anthropic-format)
# ─────────────────────────────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "get_calendar_events",
        "description": (
            "Hämtar möten och kalenderinbjudningar från Thomas Microsoft 365-kalender. "
            "Använd när Thomas frågar om sin dag, sina möten, vad som är inplanerat, "
            "eller när du behöver veta om Thomas är ledig vid en viss tid."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": (
                        "Datum att hämta möten för, format YYYY-MM-DD. "
                        "Utelämna för att få dagens möten."
                    ),
                },
                "days": {
                    "type": "integer",
                    "description": "Antal dagar att hämta möten för (från date). Standard: 1.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_emails",
        "description": (
            "Hämtar e-postmeddelanden från Thomas Microsoft 365-inkorg. "
            "Använd när Thomas frågar om sina mejl, vad som kommit in, "
            "om någon specifik person hört av sig, eller för inbox-triage."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string",
                    "description": "Mapp att läsa. Värden: inbox, drafts, sent. Standard: inbox.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max antal mejl att returnera. Standard: 10.",
                },
                "unread_only": {
                    "type": "boolean",
                    "description": "Om true, returnera bara olästa mejl. Standard: false.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_tasks",
        "description": (
            "Hämtar uppgifter från Thomas Microsoft To Do. "
            "Använd när Thomas frågar vad han har att göra, vilka tasks som väntar, "
            "eller vad som är på hans lista."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "include_completed": {
                    "type": "boolean",
                    "description": "Om true, inkludera avklarade uppgifter. Standard: false.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "search_people",
        "description": (
            "Söker efter en person i Microsoft 365-katalogen. "
            "Använd när Thomas nämner ett namn och du behöver hitta personens "
            "e-postadress, titel eller avdelning."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Namn att söka på.",
                },
            },
            "required": ["name"],
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher
# ─────────────────────────────────────────────────────────────────────────────

def execute_tool(name: str, tool_input: dict) -> str:
    """Kör rätt verktyg och returnera resultatet som en sträng."""
    try:
        if name == "get_calendar_events":
            return _get_calendar_events(**tool_input)
        elif name == "get_emails":
            return _get_emails(**tool_input)
        elif name == "get_tasks":
            return _get_tasks(**tool_input)
        elif name == "search_people":
            return _search_people(**tool_input)
        else:
            return f"Okänt verktyg: {name}"
    except Exception as exc:
        return f"FEL vid körning av {name}: {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# Implementationer
# ─────────────────────────────────────────────────────────────────────────────

def _get_calendar_events(date: Optional[str] = None, days: int = 1) -> str:
    """Hämtar möten från kalender via Graph calendarView."""
    offset = _stockholm_offset()

    # Beräkna tidsintervall (lokal tid → UTC)
    if date:
        try:
            start_local = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return f"Ogiltigt datumformat: {date}. Använd YYYY-MM-DD."
    else:
        now_local = datetime.now(timezone.utc) + offset
        start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        start_local = start_local.replace(tzinfo=None)

    end_local = start_local + timedelta(days=max(1, days))

    # Konvertera till UTC för Graph API
    start_utc = (start_local - offset).replace(tzinfo=timezone.utc)
    end_utc   = (end_local   - offset).replace(tzinfo=timezone.utc)

    start_str = start_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str   = end_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        g = _graph()
        data = g.get(
            "/me/calendarView",
            params={
                "startDateTime": start_str,
                "endDateTime": end_str,
                "$select": "subject,start,end,location,organizer,attendees,isOnlineMeeting,isCancelled,showAs",
                "$orderby": "start/dateTime",
                "$top": "50",
            },
        )
    except Exception as exc:
        return (
            f"Kunde inte hämta kalender: {exc}\n"
            "Tips: Kör scripts/outlook/reauth.py om du nyligen lade till nya behörigheter."
        )

    events = data.get("value", [])
    if not events:
        day_str = date or "idag"
        return f"Inga möten {day_str}."

    lines = []
    for ev in events:
        if ev.get("isCancelled"):
            continue
        start_time = _to_stockholm(ev["start"]["dateTime"])
        end_time   = _to_stockholm(ev["end"]["dateTime"])
        subject    = ev.get("subject", "(Utan titel)")
        location   = ev.get("location", {}).get("displayName", "")
        online     = ev.get("isOnlineMeeting", False)
        organizer  = ev.get("organizer", {}).get("emailAddress", {}).get("name", "")
        attendees  = [
            a["emailAddress"]["name"]
            for a in ev.get("attendees", [])[:5]
            if a.get("emailAddress", {}).get("name")
        ]

        line = f"{start_time}–{end_time}  {subject}"
        if location and not online:
            line += f"  📍 {location}"
        elif online:
            line += "  💻 Teams"
        if organizer:
            line += f"\n   Arrangör: {organizer}"
        if attendees:
            line += f"\n   Deltagare: {', '.join(attendees)}"
        lines.append(line)

    header = f"Kalender {date or 'idag'} ({len(lines)} möten):"
    return header + "\n\n" + "\n\n".join(lines)


def _get_emails(
    folder: str = "inbox",
    max_results: int = 10,
    unread_only: bool = False,
) -> str:
    """Hämtar e-post via Graph."""
    folder_map = {
        "inbox":  "inbox",
        "drafts": "drafts",
        "sent":   "sentitems",
    }
    graph_folder = folder_map.get(folder.lower(), "inbox")

    params = {
        "$select": "subject,from,receivedDateTime,isRead,bodyPreview",
        "$orderby": "receivedDateTime desc",
        "$top": str(min(max_results, 25)),
    }
    if unread_only:
        params["$filter"] = "isRead eq false"

    try:
        g = _graph()
        data = g.get(f"/me/mailFolders/{graph_folder}/messages", params=params)
    except Exception as exc:
        return f"Kunde inte hämta mejl: {exc}"

    messages = data.get("value", [])
    if not messages:
        return f"Inga mejl i {folder}."

    lines = []
    for m in messages:
        received = m.get("receivedDateTime", "")[:16].replace("T", " ")
        sender   = m.get("from", {}).get("emailAddress", {}).get("name", "Okänd")
        subject  = m.get("subject", "(Utan ämne)")
        preview  = m.get("bodyPreview", "")[:120]
        read_mark = "" if m.get("isRead") else "🔵 "
        lines.append(f"{read_mark}{received}  {sender}\n   {subject}\n   {preview}")

    header = f"Mejl ({folder}, {len(lines)} st):"
    return header + "\n\n" + "\n\n".join(lines)


def _get_tasks(include_completed: bool = False) -> str:
    """Hämtar uppgifter från Microsoft To Do."""
    try:
        g = _graph()
        lists_data = g.get("/me/todo/lists")
        task_lists = lists_data.get("value", [])
    except Exception as exc:
        return f"Kunde inte hämta uppgiftslistor: {exc}"

    if not task_lists:
        return "Inga uppgiftslistor hittades i Microsoft To Do."

    all_tasks = []
    for lst in task_lists:
        list_id   = lst["id"]
        list_name = lst.get("displayName", "Lista")
        params = {
            "$select": "title,status,dueDateTime,importance,body",
            "$top": "50",
        }
        if not include_completed:
            params["$filter"] = "status ne 'completed'"

        try:
            tasks_data = g.get(f"/me/todo/lists/{list_id}/tasks", params=params)
            for t in tasks_data.get("value", []):
                due = ""
                if t.get("dueDateTime"):
                    due = "  ⏰ " + t["dueDateTime"]["dateTime"][:10]
                important = "⭐ " if t.get("importance") == "high" else ""
                all_tasks.append(f"{important}{t.get('title', '?')}{due}  [{list_name}]")
        except Exception:
            continue

    if not all_tasks:
        return "Inga öppna uppgifter i Microsoft To Do."

    return f"Uppgifter ({len(all_tasks)} st):\n\n" + "\n".join(all_tasks)


def _search_people(name: str) -> str:
    """Söker efter en person i katalogen."""
    try:
        g = _graph()
        # Prova People API först (ger "relevanta" personer)
        data = g.get(
            "/me/people",
            params={
                "$search": name,
                "$select": "displayName,emailAddresses,jobTitle,department,phones",
                "$top": "5",
            },
        )
        people = data.get("value", [])
    except Exception:
        people = []

    if not people:
        # Fallback: Users-katalogen
        try:
            g = _graph()
            data = g.get(
                "/users",
                params={
                    "$search": f'"displayName:{name}"',
                    "$select": "displayName,mail,jobTitle,department,mobilePhone",
                    "$top": "5",
                    "ConsistencyLevel": "eventual",
                },
            )
            users = data.get("value", [])
            if not users:
                return f"Ingen person hittad för '{name}'."
            lines = []
            for u in users:
                line = u.get("displayName", "?")
                if u.get("mail"):
                    line += f"  {u['mail']}"
                if u.get("jobTitle"):
                    line += f"\n   Titel: {u['jobTitle']}"
                if u.get("department"):
                    line += f"  |  Avdelning: {u['department']}"
                lines.append(line)
            return "\n\n".join(lines)
        except Exception as exc:
            return f"Sökning misslyckades: {exc}"

    lines = []
    for p in people:
        emails = [e["address"] for e in p.get("emailAddresses", []) if e.get("address")]
        line = p.get("displayName", "?")
        if emails:
            line += f"  {emails[0]}"
        if p.get("jobTitle"):
            line += f"\n   Titel: {p['jobTitle']}"
        if p.get("department"):
            line += f"  |  Avdelning: {p['department']}"
        lines.append(line)

    return "\n\n".join(lines)
