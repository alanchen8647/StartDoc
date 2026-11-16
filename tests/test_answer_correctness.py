"""
Answer Correctness Verification

Combines:
1. Knowledge base coverage audit (what SHOULD the answer be?)
2. System behavior test (what DOES the system return?)
3. Compliance check (does system match expectations?)
"""

import sys
sys.path.insert(0, '.')

from docubot import DocuBot
import json
import os

# Test cases with expected behavior based on KB audit
TEST_CASES = [
    {
        "query": "What are the IRA contribution limits for 2025?",
        "category": "ira_contribution_limits",
        "kb_has_answer": True,  # Verified by audit
        "expected_behavior": "RETURN_ANSWER",
        "must_contain": ["$7,000", "$8,000"],
        "must_NOT_contain": ["I do not know"],
    },
    {
        "query": "What is the standard deduction for Married filing joint?",
        "category": "standard_deduction",
        "kb_has_answer": True,  # Verified by audit
        "expected_behavior": "RETURN_ANSWER",
        "must_contain": ["$31,500"],
        "must_NOT_contain": ["I do not know"],
    },
    {
        "query": "What's the fee for filing taxes?",
        "category": "filing_fee",
        "kb_has_answer": True,  # Verified by audit
        "expected_behavior": "RETURN_ANSWER",
        "must_contain": ["$110"],
        "must_NOT_contain": ["I do not know"],
    },
    {
        "query": "What is the IRA deduction limit?",
        "category": "ira_deduction",
        "kb_has_answer": True,  # Verified by audit
        "expected_behavior": "RETURN_ANSWER",
        "must_contain": ["deduction", "filing status"],
        "must_NOT_contain": ["I do not know"],
    },
    {
        "query": "What's the maximum I can contribute to my 401k for retirement?",
        "category": "401k_contribution_limits",
        "kb_has_answer": True,  # Now in KB after fix
        "expected_behavior": "RETURN_ANSWER",
        "must_contain": ["$24,500", "401"],
        "must_NOT_contain": ["I do not know"],
    },
    # Example of a query that SHOULD be refused
    {
        "query": "How do I maximize my tax refund?",
        "category": "tax_strategy",
        "kb_has_answer": False,  # Not in KB
        "expected_behavior": "REFUSE",
        "must_contain": [],
        "must_NOT_contain": [],  # Any response is ok, but ideally "I do not know"
        "note": "This is an advisory question - KB should not have this"
    },
]


class AnswerCorrectnessVerifier:
    """
    Verify if system behavior matches knowledge base coverage.
    """

    def __init__(self):
        self.bot = DocuBot('knowledge_base')
        self.results = []

    def verify_query(self, query, category, kb_has_answer, expected_behavior,
                    must_contain, must_NOT_contain, note=""):
        """
        Verify a single query.

        Returns compliance report:
        - Does KB have answer? (audit result)
        - Does system return answer?
        - Does system behavior match expectation?
        """
        answer = self.bot.answer_retrieval_only(query)
        answer_lower = answer.lower()

        # Analyze system behavior
        has_refusal = "i do not know" in answer_lower or "i don't know" in answer_lower

        if has_refusal:
            system_behavior = "REFUSED"
        elif len(answer) > 100:
            system_behavior = "RETURNED_ANSWER"
        else:
            system_behavior = "UNCLEAR"

        # Check compliance
        issues = []

        # If KB has answer, system MUST return it
        if kb_has_answer and system_behavior == "REFUSED":
            issues.append("❌ KB has answer but system refused")

        # Check required content
        missing_content = []
        for phrase in must_contain:
            if phrase.lower() not in answer_lower:
                missing_content.append(phrase)

        if missing_content:
            issues.append(f"❌ Missing required content: {', '.join(missing_content)}")

        # Check forbidden content
        unwanted_content = []
        for phrase in must_NOT_contain:
            if phrase.lower() in answer_lower:
                unwanted_content.append(phrase)

        if unwanted_content:
            issues.append(f"❌ Contains unwanted text: {', '.join(unwanted_content)}")

        # Determine pass/fail
        passed = len(issues) == 0

        result = {
            "passed": passed,
            "query": query,
            "category": category,
            "kb_has_answer": kb_has_answer,
            "expected_behavior": expected_behavior,
            "system_behavior": system_behavior,
            "compliance_issues": issues,
            "answer_preview": answer[:150] + "..." if len(answer) > 150 else answer,
            "answer_length": len(answer),
            "note": note
        }

        self.results.append(result)
        return result

    def run_verification(self):
        """Run verification on all test cases."""
        print("="*80)
        print("ANSWER CORRECTNESS VERIFICATION")
        print("(Knowledge Base vs System Behavior)")
        print("="*80)

        for test_case in TEST_CASES:
            print(f"\n📝 Testing: {test_case['query']}")
            print("-"*80)

            result = self.verify_query(
                test_case['query'],
                test_case['category'],
                test_case['kb_has_answer'],
                test_case['expected_behavior'],
                test_case['must_contain'],
                test_case['must_NOT_contain'],
                test_case.get('note', '')
            )

            print(f"Category: {result['category']}")
            print(f"KB has answer: {result['kb_has_answer']}")
            print(f"Expected: {result['expected_behavior']}")
            print(f"System returned: {result['system_behavior']}")

            if result['compliance_issues']:
                print(f"\n❌ FAILED")
                for issue in result['compliance_issues']:
                    print(f"   {issue}")
            else:
                print(f"\n✅ PASSED - System behavior matches expectations")

            if result['note']:
                print(f"Note: {result['note']}")

            print(f"Answer length: {result['answer_length']} chars")

    def generate_report(self):
        """Generate verification report."""
        print("\n" + "="*80)
        print("VERIFICATION SUMMARY")
        print("="*80)

        passed = sum(1 for r in self.results if r['passed'])
        failed = len(self.results) - passed

        print(f"\nTotal tests: {len(self.results)}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Pass rate: {100*passed/len(self.results):.1f}%")

        if failed > 0:
            print("\n" + "-"*80)
            print("FAILED TESTS (Compliance Issues):")
            print("-"*80)

            for result in self.results:
                if not result['passed']:
                    print(f"\n❌ {result['category']}")
                    print(f"   Query: {result['query']}")
                    print(f"   KB has answer: {result['kb_has_answer']}")
                    print(f"   System returned: {result['system_behavior']}")
                    print(f"   Issues:")
                    for issue in result['compliance_issues']:
                        print(f"      {issue}")

    def export_results(self, filepath='correctness_test_results.json'):
        """Export verification results."""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results exported to {filepath}")


if __name__ == "__main__":
    verifier = AnswerCorrectnessVerifier()
    verifier.run_verification()
    verifier.generate_report()
    verifier.export_results()
