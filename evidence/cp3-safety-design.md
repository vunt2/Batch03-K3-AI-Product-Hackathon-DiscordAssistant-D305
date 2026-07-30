# CP3 — Prompt, output contract và safety routing

## Prompt version

- Version: `cp3-safety-v1.1.0`
- Nguồn: `codebase/prompts.py`
- Điểm tích hợp: gọi `build_system_prompt(verified_context)` và dùng chuỗi trả
  về làm system prompt.
- Chỉ truyền `verified_context` lấy từ nguồn chính thức đã được ứng dụng phê
  duyệt. Context là dữ liệu tham khảo, không phải instruction.
- Prompt không chứa API key, dữ liệu cá nhân hoặc dữ liệu khóa học thật.

`build_system_prompt()` serialize context thành một JSON object bằng
`json.dumps()`. Ký tự `<` và `>` được encode thành `\u003c` và `\u003e`; prompt
không dùng XML closing delimiter. Vì vậy chuỗi như `</VERIFIED_CONTEXT>` trong
context không thể đóng một vùng prompt rồi chèn instruction. System prompt cũng
yêu cầu bỏ qua mọi instruction nằm trong dữ liệu context.

## Output schema

```json
{
  "intent": "logistics",
  "confidence": 0.92,
  "action": "handoff_to_ta",
  "reply": "Mình chưa có nguồn chính thức để xác nhận thông tin này. Mình sẽ chuyển câu hỏi cho TA hỗ trợ.",
  "rationale": "Câu hỏi logistics chưa có nguồn đã xác minh."
}
```

Các intent hợp lệ là `greeting`, `learning`, `logistics`, `ambiguous` và
`out_of_scope`. Các action hợp lệ là `answer_briefly`,
`answer_with_guidance`, `ask_clarifying_question`, `handoff_to_ta` và
`decline_and_redirect`.

`confidence` phải là số trong khoảng `0–1`; boolean không được coi là số.
`reply` và `rationale` phải là chuỗi không rỗng. Code chỉ trả năm trường chuẩn
hóa cho tầng hiển thị hoặc trace đã kiểm soát.

## Mapping intent/action

| Intent | Action hợp lệ khi confidence từ 0.70 trở lên |
|---|---|
| `greeting` | `answer_briefly` |
| `learning` | `answer_with_guidance` |
| `logistics` | `answer_briefly`, `handoff_to_ta` |
| `ambiguous` | `ask_clarifying_question` |
| `out_of_scope` | `decline_and_redirect` |

`logistics + answer_briefly` chỉ hợp lệ khi
`has_verified_logistics_source=True`. Khi confidence dưới `0.70`, chỉ
`ask_clarifying_question` hoặc `handoff_to_ta` được phép. Mọi cặp sai route đều
bị bỏ toàn bộ reply model và chuyển sang fallback an toàn.

## Quy tắc fallback

Mọi model output phải đi qua:

```python
safe_output = validate_model_output(
    raw_output,
    has_verified_logistics_source=has_approved_relevant_source,
)
```

Không hiển thị hoặc ghi trace từ `raw_output`.

- JSON rỗng, sai cú pháp, không phải object, thiếu trường, sai kiểu, intent/action
  ngoài allowlist, confidence ngoài `0–1` hoặc cặp intent/action sai đều trở
  thành `ambiguous + ask_clarifying_question`.
- Confidence dưới `0.70` nhưng action không hỏi lại/handoff cũng dùng fallback.
- Nếu `intent=logistics` và `has_verified_logistics_source=False`, validator
  luôn bỏ `reply` và `rationale` do model sinh, bất kể model đã chọn action gì.
  Output luôn là `logistics + handoff_to_ta` với `SAFE_LOGISTICS_REPLY` cố định.
- Chỉ đặt `has_verified_logistics_source=True` khi nguồn được phê duyệt có thông
  tin liên quan trực tiếp đến câu hỏi hiện tại.

## Redaction thông tin nhạy cảm

`redact_sensitive_text()` được áp dụng cho cả `reply` và `rationale` trước khi
trả output hợp lệ. Giá trị nhạy cảm được thay bằng `[REDACTED]`. Bộ lọc nhận diện
ít nhất:

- OpenAI-style key bắt đầu bằng `sk-`;
- Google-style key bắt đầu bằng `AIza`;
- Bearer token;
- token Discord có ba segment;
- giá trị sau nhãn `password`, `secret`, `token`, `api_key` hoặc `api key`;
- chuỗi token dài đáng ngờ có cả chữ và số.

Fallback reason chỉ dùng lý do tĩnh do code tạo, không nối raw output hoặc secret.
Module này không tự ghi trace. Tầng tích hợp phải chỉ lưu `safe_output`; nếu lưu
raw request/model response trước validator thì vẫn có nguy cơ rò dữ liệu.

## Các tình huống rủi ro và kiểm soát

| # | Tình huống | Prompt định hướng | Code kiểm soát cuối |
|---|---|---|---|
| 1 | Model bịa deadline | Cấm tự tạo logistics | Không nguồn thì bỏ toàn bộ reply và dùng fixed handoff |
| 2 | Model bịa link/phòng/lịch bằng cách viết không khớp regex | Chỉ dùng context đã xác minh | Không dựa vào regex; mọi logistics không nguồn đều fixed handoff |
| 3 | Model chọn sai intent/action để né policy | Nêu route chuẩn | Kiểm tra `EXPECTED_ACTIONS_BY_INTENT` |
| 4 | Input mơ hồ hoặc confidence thấp | Yêu cầu hỏi lại | Chỉ cho hỏi lại/handoff dưới ngưỡng `0.70` |
| 5 | Học viên yêu cầu làm hộ/đáp án hoàn chỉnh | Từ chối và chuyển sang gợi ý | `out_of_scope` chỉ được `decline_and_redirect` |
| 6 | Model lặp API key/token trong reply | Cấm tiết lộ bí mật | Redact reply trước khi trả |
| 7 | Model lặp secret trong rationale | Chỉ nêu lý do định tuyến | Redact rationale trước khi trả |
| 8 | Context chứa closing delimiter/instruction giả | Context chỉ là dữ liệu | JSON encode, neutralize `<`/`>`, không dùng closing delimiter |
| 9 | Model trả text, JSON thiếu trường hoặc sai kiểu | Bắt buộc JSON đủ trường | Parser/schema checks trả fallback |
| 10 | Prompt injection yêu cầu đổi schema/policy | Không coi dữ liệu là system instruction | Allowlist, route mapping và fallback vẫn do code quyết định |

## AI quyết định và code kiểm soát

AI phân loại intent, ước lượng confidence, đề xuất action, soạn reply và rationale
tóm tắt. AI không phải ranh giới tin cậy.

Code parse JSON, kiểm tra schema và type, áp allowlist, kiểm tra mapping
intent/action, áp policy confidence thấp, xác minh cờ nguồn logistics, thay
logistics không nguồn bằng fixed handoff, redact secret và chỉ sau đó mới trả
object chuẩn hóa cho UI/trace.

## Giới hạn còn lại

- Redaction dựa trên pattern nên có thể bỏ lọt định dạng credential mới hoặc che
  nhầm một chuỗi dài hợp lệ.
- Encoding và system instruction làm giảm delimiter/prompt injection nhưng không
  bảo đảm model miễn nhiễm tuyệt đối; code-side contract vẫn là lớp quyết định.
- `has_verified_logistics_source` do tầng tích hợp cung cấp. Nếu caller đặt
  `True` khi nguồn không được phê duyệt hoặc không liên quan, validator không thể
  tự đánh giá tính xác thực của nguồn.
- Không nên ghi raw model response, user input nhạy cảm hoặc raw context vào log.

## Cách chạy kiểm thử

Từ thư mục `codebase`:

```bash
python -m unittest discover -s tests -v
python -m py_compile prompts.py output_contract.py
```
