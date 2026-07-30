# Survey Summary

## Dataset

- File nguồn: `Khảo sát AI Agent hỗ trợ học tập trên Discord (Câu trả lời) - Câu trả lời biểu mẫu 1.csv` (giữ nguyên, đã thêm vào `.gitignore`).
- Thời gian khảo sát: 30/07/2026; timestamp chính xác đã loại khỏi artifact.
- Tổng response: 20.
- Learner: 18.
- TA/Labcoach: 2.
- Eligibility status: `UNVERIFIED` — chưa xác minh tất cả respondent ngoài team.
- PII status: không phát hiện email, số điện thoại, URL hay Discord identifier
  theo pattern. Agent đã đọc semantic toàn bộ 7 câu Q17 có nội dung và xác nhận
  Q27 có 0 response; không thấy định danh trực tiếp hoặc ngữ cảnh có thể suy
  ngược rõ ràng. Dùng mã R001–R020. Phạm vi review này không phải cam kết
  “PII-safe tuyệt đối” và vẫn cần human sign-off trước khi công khai.

## Method

- Filter role trước mọi thống kê; learner denominator 18, TA denominator 2.
- Giữ giá trị gốc đã làm sạch và tạo scale/multi-select normalized riêng.
- Blanks do branching là `NOT_APPLICABLE`, không đưa vào denominator.
- Multi-select được tách thành từng lựa chọn và đếm respondent duy nhất.
- `pain_confirmed_draft` dùng đúng tiêu chí đã chốt trong codebook.
- Preference giải pháp được trình bày riêng, không dùng để chứng minh pain.

## Learner findings

### Pain draft và chỉ số hành vi

| Chỉ số | Kết quả |
|---|---:|
| pain_confirmed_draft | 10/18 (55,6%) |
| Đã hỏi lại câu hỏi cũ ở mức ≥4 | 6/18 (33,3%) |
| Đã từng từ bỏ tìm kiếm | 15/18 (83,3%) |
| Mất trên 5 phút để tìm thông tin | 4/18 (22,2%) |
| Khó theo dõi hội thoại dài ở mức ≥4 | 13/18 (72,2%) |

### Tần suất sử dụng Discord

| Mức | n | N | Tỷ lệ |
|---|---:|---:|---:|
| Thường xuyên (hàng ngày) | 13 | 18 | 72,2% |
| Thỉnh thoảng (vài lần mỗi tuần) | 3 | 18 | 16,7% |
| Hiếm khi | 2 | 18 | 11,1% |

### Khó khăn được chọn

| Khó khăn | n | N | Tỷ lệ |
|---|---:|---:|---:|
| Bỏ lỡ thông báo | 16 | 18 | 88,9% |
| Tin nhắn bị trôi | 16 | 18 | 88,9% |
| Khó tìm thông tin | 12 | 18 | 66,7% |
| Không biết hỏi ở đâu | 9 | 18 | 50,0% |
| Câu hỏi không được trả lời | 7 | 18 | 38,9% |
| Có quá nhiều câu hỏi trùng lặp | 6 | 18 | 33,3% |

### Phân phối bốn thang điểm

| Điểm normalized | Q06 tìm thông tin | Q07 hỏi lại câu cũ | Q08 bỏ lỡ thông báo | Q09 hội thoại dài |
|---:|---:|---:|---:|---:|
| 1 | 0/18 | 1/18 | 1/18 | 0/18 |
| 2 | 0/18 | 4/18 | 1/18 | 2/18 |
| 3 | 8/18 | 7/18 | 4/18 | 3/18 |
| 4 | 6/18 | 6/18 | 9/18 | 8/18 |
| 5 | 4/18 | 0/18 | 3/18 | 5/18 |

### Thời gian tìm thông tin

| Mức | n | N | Tỷ lệ |
|---|---:|---:|---:|
| 1 - 5 phút | 12 | 18 | 66,7% |
| Trên 5 phút | 4 | 18 | 22,2% |
| Dưới 1 phút | 2 | 18 | 11,1% |

Không dùng từ “đa số” nếu bảng không cho thấy tỷ lệ trên 50%. Tất cả kết quả là
self-reported và eligibility ngoài team chưa xác minh.

## TA/Labcoach signals

> **Directional only — n=2.** Không tổng quát hóa cho toàn bộ TA/Labcoach.

### Thời gian hỗ trợ Discord mỗi ngày

| Mức | n | N | Tỷ lệ |
|---|---:|---:|---:|
| 1 - 3 giờ | 2 | 2 | 100,0% |

### Tần suất trả lời lặp

| Mức | n | N | Tỷ lệ |
|---|---:|---:|---:|
| Rất thường xuyên | 1 | 2 | 50,0% |
| Thỉnh thoảng | 1 | 2 | 50,0% |

### Ước lượng tỷ lệ câu hỏi lặp

| Mức | n | N | Tỷ lệ |
|---|---:|---:|---:|
| 25% - 50% | 1 | 2 | 50,0% |
| Dưới 25% | 1 | 2 | 50,0% |

Một learner có dữ liệu ở Q18; giá trị đó bị đánh dấu
`INVALID_ROLE_RESPONSE` và không được tính vào TA denominator.

## Solution preferences

Các bảng dưới chỉ dùng ưu tiên giải pháp, không phải evidence pain.

### Learner — AI nên hỗ trợ gì

| Lựa chọn | n | N | Tỷ lệ |
|---|---:|---:|---:|
| Thông báo lịch học | 15 | 18 | 83,3% |
| Hướng dẫn tìm tài liệu | 14 | 18 | 77,8% |
| Tóm tắt tin nhắn bị trôi | 13 | 18 | 72,2% |
| Trả lời câu hỏi về bài tập | 12 | 18 | 66,7% |
| Không có ý kiến | 1 | 18 | 5,6% |

### Learner — khi bot không chắc chắn

| Hành vi mong muốn | n | N | Tỷ lệ |
|---|---:|---:|---:|
| Chuyển tiếp câu hỏi cho Trợ giảng | 11 | 18 | 61,1% |
| Cố gắng trả lời dựa trên suy đoán | 5 | 18 | 27,8% |
| Xin lỗi và yêu cầu học viên hỏi lại sau | 2 | 18 | 11,1% |

### Learner — tính năng quan trọng nhất

| Lựa chọn | n | N | Tỷ lệ |
|---|---:|---:|---:|
| Giải đáp thắc mắc chuyên môn | 6 | 18 | 33,3% |
| Quản lý và tóm tắt thông báo | 5 | 18 | 27,8% |
| Tìm kiếm tài liệu thông minh | 4 | 18 | 22,2% |
| Nhắc nhở hạn nộp bài | 3 | 18 | 16,7% |

### TA — công việc muốn được hỗ trợ

| Lựa chọn | n | N | Tỷ lệ |
|---|---:|---:|---:|
| Cảnh báo học viên vắng mặt/tụt hậu | 2 | 2 | 100,0% |
| Tự động trả lời câu hỏi lặp lại | 2 | 2 | 100,0% |
| Phân loại và điều hướng câu hỏi | 1 | 2 | 50,0% |
| Tóm tắt các vấn đề học viên đang gặp | 1 | 2 | 50,0% |

### TA — trường hợp muốn được thông báo

| Lựa chọn | n | N | Tỷ lệ |
|---|---:|---:|---:|
| Khi AI không giải quyết được vấn đề | 2 | 2 | 100,0% |
| Khi có học viên bị hổng kiến thức | 2 | 2 | 100,0% |
| Khi học viên hỏi câu hỏi khó | 2 | 2 | 100,0% |
| Khi có quá nhiều thắc mắc cùng chủ đề | 1 | 2 | 50,0% |

Q30: 2/2 (100,0%)
TA chọn muốn nhận báo cáo tổng hợp cuối ngày; đây chỉ là tín hiệu định hướng n=2.

## Quotes

Tối đa năm quote Q17, giữ nguyên diễn đạt và dùng response ID:

- R002: “thông tin bị trôi, thắc mắc không được TA giải đáp”
- R004: “Khó tìm ra thông tin mình muốn”
- R017: “Khó tìm kiếm thông tin”
- R006: “Chưa sử dụng quen và thành thạo discord, …”
- R013: “Ko biết hôm đó phải làm gì ở đâu”

Q17 có 7/18 response có
nội dung. Q27 có 0/2 response.

## Limitations

- Chưa xác minh tất cả response đều từ người ngoài team.
- Mẫu TA rất nhỏ (n=2).
- Câu hỏi nhắc trực tiếp AI có thể mang tính dẫn dắt.
- Dữ liệu self-reported.
- Một số free-text để trống.
- Không thay thế mining Discord thực tế.
- Pattern PII có thể bỏ lọt tên riêng hoặc ngữ cảnh nhận dạng.
- Semantic review do agent thực hiện không thay thế quyết định công khai và
  human PII sign-off của team.
- Một learner điền Q18 dành cho TA; đã loại khỏi TA metrics.

## Rubric readiness

- Evidence A: **`UNVERIFIED`**, không được tuyên bố đạt.
- Đủ 20 response tổng, nhưng điều kiện “≥20 người ngoài nhóm” chưa được xác minh.
- `pain_confirmed_draft`: 10/18 (55,6%) learner.
- Chỉ sau khi team xác nhận không respondent nào thuộc team mới được đánh giá tiếp
  điều kiện Evidence A; tiêu chí pain draft không được đổi sau khi thấy kết quả.
- Có thể đề xuất cập nhật `spec.md` §1–§2 bằng các metric behavior/pain đã audit,
  nhưng phải giữ nhãn eligibility `UNVERIFIED` cho tới khi có xác nhận.
