# Handoff: F&Q helper for part-time (PT) staff — continue in Claude Code

Read this first. It replaces the earlier chat history. Do NOT change starter code until the user says "start step 2".

## 1. What we are building
An AI FAQ helper for part-time staff at a small accounting office. A PT types a question; the helper returns a short answer, numbered steps and quoted sources with document year, drawn from the office's training documents (and official IRS sources). If the documents do not cover it: "Not covered, ask your supervisor."

Course requirements: useful AI task; at least one integrated advanced feature (RAG core, reliability/testing second); reproducible setup with clear steps; logging/guardrails.

## 2. Fixed decisions
- Python MVP on the starter `ai110-module4tinker-docubot-starter`. 2-week timeline. Free Gemini API (`google-genai`), LLM behind one interface (`llm_client.py`).
- Keyword retrieval + small synonym list first. Embeddings only if the test set shows misses.
- Guardrail blocks SSN, EIN and real names; allows hypothetical numbers.
- Quote verification against retrieved text; low-confidence refusal; logging; test set + evaluation.
- UI: simple Streamlit page `app.py`, local only, no web server, no API. `main.py` CLI stays as a backup.
- Fee quoter, tax estimator, router, Electron: after MVP.
- User replies in Chinese with English terms in parentheses.

## 3. Target flow (diagrams/twist2_diagram.mmd)
PT question -> guardrail (name/SSN/EIN) -> retrieve from docs_pt/ -> threshold -> LLM answers only from passages -> quote check -> show answer + sources + year -> PT clicks helpful/not -> log -> owner reviews. Four exits (blocked, not covered, quote check failed, answer) all write to the log. `evaluation.py` runs 39 tests.
Earlier stages: baseline_diagram.mmd, twist1_diagram.mmd.

## 4. What already exists
Starter folder: `D:\CodePath\Final Project\ai110-module4tinker-docubot-starter\`
- `docubot.py` (DocuBot: load_documents, build_chunks, _split_by_headings, _split_by_paragraphs, build_index, score_document, retrieve(query, top_k=3), answer_retrieval_only, answer_rag; MIN_RELEVANCE_SCORE = 2.0; chunks are (filename, text) tuples), `llm_client.py` (GeminiClient), `main.py`, `evaluation.py`, `dataset.py`, `model_card.md`, `README.md`, `requirements.txt`, `.env` (never read it).
- Added already: `prepare_docs.py` (docx/pdf/md -> clean markdown, SSN/EIN scan, writes docs_pt/ + manifest.json), `docs_pt/` (16 documents + manifest.json), `diagrams/`, requirements now include python-docx and pdfplumber.
- Source files and helper data: `C:\Users\alanc\Downloads\Codepath Project` (originals, untouched) and its `helper_data\` (transcriptions, `source_index.md`, `test_questions_draft.md` with 39 tests T01-T39).
- Docs workbook (Claude Docs): https://claude.ai/artifact/VNAbFXNKgTFmJb2hh7XooS

Chunks are one numbered rule each, headed `### <Group> #<n>`. Metadata per document in manifest.json: year, tier, audience, language, type. Rules: the 2026 office manual wins over the older preparer manual on conflicts; the fee cover page wins for fee amounts.

## 5. Baseline findings (unchanged starter on docs_pt)
- Misses on plural/singular (discounts/discount) and on "standard deduction".
- T31 and T32 should refuse but do not: the threshold is too low or scoring too loose.

## 6. Step 2 tasks (retrieval) — start only when the user says go
1. Add stemming and a small synonym list.
2. Weight heading/section title above body text.
3. Chunk metadata: file, section, year, tier, audience (read from manifest.json). Ignore title-only and tiny chunks; do not paragraph-split short docs.
4. Retune MIN_RELEVANCE_SCORE so T31/T32 refuse and answerable tests still hit.
5. Normalize curly quotes (needed later by the quote check).
Done when: retrieval hit rate on the 39 tests is reported by `evaluation.py`, T31/T32 refuse, no regressions in answerable tests.

## 7. Later steps
3. Prompt format in `llm_client.py` (short answer, numbered steps, quotes with year).
4. Input guardrail (regex SSN `\b\d{3}-\d{2}-\d{4}\b`, EIN `\b\d{2}-\d{7}\b`, plus name detection).
5. Quote verifier, then logger.
6. `evaluation.py` with the 39-question set.
7. `app.py` (Streamlit; add `streamlit` to requirements; helpful/not buttons write to log).
8. README setup steps, `.env.example`, model card.

## 8. Open questions for the user
- EIC rule for singles: assumed singles need either proof; MFJ/HOH need both. T19 is blocked until confirmed.
- Which staff names in office manual Phone & Text #3 are supervisors (names currently unmasked).
- Tax estimator/router after MVP: confirm.
- $200K+ minimum fee vs table total (post-MVP quoter).
- NYC Care PDF excluded pending manual translation.

## 9. Working notes
- Keep the starter's structure; change in small steps and run `evaluation.py` after each.
- Never read or print `.env`. Never put real client data in tests.
- Streamlit can only be tested on the user's machine.
- Commit messages: short, one change each.
