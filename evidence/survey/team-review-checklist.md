# Survey Team Review Checklist

- [ ] Xác nhận không có thành viên team trong 20 response
- [ ] Nếu có, xác định response cần loại và thu bổ sung
- [ ] Xác nhận learner là target respondent chính hay tính cả learner + TA
- [ ] Nếu learner là target chính, thu thêm ≥2 learner ngoài nhóm
- [ ] Duyệt tiêu chí `pain_confirmed_draft`
- [ ] Duyệt 5 quote được đưa vào spec
- [ ] Hoàn thành human PII review
- [ ] Xác nhận TA findings chỉ là directional
- [ ] Duyệt các metric dùng trong bảng impact
- [ ] Quyết định Evidence A là `READY`/`NOT READY`
- [ ] Chỉ sau khi duyệt mới commit/push

| Decision | Current status | Owner | Evidence needed |
|---|---|---|---|
| Eligibility của 20 respondent | `UNVERIFIED` |  | Xác nhận từng Rxxx có/không thuộc team; không tạo mapping danh tính trong artifact public |
| Target respondent: learner hay learner + TA | `UNVERIFIED` |  | Team/TA xác nhận cách áp rubric; nếu learner-only thì hiện n=18 |
| Bổ sung learner ngoài nhóm | `PENDING DECISION` |  | Thu thêm ≥2 learner nếu learner là target chính |
| Tiêu chí `pain_confirmed_draft` | `DRAFT` |  | Duyệt nguyên trạng định nghĩa trong codebook; không đổi sau khi thấy kết quả |
| Năm quote trong `spec.md` | `AGENT_REVIEWED` |  | Team đọc lại R002, R004, R006, R013, R017 và xác nhận đúng pain |
| Semantic PII | `AGENT_REVIEWED; HUMAN SIGN-OFF PENDING` |  | Human đọc 7 response Q17; Q27 hiện không có response |
| TA findings | `DIRECTIONAL_ONLY, n=2` |  | Xác nhận không dùng để tổng quát hóa |
| Metric impact | `AUDITED; TEAM APPROVAL PENDING` |  | Đối chiếu `metric_id` trong `survey-metrics.csv`; bổ sung frequency/loss còn thiếu |
| Evidence A | `UNVERIFIED` |  | Eligibility ngoài team + cách tính target respondent + duyệt pain criterion + human PII sign-off |

## Hai cách hiểu rubric cần quyết định

1. Nếu tính cả learner và TA/Lab Coach, survey có n=20 nhưng eligibility ngoài
   team vẫn `UNVERIFIED`.
2. Nếu learner là target respondent chính, survey hiện chỉ có n=18 learner và
   cần thu thêm ít nhất hai learner ngoài nhóm.

Không đánh dấu Evidence A `READY` trước khi có bằng chứng mới cho các ô trên.
