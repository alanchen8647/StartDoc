"""
Knowledge Base Coverage Audit

For each test query, verify:
1. Is there an exact answer in the knowledge base?
2. If YES: Test should PASS (answer must be returned)
3. If NO: Test should FAIL with "I don't know" (system must refuse)

This prevents false positives - finding partial matches when exact answer doesn't exist.
"""

import os
import json

# Test queries to audit
AUDIT_QUERIES = [
    {
        "query": "What are the IRA contribution limits for 2025?",
        "query_intent": "Specific dollar amounts for IRA contributions",
        "expected_answer": "$7,000 (age <50), $8,000 (age 50+)",
        "document_to_check": "knowledge_base/ira_limits_2025.md",
        "exact_phrases": ["$7,000", "$8,000", "contribution limit"],
        "category": "ira_contribution_limits"
    },
    {
        "query": "What is the standard deduction for Married filing joint?",
        "query_intent": "Specific dollar amount for MFJ standard deduction",
        "expected_answer": "$31,500",
        "document_to_check": "knowledge_base/irs_standard_deduction_2025.md",
        "exact_phrases": ["$31,500", "Married filing jointly"],
        "category": "standard_deduction"
    },
    {
        "query": "What's the fee for filing taxes?",
        "query_intent": "Filing fee amount",
        "expected_answer": "$110 (MFJ)",
        "document_to_check": "knowledge_base/fee_cover_page_2026.md",
        "exact_phrases": ["$110", "fee"],
        "category": "filing_fee"
    },
    {
        "query": "What is the IRA deduction limit?",
        "query_intent": "General IRA deduction limits",
        "expected_answer": "Depends on filing status and income (see tables)",
        "document_to_check": "knowledge_base/ira_limits_2025.md",
        "exact_phrases": ["deduction limit", "filing status"],
        "category": "ira_deduction"
    },
    {
        "query": "What's the maximum I can contribute to my 401k for retirement?",
        "query_intent": "401(k) contribution limit",
        "expected_answer": "~$24,500 per year (2025)",
        "document_to_check": "knowledge_base/401k_limits_2025.md",
        "exact_phrases": ["401", "contribution limit"],
        "category": "401k_contribution_limits"
    },
]


class KnowledgeBaseAuditor:
    """
    Audit knowledge base to verify exact answers exist.
    """

    def __init__(self):
        self.audit_results = []

    def check_document_exists(self, filepath):
        """Check if document exists."""
        return os.path.exists(filepath)

    def check_exact_answer_exists(self, filepath, exact_phrases):
        """
        Check if document contains the exact answer.
        All phrases in exact_phrases must be found.
        """
        if not self.check_document_exists(filepath):
            return False, "Document not found"

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                content_lower = content.lower()

            missing_phrases = []
            for phrase in exact_phrases:
                if phrase.lower() not in content_lower:
                    missing_phrases.append(phrase)

            if missing_phrases:
                return False, f"Missing phrases: {', '.join(missing_phrases)}"

            return True, "All required phrases found"
        except Exception as e:
            return False, f"Error reading document: {str(e)}"

    def audit_query(self, query, query_intent, expected_answer, document_to_check,
                   exact_phrases, category):
        """
        Audit a single query against the knowledge base.

        Returns:
        {
            "query": str,
            "category": str,
            "document_exists": bool,
            "exact_answer_exists": bool,
            "status": "SHOULD_ANSWER" | "SHOULD_REFUSE",
            "findings": str,
            "recommendation": str
        }
        """

        doc_exists = self.check_document_exists(document_to_check)
        answer_exists, details = self.check_exact_answer_exists(document_to_check, exact_phrases)

        # Determine if system should answer or refuse
        if answer_exists:
            status = "SHOULD_ANSWER"
            recommendation = "✅ System MUST return answer with exact information"
        else:
            status = "SHOULD_REFUSE"
            recommendation = "❌ System SHOULD return 'I don't know' (no exact answer exists)"

        result = {
            "query": query,
            "category": category,
            "query_intent": query_intent,
            "expected_answer": expected_answer,
            "document": document_to_check,
            "document_exists": doc_exists,
            "exact_answer_exists": answer_exists,
            "status": status,
            "findings": details,
            "recommendation": recommendation
        }

        self.audit_results.append(result)
        return result

    def run_audit(self):
        """Run audit on all queries."""
        print("="*80)
        print("KNOWLEDGE BASE COVERAGE AUDIT")
        print("="*80)

        for query_audit in AUDIT_QUERIES:
            print(f"\n📋 Auditing: {query_audit['query']}")
            print("-"*80)

            result = self.audit_query(
                query_audit['query'],
                query_audit['query_intent'],
                query_audit['expected_answer'],
                query_audit['document_to_check'],
                query_audit['exact_phrases'],
                query_audit['category']
            )

            print(f"Category: {result['category']}")
            print(f"Intent: {result['query_intent']}")
            print(f"Expected Answer: {result['expected_answer']}")
            print(f"\nDocument: {result['document']}")
            print(f"  Exists: {result['document_exists']}")
            print(f"  Exact answer found: {result['exact_answer_exists']}")
            print(f"\nStatus: {result['status']}")
            print(f"Finding: {result['findings']}")
            print(f"Recommendation: {result['recommendation']}")

    def generate_report(self):
        """Generate audit report."""
        print("\n" + "="*80)
        print("AUDIT SUMMARY")
        print("="*80)

        should_answer = sum(1 for r in self.audit_results if r['status'] == 'SHOULD_ANSWER')
        should_refuse = sum(1 for r in self.audit_results if r['status'] == 'SHOULD_REFUSE')

        print(f"\nTotal queries audited: {len(self.audit_results)}")
        print(f"Should return answer: {should_answer}")
        print(f"Should refuse (no exact answer): {should_refuse}")

        print("\n" + "-"*80)
        print("QUERIES THAT SHOULD RETURN ANSWERS:")
        print("-"*80)
        for r in self.audit_results:
            if r['status'] == 'SHOULD_ANSWER':
                status_mark = "✅"
                print(f"{status_mark} {r['category']}: {r['query'][:60]}")
                print(f"   Expected: {r['expected_answer']}")
                print(f"   Document: {r['document']}")

        print("\n" + "-"*80)
        print("QUERIES THAT SHOULD BE REFUSED (No exact answer):")
        print("-"*80)
        if should_refuse == 0:
            print("None - all test queries have exact answers in knowledge base")
        else:
            for r in self.audit_results:
                if r['status'] == 'SHOULD_REFUSE':
                    status_mark = "❌"
                    print(f"{status_mark} {r['category']}: {r['query'][:60]}")
                    print(f"   Reason: {r['findings']}")
                    print(f"   Document: {r['document']}")

    def export_audit(self, filepath='audit_results.json'):
        """Export audit results."""
        with open(filepath, 'w') as f:
            json.dump(self.audit_results, f, indent=2)
        print(f"\n✅ Audit results exported to {filepath}")


if __name__ == "__main__":
    auditor = KnowledgeBaseAuditor()
    auditor.run_audit()
    auditor.generate_report()
    auditor.export_audit()
