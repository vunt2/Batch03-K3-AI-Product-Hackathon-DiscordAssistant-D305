# D305 Assistant

D305 Assistant là prototype chatbot hỗ trợ học viên trên Discord tìm câu trả lời nhanh từ nguồn đã được xác minh. Khi không có nguồn phù hợp hoặc độ chắc chắn chưa đủ, hệ thống chuyển câu hỏi sang Labcoach thay vì tự suy đoán thông tin.

Labcoach tiếp nhận các câu hỏi trong hàng đợi tập trung, gửi phản hồi lại cho học viên và có thể duyệt tri thức mới qua một quy trình riêng. Phản hồi của Labcoach **không tự động trở thành nguồn chính thức**.

Prototype hiện sử dụng Streamlit, Gemini, kho tri thức approved dạng JSON và SQLite cục bộ. Đây chưa phải hệ thống production.

## Thành viên

| Mã học viên | Họ và tên | Vai trò | Phần phụ trách |
|---|---|---|---|
| 2A202601115 | Nguyễn Phúc Hưng | Evidence & Product Specification | Khảo sát, evidence, impact analysis, CP checklist và spec |
| 2A202601087 | Nguyễn Văn Phong | Evaluation | Golden set, eval runner, kết quả đánh giá và phân tích case fail |
| 2A202601781 | Nguyễn Hữu Khánh Tùng | AI Integration | Gemini model client, intent engine, Streamlit integration và fallback |
| 2A202601845 | Nguyễn Tuấn Vũ | Nhóm trưởng · Prompt & Safety | Prompt contract, output validator, safety design và điều phối tích hợp |

## Luồng sản phẩm

1. Learner đặt câu hỏi → hệ thống tìm nguồn approved phù hợp → Gemini phân loại intent và chọn action → trả lời từ nguồn hoặc handoff cho Labcoach.
2. Labcoach xử lý hàng đợi → phản hồi được gửi lại Learner → câu trả lời ứng viên phải được duyệt riêng trước khi publish vào knowledge base.

Các nguyên tắc cốt lõi:

- Logistics chỉ được trả lời khi có nguồn approved, còn hiệu lực và đúng chủ đề.
- Không có nguồn hoặc nguồn không chắc chắn thì handoff, không bịa deadline, lịch hay đường dẫn.
- Câu mơ hồ được hỏi lại; yêu cầu làm hộ được từ chối và định hướng.
- Mọi output từ model phải qua validator trước khi hiển thị.
- Phản hồi Labcoach không được tự động coi là tri thức chính thức.

## Chạy prototype

```powershell
cd codebase
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

Trong `codebase/.env`, chỉ cần điền giá trị cho `GEMINI_API_KEY`. Không commit file `.env` hoặc API key vào Git.

## Cấu trúc repository

| Đường dẫn | Nội dung |
|---|---|
| `codebase/` | Ứng dụng Streamlit, tích hợp Gemini, safety routing và kiểm thử |
| `data/approved/` | Knowledge base đã qua quy trình duyệt |
| `eval/` | Golden set, eval runner và kết quả các lần đánh giá |
| `evidence/` | Bằng chứng khảo sát, phân tích impact, checklist và trace đã làm sạch |
| `validation/` | Feedback log, tổng hợp validation và changelog CP5 |
| `reflection/` | Reflection cá nhân của bốn thành viên |
| `presentation.html` | Slide trình bày tương tác của nhóm |

## Trạng thái hiện tại

- Prototype Gemini với hai giao diện Learner và Labcoach đã hoạt động.
- Golden eval lịch sử đạt **20/22** tổng thể.
- Quality Bar hiện **HOLD** vì nhóm logistics đạt **5/6**, chưa đạt điều kiện cứng.
- CP5 đã có 5 learner ngoài nhóm thử Learner View; phản hồi dẫn tới cải thiện casual routing, giọng trả lời và memory trong phiên.
- Phiên thử không lưu mapping tên/quote theo từng learner, nên chưa đạt trọn tiêu chí feedback có tên của rubric.
- Chưa có Labcoach thật tham gia validation; nhóm không tuyên bố workflow Labcoach đã được user thật xác minh.
- Sau thay đổi CP5, 150/150 unit test đạt và Streamlit AppTest không có exception.
- Demo script 5 phút đã có; nhóm vẫn cần tự dry run có bấm giờ trước checkpoint.
- Prototype chưa được tuyên bố sẵn sàng production.

## Tài liệu dự án và tiêu chí

- [Đề bài](01-de-bai.md)
- [Hướng dẫn thực hiện](02-guide.md)
- [Template AI Spec](03-template-ai-spec.md)
- [Rubric chấm điểm](04-rubric.md)
- [Product specification](spec.md)
- [CP3 checklist](evidence/cp3-checklist.md)
- [Kết quả eval 20/22](eval/results/cp3-gemini-gemini-3.5-flash-lite-20260730-210206-summary.md)
- [CP5 feedback log](validation/user-feedback-log.md)
- [CP5 validation summary](validation/cp5-summary.md)
- [CP5 changelog](validation/cp5-changelog.md)
- [Demo script 5 phút](validation/demo-script.md)
- [Slide trình bày](presentation.html)

Khi làm việc với repository, thành viên phải giữ nguyên số liệu thật, nêu rõ giới hạn của bằng chứng, không che case fail, không commit secret và không đưa dữ liệu nhạy cảm vào prompt, trace, log hoặc artifact được theo dõi bởi Git.

## An toàn dữ liệu

- Không commit `.env`, API key, database runtime hoặc mapping danh tính local.
- Không commit toàn bộ data pack được ban tổ chức cấp vào repo nộp bài; chỉ
  giữ trích dẫn ngắn và mã tham chiếu cần thiết.
- Chỉ publish knowledge khi nguồn và người duyệt có thẩm quyền đã được xác
  minh. Self-test của thành viên team không phải nguồn approved.
