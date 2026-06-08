"""
_graph_client.py — Microsoft Graph API-klient med MSAL-autentisering.

Tokens lagras i macOS Keychain via keyring-biblioteket.
Inga secrets lagras i repot eller i klartext.

Beroenden (installera med pip):
    pip install msal keyring requests
"""

import json
import sys
from pathlib import Path
from typing import Optional

import keyring
import msal
import requests

KEYCHAIN_SERVICE = "superintelligent-outlook-bridge"
KEYCHAIN_ACCOUNT = "token-cache"
GRAPH_BASE = "https://graph.microsoft.com/v1.0"


class GraphClient:
    """
    Hanterar autentisering och anrop till Microsoft Graph API.

    Vid första anrop utan cachad token startar Device Code Flow:
    Användaren får en URL och en kod att klistra in i webbläsaren.
    Efterföljande anrop förnyar token tyst via refresh token i Keychain.
    """

    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self._token_cache = self._load_cache()

    # ------------------------------------------------------------------ #
    #  Config och cache                                                    #
    # ------------------------------------------------------------------ #

    def _load_config(self, config_path: Path) -> dict:
        if not config_path.exists():
            print(
                f"\nFEL: Config saknas: {config_path}\n"
                f"Skapa filen enligt scripts/outlook/config.example.json\n"
                f"och kör sedan: python scripts/outlook/auth_setup.py",
                file=sys.stderr,
            )
            sys.exit(1)
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
        required = ["client_id"]
        for key in required:
            if not config.get(key):
                print(f"FEL: '{key}' saknas i config-filen.", file=sys.stderr)
                sys.exit(1)
        return config

    def _load_cache(self) -> msal.SerializableTokenCache:
        cache = msal.SerializableTokenCache()
        cached_data = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT)
        if cached_data:
            cache.deserialize(cached_data)
        return cache

    def _save_cache(self) -> None:
        if self._token_cache.has_state_changed:
            keyring.set_password(
                KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT, self._token_cache.serialize()
            )

    def _build_app(self) -> msal.PublicClientApplication:
        tenant = self.config.get("tenant_id", "common")
        return msal.PublicClientApplication(
            client_id=self.config["client_id"],
            authority=f"https://login.microsoftonline.com/{tenant}",
            token_cache=self._token_cache,
        )

    # ------------------------------------------------------------------ #
    #  Token-hämtning                                                      #
    # ------------------------------------------------------------------ #

    def get_token(self) -> str:
        """
        Hämtar access token. Försöker tyst refresh först.
        Startar Device Code Flow om ingen cachad token finns.
        """
        scopes = self.config.get(
            "scopes", ["Mail.ReadWrite", "Mail.Send", "User.Read"]
        )
        app = self._build_app()

        # Försök tyst
        accounts = app.get_accounts()
        result = None
        if accounts:
            result = app.acquire_token_silent(scopes, account=accounts[0])

        # Device Code Flow om tyst misslyckades
        if not result or "access_token" not in result:
            flow = app.initiate_device_flow(scopes=scopes)
            if "user_code" not in flow:
                raise RuntimeError(
                    f"Kunde inte starta Device Code Flow: {flow.get('error_description', flow)}"
                )
            print("\n" + flow["message"] + "\n")
            result = app.acquire_token_by_device_flow(flow)

        self._save_cache()

        if "access_token" not in result:
            raise RuntimeError(
                f"Token-hämtning misslyckades: {result.get('error_description', result)}"
            )
        return result["access_token"]

    # ------------------------------------------------------------------ #
    #  HTTP-metoder                                                        #
    # ------------------------------------------------------------------ #

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
        }

    def get(self, path: str, params: Optional[dict] = None) -> dict:
        resp = requests.get(
            f"{GRAPH_BASE}{path}", headers=self._headers(), params=params, timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, payload: dict) -> dict:
        resp = requests.post(
            f"{GRAPH_BASE}{path}", headers=self._headers(), json=payload, timeout=30
        )
        resp.raise_for_status()
        if resp.content:
            return resp.json()
        return {}

    def patch(self, path: str, payload: dict) -> dict:
        resp = requests.patch(
            f"{GRAPH_BASE}{path}", headers=self._headers(), json=payload, timeout=30
        )
        resp.raise_for_status()
        if resp.content:
            return resp.json()
        return {}

    def post_empty(self, path: str) -> None:
        """POST utan request-body och utan förväntad response-body (t.ex. /send)."""
        resp = requests.post(
            f"{GRAPH_BASE}{path}", headers=self._headers(), timeout=30
        )
        resp.raise_for_status()
