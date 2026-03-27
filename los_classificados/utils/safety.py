"""Anonymity and safety utilities: email/phone masking and content moderation."""
from __future__ import annotations

import re


# ── Email masking ──────────────────────────────────────────────────────────────

def mask_email(email: str) -> str:
    """
    Mask an email address for safe public display.

    'username@example.com' → 'u***e@example.com'
    'ab@example.com'       → 'a***@example.com'
    """
    if not email or "@" not in email:
        return "***@***.***"
    local, domain = email.rsplit("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "***"
    else:
        masked_local = local[0] + "***" + local[-1]
    return f"{masked_local}@{domain}"


# ── Phone masking ──────────────────────────────────────────────────────────────

def mask_phone(phone: str) -> str:
    """
    Mask a phone number for safe public display, revealing only the last 4 digits.

    '+13055550101' → '***-***-0101'
    """
    if not phone:
        return "***-***-****"
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return "***-****"
    return f"***-***-{digits[-4:]}"


# ── Content moderation ────────────────────────────────────────────────────────

# Terms strongly associated with classified-ad scams and policy violations.
PROHIBITED_TERMS: list[str] = [
    "western union",
    "moneygram",
    "wire transfer",
    "gift card payment",
    "pay with gift card",
    "advance fee",
    "send money first",
    "payment in advance",
    "cashier's check",
    "nigerian prince",
    "100% guaranteed profit",
    "replica watch",
    "fake designer",
    "counterfeit",
    "no background check required",
    "untraceable payment",
    "dark web",
    "darkweb",
]

CONTENT_GUIDELINES: dict[str, list[str]] = {
    "allowed": [
        "Genuine items, services, and real estate you own or represent",
        "Accurate descriptions — photos must match the item listed",
        "Legal goods and services only",
        "Honest pricing — no bait-and-switch tactics",
        "One listing per item — no duplicate or cross-posted ads",
    ],
    "prohibited": [
        "Fraudulent payment requests (wire transfers, gift cards, advance fees)",
        "Counterfeit, stolen, or otherwise prohibited goods",
        "Adult or sexually explicit content of any kind",
        "Personal data harvesting, phishing links, or external redirects",
        "Spam, mass re-posts, or content unrelated to the category",
        "Weapons, controlled substances, or regulated items without licensing",
    ],
}


def check_content_violations(title: str, description: str) -> list[str]:
    """
    Scan title and description for prohibited terms.

    Returns a list of human-readable violation messages; an empty list means clean.
    """
    combined = f"{title or ''} {description or ''}".lower()
    return [
        f'Prohibited term detected: "{term}". Please review our content guidelines.'
        for term in PROHIBITED_TERMS
        if term in combined
    ]
