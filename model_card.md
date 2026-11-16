# Model Card: StartDoc AI System

**Project:** Tax Office FAQ Helper (StartDoc)
---

## 1. Limitations and Biases

### System Limitations

StartDoc does not automatically update its knowledge base. The documents reflect a fixed snapshot (2025 IRS rules), and any tax law change, uncovered edge case, or missing topic will not be detected or corrected by the system itself — it depends entirely on manual updates.

**Beyond MVP:** 
1. When the system responds "I don't know," allow the user to type in the correct answer they found elsewhere, which gets captured and considered for addition to the knowledge base.
2. Add an "Import" feature letting staff upload an IRS update document directly, which gets transformed into a Markdown file and added to the knowledge base automatically.
---

## 2. Potential Misuse and Safeguards

### How Could This AI Be Misused?

- A user could intentionally or accidentally reformat client private information (SSNs, EINs, names) in a way that slips past the current pattern-matching guardrails.
- Some client situations require a higher-level supervisor's judgment, but a staff member might still ask StartDoc and accept its simple answer without considering client background.

### Safeguards We Implemented

Currently, the system only has format-based guardrails — they block input that matches known sensitive-data patterns (SSN/EIN formats, suspicious number sequences, common names). There is no safeguard yet for the "complex case → should escalate" scenario; the system cannot detect when a question is beyond its appropriate scope.

---

## 3. Surprises During Testing

During implementation, Claude was asked to generate pytest test cases to validate the quality of the project. Claude reported that all tests passed without providing the actual test details. When the test cases were reviewed manually and real queries were tested for response quality, some questions actually failed — due to retrieval errors or missing logic — that the "all tests passed" summary had not surfaced.

This was the moment that most shook confidence in the system's reliability: a passing test suite did not mean the system worked correctly in practice, and the gap was only caught by manually reading the tests and checking responses by hand.

---

## 4. Collaboration with AI (Claude)

### Suggestion You Accepted: Hierarchical Retrieval System

**What Claude Suggested:**
Implement a two-tier retrieval: first identify main category keywords (IRA, 401k), then use secondary keywords to locate the exact answer segment.

**Why You Accepted It:**
It directly solved the problem of secondary keywords (like "Married Filing Jointly") overriding the primary topic keyword in retrieval. After implementing it, retrieval accuracy on multi-topic and multi-category queries improved significantly.

---

### Suggestion You Changed #1: Feedback Buttons with Modal Pop-ups

**What Claude Suggested:**
Add "Clear Answer?" and "Not Clear" feedback buttons with a modal popup showing source documents.

**Why You Changed It:**
Streamlit's state management broke the modal — clicking the button closed the document list instead of opening it. Rather than keep debugging a non-essential MVP feature, the feature was commented out and left for future revisit instead of shipping something broken.

### Suggestion You Changed #2: Trusting "All Tests Passed" at Face Value

**What Claude Suggested (implicitly):**
Claude generated pytest cases and reported that everything passed, without surfacing the details of what was actually being tested.

**Why You Changed Your Approach:**
Rather than accepting that summary as sufficient proof of reliability, the test cases and actual responses were manually reviewed, which revealed retrieval errors and missing logic that the "all passed" report did not capture. This changed how AI-reported test results are treated going forward — as a starting point to verify, not a final answer.

---

## 5. Additional Reflections

### Key Takeaways

The biggest takeaway is noticing how unreliable things get when AI is given too much decision-making authority without verification. The pytest situation is a clear example: AI can quietly get something wrong while still reporting that everything works fine.

### What Would You Do Differently?

Collect more use-case samples from people other than myself before building. This would provide clearer goals and context for considering real user experience, and would lead to a better-informed retrieval system and guardrail design.
