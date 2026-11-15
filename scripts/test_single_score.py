"""Test scoring for specific queries."""

from docubot import DocuBot

bot = DocuBot(docs_folder="knowledge_base")

# Test a few key queries
test_queries = [
    ("T01", "standard deduction", "Should HIT high"),
    ("T25", "gift 20000", "Should HIT medium"),
    ("T27", "don't know", "Should HIT low"),
    ("T32", "22% tax bracket", "Should REFUSE"),
]

print("=" * 70)
print("SCORE BREAKDOWN FOR KEY QUERIES")
print("=" * 70)

for test_id, query, expected in test_queries:
    print(f"\n{test_id}: '{query}'")
    print(f"Expected: {expected}")

    results = bot.retrieve(query, top_k=1)

    if results:
        filename, text, meta = results[0]
        year = meta.get("year", "")
        print(f"Result: RETURNED")
        print(f"  File: {filename} ({year})")
        print(f"  Text: {text[:60]}...")
    else:
        print(f"Result: REFUSED (score < 4.0)")

print("\n" + "=" * 70)
print("Note: Need to debug why T27 score dropped from 9.23 to 1.23")
print("=" * 70)
