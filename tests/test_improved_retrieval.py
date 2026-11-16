#!/usr/bin/env python
"""Test improved retrieval with normalization and expanded synonyms"""

from docubot import DocuBot

bot = DocuBot(docs_folder='knowledge_base')

# Test various formulations of the same question
queries = [
    "What's the standard deduction for Married Filing Joint family with no dependent?",
    "standard deduction married filing joint",
    "How much is the standard deduction for a married couple filing jointly?",
    "standard deduction 2025 married",
    "What deduction do married people filing jointly get?",
]

print("=" * 80)
print("TESTING IMPROVED RETRIEVAL WITH QUERY NORMALIZATION")
print("=" * 80)

for i, query in enumerate(queries, 1):
    print(f"\n[{i}] Query: {query}")
    results = bot.retrieve(query, top_k=1)

    if results:
        filename, text, meta = results[0]
        year = meta.get('year', 'N/A')
        is_correct = 'standard_deduction' in filename.lower()
        status = "✓ CORRECT" if is_correct else "✗ WRONG"
        print(f"    Result: {status}")
        print(f"    File: {filename} ({year})")
        print(f"    Preview: {text[:100]}...")
    else:
        print(f"    Result: ✗ NO RESULTS")

print("\n" + "=" * 80)
