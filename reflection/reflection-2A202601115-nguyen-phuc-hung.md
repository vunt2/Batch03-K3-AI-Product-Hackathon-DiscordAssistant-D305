# Reflection — Nguyễn Phúc Hưng (2A202601115)

## Vai trò của tôi

Tôi phụ trách Evidence & Product Specification. Vai trò của tôi là biến quan sát ban đầu thành bằng chứng có thể kiểm tra, rồi liên kết chúng với vấn đề, tác động và phạm vi sản phẩm. Tôi theo dõi tính nhất quán giữa spec và artifact thực tế, đồng thời phân biệt dữ liệu đã xác minh, tín hiệu định hướng và claim chưa đủ bằng chứng.

## Phần tôi phụ trách

Tôi tổng hợp khảo sát 20 phản hồi, gồm 18 learner và 2 TA, đồng thời xây dựng survey summary, evidence, impact analysis, CP checklist và các phần liên quan trong spec. Tôi ghi rõ mẫu số, giới hạn của mẫu và rà soát claim cần đánh dấu `UNVERIFIED`. Tôi còn phối hợp đưa kết quả AI và eval vào tài liệu mà không làm sai ý nghĩa số liệu.

## AI đã hỗ trợ tôi như thế nào

AI giúp tôi nhóm phản hồi khảo sát, đề xuất cấu trúc bảng evidence và kiểm tra sự nhất quán giữa các file. Công cụ còn phát hiện chỗ thiếu mẫu số và gợi ý câu hỏi phản biện cho kết luận quá mạnh. Tôi chỉ dùng kết quả như gợi ý để rà soát, không coi đó là bằng chứng mới.

## Quyết định và phần tôi phải tự kiểm tra

Tôi tự xác nhận tổng phản hồi, cơ cấu 18 learner và 2 TA, nguồn số liệu và giới hạn suy rộng. Tôi quyết định claim nào đủ cơ sở, claim nào chỉ là tín hiệu và claim nào phải giữ `UNVERIFIED`. Tôi cũng kiểm tra kết quả eval từ artifact thật, không biến trạng thái HOLD thành đạt vì điểm tổng cao.

## Một case fail và bài học

Tài liệu cũ từng có claim “28 người” và “100 tin nhắn” nhưng chưa có artifact đủ để chứng minh. Nếu giữ lại, các số cụ thể sẽ tạo cảm giác chắc chắn giả. Tôi học rằng bằng chứng cần nguồn, mẫu số và giới hạn sử dụng; tín hiệu từ mẫu nhỏ không phải kết luận chắc chắn cho toàn bộ learner. Khi chưa truy được nguồn, phải sửa hoặc đánh dấu `UNVERIFIED`.

## Kết quả sau CP5

Năm learner ngoài nhóm đã thử Learner View và đánh giá chung flow chính dùng
được. Phản hồi tổng hợp cho thấy casual chat còn bị định tuyến cứng, câu trả
lời ít vui vẻ, ít emoji và chưa nhớ tên trong phiên. Nhóm đã sửa các điểm này
và lưu quyết định tại `validation/`. Vì người điều phối không lưu tên và quote
riêng cho từng learner, tôi giữ giới hạn đó trong feedback log thay vì tạo dữ
liệu bổ sung. Vòng thử cũng chưa có Labcoach thật.

## Điều tôi muốn cải thiện

Tôi muốn xây dựng quy ước provenance để mỗi claim liên kết với câu hỏi khảo
sát, dòng dữ liệu hoặc kết quả eval. Ở vòng validation tiếp theo, biểu mẫu phải
ghi tên/vai, consent, quan sát và quote ngay trong từng phiên để bằng chứng
không bị mất mapping sau khi tổng hợp.
