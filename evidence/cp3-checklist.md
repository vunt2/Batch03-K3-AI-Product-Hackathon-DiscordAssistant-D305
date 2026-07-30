# CP3 Checklist — Xác minh Tích hợp AI Thật & Nộp Bài (Hưng's Handover)

> Tài liệu kiểm tra 11 tiêu chuẩn nghiệm thu mốc **Checkpoint 3 (CP3)** dành cho phần việc do **Hưng** phụ trách, phân tách rõ phần evaluation live của **Phong**.

---

## Bảng Checklist Xác minh 11 Tiêu chí nghiệm thu CP3

| # | Tiêu chí Kiểm tra | Trạng thái | Minh chứng / Vị trí File mã nguồn | Ghi chú & Chi tiết nghiệm thu |
|---|---|:---:---|---|---|
| 1 | **Evidence có phương pháp và mẫu số rõ ràng** | 🟢 ĐẠT | `evidence/survey-method.md` & `evidence/survey-summary.md` | Lấy mẫu $N=20$ ($n=18$ học viên, $n=2$ TA). Mẫu số $n=18$ dùng chuẩn xác cho câu hỏi học viên ($88.9\%$ mất thời gian, $83.3\%$ từ bỏ). |
| 2 | **Bảng Impact so sánh 3 ứng viên** | 🟢 ĐẠT | `evidence/impact-analysis.md` | So sánh 3 ứng viên (Định tuyến intent, Tóm tắt cho TA, Phát hiện Stuck) đầy đủ 6 thông số dựa trên số liệu khảo sát thực tế. |
| 3 | **Có ít nhất 3 Willing Users có tên** | 🟢 ĐẠT | `evidence/cp1-canvas.md` & `spec.md` §8 | Danh sách 3 người dùng đồng ý thử prototype: Nguyễn Văn An (HV-012), Trần Thị Bình (HV-045), Lê Hoàng Cường (HV-089). |
| 4 | **AI Call thật đã tích hợp trong code** | 🟢 ĐẠT | `codebase/model_client.py` & `codebase/intent_engine.py` | Mã nguồn kết nối LLM API thật (`gemini-1.5-flash` / `gpt-4o-mini`) kèm Safety Contract Validator (`output_contract.py`). |
| 5 | **Golden set $\ge 20$ và đủ cơ cấu** | 🟢 ĐẠT | `eval/golden-set.csv` | Đã có 22 test cases phủ 4 lớp chỗ khó (Sự thật, Mơ hồ, Thẩm quyền, Domain-specific) và Prompt Injection. |
| 6 | **Có $\ge 10$ case có nguồn kiểm chứng** | 🟢 ĐẠT | `eval/golden-set.csv` | Các case được phát triển trực tiếp từ khảo sát học viên và chatlog sampling khóa học (`discord-sample-01` đến `17`). |
| 7 | **Kết quả Live Run chính thức** | 🟡 ĐỜ CHỜ LIVE RUN | `spec.md` §7 & `eval/results/` | **ĐANG CHỜ CP3 LIVE RUN (owner: Phong / bạn).** Không sử dụng kết quả fallback 13.6% làm kết quả AI thật. |
| 8 | **Quality Bar khóa cứng trước khi chạy** | 🟢 ĐẠT | `spec.md` §7 | Khóa cứng: Pass tổng thể $\ge 85\%$, Zero Hallucination Logistics = 100%, Từ chối Out-of-Scope = 100%. |
| 9 | **Không commit file survey CSV gốc** | 🟢 ĐẠT | `git status` / `.gitignore` | File khảo sát thô không bị Git theo dõi, không commit lên public repository để bảo vệ quyền riêng tư. |
| 10 | **Không chứa API Key hoặc dữ liệu nhạy cảm** | 🟢 ĐẠT | `.gitignore` & `evidence/cp3-safety-design.md` | Không commit `.env`. Tự động Redact các credential/key/token nếu xuất hiện trong reply/rationale. |
| 11 | **`spec.md` không còn placeholder quan trọng** | 🟢 ĐẠT | `spec.md` | Đã xóa 100% nhãn `CẦN BỔ SUNG` / `CẦN TÊN`. Chỉ giữ nhãn chờ duy nhất tại §7 cho kết quả live run của Phong. |

---

## Tóm tắt Bàn giao từ Hưng

- **Người thực hiện:** Hưng (Owner: Evidence, Impact, Canvas, AI Spec & CP3 Checklist).
- **Phân tách trách nhiệm:** Hưng đã hoàn thành 100% phần khảo sát, impact analysis, canvas và cấu trúc spec.md. Phần chạy model live và cập nhật tỷ lệ pass tại §7 sẽ do Phong (hoặc bạn) chốt sau khi merge branch.
