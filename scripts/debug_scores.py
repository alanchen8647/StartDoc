"""
Debug script to show retrieval scores for each query.
Helps determine optimal MIN_RELEVANCE_SCORE threshold.
"""

from docubot import DocuBot
import math

# Key test cases to focus on
CRITICAL_TESTS = [
    # Should HIT (return results)
    ("T01", "standard deduction", False),
    ("T05", "base fee single", False),
    ("T15", "expensive fee", False),
    ("T27", "don't know", False),

    # Should REFUSE (return empty)
    ("T31", "depreciate furniture", True),
    ("T32", "22% tax bracket", True),
    ("T33", "estimated refund", True),
    ("T34", "company formation fee", True),
]

def debug_scores():
    """Show scores for critical test cases."""
    bot = DocuBot(docs_folder="knowledge_base")

    print(f"\n{'='*80}")
    print(f"Debug: Retrieval Scores (Current MIN_RELEVANCE_SCORE = {bot.chunks[0].__class__.__dict__.get('MIN_RELEVANCE_SCORE', 'N/A')})")
    print(f"{'='*80}\n")

    for test_id, question, should_refuse in CRITICAL_TESTS:
        print(f"{test_id} | Should refuse: {should_refuse:5} | Query: '{question}'")

        # Manually compute scores for debugging
        from docubot import STOPWORDS, stem_word, expand_with_synonyms, MIN_RELEVANCE_SCORE

        query_words = {w.strip(".,!?;:-\"'") for w in question.lower().split()}
        query_words -= STOPWORDS
        query_words.discard("")

        query_stems = set()
        for word in query_words:
            query_stems.add(stem_word(word))
            for syn in expand_with_synonyms(word):
                query_stems.add(stem_word(syn))

        # Get candidates
        candidate_positions = set()
        for stem in query_stems:
            candidate_positions.update(bot.index.get(stem, []))

        results = []
        for position in candidate_positions:
            chunk_data = bot.chunks[position]
            if len(chunk_data) == 4:
                filename, heading, text, meta = chunk_data
            else:
                filename, text = chunk_data
                heading = ""

            score = bot.score_document(question, text, heading)
            if score > 0:
                results.append((score, filename, text[:60]))

        results.sort(key=lambda r: r[0], reverse=True)

        if results:
            print(f"  Top result: score={results[0][0]:.2f}, threshold={MIN_RELEVANCE_SCORE}")
            print(f"    File: {results[0][1]}")
            print(f"    Text: {results[0][2]}...")

            if results[0][0] < MIN_RELEVANCE_SCORE:
                print(f"    Status: Below threshold (would REFUSE)")
            else:
                print(f"    Status: Above threshold (would HIT)")
        else:
            print(f"  No candidates found (would REFUSE)")

        print()

if __name__ == "__main__":
    debug_scores()
