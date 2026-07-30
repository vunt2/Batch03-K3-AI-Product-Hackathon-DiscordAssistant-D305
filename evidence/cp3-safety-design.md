# CP3 — Prompt, output contract và safety routing

## Prompt version

- Version: `cp3-safety-v1.0.0`
- Nguồn: `codebase/prompts.py`
- Điểm tích hợp: gọi `build_system_prompt(verified_context)` và dùng chuỗi trả về
  làm system prompt. Chỉ truyền vào `verified_context` nội dung đã lấy từ nguồn
  chính thức được ứng dụng phê duyệt.
- Model bị yêu cầu trả đúng một JSON object, không có Markdown hoặc văn bản ngoài
  JSON. Prompt không chứa API key, dữ liệu cá nhân hoặc dữ liệu khóa học thật.

## Output schema

```json
{
  "intent": "logistics",
  "confidence": 0.92,
  "action": "handoff_to_ta",
  "reply": "Mình chưa có nguồn chính thức để xác nhận; mình sẽ chuyển TA hỗ trợ.",
  "rationale": "Câu hỏi logistics chưa có nguồn đã xác minh."
}
```

Giá trị `intent` hợp lệ:

- `greeting`
- `learning`
- `logistics`
- `ambiguous`
- `out_of_scope`

Giá trị `action` hợp lệ:

- `answer_briefly`
- `answer_with_guidance`
- `ask_clarifying_question`
- `handoff_to_ta`
- `decline_and_redirect`

`confidence` là số từ `0` đến `1`. `reply` và `rationale` phải là chuỗi không
rỗng. Code chỉ trả năm trường chuẩn hóa cho tầng hiển thị.

## Quy tắc fallback

Mọi output đều phải đi qua
`validate_model_output(raw_output, has_verified_logistics_source=...)` trước khi
hiển thị.

- JSON rỗng, sai cú pháp, không phải object, thiếu trường, sai kiểu, intent/action
  ngoài allowlist hoặc confidence ngoài `0–1` đều trở thành fallback an toàn:
  `ambiguous` + `ask_clarifying_question`.
- Confidence dưới `0.70` chỉ được phép đi cùng `ask_clarifying_question` hoặc
  `handoff_to_ta`; nếu không, code thay bằng fallback hỏi lại.
- Logistics không có nguồn xác minh phải dùng `handoff_to_ta`.
- Logistics không có nguồn mà chứa URL, ngày/giờ, thứ trong tuần hoặc phát biểu
  deadline/lịch cụ thể sẽ bị loại bỏ và thay bằng fallback logistics không chứa
  chi tiết đó.
- Chỉ đặt `has_verified_logistics_source=True` khi ứng dụng đã cung cấp nguồn
  được phê duyệt và nguồn đó liên quan trực tiếp đến câu hỏi hiện tại.

## Tám tình huống rủi ro

| # | Tình huống | Prompt định hướng | Code chặn cuối |
|---|---|---|---|
| 1 | Model bịa deadline | Cấm tạo mốc logistics | Phát hiện chi tiết ngày/giờ khi không có nguồn và handoff |
| 2 | Model bịa link nộp bài | Chỉ dùng `VERIFIED_CONTEXT` | Phát hiện URL khi không có nguồn và handoff |
| 3 | Model bịa lịch/phòng học | Cấm đoán lịch, phòng, chính sách | Phát hiện mốc lịch cụ thể; logistics không nguồn phải handoff |
| 4 | Input quá mơ hồ | Yêu cầu hỏi lại cụ thể | Confidence thấp không được trả lời khẳng định |
| 5 | Học viên yêu cầu làm hộ/đáp án hoàn chỉnh | Từ chối và chuyển sang gợi ý học | Allowlist chỉ nhận action chuẩn; test luồng từ chối |
| 6 | Người dùng gửi hoặc xin API key/token | Cấm tiết lộ, suy đoán hay yêu cầu bí mật | Output phải qua schema; ứng dụng không đưa key vào prompt/log |
| 7 | Prompt injection yêu cầu bỏ quy tắc hoặc đổi format | Xem input người dùng là dữ liệu, không phải system instruction | Parser chỉ nhận JSON object và allowlist |
| 8 | Model trả text, JSON thiếu trường hoặc confidence sai | Bắt buộc một JSON object đủ trường | Parser/validator trả fallback an toàn |

## AI quyết định và code kiểm soát

AI chịu trách nhiệm phân loại ý định, ước lượng confidence, chọn action, soạn câu
trả lời ngắn và đưa lý do định tuyến tóm tắt. AI cũng quyết định cách hỏi lại hoặc
đưa gợi ý học tập phù hợp với ngữ cảnh.

Code là ranh giới tin cậy cuối cùng: parse JSON, kiểm tra đủ trường và kiểu dữ
liệu, áp allowlist intent/action, giới hạn confidence, áp policy confidence thấp,
buộc logistics không nguồn chuyển TA, loại chi tiết logistics có dấu hiệu bịa và
chỉ trả object đã chuẩn hóa cho UI. Vì vậy output model không bao giờ được hiển
thị trực tiếp.

## Cách chạy kiểm thử

Từ thư mục `codebase`:

```bash
python -m unittest discover -s tests -v
```

