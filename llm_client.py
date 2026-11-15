"""
Gemini client wrapper used by DocuBot.

Handles:
- Configuring the Gemini client from the GEMINI_API_KEY environment variable
- Naive "generation only" answers over the full docs corpus (Phase 0)
- RAG style answers that use only retrieved snippets (Phase 2)

Experiment with:
- Prompt wording
- Refusal conditions
- How strictly the model is instructed to use only the provided context
"""

import os
from google import genai

# Central place to update the model name if needed.
# You can swap this for a different Gemini model in the future.
GEMINI_MODEL_NAME = "gemini-3.5-flash-lite"


class GeminiClient:
    """
    Simple wrapper around the Gemini model.

    Usage:
        client = GeminiClient()
        answer = client.naive_answer_over_full_docs(query, all_text)
        # or
        answer = client.answer_from_snippets(query, snippets)
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Missing GEMINI_API_KEY environment variable. "
                "Set it in your shell or .env file to enable LLM features."
            )

        self.client = genai.Client(api_key=api_key)

    # -----------------------------------------------------------
    # Phase 0: naive generation over full docs
    # -----------------------------------------------------------

    def naive_answer_over_full_docs(self, query, all_text):
        # We ignore all_text and send a generic prompt instead
        prompt = f"""
    You are a documentation assistant. 
    Answer this developer question: {query}
    """
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            return (response.text or "").strip()
        except Exception as e:
            return f"Unable to generate an answer. ({type(e).__name__}: {e})"

    # -----------------------------------------------------------
    # Phase 2: RAG style generation over retrieved snippets
    # -----------------------------------------------------------

    def answer_from_snippets(self, query, snippets):
        """
        Phase 2:
        Generate an answer using only the retrieved snippets.

        snippets: list of (filename, text) tuples selected by DocuBot.retrieve

        The prompt:
        - Shows each snippet with its filename
        - Instructs the model to rely only on these snippets
        - Requires an explicit "I do not know" refusal when needed
        """

        if not snippets:
            return "I do not know based on the docs I have."

        context_blocks = []
        for filename, text in snippets:
            block = f"File: {filename}\n{text}\n"
            context_blocks.append(block)

        context = "\n\n".join(context_blocks)

        prompt = f"""
You are a cautious assistant helping accounting office staff find answers in training documents.

CRITICAL INSTRUCTIONS:
1. You MUST answer ONLY from the provided documents below.
2. Do NOT use memory, external knowledge, or assumptions.
3. If the documents do NOT explicitly contain the answer, you MUST refuse.

DOCUMENTS PROVIDED:
{context}

STAFF QUESTION:
{query}

ANSWER GUIDELINES:
- Check if the documents contain SPECIFIC information that DIRECTLY answers the question.
- EXAMPLES OF REFUSAL:
  * Question: "What's the 22% tax bracket for 2025?"
    Documents mention "#22" rules but NOT "22% tax bracket"
    → Answer: "Not covered, ask your supervisor."

  * Question: "How do I depreciate office furniture?"
    Documents mention furniture but NOT depreciation methods
    → Answer: "Not covered, ask your supervisor."

  * Question: "What's the estimated refund for a client making $60k?"
    Documents mention "estimated tax" but NOT "refund estimation"
    → Answer: "Not covered, ask your supervisor."

- If documents DO contain the answer:
  * Provide a short, clear answer (2-3 sentences max)
  * Include the year of the source (e.g., "from 2026 office manual")
  * Cite which document you used

REMEMBER: When in doubt, refuse. Better to say "Not covered" than guess.
"""

        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            return (response.text or "").strip()
        except Exception as e:
            return f"API error — could not generate answer. ({type(e).__name__}: {e})"
