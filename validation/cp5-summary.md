# CP5 Validation Summary — Team D305

## Kết quả

Năm learner ngoài nhóm đã dùng Learner View, mỗi người đặt 5 câu hỏi tùy ý.
Đánh giá chung được người điều phối ghi nhận là flow chính dùng được. Vấn đề
lặp lại nổi bật nhất là câu chào, câu trend hoặc casual chat vô hại đôi khi bị
định tuyến quá cứng và chuyển Labcoach không cần thiết.

Vòng thử chưa có Labcoach thật. Vì queue dùng SQLite cục bộ theo từng máy,
nhóm cũng chưa tuyên bố đã kiểm chứng workflow nhiều thiết bị hoặc queue dùng
chung.

## Thay đổi thực hiện trước demo

1. Mở rộng `greeting` cho lời chào, cảm ơn, gọi bot, trend và casual chat vô
   hại; thêm guard để những câu này không tạo handoff.
2. Làm giọng trả lời tự nhiên hơn, cho phép tối đa 1–2 emoji phù hợp nhưng
   không nới lỏng logistics safety.
3. Nhớ tên khi learner chủ động tự giới thiệu; tên chỉ nằm trong Streamlit
   session, bị xóa khi reset và không được ghi vào SQLite/knowledge.
4. Giữ nguyên năm intent, bốn action, output validator và quy tắc logistics
   chỉ dùng approved knowledge.

## Xác minh kỹ thuật sau thay đổi

- Unit test: 150/150 PASS.
- Streamlit AppTest: 0 exception.
- `git diff --check`: PASS.
- Golden eval live lịch sử vẫn là 20/22; nhóm không chạy lại và không sửa
  Quality Bar sau khi nhìn thấy kết quả.

## Giữ nguyên có lý do

- Không lưu danh tính lâu dài: chưa cần cho lát cắt demo và có rủi ro riêng tư.
- Không tự động publish phản hồi Labcoach: mọi candidate vẫn cần duyệt.
- Không làm queue nhiều máy: ngoài phạm vi prototype CP5.

## Backlog

- Mời Labcoach thật thử queue, phản hồi và review/publish workflow.
- Khi có consent, thu quote nguyên văn và vai trò theo từng người thử.
- Nếu phát triển production, thiết kế authentication, shared database và chính
  sách lưu/xóa profile trước khi thêm persistent user memory.

## Trạng thái dry run

Demo script 5 phút đã được chốt tại `validation/demo-script.md`. Nhóm chưa cung
cấp log xác nhận đã chạy thử đủ một lượt có bấm giờ, nên tài liệu này không tuyên
bố dry run đã hoàn tất.
