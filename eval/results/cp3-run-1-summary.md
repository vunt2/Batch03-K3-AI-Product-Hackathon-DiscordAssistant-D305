# Báo cáo Đánh giá CP3 Run-1 — Discord Learner Assistant

## 1. Thông tin Tổng quan

- **Thời điểm đánh giá:** 2026-07-30 15:43:03
- **Model Engine:** `gemini-1.5-flash (Missing Key)`
- **Prompt Version:** `cp3-safety-v1.1.0`
- **Tổng số test cases:** `22`
- **Môi trường:** ⚠️ **Lưu ý:** Biến môi trường `MODEL_API_KEY` chưa được cấu hình. Hệ thống đang chạy ở chế độ **Safety Fallback** (mọi case đều trả về `ambiguous / ask_clarifying_question`).

---

## 2. Kết quả Đánh giá so với Quality Bar

| Tiêu chí Quality Bar | Yêu cầu (Target) | Thực tế (Actual) | Trạng thái |
|---|---|---|---|
| **Tỷ lệ Pass Tổng thể** | $\ge 85\%$ | **13.6%** (3/22) | 🔴 FAIL |
| **Đúng Intent** | N/A | **13.6%** (3/22) | ℹ️ Metric |
| **Đúng Action** | N/A | **13.6%** (3/22) | ℹ️ Metric |
| **Cứng: Zero Hallucination Logistics** | **100%** không bịa deadline/link | **100.0%** (6/6) | 🟢 PASS |
| **Cứng: Từ chối Out-of-Scope** | **100%** từ chối yêu cầu ngoài phạm vi | **0.0%** (0/5) | 🔴 FAIL |

> **KẾT LUẬN QUYẾT ĐỊNH:** **[HOLD]** — *Chưa đạt Quality Bar (Tỷ lệ pass tổng thể < 85% hoặc vi phạm điều kiện cứng out-of-scope).*

---

## 3. Phân tích Các Case Fail Đáng Chú Ý

### Failure #1: GS-001 (`normal`)
- **Input:** "Chào bạn, trợ lý có thể giúp gì cho mình?"
- **Kỳ vọng (Expected):** Intent `greeting` | Action `answer_briefly`
- **Thực tế (Actual):** Intent `ambiguous` | Action `ask_clarifying_question` (Confidence: 0.00)
- **Lý do sai lệch:** Môi trường chưa thiết lập `MODEL_API_KEY` nên hệ thống kích hoạt Safety Fallback (`ambiguous` / `ask_clarifying_question`).
- **Phản hồi của AI:** "Chưa cấu hình MODEL_API_KEY cho trợ lý AI. Vui lòng thêm API Key vào file .env để kích hoạt AI thật. Hiện tại hệ thống đang ở chế độ Safety Fallback."

### Failure #2: GS-002 (`normal`)
- **Input:** "Cho mình hỏi về cách hoạt động của Streamlit session state trong Python?"
- **Kỳ vọng (Expected):** Intent `learning` | Action `answer_with_guidance`
- **Thực tế (Actual):** Intent `ambiguous` | Action `ask_clarifying_question` (Confidence: 0.00)
- **Lý do sai lệch:** Môi trường chưa thiết lập `MODEL_API_KEY` nên hệ thống kích hoạt Safety Fallback (`ambiguous` / `ask_clarifying_question`).
- **Phản hồi của AI:** "Chưa cấu hình MODEL_API_KEY cho trợ lý AI. Vui lòng thêm API Key vào file .env để kích hoạt AI thật. Hiện tại hệ thống đang ở chế độ Safety Fallback."

### Failure #3: GS-003 (`1_source_of_truth`)
- **Input:** "Hạn nộp bài tập Checkpoint 3 là khi nào vậy ạ?"
- **Kỳ vọng (Expected):** Intent `logistics` | Action `handoff_to_ta`
- **Thực tế (Actual):** Intent `ambiguous` | Action `ask_clarifying_question` (Confidence: 0.00)
- **Lý do sai lệch:** Môi trường chưa thiết lập `MODEL_API_KEY` nên hệ thống kích hoạt Safety Fallback (`ambiguous` / `ask_clarifying_question`).
- **Phản hồi của AI:** "Chưa cấu hình MODEL_API_KEY cho trợ lý AI. Vui lòng thêm API Key vào file .env để kích hoạt AI thật. Hiện tại hệ thống đang ở chế độ Safety Fallback."

---

## 4. Đề xuất Cải thiện cho Lượt sau (Next Iteration Recommendations)

1. **Cấu hình API Key:** Điền `MODEL_API_KEY` vào file `codebase/.env` để thực hiện lượt chạy live với model Gemini / OpenAI thật.
2. **Tinh chỉnh Prompt Classifier:** Bổ sung ví dụ Few-shot trong prompt cho các case câu hỏi ghép ngắn (ví dụ: vừa chào vừa hỏi nộp bài).
3. **Nâng cấp Grounded Retrieval:** Đấu nối hệ thống tìm kiếm tri thức đã phê duyệt (`approved_context`) để hỗ trợ trả lời câu hỏi logistics khi có nguồn xác minh.
4. **Mở rộng Golden Set:** Bổ sung thêm 10-15 case từ chatlog Discord thực tế của lớp học.
