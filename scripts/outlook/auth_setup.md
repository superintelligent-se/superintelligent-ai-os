# auth_setup.md — Inställning av Microsoft Graph-autentisering

Engångsprocedur för att koppla Outlook Mail Bridge till ditt Microsoft-konto.

---

## Steg 1 — Registrera Azure AD-app

1. Gå till [portal.azure.com](https://portal.azure.com) → **Azure Active Directory** (eller **Entra ID**)
2. Välj **App registrations** → **New registration**
3. Fyll i:
   - Name: `superintelligent-outlook-bridge` (eller valfritt)
   - Supported account types: **Accounts in this organizational directory only** (om företagskonto) eller **Personal Microsoft accounts** (om privat konto)
   - Redirect URI: Välj **Mobile and desktop application** → `https://login.microsoftonline.com/common/oauth2/nativeclient`
4. Klicka **Register**
5. Notera **Application (client) ID** och **Directory (tenant) ID** på Overview-sidan

---

## Steg 2 — Lägg till permissions

1. Välj din app → **API permissions** → **Add a permission** → **Microsoft Graph**
2. Välj **Delegated permissions** (INTE Application permissions)
3. Lägg till:
   - `Mail.ReadWrite`
   - `Mail.Send`
   - `User.Read`
4. Klicka **Add permissions**
5. Klicka **Grant admin consent** om du är administratör, annars logga in med ditt konto vid första körning

**Verifiera:** Under API permissions ska du se att kolumnen "Type" visar "Delegated" för alla tre. Om "Application" visas har du valt fel typ — ta bort och lägg till igen.

---

## Steg 3 — Skapa config-fil

Skapa katalogen och filen (utanför repot):

```bash
mkdir -p ~/.config/superintelligent/outlook-bridge
```

Skapa `~/.config/superintelligent/outlook-bridge/config.json`:

```json
{
  "client_id": "KLISTRA-IN-DIN-APPLICATION-CLIENT-ID-HÄR",
  "tenant_id": "common",
  "scopes": ["Mail.ReadWrite", "Mail.Send", "User.Read"]
}
```

- `client_id`: Application (client) ID från steg 1
- `tenant_id`: Använd `"common"` för personliga konton eller Microsoft 365 Family. För företagskonton, använd Directory (tenant) ID från steg 1.
- `scopes`: Ändra inte — matchar permissions i steg 2

```bash
# Sätt restriktiva rättigheter
chmod 600 ~/.config/superintelligent/outlook-bridge/config.json
```

---

## Steg 4 — Installera Python-beroenden

```bash
pip install msal keyring requests
```

Verifiera installation:

```bash
python -c "import msal, keyring, requests; print('OK')"
```

---

## Steg 5 — Kör första autentisering

Vid första körning av något script (t.ex. `list_drafts.py`) startar Device Code Flow automatiskt:

```
Gå till https://microsoft.com/devicelogin och ange koden: ABCD1234
```

1. Öppna länken i webbläsaren
2. Klistra in koden
3. Logga in med ditt Microsoft-konto
4. Godkänn de begärda permissions

Token sparas automatiskt i macOS Keychain under `superintelligent-outlook-bridge`. Du behöver inte logga in igen förrän refresh token löper ut (normalt flera månader).

---

## Steg 6 — Verifiera

```bash
cd /Users/thomasdalebring/Github/Superintelligent/superintelligent-ai-os
python scripts/outlook/list_drafts.py
```

Förväntad output (om inga aktiva drafts finns):

```
Inga aktiva drafts.
```

---

## Återkalla access

Om du misstänker att token eller konto är komprometterat:

1. Gå till [mysignins.microsoft.com](https://mysignins.microsoft.com) → **Security info** → Återkalla sessioner
2. Eller: Entra ID portal → Enterprise Applications → din app → Users → Revoke

Lokal Keychain-post tas bort med:

```bash
python -c "import keyring; keyring.delete_password('superintelligent-outlook-bridge', 'token-cache')"
```

---

## Vad som INTE lagras i repot

- Client ID (i config.json utanför repot)
- Tenant ID (i config.json utanför repot)
- Access tokens (i macOS Keychain)
- Refresh tokens (i macOS Keychain)
- Drafts state (i `~/.config/superintelligent/outlook-bridge/drafts.json`)
- Aktivitetslogg (i `~/.config/superintelligent/outlook-bridge/activity.log`)
