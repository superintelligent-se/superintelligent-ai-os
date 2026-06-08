# Microsoft Graph — Endpoints och permissions (v0.1)

## Permissions — Delegated only

| Permission | Syfte |
|---|---|
| `Mail.ReadWrite` | Skapa, läsa och uppdatera drafts |
| `Mail.Send` | Skicka drafts |
| `User.Read` | Verifiera inloggad användares identitet |

**Aldrig application permissions.** Application permissions ger access på alla användares vägnar i tenanten och bryter mot säkerhetsmodellen. Verifiera i Azure Portal (Entra ID → App registrations → API permissions) att noll application permissions finns.

---

## Azure AD App-registrering

- App-typ: **Public client** (Native/Mobile application)
- Platform: **Mobile and desktop application**
- Redirect URI: `https://login.microsoftonline.com/common/oauth2/nativeclient`
- Ingen client secret behövs (public client)
- Auth-flöde: **Device Code Flow** via MSAL för Python

Client ID är inte en hemlighet men ska ändå förvaras i config-fil utanför repot (`~/.config/superintelligent/outlook-bridge/config.json`), aldrig committad.

---

## Graph-endpoints som används i v0.1

| Endpoint | Metod | Syfte |
|---|---|---|
| `/me` | GET | Hämta inloggad användare (verifiera identitet) |
| `/me/messages` | POST | Skapa nytt draft (`isDraft: true`) |
| `/me/messages/{id}/createReply` | POST | Skapa reply-draft från befintligt mejl |
| `/me/messages/{id}` | GET | Hämta draft för review och pre-send-verifiering |
| `/me/messages/{id}` | PATCH | Uppdatera draft (ämne, text) |
| `/me/messages/{id}/send` | POST | Skicka draft — **enda send-metod som används** |
| `/me/mailFolders/drafts/messages` | GET | Lista drafts-mapp |

### Endpoints som medvetet INTE används i v0.1

| Endpoint | Varför utesluten |
|---|---|
| `POST /me/sendMail` | Kringgår draft-review-flödet — kan skicka utan att draft skapas |
| `DELETE /me/messages/{id}` | Draft-radering implementeras inte i v0.1 |
| `POST /me/messages/{id}/attachments` | Bilageuppladdning implementeras inte i v0.1 |

---

## Fält från GET /me/messages/{id} som används

```json
{
  "id": "AAMkAGZj...",
  "subject": "...",
  "isDraft": true,
  "hasAttachments": false,
  "toRecipients":  [{"emailAddress": {"address": "...", "name": "..."}}],
  "ccRecipients":  [],
  "bccRecipients": [],
  "body": {"contentType": "text", "content": "..."},
  "createdDateTime": "2026-06-04T10:23:44Z"
}
```

`recipient_count = len(toRecipients) + len(ccRecipients) + len(bccRecipients)`

---

## Token-hantering

- Tokens lagras i **macOS Keychain** via `keyring`-biblioteket
- MSAL SerializableTokenCache serialiseras till Keychain-posten `superintelligent-outlook-bridge`
- Access token: livslängd ~1 timme, förnyas tyst via refresh token
- Refresh token: långlivad, knyten till din inloggning
- Tokens hamnar aldrig i repot, aldrig i loggfiler

### Återkalla access

Om token-kompromiss misstänks: gå till Entra ID → Enterprise Applications → [din app] → Users and groups → Revoke sessions.
