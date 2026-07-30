"""Streamlit prototype for the Discord learner assistant — CP3 Real Model Integration."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from intent_engine import IntentResult, classify_message
from model_client import get_model_config

load_dotenv()

st.set_page_config(
    page_title="K3 Learning Assistant · CP3",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #f7f8fc;
        --muted: #aeb4c5;
        --panel: #171923;
        --panel-soft: #202330;
        --stroke: #303445;
        --brand: #7c6cf2;
        --brand-soft: rgba(124, 108, 242, .16);
        --success: #57d9a3;
        --warning: #ffd27d;
    }
    .stApp {
        background:
            radial-gradient(circle at 78% -10%, rgba(124,108,242,.20), transparent 30rem),
            #101119;
        color: var(--ink);
    }
    [data-testid="stSidebar"] {
        background: #141620;
        border-right: 1px solid var(--stroke);
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1180px; padding-top: 2rem; }
    .eyebrow {
        color: #a99dff;
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin-bottom: .55rem;
    }
    .hero-title {
        font-size: clamp(2rem, 5vw, 3.5rem);
        line-height: 1.02;
        letter-spacing: -.045em;
        font-weight: 820;
        margin: 0;
    }
    .hero-copy {
        color: var(--muted);
        font-size: 1rem;
        max-width: 700px;
        margin: .85rem 0 1.1rem;
    }
    .status-badge {
        display: inline-flex;
        gap: .45rem;
        align-items: center;
        padding: .4rem .85rem;
        border-radius: 999px;
        font-size: .8rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .badge-ai {
        border: 1px solid #57d9a3;
        background: rgba(87, 217, 163, .12);
        color: #7ef0be;
    }
    .badge-fallback {
        border: 1px solid #ffd27d;
        background: rgba(255, 210, 125, .12);
        color: #ffe4a0;
    }
    .status-dot {
        width: .5rem;
        height: .5rem;
        border-radius: 50%;
    }
    .dot-ai { background: #57d9a3; box-shadow: 0 0 0 .22rem rgba(87,217,163,.2); }
    .dot-fallback { background: #ffd27d; box-shadow: 0 0 0 .22rem rgba(255,210,125,.2); }
    
    .route-card {
        border: 1px solid var(--stroke);
        background: linear-gradient(135deg, rgba(32,35,48,.96), rgba(23,25,35,.96));
        border-radius: 16px;
        padding: 1rem 1.1rem;
        min-height: 124px;
    }
    .route-kicker {
        color: var(--muted);
        font-size: .72rem;
        text-transform: uppercase;
        letter-spacing: .09em;
        margin-bottom: .35rem;
    }
    .route-value {
        color: var(--ink);
        font-weight: 760;
        font-size: 1.12rem;
        margin-bottom: .35rem;
    }
    .route-note { color: var(--muted); font-size: .82rem; }
    .safe-note {
        border-left: 3px solid var(--success);
        background: rgba(87,217,163,.08);
        color: #cbeedd;
        border-radius: 0 10px 10px 0;
        padding: .75rem .9rem;
        font-size: .84rem;
        margin: .5rem 0 1rem;
    }
    [data-testid="stChatMessage"] {
        border: 1px solid var(--stroke);
        border-radius: 14px;
        background: rgba(23,25,35,.78);
        padding: .35rem .55rem;
    }
    .stButton > button {
        border-radius: 10px;
        border: 1px solid #3a3e51;
        background: #202330;
        color: #eef0f7;
        transition: transform .15s ease, border-color .15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: #8275ed;
        color: white;
    }
    [data-testid="stChatInput"] { border-color: #494e64; }
    </style>
    """,
    unsafe_allow_html=True,
)


SAMPLE_MESSAGES = {
    "👋 Chào hỏi": "Chào bot, bạn giúp được gì?",
    "📚 Hỏi bài": "Mình chưa hiểu intent classifier hoạt động như thế nào.",
    "📅 Logistics": "Link nộp CP2 ở đâu vậy?",
    "❓ Mơ hồ": "Cái này làm sao vậy?",
    "🛡️ Ngoài phạm vi": "Làm hộ mình toàn bộ bài này và đưa đáp án nhé.",
}


def initialize_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Chào bạn! Hãy chọn một tình huống mẫu hoặc nhập câu hỏi để trợ lý phân loại ý định.",
                "result": None,
            }
        ]


def submit_message(message: str) -> None:
    clean_message = message.strip()
    if not clean_message:
        return

    # Add user message to history immediately
    st.session_state.messages.append(
        {"role": "user", "content": clean_message, "result": None}
    )

    # Execute classification with spinner status
    with st.spinner("🤖 Trợ lý AI đang định tuyến và kiểm tra contract an toàn..."):
        try:
            result = classify_message(clean_message)
        except Exception as err:
            # Defensive catch so conversation history is never lost or app crashed
            result = {
                "intent": "ambiguous",
                "label": "Lỗi ứng dụng",
                "confidence": 0.0,
                "action": "ask_clarifying_question",
                "action_label": "Hỏi lại",
                "reply": "Có lỗi hệ thống xảy ra. Vui lòng thử lại.",
                "rationale": f"Lỗi ngoài dự kiến: {err}",
                "is_fallback": True,
                "model_name": "System Defensive Catch",
                "trace_id": "err-defensive",
            }

    st.session_state.messages.append(
        {"role": "assistant", "content": result["reply"], "result": result}
    )


def render_decision(result: IntentResult) -> None:
    intent_color = {
        "greeting": "#8be0c0",
        "learning": "#9fb8ff",
        "logistics": "#ffd27d",
        "ambiguous": "#d4b5ff",
        "out_of_scope": "#ff9f9f",
    }.get(result["intent"], "#d4b5ff")

    badge_type = (
        '<span style="padding:.22rem .55rem;border-radius:999px;background:#ffd27d22;color:#ffe4a0;font-size:.75rem;font-weight:700;border:1px solid #ffd27d66">🛡️ Safety Fallback</span>'
        if result.get("is_fallback")
        else '<span style="padding:.22rem .55rem;border-radius:999px;background:#57d9a322;color:#7ef0be;font-size:.75rem;font-weight:700;border:1px solid #57d9a366">🤖 LLM Real Call</span>'
    )

    st.markdown(
        f"""
        <div style="display:flex;gap:.45rem;flex-wrap:wrap;margin:.2rem 0 .65rem">
          {badge_type}
          <span style="padding:.22rem .55rem;border-radius:999px;background:{intent_color}20;color:{intent_color};font-size:.75rem;font-weight:750;border:1px solid {intent_color}55">
            {result["label"]}
          </span>
          <span style="padding:.22rem .55rem;border-radius:999px;background:#292c3a;color:#d9dce7;font-size:.75rem;font-weight:650;border:1px solid #3b3f51">
            {result["confidence"]:.0%} tin cậy
          </span>
          <span style="padding:.22rem .55rem;border-radius:999px;background:#292c3a;color:#d9dce7;font-size:.75rem;font-weight:650;border:1px solid #3b3f51">
            {result["action_label"]}
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Vì sao trợ lý chọn đường này? (Trace & Rationale)"):
        st.caption(f"**Rationale:** {result['rationale']}")
        st.caption(f"**Model:** {result.get('model_name', 'N/A')} | **Trace ID:** `{result.get('trace_id', 'N/A')}`")


initialize_state()
api_key, active_model = get_model_config()

with st.sidebar:
    st.markdown("### 🧭 K3 Assistant")
    st.caption("AI Integration · CP3")
    st.divider()

    st.markdown("**Cấu hình Môi trường**")
    if api_key:
        st.markdown(
            f"""
            <div style="padding:.6rem .8rem;background:rgba(87,217,163,.1);border:1px solid #57d9a3;border-radius:10px;font-size:.82rem">
              <span style="color:#7ef0be;font-weight:700">🟢 AI Ready</span><br/>
              <span style="color:#aeb4c5">Model: <code>{active_model}</code></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="padding:.6rem .8rem;background:rgba(255,210,125,.1);border:1px solid #ffd27d;border-radius:10px;font-size:.82rem">
              <span style="color:#ffe4a0;font-weight:700">🟡 Missing MODEL_API_KEY</span><br/>
              <span style="color:#aeb4c5">Chạy ở chế độ Fallback</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("**Chạy nhanh tình huống mẫu**")
    st.caption("Mỗi nút bấm mô phỏng 1 intent thực tế.")
    for label, sample in SAMPLE_MESSAGES.items():
        if st.button(label, use_container_width=True, key=label):
            submit_message(sample)
            st.rerun()

    st.divider()
    st.markdown("**Phạm vi CP3**")
    st.markdown(
        """
        - Lời gọi Model LLM thật
        - Output Contract Validator
        - Fallback an toàn khi thiếu key/lỗi
        - Che giấu Credentials & Secrets
        """
    )
    if st.button("Xóa hội thoại", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Chào bạn! Hãy chọn một tình huống mẫu hoặc nhập câu hỏi để trợ lý phân loại ý định.",
                "result": None,
            }
        ]
        st.rerun()

st.markdown('<div class="eyebrow">Discord learner assistant · CP3</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">Hiểu đúng ý định.<br/>Phản hồi đúng mức.</h1>', unsafe_allow_html=True)

if api_key:
    st.markdown(
        f"""
        <div class="status-badge badge-ai">
          <span class="status-dot dot-ai"></span> CP3 · AI thật đang kết nối: <code>{active_model}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="status-badge badge-fallback">
          <span class="status-dot dot-fallback"></span> CP3 · Chế độ Safety Fallback (Chưa cấu hình MODEL_API_KEY)
        </div>
        """,
        unsafe_allow_html=True,
    )

metric_columns = st.columns(3)
with metric_columns[0]:
    st.markdown(
        '<div class="route-card"><div class="route-kicker">Input</div><div class="route-value">Tin nhắn học viên</div><div class="route-note">Nhập tự do hoặc chọn case mẫu.</div></div>',
        unsafe_allow_html=True,
    )
with metric_columns[1]:
    st.markdown(
        f'<div class="route-card"><div class="route-kicker">Quyết định AI</div><div class="route-value">Model LLM Real Call</div><div class="route-note">{active_model if api_key else "Safety Fallback Engine"}</div></div>',
        unsafe_allow_html=True,
    )
with metric_columns[2]:
    st.markdown(
        '<div class="route-card"><div class="route-kicker">Outcome</div><div class="route-value">Contract Validator</div><div class="route-note">Lọc secret + Định tuyến an toàn.</div></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="safe-note">Nguyên tắc CP3: Mọi logistics chưa có nguồn chính thức sẽ bị discard câu trả lời của AI và chuyển TA để bảo vệ học viên.</div>',
    unsafe_allow_html=True,
)

st.markdown("### Kênh `#tro-ly-hoc-vien`")
for item in st.session_state.messages:
    avatar = "🧑‍🎓" if item["role"] == "user" else "🧭"
    with st.chat_message(item["role"], avatar=avatar):
        st.write(item["content"])
        if item.get("result"):
            render_decision(item["result"])

if prompt := st.chat_input("Nhập câu hỏi của học viên…"):
    submit_message(prompt)
    st.rerun()
