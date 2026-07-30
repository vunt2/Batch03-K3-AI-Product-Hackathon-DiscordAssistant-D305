# Kim chỉ nam phát triển — Discord Learner Assistant

> **BẮT BUỘC:** Mọi AI coding agent và thành viên phải đọc hết file này trước
> khi thay đổi repository.
>
> **KHÔNG TỰ MỞ RỘNG SCOPE.** Sau CP4 không thêm feature mới. Mọi thay đổi North
> Star, lát cắt, ground-truth policy, non-goals hoặc quality bar phải được team
> xác nhận trước.

## Current Phase

**CP3 — `IN PROGRESS` (xác minh từ repository ngày 30/07/2026).**

- CP2 đã có Streamlit UI, flow năm intent và commit riêng.
- CP3 đã tích hợp model client vào Streamlit, có prompt versioned, output
  validator, timeout/fallback, trace mẫu và 23 unit test.
- Test model call hiện dùng mock; repository chưa đủ bằng chứng để tự xác minh
  một API call live. Chưa có retrieval từ nguồn được duyệt, golden set hoặc
  evaluation run.
- `spec.md` vẫn là draft nối CP2 → CP3; evidence, impact, owner, willing users và
  quality bar chưa được xác minh/freeze.

Agent không được mô tả CP3 là hoàn thành cho đến khi xác minh được model call
live, có golden set ≥20 và bảng kết quả lượt đầu có phần trăm.

## 1. Mục đích và thứ tự ưu tiên

File này hướng dẫn cách triển khai và cách báo cáo trung thực trạng thái dự án.

- [`spec.md`](../spec.md) là artifact sản phẩm/rubric, không tự động chứng minh
  implementation đã tồn tại.
- [`README.md`](../README.md) là tài liệu cho người dùng và yêu cầu nộp bài.
- [`01-de-bai.md`](../01-de-bai.md),
  [`02-guide.md`](../02-guide.md) và
  [`04-rubric.md`](../04-rubric.md) là nguồn chính thức.
- [`03-template-ai-spec.md`](../03-template-ai-spec.md) là khung của spec.

Khi có xung đột, dùng thứ tự:

1. Yêu cầu trực tiếp mới nhất của người dùng.
2. Đề bài, guide và rubric chính thức.
3. Quyết định sản phẩm được team chốt trong file này.
4. `spec.md`.
5. Implementation hiện tại.

Nếu xung đột làm thay đổi scope hoặc hành vi sản phẩm, agent phải nêu rõ và xin
team xác nhận trước khi code. Không được biến một mô tả, TODO hoặc target
architecture thành tuyên bố `DONE`.

## 2. Product North Star

### Problem statement

Khi học viên hỏi về chương trình hoặc dự án trong Discord, câu hỏi lặp lại, mơ
hồ hoặc thiếu nguồn chính thức có thể bị bỏ sót hay nhận câu trả lời sai; đặc
biệt, sai deadline hoặc link nộp bài có thể gây hậu quả trực tiếp. Labcoach
không thể đọc và xử lý kịp toàn bộ câu hỏi.

### Hai vai trò

**Learner**

- Đặt câu hỏi tự do về chương trình/dự án.
- Nhận trả lời nhanh khi có căn cứ từ nguồn đã được duyệt.
- Được hỏi lại khi input mơ hồ.
- Biết rõ khi câu hỏi được chuyển cho labcoach.

**Labcoach**

- Tập trung vào câu bot không đủ căn cứ hoặc cần thẩm quyền.
- Xem unanswered queue và các câu tương tự được gom theo chủ đề.
- Sửa, phê duyệt câu trả lời hoặc bài chia sẻ.
- Cho phép nội dung đã duyệt cập nhật vào knowledge base.

### Lát cắt một câu

Khi một học viên đặt câu hỏi về chương trình trong Discord, trợ lý kiểm tra
nguồn tri thức đã được labcoach phê duyệt và quyết định trả lời kèm nguồn hoặc
hỏi lại/chuyển labcoach, để học viên nhận hỗ trợ nhanh mà không nhận thông tin
thiếu căn cứ.

### Quyết định AI trung tâm

**Có đủ căn cứ để trả lời hay phải hỏi lại/chuyển labcoach?**

Intent classification là tín hiệu hỗ trợ quyết định này, không phải outcome cuối.

### Outcome

Bot xử lý câu lặp lại có căn cứ; labcoach tập trung vào câu chưa biết, rủi ro
hoặc cần thẩm quyền. Nội dung chỉ cải thiện knowledge base sau khi labcoach duyệt.

## 3. Product flow

```text
Learner hỏi
→ phân loại và tìm nguồn đã duyệt
→ kiểm tra đủ căn cứ
→ trả lời kèm nguồn | hỏi lại | handoff
→ unanswered queue
→ gom câu tương tự
→ labcoach sửa/phê duyệt
→ cập nhật knowledge base
→ hỗ trợ tốt hơn cho câu tương tự sau này
```

**Core flow/P0:** từ Learner hỏi đến answer/clarify/handoff, có nguồn và fail-safe.

**Mở rộng/P1:** queue, grouping, Labcoach View, chỉnh sửa/phê duyệt và mô phỏng
cập nhật knowledge base.

**Không ưu tiên/P2:** Discord integration thật, authentication, notification,
analytics nâng cao, phát hiện learner stuck và đồng bộ production.

## 4. Ground-truth policy

Thứ tự nguồn:

1. Tài liệu chính thức.
2. Nội dung labcoach đã phê duyệt.
3. Bài chia sẻ đã phê duyệt.
4. Dữ liệu khác chỉ là signal, không phải ground truth.

Quy tắc cứng:

- Không có nguồn thì không đoán.
- Output cũ của bot không phải nguồn sự thật.
- Tin nhắn Discord chưa duyệt không tự động trở thành knowledge.
- Mọi cập nhật knowledge base cần labcoach phê duyệt.
- Mỗi mục knowledge phải lưu nguồn, thời điểm và trạng thái phê duyệt.
- Logistics không nguồn phải hỏi lại hoặc handoff; tuyệt đối không tạo deadline,
  lịch, phòng hoặc link.
- Cờ “nguồn đã xác minh” chỉ được bật khi nguồn được phê duyệt và liên quan trực
  tiếp đến câu hỏi hiện tại.

## 5. Scope và ưu tiên

### P0 — Bắt buộc

- Learner View trên Streamlit.
- Câu hỏi tự do.
- Ít nhất một model call thật tại quyết định trung tâm.
- Tìm trong nguồn được duyệt.
- Answer/clarify/handoff.
- Trả lời có nguồn.
- Fail-safe khi model/API lỗi.
- Golden set ≥20.
- Evaluation run đầu tiên, giữ cả case fail.

### P1 — Nên có cho demo hai vai trò

- Labcoach View.
- Unanswered queue.
- Gom câu tương tự.
- Bản nháp câu trả lời/bài chia sẻ.
- Labcoach sửa và phê duyệt.
- Mô phỏng cập nhật knowledge base.

### P2 — Chỉ làm nếu còn thời gian

- Discord integration thật.
- Authentication và notification.
- Analytics nâng cao.
- Phát hiện learner stuck.
- Đồng bộ knowledge base production.

## 6. Non-goals

- Không trả lời mọi chủ đề.
- Không tự tạo deadline, lịch hoặc link.
- Không làm bài thay learner hay cung cấp đáp án hoàn chỉnh.
- Không thay thế hoàn toàn labcoach.
- Không tự động xuất bản nội dung.
- Không tự học từ output của bot.
- Không coi mọi tin nhắn Discord là sự thật.
- Không build Discord integration trước khi flow Streamlit được đo.
- Không thêm feature ngoài scope nếu team chưa duyệt.
- Không dùng dữ liệu VLearn như bằng chứng trực tiếp cho pain Discord nếu chưa
  chứng minh tính liên quan.

## 7. Checkpoint roadmap

| Mốc | Artifact / Definition of Done | Trạng thái repo | Còn thiếu |
|---|---|---|---|
| CP1 | Canvas 7 dòng; evidence ban đầu; lát cắt; automation; ≥3 willing users; phân công có tên | `IN PROGRESS` | Canvas đang là draft; evidence, willing users và tên owner `UNVERIFIED` |
| CP2 | Flow chính bấm hết được; có commit | `DONE` theo code/commit | Cần live-check lại trước demo |
| CP3 | Model call thật ở quyết định trung tâm; golden set ≥20; run 1 có % và đủ case fail | `IN PROGRESS` | Đã tích hợp model client và trace mẫu; live call `UNVERIFIED`; chưa có retrieval, `eval/` và kết quả |
| CP4 | Spec gần cuối; evidence chuẩn A/B; impact ≥3; bốn lớp chỗ khó; ≥4 HAX/PAIR; quality bar bằng số | `IN PROGRESS` | Spec còn draft; evidence/impact/owner thiếu; quality bar chỉ là đề xuất |
| Spec freeze | `spec.md` commit trước 23:59 N1; quality bar không hạ sau đó | `UNVERIFIED` | Cần team xác nhận commit freeze và bar chính thức |
| CP5 | ≥5 user test, trong đó ≥2 willing users CP1; quote nguyên văn; changelog; slide; dry run | `NOT STARTED` | Chưa có `validation/`, slide hoặc log |
| CP6 | Demo 5 phút + Q&A; sáu slide; case chuẩn + case khó; % so với bar; mọi thành viên trình bày | `NOT STARTED` | Chưa có slide, demo script hoặc reflection |

Không đánh dấu hoàn thành chỉ dựa trên mô tả. Nếu không kiểm tra được, dùng
`UNVERIFIED`.

## 8. Yêu cầu toàn dự án

- Một user, một việc, một quyết định AI, một kết quả.
- Có ≥1 model call thật.
- Cụ thể hóa bốn lớp chỗ khó.
- Có ≥8 kịch bản rủi ro.
- Golden set ≥20 đúng cơ cấu rubric.
- Có ≥10 case lấy/phát triển từ chatlog thật, được rút gọn và ẩn danh đúng quy
  định.
- Mọi evaluation run giữ cả case fail.
- Quality bar được chốt đúng hạn và không hạ sau khi thấy kết quả.
- User validation ≥5 người.
- Có reflection cho từng thành viên.
- Mỗi thành viên giải thích được phần mình phụ trách.

## 9. Trạng thái implementation hiện tại

### `DONE` / đã chạy được từ code và test

- Streamlit Learner View nhận input và hiển thị hội thoại.
- `app.py` đã nối `intent_engine.py` với model client và safety contract.
- Model client hỗ trợ Gemini/OpenAI-compatible call, timeout và lỗi mạng.
- Prompt CP3 version `cp3-safety-v1.1.0`.
- Validator parse JSON, kiểm tra schema, mapping intent/action và confidence.
- Fixed handoff cho logistics không có nguồn.
- Redaction credential trong `reply` và `rationale`.
- Context được JSON-encode để giảm delimiter injection.
- Có `.env.example` không chứa secret và safety fallback khi thiếu key.
- 23 unit test đang pass tại thời điểm cập nhật tài liệu.

### `IN PROGRESS` / đang mock hoặc chưa xác minh

- Model call path đã tích hợp nhưng unit test mock network; API call live
  `UNVERIFIED` từ môi trường hiện tại.
- `evidence/cp3-traces/sample-trace.json` là trace mẫu; không tự động chứng minh
  lượt gọi live nếu chưa có provenance/log thực được làm sạch.
- Handoff mới là thông báo UI, chưa tạo queue thật.
- Cờ nguồn logistics đã xác minh do caller cung cấp, chưa có retrieval kiểm chứng.

### `NOT STARTED`

- Approved-knowledge retrieval và citations.
- Labcoach View, queue, grouping, approval workflow.
- Knowledge-base update.
- Golden set, eval runner và run đầu tiên.
- User validation, slide, demo script và reflection.

## 10. Target architecture

```text
Streamlit UI
├─ Learner View
└─ Labcoach View
   ↓
Application service
   ↓
Intent + answer-or-escalate decision
   ├─ Approved-knowledge retrieval
   ├─ Model client
   └─ Output validation/redaction
   ↓
Answer with sources | Clarify | Unanswered queue
   ↓
Grouping + labcoach approval
   ↓
Knowledge-base update
   ↓
Evaluation
```

Không đặt logic nghiệp vụ, model call, retrieval hay validation trực tiếp trong
Streamlit UI. Không khóa framework retrieval/database trước khi flow P0 được đo.

## 11. Output contract

### Contract hiện đang được code enforce

Xem [`codebase/output_contract.py`](../codebase/output_contract.py):

```json
{
  "intent": "greeting | learning | logistics | ambiguous | out_of_scope",
  "confidence": 0.91,
  "action": "answer_briefly | answer_with_guidance | ask_clarifying_question | handoff_to_ta | decline_and_redirect",
  "reply": "Nội dung đã qua validation/redaction",
  "rationale": "Lý do định tuyến tóm tắt"
}
```

Mọi model output phải qua `validate_model_output()` trước khi hiển thị hoặc ghi
trace. Không lưu raw model output. Output lỗi phải chuyển fail-safe, không crash
hoặc đoán.

### Contract mục tiêu cho flow grounded answer

```json
{
  "intent": "program_question",
  "confidence": 0.91,
  "action": "answer_with_source",
  "answer": "Nội dung trả lời",
  "sources": [
    {
      "document": "04-rubric.md",
      "section": "CP3"
    }
  ],
  "rationale": "Tìm thấy căn cứ trong nguồn chính thức"
}
```

Action mục tiêu:

- `answer_with_source`
- `ask_clarifying_question`
- `handoff_to_labcoach`
- `decline_and_redirect`

Hai contract đang khác nhau. Đây là **migration chưa làm**, không phải thay tên
đơn giản. Trước khi đổi phải cập nhật đồng bộ prompt, validator, UI adapter,
tests, golden set, evidence và `spec.md`; không làm app vừa dùng hai schema ngầm.

## 12. Evaluation requirements

### `eval/golden-set.csv`

Tối thiểu nên có:

```text
case_id,input,case_type,difficulty_layer,expected_intent,expected_action,
requires_source,expected_source_ref,safety_rule,provenance
```

- ≥20 case.
- 8–10 case thường.
- ≥2 case cho mỗi lớp chỗ khó.
- 2–4 case hiếm.
- ≥10 case lấy/phát triển từ chatlog thật, đã ẩn danh và chỉ giữ phần tối thiểu.

### `eval/run-XX.csv`

Tối thiểu nên có:

```text
case_id,prompt_version,model,raw_output_ref,validated_intent,validated_action,
source_ref,pass_intent,pass_action,pass_grounding,pass_safety,overall_pass,notes
```

Không lưu secret hoặc raw nội dung nhạy cảm trong `raw_output_ref`.

Các chiều chất lượng: đúng intent, đúng action, grounding/source, xử lý mơ hồ,
đúng phạm vi và an toàn. Logistics không nguồn chỉ pass khi không có deadline,
lịch, link bịa và được clarify/handoff.

Mỗi thay đổi prompt/model phải chạy lại toàn bộ golden set. Không xóa case fail.
Quality bar trong `spec.md` hiện là **đề xuất, `UNVERIFIED`**, chưa được coi là
frozen nếu chưa có xác nhận commit đúng hạn.

## 13. Data và security

- Không commit `.env`, API key, Discord token hoặc authorization header.
- Phải có `.env.example` chỉ chứa tên biến và giá trị giả. File
  `codebase/.env.example` hiện đã có.
- Không commit dữ liệu cá nhân hoặc Discord thật chưa được phép/ẩn danh.
- Chỉ lưu trích đoạn tối thiểu đã ẩn danh; không sao chép nguyên data pack vào
  artifact nộp bài.
- Không log authorization header, raw secret, raw user input nhạy cảm hoặc raw
  model response chưa làm sạch.
- Trace AI phải qua validation và redaction.
- Không ghi/xuất bản lên Discord thật nếu người dùng chưa cho phép.
- Dữ liệu trong `data/vlearn-pack/` thuộc pack hạn chế của hackathon. Track B
  không có Discord pack riêng; không được suy diễn dữ liệu VLearn thành evidence
  Discord.
- Repository hiện vẫn chứa data pack từ starter history; việc repository nộp bài
  có được giữ pack này hay phải loại bỏ là `UNVERIFIED` và cần team/TA xác nhận.

## 14. Coding rules

- Tách business logic khỏi Streamlit UI.
- Dùng type/schema cho model output.
- Model/API phải có timeout, error handling và fail-safe.
- Viết test cho happy path, failure path và safety invariant.
- Không hardcode kết quả để làm đẹp demo.
- Không xóa/sửa kết quả evaluation nhằm tăng điểm.
- Không đổi scope, non-goals hoặc quality bar khi chưa được team duyệt.
- Không sửa file ngoài phạm vi task.
- Giữ thay đổi tương thích hoặc cung cấp migration rõ ràng.
- Trước khi hoàn thành phải chạy test phù hợp và báo chính xác phần chưa chạy.

Lệnh kiểm tra hiện tại:

```powershell
cd codebase
python -m unittest discover -s tests -v
python -m py_compile prompts.py output_contract.py
```

## 15. Definition of Done

- [ ] Chạy được theo README.
- [ ] Khớp lát cắt và checkpoint đang phục vụ.
- [ ] Có happy path và failure path.
- [ ] Không làm hỏng Learner/Labcoach View liên quan.
- [ ] Có test cho behavior quan trọng.
- [ ] Có timeout/fail-safe cho API/model nếu task chạm vào integration.
- [ ] Không có secret hoặc dữ liệu cá nhân.
- [ ] Cập nhật tài liệu/changelog khi behavior thay đổi.
- [ ] Chạy lại evaluation nếu thay prompt/model.
- [ ] Phần mock/thật được ghi trung thực.
- [ ] Không có thay đổi ngoài phạm vi task.

## 16. Change protocol

Trước khi code, agent phải tự trả lời:

1. Task phục vụ checkpoint nào?
2. Task phục vụ lát cắt thế nào?
3. Thuộc P0, P1 hay P2?
4. Có thêm hoặc đổi quyết định AI trung tâm không?
5. Có mâu thuẫn với spec hoặc non-goals không?
6. Cần thêm unit test/evaluation case nào?

Agent phải dừng và xin team xác nhận nếu task:

- thay đổi North Star hoặc lát cắt;
- thay đổi ground-truth policy;
- bỏ/thêm non-goal;
- thay quality bar;
- chuyển P1/P2 thành P0;
- thay output contract mà không có migration đồng bộ.

Khi báo cáo, luôn phân biệt `DONE`, `IN PROGRESS`, `NOT STARTED`, `BLOCKED` và
`UNVERIFIED`; dùng `TODO` cho dữ liệu chưa có. Không tự tạo evidence, số khảo sát,
tên thành viên, willing users, evaluation result hoặc trạng thái hoàn thành.
