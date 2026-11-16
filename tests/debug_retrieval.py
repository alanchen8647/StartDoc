#!/usr/bin/env python
"""Debug why standard deduction query is not matching correctly"""

from docubot import DocuBot
import os

bot = DocuBot(docs_folder='knowledge_base')

# Try different query formulations
queries = [
    "What's the standard deduction for Married Filing Joint?",
    "standard deduction 2025 married",
    "2025 standard deduction",
    "Standard deduction amounts",
    "deduction married filing jointly",
]

print("=" * 80)
print("TESTING DIFFERENT QUERY FORMULATIONS")
print("=" * 80)

for query in queries:
    print(f"\nQuery: {query}")
    results = bot.retrieve(query, top_k=1)
    if results:
        filename, text, meta = results[0]
        print(f"  → {filename} ({meta.get('year', 'N/A')})")
        print(f"  Preview: {text[:80]}...")
    else:
        print(f"  → No results")

print("\n" + "=" * 80)
print("CHECKING DOCUMENT CONTENTS")
print("=" * 80)

# Check what's in the standard deduction file
std_ded_file = 'knowledge_base/irs_standard_deduction_2025.md'
if os.path.exists(std_ded_file):
    with open(std_ded_file, 'r') as f:
        content = f.read()
    print(f"\n{std_ded_file}:")
    print(f"  - Length: {len(content)} chars")
    print(f"  - Contains 'standard deduction': {'Yes' if 'standard deduction' in content.lower() else 'No'}")
    print(f"  - Contains 'married': {'Yes' if 'married' in content.lower() else 'No'}")
    print(f"  - Contains '$31,500': {'Yes' if '$31,500' in content else 'No'}")
    print(f"\n  First 200 chars: {content[:200]}")

print("\n" + "=" * 80)
