"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import re
import glob
import string
import math
import json
from nltk.stem import PorterStemmer

# Common words that carry little topical signal on their own. Chunks are
# short, so even a word present in most chunks (like "the") can still rack
# up enough raw occurrences to outweigh the one or two words that actually
# distinguish a relevant section. Filtering these out of the query keeps
# scoring focused on words that identify a topic.
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "doing", "in", "on", "at", "to", "of", "for",
    "and", "or", "but", "with", "about", "as", "by", "from", "this",
    "that", "these", "those", "it", "its", "what", "which", "who", "how",
    "where", "when", "why", "there", "any", "i",
}

# Minimum score the best-matching chunk must reach before we treat it as
# real evidence. Kept at 3.0 with phrase-matching + guardrail improvements.
# Phrase-level matching reduces false positives (e.g., "#22" won't match "22% tax bracket")
# Guardrails (Step 3) handle SSN/EIN/names, so retrieval can focus on content accuracy.
MIN_RELEVANCE_SCORE = 3.0

# Extended synonym table for common accounting office terms
# Maps keywords to their semantic equivalents for better retrieval
SYNONYMS = {
    # Fee-related
    "fee": {"charge", "cost", "price", "service charge", "amount"},
    "charge": {"fee", "cost", "price"},
    "price": {"fee", "charge", "cost"},
    "cost": {"fee", "charge", "price"},

    # Deduction-related
    "deduction": {"discount", "write-off", "reduction", "standard"},
    "discount": {"deduction", "reduction"},
    "write-off": {"deduction"},
    "reduction": {"deduction", "discount"},

    # Standard deduction (key improvement)
    "standard": {"standard deduction", "base deduction"},
    "amount": {"fee", "sum", "total"},

    # Filing/Return-related
    "return": {"form", "filing", "file"},
    "filing": {"return", "file", "form"},
    "file": {"filing", "return", "form"},
    "form": {"return", "filing", "1040"},

    # Marital status (crucial for queries)
    "married": {"joint", "jointly", "mfj"},
    "joint": {"married", "jointly", "mfj"},
    "jointly": {"married", "joint", "mfj"},
    "single": {"unmarried", "individual"},

    # Dependent-related
    "dependent": {"dependent", "family", "child", "spouse"},
    "family": {"dependent", "household", "spouse"},
    "household": {"family", "dependent"},

    # Tax-related
    "tax": {"income tax", "federal tax"},
    "income": {"earnings", "salary", "wage"},
    "estimate": {"calculation", "quote", "estimated"},
    "bracket": {"rate", "percentage"},

    # Credit-related
    "credit": {"eic", "eitc", "tax credit", "earned income"},
    "eic": {"earned income credit", "eitc", "credit"},
    "eitc": {"eic", "earned income credit", "credit"},

    # IRA/Retirement
    "ira": {"retirement", "retirement account", "401k"},
    "retirement": {"ira", "pension", "401k"},
    "limit": {"limit", "maximum", "cap"},
    "maximum": {"limit", "cap"},

    # Payment/Filing status
    "payment": {"pay", "remit", "send"},
    "deadline": {"due date", "due", "date"},
    "threshold": {"limit", "minimum", "requirement"},

    # Accounting concepts
    "income": {"earnings", "compensation", "salary", "wages"},
    "salary": {"income", "wages", "compensation"},
    "wage": {"income", "salary", "earnings"},
}

# Stemmer for handling plurals/singulars
_STEMMER = PorterStemmer()

def stem_word(word):
    """Apply Porter stemming to normalize word forms."""
    return _STEMMER.stem(word)

def normalize_query(query: str) -> str:
    """
    Normalize common question patterns to improve retrieval.

    Handles:
    - "What's/What is" → remove
    - "for/to" before filing status → extract key terms
    - Remove redundant context words ("family", "with no dependent")
    - Keep only high-value terms for retrieval
    """
    import re

    # Remove common question starters
    normalized = re.sub(r"^(what|tell me|can you|how|is there)", "", query, flags=re.IGNORECASE)
    normalized = re.sub(r"^('s|is|are|the)\s+", "", normalized, flags=re.IGNORECASE)

    # Remove "for" and "with" noise when followed by context words
    # "for Married Filing Joint family with no dependent" → extract "married filing"
    normalized = re.sub(r"\s+(family|with no dependent|without dependents|who is|that is)\b.*$", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+for\s+(?=married|single|head)", " ", normalized, flags=re.IGNORECASE)

    # Clean up extra spaces and lowercase
    normalized = " ".join(normalized.split()).strip()
    return normalized if normalized else query

def expand_with_synonyms(word):
    """Expand a word with its synonyms from the table."""
    expanded = {word}
    if word in SYNONYMS:
        expanded.update(SYNONYMS[word])
    return expanded


def extract_ngrams(text: str, n: int = 2) -> set:
    """
    Extract n-grams (consecutive word sequences) from text.

    Purpose: Capture phrases to improve matching accuracy.

    Example:
        extract_ngrams("estimated refund amount", n=2)
        → {"estimated refund", "refund amount"}

    Why this works:
        - Detects that "estimated refund" is a complete phrase
        - Not just scattered "estimated" and "refund" in different contexts
    """
    words = text.lower().split()
    if len(words) < n:
        return set()

    # Create n-grams as space-separated strings
    return {
        ' '.join(words[i:i+n])
        for i in range(len(words) - n + 1)
    }


def has_negation(text: str) -> bool:
    """
    Check if text contains negation/contradiction words.

    Used for penalty: if query says "not X" but document doesn't mention "not",
    the document might not be addressing the actual question.
    """
    negation_words = ["not", "don't", "doesn't", "can't", "cannot",
                      "except", "without", "except", "no ", "never"]
    text_lower = text.lower()
    return any(f" {neg} " in f" {text_lower} " for neg in negation_words)

class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load document metadata from manifest.json if it exists
        self.metadata_map = self._load_metadata()

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, text)

        # Split documents into smaller, independently retrievable sections
        # chunks include: List of (filename, heading, chunk_text, metadata_dict)
        self.chunks = self.build_chunks(self.documents)

        # Build a retrieval index over chunks, not whole documents
        self.index = self.build_index(self.chunks)

    # -----------------------------------------------------------
    # Metadata Loading
    # -----------------------------------------------------------

    def _load_metadata(self):
        """
        Load document metadata from manifest.json in docs_folder.
        Returns a dict mapping filename -> metadata dict.
        """
        metadata_path = os.path.join(self.docs_folder, "manifest.json")
        if not os.path.exists(metadata_path):
            return {}

        try:
            with open(metadata_path, "r", encoding="utf8") as f:
                manifest = json.load(f)

            # Build a map: filename -> metadata
            meta_map = {}
            for doc_info in manifest.get("documents", []):
                filename = doc_info.get("doc")
                if filename:
                    meta_map[filename] = {
                        "year": doc_info.get("year"),
                        "tier": doc_info.get("tier", 4),
                        "audience": doc_info.get("audience"),
                        "type": doc_info.get("type"),
                    }
            return meta_map
        except Exception as e:
            print(f"Warning: could not load manifest.json: {e}")
            return {}

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)

        Normalizes smart/curly quotes to straight quotes for later quote verification.
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)

                # Normalize curly quotes to straight quotes
                # " → " and " → "
                text = text.replace(""", '"').replace(""", '"')
                # ' → ' and ' → '
                text = text.replace("'", "'").replace("'", "'")

                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Chunking: split documents into smaller retrievable sections
    # -----------------------------------------------------------

    _HEADING_RE = re.compile(r"^#{1,6}\s+\S")

    def build_chunks(self, documents):
        """
        Splits each document into smaller sections so retrieval can return
        a focused snippet instead of the entire file.

        Preferred rule: split on markdown headings (# through ######),
        keeping each heading attached to the content below it. If a
        document has no headings (e.g. a plain .txt file), fall back to
        splitting on blank lines (paragraphs).

        Returns list of (filename, heading, chunk_text, metadata) tuples.
        Metadata is a dict with keys: year, tier, audience, type.
        """
        chunks = []
        for filename, text in documents:
            # Get metadata for this document from manifest
            doc_meta = self.metadata_map.get(filename, {})

            sections = self._split_by_headings_with_title(text)
            if not sections or all(not s[1] for s in sections):
                # No headings found; fall back to paragraph split
                paras = self._split_by_paragraphs(text)
                sections = [("", para) for para in paras]

            for heading, section in sections:
                section = section.strip()
                if section:
                    chunks.append((filename, heading, section, doc_meta))
        return chunks

    def _split_by_headings_with_title(self, text):
        """Split by headings and track the heading for each section."""
        sections = []
        current_heading = ""
        current_lines = []

        for line in text.splitlines():
            if self._HEADING_RE.match(line):
                if current_lines:
                    sections.append((current_heading, "\n".join(current_lines)))
                current_heading = line
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_heading, "\n".join(current_lines)))
        return sections

    def _split_by_headings(self, text):
        sections = []
        current_lines = []
        for line in text.splitlines():
            if self._HEADING_RE.match(line):
                if current_lines:
                    sections.append("\n".join(current_lines))
                current_lines = [line]
            else:
                current_lines.append(line)
        if current_lines:
            sections.append("\n".join(current_lines))
        return sections

    def _split_by_paragraphs(self, text):
        return re.split(r"\n\s*\n", text)

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def build_index(self, chunks):
        """
        Builds a tiny inverted index mapping stemmed words to the
        positions (in self.chunks) of the chunks they appear in:

        {
            "token": [0, 4],
            "databas": [7]
        }

        Words are stemmed to handle plurals/singulars. Synonyms are
        expanded at query time, not in the index.
        retrieve() uses this both to find candidate chunks quickly and,
        via len(index[word]), to tell common words from rare ones.
        """
        index = {}
        for position, chunk_data in enumerate(chunks):
            # Unpack (filename, heading, text, metadata) [4-tuple now]
            if len(chunk_data) == 4:
                filename, heading, text, meta = chunk_data
            elif len(chunk_data) == 3:
                filename, heading, text = chunk_data
                meta = {}
            else:
                filename, text = chunk_data
                heading = ""
                meta = {}

            # Index both heading and body text
            full_text = (heading + " " + text) if heading else text

            for token in full_text.lower().split():
                word = token.strip(string.punctuation)
                if not word:
                    continue
                stemmed = stem_word(word)
                positions = index.setdefault(stemmed, [])
                if position not in positions:
                    positions.append(position)
        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text, heading=""):
        """
        Relevance score for how well text (a chunk) matches query.

        Plain word-overlap counts are dominated by common words ("the",
        "does", "what") that appear in every chunk. To avoid that, each
        matching word is weighted by inverse chunk frequency using
        self.index: a word that appears in few chunks is a stronger
        signal than one that appears in most of them.

        Words are stemmed and expanded with synonyms for matching.
        Words in the heading are weighted 2x higher than body words.
        """
        # Process query: lowercase, strip punctuation, stem, remove stopwords
        query_words = {w.strip(string.punctuation) for w in query.lower().split()}
        query_words -= STOPWORDS
        query_words.discard("")

        # Stem query words and expand with synonyms
        query_stems = set()
        for word in query_words:
            query_stems.add(stem_word(word))
            # Also add stemmed versions of synonyms
            for syn in expand_with_synonyms(word):
                query_stems.add(stem_word(syn))

        # Process heading and body separately for weighting
        heading_words_stemmed = []
        body_words_stemmed = []

        for token in heading.lower().split():
            word = token.strip(string.punctuation)
            if word:
                heading_words_stemmed.append(stem_word(word))

        for token in text.lower().split():
            word = token.strip(string.punctuation)
            if word:
                body_words_stemmed.append(stem_word(word))

        total_chunks = len(self.chunks)
        score = 0.0

        for stem in query_stems:
            # Count in heading (2x weight) and body (1x weight)
            heading_count = heading_words_stemmed.count(stem)
            body_count = body_words_stemmed.count(stem)
            total_count = heading_count * 2 + body_count

            if total_count == 0:
                continue

            chunk_frequency = len(self.index.get(stem, []))
            if total_chunks <= 1:
                weight = 1
            elif chunk_frequency >= total_chunks:
                weight = 0
            else:
                weight = math.log(total_chunks / chunk_frequency)

            score += total_count * weight

        # ===== NEW (Step 2, Plan C): PHRASE-LEVEL BONUS =====
        # Check if 2-grams and 3-grams (exact phrases) appear in text
        # This boosts relevant documents and reduces false positives

        full_text_lower = (heading + " " + text).lower()
        phrase_bonus = 0

        # 2-gram check (two consecutive words)
        # If a 2-word phrase matches, it's a strong signal
        bigrams = extract_ngrams(query, n=2)
        for bigram in bigrams:
            if bigram in full_text_lower:
                phrase_bonus += 12.0

        # 3-gram check (three consecutive words)
        # If a 3-word phrase matches, it's very strong
        trigrams = extract_ngrams(query, n=3)
        for trigram in trigrams:
            if trigram in full_text_lower:
                phrase_bonus += 20.0

        score += phrase_bonus

        # ===== NEW: NEGATION PENALTY (REFINED) =====
        # Be more selective: only penalize substantive negation questions
        # E.g., "without X" → should mention "without" in answer
        # But "don't know" isn't a question about absence, so don't penalize

        negation_penalty = 0

        # Only check for strong negation patterns (substantive absence questions)
        strong_negations = ["without ", "no ", "cannot ", "not allowed"]
        has_strong_negation = any(neg in query.lower() for neg in strong_negations)

        if has_strong_negation:
            # Only penalize if document lacks negation context
            if not has_negation(text) and not has_negation(heading):
                negation_penalty -= 3.0  # Reduced penalty

        score += negation_penalty

        return score

    def _identify_category(self, query: str):
        """
        Hierarchical retrieval: identify if query matches a known category.
        Returns (category_name, target_file) or (None, None)
        """
        query_lower = query.lower()

        # Define category keywords and their target documents
        categories = {
            "standard_deduction": {
                "keywords": ["standard deduction", "standard deduction for"],
                "file": "irs_standard_deduction_2025.md",
            },
            "ira": {
                "keywords": ["ira", "ira contribution", "ira limit", "ira deduction"],
                "file": "ira_limits_2025.md",
            },
            "fees": {
                "keywords": ["fee", "fees", "filing fee", "service fee"],
                "file": "fee_cover_page_2026.md",
            },
        }

        # Check for category match (longer keywords first)
        for category, info in categories.items():
            for keyword in sorted(info["keywords"], key=len, reverse=True):
                if keyword in query_lower:
                    return category, info["file"]

        return None, None

    def retrieve(self, query, top_k=3):
        """
        Hierarchical Retrieval: Two-level search strategy

        Level 1: Check if query matches a known category (e.g., "standard deduction")
        Level 2: If category matched, load that document directly
        Otherwise: Use standard TF-IDF retrieval

        Returns list of (filename, text, metadata) tuples sorted by relevance.
        Refuses (returns []) if no match is strong enough.
        """
        # Normalize query to improve retrieval (remove noise words, standardize phrasing)
        query = normalize_query(query)

        # LEVEL 1: Try category-first retrieval for known categories
        category, target_file = self._identify_category(query)

        if category and target_file:
            # Try to load the target document directly
            target_path = os.path.join(self.docs_folder, target_file)
            if os.path.exists(target_path):
                try:
                    with open(target_path, 'r', encoding='utf-8') as f:
                        full_text = f.read()

                    # Return the document directly
                    meta = {"year": 2025 if "2025" in target_file else 2026, "type": category}
                    return [(target_file, full_text, meta)]
                except Exception:
                    # Fall back to standard retrieval if file read fails
                    pass

        # LEVEL 2: Standard retrieval (fallback)
        # Process query: lowercase, strip punctuation, stem
        query_words = {w.strip(string.punctuation) for w in query.lower().split()}
        query_words -= STOPWORDS
        query_words.discard("")

        # Stem query words and expand with synonyms to find candidates
        query_stems = set()
        for word in query_words:
            query_stems.add(stem_word(word))
            for syn in expand_with_synonyms(word):
                query_stems.add(stem_word(syn))

        candidate_positions = set()
        for stem in query_stems:
            candidate_positions.update(self.index.get(stem, []))

        results = []
        for position in candidate_positions:
            chunk_data = self.chunks[position]
            if len(chunk_data) == 4:
                filename, heading, text, meta = chunk_data
            elif len(chunk_data) == 3:
                filename, heading, text = chunk_data
                meta = {}
            else:
                filename, text = chunk_data
                heading = ""
                meta = {}

            score = self.score_document(query, text, heading)
            if score > 0:
                results.append((score, filename, text, meta))

        results.sort(key=lambda r: r[0], reverse=True)

        # Refusal guardrail: even the best match isn't strong enough to
        # count as real evidence, so return nothing rather than a guess.
        if not results or results[0][0] < MIN_RELEVANCE_SCORE:
            return []

        return [(filename, text, meta) for _, filename, text, meta in results[:top_k]]

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []
        for item in snippets:
            if len(item) == 3:
                filename, text, meta = item
            else:
                filename, text = item
                meta = {}

            year = meta.get("year", "")
            year_str = f" ({year})" if year else ""
            formatted.append(f"[{filename}{year_str}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        # Convert to format expected by llm_client: (filename, text) tuples
        snippet_pairs = [(item[0], item[1]) if len(item) == 3 else item for item in snippets]
        return self.llm_client.answer_from_snippets(query, snippet_pairs)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
