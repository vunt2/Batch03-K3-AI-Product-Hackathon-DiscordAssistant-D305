# Survey Analysis Notes

## Anomalies

- Shape xác minh: 20 data rows × 30 columns.
- Role: 18 learner, 2 TA/Labcoach.
- R001 có Q18 không thuộc vai trò; đánh dấu `INVALID_ROLE_RESPONSE`.
- Q18 có 3 ô nonblank nhưng chỉ 2 thuộc role TA; metrics Q18 dùng N=2.
- Q27 trống toàn bộ.
- Q06–Q09 trộn giá trị số ngắn và giá trị “số: nhãn”; đã normalize bằng số đầu.
- Checkbox được lưu nhiều lựa chọn trong cùng ô; đã tách trước khi đếm.
- Blank do Google Form branching được đánh dấu `NOT_APPLICABLE`.

## PII review

- Không phát hiện email, số điện thoại, URL hoặc Discord identifier theo pattern.
- Timestamp chính xác không được đưa vào artifact public.
- Semantic review đã đọc từng ô tự luận trong bản anonymized: Q17 có 7 response
  nonblank; Q27 có 0 response. Đã kiểm tra họ tên, email, Discord username, số
  điện thoại, link cá nhân, mã học viên, tên lớp/nhóm, người thứ ba và ngữ cảnh
  có thể suy ngược danh tính.
- Không phát hiện PII hoặc ngữ cảnh nhận dạng rõ ràng trong 7 response Q17; không
  cần thay bằng `[đã ẩn]` hoặc `[NEEDS_HUMAN_REVIEW]`.
- Năm quote pain đưa vào spec dùng R002, R004, R006, R013 và R017. R010 và R014
  mô tả mong muốn AI/tính năng nên không dùng làm pain evidence.
- Không có mapping response ID → danh tính trong artifact.
- Phạm vi kiểm tra gồm pattern scan và semantic review do agent thực hiện; không
  tuyên bố dữ liệu “PII-safe tuyệt đối”. Team vẫn cần một người human sign-off
  trước khi công khai artifact.

## Cleaning decisions

- Không sửa CSV nguồn.
- Không sửa chính tả/cách diễn đạt.
- Giữ original cleaned values; normalized values ở cột riêng.
- Mọi respondent có `eligibility_status=UNVERIFIED`.
- TA metrics có status `DIRECTIONAL_ONLY_ELIGIBILITY_UNVERIFIED`.
- Preference không được dùng làm pain evidence.

## Không thể kết luận

- Không thể kết luận Evidence A đã đạt trước khi team xác nhận 20 respondent đều
  ngoài team.
- Không thể khái quát hai TA cho toàn bộ labcoach.
- Không thể suy ra hành vi thực tế chỉ từ self-report.
- Không thể dùng mong muốn tính năng để chứng minh pain.
- Không thể coi survey là thay thế cho mining Discord.

## Cần con người quyết định

1. Trong 20 respondent có ai thuộc chính team hay không?
2. Team có duyệt nguyên trạng tiêu chí `pain_confirmed_draft` không?
3. Artifact có được công khai ngoài khóa học không; nếu có, ai sẽ thực hiện
   human PII sign-off lần cuối?
4. Có cần xác nhận lại respondent R001 vì điền Q18 không thuộc vai trò?

## Spec và golden-set candidates

- Có thể đưa vào `spec.md` §1–§2: learner behavior/pain metrics, numerator,
  denominator và limitation; chưa tuyên bố Evidence A đạt.
- Q05/Q17 có thể tạo question variants về tin nhắn bị trôi, khó tìm thông tin,
  câu hỏi không được trả lời và câu hỏi trùng lặp.
- Q07–Q11 có thể tạo normal/edge cases cho learner đã hỏi lại, bỏ lỡ thông báo,
  hội thoại dài và từ bỏ tìm kiếm.
- Q14 có thể tạo safety route variants, nhưng là preference chứ không phải pain.
- Tất cả candidate từ survey vẫn cần ẩn danh và không thay thế yêu cầu ≥10 case
  từ chatlog thật của rubric.
