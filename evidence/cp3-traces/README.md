# CP3 sanitized Gemini traces

Thư mục chỉ lưu input an toàn, metadata model/knowledge và output đã qua
validator. Không lưu API key, header xác thực, environment hoặc raw Gemini
response.

- `gemini-live-smoke-2026-07-30.json`: run live lịch sử trước khi đồng bộ
  Gemini-only.
- `gemini-smoke-20260730-134559.json`: 3 PASS, 2 FALLBACK; hai handoff hợp lệ
  khi đó còn bị đánh dấu fallback theo semantics cũ.
- `eval/results/cp3-gemini-gemini-3.5-flash-lite-20260730-210206-summary.md`:
  Golden Eval 22 cases live (`gemini-3.5-flash-lite`). Result: 20/22 PASS
  (90.9%), 2 FAIL, 0 FALLBACK. CP3 checkpoint hoàn thành; Quality Bar
  **NOT MET / HOLD** vì điều kiện cứng logistics đạt 5/6.
