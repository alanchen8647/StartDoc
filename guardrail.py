"""
Input guardrail: blocks sensitive data (SSN, EIN, real names)
before the query reaches the LLM or retrieval system.

This is a SAFETY-FIRST layer - we refuse early rather than
hoping the LLM or retrieval won't leak the data.
"""

import re
from typing import Tuple

# Common first names (curated list for PT staff context)
# Real names in business questions are rare; we prioritize recall (catch real names)
# over precision (avoid false positives like "Bill" for bill payment)
COMMON_NAMES = {
    # Female names
    'maria', 'jane', 'sarah', 'mary', 'jennifer', 'lisa', 'barbara', 'susan',
    'jessica', 'stephanie', 'melissa', 'patricia', 'linda', 'nancy', 'karen',
    'betty', 'margaret', 'sandra', 'ashley', 'dorothy', 'kimberly', 'emily',
    'donna', 'michelle', 'carol', 'amanda', 'melissa', 'deborah', 'amy', 'anna',
    # Male names
    'john', 'james', 'robert', 'michael', 'william', 'david', 'richard', 'joseph',
    'thomas', 'charles', 'christopher', 'daniel', 'matthew', 'anthony', 'mark',
    'donald', 'steven', 'paul', 'andrew', 'joshua', 'kenneth', 'george', 'brian',
    'edward', 'ronald', 'anthony', 'frank', 'ryan', 'gary', 'nicholas', 'eric',
}


def detect_ssn(text: str) -> bool:
    """
    Detect Social Security Number pattern: XXX-XX-XXXX

    Examples that match:
    - "123-45-6789"
    - "Client 999-99-9999 has..."

    Why this pattern?
    SSN format is strictly 3-2-4 digits with hyphens.
    This is unambiguous - no legitimate accounting term matches this.
    """
    # Pattern: word boundary + 3 digits + dash + 2 digits + dash + 4 digits + word boundary
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    return bool(re.search(ssn_pattern, text))


def detect_ein(text: str) -> bool:
    """
    Detect Employer Identification Number: XX-XXXXXXX

    Examples that match:
    - "12-3456789"
    - "EIN is 45-6789123"

    Why this pattern?
    EIN is strictly 2-7 digits. More rare in docs, but should be blocked.
    """
    ein_pattern = r'\b\d{2}-\d{7}\b'
    return bool(re.search(ein_pattern, text))


def detect_real_name(text: str) -> Tuple[bool, str]:
    """
    Detect likely real names in the question.

    Strategy:
    1. Find capitalized words (Name Pattern)
    2. Check if they're in COMMON_NAMES list
    3. Verify context (avoid false positives)

    Examples that match:
    - "Maria Gonzalez wants to claim her nephew"
    - "John's client has..."

    Why this approach?
    Real names in accounting questions are rare. When they appear:
    - They're usually capitalized (Proper nouns)
    - They're in specific contexts ("X wants...", "X's client", "For X,")
    - They appear in COMMON_NAMES list

    False positive risk: "Bill" (name) vs "bill payment" (lowercase)
    Mitigation: We only flag CAPITALIZED words in COMMON_NAMES
    """
    # Find all capitalized words (likely proper nouns)
    words = text.split()

    for i, word in enumerate(words):
        # Skip if not capitalized
        if not word or not word[0].isupper():
            continue

        # Remove punctuation and convert to lowercase for lookup
        clean_word = word.strip('.,!?;:\'"').lower()

        # Check if this word is in our common names database
        if clean_word in COMMON_NAMES:
            # If we found a name in COMMON_NAMES and it's capitalized,
            # it's likely a real name - flag it
            # (Simpler approach: capitalized common name = real name)
            # Avoid false positives by also checking that it's not at start of sentence
            # followed by common words like "a", "the", etc.

            # Look at word after this one
            next_word = words[i + 1].lower() if i + 1 < len(words) else ""

            # If followed by another capitalized word (likely last name) or
            # by action verbs (wants, has, with), it's a name
            is_likely_name = (
                (i + 1 < len(words) and words[i + 1] and words[i + 1][0].isupper()) or  # Followed by capital
                next_word in ['wants', 'has', 'with', 'will', 'does', 'is'] or  # Action verbs
                "'" in word  # Possessive form
            )

            if is_likely_name:
                return True, word

    return False, ""


def check_input_safety(question: str) -> Tuple[bool, str]:
    """
    Main guardrail function.

    Returns:
        (is_safe, reason_if_blocked)
    """
    # Check 1: SSN
    if detect_ssn(question):
        return False, "SSN detected"

    # Check 2: EIN
    if detect_ein(question):
        return False, "EIN detected"

    # Check 3: Real name
    has_name, name_found = detect_real_name(question)
    if has_name:
        return False, f"Real name detected ({name_found})"

    # All checks passed
    return True, "OK"


def get_safe_response(reason: str) -> str:
    """
    User-friendly error messages for blocked inputs.
    """
    messages = {
        "SSN detected": (
            "⚠️ Please do not share client SSNs. "
            "Describe the client generally (e.g., 'A single client with...')"
        ),
        "EIN detected": (
            "⚠️ Please do not share client EINs. "
            "Refer to clients by type instead (e.g., 'A business client with...')"
        ),
        "Real name detected": (
            "⚠️ Real names detected. "
            "Please describe clients generally instead (e.g., 'A married client with 2 kids')"
        ),
    }

    for key, msg in messages.items():
        if key in reason:
            return msg

    return "⚠️ Invalid input. Please try again."


# ============================================================
# Logging (for Step 4)
# ============================================================

def log_guardrail_block(question: str, reason: str) -> None:
    """
    Log blocked inputs for review and monitoring.

    Future: Write to file or database for staff review.
    Question is NOT stored (privacy-first), only the reason.
    """
    # For now, just print
    # Later (Step 4): write to guardrail_blocks.log
    print(f"[GUARDRAIL BLOCK] Reason: {reason}")
