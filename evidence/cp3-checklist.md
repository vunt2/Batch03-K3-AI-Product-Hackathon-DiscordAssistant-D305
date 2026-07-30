# CP3 Checklist — AI, Grounding và Safety (Nhóm D305)

> Cập nhật 30/07/2026. Trạng thái tổng: **CP3 DONE**. Đã thực hiện Gemini real calls, chạy đủ golden set 22 câu và xuất kết quả mới đủ 22 dòng.

| # | Tiêu chí | Trạng thái | Minh chứng |
|---|---|---|---|
| 1 | Gemini call live ở quyết định trung tâm | **PASS** | `gemini-3.5-flash-lite` gọi live thành công qua golden eval 22 cases |
| 2 | Unit test và compile | **PASS** | 47/47 unit test; py_compile và `git diff --check` pass |
| 3 | Retrieval không gắn sai nguồn | **PASS** | Nhà ăn/deadline tạo team không match; Mentor Duty→KB-030; weekly→KB-013/KB-006 |
| 4 | Trace được làm sạch | **PASS** | Lưu kết quả tại `eval/results/`; không chứa raw credential hay raw response |
| 5 | Golden set đủ case | **PASS** | `eval/golden-set.csv` đủ 22 case, schema action đồng bộ |
| 6 | Smoke test đạt điều kiện mở eval | **PASS** | Smoke test đã đạt điều kiện mở eval với Gemini real calls thành công |
| 7 | Golden eval chính thức | **PASS** | Chạy 22 cases live: `cp3-gemini-gemini-3.5-flash-lite-20260730-210206.csv` (20/22 PASS, 90.9%) |
| 8 | Hai điều kiện cứng | **NOT MET / HOLD** | Zero Hallucination Logistics: 83.3% (5/6); Out-of-Scope refusal: 100.0% (5/5) |

## Golden Eval Run Live (30/07/2026)

- Model: Gemini / `gemini-3.5-flash-lite`
- File CSV: `eval/results/cp3-gemini-gemini-3.5-flash-lite-20260730-210206.csv`
- File Summary: `eval/results/cp3-gemini-gemini-3.5-flash-lite-20260730-210206-summary.md`
- Tổng số case: 22/22
- Kết quả: **20/22**
- PASS: **20** | FAIL: **2** (GS-008, GS-021) | FALLBACK: **0**
- Quality Bar: **NOT MET / HOLD** — overall đạt 90.9%, nhưng điều kiện cứng
  Zero Hallucination Logistics chỉ đạt 83.3% (5/6).
- Điều kiện cứng 1 (Zero Hallucination Logistics): **83.3% (5/6)**
- Điều kiện cứng 2 (Out-of-Scope refusal): **100.0% (5/5)**

## Kết luận

**CP3 CHECKPOINT DONE — QUALITY BAR NOT MET / HOLD**. Đã có Gemini real call
live, chạy đủ 22 câu golden set và lưu bảng kết quả mới 22 dòng đầy đủ, trung
thực. Ngưỡng tổng đạt 90.9%, nhưng điều kiện cứng logistics chỉ đạt 5/6.
