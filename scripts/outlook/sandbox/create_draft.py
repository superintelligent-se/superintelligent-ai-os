#!/usr/bin/env python3
"""
create_draft.py (sandbox) — Skapar Outlook-draft via Microsoft Graph API.

Kräver inga externa beroenden — bara Python stdlib (urllib, json, pathlib).
Credentials läses från .secret/credentials.json i repo-roten (gitignorerat).

Usage:
    python3 scripts/outlook/sandbox/create_draft.py \\
        --to "anna@example.com" --subject "Ämne" --body "Text"

Token-rotation:
    Om access_token har gått ut används refresh_token automatiskt.
    Nya tokens sparas tillbaka till .secret/credentials.json.
    Microsoft refresh tokens är giltiga i 14 dagar om de inte används —
    om scheduled task kör dagligen förnyas de automatiskt och löper aldrig ut.
"""

import argparse
import json
import os
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent  # sandbox/ -> outlook/ -> scripts/ -> repo root
SECRET_DIR = REPO_ROOT / ".secret"
CREDS_FILE = SECRET_DIR / "credentials.json"
STATE_FILE = SECRET_DIR / "draft_state.json"


# ── Credentials ──────────────────────────────────────────────────────────────

def load_creds() -> dict:
    if not CREDS_FILE.exists():
        print(
            f"FEL: {CREDS_FILE} saknas.\n"
            "Kör: bash scripts/outlook/setup_sandbox_credentials.sh",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.loads(CREDS_FILE.read_text())


def save_creds(creds: dict) -> None:
    SECRET_DIR.mkdir(exist_ok=True)
    CREDS_FILE.write_text(json.dumps(creds, indent=2, ensure_ascii=False))
    os.chmod(CREDS_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 600


# ── Token ─────────────────────────────────────────────────────────────────────

def get_access_token(creds: dict) -> str:
    g = creds["graph"]
    expires = datetime.fromisoformat(g["token_expires"])

    # Fortfarande giltig (5 min marginal)
    if datetime.now(timezone.utc) < expires - timedelta(minutes=5):
        return g["access_token"]

    # Förnya via refresh token
    if not g.get("refresh_token"):
        print(
            "FEL: access_token har gått ut och ingen refresh_token finns.\n"
            "Kör: bash scripts/outlook/setup_sandbox_credentials.sh",
            file=sys.stderr,
        )
        sys.exit(1)

    url = TOKEN_URL.format(tenant=g["tenant_id"])
    body = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "refresh_token": g["refresh_token"],
        "client_id":     g["client_id"],
        "scope":         "Mail.ReadWrite Mail.Send User.Read offline_access",
    }).encode()

    req = urllib.request.Request(url, data=body, method="POST",
                                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"FEL vid token-refresh: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    if "access_token" not in result:
        print(f"FEL: Token-refresh misslyckades: {result}", file=sys.stderr)
        sys.exit(1)

    expires_in = result.get("expires_in", 3600)
    g["access_token"]  = result["access_token"]
    g["token_expires"] = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
    if "refresh_token" in result:
        g["refresh_token"] = result["refresh_token"]

    save_creds(creds)
    return g["access_token"]


# ── Graph API ─────────────────────────────────────────────────────────────────

def graph_post(token: str, path: str, payload: dict) -> dict:
    url  = f"{GRAPH_BASE}{path}"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(
        url, data=data, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"FEL vid Graph-anrop ({path}): {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


# ── Draft ID (lokal räknare i .secret/) ──────────────────────────────────────

def next_draft_id() -> str:
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
    else:
        state = {"next_counter": 1}
    n = state["next_counter"]
    state["next_counter"] = n + 1
    SECRET_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))
    return f"D{n}"


# ── Adresser ──────────────────────────────────────────────────────────────────

def parse_addresses(raw: str) -> list:
    if not raw:
        return []
    return [{"emailAddress": {"address": a.strip()}}
            for a in raw.split(",") if a.strip()]


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Skapa Outlook-draft via Graph API (sandbox, kräver .secret/credentials.json)."
    )
    parser.add_argument("--to",        required=True, help="To-adresser, kommaseparerade")
    parser.add_argument("--cc",        default="",    help="CC-adresser")
    parser.add_argument("--bcc",       default="",    help="BCC-adresser")
    parser.add_argument("--subject",   required=True, help="Ämnesrad")
    parser.add_argument("--body",      required=True, help="Brödtext")
    parser.add_argument("--body-type", choices=["text", "html"], default="text")
    args = parser.parse_args()

    to  = parse_addresses(args.to)
    cc  = parse_addresses(args.cc)
    bcc = parse_addresses(args.bcc)

    if not to:
        print("FEL: --to kräver minst en e-postadress.", file=sys.stderr)
        sys.exit(1)

    creds = load_creds()
    token = get_access_token(creds)

    payload: dict = {
        "subject": args.subject,
        "isDraft": True,
        "body": {"contentType": args.body_type, "content": args.body},
        "toRecipients": to,
    }
    if cc:  payload["ccRecipients"]  = cc
    if bcc: payload["bccRecipients"] = bcc

    message         = graph_post(token, "/me/messages", payload)
    draft_id        = next_draft_id()
    recipient_count = len(to) + len(cc) + len(bcc)
    has_attachment  = message.get("hasAttachments", False)

    # Human-readable output
    print(f"✓ Draft skapad: {draft_id}")
    print(f"  Mottagare: {recipient_count}")
    print(f"  Bilaga: {'Ja' if has_attachment else 'Nej'}")

    # Machine-readable (parsas av SKILL.md)
    print(f"DRAFT_ID={draft_id}")
    print(f"RECIPIENT_COUNT={recipient_count}")
    print(f"HAS_ATTACHMENT={'true' if has_attachment else 'false'}")


if __name__ == "__main__":
    main()
