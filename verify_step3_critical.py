"""
Quick verification: Test only the 4 critical problem cases (T31-T34).

These were false positives in Step 2 that the improved LLM prompt should catch.
"""

from dotenv import load_dotenv
load_dotenv()

from docubot import DocuBot
from llm_client import GeminiClient

# The 4 problem cases that should now be correctly refused by LLM
critical_tests = [
    ("T31", "How do I depreciate office furniture for a business client?",
     "Documents mention furniture but NOT depreciation methods"),
    ("T32", "What's the 22% tax bracket for 2025?",
     "Documents mention '#22' rules but NOT '22%' tax brackets"),
    ("T33", "Client makes $60k, married, two kids, what's the estimated refund?",
     "Documents mention 'estimated tax' but NOT refund estimates"),
    ("T34", "What is the fee for company formation?",
     "Documents mention 'company formation' but NO fee is listed"),
]

print("=" * 80)
print("STEP 3 VERIFICATION - Critical Problem Cases (T31-T34)")
print("=" * 80)
print("Testing whether LLM now correctly refuses false positives\n")

try:
    llm_client = GeminiClient()
    bot = DocuBot(docs_folder="docs_pt", llm_client=llm_client)
    has_llm = True
except RuntimeError as e:
    print(f"Cannot initialize LLM: {e}")
    print("Falling back to retrieval only (less strict)\n")
    bot = DocuBot(docs_folder="docs_pt")
    has_llm = False

for test_id, query, reason in critical_tests:
    print(f"\n{test_id}: {query}")
    print(f"Reason should refuse: {reason}")
    print("-" * 80)

    if has_llm:
        # Use RAG mode (with LLM filtering)
        answer = bot.answer_rag(query)
    else:
        # Use retrieval only
        answer = bot.answer_retrieval_only(query)

    # Check if refused
    is_refused = ("I do not know" in answer or
                 "not covered" in answer.lower() or
                 "ask your supervisor" in answer.lower() or
                 "unavailable" in answer.lower())

    if is_refused:
        print("✓ CORRECTLY REFUSED")
        print(f"  Response: {answer[:80]}")
    else:
        print("✗ INCORRECTLY RETURNED (still a problem)")
        print(f"  Response: {answer[:120]}")
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
if has_llm:
    print("Using RAG mode (with LLM) - LLM prompt engineering should filter false positives")
else:
    print("Using retrieval only - LLM filtering not available")
print("\nIf all 4 show ✓, then Step 3 improvements are working!")
