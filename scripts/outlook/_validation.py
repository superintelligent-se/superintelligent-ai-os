"""
_validation.py — OK-kommando grammar och validering för Outlook Mail Bridge.

Grammar:
    OK <draft_id>           Standardskickning
    OK <draft_id> B         Bekräftelse: draften har bilaga
    OK <draft_id> FM        Bekräftelse: fler än 3 mottagare totalt
    OK <draft_id> B FM      Bekräftelse: bilaga + fler än 3 mottagare

- Case-insensitivt: "ok d42 b fm" → "OK D42 B FM"
- B ska stå före FM om båda anges (kanonisk ordning)
- Accepterar aldrig: "OK", "skicka", "ja", "kör", "ser bra ut", "yes", "send"

Returtyp för parse_ok_command:
    (is_valid: bool, draft_id: str|None, tokens: set|None, error: str|None)
"""

import re
from typing import Optional, Tuple

# Kanoniskt mönster: OK <D\d+> [B] [FM]
_OK_PATTERN = re.compile(
    r"^OK\s+(D\d+)(?:\s+(B))?(?:\s+(FM))?$",
    re.IGNORECASE,
)

# Fraser som ska avvisas med specifikt felmeddelande
_VAGUE_PHRASES = frozenset(
    {"ok", "skicka", "ja", "kör", "ser bra ut", "yes", "send", "looks good", "go ahead"}
)


def parse_ok_command(
    user_input: str,
) -> Tuple[bool, Optional[str], Optional[set], Optional[str]]:
    """
    Parsar ett OK-kommando från användarens inmatning.

    Returns:
        (is_valid, draft_id, tokens, error_message)
        - draft_id: normaliserat till versaler, t.ex. "D42"
        - tokens: set med "B" och/eller "FM"
        - error_message: förklarande text om is_valid är False
    """
    text = user_input.strip()
    lower = text.lower()

    # Enstaka vaga fraser
    if lower in _VAGUE_PHRASES:
        return False, None, None, (
            "Okänt kommando. Bekräfta med: OK D<nummer>\n"
            "Exempel: OK D42"
        )

    # Bara "OK" utan ID
    if re.fullmatch(r"ok", lower):
        return False, None, None, (
            "Ange draft-ID. Använd: OK D<nummer>\n"
            "Exempel: OK D42"
        )

    # "OK B" utan ID
    if re.fullmatch(r"ok\s+b", lower):
        return False, None, None, (
            "Ange draft-ID. Använd: OK D<nummer> B\n"
            "Exempel: OK D42 B"
        )

    # "OK FM" utan ID
    if re.fullmatch(r"ok\s+fm", lower):
        return False, None, None, (
            "Ange draft-ID. Använd: OK D<nummer> FM\n"
            "Exempel: OK D42 FM"
        )

    # "skicka ..." varianter
    if re.match(r"skicka", lower):
        return False, None, None, (
            "Okänt kommando. Bekräfta med: OK D<nummer>\n"
            "Exempel: OK D42"
        )

    # Huvudmatch — fullmatch för att avvisa extra text efter kommandot
    m = _OK_PATTERN.fullmatch(text)
    if not m:
        return False, None, None, (
            "Okänt format. Giltiga format:\n"
            "  OK D42\n"
            "  OK D42 B          (om draften har bilaga)\n"
            "  OK D42 FM         (om fler än 3 mottagare totalt)\n"
            "  OK D42 B FM       (om bilaga och fler än 3 mottagare)"
        )

    draft_id = m.group(1).upper()
    tokens: set = set()
    if m.group(2):
        tokens.add("B")
    if m.group(3):
        tokens.add("FM")

    return True, draft_id, tokens, None


def validate_tokens(
    draft_id: str,
    tokens: set,
    has_attachment: bool,
    recipient_count: int,
) -> Tuple[bool, Optional[str]]:
    """
    Kontrollerar att tokens täcker alla obligatoriska bekräftelser för draften.

    Returns:
        (is_valid, error_message)
    """
    errors = []

    if has_attachment and "B" not in tokens:
        expected = _expected_command(draft_id, has_attachment, recipient_count)
        errors.append(
            f"Draften har bilaga. Bekräfta med: {expected}"
        )

    if recipient_count > 3 and "FM" not in tokens:
        expected = _expected_command(draft_id, has_attachment, recipient_count)
        errors.append(
            f"Draften har {recipient_count} mottagare (>3). Bekräfta med: {expected}"
        )

    if errors:
        return False, "\n".join(errors)
    return True, None


def _expected_command(draft_id: str, has_attachment: bool, recipient_count: int) -> str:
    """Returnerar det exakta OK-kommandot som krävs för detta draft."""
    parts = ["OK", draft_id]
    if has_attachment:
        parts.append("B")
    if recipient_count > 3:
        parts.append("FM")
    return " ".join(parts)
