"""Streamlit demo for the Gemini-powered learner and Labcoach workflow."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import html
from pathlib import Path

import streamlit as st
import os
import uuid

from dotenv import load_dotenv


CODEBASE_DIR = Path(__file__).resolve().parent
ENV_PATH = CODEBASE_DIR / ".env"
load_dotenv(ENV_PATH, override=ENV_PATH.exists())


def load_runtime_secrets() -> None:
    """Load runtime configuration from Streamlit secrets into os.environ if not set."""
    try:
        if not hasattr(st, "secrets"):
            return
        secret_keys = (
            "GEMINI_API_KEY",
            "GEMINI_MODEL",
            "GEMINI_TIMEOUT_SECONDS",
            "ASSISTANT_DB_PATH",
        )
        for key in secret_keys:
            if key not in os.environ and key in st.secrets:
                val = str(st.secrets[key])
                if val and str(val).strip():
                    os.environ[key] = str(val).strip()
    except Exception:
        pass


load_runtime_secrets()

from handoff_store import (  # noqa: E402
    APPROVED_FOR_PUBLISH,
    PENDING,
    PENDING_REVIEW,
    PUBLISHED,
    REJECTED,
    RESOLVED,
    StoreError,
    count_handoffs,
    count_knowledge_candidates,
    create_handoff,
    delete_session_handoffs,
    get_knowledge_candidate_for_handoff,
    initialize_store,
    list_handoffs,
    list_knowledge_candidates,
    list_session_handoffs,
    reopen_handoff as store_reopen_handoff,
    resolve_handoff as store_resolve_handoff,
    review_knowledge_candidate,
)
from insight_service import build_daily_digest  # noqa: E402
from intent_engine import IntentResult, classify_message  # noqa: E402
from conversation_context import extract_preferred_name  # noqa: E402
from knowledge_base import load_approved_knowledge  # noqa: E402
from knowledge_publisher import (  # noqa: E402
    KnowledgePublishError,
    publish_candidate,
)
from model_client import get_gemini_status  # noqa: E402


st.set_page_config(
    page_title="D305 Learner Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --canvas: #101119;
        --panel: #171923;
        --panel-soft: #202330;
        --stroke: #303445;
        --ink: #f7f8fc;
        --muted: #aeb4c5;
        --brand: #7c6cf2;
        --brand-soft: rgba(124, 108, 242, .16);
        --success: #57d9a3;
        --warning: #ffd27d;
        --danger: #ff9f9f;
    }
    .stApp {
        background:
            radial-gradient(circle at 78% -10%, rgba(124,108,242,.20), transparent 30rem),
            var(--canvas);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: #141620;
        border-right: 1px solid var(--stroke);
    }
    [data-testid="stSidebar"] * { color: var(--ink); }
    .block-container {
        max-width: 1240px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    h1, h2, h3 { letter-spacing: -.025em; color: var(--ink); }
    .product-mark {
        color: var(--brand);
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin-bottom: .45rem;
    }
    .hero-title {
        color: var(--ink);
        font-size: clamp(2rem, 4.8vw, 3.6rem);
        line-height: 1.04;
        letter-spacing: -.052em;
        font-weight: 820;
        margin: 0 0 .65rem;
    }
    .hero-copy {
        color: var(--muted);
        max-width: 760px;
        font-size: 1.04rem;
        line-height: 1.65;
        margin-bottom: 1.25rem;
    }
    .status-row {
        display: flex;
        gap: .55rem;
        flex-wrap: wrap;
        margin: .4rem 0 1.4rem;
    }
    .pill {
        display: inline-flex;
        align-items: center;
        gap: .38rem;
        padding: .36rem .7rem;
        border: 1px solid var(--stroke);
        border-radius: 999px;
        background: rgba(32,35,48,.92);
        color: #d9dce7;
        font-size: .76rem;
        font-weight: 700;
        line-height: 1.2;
        overflow-wrap: anywhere;
    }
    .pill-ok {
        color: #7ef0be;
        border-color: rgba(87,217,163,.48);
        background: rgba(87,217,163,.12);
    }
    .pill-warn {
        color: #ffe4a0;
        border-color: rgba(255,210,125,.48);
        background: rgba(255,210,125,.12);
    }
    .pill-brand {
        color: #c7c0ff;
        border-color: rgba(124,108,242,.55);
        background: var(--brand-soft);
    }
    .value-strip {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .8rem;
        margin: 1rem 0 1.5rem;
    }
    .value-card {
        min-width: 0;
        border: 1px solid var(--stroke);
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            rgba(32,35,48,.96),
            rgba(23,25,35,.96)
        );
        padding: 1rem;
        box-shadow: 0 12px 32px rgba(0,0,0,.18);
    }
    .value-card strong { display: block; color: var(--ink); margin-bottom: .25rem; }
    .value-card span { color: var(--muted); font-size: .86rem; line-height: 1.45; }
    [data-testid="stChatMessage"] {
        background: rgba(23,25,35,.88);
        border: 1px solid var(--stroke);
        border-radius: 16px;
        padding: .35rem .55rem;
        box-shadow: 0 10px 26px rgba(0,0,0,.14);
        overflow-wrap: anywhere;
    }
    [data-testid="stChatMessage"] p { color: var(--ink); }
    [data-testid="stChatInput"] {
        background: var(--panel-soft);
        border: 1px solid #494e64;
        border-radius: 16px;
    }
    [data-testid="stChatInput"] textarea {
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink);
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--muted) !important;
    }
    .source-box {
        margin-top: .7rem;
        padding: .72rem .8rem;
        border-radius: 12px;
        border: 1px solid rgba(87,217,163,.45);
        background: rgba(87,217,163,.10);
        color: #bdebd8;
        font-size: .82rem;
        line-height: 1.5;
        overflow-wrap: anywhere;
    }
    .coach-answer {
        margin-top: .75rem;
        padding: .8rem .9rem;
        border-radius: 12px;
        border-left: 4px solid var(--brand);
        background: var(--brand-soft);
        color: #dedaff;
    }
    .queue-empty {
        padding: 3rem 1rem;
        text-align: center;
        border: 1px dashed #494e64;
        border-radius: 18px;
        background: rgba(23,25,35,.78);
        color: var(--muted);
    }
    .stButton > button {
        border-radius: 11px;
        border: 1px solid #3a3e51;
        background: var(--panel-soft);
        color: var(--ink);
        min-height: 2.55rem;
        transition: transform .15s ease, border-color .15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: var(--brand);
        background: rgba(124,108,242,.16);
        color: #ffffff;
    }
    .stButton > button:disabled {
        background: #181a23;
        color: #6f7484;
        border-color: #292c38;
    }
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stExpander"],
    [data-testid="stMetric"] {
        background: rgba(23,25,35,.82);
        border-color: var(--stroke);
        color: var(--ink);
    }
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] {
        color: var(--ink);
    }
    [data-baseweb="radio"] label,
    [data-testid="stCheckbox"] label,
    [data-testid="stExpander"] summary {
        color: var(--ink) !important;
    }
    [data-testid="stTextArea"] textarea {
        background: var(--panel-soft);
        color: var(--ink);
        -webkit-text-fill-color: var(--ink);
        border-color: #494e64;
    }
    [data-testid="stTextArea"] textarea::placeholder {
        color: var(--muted);
    }
    [data-testid="stAlert"] {
        background: rgba(32,35,48,.94);
        border: 1px solid var(--stroke);
        color: var(--ink);
    }
    [data-testid="stAlert"] p { color: var(--ink); }
    hr { border-color: var(--stroke) !important; }
    code {
        color: #c7c0ff;
        background: rgba(124,108,242,.12);
    }
    @media (max-width: 760px) {
        .block-container { padding: 1.2rem .9rem 3rem; }
        .value-strip { grid-template-columns: 1fr; }
        .hero-title { font-size: 2.3rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


WELCOME_MESSAGE = {
    "role": "assistant",
    "content": (
        "Chào bạn! Mình có thể tìm câu trả lời từ nguồn khóa học đã được xác minh, "
        "hỏi lại khi chưa rõ hoặc chuyển câu hỏi cho Labcoach."
    ),
    "result": None,
}

SAMPLE_MESSAGES = (
    ("Weekly report gồm gì?", "Weekly report cần nộp nội dung gì?"),
    (
        "Ai nộp weekly report?",
        "Một người hay cả team phải nộp weekly report?",
    ),
    ("Lịch Mentor Duty", "Mentor Duty diễn ra khi nào?"),
    ("Deadline tạo team", "Deadline tạo team là khi nào?"),
    ("Nhờ làm hộ bài", "Làm hộ mình toàn bộ bài và đưa đáp án hoàn chỉnh."),
)


def initialize_state() -> None:
    st.session_state.setdefault("messages", [dict(WELCOME_MESSAGE)])
    st.session_state.setdefault("learner_display_name", "")
    st.session_state.setdefault(
        "learner_session_id", f"session-{uuid.uuid4().hex[:12]}"
    )
    st.session_state.setdefault("navigation", "Learner")
    st.session_state.setdefault("queue_filter", "Đang chờ")
    st.session_state.setdefault("flash_message", "")
    st.session_state.setdefault("reset_confirmed", False)
    st.session_state.setdefault("reset_notice", False)
    st.session_state.setdefault("reset_error", "")
    st.session_state.setdefault("storage_available", True)
    st.session_state.setdefault("storage_error_message", "")

    try:
        initialize_store()
        st.session_state.storage_available = True
        st.session_state.storage_error_message = ""
    except StoreError as error:
        st.session_state.storage_available = False
        st.session_state.storage_error_message = str(error)


def reset_demo_session() -> None:
    st.session_state.learner_display_name = ""
    try:
        delete_session_handoffs(st.session_state.learner_session_id)
        st.session_state.messages = [dict(WELCOME_MESSAGE)]
        st.session_state.flash_message = ""
        st.session_state.reset_confirmed = False
        st.session_state.reset_notice = True
        st.session_state.reset_error = ""
    except StoreError as error:
        st.session_state.reset_confirmed = False
        st.session_state.reset_notice = False
        st.session_state.reset_error = (
            "Không thể xóa dữ liệu phiên do kho lưu trữ tạm thời chưa sẵn sàng."
        )


def submit_message(message: str) -> None:
    clean_message = message.strip()
    if not clean_message:
        return

    preferred_name = extract_preferred_name(clean_message)
    if preferred_name:
        st.session_state.learner_display_name = preferred_name

    history = list(st.session_state.messages)
    st.session_state.messages.append(
        {"role": "user", "content": clean_message, "result": None}
    )
    try:
        with st.spinner("Gemini đang kiểm tra ý định và nguồn phù hợp…"):
            result = classify_message(
                clean_message,
                conversation_history=history,
                preferred_name=(
                    st.session_state.learner_display_name or None
                ),
            )
    except Exception:
        result = {
            "intent": "ambiguous",
            "label": "Cần làm rõ",
            "confidence": 0.0,
            "action": "ask_clarifying_question",
            "action_label": "Hỏi lại",
            "reply": (
                "Trợ lý đang gặp sự cố tạm thời. "
                "Bạn hãy thử lại hoặc chuyển câu hỏi cho Labcoach."
            ),
            "rationale": "Lỗi ngoài dự kiến đã được ẩn khỏi giao diện.",
            "is_fallback": True,
            "model_name": "Gemini",
            "trace_id": f"trace-ui-{len(st.session_state.messages):04d}",
            "model_requested": "Gemini",
            "model_used": "Gemini",
            "used_fallback": True,
            "error_type": "unexpected_error",
            "error_code": None,
            "knowledge_id": None,
            "source_ids": [],
            "topic": None,
            "source_verified": False,
        }

    handoff_id = None
    if result["action"] == "handoff_to_ta":
        try:
            record = create_handoff(
                question=clean_message,
                intent=result["intent"],
                reason=result["rationale"],
                trace_id=result["trace_id"],
                model=result["model_used"],
                learner_session_id=st.session_state.learner_session_id,
            )
            handoff_id = record["handoff_id"]
        except StoreError as error:
            st.session_state.storage_available = False
            st.session_state.storage_error_message = str(error)
            result["reply"] = (
                "Mình chưa thể lưu yêu cầu cho Labcoach do kho dữ liệu tạm thời "
                "chưa sẵn sàng. Bạn vui lòng thử lại sau."
            )
            handoff_id = None

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["reply"],
            "result": result,
            "handoff_id": handoff_id,
            "labcoach_response": "",
            "resolved_at": None,
        }
    )


def render_decision(result: IntentResult) -> None:
    call_label = (
        "Safety fallback" if result["used_fallback"] else "Gemini real call"
    )
    call_class = "pill-warn" if result["used_fallback"] else "pill-ok"
    st.markdown(
        f"""
        <div class="status-row">
          <span class="pill {call_class}">{html.escape(call_label)}</span>
          <span class="pill pill-brand">Intent · {html.escape(result["label"])}</span>
          <span class="pill">Action · {html.escape(result["action_label"])}</span>
          <span class="pill">Tin cậy · {result["confidence"]:.0%}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result["source_verified"]:
        source_ids = ", ".join(result["source_ids"])
        st.markdown(
            f"""
            <div class="source-box">
              <strong>✓ Nguồn đã được xác minh</strong><br/>
              Knowledge ID: <strong>{html.escape(result["knowledge_id"] or "")}</strong>
              · Source ID: {html.escape(source_ids)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Chi tiết quyết định"):
        st.write(result["rationale"])
        st.caption(
            f"Trace ID: {result['trace_id']} · Model: {result['model_used']}"
        )


def render_learner_view() -> None:
    _sync_labcoach_response(st.session_state.learner_session_id)
    st.markdown(
        '<div class="product-mark">Learner workspace</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h1 class="hero-title">Hỏi nhanh.<br/>Nhận đúng nguồn.</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero-copy">
          Learner nhận câu trả lời từ knowledge đã được xác minh. Những câu chưa
          đủ căn cứ được chuyển thẳng vào queue để Labcoach xử lý.
        </div>
        <div class="value-strip">
          <div class="value-card"><strong>① Tìm nguồn</strong><span>Chỉ dùng knowledge approved, còn hiệu lực và đúng chủ đề.</span></div>
          <div class="value-card"><strong>② Quyết định an toàn</strong><span>Gemini chọn trả lời, hỏi lại, từ chối hoặc handoff.</span></div>
          <div class="value-card"><strong>③ Có người tiếp nhận</strong><span>Câu bot chưa biết không bị bỏ quên trong hội thoại.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.learner_display_name:
        st.caption(
            f"Đang nhớ trong phiên: {st.session_state.learner_display_name}"
        )

    st.markdown("#### Câu hỏi mẫu")
    sample_columns = st.columns(3)
    for index, (label, sample) in enumerate(SAMPLE_MESSAGES):
        with sample_columns[index % 3]:
            if st.button(
                label,
                key=f"sample-{index}",
                use_container_width=True,
            ):
                submit_message(sample)
                st.rerun()

    st.markdown("#### Hội thoại")
    for item in st.session_state.messages:
        with st.chat_message(item["role"]):
            st.write(item["content"])
            if item.get("result"):
                render_decision(item["result"])
            if item.get("labcoach_response"):
                st.markdown(
                    f"""
                    <div class="coach-answer">
                      <strong>Phản hồi từ Labcoach</strong><br/>
                      {html.escape(item["labcoach_response"])}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if prompt := st.chat_input("Nhập câu hỏi của bạn…"):
        submit_message(prompt)
        st.rerun()


def _format_timestamp(value: str | None) -> str:
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value).strftime("%d/%m/%Y · %H:%M")
    except ValueError:
        return value


def _sync_labcoach_response(learner_session_id: str) -> None:
    try:
        session_handoffs = list_session_handoffs(learner_session_id)
    except StoreError:
        return
    records_by_id = {h["handoff_id"]: h for h in session_handoffs}
    for message in st.session_state.messages:
        h_id = message.get("handoff_id")
        if h_id and h_id in records_by_id:
            rec = records_by_id[h_id]
            if rec["status"] == RESOLVED:
                message["labcoach_response"] = rec["labcoach_response"]
                message["resolved_at"] = rec["resolved_at"]


def execute_candidate_publish(
    candidate_id: str,
    topic: str,
    volatile: bool,
    valid_until: str | None,
) -> tuple[bool, str]:
    """Execute candidate publish safely via backend publisher."""
    try:
        entry = publish_candidate(
            candidate_id=candidate_id,
            topic=topic,
            volatile=volatile,
            valid_until=valid_until,
        )
        k_id = entry.get("id", "")
        return True, f"Đã publish knowledge {k_id}."
    except KnowledgePublishError:
        return (
            False,
            "Không thể publish knowledge. Vui lòng kiểm tra trạng thái "
            "candidate và thông tin đã nhập.",
        )


def render_labcoach_view() -> None:
    st.warning(
        "Labcoach View hiện chưa có xác thực. Không triển khai công khai với dữ liệu thật."
    )
    try:
        pending_count, resolved_count = count_handoffs()
        cand_p_count, cand_a_count, cand_r_count = count_knowledge_candidates()
        published_candidates = list_knowledge_candidates(PUBLISHED)
        cand_pub_count = len(published_candidates)
    except StoreError:
        st.error("Không thể lấy dữ liệu thống kê từ kho lưu trữ.")
        return

    st.markdown(
        '<div class="product-mark">Labcoach workspace</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h1 class="hero-title">Một queue.<br/>Không sót câu hỏi.</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-copy">Xử lý tập trung các câu bot chưa có đủ căn cứ. Câu hỏi và phản hồi được lưu trong persistent queue; phản hồi Labcoach không tự động trở thành knowledge chính thức.</div>',
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(6)
    metric_columns[0].metric("Handoff chờ", pending_count)
    metric_columns[1].metric("Handoff xong", resolved_count)
    metric_columns[2].metric("Chờ duyệt", cand_p_count)
    metric_columns[3].metric("Sẵn sàng publish", cand_a_count)
    metric_columns[4].metric("Đã từ chối", cand_r_count)
    metric_columns[5].metric("Đã publish", cand_pub_count)

    if st.session_state.flash_message:
        st.success(st.session_state.flash_message)
        st.session_state.flash_message = ""

    st.markdown("### ✦ Knowledge chờ duyệt")
    try:
        pending_candidates = list_knowledge_candidates(PENDING_REVIEW)
    except StoreError:
        st.error("Không thể tải danh sách candidate từ kho lưu trữ.")
        pending_candidates = []

    if not pending_candidates:
        st.caption("Chưa có candidate nào đang chờ duyệt.")
    else:
        for cand in pending_candidates:
            c_id = cand["candidate_id"]
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="status-row">
                      <span class="pill pill-warn">Chờ duyệt</span>
                      <span class="pill pill-brand">{html.escape(cand["intent"])}</span>
                      <span class="pill">{html.escape(c_id)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                edited_q = st.text_area(
                    "Câu hỏi (có thể chỉnh sửa)",
                    value=cand["question"],
                    key=f"cand-q-{c_id}",
                )
                edited_a = st.text_area(
                    "Câu trả lời (có thể chỉnh sửa)",
                    value=cand["answer"],
                    key=f"cand-a-{c_id}",
                )
                st.caption(
                    f"Nguồn: `{cand['source_type']}` · Handoff: `{cand['handoff_id']}`"
                )
                rev_cols = st.columns(2)
                with rev_cols[0]:
                    reviewer = st.text_input(
                        "Người duyệt (bắt buộc)",
                        key=f"cand-rev-{c_id}",
                        placeholder="Họ tên hoặc ID người duyệt…",
                    )
                with rev_cols[1]:
                    review_note = st.text_input(
                        "Ghi chú review (không bắt buộc)",
                        key=f"cand-note-{c_id}",
                        placeholder="Ghi chú thêm nếu có…",
                    )
                btn_cols = st.columns(2)
                with btn_cols[0]:
                    if st.button(
                        "Duyệt để chờ publish",
                        key=f"cand-app-{c_id}",
                        type="primary",
                        use_container_width=True,
                    ):
                        if not reviewer.strip():
                            st.warning("Vui lòng nhập tên/ID Người duyệt.")
                        elif not edited_q.strip() or not edited_a.strip():
                            st.warning("Câu hỏi và câu trả lời không được để trống.")
                        else:
                            try:
                                if review_knowledge_candidate(
                                    c_id,
                                    APPROVED_FOR_PUBLISH,
                                    edited_q,
                                    edited_a,
                                    reviewer,
                                    review_note,
                                ):
                                    st.session_state.flash_message = (
                                        f"Đã duyệt candidate {c_id} (chờ publish)."
                                    )
                                    st.rerun()
                                else:
                                    st.error("Không thể duyệt candidate này.")
                            except StoreError:
                                st.error("Lỗi kho lưu trữ khi duyệt candidate.")
                with btn_cols[1]:
                    if st.button(
                        "Từ chối",
                        key=f"cand-rej-{c_id}",
                        use_container_width=True,
                    ):
                        if not reviewer.strip():
                            st.warning("Vui lòng nhập tên/ID Người duyệt.")
                        elif not edited_q.strip() or not edited_a.strip():
                            st.warning("Câu hỏi và câu trả lời không được để trống.")
                        else:
                            try:
                                if review_knowledge_candidate(
                                    c_id,
                                    REJECTED,
                                    edited_q,
                                    edited_a,
                                    reviewer,
                                    review_note,
                                ):
                                    st.session_state.flash_message = (
                                        f"Đã từ chối candidate {c_id}."
                                    )
                                    st.rerun()
                                else:
                                    st.error("Không thể từ chối candidate này.")
                            except StoreError:
                                st.error("Lỗi kho lưu trữ khi từ chối candidate.")

    st.divider()
    st.markdown("### ✦ Knowledge sẵn sàng publish")
    try:
        approved_candidates = list_knowledge_candidates(APPROVED_FOR_PUBLISH)
    except StoreError:
        st.error("Không thể tải danh sách candidate sẵn sàng publish.")
        approved_candidates = []

    if not approved_candidates:
        st.caption("Chưa có candidate nào ở trạng thái sẵn sàng publish.")
    else:
        for cand in approved_candidates:
            c_id = cand["candidate_id"]
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="status-row">
                      <span class="pill pill-brand">Sẵn sàng publish</span>
                      <span class="pill">{html.escape(cand["intent"])}</span>
                      <span class="pill">{html.escape(c_id)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.text_input(
                    "Câu hỏi (đã duyệt)",
                    value=cand["question"],
                    disabled=True,
                    key=f"pub-q-{c_id}",
                )
                st.text_area(
                    "Câu trả lời (đã duyệt)",
                    value=cand["answer"],
                    disabled=True,
                    key=f"pub-a-{c_id}",
                )
                st.caption(
                    f"Người duyệt: `{cand['reviewed_by']}` · Thời gian: `{cand['reviewed_at']}`"
                )
                pub_topic = st.text_input(
                    "Topic",
                    value=cand["intent"],
                    key=f"pub-topic-{c_id}",
                )
                is_volatile = st.checkbox(
                    "Thông tin có thời hạn",
                    key=f"pub-vol-{c_id}",
                )
                if is_volatile:
                    valid_date = st.date_input(
                        "Có hiệu lực đến",
                        value=datetime.now(timezone.utc).date(),
                        key=f"pub-date-{c_id}",
                    )
                    valid_until_str = valid_date.strftime("%Y-%m-%d")
                else:
                    valid_until_str = None

                if st.button(
                    "Publish knowledge",
                    key=f"pub-btn-{c_id}",
                    type="primary",
                    use_container_width=True,
                ):
                    clean_topic = pub_topic.strip()
                    if not clean_topic:
                        st.warning("Vui lòng nhập Topic.")
                    else:
                        success, msg = execute_candidate_publish(
                            c_id, clean_topic, is_volatile, valid_until_str
                        )
                        if success:
                            st.session_state.flash_message = msg
                            st.rerun()
                        else:
                            st.error(msg)

    st.caption(f"Đã publish: {cand_pub_count} knowledge từ phản hồi Labcoach.")

    st.divider()
    st.markdown("### ✦ Tổng hợp cuối ngày")
    bangkok_today = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=7))).date()
    selected_digest_date = st.date_input(
        "Chọn ngày xem tổng hợp",
        value=bangkok_today,
        key="digest_date_picker",
    )

    try:
        all_handoffs_for_digest = list_handoffs(None)
        digest = build_daily_digest(all_handoffs_for_digest, selected_digest_date)
    except StoreError:
        st.error("Không thể lấy dữ liệu handoff để lập bản tổng hợp.")
        digest = None

    if digest is not None:
        digest_cols = st.columns(4)
        digest_cols[0].metric("Tổng câu hỏi", digest["total_questions"])
        digest_cols[1].metric("Chưa xử lý", digest["pending_count"])
        digest_cols[2].metric("Đã xử lý", digest["resolved_count"])
        digest_cols[3].metric("Nhóm câu lặp", digest["repeated_cluster_count"])

        if digest["repeated_clusters"]:
            st.markdown("#### các nhóm câu hỏi lặp trùng:")
            for cluster in digest["repeated_clusters"]:
                with st.expander(
                    f"[{cluster['cluster_id']}] {cluster['representative_question']} ({cluster['count']} lượt)"
                ):
                    st.write(
                        f"**Chờ xử lý:** {cluster['pending_count']} · **Đã xử lý:** {cluster['resolved_count']}"
                    )
                    st.write(f"**Intents:** {', '.join(cluster['intents'])}")
                    st.write("**Danh sách câu hỏi trong nhóm:**")
                    for q in cluster["questions"]:
                        st.markdown(f"- {html.escape(q)}")
        else:
            st.caption("Không có nhóm câu hỏi lặp trong ngày đã chọn.")

        with st.expander("Xem trước bản tổng hợp Markdown"):
            st.markdown(digest["markdown"])

        st.download_button(
            label="Tải bản tổng hợp Markdown",
            data=digest["markdown"],
            file_name=f"labcoach-digest-{digest['selected_date']}.md",
            mime="text/markdown",
            key=f"download-digest-{digest['selected_date']}",
        )

    st.divider()
    st.markdown("### ✦ Hàng chờ Handoff")

    st.radio(
        "Lọc câu hỏi",
        ("Đang chờ", "Đã xử lý", "Tất cả"),
        horizontal=True,
        key="queue_filter",
    )
    filter_status = {
        "Đang chờ": PENDING,
        "Đã xử lý": RESOLVED,
        "Tất cả": None,
    }[st.session_state.queue_filter]

    try:
        visible_items = list_handoffs(filter_status)
    except StoreError:
        st.error("Không thể tải danh sách câu hỏi từ kho lưu trữ.")
        return

    if not visible_items:
        st.markdown(
            """
            <div class="queue-empty">
              <div style="font-size:2rem;margin-bottom:.5rem">✓</div>
              <strong>Chưa có câu hỏi trong nhóm này</strong><br/>
              Câu Learner được handoff sẽ xuất hiện tại đây.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for item in visible_items:
        with st.container(border=True):
            status_label = (
                "Đang chờ" if item["status"] == PENDING else "Đã xử lý"
            )
            status_class = (
                "pill-warn" if item["status"] == PENDING else "pill-ok"
            )
            st.markdown(
                f"""
                <div class="status-row">
                  <span class="pill {status_class}">{status_label}</span>
                  <span class="pill pill-brand">{html.escape(item["intent"])}</span>
                  <span class="pill">{html.escape(item["handoff_id"])}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.subheader(item["question"])
            st.caption(
                f"Tạo lúc {_format_timestamp(item['created_at'])} · "
                f"Trace `{item['trace_id']}` · Model `{item['model']}`"
            )
            with st.expander("Lý do chuyển Labcoach"):
                st.write(item["reason"])

            if item["status"] == PENDING:
                response = st.text_area(
                    "Phản hồi cho Learner",
                    key=f"response-{item['handoff_id']}",
                    placeholder=(
                        "Nhập câu trả lời đã được Labcoach kiểm tra…"
                    ),
                )
                if st.button(
                    "Gửi phản hồi và đánh dấu đã xử lý",
                    key=f"resolve-{item['handoff_id']}",
                    type="primary",
                    use_container_width=True,
                ):
                    if not response.strip():
                        st.warning("Vui lòng nhập phản hồi trước khi xử lý.")
                    else:
                        try:
                            if store_resolve_handoff(
                                item["handoff_id"],
                                response,
                            ):
                                _sync_labcoach_response(
                                    st.session_state.learner_session_id
                                )
                                st.session_state.flash_message = (
                                    "Đã gửi phản hồi cho Learner và lưu thành candidate chờ team duyệt."
                                )
                                st.rerun()
                            else:
                                st.error("Không thể đánh dấu xử lý câu hỏi này.")
                        except StoreError:
                            st.error("Lỗi kho lưu trữ: Không thể gửi phản hồi lúc này.")
            else:
                st.markdown("**Phản hồi đã gửi**")
                st.info(item["labcoach_response"])
                st.caption(
                    f"Xử lý lúc {_format_timestamp(item['resolved_at'])}"
                )
                try:
                    cand = get_knowledge_candidate_for_handoff(
                        item["handoff_id"]
                    )
                    if cand:
                        st.caption("Knowledge candidate: Chờ team duyệt")
                except StoreError:
                    pass
                if st.button(
                    "Mở lại câu hỏi",
                    key=f"reopen-{item['handoff_id']}",
                    use_container_width=True,
                ):
                    try:
                        if store_reopen_handoff(item["handoff_id"]):
                            st.session_state.flash_message = (
                                "Đã mở lại câu hỏi trong hàng chờ."
                            )
                            st.rerun()
                        else:
                            st.error("Không thể mở lại câu hỏi này.")
                    except StoreError:
                        st.error("Lỗi kho lưu trữ: Không thể mở lại câu hỏi lúc này.")


def render_sidebar() -> None:
    if st.session_state.get("reset_notice", False):
        st.toast("Đã xóa dữ liệu phiên demo.")
        st.session_state.reset_notice = False

    if st.session_state.get("reset_error", ""):
        st.sidebar.error(st.session_state.reset_error)
        st.session_state.reset_error = ""

    if not st.session_state.get("storage_available", True):
        st.sidebar.warning("Kho lưu trữ handoff tạm thời chưa sẵn sàng.")

    gemini_status = get_gemini_status()
    knowledge_count = len(load_approved_knowledge())
    pending_count = 0
    try:
        pending_count, _ = count_handoffs()
    except StoreError:
        pass

    with st.sidebar:
        st.markdown("## ✦ D305 Assistant")
        st.caption("Learner support · Gemini")
        st.caption("Demo có kiểm soát · Chưa tích hợp đăng nhập hoặc Discord thật.")
        st.radio(
            "Không gian làm việc",
            ("Learner", "Labcoach"),
            key="navigation",
            label_visibility="collapsed",
        )
        st.divider()

        if gemini_status["configured"]:
            st.success("Gemini Ready")
        else:
            st.warning("Gemini chưa được cấu hình")
        st.caption(f"Model: `{gemini_status['model']}`")
        st.caption(f"Knowledge đã tải: **{knowledge_count} nguồn**")
        if pending_count:
            st.info(f"Labcoach có **{pending_count}** câu đang chờ.")

        st.divider()
        st.markdown("**Giá trị demo**")
        st.caption("✓ Trả lời từ nguồn đã xác minh")
        st.caption("✓ Không đoán logistics thiếu nguồn")
        st.caption("✓ Handoff vào queue tập trung")

        st.divider()
        st.markdown("**Xóa dữ liệu phiên demo**")
        confirmed = st.checkbox(
            "Tôi xác nhận xóa hội thoại và queue",
            key="reset_confirmed",
        )
        st.button(
            "Xóa dữ liệu phiên",
            disabled=not confirmed,
            on_click=reset_demo_session,
            use_container_width=True,
        )


def main() -> None:
    initialize_state()
    render_sidebar()
    if st.session_state.navigation == "Learner":
        render_learner_view()
    else:
        render_labcoach_view()


if __name__ == "__main__":
    main()
