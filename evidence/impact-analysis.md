# Bảng Phân tích Impact và Quyết định Chọn Ứng viên (Impact Analysis)

## 1. Tổng quan Đánh giá Ứng viên

Nhóm D305 đánh giá 3 ứng viên tính năng dựa trên số liệu khảo sát thực tế $N = 20$ ($n = 18$ học viên, $n = 2$ TA).

---

## 2. Bảng So sánh 3 Ứng viên Tính năng

| Tiêu chí | Ứng viên 1: Định tuyến Intent & Phản hồi Đúng mức | Ứng viên 2: Bản tin / Tóm tắt Cuối ngày cho TA | Ứng viên 3: Phát hiện Học viên bị Stuck |
|---|---|---|---|
| **Bao nhiêu người gặp** | **16 / 18 học viên** (88.9%) tốn thời gian tìm kiếm info; **15 / 18** (83.3%) từng từ bỏ tìm kiếm. | **5 / 18 học viên** (27.8%) bình chọn ưu tiên; **2 / 2 TA** vướng nợ thời gian đọc tin trôi. | **12 / 18 học viên** (66.7%) mong muốn có tính năng hỗ trợ khi vướng bài. |
| **Tần suất** | Hằng ngày (72.2% học viên dùng Discord hằng ngày, 3–5 câu hỏi/ngày). | 1 lần/ngày (cuối mỗi buổi học). | Đột xuất (khi gặp bài tập lập trình khó hoặc sát deadline). |
| **Tổn thất mỗi lần (Cost of Error)** | **Rất cao:** Trả lời nhầm deadline/link dẫn tới 0đ Checkpoint; chờ đợi lãng phí 15–45 phút làm đứt gãy mạch học. | **Trung bình:** TA mất 15–20 phút tổng hợp tin nhắn chưa trả lời bằng tay. | **Thấp – Trung bình:** Học viên bỏ dở bài tập nhưng ngại hỏi TA. |
| **Evidence hỗ trợ từ khảo sát** | 88.9% mất thời gian; 83.3% muốn AI rep ngay; 61.1% muốn handoff khi mơ hồ. Quote: *"Cần nhất là AI không bịa deadline hay thông tin sai lệch."* | 27.8% chọn ưu tiên tóm tắt. Khảo sát TA: $>60\%$ câu hỏi trên Discord là lặp đi lặp lại. | 66.7% học viên mong muốn được hỗ trợ khi bị stuck bài tập. |
| **Khả thi trong Hackathon** | **Rất cao:** Xây dựng hoàn chỉnh trong 1.5 ngày với Streamlit UI + Real LLM + Output Contract Validator. | **Trung bình:** Cần kết nối Discord Bot API lắng nghe toàn bộ channel và cronjob tóm tắt. | **Thấp:** Cần lưu trữ lịch sử hội thoại dài hạn và mô hình phân tích ngưỡng tâm lý/stuck phức tạp. |
| **Quyết định nhóm** | **CHỌN CHÍNH THỨC** | **LOẠI** | **LOẠI** |

---

## 3. Lý do Chi tiết Chọn & Loại

### 3.1 Lý do CHỌN Ứng viên 1: "Định tuyến Intent và Phản hồi Đúng mức"
1. **Impact trực tiếp rộng nhất:** 88.9% học viên vướng nỗi đau mất thời gian tìm kiếm thông tin; 83.3% từng từ bỏ tìm kiếm trên Discord.
2. **Cost-of-error cực cao:** Nhầm lẫn giữa thông tin logistics và câu hỏi học tập gây hậu quả trực tiếp đến điểm số học viên (nộp sai link hoặc trễ hạn Checkpoint).
3. **Phù hợp tiêu chí an toàn (Safety First):** Khảo sát ghi nhận 61.1% học viên muốn chuyển TA khi AI không chắc chắn. Tính năng này giải quyết triệt để bài toán ảo giác (Zero Hallucination).
4. **Khả thi cao trong 1.5 ngày:** Đã tích hợp hoàn chỉnh tại CP3 với Real LLM Model Call và Output Contract Validator.

### 3.2 Lý do LOẠI Ứng viên 2 & 3
- **Ứng viên 2 (Bản tin / Tóm tắt cuối ngày cho TA):** Chỉ có 27.8% học viên bình chọn ưu tiên; đối tượng hưởng lợi chủ yếu là TA ($n=2$), impact không trực tiếp giải quyết nỗi đau đứt gãy luồng học của 18/18 học viên.
- **Ứng viên 3 (Phát hiện Học viên bị Stuck):** Mặc dù 66.7% học viên thích ý tưởng, nhưng độ khả thi kỹ thuật trong thời gian 1.5 ngày rất thấp (cần theo dõi lịch sử dài hạn, dễ gây phiền hà nếu phát hiện nhầm), không đảm bảo chất lượng cho buổi Demo CP6.
