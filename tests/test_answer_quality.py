"""
Answer Quality Verification System

Automatically detects:
1. Partial matches (answer is related but not exactly what was asked)
2. Missing key information
3. Refusal vs legitimate "not covered"
4. Answer relevance vs query specificity
"""

import sys
sys.path.insert(0, '.')

from docubot import DocuBot
import json

# Define test cases: (query, expected_keywords, should_have, should_NOT_have)
QUALITY_TEST_CASES = [
    {
        "query": "What are the IRA contribution limits for 2025?",
        "expected_keywords": ["contribution", "7", "8"],  # What MUST be in answer (flexible)
        "should_mention": ["$7,000", "$8,000"],  # Specific values
        "should_NOT_mention": ["I do not know"],  # Signs of failure (not "not covered" - that's legitimate text)
        "category": "ira_contribution_limits",
        "severity": "HIGH",  # High priority - common question
        "note": "MUST include specific dollar amounts ($7,000 and $8,000)"
    },
    {
        "query": "What is the standard deduction for Married filing joint?",
        "expected_keywords": ["standard deduction", "31", "married"],  # Flexible matching
        "should_mention": ["$31,500"],
        "should_NOT_mention": ["I do not know"],
        "category": "standard_deduction",
        "severity": "HIGH",
        "note": "MUST include MFJ amount ($31,500)"
    },
    {
        "query": "What is the IRA deduction limit?",
        "expected_keywords": ["deduction", "limit"],
        "should_mention": ["table", "income", "filing status"],  # More flexible
        "should_NOT_mention": ["I do not know"],
        "category": "ira_deduction",
        "severity": "MEDIUM",
        "note": "Acceptable if returns deduction tables"
    },
    {
        "query": "What's the fee for filing taxes?",
        "expected_keywords": ["fee", "110"],
        "should_mention": ["$110"],
        "should_NOT_mention": ["I do not know"],
        "category": "filing_fee",
        "severity": "HIGH",
        "note": "MUST include fee amount"
    },
]


class AnswerQualityTester:
    """
    Tests if answers are not just 'related' but actually answer the question.
    """

    def __init__(self, docs_folder='knowledge_base'):
        self.bot = DocuBot(docs_folder)
        self.results = []

    def test_answer_quality(self, query, expected_keywords, should_mention,
                           should_NOT_mention, category, severity, note):
        """
        Test if answer contains required information.

        Returns: {
            "passed": bool,
            "query": str,
            "category": str,
            "severity": str,
            "issues": list of problems found,
            "answer_preview": str
        }
        """
        answer = self.bot.answer_retrieval_only(query)
        answer_lower = answer.lower()

        issues = []

        # Check 1: Answer rejection
        if "i do not know" in answer_lower:
            issues.append("❌ REJECTION: Answer is 'I do not know'")

        # Check 2: Expected keywords present
        missing_keywords = []
        for keyword in expected_keywords:
            if keyword.lower() not in answer_lower:
                missing_keywords.append(keyword)

        if missing_keywords:
            issues.append(f"❌ MISSING KEYWORDS: {', '.join(missing_keywords)}")

        # Check 3: Required mentions
        missing_mentions = []
        for mention in should_mention:
            if mention.lower() not in answer_lower:
                missing_mentions.append(mention)

        if missing_mentions:
            issues.append(f"❌ MISSING VALUES: {', '.join(missing_mentions)}")

        # Check 4: Should NOT mention
        bad_mentions = []
        for mention in should_NOT_mention:
            if mention.lower() in answer_lower:
                bad_mentions.append(mention)

        if bad_mentions:
            issues.append(f"❌ UNWANTED TEXT: {', '.join(bad_mentions)}")

        # Determine pass/fail
        passed = len(issues) == 0

        result = {
            "passed": passed,
            "query": query,
            "category": category,
            "severity": severity,
            "note": note,
            "issues": issues,
            "answer_preview": answer[:200] + "..." if len(answer) > 200 else answer,
            "full_answer_length": len(answer)
        }

        self.results.append(result)
        return result

    def run_all_tests(self):
        """Run all quality tests."""
        print("="*80)
        print("ANSWER QUALITY VERIFICATION")
        print("="*80)

        for test_case in QUALITY_TEST_CASES:
            print(f"\n📝 Testing: {test_case['query']}")
            print(f"   Category: {test_case['category']} | Severity: {test_case['severity']}")
            print(f"   Note: {test_case['note']}")
            print("-"*80)

            result = self.test_answer_quality(
                test_case['query'],
                test_case['expected_keywords'],
                test_case['should_mention'],
                test_case['should_NOT_mention'],
                test_case['category'],
                test_case['severity'],
                test_case['note']
            )

            if result['passed']:
                print("✅ PASSED - Answer contains all required information")
            else:
                print("❌ FAILED - Issues found:")
                for issue in result['issues']:
                    print(f"   {issue}")

            print(f"   Answer preview: {result['answer_preview']}")

    def generate_report(self):
        """Generate a summary report."""
        print("\n" + "="*80)
        print("QUALITY TEST SUMMARY")
        print("="*80)

        passed = sum(1 for r in self.results if r['passed'])
        failed = len(self.results) - passed

        print(f"\nTotal tests: {len(self.results)}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Pass rate: {100*passed/len(self.results):.1f}%")

        if failed > 0:
            print("\n" + "-"*80)
            print("FAILED TESTS (require attention):")
            print("-"*80)

            for result in self.results:
                if not result['passed']:
                    severity_mark = "🔴" if result['severity'] == "HIGH" else "🟡"
                    print(f"\n{severity_mark} {result['category']} [{result['severity']} SEVERITY]")
                    print(f"   Query: {result['query']}")
                    print(f"   Issues:")
                    for issue in result['issues']:
                        print(f"      {issue}")

    def export_results(self, filepath='quality_test_results.json'):
        """Export results to JSON for analysis."""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results exported to {filepath}")


if __name__ == "__main__":
    tester = AnswerQualityTester()
    tester.run_all_tests()
    tester.generate_report()
    tester.export_results()
