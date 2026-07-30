"""Streamlit prototype for the Discord learner assistant — CP2."""

from __future__ import annotations

import streamlit as st

from intent_engine import IntentResult, classify_message


st.set_page_config(
    page_title="K3 Learning Assistant · CP2",
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
    .mock-badge {
        display: inline-flex;
        gap: .45rem;
        align-items: center;
        padding: .4rem .7rem;
        border: 1px solid #514a82;
        border-radius: 999px;
        background: var(--brand-soft);
        color: #d8d3ff;
        font-size: .78rem;
        font-weight: 700;
    }
    .mock-dot {
        width: .46rem;
        height: .46rem;
        border-radius: 50%;
        background: #aa9eff;
        box-shadow: 0 0 0 .22rem rgba(170,158,255,.13);
    }
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
                "content": "Chào bạn! Hãy chọn một tình huống mẫu hoặc nhập câu hỏi để xem trợ lý định tuyến.",
                "result": None,
            }
        ]


def submit_message(message: str) -> None:
    clean_message = message.strip()
    if not clean_message:
        return
    result = classify_message(clean_message)
    st.session_state.messages.append(
        {"role": "user", "content": clean_message, "result": None}
    )
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
    }[result["intent"]]
    st.markdown(
        f"""
        <div style="display:flex;gap:.45rem;flex-wrap:wrap;margin:.2rem 0 .65rem">
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
    with st.expander("Vì sao trợ lý chọn đường này?"):
        st.caption(result["rationale"])


initialize_state()

with st.sidebar:
    st.markdown("### 🧭 K3 Assistant")
    st.caption("Clickable prototype · CP2")
    st.divider()
    st.markdown("**Chạy nhanh một tình huống**")
    st.caption("Mỗi nút đi hết một đường trải nghiệm.")
    for label, sample in SAMPLE_MESSAGES.items():
        if st.button(label, use_container_width=True, key=label):
            submit_message(sample)
            st.rerun()
    st.divider()
    st.markdown("**Phạm vi bản này**")
    st.markdown(
        """
        - Phân loại 5 nhóm intent
        - Hỏi lại khi mơ hồ
        - Chuyển TA khi thiếu nguồn
        - Không dùng dữ liệu thật
        """
    )
    if st.button("Xóa hội thoại", use_container_width=True):
        del st.session_state.messages
        st.rerun()

st.markdown('<div class="eyebrow">Discord learner assistant</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">Hiểu đúng ý định.<br/>Phản hồi đúng mức.</h1>', unsafe_allow_html=True)
st.markdown(
    """
    <p class="hero-copy">
      Prototype minh họa cách trợ lý nhận diện câu hỏi của học viên và chọn giữa
      trả lời, hỏi lại, từ chối hoặc chuyển TA — trước khi kết nối AI thật ở CP3.
    </p>
    <span class="mock-badge"><span class="mock-dot"></span> CP2 · Logic đang mock có chủ đích</span>
    """,
    unsafe_allow_html=True,
)

st.write("")
metric_columns = st.columns(3)
with metric_columns[0]:
    st.markdown(
        '<div class="route-card"><div class="route-kicker">Input</div><div class="route-value">Tin nhắn học viên</div><div class="route-note">Nhập tự do hoặc chọn case mẫu.</div></div>',
        unsafe_allow_html=True,
    )
with metric_columns[1]:
    st.markdown(
        '<div class="route-card"><div class="route-kicker">Quyết định trung tâm</div><div class="route-value">Phân loại intent</div><div class="route-note">5 nhãn cùng mức tin cậy mô phỏng.</div></div>',
        unsafe_allow_html=True,
    )
with metric_columns[2]:
    st.markdown(
        '<div class="route-card"><div class="route-kicker">Outcome</div><div class="route-value">Định tuyến an toàn</div><div class="route-note">Trả lời · hỏi lại · chuyển TA.</div></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="safe-note">Nguyên tắc CP2: logistics chưa có nguồn chính thức sẽ được chuyển TA, không tạo câu trả lời đoán.</div>',
    unsafe_allow_html=True,
)

st.markdown("### Kênh `#tro-ly-hoc-vien`")
for item in st.session_state.messages:
    avatar = "🧑‍🎓" if item["role"] == "user" else "🧭"
    with st.chat_message(item["role"], avatar=avatar):
        st.write(item["content"])
        if item["result"]:
            render_decision(item["result"])

if prompt := st.chat_input("Nhập câu hỏi của học viên…"):
    submit_message(prompt)
    st.rerun()
