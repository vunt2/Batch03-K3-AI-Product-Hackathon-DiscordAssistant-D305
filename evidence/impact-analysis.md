# Bảng Phân tích Impact và Quyết định Chọn Ứng viên (Impact Analysis)

## 1. Danh sách Ứng viên Tính năng

Nhóm D305 đánh giá 3 ứng viên giải pháp dựa trên dữ liệu thu thập từ $n = 28$ học viên khảo sát và $n = 100$ tin nhắn mining Discord.

---

## 2. Bảng Phân tích Impact Chi tiết (Impact Matrix)

| Ứng viên tính năng | Số người gặp (n = 28) | Tần suất xuất hiện | Tổn thất mỗi lần (Cost of Error) | Khả thi trong Hackathon | Quyết định nhóm |
|---|---:|---|---|---|---|
| **1. Định tuyến Intent & Phản hồi Đúng mức** | **20 / 28** (71.4%) | 3–5 lần/học viên/tuần (~28% câu hỏi Discord) | **Rất cao:** Trả lời sai deadline/link nộp làm học viên mất điểm CP (0đ); trả lời mơ hồ làm lãng phí 30-45 phút chờ đợi của TA & Học viên. | **Rất cao:** Xây dựng trong 1.5 ngày với Streamlit UI + Output Contract Validator. | **CHỌN CHÍNH THỨC** |
| **2. Bản tin Cuối ngày cho TA (TA Daily Digest)** | **6 / 28** (21.4%) | 1 lần/ngày (cuối buổi học) | **Trung bình:** TA mất 15–20 phút tổng hợp thủ công danh sách câu hỏi chưa trả lời. | **Trung bình:** Cần hệ thống gom tin nhắn Discord theo thời gian thực và cronjob tóm tắt. | **LOẠI** |
| **3. Phát hiện Học viên bị Stuck** | **4 / 28** (14.3%) | Đột xuất khi có bài tập khó | **Thấp – Trung bình:** Học viên không nộp được bài nhưng ít chủ động báo TA. | **Thấp:** Cần lưu trữ lịch sử hội thoại dài hạn và thiết lập ngưỡng phân tích tâm lý/stuck. | **LOẠI** |

---

## 3. Lý do Chi tiết Chọn & Loại Ứng viên

### 3.1 Lý do CHỌN Ứng viên 1: "Định tuyến Intent và Phản hồi Đúng mức"
1. **Impact trực tiếp & rộng nhất:** $71.4\%$ học viên xác nhận gặp khó khăn, chiếm $28\%$ tổng số câu hỏi trên Discord.
2. **Cost-of-error cực cao:** Nhầm lẫn giữa thông tin logistics và câu hỏi học tập gây hậu quả trực tiếp đến kết quả học tập (nộp sai link hoặc trễ hạn Checkpoint).
3. **Tính khả thi và tính đại diện:** Phản ánh đúng 4 lớp chỗ khó trong thiết kế AI (Nguồn sự thật, Mơ hồ, Thẩm quyền, Domain-specific), demo trực quan được trong 5 phút tại CP6.

### 3.2 Lý do LOẠI Ứng viên 2 & 3
- **Ứng viên 2 (Bản tin TA):** Số lượng người hưởng lợi ít (chỉ 2-3 TA/lớp), impact không trực tiếp đến trải nghiệm học tập của 1.000 học viên.
- **Ứng viên 3 (Phát hiện Stuck):** Nguy cơ gây phiền hà (spam notification) nếu ngưỡng phát hiện không chuẩn xác; khó kiểm chứng tính hiệu quả trong khoảng thời gian 1.5 ngày của hackathon.
