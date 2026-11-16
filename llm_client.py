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
You are a helpful assistant for accounting office staff. Your job is to answer questions using ONLY the provided documents.

CRITICAL INSTRUCTIONS:
1. Answer ONLY from the documents below - do NOT use external knowledge
2. If the answer requires specific numbers, dollar amounts, or exact values, they MUST be in the documents
3. If the documents do NOT contain the answer, respond: "Not covered, ask your supervisor."

DOCUMENTS PROVIDED:
{context}

STAFF QUESTION:
{query}

RESPONSE FORMAT:
Use this structure for CLEAR, READABLE answers:

## Answer
[1-2 sentence direct answer]

### Key Information:
[Format as bullet points or table, depending on what's most readable]

**Source:** [Document name and year]

FORMATTING EXAMPLES:

Example 1 - Filing Status Question:
## Answer
For Married Filing Jointly in 2025, the standard deduction is $31,500.

### Standard Deduction Amounts (2025):
- Single: $15,750
- Married Filing Jointly: $31,500
- Head of Household: $23,625

**Source:** irs_standard_deduction_2025.md

Example 2 - Table Format for Multiple Values:
## Answer
2025 IRA contribution limits depend on your age.

| Age | Traditional IRA | Roth IRA |
|-----|---|---|
| Under 50 | $7,000 | $7,000 |
| 50 and older | $8,000 | $8,000 |

**Source:** ira_limits_2025.md

Example 3 - When to Refuse:
"Not covered, ask your supervisor."

IMPORTANT:
- Use tables for comparing multiple values or filing statuses
- Use bullet points for lists of information
- Always include the year (2025, 2026, etc.) in numbers
- Always cite which document you used
- Keep answers SHORT and DIRECT (no long paragraphs)
- When multiple topics are in the question, provide information for ALL topics you have documents for
"""

        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            return (response.text or "").strip()
        except Exception as e:
            return f"API error — could not generate answer. ({type(e).__name__}: {e})"
