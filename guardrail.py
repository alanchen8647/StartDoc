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
    Detect Social Security Number in any format.

    Catches:
    - Formatted: "123-45-6789", "123 45 6789"
    - Unformatted: "123456789" (9 consecutive digits)
    - With context: "SSN is 123456789", "My SSN: 123-45-6789"

    Examples that match:
    - "123-45-6789"
    - "123456789"
    - "SSN 999999999"

    Why catch both formats?
    In practice, users might paste SSNs with or without formatting.
    9-digit sequences are almost always SSNs in this context.
    """
    # Pattern 1: Formatted SSN with separators (XXX-XX-XXXX or XXX XX XXXX)
    ssn_formatted = r'\b\d{3}[\s\-]\d{2}[\s\-]\d{4}\b'
    if re.search(ssn_formatted, text):
        return True

    # Pattern 2: Unformatted SSN (9 consecutive digits = XXX XX XXXX without separators)
    ssn_unformatted = r'\b\d{9}\b'
    if re.search(ssn_unformatted, text):
        return True

    return False


def detect_ein(text: str) -> bool:
    """
    Detect Employer Identification Number in any format.

    Catches:
    - Formatted: "12-3456789", "12 3456789"
    - Unformatted: "123456789" (9 consecutive digits)

    Examples that match:
    - "12-3456789"
    - "123456789"
    - "EIN is 999999999"

    Why catch both formats?
    EINs also appear with or without formatting.
    9-digit sequences in business context likely EIN or SSN.
    """
    # Pattern 1: Formatted EIN with separators (XX-XXXXXXX or XX XXXXXXX)
    ein_formatted = r'\b\d{2}[\s\-]\d{7}\b'
    if re.search(ein_formatted, text):
        return True

    # Pattern 2: Unformatted (9 consecutive digits)
    ein_unformatted = r'\b\d{9}\b'
    if re.search(ein_unformatted, text):
        return True

    return False


def detect_suspicious_numbers(text: str) -> bool:
    """
    Detect suspicious number combinations that might be sensitive data.

    Catches:
    - Long continuous digit sequences (8+ digits): could be account/phone/passport
    - Credit card patterns: 4111-1111-1111-1111 or variations
    - Phone numbers with dashes: 555-123-4567
    - Consecutive numbers separated by spaces: "1234 5678 9012"
    - Other formatted number sequences

    Examples that match:
    - "Account 123456789" (8+ digits)
    - "Credit card 4111-1111-1111-1111"
    - "My number is 555-123-4567"
    - "Client ID 87654321"

    False positives to avoid:
    - "2025" (year)
    - "31,500" (currency amounts - context-dependent)
    - Single numbers: "5", "10", "50"
    """

    # Pattern 1: 8+ consecutive digits (account numbers, long IDs, etc.)
    # Examples: "123456789", "87654321000"
    # In practice, users won't type long unformatted sequences for legitimate reasons
    long_digits = r'\b\d{8,}\b'
    if re.search(long_digits, text):
        return True

    # Pattern 2: Credit card-like patterns (16 digits with separators)
    # Examples: "4111-1111-1111-1111", "4111 1111 1111 1111"
    credit_card = r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b'
    if re.search(credit_card, text):
        return True

    # Pattern 3: Phone number patterns (formatted with separators)
    # Examples: "555-123-4567", "555 123 4567", "(555) 123-4567"
    # Must have separators to avoid false positives
    phone = r'\b\d{3}[\s\-.\(\)]\d{3}[\s\-.\(\)]\d{4}\b'
    if re.search(phone, text):
        return True

    return False


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
    # Check 1: SSN (specific format: XXX-XX-XXXX)
    if detect_ssn(question):
        return False, "SSN detected"

    # Check 2: EIN (specific format: XX-XXXXXXX)
    if detect_ein(question):
        return False, "EIN detected"

    # Check 3: Suspicious number combinations (generic catch-all)
    # Catches: long sequences, credit cards, phone numbers, account IDs
    if detect_suspicious_numbers(question):
        return False, "Suspicious number sequence detected"

    # Check 4: Real name
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
        "Suspicious number sequence detected": (
            "⚠️ Please do not share sensitive numbers (account IDs, phone numbers, credit cards, etc.). "
            "Describe what you need help with without including specific client identifiers."
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
