"""
starter_v0/app.py — Streamlit UI cho Research Agent Tool Eval (Lab 04 v2).

Tái sử dụng `run_model_tool_loop` từ `chat.py`, hiển thị chi tiết `rounds`, `tool_events`,
và lưu transcript theo yêu cầu nghiệm thu core của đề bài.

Chạy bằng lệnh:
    streamlit run starter_v0/app.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st

# Đường dẫn thư mục starter_v0
ROOT = Path(__file__).parent
sys.path.append(str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version
from chat import run_model_tool_loop, write_transcript, trim_history, now_iso

load_lab_env(ROOT)
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"

# Cấu hình Trang Streamlit
st.set_page_config(
    page_title="Research Agent Tool Eval — Lab 04 v2",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 1.2rem;
    }
    .badge-tool {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .tool-card {
        background-color: #0f172a;
        border-left: 3px solid #3b82f6;
        padding: 0.6rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        font-family: monospace;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SIDEBAR CONTROL PANEL
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Agent Controls")
    
    provider_name = st.selectbox(
        "AI Provider:",
        ["openrouter", "openai", "gemini", "anthropic"],
        index=0,
    )
    
    model_override = st.text_input("Model Name (tuỳ chọn):", value="", placeholder="Mặc định theo provider")
    
    version_label = st.selectbox(
        "Artifact Version Label:",
        ["v0", "v1", "v2", "v3"],
        index=0,
    )
    
    max_tool_rounds = st.slider("Max Tool Rounds:", min_value=1, max_value=10, value=5)
    history_window = st.slider("Context Pair Window:", min_value=1, max_value=10, value=5)

    st.markdown("---")
    st.markdown("### 📜 System Prompt & Tools")
    
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_yaml_path = ARTIFACTS_DIR / "tools.yaml"

    if system_prompt_path.exists():
        with st.expander("📄 system_prompt.md"):
            st.code(system_prompt_path.read_text(encoding="utf-8"), language="markdown")
            
    if tools_yaml_path.exists():
        with st.expander("🛠️ tools.yaml"):
            st.code(tools_yaml_path.read_text(encoding="utf-8"), language="yaml")


# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history_pairs" not in st.session_state:
    st.session_state.history_pairs = []

if "current_transcript" not in st.session_state:
    st.session_state.current_transcript = {
        "version": version_label,
        "created_at": now_iso(),
        "messages": [],
    }


# -----------------------------------------------------------------------------
# MAIN DASHBOARD UI
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">🔬 Day 04 — Research Agent Tool Eval</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Evidence-driven Agent Optimization & Multi-turn Tool Trace Inspection</div>', unsafe_allow_html=True)

tab_chat, tab_transcript, tab_info = st.tabs(["💬 Interactive Research Chat", "📑 Transcript & Logs", "ℹ️ Lab Info & Rubric"])

with tab_chat:
    # Action buttons
    col_clear, col_run_sample = st.columns([1, 4])
    if col_clear.button("🗑️ Xoá Chat History"):
        st.session_state.messages = []
        st.session_state.history_pairs = []
        st.session_state.current_transcript = {
            "version": version_label,
            "created_at": now_iso(),
            "messages": [],
        }
        st.rerun()

    # Display Chat Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            
            # Display Tool Events & Rounds if available
            if msg.get("rounds"):
                with st.expander("🔍 Executed Tool Traces (Rounds & Events)"):
                    for r in msg["rounds"]:
                        st.markdown(f"**Round {r.get('round')}** — Assistant Text: `{r.get('assistant_text')}`")
                        if r.get("tool_calls"):
                            st.markdown("**Called Tools:**")
                            for tc in r["tool_calls"]:
                                st.code(f"{tc['name']}({json.dumps(tc['args'], ensure_ascii=False)})", language="python")
                        if r.get("tool_results"):
                            st.markdown("**Tool Results:**")
                            for tr in r["tool_results"]:
                                st.json(tr)

    # Chat Input Box
    user_query = st.chat_input("Nhập yêu cầu nghiên cứu (vd: 'Tìm bài viết mới nhất của Sam Altman và tổng hợp')...")

    if user_query:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)

        # Prepare Provider & Loop Execution
        with st.spinner(f"Agent đang xử lý với provider '{provider_name}'..."):
            try:
                prov = make_provider(provider_name)
                sys_prompt_text = system_prompt_path.read_text(encoding="utf-8") if system_prompt_path.exists() else "You are a research assistant."
                declarations = load_tool_declarations(tools_yaml_path) if tools_yaml_path.exists() else []
                openai_tools = to_openai_tools(declarations)

                # Context Building
                context_messages = [{"role": "system", "content": sys_prompt_text}]
                context_messages.extend(trim_history(st.session_state.history_pairs, history_window))
                context_messages.append({"role": "user", "content": user_query})

                # Execute run_model_tool_loop
                loop_result = run_model_tool_loop(
                    provider=prov,
                    messages=context_messages,
                    tools=openai_tools,
                    model=model_override.strip() or None,
                    max_tool_rounds=max_tool_rounds,
                )

                assistant_reply = loop_result.get("assistant_text", "")
                
                # Append Assistant Message
                msg_entry = {
                    "role": "assistant",
                    "content": assistant_reply,
                    "status": loop_result.get("status"),
                    "rounds": loop_result.get("rounds"),
                    "tool_events": loop_result.get("tool_events"),
                }
                st.session_state.messages.append(msg_entry)

                # Update history pairs
                st.session_state.history_pairs.append({"role": "user", "content": user_query})
                st.session_state.history_pairs.append({"role": "assistant", "content": assistant_reply})

                # Save transcript
                artifact_ver = build_artifact_version(system_prompt_path, tools_yaml_path)
                transcript_data = {
                    "version": version_label,
                    "artifact_version": artifact_ver,
                    "updated_at": now_iso(),
                    "messages": st.session_state.messages,
                }
                transcript_file = TRANSCRIPTS_DIR / f"transcript_{version_label}.json"
                write_transcript(transcript_file, transcript_data)

                st.rerun()

            except Exception as e:
                st.error(f"Lỗi khi chạy Agent: {e}")

with tab_transcript:
    st.markdown("### 📑 Full Transcript & Run JSON Inspector")
    if st.session_state.messages:
        st.json(st.session_state.messages)
    else:
        st.info("Chưa có lượt hội thoại nào. Nhập câu hỏi để bắt đầu sinh transcript.")

with tab_info:
    st.markdown("### ℹ️ Thông Tin Lab 04 & Bảng Tiêu Chí")
    st.markdown("""
    - **Nhiệm vụ Core**: Tối ưu Research Agent qua các vòng `v0` ➔ `v3` bằng việc sửa `system_prompt.md` và `tools.yaml`.
    - **UI Contract**: Tái sử dụng `run_model_tool_loop`, soi chi tiết `rounds`/`tool_events` và lưu transcript JSON.
    """)
