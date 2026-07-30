# Phương pháp Khai thác Dữ liệu Discord & Khảo sát Học viên (Evidence Methodology)

## 1. Tổng quan Phương pháp (Combined Methodology)

Để xây dựng căn cứ minh chứng đạt tiêu chuẩn nghiệm thu của Hackathon (đáp ứng đồng thời cả **Chuẩn A — Khảo sát** và **Chuẩn B — Mining Data**), nhóm D305 áp dụng phương pháp kết hợp:

1. **Khảo sát trực tiếp (Survey):** Khảo sát độc lập $n = 20$ phản hồi (18 learner, 2 TA). Tất cả 20 người đã được nhóm xác minh thủ công là ngoài nhóm D305 (chưa có trường dữ liệu độc lập chứng minh eligibility).
2. **Khai thác dữ liệu Discord (Chatlog Mining):** Trích xuất và phân loại $n = 88$ message Discord đã trích xuất từ [`data/processed/discord/messages-anonymized.csv`](../data/processed/discord/messages-anonymized.csv).

---

## 2. Chi tiết Thu thập & Cỡ mẫu (Sampling Details)

### 2.1 Khảo sát Học viên ($n = 20$)
- **Phương pháp lấy mẫu:** Thu thập mẫu ngẫu nhiên từ học viên và Trợ giảng (18 learner, 2 TA) qua biểu mẫu khảo sát trực tuyến.
- **Tiêu chí xác nhận pain:** 10/18 learner ($55.6\%$) xác nhận vướng phải tình huống câu hỏi không được trả lời hoặc trùng lặp (`pain_confirmed_draft`).
- **Xác minh eligibility:** Nhóm đã đối chiếu danh sách thủ công để bảo đảm 20/20 người phản hồi ngoài nhóm D305. Vì chưa có trường thông tin định danh độc lập trong dataset khảo sát nên trạng thái ghi nhận là `UNVERIFIED` theo tiêu chuẩn guide.

### 2.2 Chatlog Discord Sampling ($n = 88$ message Discord đã trích xuất)
- **Nguồn dữ liệu:** Kênh Discord khóa học (`data/processed/discord/messages-anonymized.csv`, đã loại bỏ thông tin cá nhân).
- **Cơ cấu loại Message (`message_type`):**
  - `question`: 56 message (63.6%)
  - `answer`: 26 message (29.5%)
  - `announcement`: 5 message (5.7%)
  - `follow_up`: 1 message (1.1%)
- **Cơ cấu vai trò người gửi (`speaker_role`):**
  - `learner`: 57 message (64.8%)
  - `unknown / chưa xác định vai trò`: 22 message (25.0%)
  - `labcoach`: 7 message (8.0%)
  - `official_announcement`: 2 message (2.3%)

#### Bảng Thống kê Chủ đề (`topic`) Phân loại cho 56 Câu hỏi (`message_type = question`):

| Chủ đề (`topic`) | Số lượng câu hỏi | Tỷ lệ (%) | Mô tả sơ bộ |
|---|---:|---:|---|
| `course_policy` | 11 | 19.6% | Quy định khóa học, xin nghỉ, điểm danh |
| `team_workflow` | 10 | 17.9% | Phân chia nhóm, mã nhóm, chung nhóm giữa các khóa |
| `github` | 9 | 16.1% | Lời mời GitHub Org, tài khoản, xác thực |
| `schedule` | 6 | 10.7% | Lịch học, hoạt động online buổi tối, giờ nhà ăn |
| `submission` | 6 | 10.7% | Lệnh /weekly submit, định dạng báo cáo tuần |
| `technical_setup` | 5 | 8.9% | Lỗi kết nối Git, Wi-Fi, xem slide, gửi ticket |
| `deadline` | 3 | 5.4% | Thời hạn tạo team, hạn nộp các checkpoint |
| `api_key` | 3 | 5.4% | Hướng dẫn submit AI log, tạo API key |
| `checkpoint` | 2 | 3.6% | Đăng ký và đổi đề tài thi / checkpoint |
| `other` | 1 | 1.8% | Câu hỏi khác chưa phân loại |
| **Tổng cộng** | **56** | **100.0%** | **Đúng 56 câu hỏi trong CSV** |

*(Ghi chú: Đối với toàn bộ 88 message trong CSV, cơ cấu chủ đề gồm: 19 `course_policy`, 13 `team_workflow`, 12 `submission`, 11 `github`, 10 `schedule`, 7 `technical_setup`, 5 `deadline`, 4 `api_key`, 4 `checkpoint`, 3 `other` — tổng đúng 88).*

---

## 3. Trích dẫn Nguyên văn từ Dataset (`messages-anonymized.csv`)

Tất cả 5 quote bên dưới được chép đúng nguyên văn đã ẩn danh (`text_redacted`) kèm theo `message_id`, `image_id`, `speaker_role` và `topic` từ file CSV:

1. **Quote #1 (`MSG-004-01`):** *"Đến bước xác thực lời mời GitHub Org nhưng kiểm tra điện thoại và máy tính đều không thấy lời mời; cần làm gì?"*
   - *Message ID:* `MSG-004-01` | *Image ID:* `IMG-004`
   - *Speaker Role:* `learner` | *Message Type:* `question` | *Topic:* `github`
2. **Quote #2 (`MSG-007-01`):** *"Thành viên khóa 3 và khóa 4 có thể chung nhóm không?"*
   - *Message ID:* `MSG-007-01` | *Image ID:* `IMG-007`
   - *Speaker Role:* `learner` | *Message Type:* `question` | *Topic:* `team_workflow`
3. **Quote #3 (`MSG-010-01`):** *"Weekly submit gồm những gì?"*
   - *Message ID:* `MSG-010-01` | *Image ID:* `IMG-010`
   - *Speaker Role:* `learner` | *Message Type:* `question` | *Topic:* `submission`
4. **Quote #4 (`MSG-020-01`):** *"Thời hạn tạo team là đến bao giờ?"*
   - *Message ID:* `MSG-020-01` | *Image ID:* `IMG-020`
   - *Speaker Role:* `learner` | *Message Type:* `question` | *Topic:* `deadline`
5. **Quote #5 (`MSG-024-01`):** *"Các buổi tối có phải luôn hoạt động online không, và học viên có được thông báo trước không?"*
   - *Message ID:* `MSG-024-01` | *Image ID:* `IMG-024`
   - *Speaker Role:* `learner` | *Message Type:* `question` | *Topic:* `schedule`

---

## 4. Phân tích Hạn chế và Biến số Bias (Limitations & Biases)

1. **Sampling Bias (Lệch mẫu khảo sát):** Mẫu khảo sát $n=20$ (18 learner, 2 TA) là tự báo cáo (self-reported), người phản hồi có thể đánh giá nỗi đau cao hơn nhóm ít tương tác.
2. **Temporal Bias:** Dataset không có timestamp chuẩn hóa, vì vậy nhóm chưa thể kết luận tần suất câu hỏi thay đổi theo thời điểm trong ngày hoặc theo khoảng cách đến deadline.
3. **Eligibility Verification Limit:** Chưa có trường dữ liệu định danh độc lập trong survey dataset; việc xác minh 20/20 người ngoài team hiện dựa trên kiểm tra thủ công của nhóm.
