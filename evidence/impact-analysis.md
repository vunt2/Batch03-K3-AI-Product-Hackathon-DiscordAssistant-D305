# Bảng Phân tích Impact và Quyết định Chọn Ứng viên (Impact Analysis)

## 1. Danh sách Ứng viên Tính năng

Nhóm D305 đánh giá 3 ứng viên giải pháp dựa trên dữ liệu khảo sát ($n = 20$ phản hồi: 18 learner, 2 TA) và trích xuất chatlog Discord ($n = 88$ message đã trích xuất tại `data/processed/discord/messages-anonymized.csv`). Tất cả 20 phản hồi khảo sát đã được nhóm xác minh thủ công là người ngoài nhóm D305 (chưa có trường dữ liệu độc lập chứng minh eligibility). Cơ cấu loại message: 56 `question`, 26 `answer`, 5 `announcement`, 1 `follow_up`.

---

## 2. Bảng Phân tích Impact Chi tiết (Impact Matrix)

| Ứng viên tính năng | Số người gặp (Verified Evidence) | Tần suất xuất hiện | Tổn thất mỗi lần (Cost of Error) | Khả thi trong Hackathon | Quyết định nhóm |
|---|---|---|---|---|---|
| **1. Định tuyến Intent & Phản hồi Đúng mức** | **10 / 18 learner** khảo sát ($n=18$) vướng câu hỏi không được trả lời/trùng lặp; **56 / 88 message** là `question` (gồm 11 `course_policy`, 10 `team_workflow`, 9 `github`, 6 `schedule`, 6 `submission`, 5 `technical_setup`, 3 `deadline`, 3 `api_key`, 2 `checkpoint`, 1 `other` — tổng đúng 56) từ chatlog Discord ($n=88$) | `UNVERIFIED` (chưa có dữ liệu đo số lần/tuần của từng học viên) | **Rất cao:** Trả lời sai deadline/link nộp bài có thể làm học viên mất điểm Checkpoint (0đ); trả lời mơ hồ gây lãng phí thời gian làm rõ của TA & Học viên. | **Rất cao:** Xây dựng thành công prototype Streamlit UI + Gemini LLM Intent Engine + Output Contract Validator trong 1.5 ngày. | **CHỌN CHÍNH THỨC** |
| **2. Bản tin Cuối ngày cho TA (TA Daily Digest)** | **2 / 2 TA** khảo sát mong muốn nhận báo cáo tổng hợp cuối ngày; **16 / 18 learner** gặp tin nhắn bị trôi | `UNVERIFIED` (chưa đo số lần/ngày) | **Trung bình:** TA mất thời gian tổng hợp thủ công danh sách câu hỏi trôi. | **Trung bình:** Cần hạ tầng gom tin nhắn thời gian thực và cronjob tóm tắt. | **LOẠI** |
| **3. Phát hiện Học viên bị Stuck** | **15 / 18 learner** từng từ bỏ tìm kiếm khi gặp vướng mắc | `UNVERIFIED` (chưa đo số lần gặp sự cố) | `UNVERIFIED` (chưa có đo lường thời gian mất chính xác cho toàn bộ mẫu) | **Thấp:** Cần theo dõi lịch sử hội thoại dài hạn và thiết lập ngưỡng phát hiện chủ động. | **LOẠI** |

---

## 3. Lý do Chi tiết Chọn & Loại Ứng viên

### 3.1 Lý do CHỌN Ứng viên 1: "Định tuyến Intent và Phản hồi Đúng mức"
1. **Bằng chứng rõ ràng nhất:** 10/18 learner khảo sát xác nhận vướng khó khăn trực tiếp; dữ liệu trích xuất Discord ($n=88$) có 56 câu hỏi (`question`) tập trung vào chính sách khóa học (11), quy trình nhóm (10), GitHub (9), lịch học (6), nộp bài (6), kỹ thuật (5), deadline (3), API key (3), đề tài (2) và khác (1) — tổng 56 câu hỏi.
2. **Cost-of-error cực cao:** Nhầm lẫn thông tin logistics hoặc bịa đặt deadline có hậu quả trực tiếp (nộp trễ hoặc sai link dẫn đến 0 điểm Checkpoint).
3. **Phù hợp với 4 lớp chỗ khó:** Phụ thuộc đúng 4 lớp chỗ khó trong thiết kế AI (Nguồn sự thật, Mơ hồ, Thẩm quyền, Domain-specific), cho phép demo 4 đường đi trải nghiệm trực quan tại CP6.

### 3.2 Lý do LOẠI Ứng viên 2 & 3
- **Ứng viên 2 (Bản tin TA):** Số lượng người hưởng lợi trực tiếp ít (chỉ 2 TA khảo sát), không tác động trực tiếp đến trải nghiệm phản hồi tức thì cho học viên khi đang học.
- **Ứng viên 3 (Phát hiện Stuck):** Độ phức tạp kỹ thuật cao, nguy cơ gây phiền (spam) nếu ngưỡng phát hiện sai; chưa đo lường được tổn thất chính xác để ưu tiên trong 1.5 ngày.
