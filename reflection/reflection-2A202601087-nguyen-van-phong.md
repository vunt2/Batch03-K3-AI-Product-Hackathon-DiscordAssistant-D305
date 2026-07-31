# Reflection — Nguyễn Văn Phong (2A202601087)

## Vai trò của tôi

Tôi phụ trách Evaluation, biến yêu cầu an toàn trong spec thành các trường hợp kiểm tra có thể chạy lại. Tôi tập trung vào golden set, eval runner, cách ghi nhận kết quả và phân tích case fail. Đánh giá không chỉ tạo điểm số mà phải chỉ ra hệ thống sai ở đâu và điều kiện cứng nào chưa đạt.

## Phần tôi phụ trách

Tôi xây dựng golden set, chuẩn hóa expected intent/action, chạy eval và lưu đủ PASS, FAIL, FALLBACK. Lần chạy Gemini thật đạt 20/22, tương đương 90,9%. Tôi tách nhóm logistics và out-of-scope để đối chiếu Quality Bar, đồng thời ghi từng case fail. Tôi bảo đảm không sửa expected output sau khi thấy kết quả và không ghi đè lịch sử.

## AI đã hỗ trợ tôi như thế nào

AI hỗ trợ rà schema golden set, gợi ý biến thể câu hỏi và tổng hợp log. Nó giúp so sánh actual với expected, nhận diện nhóm lỗi và gợi ý nguyên nhân cần kiểm tra. Tuy nhiên, AI không được tự quyết định PASS hay đổi tiêu chí; kết luận phải dựa trên Quality Bar, output đã lưu và hành vi an toàn.

## Quyết định và phần tôi phải tự kiểm tra

Tôi tự kiểm tra đủ 22 dòng, metadata, mẫu số từng nhóm và việc mọi case đều được ghi nhận. Tôi xác nhận logistics có nguồn phù hợp, out-of-scope được xử lý đúng và fallback không bị tính nhầm thành PASS. Câu hỏi thực tế phải giữ `source_type` và `source_ref` để truy được nguồn.

## Một case fail và bài học

Hệ thống đạt 20/22, tức 90,9%, nhưng logistics chỉ đạt 5/6 nên quyết định vẫn là HOLD. Một câu logistics sai có thể gây hậu quả lớn hơn nhiều câu thường đúng. Tôi học rằng tỷ lệ tổng thể cao không thay thế hard safety condition. Báo cáo phải nêu cả hai số, không được nói logistics 100% hoặc CP5 đã hoàn tất.

## Kết quả sau CP5

Phản hồi của 5 learner cho thấy golden set ban đầu chưa phản ánh đủ lời chào
theo trend và casual chat. Nhóm bổ sung regression test cho casual routing,
session name và contract fallback. Sau thay đổi, toàn bộ 150 unit test đạt.
Đây là kiểm tra hồi quy code, không thay thế golden eval live; kết quả chính
thức 20/22 và trạng thái HOLD vẫn được giữ nguyên.

## Điều tôi muốn cải thiện

Tôi muốn phân loại severity cho case fail và báo cáo provenance rõ hơn. Eval
runner nên làm nổi bật điều kiện cứng cạnh điểm tổng. Lượt eval tiếp theo cần
bổ sung biến thể casual thật từ validation nhưng vẫn phải chốt expected trước
khi chạy và giữ nguyên kết quả lịch sử.
