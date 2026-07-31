# Reflection — Nguyễn Tuấn Vũ (2A202601845)

## Vai trò của tôi

Tôi là nhóm trưởng và phụ trách Prompt & Safety. Tôi điều phối tích hợp, xây dựng prompt contract, output validator và safety routing. Mục tiêu là giữ quyết định AI đúng phạm vi: trả lời khi có cơ sở, hỏi lại khi mơ hồ, từ chối yêu cầu làm hộ và chuyển Labcoach khi logistics thiếu nguồn tin cậy.

## Phần tôi phụ trách

Tôi định nghĩa intent, action và JSON model phải trả về, rồi phối hợp model client và UI để contract nhất quán. Tôi xây dựng quy tắc cho logistics thiếu nguồn, ngoài phạm vi, dữ liệu nhạy cảm và confidence thấp. Output sai định dạng phải sang fallback. Tôi theo dõi liên kết giữa evidence, knowledge, AI và eval; toàn bộ code vẫn là kết quả chung.

## AI đã hỗ trợ tôi như thế nào

AI giúp tôi tạo phiên bản prompt, liệt kê rủi ro và sinh output xấu để thử validator. Nó hỗ trợ so sánh action giữa prompt, test và UI để tìm contract cũ. Tôi dùng AI để phản biện và tạo gợi ý ban đầu; quyết định safety vẫn phải đối chiếu spec, nguồn approved và hành vi thật.

## Quyết định và phần tôi phải tự kiểm tra

Tôi tự xác nhận intent/action hợp lệ, điều kiện handoff và fallback không bịa logistics. Tôi kiểm tra không có API key hay dữ liệu nhạy cảm trong prompt, trace và test. Tôi còn theo dõi provenance: reply, Knowledge ID và Source ID phải cùng chủ đề. Reply an toàn nhưng nguồn sai vẫn là lỗi.

## Một case fail và bài học

Case “Nhà ăn đóng cửa lúc mấy giờ?” cho thấy bot không bịa giờ, nhưng UI lại hiện nhầm nguồn Build Phase do trùng từ thời gian chung. Nếu chỉ đọc reply, hệ thống có vẻ đúng; provenance mới làm lộ lỗi. Tôi học rằng retrieval cần anchor đúng chủ đề, còn Knowledge ID và Source ID phải đúng trước khi gắn nhãn “Nguồn đã được xác minh”.

## Kết quả sau CP5

Feedback từ 5 learner cho thấy safety đúng nhưng cách định tuyến casual còn quá
cứng. Tôi giữ nguyên taxonomy và logistics guard, đồng thời mở rộng prompt cho
casual/trend, cho phép tối đa 1–2 emoji và thêm session profile chỉ để xưng hô.
Một regression phát sinh khi casual guard ghi đè contract fallback đã được
phát hiện và sửa: JSON lỗi vẫn phải đi theo fallback an toàn. Sau sửa, 150/150
unit test đạt và Streamlit AppTest không có exception.

## Điều tôi muốn cải thiện

Tôi muốn đưa provenance thành điều kiện bắt buộc trong eval, không chỉ so
intent và action. Vòng validation tiếp theo cần có Labcoach thật để kiểm tra
queue, nội dung handoff và quy trình duyệt knowledge; self-test của team không
được dùng làm nguồn approved.
