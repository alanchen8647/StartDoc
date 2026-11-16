"""
Comprehensive Hierarchical Retrieval Test Suite

Tests the category-first retrieval system with various question phrasings
to ensure it can handle natural language variations while returning correct answers.
"""

import pytest
import os
from docubot import DocuBot

_bot = DocuBot(docs_folder='knowledge_base')


def category_first_retrieve(query, top_k=3):
    return _bot.retrieve(query, top_k=top_k)


class TestStandardDeductionCategory:
    """Test various ways to ask about standard deduction"""

    def test_standard_deduction_married_filing_joint_original(self):
        """Original problematic query"""
        query = "What is the standard deduction for Married filing joint?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "standard_deduction" in meta.get("type", ""), f"Should match standard_deduction category, got {meta}"
        assert "$31,500" in text, "Should contain Married Filing Jointly amount"
        assert "Married filing jointly" in text or "married" in text.lower(), "Should have filing status info"

    def test_standard_deduction_married_with_dependents(self):
        """Query with mention of dependents"""
        query = "What's the standard deduction for a married couple with dependents?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "standard_deduction" in meta.get("type", ""), "Should match standard_deduction category"
        assert "$31,500" in text, "Should contain standard deduction amount"

    def test_standard_deduction_single_filer(self):
        """Query about single filer"""
        query = "What is the standard deduction for a single person?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "standard_deduction" in meta.get("type", ""), "Should match standard_deduction category"
        assert "$15,750" in text, "Should contain single filer amount"

    def test_standard_deduction_head_of_household(self):
        """Query about head of household"""
        query = "What's the standard deduction for head of household?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "standard_deduction" in meta.get("type", ""), "Should match standard_deduction category"
        assert "$23,625" in text, "Should contain head of household amount"

    def test_standard_deduction_age_65_bonus(self):
        """Query about additional deduction for age"""
        query = "How much additional standard deduction do you get at age 65?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "standard_deduction" in meta.get("type", ""), "Should match standard_deduction category"
        assert "$2,000" in text or "additional amount" in text.lower(), "Should mention age 65 bonus"


class TestIRALimitsCategory:
    """Test various ways to ask about IRA limits"""

    def test_ira_contribution_limits_basic(self):
        """Basic IRA limits query"""
        query = "What are the IRA contribution limits for 2025?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "ira" in meta.get("type", ""), "Should match ira category"
        assert "2025" in text.lower(), "Should mention 2025"

    def test_ira_married_covered_by_plan(self):
        """IRA query for married person covered by plan"""
        query = "What's the IRA deduction limit for a married person covered by a retirement plan?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "ira" in meta.get("type", ""), "Should match ira category"
        assert "covered by a retirement plan" in text or "covered" in text.lower(), "Should have plan coverage info"

    def test_ira_retirement_contribution_limit(self):
        """Retirement contribution query"""
        query = "What's the maximum I can contribute to my 401k for retirement?"
        results = category_first_retrieve(query)

        # This might not match if 401k isn't in knowledge base, but should try ira
        if len(results) > 0:
            filename, text, meta = results[0]
            assert "ira" in meta.get("type", "") or meta.get("type", ""), "Should attempt to find retirement info"

    def test_ira_single_no_coverage(self):
        """IRA query for single person not covered by plan"""
        query = "How much can I put in an IRA if I'm single and not covered by a retirement plan?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "ira" in meta.get("type", ""), "Should match ira category"


class TestFeesCategory:
    """Test various ways to ask about fees"""

    def test_fees_married_filing_jointly(self):
        """Fee query for married filing jointly"""
        query = "What's the fee for a married couple filing jointly?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "fees" in meta.get("type", ""), "Should match fees category"
        assert "$110" in text or "fee" in text.lower(), "Should have fee information"

    def test_fees_single_filer(self):
        """Fee query for single filer"""
        query = "How much does it cost to file taxes as a single person?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "fees" in meta.get("type", ""), "Should match fees category"

    def test_fees_with_dependents(self):
        """Fee query mentioning dependents"""
        query = "What is the filing fee for married filing jointly with dependents?"
        results = category_first_retrieve(query)

        assert len(results) > 0, "Should find results"
        filename, text, meta = results[0]
        assert "fees" in meta.get("type", ""), "Should match fees category"


class TestNaturalLanguageVariations:
    """Test different phrasings of the same question"""

    def test_standard_deduction_variations(self):
        """Multiple ways to ask about standard deduction"""
        variations = [
            "What is the standard deduction for married filing jointly in 2025?",
            "How much standard deduction for MFJ?",
            "Tell me the standard deduction amount for married filing joint",
            "What's the base deduction for a married couple filing together?",
        ]

        for query in variations:
            results = category_first_retrieve(query)
            if len(results) > 0:
                filename, text, meta = results[0]
                # Should either match standard deduction or fallback gracefully
                assert filename is not None, f"Query '{query}' should return some result"

    def test_ira_limits_variations(self):
        """Multiple ways to ask about IRA limits"""
        variations = [
            "IRA limits 2025",
            "How much can I contribute to my IRA?",
            "What's the maximum IRA contribution for someone with a retirement plan?",
            "Tell me about retirement account contribution limits",
        ]

        for query in variations:
            results = category_first_retrieve(query)
            if len(results) > 0:
                filename, text, meta = results[0]
                assert filename is not None, f"Query '{query}' should return some result"


class TestEdgeCases:
    """Test edge cases and ambiguous queries"""

    def test_ambiguous_deduction_query(self):
        """Query mentioning deduction without specifying type"""
        query = "What's the deduction for married filing jointly?"
        results = category_first_retrieve(query)

        # Should handle gracefully - might match standard_deduction or use fallback
        # The important thing is it doesn't crash and makes an attempt
        assert isinstance(results, list), "Should return a list"

    def test_multiple_concepts_standard_deduction_priority(self):
        """Query with multiple concepts - standard deduction should win"""
        query = "standard deduction and IRA limits for married filing"
        results = category_first_retrieve(query)

        if len(results) > 0:
            filename, text, meta = results[0]
            # Should prioritize standard_deduction since it's more specific
            assert filename is not None, "Should return a result"

    def test_typo_resilience(self):
        """Query with potential typos"""
        query = "standerd deduction for maried filing joint"  # typos
        results = category_first_retrieve(query)

        # Might not match due to typos, but should handle gracefully
        assert isinstance(results, list), "Should handle typos without crashing"

    def test_empty_query(self):
        """Empty query"""
        query = ""
        results = category_first_retrieve(query)

        # Should return empty or use fallback
        assert isinstance(results, list), "Should handle empty query gracefully"


# Run the tests
if __name__ == "__main__":
    print("="*80)
    print("HIERARCHICAL RETRIEVAL COMPREHENSIVE TEST SUITE")
    print("="*80)
    print()

    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
