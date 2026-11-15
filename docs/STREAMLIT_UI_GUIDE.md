# DocuBot Streamlit UI Guide

## Overview

This is a modern, web-based interface for the DocuBot FAQ helper. It provides:
- **Chat-like Q&A interface** - Familiar interaction pattern
- **Knowledge base browser** - Preview documents in the sidebar
- **Log viewer** - Monitor system behavior in real-time
- **Mode switcher** - Toggle between fast retrieval and intelligent RAG mode

## Quick Start

### Option 1: Batch File (Windows)
```bash
run_streamlit.bat
```

The app will open at `http://localhost:8501` automatically.

### Option 2: Command Line
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run Streamlit
streamlit run app.py
```

## UI Layout

```
┌─────────────────────────────────────────────────────┐
│                    SIDEBAR                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ⚙️ SETTINGS                                        │
│  ┌─────────────────────────────────────────────┐  │
│  │ Select Mode:                                │  │
│  │ ○ Retrieval Only                            │  │
│  │ ○ RAG (with LLM)                            │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  📚 KNOWLEDGE BASE                                 │
│  ┌─────────────────────────────────────────────┐  │
│  │ Browse documents:                           │  │
│  │ [Select file dropdown  ▼]                   │  │
│  │                                             │  │
│  │ [👁️ Preview Button]                        │  │
│  │                                             │  │
│  │ 📊 Size: 12.5 KB                           │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  📋 RECENT LOGS                                    │
│  ┌─────────────────────────────────────────────┐  │
│  │ Filter logs:                                │  │
│  │ [All ▼]                                     │  │
│  │                                             │  │
│  │ 🛡️ SSN detected (2026-11-15 10:30:00)      │  │
│  │ ✓ Hit: fees_2026.md (2026-11-15 10:29:00)  │  │
│  │ ✗ Miss: score too low (2026-11-15 10:28:00)│  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
                         │
                         │
┌─────────────────────────┴──────────────────────────┐
│            MAIN CHAT AREA (70% width)              │
├───────────────────────────────────────────────────┤
│                                                   │
│ 💬 DocuBot FAQ Helper                            │
│ Ask questions about accounting procedures, tax  │
│ info, and service fees.                         │
│                                                   │
│ ┌───────────────────────────────────────────────┐ │
│ │ You:                                          │ │
│ │ "What is the standard deduction?"             │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│ ┌───────────────────────────────────────────────┐ │
│ │ DocuBot:                                      │ │
│ │ For tax year 2025, the standard deduction... │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│ ┌───────────────────────────────────────────────┐ │
│ │ You:                                          │ │
│ │ "How do I depreciate office furniture?"      │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│ ┌───────────────────────────────────────────────┐ │
│ │ 🛡️ Safety Check:                             │ │
│ │ Not covered, ask your supervisor.            │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
├───────────────────────────────────────────────────┤
│ Your question:                                    │
│ [________________________________________________] │
│                                                📤 │
│                                              Send │
└───────────────────────────────────────────────────┘
```

## Features

### 1. 🔍 Mode Selection

**Retrieval Only**
- ⚡ Fast response (< 1 second)
- 📊 Returns document chunks directly
- 🎯 Good for quick lookups

**RAG (with LLM)**
- 🧠 Intelligent filtering
- ⚠️ Slower (2-5 seconds)
- 🎯 Better accuracy, fewer false positives
- 💡 Requires GEMINI_API_KEY

### 2. 📚 Knowledge Base Browser

**Features:**
- Browse all documents in `docs_pt/` folder
- Preview files with scrollable content
- See file size and modification date
- Markdown formatting preserved

**How to use:**
1. Select a file from the dropdown
2. Click "Preview" button
3. Content opens in an expandable section
4. First 2000 characters shown (with indicator if longer)

### 3. 📋 Log Viewer

**Log Types:**

| Icon | Type | Color | Meaning |
|------|------|-------|---------|
| 🛡️ | Guardrail Block | Red | Input blocked (SSN/EIN/name detected) |
| ✓ | Retrieval Hit | Green | Document chunk retrieved successfully |
| ✗ | Retrieval Miss | Green | No relevant document found |
| 💬 | Answer | Blue | LLM generated an answer |

**Filters:**
- **All** - Show all log types
- **Guardrail Blocks** - Security events only
- **Retrieval** - Document retrieval only
- **Answers** - LLM responses only

**Info shown:**
- Timestamp
- Event type and reason
- File retrieved (for hits)
- Score (for retrieval events)

### 4. 💬 Chat Interface

**Message types:**

| Type | Style | Example |
|------|-------|---------|
| User | Blue background | "What is the fee?" |
| Assistant | Gray background | "According to the 2026 fee schedule..." |
| Refused | Yellow background | "Not covered, ask your supervisor." |

**Features:**
- Scrollable message history
- Clear visual distinction between roles
- Automatic message accumulation (session persists)
- Real-time log updates

## Message Flow

```
User types question
        ↓
[Validate input]
        ↓
    Safe?
   /      \
  No       Yes
  │         │
[Log]    [Retrieve]
  │         │
[Show]  [Got text?]
Refusal  /       \
        Yes      No
        │         │
    [LLM?]    [Refuse]
    /    \      │
   Yes   No   [Show]
   │      │
[LLM]  [Show]
Filter  Text
   │      │
[Show]   └─ Both show in chat
Answer    Both log events
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Submit query (when focus in text box) |
| `Tab` | Navigate between UI elements |
| `Escape` | Close expanders/dialogs |

## Tips & Tricks

### For Staff Members

1. **Quick lookups**: Use Retrieval Only mode for fast answers
2. **Complex questions**: Switch to RAG mode for better filtering
3. **Browse docs**: Check sidebar to see available documents
4. **Check logs**: Monitor recent logs to understand system behavior

### For System Administrators

1. **Logs location**: `guardrail_blocks.jsonl`, `retrieval_results.jsonl`
2. **Clear logs**: Delete JSONL files in project root (logs regenerate)
3. **Monitor security**: Check guardrail logs for blocked queries
4. **Analyze failures**: Review retrieval_misses to improve knowledge base

## Troubleshooting

### Problem: "LLM unavailable" message

**Cause**: `GEMINI_API_KEY` not found in `.env` file

**Solution**:
```
# In .env file (root directory)
GEMINI_API_KEY=your_api_key_here
```

**Workaround**: Use Retrieval Only mode (doesn't need API key)

### Problem: App crashes on startup

**Cause**: Missing dependencies

**Solution**:
```bash
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problem: Knowledge base folder not found

**Cause**: `docs_pt/` directory doesn't exist

**Solution**: Run `prepare_docs.py` to generate documents from Word/PDF files
```bash
python prepare_docs.py
```

### Problem: No logs showing

**Cause**: This is normal on first startup

**Solution**: Ask a question to generate logs. Logs update automatically.

## Customization

### Change Page Title/Icon
Edit `app.py` line 16:
```python
st.set_page_config(
    page_title="My FAQ Helper",  # Change this
    page_icon="❓",  # Change this
    ...
)
```

### Change Colors
Edit CSS in `app.py` (lines 26-47):
```css
.user-message {
    background-color: #your_color;
    border-left: 4px solid #your_border;
}
```

### Add Custom Instructions
Edit markdown text in `app.py`:
```python
st.markdown("Your custom instructions here")
```

## Performance Notes

| Operation | Time | Notes |
|-----------|------|-------|
| Retrieval Only | 0.5s | Fast, local operation |
| RAG (LLM) | 2-5s | Depends on API latency |
| Document Preview | 0.1s | Instant for small files |
| Log Load | 0.1s | Depends on log size |

For production use with frequent queries, consider:
- Caching LLM responses
- Batch processing queries
- Archiving old logs

## File Structure

```
project/
├── app.py                      ← Streamlit app (this UI)
├── run_streamlit.bat           ← Quick launcher
├── STREAMLIT_UI_GUIDE.md       ← This file
├── docubot.py                  ← Retrieval engine
├── llm_client.py               ← LLM integration
├── guardrail.py                ← Input validation
├── logger.py                   ← Logging system
├── docs_pt/                    ← Knowledge base (markdown files)
└── .env                        ← API keys (GEMINI_API_KEY)
```

## Architecture

```
┌─────────────────────────────────────────┐
│        Streamlit Web Interface          │
│  (Chat, Sidebar, Log Viewer)            │
└──────────────┬──────────────────────────┘
               │
       ┌───────┼───────┐
       │       │       │
   ┌───▼───┐ ┌─▼──┐ ┌──▼────┐
   │Guardrail │ Bot │ Logger │
   │          │     │        │
   └───┬───┘ └─┬──┘ └──┬────┘
       │       │       │
   ┌───▼───────▼───────▼───┐
   │   Docs + LLM + Logs    │
   │   (File System)        │
   └────────────────────────┘
```

## Security

✅ **Enabled protections:**
- SSN detection (XXX-XX-XXXX)
- EIN detection (XX-XXXXXXX)
- Name detection (capitalized names with context)
- Query logging (for audit)

⚠️ **Remember:**
- Logs are not encrypted (store securely)
- API key in `.env` should be protected
- Don't share logs with sensitive data

## Support

For issues:
1. Check logs in sidebar
2. Run verification script: `python verify_step3_critical.py`
3. Review STEP3_SUMMARY.md for technical details
4. Check main.py and app.py for error messages
