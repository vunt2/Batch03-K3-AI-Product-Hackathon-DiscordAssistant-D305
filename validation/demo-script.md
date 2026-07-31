# Demo Script — Team D305

## Mục tiêu

Trình bày trong 5 phút lát cắt **Answer-or-Handoff**: một learner đặt câu hỏi,
AI phân loại intent và chọn hành động; câu có nguồn được trả lời, câu thiếu căn
cứ được chuyển Labcoach thay vì bịa thông tin.

## Phân công nói

| Thời gian | Thành viên | Nội dung |
|---:|---|---|
| 0:00–0:35 | Nguyễn Phúc Hưng | Pain, evidence khảo sát và chatlog |
| 0:35–1:10 | Nguyễn Tuấn Vũ | Lát cắt, quyết định AI và nguyên tắc an toàn |
| 1:10–2:55 | Nguyễn Hữu Khánh Tùng | Demo live Learner View và Labcoach View |
| 2:55–3:40 | Nguyễn Văn Phong | Golden eval, quality bar và case fail |
| 3:40–4:25 | Nguyễn Phúc Hưng | Validation với 5 learner và thay đổi sau feedback |
| 4:25–5:00 | Nguyễn Tuấn Vũ | Giới hạn hiện tại, backlog và bài học |

## Hai case demo live

### Case chuẩn — có nguồn approved

1. Mở Learner View.
2. Nhập: `Một người hay cả team phải nộp weekly report?`
3. Kết quả cần chỉ ra:
   - bot trả lời từ approved knowledge;
   - giao diện hiển thị Knowledge ID và Source ID;
   - câu trả lời không tự bổ sung deadline, link hoặc dữ kiện ngoài nguồn.

### Case khó — logistics không có nguồn

1. Nhập: `Nhà ăn đóng cửa lúc mấy giờ?`
2. Kết quả cần chỉ ra:
   - bot nói không có nguồn chính thức;
   - action là chuyển Labcoach;
   - câu hỏi xuất hiện trong handoff queue.
3. Chuyển sang Labcoach View để cho thấy câu hỏi, lý do handoff và trace.

## Số liệu phải nói đúng

- Khảo sát: 20 response, gồm 18 learner và 2 TA/Labcoach.
- Discord mining: 88 message, trong đó có 56 learner question.
- Golden eval live lịch sử: 20/22, tương đương 90,9%.
- Điều kiện cứng logistics: 5/6, nên Quality Bar vẫn **HOLD**.
- Validation CP5: 5 learner ngoài nhóm, mỗi người đặt 5 câu hỏi.
- Chưa có Labcoach thật tham gia validation.
- Feedback CP5 không còn mapping tên/quote theo từng người; không tuyên bố đã
  đạt trọn tiêu chí quote có tên.

## Phương án dự phòng

- Nếu Gemini lỗi hoặc timeout, giải thích đây là safety fallback và không gọi
  đó là live model output.
- Nếu API key không dùng được, vẫn demo được retrieval, handoff queue và luồng
  Labcoach bằng fallback an toàn.
- Không mở `.env`, API key, database thô hoặc dữ liệu nhận dạng trong lúc demo.

## Checklist trước khi bấm giờ

- Chạy ứng dụng từ thư mục `codebase`.
- Kiểm tra Gemini Ready và knowledge đã load.
- Xóa dữ liệu phiên demo cũ.
- Mở sẵn `presentation.html` và ứng dụng Streamlit.
- Mỗi thành viên tự giải thích được phần có tên mình.
- Chạy thử một lượt có bấm giờ; ghi kết quả thực tế bên ngoài repo nếu chưa có
  sự đồng ý lưu tên người tham gia.
