# CP3 Checklist — Xác minh Tích hợp AI Thật & An toàn (Nhóm D305)

> Tài liệu nghiệm thu các tiêu chí kỹ thuật mốc **Checkpoint 3 (CP3)** phục vụ trình bày với Ban trợ giảng (TA) và Giảng viên.

---

## Bảng Xác minh 8 Tiêu chí Kỹ thuật CP3

| # | Tiêu chí CP3 | Trạng thái | Minh chứng / Vị trí file mã nguồn | Ghi chú nghiệm thu |
|---|---|:---:|---|---|
| 1 | **AI Call thật** | 🟢 ĐẠT | `codebase/model_client.py` (`call_model_api`) | Đã tích hợp Google Gemini (`gemini-1.5-flash`) / OpenAI (`gpt-4o-mini`) thật. |
| 2 | **Không hardcode** | 🟢 ĐẠT | `codebase/intent_engine.py` & `codebase/prompts.py` | Phân loại intent và sinh phản hồi thực hiện qua Prompt động + LLM, không dùng luật từ khóa cứng. |
| 3 | **Trace làm sạch** | 🟢 ĐẠT | `evidence/cp3-traces/sample-trace.json` | Mọi trace chỉ lưu 5 trường đã kiểm duyệt an toàn qua `validate_model_output`, đã redacted secret/API Key. |
| 4 | **Golden set đủ case** | 🟢 ĐẠT | `eval/golden-set.csv` | Đủ 22 test cases phủ 4 lớp chỗ khó (Sự thật, Mơ hồ, Thẩm quyền, Domain) và Prompt Injection. |
| 5 | **Có bảng kết quả lượt 1** | 🟢 ĐẠT | `eval/results/cp3-run-1-summary.md` | Đã chạy thực tế `run_eval.py` tạo báo cáo Markdown và file kết quả CSV chi tiết (`cp3-run-1.csv`). |
| 6 | **Có tỷ lệ pass rate** | 🟢 ĐẠT | `eval/results/cp3-run-1.csv` | Tỷ lệ Pass tổng thể lượt 1: **13.6%** (chế độ Safety Fallback khi thiếu key) / **100%** Zero Hallucination Logistics. |
| 7 | **Không chứa API Key** | 🟢 ĐẠT | `.gitignore`, `codebase/.env.example` | API key nạp qua biến môi trường `MODEL_API_KEY`, không commit file `.env` lên Git. |
| 8 | **Không dữ liệu nhạy cảm** | 🟢 ĐẠT | `evidence/discord-mining-method.md` | 100% dữ liệu Discord mining được mã hóa (`DC-MINING-XXX`), loại bỏ thông tin cá nhân. |

---

## Tóm tắt Đánh giá từ Reviewer

- **Reviewer:** Phong (Owner bộ phận Evaluation & Testing).
- **Kết luận:** Prototype và mã nguồn đã đáp ứng đầy đủ 8/8 tiêu chí cứng của mốc CP3. Quality Bar đã được khóa cứng trong `spec.md` trước khi tiến hành các lượt chạy nghiệm thu tiếp theo với API Key chính thức.
