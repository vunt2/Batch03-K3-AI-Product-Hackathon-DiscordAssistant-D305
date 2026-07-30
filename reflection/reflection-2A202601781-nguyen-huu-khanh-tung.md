# Reflection — Nguyễn Hữu Khánh Tùng (2A202601781)

> Trạng thái: Bản nháp — thành viên cần đọc, xác nhận và chỉnh lại theo trải nghiệm thực tế trước khi nộp.

## Vai trò của tôi

Tôi phụ trách AI Integration, kết nối Gemini với ứng dụng Streamlit. Tôi làm cho model client, intent engine, cấu hình môi trường và fallback hoạt động thống nhất. Ngoài việc model trả lời được, tôi phải bảo đảm lỗi mạng, lỗi JSON hoặc thiếu cấu hình không làm app crash hay tạo câu trả lời logistics thiếu nguồn.

## Phần tôi phụ trách

Tôi triển khai Gemini model client, đọc `.env`, kết nối intent engine với prompt và đưa kết quả đã validate vào hai giao diện. Tôi xử lý timeout, HTTP error, JSON lỗi và thiếu key bằng safety fallback. Contract và metadata giúp UI phân biệt real call với fallback. Tôi không để key xuất hiện trong log, exception, trace hoặc UI. Knowledge workflow và ứng dụng là kết quả chung của nhóm.

## AI đã hỗ trợ tôi như thế nào

AI giúp tôi phác thảo client, rà nhánh exception, tạo mock lỗi và đối chiếu output với contract. Khi response khác dự kiến, AI hỗ trợ đọc cấu trúc lỗi và làm sạch message trước khi ghi metadata. Tôi vẫn tự đọc code, kiểm tra môi trường và xác nhận không có secret trong artifact.

## Quyết định và phần tôi phải tự kiểm tra

Tôi tự quyết định timeout, điểm chuyển fallback và metadata an toàn. Tôi kiểm tra Gemini thật và fallback cùng đi qua validator, UI không nhận raw response, logistics không nguồn được handoff và exception không chứa credential. Tôi cũng phân biệt lỗi code, model, credential, quota hay network trước khi kết luận tích hợp hoạt động.

## Một case fail và bài học

Smoke test từng bị chặn bởi Gemini HTTP 400, credential hoặc timeout. Có API key không đồng nghĩa request chắc chắn thành công; demo chỉ dựa vào happy path rất dễ vỡ. Tôi học rằng lớp AI cần timeout, validator, fallback và metadata từ đầu. Báo cáo phải nói rõ fallback không phải real model call để tránh nhầm với kiểm thử live.

## Điều tôi muốn cải thiện

Tôi muốn làm rõ mã lỗi đã làm sạch và quan sát từng bước request mà không lộ dữ liệu nhạy cảm. Tôi cũng muốn giảm phụ thuộc giữa UI và model client nhưng giữ kiến trúc vừa đủ. Sau CP5, tôi sẽ xem lỗi thực tế có liên quan đến độ trễ, fallback hoặc cách UI giải thích trạng thái hay không.

## Bổ sung sau CP5

- [ ] Bổ sung một phản hồi thực tế từ user test.
- [ ] Ghi thay đổi nhóm thực hiện sau feedback.
- [ ] Xác nhận thành viên đã đọc và có thể giải thích nội dung reflection.
