# 🚀 DocuBot - Getting Started

## Quick Start (30 seconds)

```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1    # Windows PowerShell
source venv/bin/activate        # Mac/Linux

# 2. Run the app
streamlit run app.py

# 3. Open browser to http://localhost:8501
```

That's it! The Streamlit UI should open automatically.

---

## Project Structure

```
docubot/
├── app.py                       ← Main Streamlit application
├── docubot.py                   ← Retrieval engine
├── llm_client.py                ← LLM integration
├── guardrail.py                 ← Security/input validation
├── logger.py                    ← Logging system
├── main.py                      ← CLI interface (alternative)
├── dataset.py                   ← Sample queries
├── requirements.txt             ← Dependencies
├── .env                         ← Environment variables (GEMINI_API_KEY)
│
├── docs/                        ← Documentation
│   ├── README_FINAL.md          ← Project overview
│   ├── QUICKSTART_UI.md         ← UI usage guide
│   ├── STREAMLIT_UI_GUIDE.md    ← Detailed feature docs
│   ├── STEP3_SUMMARY.md         ← Technical architecture
│   └── TROUBLESHOOTING.md       ← Problem solving
│
├── scripts/                     ← Test & utility scripts
│   ├── verify_step3_critical.py ← Quick system verification
│   ├── step3_evaluation.py      ← Full 39-test evaluation
│   ├── prepare_docs.py          ← Convert Word/PDF to markdown
│   └── ... (other test scripts)
│
├── knowledge_base/              ← FAQ documents (auto-loaded)
│   ├── fees_2026.md
│   ├── irs_standard_deduction_2025.md
│   └── ... (more markdown files)
│
└── .gitignore                   ← Git configuration
```

---

## First Time Setup

```bash
# 1. Create & activate virtual environment
python -m venv venv
.\.venv\Scripts\Activate.ps1    # Windows
source venv/bin/activate        # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set GEMINI_API_KEY (optional, for LLM features)
# Edit .env and add your key:
# GEMINI_API_KEY=your_key_here

# 4. Start app
streamlit run app.py
```

---

## Documentation Guide

- **👤 Just want to use it?**  
  → Read: `docs/QUICKSTART_UI.md`

- **👨‍💼 Managing/administering the system?**  
  → Read: `docs/STREAMLIT_UI_GUIDE.md`

- **🔧 IT/Technical setup & troubleshooting?**  
  → Read: `docs/TROUBLESHOOTING.md`

- **👨‍💻 Developer/Technical deep dive?**  
  → Read: `docs/STEP3_SUMMARY.md` and `docs/README_FINAL.md`

---

## Key Features

✅ Modern Streamlit Web UI  
✅ Two retrieval modes: Fast (0.3s) & Smart (2-5s)  
✅ Document browser & preview  
✅ Real-time log viewer  
✅ SSN/EIN/Name detection  
✅ LLM-powered answer filtering  
✅ 97-100% accuracy  

---

## Verification

```bash
# Quick test (4 critical cases)
python scripts/verify_step3_critical.py
# Expected: All 4 should show ✓ CORRECTLY REFUSED

# Full test (39 total cases)
python scripts/step3_evaluation.py
# Expected: 38-39/39 correct (97-100%)
```

---

## File Organization

| Folder | Purpose | When to Use |
|--------|---------|-------------|
| `/` | Core code files | Daily use |
| `docs/` | All documentation | Learning & reference |
| `scripts/` | Testing & utilities | Verification & analysis |
| `knowledge_base/` | FAQ documents | Auto-loaded by app |

---

## Next Steps

1. Start the app: `streamlit run app.py`
2. Try asking a question
3. Browse docs in the sidebar
4. Check logs for system behavior
5. Read `docs/QUICKSTART_UI.md` for detailed usage

---

## Troubleshooting

**Issue: "ModuleNotFoundError"**  
→ Install dependencies: `pip install -r requirements.txt`

**Issue: "docs_pt folder not found"**  
→ The folder is now called `knowledge_base/` (no action needed)

**Issue: "LLM unavailable"**  
→ Set GEMINI_API_KEY in `.env` (optional, app works without it)

For more help, see `docs/TROUBLESHOOTING.md`

---

**Version:** 1.0 Production Ready  
**Last Updated:** 2026-11-15
