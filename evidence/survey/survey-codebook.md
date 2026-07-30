# Survey Codebook

## Data dictionary

| ID | Ý nghĩa/câu hỏi | Phân loại | Vai trò áp dụng | Kiểu | Chuẩn hóa | Evidence use | Ghi chú |
|---|---|---|---|---|---|---|---|
| Q01 | Dấu thời gian | metadata | all | metadata | Loại timestamp chính xác khỏi artifact public; chỉ giữ ngày khảo sát | NO | Timestamp removed from public artifacts |
| Q02 | Bạn là? | role | all | categorical | Giữ nguyên sau PII redaction | SEGMENTATION | Role filter for every metric |
| Q03 | Tần suất sử dụng Discord của bạn trong học tập | behavior | learner-only | categorical | Giữ nguyên sau PII redaction | YES | Actual Discord usage frequency |
| Q04 | Mục đích sử dụng Discord chính của bạn | behavior | learner-only | multi-select | Tách lựa chọn bằng dấu phẩy + khoảng trắng; giữ chuỗi gốc | CONTEXT | Actual Discord uses |
| Q05 | Những khó khăn bạn thường gặp khi sử dụng Discord (Dành cho Học viên) | pain | learner-only | multi-select | Tách lựa chọn bằng dấu phẩy + khoảng trắng; giữ chuỗi gốc | YES | Actual difficulties |
| Q06 | Đánh giá các vấn đề sau (Dành cho Học viên) [Mất nhiều thời gian tìm thông tin] | pain | learner-only | scale 1-5 | Lấy số đầu 1–5; giữ giá trị gốc ở cột original | YES | Time spent finding information |
| Q07 | Đánh giá các vấn đề sau (Dành cho Học viên) [Đã từng hỏi lại câu hỏi cũ] | pain | learner-only | scale 1-5 | Lấy số đầu 1–5; giữ giá trị gốc ở cột original | YES | Repeated old questions |
| Q08 | Đánh giá các vấn đề sau (Dành cho Học viên) [Bỏ lỡ thông báo quan trọng] | pain | learner-only | scale 1-5 | Lấy số đầu 1–5; giữ giá trị gốc ở cột original | YES | Missed important announcements |
| Q09 | Đánh giá các vấn đề sau (Dành cho Học viên) [Khó theo dõi cuộc trò chuyện dài] | pain | learner-only | scale 1-5 | Lấy số đầu 1–5; giữ giá trị gốc ở cột original | YES | Difficulty following long threads |
| Q10 | Trung bình bạn mất bao lâu để tìm kiếm thông tin cần thiết trên Discord? | impact | learner-only | categorical | Giữ nguyên sau PII redaction | YES | Observed search time |
| Q11 | Bạn đã từng từ bỏ việc tìm thông tin vì mất quá nhiều thời gian hay chưa? | pain | learner-only | categorical | Giữ nguyên sau PII redaction | YES | Abandoned search behavior |
| Q12 | AI nên hỗ trợ những gì cho bạn? | solution preference | learner-only | multi-select | Tách lựa chọn bằng dấu phẩy + khoảng trắng; giữ chuỗi gốc | NO | Preference only |
| Q13 | Khi nào AI nên trả lời câu hỏi của bạn? | solution preference | learner-only | categorical | Giữ nguyên sau PII redaction | NO | Preference only |
| Q14 | AI nên làm gì khi không chắc chắn về câu trả lời? | solution preference | learner-only | categorical | Giữ nguyên sau PII redaction | NO | Safety preference only |
| Q15 | Bạn có muốn AI chủ động hỗ trợ khi bị kẹt (stuck) trong bài tập không? | solution preference | learner-only | categorical | Giữ nguyên sau PII redaction | NO | Preference only |
| Q16 | Tính năng AI nào bạn cho là quan trọng nhất? | solution preference | learner-only | categorical | Giữ nguyên sau PII redaction | NO | Preference only |
| Q17 | Khó khăn lớn nhất của bạn khi học trên Discord là gì? (Dành cho Học viên) | free text / pain | learner-only | free text | Giữ nguyên sau PII redaction | YES | Qualitative pain evidence after PII review |
| Q18 | Thời gian mỗi ngày bạn dành để hỗ trợ trên Discord (Dành cho TA) | impact | TA-only | categorical | Giữ nguyên sau PII redaction | DIRECTIONAL | TA sample n=2 |
| Q19 | Những loại câu hỏi học viên hỏi nhiều nhất (Dành cho TA) | behavior | TA-only | multi-select | Tách lựa chọn bằng dấu phẩy + khoảng trắng; giữ chuỗi gốc | DIRECTIONAL | TA sample n=2 |
| Q20 | Tần suất phải trả lời lặp lại các câu hỏi cũ (Dành cho TA) | pain / behavior | TA-only | categorical | Giữ nguyên sau PII redaction | DIRECTIONAL | TA sample n=2 |
| Q21 | Ước lượng tỷ lệ câu hỏi lặp lại mỗi ngày (Dành cho TA) | impact | TA-only | categorical | Giữ nguyên sau PII redaction | DIRECTIONAL | TA sample n=2 |
| Q22 | Những khó khăn khi quản lý Discord (Dành cho TA) [Rất khó khăn] | pain | TA-only | multi-select | Tách lựa chọn bằng dấu phẩy + khoảng trắng; giữ chuỗi gốc | DIRECTIONAL | TA sample n=2 |
| Q23 | Những khó khăn khi quản lý Discord (Dành cho TA) [Bình thường] | pain | TA-only | multi-select | Tách lựa chọn bằng dấu phẩy + khoảng trắng; giữ chuỗi gốc | DIRECTIONAL | TA sample n=2 |
| Q24 | Những khó khăn khi quản lý Discord (Dành cho TA) [Không vấn đề] | pain | TA-only | multi-select | Tách lựa chọn bằng dấu phẩy + khoảng trắng; giữ chuỗi gốc | DIRECTIONAL | TA sample n=2 |
| Q25 | Bạn đã từng trả lời sai do quá nhiều tin nhắn hay chưa? | pain / behavior | TA-only | categorical | Giữ nguyên sau PII redaction | DIRECTIONAL | TA sample n=2 |
| Q26 | AI nên hỗ trợ những công việc nào cho Trợ giảng? | solution preference | TA-only | multi-select | Tách lựa chọn bằng dấu phẩy + khoảng trắng; giữ chuỗi gốc | NO | Preference only; TA n=2 |
| Q27 | AI tuyệt đối không nên tự động trả lời những nội dung nào? | free text / safety | TA-only | free text | Giữ nguyên sau PII redaction | NO | No responses |
| Q28 | Nếu AI chỉ được hỗ trợ một việc thì nên hỗ trợ việc gì? | solution preference | TA-only | categorical | Giữ nguyên sau PII redaction | NO | Preference only; TA n=2 |
| Q29 | AI nên chủ động thông báo cho bạn trong trường hợp nào? | solution preference | TA-only | multi-select | Tách lựa chọn bằng dấu phẩy + khoảng trắng; giữ chuỗi gốc | NO | Preference only; TA n=2 |
| Q30 | Có muốn nhận báo cáo tổng hợp cuối ngày về hoạt động của cộng đồng hay không? | solution preference | TA-only | categorical | Giữ nguyên sau PII redaction | NO | Preference only; TA n=2 |

## Cột kiểm soát

- `response_id`: mã tuần tự R001–R020, không ánh xạ công khai tới danh tính.
- `role`: `learner` hoặc `ta_labcoach`.
- `eligibility_status`: luôn `UNVERIFIED` cho tới khi team xác nhận respondent
  nằm ngoài team.
- `pii_review_status`: `NO_PII_DETECTED` nếu không khớp pattern PII;
  `NEEDS_REVIEW` nếu có.
- `data_quality_notes`: anomaly theo row, không chứa nội dung nhận dạng.

## Mapping thang điểm

| Giá trị gốc | Normalized |
|---|---:|
| `1` hoặc `1: Không bao giờ` | 1 |
| `2` hoặc `2: Hiếm khi` | 2 |
| `3` hoặc `3: Thỉnh thoảng` | 3 |
| `4` hoặc `4: Thường xuyên` | 4 |
| `5` hoặc `5: Rất thường xuyên` | 5 |

Giá trị gốc không bị ghi đè; Q06–Q09 có cột normalized riêng.

## Multi-select

Các Q04, Q05, Q12, Q19, Q22–Q24, Q26 và Q29 được tách thành lựa chọn
riêng. Mỗi respondent chỉ được đếm tối đa một lần cho mỗi lựa chọn. Chuỗi gốc
được giữ; cột `*_options_normalized` dùng dấu ` | ` để dễ audit.

## Missing values

- `OBSERVED`: đúng vai trò và có câu trả lời.
- `NO_RESPONSE`: đúng vai trò nhưng để trống.
- `NOT_APPLICABLE`: câu không thuộc vai trò và để trống.
- `INVALID_ROLE_RESPONSE`: có dữ liệu ở câu không thuộc vai trò.
- `NEEDS_REVIEW`: không xác định được vai trò/trạng thái.

Google Form branching blanks không được tính như missing thông thường và không
được đưa vào denominator của vai trò khác.

## pain_confirmed_draft

Learner được gắn 1 nếu thỏa ít nhất một điều:

1. Q05 có “Câu hỏi không được trả lời”; hoặc
2. Q05 có “Có quá nhiều câu hỏi trùng lặp”; hoặc
3. Q07 normalized ≥4.

Đây là tiêu chí `DRAFT` do team đề xuất trước phân tích. Không đổi tiêu chí để
đạt mốc 50%.

## Anonymization

- Bỏ timestamp chính xác; chỉ summary ngày khảo sát 30/07/2026.
- Thay respondent bằng R001–R020.
- Redact email, số điện thoại, URL cá nhân và Discord identifier nếu phát hiện.
- Không phát hiện pattern PII trong file nguồn ở lượt kiểm tra này.
- Free text được giữ nguyên diễn đạt sau PII review; không sửa chính tả.

## Hạn chế

- Không có trường tên/email, nhưng eligibility ngoài team chưa xác minh.
- Self-reported data và câu hỏi nhắc trực tiếp AI có thể gây thiên lệch.
- TA chỉ n=2, chỉ dùng như tín hiệu định hướng.
- Q17 chỉ có một phần learner trả lời; Q27 trống toàn bộ.
- Bộ lọc PII theo pattern không bảo đảm phát hiện mọi tên riêng/ngữ cảnh nhận dạng.
