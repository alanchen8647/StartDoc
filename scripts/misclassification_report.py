"""
Detailed analysis of the 4 misclassified queries (should refuse but return).
Shows: query, retrieved chunk, scores, and why it was incorrectly matched.
"""

from docubot import DocuBot, STOPWORDS, stem_word, expand_with_synonyms
import math
import string

bot = DocuBot(docs_folder="knowledge_base")

# The 4 problem cases
problem_queries = [
    ("T31", "How do I depreciate office furniture for a business client?",
     "不在文档中（监管），应该拒绝"),
    ("T32", "What's the 22% tax bracket for 2025?",
     "不在文档中（可能2026），应该拒绝"),
    ("T33", "Client makes $60k, married, two kids, what's the estimated refund?",
     "没有退税估算器，应该拒绝"),
    ("T34", "What is the fee for company formation?",
     "公司成立没有价格，应该拒绝"),
]

print("=" * 80)
print("MISCLASSIFICATION ANALYSIS - 4 PROBLEM QUERIES")
print("=" * 80)

for test_id, query, reason in problem_queries:
    print(f"\n{test_id}: {query[:60]}...")
    print(f"    Reason should refuse: {reason}")
    print("-" * 80)

    # Get retrieval result
    results = bot.retrieve(query, top_k=3)

    if not results:
        print("    ✓ CORRECTLY REFUSED (score < 3.0)")
        continue

    # Show top result
    filename, text, meta = results[0]
    year = meta.get("year", "")

    print(f"    ✗ INCORRECTLY RETURNED")
    print(f"    Retrieved: [{filename} ({year})]")
    print(f"    Text: {text[:100]}...")

    # Detailed score breakdown
    print(f"\n    SCORE BREAKDOWN:")

    # Manual score calculation to show components
    query_words = {w.strip(string.punctuation) for w in query.lower().split()}
    query_words -= STOPWORDS
    query_words.discard("")

    query_stems = set()
    for word in query_words:
        query_stems.add(stem_word(word))
        for syn in expand_with_synonyms(word):
            query_stems.add(stem_word(syn))

    print(f"      Query stems: {list(query_stems)[:5]}{'...' if len(query_stems) > 5 else ''}")

    # Score from this specific chunk
    score = bot.score_document(query, text, "")
    print(f"      Score: {score:.2f} (threshold: 3.0)")

    # Which words matched
    text_lower = text.lower()
    matched_words = []
    for stem in query_stems:
        # Simple check - not exact stemming reproduction but illustrative
        if stem in text_lower or any(stem in word for word in text_lower.split()):
            matched_words.append(stem)

    if matched_words:
        print(f"      Matched stems: {matched_words[:8]}")

    # Problem analysis
    print(f"\n    WHY IT MATCHED:")

    if test_id == "T31":
        print("      • Query word 'business' or 'office' + 'furniture' in docs")
        print("      • Document mentions furniture but NOT depreciation methods")
        print("      • Needs semantic understanding that 'furniture' without")
        print("        'depreciation' method isn't an answer")

    elif test_id == "T32":
        print("      • Query has '#22' (rare number) → high IDF weight")
        print("      • Document title: '### Tax & Software #22'")
        print("      • Words '22' and 'tax' both match, giving 8.80 score")
        print("      • But '22%' (percentage) ≠ '#22' (rule number)")
        print("      • Needs format-aware matching or semantic understanding")

    elif test_id == "T33":
        print("      • Query words: 'client', 'estimated', 'married', 'kids'")
        print("      • Document has sections on 'estimated tax' but NOT refund")
        print("      • 'Estimated' word match overcomes semantic mismatch")
        print("      • Needs phrase-level understanding of 'estimated refund'")

    elif test_id == "T34":
        print("      • Query: 'company formation fee'")
        print("      • Document lists 'company formation' as a service")
        print("      • Document has 'fee' tables, but NO fee for formation")
        print("      • System finds 'company' + 'formation' + 'fee' separately")
        print("      • Needs to know 'formation' has NO price listed")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Step 2 Results: 36/39 (92.3%) accuracy

Correct Refuse (4): T31-T37 via guardrails
False Positives (4):
  - T31: "depreciate" query hits furniture mention
  - T32: "#22" rare token override context mismatch
  - T33: "estimated" word match overrides semantic gap
  - T34: Service exists but price doesn't (multi-word false match)
  - T39: "supervisor" mention returns despite prompt injection

Key Pattern: Single word matches dominate despite phrase-level mismatch.
           Need semantic/phrase-level understanding for refinement.

Next: Step 3 (Prompt Engineering + Logging)
      Can address via better LLM prompting ("only answer if found in these chunks")
      Don't need more retrieval improvements for MVP.
""")
