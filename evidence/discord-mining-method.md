# Phương pháp Khai thác Dữ liệu Discord & Khảo sát Học viên (Evidence Methodology)

## 1. Tổng quan Phương pháp (Combined Methodology)

Để xây dựng căn cứ minh chứng đạt tiêu chuẩn nghiệm thu của Hackathon (đáp ứng đồng thời cả **Chuẩn A — Khảo sát** và **Chuẩn B — Mining Data**), nhóm D305 áp dụng phương pháp kết hợp:

1. **Khảo sát trực tiếp (Survey):** Khảo sát độc lập $n = 28$ học viên ngoài nhóm trong kênh Discord và zone lớp học.
2. **Khai thác dữ liệu Discord (Chatlog Sampling):** Lấy mẫu ngẫu nhiên và phân loại $n = 100$ câu hỏi thực tế của học viên trên kênh chat Discord của khóa học AI Thực Chiến.

---

## 2. Chi tiết Thu thập & Cỡ mẫu (Sampling Details)

### 2.1 Khảo sát Học viên ($n = 28$)
- **Phương pháp lấy mẫu:** Thu thập mẫu ngẫu nhiên từ học viên đang tham gia khóa học trong giờ giải lao và trên kênh Discord chính thức.
- **Tiêu chí xác nhận pain:** Học viên xác nhận đã từng (1) bị trả lời chậm/sai thông tin logistics, (2) phải chờ TA làm rõ câu hỏi mơ hồ, hoặc (3) tự bối rối khi không biết hỏi ai.
- **Kết quả:** $20 / 28$ học viên (**71.4%**) xác nhận gặp nỗi đau này tần suất hàng tuần.

### 2.2 Chatlog Discord Sampling ($n = 100$)
- **Nguồn dữ liệu:** Kênh Discord khóa học AI Thực Chiến (đã loại bỏ toàn bộ thông tin cá nhân như Username, Avatar, ID).
- **Tiêu chí phân loại (Counting Criteria):**
  - `greeting`: Tin nhắn chỉ chứa câu chào hỏi, chúc mừng.
  - `learning`: Hỏi về kiến thức lập trình, bài tập, lỗi code Python/Streamlit.
  - `logistics`: Hỏi về hạn nộp bài, link nộp bài, lịch học, tài nguyên khóa học.
  - `ambiguous`: Tin nhắn quá ngắn (ví dụ "Lỗi này sửa sao?", "Cái này làm thế nào?") không kèm traceback hoặc mã bài.
  - `out_of_scope`: Đòi đáp án hoàn chỉnh, nhờ làm hộ bài tập, hoặc xin API Key/Token.

#### Bảng Thống kê Phân bổ Intent ($n = 100$):

| Intent Group | Số lượng tin nhắn | Tỷ lệ (%) | Phản hồi hiện tại của TA / Bot | Hậu quả quan sát được |
|---|---:|---:|---|---|
| **Learning** (Hỏi bài) | 42 | 42.0% | TA trả lời / bạn học hỗ trợ | Chờ đợi 15–45 phút |
| **Logistics** (Deadline/Link) | 28 | 28.0% | Trả lời thủ công / hỏi lại | Dễ bị trôi tin nhắn, nộp muộn |
| **Ambiguous** (Thiếu context) | 18 | 18.0% | TA phải hỏi lại 2-3 câu | Tốn thời gian làm rõ context |
| **Greeting** (Chào hỏi) | 8 | 8.0% | Không phản hồi hoặc trả lời ngắn | Thất lạc tin |
| **Out of Scope** (Ngoài phạm vi) | 4 | 4.0% | Từ chối hoặc nhắc nhở | Gây xao nhãng kênh chat |

---

## 3. Ít nhất 5 Trích dẫn Nguyên văn (Anonymized Quotes)

1. **Quote #1 (Logistics):** *"Anh ơi deadline Checkpoint 3 chốt 23:59 hôm nay hay trưa mai vậy ạ, em tìm trên Discord thấy 2 link thông báo khác nhau?"*
   - *Mã mẫu:* `DC-MINING-014`
   - *Phân loại:* `logistics`
2. **Quote #2 (Ambiguous):** *"Em bị lỗi code rồi giúp em với ạ"* (Không gửi kèm screenshot hay đoạn code lỗi).
   - *Mã mẫu:* `DC-MINING-027`
   - *Phân loại:* `ambiguous`
3. **Quote #3 (Learning):** *"Cho mình hỏi làm sao để truyền session state qua các page khác nhau trong Streamlit vậy mọi người?"*
   - *Mã mẫu:* `DC-MINING-041`
   - *Phân loại:* `learning`
4. **Quote #4 (Out of Scope):** *"Bạn ơi viết hộ mình cả file app.py cho bài toán này với, mình bận quá"*
   - *Mã mẫu:* `DC-MINING-063`
   - *Phân loại:* `out_of_scope`
5. **Quote #5 (Logistics + Greeting):** *"Chào TA, cho em xin lại link submit bài tập nhóm D305 với ạ"*
   - *Mã mẫu:* `DC-MINING-082`
   - *Phân loại:* `logistics` (ghép intent chào hỏi, ưu tiên logistics vì có hậu quả nộp bài).

---

## 6. Phân tích Hạn chế và Biến số Bias (Limitations & Biases)

1. **Sampling Bias (Lệch mẫu khảo sát):** Mẫu khảo sát $n=28$ tập trung vào học viên online tích cực hoạt động trong ngày thi Hackathon, có thể đánh giá nỗi đau cao hơn nhóm học viên ít tương tác.
2. **Time-of-day Bias (Bias thời điểm):** Tỷ lệ câu hỏi `logistics` tăng vọt vào 2-3 tiếng trước các mốc Checkpoint cứng.
3. **Anonymization Boundary:** Dữ liệu trích dẫn chỉ lưu dạng mã hóa ký hiệu (`DC-MINING-XXX`), không lưu tên tài khoản Discord để bảo đảm an toàn dữ liệu theo quy định của cuộc thi.
