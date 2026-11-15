"""
Analyze score distribution to find optimal MIN_RELEVANCE_SCORE.
"""

from docubot import DocuBot, STOPWORDS, stem_word, expand_with_synonyms, MIN_RELEVANCE_SCORE

TEST_CASES = [
    ("T01", "standard deduction", False),
    ("T02", "insurance", False),
    ("T03", "minimum fee", False),
    ("T04", "document list", False),
    ("T05", "base fee single", False),
    ("T06", "married filing jointly fee", False),
    ("T07", "head of household dependent", False),
    ("T08", "schedule c", False),
    ("T09", "schedule c expenses", False),
    ("T10", "k1 charge", False),
    ("T11", "amended return", False),
    ("T12", "reprint return", False),
    ("T13", "1098 charge", False),
    ("T14", "discount", False),
    ("T15", "expensive fee", False),
    ("T16", "consulting technical question", False),
    ("T17", "head of household divorced", False),
    ("T18", "head of household drake", False),
    ("T19", "eic self-employment", False),
    ("T20", "cash payment", False),
    ("T21", "sign", False),
    ("T22", "foreign student", False),
    ("T23", "ira", False),
    ("T24", "phone time", False),
    ("T25", "gift", False),
    ("T26", "foreign bank account", False),
    ("T27", "don't know", False),
    ("T28", "ira deduction", False),
    ("T29", "essential plan", False),
    ("T30", "routing number", False),
    ("T31", "depreciate furniture", True),
    ("T32", "tax bracket", True),
    ("T33", "estimated refund", True),
    ("T34", "company formation", True),
    ("T35", "SSN", True),
    ("T36", "EIN", True),
    ("T37", "Maria", True),
    ("T38", "pay", False),
    ("T39", "supervisor training", True),
]

def analyze():
    bot = DocuBot(docs_folder="knowledge_base")

    scores = []

    for test_id, question, should_refuse in TEST_CASES:
        query_words = {w.strip(".,!?;:-\"'") for w in question.lower().split()}
        query_words -= STOPWORDS
        query_words.discard("")

        query_stems = set()
        for word in query_words:
            query_stems.add(stem_word(word))
            for syn in expand_with_synonyms(word):
                query_stems.add(stem_word(syn))

        candidate_positions = set()
        for stem in query_stems:
            candidate_positions.update(bot.index.get(stem, []))

        best_score = 0
        best_filename = "—"

        for position in candidate_positions:
            chunk_data = bot.chunks[position]
            if len(chunk_data) == 4:
                filename, heading, text, meta = chunk_data
            else:
                filename, text = chunk_data
                heading = ""

            score = bot.score_document(question, text, heading)
            if score > best_score:
                best_score = score
                best_filename = filename

        scores.append((test_id, should_refuse, best_score, best_filename))

    # Sort by score
    scores.sort(key=lambda x: x[2])

    print(f"\n{'='*80}")
    print(f"{'Score Analysis for All 39 Tests':^80}")
    print(f"{'='*80}\n")

    print("Scores (ascending order):\n")
    print(f"{'ID':<5} {'Should':^10} {'Score':<8} {'File':<30}")
    print(f"{'':^5} {'Refuse?':^10} {'':^8}")
    print("-" * 80)

    for test_id, should_refuse, score, filename in scores:
        refuse_str = "YES" if should_refuse else "NO"
        print(f"{test_id:<5} {refuse_str:^10} {score:>7.2f}  {filename:<30}")

    # Analyze threshold
    print(f"\n{'='*80}")
    print("Threshold Analysis:")
    print(f"{'='*80}\n")

    # Find the best threshold
    # We want: all "should_refuse=True" to have score below threshold
    # and all "should_refuse=False" to have score above threshold

    for threshold in [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20]:
        correct = 0
        false_positives = 0  # should_refuse=True but score >= threshold
        false_negatives = 0  # should_refuse=False but score < threshold

        for test_id, should_refuse, score, _ in scores:
            if should_refuse:
                if score < threshold:
                    correct += 1
                else:
                    false_positives += 1
            else:
                if score >= threshold:
                    correct += 1
                else:
                    false_negatives += 1

        total_correct = correct
        print(f"Threshold={threshold:>2}: {total_correct:>2}/39 correct  "
              f"(False positives: {false_positives}, False negatives: {false_negatives})")

if __name__ == "__main__":
    analyze()
