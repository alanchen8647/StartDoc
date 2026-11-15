"""Test guardrail functions."""

from guardrail import check_input_safety, detect_ssn, detect_ein, detect_real_name, get_safe_response

print("=" * 70)
print("TESTING GUARDRAIL FUNCTIONS")
print("=" * 70)

# Test 1: SSN Detection
print("\n[Test 1] SSN Detection:")
test_cases_ssn = [
    ("Client 123-45-6789 has two W-2s", True),
    ("What is the standard deduction?", False),
    ("My SSN is 999-99-9999", True),
]
for text, expected in test_cases_ssn:
    result = detect_ssn(text)
    status = "✅" if result == expected else "❌"
    print(f"  {status} '{text[:40]}...' → {result} (expected {expected})")

# Test 2: EIN Detection
print("\n[Test 2] EIN Detection:")
test_cases_ein = [
    ("My client's EIN is 12-3456789", True),
    ("What is the base fee?", False),
    ("EIN: 45-6789123", True),
]
for text, expected in test_cases_ein:
    result = detect_ein(text)
    status = "✅" if result == expected else "❌"
    print(f"  {status} '{text[:40]}...' → {result} (expected {expected})")

# Test 3: Name Detection
print("\n[Test 3] Name Detection:")
test_cases_name = [
    ("Maria Gonzalez wants to claim her nephew", True),
    ("A client with 2 W-2s and a child", False),
    ("John's client has a Schedule C", True),
]
for text, expected in test_cases_name:
    has_name, name_found = detect_real_name(text)
    status = "✅" if has_name == expected else "❌"
    print(f"  {status} '{text[:40]}...' → {has_name} (found: {name_found if name_found else 'none'})")

# Test 4: Full Guardrail Check
print("\n[Test 4] Full Guardrail Check:")
test_cases_full = [
    ("Client 123-45-6789 has two W-2s, what do I charge?", False, "SSN detected"),
    ("My client's EIN is 12-3456789, how do I enter it?", False, "EIN detected"),
    ("Maria Gonzalez wants to claim her nephew, what do I do?", False, "Real name detected"),
    ("A client with 2 W-2s and a child wants to know how to pay.", True, "OK"),
    ("What's the base fee for a single client?", True, "OK"),
]
for text, expected_safe, expected_reason in test_cases_full:
    is_safe, reason = check_input_safety(text)
    safe_ok = "✅" if is_safe == expected_safe else "❌"
    reason_ok = "✅" if expected_reason in reason else "❌"

    print(f"  {safe_ok} {reason_ok} '{text[:45]}...'")
    print(f"       → safe={is_safe}, reason={reason}")

    # Show user-friendly response
    if not is_safe:
        response = get_safe_response(reason)
        print(f"       → User sees: {response[:60]}...")

print("\n" + "=" * 70)
print("GUARDRAIL TESTS COMPLETE")
print("=" * 70)
