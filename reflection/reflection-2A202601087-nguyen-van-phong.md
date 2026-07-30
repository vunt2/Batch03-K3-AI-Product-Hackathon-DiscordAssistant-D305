# Reflection — Nguyễn Văn Phong (2A202601087)

> Trạng thái: Bản nháp — thành viên cần đọc, xác nhận và chỉnh lại theo trải nghiệm thực tế trước khi nộp.

## Vai trò của tôi

Tôi phụ trách Evaluation, biến yêu cầu an toàn trong spec thành các trường hợp kiểm tra có thể chạy lại. Tôi tập trung vào golden set, eval runner, cách ghi nhận kết quả và phân tích case fail. Đánh giá không chỉ tạo điểm số mà phải chỉ ra hệ thống sai ở đâu và điều kiện cứng nào chưa đạt.

## Phần tôi phụ trách

Tôi xây dựng golden set, chuẩn hóa expected intent/action, chạy eval và lưu đủ PASS, FAIL, FALLBACK. Lần chạy Gemini thật đạt 20/22, tương đương 90,9%. Tôi tách nhóm logistics và out-of-scope để đối chiếu Quality Bar, đồng thời ghi từng case fail. Tôi bảo đảm không sửa expected output sau khi thấy kết quả và không ghi đè lịch sử.

## AI đã hỗ trợ tôi như thế nào

AI hỗ trợ rà schema golden set, gợi ý biến thể câu hỏi và tổng hợp log. Nó giúp so sánh actual với expected, nhận diện nhóm lỗi và tạo bản nháp nguyên nhân. Tuy nhiên, AI không được tự quyết định PASS hay đổi tiêu chí; kết luận phải dựa trên Quality Bar, output đã lưu và hành vi an toàn.

## Quyết định và phần tôi phải tự kiểm tra

Tôi tự kiểm tra đủ 22 dòng, metadata, mẫu số từng nhóm và việc mọi case đều được ghi nhận. Tôi xác nhận logistics có nguồn phù hợp, out-of-scope được xử lý đúng và fallback không bị tính nhầm thành PASS. Câu hỏi thực tế phải giữ `source_type` và `source_ref` để truy được nguồn.

## Một case fail và bài học

Hệ thống đạt 20/22, tức 90,9%, nhưng logistics chỉ đạt 5/6 nên quyết định vẫn là HOLD. Một câu logistics sai có thể gây hậu quả lớn hơn nhiều câu thường đúng. Tôi học rằng tỷ lệ tổng thể cao không thay thế hard safety condition. Báo cáo phải nêu cả hai số, không được nói logistics 100% hoặc CP5 đã hoàn tất.

## Điều tôi muốn cải thiện

Tôi muốn phân loại severity cho case fail và báo cáo provenance rõ hơn. Eval runner nên làm nổi bật điều kiện cứng cạnh điểm tổng để người đọc không bỏ qua. Sau CP5, tôi muốn so sánh golden set với phản hồi user test thật để nhận ra kiểu diễn đạt hoặc tình huống còn thiếu.

## Bổ sung sau CP5

- [ ] Bổ sung một phản hồi thực tế từ user test.
- [ ] Ghi thay đổi nhóm thực hiện sau feedback.
- [ ] Xác nhận thành viên đã đọc và có thể giải thích nội dung reflection.
