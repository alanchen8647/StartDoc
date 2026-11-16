#!/usr/bin/env python
"""Test retrieval for standard deduction query"""

from docubot import DocuBot

bot = DocuBot(docs_folder='knowledge_base')

query = "What's the standard deduction for Married Filing Joint family with no dependent?"
print('=' * 80)
print('QUERY:', query)
print('=' * 80)
print('')

results = bot.retrieve(query, top_k=3)

if results:
    print(f"Retrieved {len(results)} results:\n")
    for i, (filename, text, meta) in enumerate(results, 1):
        year = meta.get('year', 'N/A')
        print(f'[{i}] {filename} ({year})')
        print(f'    Preview: {text[:130]}...')
        print()
else:
    print("No results found (all below threshold)")

print("=" * 80)
