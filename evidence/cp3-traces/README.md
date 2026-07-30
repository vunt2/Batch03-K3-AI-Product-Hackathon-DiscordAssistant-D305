# CP3 AI Call Traces & Evidence

Thư mục này chứa vết dữ liệu (traces) minh họa các lượt gọi model LLM thật tại mốc **CP3** cho dự án **Trợ lý Học viên Discord (Nhóm D305)**.

## Quy tắc lưu Trace & Bảo mật

1. **Minh chứng AI thật:** Trace ghi nhận input người dùng, model được sử dụng (`gemini-1.5-flash` / `gpt-4o-mini`), version của system prompt (`cp3-safety-v1.1.0`), raw model response và validated output sau khi qua Output Contract Validator.
2. **Khóa bảo mật (Zero API Key Leak):** Mọi trace đều tuân thủ quy tắc Redaction. API Keys, Bearer Tokens, Discord Tokens hoặc Passwords tuyệt đối không xuất hiện trong file trace.
3. **Minh chứng Safety Fallback:** Mẫu trace minh họa trường hợp câu hỏi Logistics không có nguồn xác minh (`verified_context_provided = false`), mặc dù AI thật đã cố đưa ra ngày deadline nhưng **Output Validator đã loại bỏ câu trả lời bịa** và chuyển về `handoff_to_ta` an toàn.

## Cấu trúc file Sample Trace (`sample-trace.json`)

```json
{
  "trace_id": "cp3-example-001",
  "timestamp": "2026-07-30T13:35:00Z",
  "input": "Deadline CP3 là khi nào?",
  "model": "gemini-1.5-flash",
  "prompt_version": "cp3-safety-v1.1.0",
  "verified_context_provided": false,
  "raw_output_redacted": { ... },
  "validated_output": { ... },
  "fallback_used": true
}
```
