"""
starter_v0/app.py — Streamlit UI Research Studio Edition (Lab 04 v2).

Tái sử dụng `run_model_tool_loop` từ `chat.py`, hiển thị chi tiết `rounds`, `tool_events`,
và lưu transcript theo yêu cầu nghiệm thu core của đề bài.

Chạy bằng lệnh:
    streamlit run starter_v0/app.py
"""

from __future__ import annotations

import base64
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
    page_title="Research Studio — Lab 04 Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling Cyber Dark Mode Chuẩn Đẹp Hài Hòa Cho Cả 2 Chế Độ
st.markdown("""
<style>
    /* Dark Theme Default Settings */
    .stApp {
        background-color: #090d16;
        color: #f1f5f9;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }
    .welcome-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .status-badge-success {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(16, 185, 129, 0.3);
        display: inline-block;
        margin-top: 0.4rem;
    }
    .status-badge-waiting {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(245, 158, 11, 0.3);
        display: inline-block;
        margin-top: 0.4rem;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(148, 163, 184, 0.1);
    }

    /* BONG BÓNG CHÁT CĂN LỀ 2 BÊN HÀI HOÀ */
    .user-align-wrapper [data-testid="stChatMessage"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border-radius: 18px 18px 2px 18px !important;
        border: 1px solid #38bdf8 !important;
    }
    .agent-align-wrapper [data-testid="stChatMessage"] {
        background-color: #1e293b !important;
        border: 1px solid rgba(168, 85, 247, 0.45) !important;
        color: #f8fafc !important;
        border-radius: 18px 18px 18px 2px !important;
    }

    /* FIX CHO BẢNG BIỂU HIỂN THỊ RÕ RÀNG */
    .stTable {
        background-color: #0f172a !important;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SIDEBAR CONTROL PANEL
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🤖 Research Agent Studio")
    st.markdown("---")
    
    st.markdown("#### ⚙️ Cấu Hình Hệ Thống")
    provider_raw = st.selectbox(
        "AI Provider:",
        ["openrouter", "mock (offline demo)", "openai", "gemini", "anthropic"],
        index=0,
        help="Chọn OpenRouter để dùng API Key thực tế của bạn, hoặc chọn 'mock (offline demo)' để chạy thử không tốn key."
    )
    provider_name = provider_raw.split()[0]
    
    model_override = st.text_input("Model Name (tuỳ chọn):", value="", placeholder="Mặc định: openai/gpt-4o-mini")
    
    version_label = st.selectbox(
        "Artifact Version Label:",
        ["v3", "v2", "v1", "v0"],
        index=0,
        help="v3 là phiên bản hoàn thiện nhất đạt 100% độ chính xác."
    )
    
    max_tool_rounds = st.slider("Max Tool Rounds:", min_value=1, max_value=10, value=5)
    history_window = st.slider("Context Pair Window:", min_value=1, max_value=10, value=5)

    st.markdown("---")
    st.markdown("#### 📜 System Prompt & Tools")
    
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


# -----------------------------------------------------------------------------
# MAIN DASHBOARD HEADER & KPI METRIC CARDS
# -----------------------------------------------------------------------------
st.markdown('<div class="hero-title">🤖 Research Agent Studio</div>', unsafe_allow_html=True)

# Executive KPI Metrics Cards
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
col_kpi1.metric("Active Version", f"Bản {version_label}", delta="Tối ưu nhất" if version_label == "v3" else None)
col_kpi2.metric("Pass Rate (Accuracy)", "100%", delta="⚡ +30% vs v0")
col_kpi3.metric("Registered Tools", "11 Tools", delta="1 Tool Mới (tech_news)")
col_kpi4.metric("Provider Engine", provider_name.upper(), delta="Live OpenRouter Key" if provider_name != "mock" else "Offline Mock Mode")

st.markdown("---")

tab_chat, tab_transcript, tab_comparison, tab_authors, tab_info = st.tabs([
    "💬 Research Chat", 
    "📑 Transcript & Logs", 
    "📊 Version Progress (v0 ➔ v3)", 
    "👥 Tác Giả & Phân Công",
    "ℹ️ Lab Info & Rubric"
])

with tab_chat:
    # Load custom avatar image for Welcome Hero Card
    domixi_img_path = ARTIFACTS_DIR / "domixi.png"
    if domixi_img_path.exists():
        b64_str = base64.b64encode(domixi_img_path.read_bytes()).decode("utf-8")
        domixi_avatar_html = f'<img src="data:image/png;base64,{b64_str}" style="width: 75px; height: 75px; border-radius: 50%; object-fit: cover; border: 3px solid #38bdf8; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);" />'
    else:
        domixi_avatar_html = '<span style="font-size:3rem;">👋</span>'

    # If Chat is empty, render ChatGPT Welcome Hero & Prompt Cards Grid
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="welcome-card" style="display: flex; align-items: center; gap: 1.2rem;">
            <div>{domixi_avatar_html}</div>
            <div>
                <h2 style="margin:0; color:#38bdf8;">Alo Vũ à Vũ! Tôi là Trợ lý Nghiên cứu AI (Research Agent v3)</h2>
    
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 💡 Gợi ý câu hỏi thử nghiệm (Bấm 1-Click để chát ngay):")
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    preset_query = None
    
    if col_p1.button("📰 Tin AI & OpenAI", use_container_width=True):
        preset_query = "Tìm tin tức mới nhất về OpenAI và Sam Altman trên mạng xã hội"
    if col_p2.button("👤 Posts @samaltman", use_container_width=True):
        preset_query = "Xem các bài đăng gần đây của tài khoản samaltman"
    if col_p3.button("📄 Bài báo arXiv AI", use_container_width=True):
        preset_query = "Tìm bài báo khoa học mới về Transformer và LLM trên arXiv"
    if col_p4.button("⚡ Tech News Hot", use_container_width=True):
        preset_query = "Tra cứu tin tức công nghệ mới nhất hôm nay"

    col_p5, col_p6, col_p7, col_p8 = st.columns(4)
    if col_p5.button("❓ Thiếu Info (Clarify)", use_container_width=True):
        preset_query = "Tổng hợp bài viết của tác giả này"
    if col_p6.button("📤 Gửi Telegram (Bound)", use_container_width=True):
        preset_query = "Gửi bản tổng hợp tin tức này lên kênh Telegram"
    if col_p7.button("🔒 Quy định Công ty", use_container_width=True):
        preset_query = "Chính sách công ty về data privacy quy định thế nào?"
    if col_p8.button("🗑️ Xoá Lịch Sử Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history_pairs = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # STREAMLIT COLUMNS SPLIT: USER ON RIGHT (COL 2), AGENT ON LEFT (COL 1)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            # USER MESSAGE — ALIGNED TO RIGHT COLUMN (XANH DƯƠNG)
            c_space, c_user = st.columns([1, 4])
            with c_user:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #0284c7, #2563eb); color: #ffffff; padding: 1rem 1.4rem; border-radius: 18px 18px 4px 18px; margin-bottom: 1rem; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);">
                    <div style="font-size: 0.75rem; font-weight: 800; color: #e0f2fe; text-align: right; margin-bottom: 0.3rem; letter-spacing: 0.5px;">👤 YOU</div>
                    <div style="font-size: 0.98rem; line-height: 1.5;">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # AGENT MESSAGE — ALIGNED TO LEFT COLUMN (TÍM CYBER GLASS)
            c_agent, c_space2 = st.columns([4, 1])
            with c_agent:
                status_html = ""
                if msg.get("status") == "success":
                    status_html = '<div style="margin-top:0.4rem;"><span class="status-badge-success">🟢 COMPLETED (AGENT SUCCESS)</span></div>'
                elif msg.get("status") == "waiting_for_user":
                    status_html = '<div style="margin-top:0.4rem;"><span class="status-badge-waiting">🟡 AWAITING USER INPUT (CLARIFICATION / CONFIRMATION)</span></div>'

                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e1b4b, #0f172a); border: 1px solid rgba(168, 85, 247, 0.45); color: #f8fafc; padding: 1.1rem 1.4rem; border-radius: 18px 18px 18px 4px; margin-bottom: 0.5rem; box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5);">
                    <div style="font-size: 0.75rem; font-weight: 800; color: #c084fc; text-align: left; margin-bottom: 0.3rem; letter-spacing: 0.5px;">🤖 AGENT RESEARCH AI</div>
                    <div style="font-size: 0.98rem; line-height: 1.5;">{msg['content']}</div>
                    {status_html}
                </div>
                """, unsafe_allow_html=True)

                # Display Tool Events & Rounds inside expander directly under Agent card
                if msg.get("rounds"):
                    with st.expander("🔍 Executed Tool Traces (Soi chi tiết AI gọi Tool)"):
                        for r in msg["rounds"]:
                            st.markdown(f"**Round {r.get('round')}** — Assistant Text: `{r.get('assistant_text')}`")
                            if r.get("tool_calls"):
                                st.markdown("**Tool Call (Lệnh AI phát ra):**")
                                for tc in r["tool_calls"]:
                                    st.code(f"{tc['name']}({json.dumps(tc['args'], ensure_ascii=False)})", language="python")
                            if r.get("tool_results"):
                                st.markdown("**Tool Results (Kết quả Tool trả về):**")
                                for tr in r["tool_results"]:
                                    st.json(tr)

    # Chat Input Box ChatGPT Style
    typed_query = st.chat_input("Nhập yêu cầu nghiên cứu của bạn ở đây (vd: 'Tìm bài báo arXiv về DeepSeek')...")
    user_query = preset_query or typed_query

    if user_query:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": user_query})

        # Prepare Provider & Loop Execution
        with st.spinner(f"🧠 Agent AI đang suy nghĩ và thực thi các Tool với provider '{provider_name}'..."):
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

                # Save transcript according to top-level schema contract
                art_obj = build_artifact_version(version_label, system_prompt_path, tools_yaml_path)
                
                all_events = []
                for m in st.session_state.messages:
                    if isinstance(m, dict) and m.get("tool_events"):
                        all_events.extend(m["tool_events"])

                transcript_data = {
                    "version": art_obj.version,
                    "artifact_version": art_obj.artifact_version,
                    "prompt_hash": art_obj.prompt_hash,
                    "tools_hash": art_obj.tools_hash,
                    "updated_at": now_iso(),
                    "turns": st.session_state.messages,
                    "messages": st.session_state.messages,
                    "tool_events": all_events,
                }
                transcript_file = TRANSCRIPTS_DIR / f"transcript_{version_label}.json"
                write_transcript(transcript_file, transcript_data)

                st.rerun()

            except Exception as e:
                err_str = str(e)
                if "Missing API key env var" in err_str:
                    st.warning(
                        "⚠️ **THIẾU API KEY CHO AI PROVIDER ĐÃ CHỌN!**\n\n"
                        f"Chi tiết lỗi: `{err_str}`\n\n"
                        "💡 **Cách khắc phục:**\n"
                        "1. **Cách 1 (Chạy Offline)**: Chọn Provider là **`mock (offline demo)`** ở thanh Sidebar bên trái để chạy thử ngay không cần API key.\n"
                        "2. **Cách 2 (Chạy API Thật)**: Mở file `starter_v0/.env` trên máy bạn và dán API Key (vd: `OPENROUTER_API_KEY=...` hoặc `GEMINI_API_KEY=...`)."
                    )
                else:
                    st.error(f"Lỗi khi chạy Agent: {e}")

with tab_transcript:
    st.markdown("### 📑 Full Transcript & Run JSON Inspector")
    if st.session_state.messages:
        st.json(st.session_state.messages)
    else:
        st.info("Chưa có lượt hội thoại nào. Nhập câu hỏi để bắt đầu sinh transcript.")

with tab_comparison:
    st.markdown("### 📊 Tiến Trình Tối Ưu Phiên Bản (Evidence-driven Progress)")
    st.markdown("Dưới đây là kết quả đánh giá thực tế thu nạp từ log qua từng vòng tối ưu `v0` ➔ `v3`:")
    
    st.table([
        {"Version": "v0 (Baseline)", "Metric": "Base Case Accuracy", "Before": "0.00", "After": "0.70 (70%)", "Cải tiến chính": "Khởi đầu mặc định (bị lỗi guessing tham số)"},
        {"Version": "v1 (Clarification)", "Metric": "Base Case Accuracy", "Before": "0.70", "After": "1.00 (100%)", "Cải tiến chính": "Bổ sung quy tắc clarify vắng URL/handle & Confirmation boundary"},
        {"Version": "v2 (Tool Routing)", "Metric": "Base Case Accuracy", "Before": "1.00", "After": "1.00 (100%)", "Cải tiến chính": "Tối ưu mô tả tools.yaml & phân định rõ timeline vs social_search"},
        {"Version": "v3 (Final Group)", "Metric": "Group Case Accuracy", "Before": "1.00", "After": "1.00 (100%)", "Cải tiến chính": "Hoàn thiện 100% cho 10 test cases nhóm (Single-turn & Multi-turn)"},
    ])

with tab_authors:
    st.markdown("### 👥 Tác Giả & Phân Công Đầu Việc Qua Các Phiên Bản")
    st.markdown("Bảng phân công chi tiết công việc và đóng góp cải tiến của từng thành viên:")
    
    st.table([
        {
            "Thành viên": "Nguyễn Tuấn Vũ (MSSV: 2A202601845)",
            "Vai trò": "Trưởng nhóm / UI & Report Lead",
            "Phiên bản": "v0 ➔ v3",
            "Đầu việc đơn giản": "Xây dựng Streamlit UI (app.py), cấu hình API Key, chuẩn hóa schema transcript JSON và hoàn thiện báo cáo REPORT.md.",
            "Cải tiến qua từng bản": "Tạo UI Streamlit tái sử dụng run_model_tool_loop, bổ sung Presets 1-Click, xử lý lỗi API Key và căn lề 2 bên 2 màu."
        },
        {
            "Thành viên": "Nguyễn Phúc Hưng (MSSV: 2A202601115)",
            "Vai trò": "Prompt & Policy Engineer",
            "Phiên bản": "v1, v2, v3",
            "Đầu việc đơn giản": "Chỉnh sửa system_prompt.md thiết lập quy tắc tư duy, clarify boundary và từ chối ngoài phạm vi.",
            "Cải tiến qua từng bản": "• v1: Thêm clarify khi vắng handle/URL.\n• v2: Routing timeline vs social_search.\n• v3: Confirmation boundary cho Telegram."
        },
        {
            "Thành viên": "Nguyễn Văn Phong (MSSV: 2A202601087)",
            "Vai trò": "Tool Developer",
            "Phiên bản": "v0 ➔ v2",
            "Đầu việc đơn giản": "Phát triển Tool mới tech_news và khai báo chuẩn hóa schema trong tools.yaml.",
            "Cải tiến qua từng bản": "• v0: Tạo mã nguồn get_tech_news (Hacker News API).\n• v2: Chuẩn hóa tham số (mode, limit, query) giải quyết lỗi wrong_arg_value."
        },
        {
            "Thành viên": "Nguyễn Hữu Khánh Tùng (MSSV: 2A202601781)",
            "Vai trò": "Eval & QA Lead",
            "Phiên bản": "v0 ➔ v3",
            "Đầu việc đơn giản": "Viết bộ 10 test cases nhóm (eval_group.json) và chạy benchmark đo số liệu qua các bản.",
            "Cải tiến qua từng bản": "• v0: Thu log baseline (70%).\n• v1: Đánh giá v1 đạt 100% base.\n• v3: Đánh giá v3 đạt 100% Pass Rate trên cả 10 cases nhóm."
        }
    ])

with tab_info:
    st.markdown("### ℹ️ Thông Tin Lab 04 & Bảng Tiêu Chí")
    st.markdown("""
    - **Nhiệm vụ Core**: Tối ưu Research Agent qua các vòng `v0` ➔ `v3` bằng việc sửa `system_prompt.md` và `tools.yaml`.
    - **UI Contract**: Tái sử dụng `run_model_tool_loop`, soi chi tiết `rounds`/`tool_events` và lưu transcript JSON.
    """)
