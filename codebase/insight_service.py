"""Service for clustering handoff questions and generating Labcoach daily digests."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import re
from typing import Any
import unicodedata

from conversation_context import redact_sensitive_text


STOPWORDS = {
    "minh",
    "ban",
    "oi",
    "a",
    "cho",
    "hoi",
    "la",
    "gi",
    "the",
    "nao",
}

BANGKOK_TZ = timezone(timedelta(hours=7))


def _normalize_canonical_string(text: str) -> str:
    """Normalize text by NFD, stripping accents, đ->d, casefold, and whitespace collapsing."""
    if not isinstance(text, str) or not text.strip():
        return ""
    normalized = unicodedata.normalize("NFD", text.casefold())
    plain = "".join(char for char in normalized if not unicodedata.combining(char))
    plain = plain.replace("đ", "d")
    return re.sub(r"\s+", " ", plain).strip()


def _normalize_and_tokenize(text: str) -> set[str]:
    """Tokenize normalized text and remove generic stopwords."""
    plain = _normalize_canonical_string(text)
    if not plain:
        return set()
    clean_text = re.sub(r"[^\w\s]", " ", plain, flags=re.UNICODE)
    tokens = set(re.sub(r"\s+", " ", clean_text).strip().split())
    return tokens - STOPWORDS


def _jaccard_similarity(tokens1: set[str], tokens2: set[str]) -> float:
    """Calculate Jaccard similarity coefficient between two token sets."""
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    return intersection / union if union > 0 else 0.0


def cluster_handoffs(
    handoffs: list[dict[str, Any]],
    similarity_threshold: float = 0.6,
) -> list[dict[str, Any]]:
    """Cluster handoff questions deterministically using Jaccard similarity."""
    if not isinstance(handoffs, list) or not handoffs:
        return []

    # Sort input deterministically by created_at then handoff_id
    valid_items = []
    for h in handoffs:
        if isinstance(h, dict) and h.get("handoff_id") and h.get("question"):
            valid_items.append(h)

    valid_items.sort(
        key=lambda x: (
            str(x.get("created_at", "")),
            str(x.get("handoff_id", "")),
        )
    )

    clusters: list[dict[str, Any]] = []

    for item in valid_items:
        h_id = str(item["handoff_id"])
        raw_q = str(item["question"])
        clean_q = redact_sensitive_text(raw_q.strip()).strip()
        if not clean_q:
            continue

        norm_str = _normalize_canonical_string(clean_q)
        tokens = _normalize_and_tokenize(clean_q)
        intent = str(item.get("intent", "other"))
        status = str(item.get("status", "pending"))

        matched_cluster = None
        for c in clusters:
            rep_norm_str = c["_rep_norm_str"]
            rep_tokens = c["_rep_tokens"]

            # 1. Exact-normalized match
            if norm_str and norm_str == rep_norm_str:
                matched_cluster = c
                break

            # 2. Token Jaccard similarity match
            if tokens and rep_tokens:
                sim = _jaccard_similarity(tokens, rep_tokens)
                if sim >= similarity_threshold:
                    matched_cluster = c
                    break

        if matched_cluster:
            matched_cluster["questions"].append(clean_q)
            matched_cluster["handoff_ids"].append(h_id)
            matched_cluster["count"] += 1
            if intent not in matched_cluster["intents"]:
                matched_cluster["intents"].append(intent)
            if status == "pending":
                matched_cluster["pending_count"] += 1
            elif status == "resolved":
                matched_cluster["resolved_count"] += 1
        else:
            new_cluster = {
                "cluster_id": f"CLUST-{h_id}",
                "representative_question": clean_q,
                "questions": [clean_q],
                "handoff_ids": [h_id],
                "count": 1,
                "intents": [intent],
                "pending_count": 1 if status == "pending" else 0,
                "resolved_count": 1 if status == "resolved" else 0,
                "_rep_norm_str": norm_str,
                "_rep_tokens": tokens,
            }
            clusters.append(new_cluster)

    # Filter only repeated clusters (count >= 2) and clean internal keys
    repeated = []
    for idx, c in enumerate(clusters):
        if c["count"] >= 2:
            clean_c = {
                "cluster_id": f"CLUST-{idx + 1:03d}",
                "representative_question": c["representative_question"],
                "questions": c["questions"],
                "handoff_ids": c["handoff_ids"],
                "count": c["count"],
                "intents": c["intents"],
                "pending_count": c["pending_count"],
                "resolved_count": c["resolved_count"],
            }
            repeated.append(clean_c)

    # Sort repeated clusters by count DESC, cluster_id ASC
    repeated.sort(key=lambda x: (-x["count"], x["cluster_id"]))
    return repeated


def _parse_bangkok_date(created_at_str: Any) -> date | None:
    """Parse ISO timestamp and convert to Asia/Bangkok local date."""
    if not isinstance(created_at_str, str) or not created_at_str.strip():
        return None
    try:
        ts = created_at_str.strip()
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        bangkok_dt = dt.astimezone(BANGKOK_TZ)
        return bangkok_dt.date()
    except (ValueError, TypeError):
        return None


def build_daily_digest(
    handoffs: list[dict[str, Any]],
    selected_date: date | str,
    timezone_name: str = "Asia/Bangkok",
) -> dict[str, Any]:
    """Build daily digest for Labcoach workspace on selected date."""
    if isinstance(selected_date, str):
        try:
            target_date = datetime.strptime(selected_date.strip(), "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.now(BANGKOK_TZ).date()
    elif isinstance(selected_date, date):
        target_date = selected_date
    else:
        target_date = datetime.now(BANGKOK_TZ).date()

    target_date_str = target_date.strftime("%Y-%m-%d")

    if not isinstance(handoffs, list):
        handoffs = []

    # Filter records matching selected_date in Asia/Bangkok timezone
    day_handoffs = []
    for h in handoffs:
        if not isinstance(h, dict):
            continue
        h_date = _parse_bangkok_date(h.get("created_at"))
        if h_date == target_date:
            day_handoffs.append(h)

    # Deterministic sort
    day_handoffs.sort(
        key=lambda x: (
            str(x.get("created_at", "")),
            str(x.get("handoff_id", "")),
        )
    )

    total_questions = len(day_handoffs)
    pending_count = 0
    resolved_count = 0

    pending_questions = []
    resolved_items = []

    for h in day_handoffs:
        h_id = str(h.get("handoff_id", ""))
        raw_q = str(h.get("question", ""))
        clean_q = redact_sensitive_text(raw_q.strip()).strip()
        intent = str(h.get("intent", "other"))
        status = str(h.get("status", "pending"))

        if not clean_q or not h_id:
            continue

        if status == "pending":
            pending_count += 1
            pending_questions.append(
                {
                    "handoff_id": h_id,
                    "question": clean_q,
                    "intent": intent,
                    "created_at": str(h.get("created_at", "")),
                }
            )
        elif status == "resolved":
            resolved_count += 1
            raw_resp = str(h.get("labcoach_response", ""))
            clean_resp = redact_sensitive_text(raw_resp.strip()).strip()
            resolved_items.append(
                {
                    "handoff_id": h_id,
                    "question": clean_q,
                    "answer": clean_resp,
                    "intent": intent,
                    "resolved_at": str(h.get("resolved_at", "")),
                }
            )

    # Run clustering for the day's handoffs
    repeated_clusters = cluster_handoffs(day_handoffs, similarity_threshold=0.6)

    # Enforce Limits: max 20 pending, max 20 resolved, max 10 repeated clusters
    limited_pending = pending_questions[:20]
    limited_resolved = resolved_items[:20]
    limited_clusters = repeated_clusters[:10]

    # Generate Markdown Digest Report
    md_lines = [
        f"# BÁO CÁO TỔNG HỢP LABCOACH - {target_date_str}",
        "",
        "## ✦ THỐNG KÊ TỔNG QUAN",
        f"- **Tổng số câu hỏi trong ngày:** {total_questions}",
        f"- **Đang chờ xử lý:** {pending_count}",
        f"- **Đã xử lý:** {resolved_count}",
        f"- **Nhóm câu hỏi lặp:** {len(repeated_clusters)}",
        "",
        "## ✦ 1. NHÓM CÂU HỎI LẶP",
    ]

    if not limited_clusters:
        md_lines.append("Không có nhóm câu hỏi lặp trong ngày.")
    else:
        for c in limited_clusters:
            md_lines.append(
                f"### [{c['cluster_id']}] {c['representative_question']} ({c['count']} lượt)"
            )
            md_lines.append(
                f"- **Chờ xử lý:** {c['pending_count']} · **Đã xử lý:** {c['resolved_count']}"
            )
            md_lines.append("- **Các câu hỏi thành viên:**")
            for q in c["questions"]:
                md_lines.append(f"  - {q}")
            md_lines.append("")

    md_lines.extend(
        [
            "",
            f"## ✦ 2. CÂU HỎI ĐANG CHỜ LABCOACH ({len(pending_questions)})",
        ]
    )

    if not limited_pending:
        md_lines.append("Không có câu hỏi nào đang chờ.")
    else:
        for item in limited_pending:
            md_lines.append(
                f"- `[{item['handoff_id']}]` ({item['intent']}): {item['question']}"
            )

    md_lines.extend(
        [
            "",
            f"## ✦ 3. CÂU HỎI ĐÃ XỬ LÝ VÀ PHẢN HỒI ({len(resolved_items)})",
        ]
    )

    if not limited_resolved:
        md_lines.append("Chưa có câu hỏi nào được xử lý trong ngày.")
    else:
        for item in limited_resolved:
            md_lines.append(f"### `[{item['handoff_id']}]` {item['question']}")
            md_lines.append(
                f"**Phản hồi Labcoach:** {item['answer'] if item['answer'] else '(Chưa ghi nhận phản hồi)'}"
            )
            md_lines.append("")

    md_lines.extend(
        [
            "",
            "---",
            "*Ghi chú: Đây là bản tổng hợp tự động từ dữ liệu thực tế trong hệ thống persistent handoff queue.*",
        ]
    )

    markdown_text = "\n".join(md_lines)

    return {
        "selected_date": target_date_str,
        "total_questions": total_questions,
        "pending_count": pending_count,
        "resolved_count": resolved_count,
        "repeated_cluster_count": len(repeated_clusters),
        "repeated_clusters": limited_clusters,
        "pending_questions": limited_pending,
        "resolved_items": limited_resolved,
        "markdown": markdown_text,
    }
