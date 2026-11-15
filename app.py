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
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 14px;
        line-height: 1.4;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        margin-left: 20px;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #666;
    }
    .refused-message {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .log-entry {
        font-size: 12px;
        padding: 8px;
        margin: 4px 0;
        border-radius: 4px;
        background-color: #f9f9f9;
        border-left: 3px solid #ddd;
        font-family: monospace;
    }
    .log-guardrail {
        border-left-color: #f44336;
        background-color: #ffebee;
    }
    .log-retrieval {
        border-left-color: #4caf50;
        background-color: #f1f8e9;
    }
    .log-answer {
        border-left-color: #2196f3;
        background-color: #e3f2fd;
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
    st.markdown("## ⚙️ Settings")

    # Mode selection
    mode = st.radio(
        "🔍 Select Mode:",
        options=["Retrieval Only", "RAG (with LLM)"],
        help="Retrieval Only: Fast, returns document chunks\nRAG: Slower, uses LLM for better filtering"
    )

    if mode == "RAG (with LLM)" and not st.session_state.llm_available:
        st.warning("⚠️ LLM is unavailable. Using Retrieval Only mode.")
        mode = "Retrieval Only"

    st.session_state.mode = mode

    # Display mode status
    if mode == "RAG (with LLM)":
        st.success("✓ RAG mode active (LLM enabled)")
    else:
        st.info("ℹ️ Retrieval Only mode")

# ============================================================================
# SIDEBAR: KNOWLEDGE BASE BROWSER
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.markdown("## 📚 Knowledge Base")

    docs_folder = Path("knowledge_base")

    if docs_folder.exists():
        doc_files = sorted(list(docs_folder.glob("*.md")) + list(docs_folder.glob("*.txt")))

        if doc_files:
            # File selector
            selected_file = st.selectbox(
                "📄 Browse documents:",
                options=[f.name for f in doc_files],
                help="Select a file to preview"
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
                st.caption(f"📊 Size: {file_size/1024:.1f} KB")
        else:
            st.info("No documents found in knowledge_base/")
    else:
        st.warning("knowledge_base/ folder not found")

# ============================================================================
# SIDEBAR: LOG VIEWER
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.markdown("## 📋 Recent Logs")

    logger = st.session_state.logger

    # Log type selector
    log_type = st.selectbox(
        "Filter logs:",
        options=["All", "Guardrail Blocks", "Retrieval", "Answers"],
        key="log_filter"
    )

    # Read logs
    log_files = {
        "guardrail": logger.guardrail_log,
        "retrieval": logger.retrieval_log,
        "answer": logger.retrieval_log,  # Answers go to retrieval_log
    }

    logs_to_show = []

    # Collect logs based on filter
    if log_type in ["All", "Guardrail Blocks"]:
        try:
            if os.path.exists(log_files["guardrail"]):
                with open(log_files["guardrail"], "r") as f:
                    for line in f:
                        if line.strip():
                            try:
                                record = json.loads(line)
                                logs_to_show.append(("guardrail", record))
                            except:
                                pass
        except:
            pass

    if log_type in ["All", "Retrieval", "Answers"]:
        try:
            if os.path.exists(log_files["retrieval"]):
                with open(log_files["retrieval"], "r") as f:
                    for line in f:
                        if line.strip():
                            try:
                                record = json.loads(line)
                                if log_type == "All" or log_type == "Retrieval" and record.get("event") in ["retrieval_hit", "retrieval_miss"]:
                                    logs_to_show.append(("retrieval", record))
                                elif log_type == "Answers" and record.get("event") == "answer_provided":
                                    logs_to_show.append(("answer", record))
                            except:
                                pass
        except:
            pass

    # Show last 10 logs
    if logs_to_show:
        logs_to_show = logs_to_show[-10:]  # Last 10

        for log_type_name, log_entry in reversed(logs_to_show):
            timestamp = log_entry.get("timestamp", "N/A")
            event = log_entry.get("event", "unknown")

            if log_type_name == "guardrail":
                reason = log_entry.get("reason", "")
                st.markdown(
                    f'<div class="log-entry log-guardrail">'
                    f'<strong>🛡️ {event}</strong><br/>'
                    f'{reason}<br/>'
                    f'<small>{timestamp}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            elif log_type_name == "retrieval":
                if event == "retrieval_hit":
                    filename = log_entry.get("filename", "?")
                    score = log_entry.get("score", "?")
                    st.markdown(
                        f'<div class="log-entry log-retrieval">'
                        f'<strong>✓ Hit</strong><br/>'
                        f'{filename} (score: {score})<br/>'
                        f'<small>{timestamp}</small>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    reason = log_entry.get("reason", "")
                    st.markdown(
                        f'<div class="log-entry log-retrieval">'
                        f'<strong>✗ Miss</strong><br/>'
                        f'{reason}<br/>'
                        f'<small>{timestamp}</small>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            elif log_type_name == "answer":
                st.markdown(
                    f'<div class="log-entry log-answer">'
                    f'<strong>💬 Answer</strong><br/>'
                    f'<small>{timestamp}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )
    else:
        st.caption("No logs yet")

# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================

st.markdown("# 💬 DocuBot FAQ Helper")
st.markdown("Ask questions about accounting procedures, tax info, and service fees.")

# Chat display area
chat_container = st.container()

with chat_container:
    for i, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]

        if role == "user":
            st.markdown(
                f'<div class="chat-message user-message">'
                f'<strong>You:</strong><br/>{content}'
                f'</div>',
                unsafe_allow_html=True
            )
        elif role == "refused":
            st.markdown(
                f'<div class="chat-message refused-message">'
                f'<strong>🛡️ Safety Check:</strong><br/>{content}'
                f'</div>',
                unsafe_allow_html=True
            )
        else:  # assistant
            st.markdown(
                f'<div class="chat-message assistant-message">'
                f'<strong>DocuBot:</strong><br/>{content}'
                f'</div>',
                unsafe_allow_html=True
            )

# Input area
st.markdown("---")

# Create columns for input and buttons
input_col, button_col = st.columns([4, 1])

with input_col:
    user_input = st.text_input(
        "Your question:",
        placeholder="Type your question here (e.g., 'What is the standard deduction?')",
        label_visibility="collapsed"
    )

with button_col:
    send_button = st.button("📤 Send", use_container_width=True)

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
                    if "I do not know" not in answer and "not covered" not in answer.lower():
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
