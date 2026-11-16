"""
Streamlit UI for DocuBot FAQ Helper.

Features:
- Chat-like interface for Q&A
- Knowledge base file browser/preview (right sidebar)
- Log viewer for tracking system behavior
- Real-time mode selection (Retrieval-only vs RAG)
"""

import streamlit as st
from pathlib import Path
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from docubot import DocuBot
from llm_client import GeminiClient
from guardrail import check_input_safety, get_safe_response
from logger import get_logger

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="DocuBot - FAQ Helper",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://streamlit.io',
        'Report a bug': None,
        'About': "DocuBot FAQ Helper v1.0"
    }
)

# Force dark theme for better visibility
import os
os.environ['STREAMLIT_CLIENT_THEME'] = 'dark'

# Custom CSS for better visibility and dark theme - ENHANCED FOR READABILITY
st.markdown("""
<style>
    * {
        color: #ffffff;
    }

    body, .stApp {
        background-color: #0f172a;
        color: #ffffff;
    }

    /* ===== MAIN HEADING ===== */
    h1 {
        font-size: 2.5em !important;
        color: #3b82f6 !important;
        margin-bottom: 8px !important;
    }

    h2 {
        font-size: 1.8em !important;
        color: #60a5fa !important;
        margin-top: 16px !important;
        margin-bottom: 12px !important;
    }

    h3 {
        font-size: 1.4em !important;
        color: #93c5fd !important;
    }

    p {
        font-size: 1.1em !important;
        line-height: 1.6 !important;
        color: #e2e8f0 !important;
    }

    /* ===== CHAT MESSAGES - MODERN CHAT BUBBLE STYLE ===== */
    .chat-container {
        display: flex;
        margin: 12px 0;
        width: 100%;
    }

    .chat-bubble-wrapper {
        display: flex;
        width: 100%;
        margin: 8px 0;
    }

    .chat-bubble-wrapper.user {
        justify-content: flex-end;
    }

    .chat-bubble-wrapper.assistant {
        justify-content: flex-start;
    }

    .chat-bubble {
        max-width: 85%;
        padding: 16px 20px;
        border-radius: 18px;
        font-size: 1.05em;
        line-height: 1.7;
        word-wrap: break-word;
    }

    .chat-bubble.user {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: #ffffff;
        border-radius: 18px 4px 18px 18px;
    }

    .chat-bubble.assistant {
        background-color: #1f2937;
        color: #e2e8f0;
        border: 1px solid #374151;
        border-radius: 4px 18px 18px 18px;
    }

    .chat-bubble.refused {
        background-color: #7c2d12;
        color: #fed7aa;
        border: 1px solid #b45309;
        border-radius: 4px 18px 18px 18px;
    }

    /* ===== KEYWORDS & EMPHASIS ===== */
    .keyword {
        font-weight: bold;
        font-size: 1.15em;
        color: #fbbf24;
        background-color: rgba(251, 191, 36, 0.15);
        padding: 2px 6px;
        border-radius: 4px;
    }

    .assistant .keyword {
        color: #fbbf24;
        background-color: rgba(251, 191, 36, 0.1);
    }

    .user-message {
        background-color: #1e3a8a;
        border-left: 6px solid #3b82f6;
        margin-left: 20px;
        color: #e0e7ff;
    }

    .user-message strong {
        font-size: 1.15em;
        color: #60a5fa;
    }

    .assistant-message {
        background-color: #1f2937;
        border-left: 6px solid #10b981;
        color: #d1d5db;
    }

    .assistant-message strong {
        font-size: 1.15em;
        color: #34d399;
    }

    .refused-message {
        background-color: #7c2d12;
        border-left: 6px solid #f97316;
        color: #fed7aa;
    }

    .refused-message strong {
        font-size: 1.15em;
        color: #fb923c;
    }

    /* ===== ANSWER CONTENT - MUCH LARGER ===== */
    .answer-content {
        font-size: 1.1em;
        line-height: 1.8;
        color: #e2e8f0;
        margin: 12px 0;
    }

    .answer-title {
        font-size: 1.2em;
        font-weight: bold;
        color: #34d399;
        margin-bottom: 8px;
    }

    .answer-value {
        font-size: 1.15em;
        font-weight: bold;
        color: #fbbf24;
        background-color: rgba(45, 212, 191, 0.1);
        padding: 6px 12px;
        border-radius: 6px;
        display: inline-block;
        margin: 4px 0;
    }

    .answer-table {
        font-size: 1.05em;
        margin: 12px 0;
    }

    .answer-table td, .answer-table th {
        padding: 12px;
        border: 1px solid #475569;
        color: #e2e8f0;
    }

    .answer-table th {
        background-color: #1e40af;
        font-weight: bold;
        color: #93c5fd;
        font-size: 1.08em;
    }

    .answer-table tr:nth-child(even) {
        background-color: #1f2937;
    }

    .answer-table tr:nth-child(odd) {
        background-color: #111827;
    }

    /* ===== SECTION HEADERS ===== */
    .section-header {
        font-size: 1.15em;
        font-weight: bold;
        color: #60a5fa;
        margin-top: 16px;
        margin-bottom: 8px;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 6px;
    }

    /* ===== BULLET POINTS ===== */
    ul, ol {
        font-size: 1.05em;
        margin-left: 20px;
        line-height: 1.8;
    }

    li {
        margin-bottom: 8px;
        color: #cbd5e1;
    }

    /* ===== LOGS ===== */
    .log-entry {
        font-size: 0.95em;
        padding: 10px;
        margin: 6px 0;
        border-radius: 6px;
        background-color: #1f2937;
        border-left: 4px solid #555;
        font-family: monospace;
        color: #d1d5db;
    }

    .log-guardrail {
        border-left-color: #ef4444;
        background-color: #5f2c2c;
    }

    .log-retrieval {
        border-left-color: #22c55e;
        background-color: #2d5a2d;
    }

    .log-answer {
        border-left-color: #3b82f6;
        background-color: #2d4a7d;
    }

    /* ===== FORM ELEMENTS ===== */
    [data-testid="stTextInput"] input {
        font-size: 1.05em !important;
        padding: 12px !important;
        height: 50px !important;
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border: 2px solid #475569 !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #9ca3af !important;
        font-size: 1.05em !important;
    }

    button {
        font-size: 1.05em !important;
        padding: 12px 20px !important;
        height: 50px !important;
    }

    /* ===== LABELS & CAPTIONS ===== */
    label {
        font-size: 1.08em !important;
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }

    .stCaption {
        font-size: 1em !important;
        color: #9ca3af !important;
    }

    /* ===== SELECTBOX & RADIO ===== */
    [data-testid="stSelectbox"] {
        font-size: 1.05em !important;
    }

    [role="radiogroup"] {
        font-size: 1.08em !important;
    }

    /* ===== MARKDOWN CONTAINER ===== */
    [data-testid="stMarkdownContainer"] {
        color: #ffffff;
        font-size: 1.05em;
    }

    /* ===== DIVIDER ===== */
    hr {
        border-color: #334155 !important;
    }

    /* ===== CODE BLOCKS ===== */
    code {
        font-size: 0.95em;
        background-color: #1f2937;
        color: #fbbf24;
        padding: 2px 6px;
        border-radius: 4px;
    }

    pre {
        background-color: #111827 !important;
        color: #d1d5db !important;
        font-size: 0.95em !important;
        padding: 16px !important;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
    }

    .sidebar-title {
        font-size: 1.2em !important;
        font-weight: bold !important;
        color: #60a5fa !important;
    }

    /* ===== ALERTS & INFO ===== */
    [data-testid="stAlert"] {
        font-size: 1.05em !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "llm_available" not in st.session_state:
    try:
        llm_client = GeminiClient()
        st.session_state.llm_available = True
        st.session_state.llm_client = llm_client
    except RuntimeError:
        st.session_state.llm_available = False
        st.session_state.llm_client = None

if "bot" not in st.session_state:
    bot = DocuBot(
        docs_folder="knowledge_base",
        llm_client=st.session_state.llm_client
    )
    st.session_state.bot = bot

if "logger" not in st.session_state:
    st.session_state.logger = get_logger()

# ============================================================================
# SIDEBAR: MODE SELECTION
# ============================================================================

with st.sidebar:
    st.markdown("<h2 style='font-size: 1.4em;'>⚙️ Settings</h2>", unsafe_allow_html=True)

    # Mode selection
    st.markdown("<div style='font-size: 1.1em; margin-bottom: 10px;'><strong>🔍 Select Mode:</strong></div>", unsafe_allow_html=True)
    mode = st.radio(
        "Mode",
        options=["Retrieval Only", "RAG (with LLM)"],
        help="Retrieval Only: Fast, returns document chunks\nRAG (with LLM): Uses AI for better formatting and clarity",
        label_visibility="collapsed"
    )

    if mode == "RAG (with LLM)" and not st.session_state.llm_available:
        st.warning("⚠️ LLM is unavailable. Using Retrieval Only mode.")
        mode = "Retrieval Only"

    st.session_state.mode = mode

    # Display mode status
    if mode == "RAG (with LLM)":
        st.success("✅ RAG mode active\n(AI-powered formatting)")
    else:
        st.info("ℹ️ Retrieval Only mode\n(Fast document search)")

# ============================================================================
# SIDEBAR: KNOWLEDGE BASE BROWSER
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.markdown("<h2 style='font-size: 1.4em;'>📚 Knowledge Base</h2>", unsafe_allow_html=True)

    docs_folder = Path("knowledge_base")

    if docs_folder.exists():
        doc_files = sorted(list(docs_folder.glob("*.md")) + list(docs_folder.glob("*.txt")))

        if doc_files:
            # File selector
            st.markdown("<div style='font-size: 1.05em; margin-bottom: 10px;'><strong>📄 Browse documents:</strong></div>", unsafe_allow_html=True)
            selected_file = st.selectbox(
                "Document",
                options=[f.name for f in doc_files],
                help="Select a file to preview",
                label_visibility="collapsed"
            )

            if selected_file:
                file_path = docs_folder / selected_file

                # Preview button
                if st.button("👁️ Preview", use_container_width=True):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Show preview in expander
                        with st.expander(f"📖 Preview: {selected_file}", expanded=True):
                            st.markdown(content[:2000])
                            if len(content) > 2000:
                                st.info(f"... (showing first 2000 chars, total: {len(content)})")
                    except Exception as e:
                        st.error(f"Error reading file: {e}")

                # File info
                file_size = file_path.stat().st_size
                st.markdown(f"<div style='font-size: 0.95em; color: #9ca3af;'>📊 Size: {file_size/1024:.1f} KB</div>", unsafe_allow_html=True)
        else:
            st.info("No documents found in knowledge_base/")
    else:
        st.warning("knowledge_base/ folder not found")

# ============================================================================
# SIDEBAR: LOG DOWNLOAD
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.markdown("<h2 style='font-size: 1.4em;'>📊 System Logs</h2>", unsafe_allow_html=True)

    logger = st.session_state.logger

    # Function to generate log file content
    def generate_log_file():
        """Compile all logs into a single text file"""
        log_content = []
        log_content.append("=" * 80)
        log_content.append("DOCUBOT SYSTEM LOGS")
        log_content.append(f"Generated: {datetime.now().isoformat()}")
        log_content.append("=" * 80)
        log_content.append("")

        # Guardrail logs
        if os.path.exists(logger.guardrail_log):
            log_content.append("\n" + "=" * 80)
            log_content.append("GUARDRAIL BLOCKS (Sensitive Data Detected)")
            log_content.append("=" * 80)
            try:
                with open(logger.guardrail_log, "r") as f:
                    for line in f:
                        if line.strip():
                            try:
                                record = json.loads(line)
                                log_content.append(f"\nTimestamp: {record.get('timestamp', 'N/A')}")
                                log_content.append(f"Reason: {record.get('reason', 'Unknown')}")
                                log_content.append(f"Query Preview: {record.get('query_preview', 'N/A')}")
                            except:
                                pass
            except:
                pass

        # Retrieval logs
        if os.path.exists(logger.retrieval_log):
            log_content.append("\n" + "=" * 80)
            log_content.append("RETRIEVAL & ANSWER LOGS")
            log_content.append("=" * 80)
            try:
                with open(logger.retrieval_log, "r") as f:
                    for line in f:
                        if line.strip():
                            try:
                                record = json.loads(line)
                                event = record.get("event", "unknown")
                                timestamp = record.get("timestamp", "N/A")

                                log_content.append(f"\n[{timestamp}] {event.upper()}")

                                if event == "retrieval_hit":
                                    log_content.append(f"  Query: {record.get('query', 'N/A')}")
                                    log_content.append(f"  Document: {record.get('filename', '?')}")
                                    log_content.append(f"  Score: {record.get('score', '?')}")

                                elif event == "retrieval_miss":
                                    log_content.append(f"  Query: {record.get('query', 'N/A')}")
                                    log_content.append(f"  Reason: {record.get('reason', 'Unknown')}")

                                elif event == "answer_provided":
                                    log_content.append(f"  Query: {record.get('query', 'N/A')[:100]}")
                                    log_content.append(f"  Answer: {record.get('answer', 'N/A')[:100]}")
                                    log_content.append(f"  Mode: {record.get('mode', 'N/A')}")

                                elif event == "user_feedback":
                                    log_content.append(f"  Query: {record.get('query', 'N/A')[:100]}")
                                    log_content.append(f"  Feedback: {'Helpful ✓' if record.get('helpful') else 'Not Helpful ✗'}")

                            except:
                                pass
            except:
                pass

        log_content.append("\n" + "=" * 80)
        log_content.append("END OF LOG FILE")
        log_content.append("=" * 80)

        return "\n".join(log_content)

    # Download button
    log_text = generate_log_file()
    st.download_button(
        label="📥 Download Logs (TXT)",
        data=log_text,
        file_name=f"docubot_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.caption("💡 Click to download all system logs as a text file for review and analysis.")

# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================

st.markdown("# 💬 DocuBot FAQ Helper")
st.markdown("Ask questions about accounting procedures, tax info, and service fees.")

# Chat display area
chat_container = st.container()

def highlight_keywords(content: str) -> str:
    """
    Highlight important keywords and numbers in the answer.
    Makes dollar amounts, key terms, and important concepts stand out.
    """
    import re

    # Dollar amounts like $31,500
    content = re.sub(
        r'\$(\d+,?\d*)',
        r'<span class="keyword">$\1</span>',
        content
    )

    # Numbers with specific context (age, percentages)
    content = re.sub(
        r'(\d+)\s*(year|age|percent|%)',
        r'<span class="keyword">\1 \2</span>',
        content,
        flags=re.IGNORECASE
    )

    # Key terms to highlight
    keywords = [
        'Married Filing Jointly',
        'Head of Household',
        'Single',
        'contribution limit',
        'deduction',
        'income requirement'
    ]

    for keyword in keywords:
        pattern = f'({re.escape(keyword)})'
        replacement = f'<span class="keyword">{keyword}</span>'
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

    return content

def format_answer(content: str) -> str:
    """Format answer for better readability with proper Markdown rendering"""
    # Process Markdown tables to make them more readable
    if "|" in content and "---" in content:
        # This is likely a Markdown table, keep as-is for Streamlit to render
        return content

    # Highlight keywords in regular text
    return highlight_keywords(content)

with chat_container:
    for i, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]

        if role == "user":
            # User message - RIGHT SIDE in blue bubble
            st.markdown(
                f'''
                <div class="chat-bubble-wrapper user">
                    <div class="chat-bubble user">
                        {content}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

        elif role == "refused":
            # Refused message (safety check) - LEFT SIDE in orange
            st.markdown(
                f'''
                <div class="chat-bubble-wrapper assistant">
                    <div class="chat-bubble refused">
                        <strong>🛡️ Safety Check:</strong><br/>{content}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

        else:  # assistant
            # Assistant message - LEFT SIDE in dark bubble
            formatted_content = format_answer(content)

            st.markdown(
                f'''
                <div class="chat-bubble-wrapper assistant">
                    <div class="chat-bubble assistant">
                        {formatted_content}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

            # COMMENTED OUT: Feedback buttons and modal feature (not working correctly)
            # TODO: Revisit this feature in future iterations

            # # Add "Clear Answer?" feedback button for the latest assistant message
            # if i == len(st.session_state.messages) - 1:
            #     st.markdown("---")
            #     col1, col2, col3 = st.columns([1, 1, 2])
            #
            #     with col1:
            #         if st.button("✅ Clear", key=f"clear_{i}", help="This answer is clear and helpful"):
            #             logger = st.session_state.logger
            #             query = st.session_state.messages[i-1]["content"] if i > 0 else ""
            #             # Log positive feedback
            #             logger.log_user_feedback(query, content, helpful=True)
            #             st.success("✅ Feedback recorded! Thank you.")
            #
            #     with col2:
            #         if st.button("❌ Not Clear", key=f"not_clear_{i}", help="Show original KB passages"):
            #             logger = st.session_state.logger
            #             query = st.session_state.messages[i-1]["content"] if i > 0 else ""
            #             # Log negative feedback
            #             logger.log_user_feedback(query, content, helpful=False)
            #
            #             # Retrieve original documents for fallback
            #             bot = st.session_state.bot
            #             retrieved_docs = bot.retrieve(query)
            #
            #             if retrieved_docs:
            #                 # Check if modal is open FIRST
            #                 if st.session_state.get("modal_open"):
            #                     modal_data = st.session_state.modal_content
            #
            #                     st.markdown("---")
            #                     st.markdown("### 📖 Full Document Viewer")
            #
            #                     # Back button
            #                     if st.button("← Back to Documents", key="back_to_list"):
            #                         st.session_state.modal_open = False
            #                         st.rerun()
            #
            #                     # Modal container
            #                     modal_col1, modal_col2, modal_col3 = st.columns([0.1, 3.8, 0.1])
            #
            #                     with modal_col2:
            #                         with st.container(border=True):
            #                             st.markdown(f"## 📄 {modal_data['filename']}")
            #                             st.divider()
            #                             st.markdown(modal_data['content'])
            #                             st.divider()
            #                             st.caption(f"📊 Document size: {len(modal_data['content'])} characters")
            #                 else:
            #                     # Show document list with previews
            #                     st.warning("❌ Showing original KB passages instead...")
            #                     st.markdown("### 📖 Original Knowledge Base Passages:")
            #
            #                     for idx, (filename, passage_text, meta) in enumerate(retrieved_docs):
            #                         col1, col2 = st.columns([4, 1])
            #
            #                         with col1:
            #                             # Show preview
            #                             preview = passage_text[:200] + "..." if len(passage_text) > 200 else passage_text
            #                             st.markdown(f"**📄 {filename}**")
            #                             st.caption(preview)
            #
            #                         with col2:
            #                             # View Full button
            #                             if st.button("📖 View", key=f"view_doc_{idx}"):
            #                                 st.session_state.modal_open = True
            #                                 st.session_state.modal_content = {
            #                                     "filename": filename,
            #                                     "content": passage_text,
            #                                     "meta": meta
            #                                 }
            #                                 st.rerun()
            #             else:
            #                 st.warning("No original KB passages found for this query.")

# Input area
st.markdown("---")

# Create columns for input and buttons
input_col, button_col = st.columns([4, 1])

with input_col:
    st.markdown("<div style='font-size: 1.15em; margin-bottom: 10px;'>💬 <strong>Ask your question:</strong></div>", unsafe_allow_html=True)
    user_input = st.text_input(
        "Your question:",
        placeholder="e.g., 'What is the standard deduction?' or 'IRA and 401k limits for married filing'",
        label_visibility="collapsed"
    )

with button_col:
    st.markdown("<div style='font-size: 0.9em; margin-bottom: 2px;'>&nbsp;</div>", unsafe_allow_html=True)
    send_button = st.button("📤 Send", use_container_width=True, key="send_button")

# ============================================================================
# PROCESS USER INPUT
# ============================================================================

if send_button and user_input:
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    logger = st.session_state.logger
    bot = st.session_state.bot

    # Check input safety
    is_safe, reason = check_input_safety(user_input)

    if not is_safe:
        # Guardrail triggered
        response = get_safe_response(reason)
        logger.log_guardrail_block(reason, user_input)

        st.session_state.messages.append({
            "role": "refused",
            "content": response
        })
    else:
        # Process with retrieval
        mode = st.session_state.mode

        with st.spinner("Processing your question..."):
            try:
                if mode == "RAG (with LLM)":
                    # RAG mode
                    answer = bot.answer_rag(user_input)
                    logger.log_answer(user_input, answer, "retrieval + LLM", mode="rag")
                else:
                    # Retrieval only mode
                    answer = bot.answer_retrieval_only(user_input)

                    # Log based on whether we got results
                    # Only check for "I do not know" - document content may legitimately contain "not covered"
                    if "I do not know" not in answer:
                        logger.log_retrieval_hit(user_input, "retrieved", 0.0)
                    else:
                        logger.log_retrieval_miss(user_input, "score below threshold")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
            except Exception as e:
                error_msg = f"Error processing question: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.error(error_msg)

    # Rerun to update chat display
    st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
    <p>💡 <strong>Tips:</strong> Ask about standard deductions, filing deadlines, fees, or procedures.</p>
    <p>🛡️ Your personal information (SSN, names) is protected.</p>
    <p>📊 All queries are logged for system improvement.</p>
</div>
""", unsafe_allow_html=True)
