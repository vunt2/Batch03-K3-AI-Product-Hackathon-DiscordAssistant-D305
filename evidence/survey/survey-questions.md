# Survey Questions

Nguồn: `Khảo sát AI Agent hỗ trợ học tập trên Discord (Câu trả lời) - Câu trả lời biểu mẫu 1.csv`. File có 30 cột; Q01 là metadata thời gian, không phải
câu hỏi nội dung. Cột “Evidence use” phân biệt evidence pain/behavior với
preference giải pháp.

| ID | Câu hỏi/cột | Phân loại | Đối tượng | Kiểu dữ liệu | Evidence use | Ghi chú |
|---|---|---|---|---|---|---|
| Q01 | Dấu thời gian | metadata | all | metadata | NO | Timestamp removed from public artifacts |
| Q02 | Bạn là? | role | all | categorical | SEGMENTATION | Role filter for every metric |
| Q03 | Tần suất sử dụng Discord của bạn trong học tập | behavior | learner-only | categorical | YES | Actual Discord usage frequency |
| Q04 | Mục đích sử dụng Discord chính của bạn | behavior | learner-only | multi-select | CONTEXT | Actual Discord uses |
| Q05 | Những khó khăn bạn thường gặp khi sử dụng Discord (Dành cho Học viên) | pain | learner-only | multi-select | YES | Actual difficulties |
| Q06 | Đánh giá các vấn đề sau (Dành cho Học viên) [Mất nhiều thời gian tìm thông tin] | pain | learner-only | scale 1-5 | YES | Time spent finding information |
| Q07 | Đánh giá các vấn đề sau (Dành cho Học viên) [Đã từng hỏi lại câu hỏi cũ] | pain | learner-only | scale 1-5 | YES | Repeated old questions |
| Q08 | Đánh giá các vấn đề sau (Dành cho Học viên) [Bỏ lỡ thông báo quan trọng] | pain | learner-only | scale 1-5 | YES | Missed important announcements |
| Q09 | Đánh giá các vấn đề sau (Dành cho Học viên) [Khó theo dõi cuộc trò chuyện dài] | pain | learner-only | scale 1-5 | YES | Difficulty following long threads |
| Q10 | Trung bình bạn mất bao lâu để tìm kiếm thông tin cần thiết trên Discord? | impact | learner-only | categorical | YES | Observed search time |
| Q11 | Bạn đã từng từ bỏ việc tìm thông tin vì mất quá nhiều thời gian hay chưa? | pain | learner-only | categorical | YES | Abandoned search behavior |
| Q12 | AI nên hỗ trợ những gì cho bạn? | solution preference | learner-only | multi-select | NO | Preference only |
| Q13 | Khi nào AI nên trả lời câu hỏi của bạn? | solution preference | learner-only | categorical | NO | Preference only |
| Q14 | AI nên làm gì khi không chắc chắn về câu trả lời? | solution preference | learner-only | categorical | NO | Safety preference only |
| Q15 | Bạn có muốn AI chủ động hỗ trợ khi bị kẹt (stuck) trong bài tập không? | solution preference | learner-only | categorical | NO | Preference only |
| Q16 | Tính năng AI nào bạn cho là quan trọng nhất? | solution preference | learner-only | categorical | NO | Preference only |
| Q17 | Khó khăn lớn nhất của bạn khi học trên Discord là gì? (Dành cho Học viên) | free text / pain | learner-only | free text | YES | Qualitative pain evidence after PII review |
| Q18 | Thời gian mỗi ngày bạn dành để hỗ trợ trên Discord (Dành cho TA) | impact | TA-only | categorical | DIRECTIONAL | TA sample n=2 |
| Q19 | Những loại câu hỏi học viên hỏi nhiều nhất (Dành cho TA) | behavior | TA-only | multi-select | DIRECTIONAL | TA sample n=2 |
| Q20 | Tần suất phải trả lời lặp lại các câu hỏi cũ (Dành cho TA) | pain / behavior | TA-only | categorical | DIRECTIONAL | TA sample n=2 |
| Q21 | Ước lượng tỷ lệ câu hỏi lặp lại mỗi ngày (Dành cho TA) | impact | TA-only | categorical | DIRECTIONAL | TA sample n=2 |
| Q22 | Những khó khăn khi quản lý Discord (Dành cho TA) [Rất khó khăn] | pain | TA-only | multi-select | DIRECTIONAL | TA sample n=2 |
| Q23 | Những khó khăn khi quản lý Discord (Dành cho TA) [Bình thường] | pain | TA-only | multi-select | DIRECTIONAL | TA sample n=2 |
| Q24 | Những khó khăn khi quản lý Discord (Dành cho TA) [Không vấn đề] | pain | TA-only | multi-select | DIRECTIONAL | TA sample n=2 |
| Q25 | Bạn đã từng trả lời sai do quá nhiều tin nhắn hay chưa? | pain / behavior | TA-only | categorical | DIRECTIONAL | TA sample n=2 |
| Q26 | AI nên hỗ trợ những công việc nào cho Trợ giảng? | solution preference | TA-only | multi-select | NO | Preference only; TA n=2 |
| Q27 | AI tuyệt đối không nên tự động trả lời những nội dung nào? | free text / safety | TA-only | free text | NO | No responses |
| Q28 | Nếu AI chỉ được hỗ trợ một việc thì nên hỗ trợ việc gì? | solution preference | TA-only | categorical | NO | Preference only; TA n=2 |
| Q29 | AI nên chủ động thông báo cho bạn trong trường hợp nào? | solution preference | TA-only | multi-select | NO | Preference only; TA n=2 |
| Q30 | Có muốn nhận báo cáo tổng hợp cuối ngày về hoạt động của cộng đồng hay không? | solution preference | TA-only | categorical | NO | Preference only; TA n=2 |

## Nguyên tắc sử dụng

- Chỉ câu behavior/pain/impact mới được dùng để chứng minh pain.
- Câu solution preference chỉ dùng để ưu tiên thiết kế, không chứng minh pain.
- TA metrics chỉ mang tính định hướng vì mẫu TA có n=2.
- Mọi thống kê phải filter theo Q02 trước khi tính denominator.
