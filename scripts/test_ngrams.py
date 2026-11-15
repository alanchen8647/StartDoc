"""Test n-gram extraction and phrase matching."""

from docubot import extract_ngrams, has_negation

# Test 1: N-gram extraction
print("=" * 70)
print("TEST 1: N-gram Extraction")
print("=" * 70)

test_query = "estimated refund amount"
print(f"\nQuery: '{test_query}'")

bigrams = extract_ngrams(test_query, n=2)
print(f"2-grams: {bigrams}")

trigrams = extract_ngrams(test_query, n=3)
print(f"3-grams: {trigrams}")

# Test 2: Phrase matching in text
print("\n" + "=" * 70)
print("TEST 2: Phrase Matching")
print("=" * 70)

test_cases = [
    ("gift of $20000", "The estimated refund of $20,000 is owed to the client"),
    ("22% tax bracket", "### Tax & Software #22 - do this first"),
    ("company formation fee", "Services include company formation. Fees are listed above."),
]

for phrase, text in test_cases:
    print(f"\nPhrase: '{phrase}'")
    print(f"Text: '{text[:50]}...'")

    bigrams = extract_ngrams(phrase, n=2)
    trigrams = extract_ngrams(phrase, n=3)

    text_lower = text.lower()

    print(f"  2-grams in text: ", end="")
    found_bigrams = [b for b in bigrams if b in text_lower]
    print(found_bigrams if found_bigrams else "NONE")

    print(f"  3-grams in text: ", end="")
    found_trigrams = [t for t in trigrams if t in text_lower]
    print(found_trigrams if found_trigrams else "NONE")

# Test 3: Negation detection
print("\n" + "=" * 70)
print("TEST 3: Negation Detection")
print("=" * 70)

negation_tests = [
    "How do I depreciate office furniture?",
    "What's the 22% tax bracket?",
    "Single client without proof of income",
]

for query in negation_tests:
    has_neg = has_negation(query)
    print(f"Query: '{query}'")
    print(f"  Has negation: {has_neg}\n")
