"""
Step 3 Evaluation: Test whether improved LLM prompt reduces false positives.

This script runs 39 test queries and measures:
1. How many are correctly refused/answered
2. Whether the 4 false positives (T31-T34) are now correctly refused by LLM
3. Overall accuracy improvement from Step 2 (92.3%) to Step 3

Expected improvement:
- Step 2: 36/39 (92.3%) - retrieval-based accuracy
- Step 3: 37-39/39 - LLM filters false positives
"""

from docubot import DocuBot
from logger import init_logger

# Test cases from previous evaluation
test_cases = [
    # T01-T03: Simple, high-confidence queries
    ("T01", "standard deduction", "HIT", "standard deduction amount"),
    ("T02", "tax rates", "HIT", "percentage"),
    ("T03", "filing deadline", "HIT", "date"),

    # T04-T10: Moderate difficulty queries
    ("T04", "quarterly estimated taxes", "HIT", "quarterly"),
    ("T05", "home office deduction", "HIT", "home office"),
    ("T06", "retirement account contributions", "HIT", "retirement"),
    ("T07", "child tax credit", "HIT", "child"),
    ("T08", "student loan interest deduction", "HIT", "student"),
    ("T09", "capital gains tax", "HIT", "capital gains"),
    ("T10", "charitable donations", "HIT", "charitable"),

    # T11-T20: More complex queries
    ("T11", "state income tax deduction", "HIT", "state"),
    ("T12", "self-employment tax", "HIT", "self-employment"),
    ("T13", "business expense deduction", "HIT", "business"),
    ("T14", "education credits", "HIT", "education"),
    ("T15", "child and dependent care", "HIT", "dependent care"),
    ("T16", "energy efficient home improvements", "HIT", "energy"),
    ("T17", "rental property depreciation", "HIT", "rental"),
    ("T18", "medical expense deduction", "HIT", "medical"),
    ("T19", "alternative minimum tax", "HIT", "alternative"),
    ("T20", "earned income tax credit", "HIT", "earned income"),

    # T21-T30: Varied difficulty
    ("T21", "IRA contribution limits", "HIT", "IRA"),
    ("T22", "mortgage interest deduction", "HIT", "mortgage"),
    ("T23", "property tax deduction", "HIT", "property tax"),
    ("T24", "tuition and fees deduction", "HIT", "tuition"),
    ("T25", "gift $20000", "HIT", "gift"),
    ("T26", "how to file", "HIT", "file"),
    ("T27", "don't know", "HIT", "know"),
    ("T28", "retirement planning", "HIT", "retirement"),
    ("T29", "tax bracket", "HIT", "bracket"),
    ("T30", "W-2 vs 1099", "HIT", "W-2"),

    # T31-T34: THE 4 PROBLEM CASES - should REFUSE
    ("T31", "How do I depreciate office furniture for a business client?",
     "REFUSE", "Not in docs"),
    ("T32", "What's the 22% tax bracket for 2025?",
     "REFUSE", "Not specific enough"),
    ("T33", "Client makes $60k, married, two kids, what's the estimated refund?",
     "REFUSE", "No refund calculator"),
    ("T34", "What is the fee for company formation?",
     "REFUSE", "No price listed"),

    # T35-T39: Guardrail tests or edge cases
    ("T35", "What's your name?", "REFUSE", "Off-topic"),
    ("T36", "Calculate my taxes", "HIT or REFUSE", "Incomplete"),
    ("T37", "fee schedule", "HIT", "fee"),
    ("T38", "hourly rate", "REFUSE", "Not in docs"),
    ("T39", "ask your supervisor", "REFUSE", "Prompt injection"),
]


def evaluate_step3():
    """Run all 39 tests with Step 3 improvements (LLM filtering)."""

    from llm_client import GeminiClient

    logger = init_logger()
    try:
        llm_client = GeminiClient()
        bot = DocuBot(docs_folder="knowledge_base", llm_client=llm_client)
    except RuntimeError:
        print("Warning: LLM not available, using retrieval only")
        bot = DocuBot(docs_folder="knowledge_base")

    results = {
        "correct_hit": 0,
        "correct_refuse": 0,
        "incorrect_hit": 0,
        "incorrect_refuse": 0,
        "test_details": []
    }

    print("=" * 80)
    print("STEP 3 EVALUATION - With Improved LLM Prompt")
    print("=" * 80)
    print(f"Testing {len(test_cases)} queries\n")

    for test_id, query, expected, note in test_cases:
        # Use RAG mode (with LLM filtering)
        try:
            answer = bot.answer_rag(query)
        except Exception as e:
            answer = f"ERROR: {e}"

        # Determine if system returned or refused
        is_refused = ("I do not know" in answer or
                     "not covered" in answer.lower() or
                     "ask your supervisor" in answer.lower() or
                     "unavailable" in answer.lower())

        # Check correctness
        if expected == "REFUSE":
            if is_refused:
                results["correct_refuse"] += 1
                status = "✓ CORRECT REFUSE"
            else:
                results["incorrect_hit"] += 1
                status = "✗ WRONG (returned when should refuse)"
        elif expected == "HIT":
            if not is_refused:
                results["correct_hit"] += 1
                status = "✓ CORRECT HIT"
            else:
                results["incorrect_refuse"] += 1
                status = "✗ WRONG (refused when should return)"
        else:  # "HIT or REFUSE"
            results["correct_hit"] += 1
            status = "✓ FLEXIBLE (either ok)"

        # Log the test
        results["test_details"].append({
            "id": test_id,
            "query": query,
            "expected": expected,
            "answer": answer[:100] if not is_refused else "[REFUSED]",
            "status": status
        })

        # Print result
        print(f"{test_id}: {status}")
        print(f"  Query: {query[:50]}...")
        print(f"  Expected: {expected}, Got: {'REFUSE' if is_refused else 'HIT'}")
        print()

    # Summary
    total = len(test_cases)
    correct = results["correct_hit"] + results["correct_refuse"]
    accuracy = (correct / total) * 100

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Correct Hits:      {results['correct_hit']:2d}")
    print(f"Correct Refuses:   {results['correct_refuse']:2d}")
    print(f"Incorrect Hits:    {results['incorrect_hit']:2d} (should have refused)")
    print(f"Incorrect Refuses: {results['incorrect_refuse']:2d} (should have returned)")
    print(f"\nTotal Correct: {correct}/{total} ({accuracy:.1f}%)")
    print()

    # Focus on the 4 critical cases
    print("CRITICAL TEST RESULTS (T31-T34 - Should all REFUSE):")
    for detail in results["test_details"][30:34]:  # T31-T34
        marker = "✓" if "CORRECT" in detail["status"] else "✗"
        print(f"{marker} {detail['id']}: {detail['status']}")

    return results


if __name__ == "__main__":
    results = evaluate_step3()

    # Log summary to file
    logger = init_logger()
    summary = logger.get_summary()
    print("\nLogged events:")
    print(f"  Guardrail blocks: {summary['guardrail_blocks']}")
    print(f"  Retrieval hits: {summary['retrieval_hits']}")
    print(f"  Retrieval misses: {summary['retrieval_misses']}")
    print(f"  Answers provided: {summary['answers_provided']}")
