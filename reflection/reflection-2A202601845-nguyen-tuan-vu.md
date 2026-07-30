# Reflection — Nguyễn Tuấn Vũ (2A202601845)

> Trạng thái: Bản nháp — thành viên cần đọc, xác nhận và chỉnh lại theo trải nghiệm thực tế trước khi nộp.

## Vai trò của tôi

Tôi là nhóm trưởng và phụ trách Prompt & Safety. Tôi điều phối tích hợp, xây dựng prompt contract, output validator và safety routing. Mục tiêu là giữ quyết định AI đúng phạm vi: trả lời khi có cơ sở, hỏi lại khi mơ hồ, từ chối yêu cầu làm hộ và chuyển Labcoach khi logistics thiếu nguồn tin cậy.

## Phần tôi phụ trách

Tôi định nghĩa intent, action và JSON model phải trả về, rồi phối hợp model client và UI để contract nhất quán. Tôi xây dựng quy tắc cho logistics thiếu nguồn, ngoài phạm vi, dữ liệu nhạy cảm và confidence thấp. Output sai định dạng phải sang fallback. Tôi theo dõi liên kết giữa evidence, knowledge, AI và eval; toàn bộ code vẫn là kết quả chung.

## AI đã hỗ trợ tôi như thế nào

AI giúp tôi tạo phiên bản prompt, liệt kê rủi ro và sinh output xấu để thử validator. Nó hỗ trợ so sánh action giữa prompt, test và UI để tìm contract cũ. Tôi dùng AI để phản biện và tạo bản nháp; quyết định safety vẫn phải đối chiếu spec, nguồn approved và hành vi thật.

## Quyết định và phần tôi phải tự kiểm tra

Tôi tự xác nhận intent/action hợp lệ, điều kiện handoff và fallback không bịa logistics. Tôi kiểm tra không có API key hay dữ liệu nhạy cảm trong prompt, trace và test. Tôi còn theo dõi provenance: reply, Knowledge ID và Source ID phải cùng chủ đề. Reply an toàn nhưng nguồn sai vẫn là lỗi.

## Một case fail và bài học

Case “Nhà ăn đóng cửa lúc mấy giờ?” cho thấy bot không bịa giờ, nhưng UI lại hiện nhầm nguồn Build Phase do trùng từ thời gian chung. Nếu chỉ đọc reply, hệ thống có vẻ đúng; provenance mới làm lộ lỗi. Tôi học rằng retrieval cần anchor đúng chủ đề, còn Knowledge ID và Source ID phải đúng trước khi gắn nhãn “Nguồn đã được xác minh”.

## Điều tôi muốn cải thiện

Tôi muốn đưa provenance thành điều kiện bắt buộc trong eval, không chỉ so intent và action. Mỗi thay đổi contract cần được rà ở prompt, validator, model client, UI và golden set. Sau CP5, tôi sẽ dùng phản hồi thật để xem handoff, thông báo nguồn và lời từ chối có dễ hiểu hay không.

## Bổ sung sau CP5

- [ ] Bổ sung một phản hồi thực tế từ user test.
- [ ] Ghi thay đổi nhóm thực hiện sau feedback.
- [ ] Xác nhận thành viên đã đọc và có thể giải thích nội dung reflection.
