"""Quick test of stemming and synonym functionality."""

from docubot import DocuBot

bot = DocuBot(docs_folder="knowledge_base")
print(f"Loaded {len(bot.chunks)} chunks from {len(bot.documents)} documents\n")

# Test 1: Plural/singular matching (discounts vs discount)
test_queries = [
    ("standard deduction", "Should find IRS standard deduction doc"),
    ("standard deductions", "Plural version should also work"),
    ("fee charge", "Fee and charge should match"),
    ("what is the discount", "Discount should match"),
    ("depreciate furniture", "Should NOT find anything (not covered)"),
    ("minimum fee $200K", "Should find minimum fee letter"),
]

for query, description in test_queries:
    results = bot.retrieve(query, top_k=2)
    print(f"Query: '{query}'")
    print(f"  ({description})")
    if results:
        for i, item in enumerate(results, 1):
            if len(item) == 3:
                filename, text, meta = item
                year = meta.get("year", "")
            else:
                filename, text = item
                year = ""
            preview = text[:80].replace("\n", " ")
            year_str = f" ({year})" if year else ""
            print(f"  {i}. [{filename}{year_str}] {preview}...")
    else:
        print(f"  [REFUSED - below threshold]")
    print()
