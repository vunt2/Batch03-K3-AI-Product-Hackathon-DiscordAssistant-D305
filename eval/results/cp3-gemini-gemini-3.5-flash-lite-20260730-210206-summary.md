# CP3 evaluation — Gemini / gemini-3.5-flash-lite

- Timestamp: 2026-07-30T21:04:32
- Model pinned: `gemini-3.5-flash-lite`
- Prompt version: `cp3-gemini-demo-v2.0.0`
- Result: **20/22**
- Total cases: 22
- PASS: 20
- FAIL: 2
- FALLBACK: 0
- Overall pass rate: 90.9%
- Overall threshold (>=85%): **PASS (90.9%)**
- Quality Bar (overall threshold + both hard conditions): **NOT MET**
- Intent accuracy: 95.5%
- Action accuracy: 90.9%
- Zero Hallucination Logistics: 83.3% (5/6)
- Out-of-Scope refusal: 100.0% (5/5)
- Decision: **HOLD**

## Unachieved Cases Breakdown (FAIL / FALLBACK)

- **GS-008** (FAIL): Input: "Vừa làm bài tập vừa xem nộp bài ở đâu vậy ạ" | Expected: ambiguous/ask_clarifying_question | Actual: logistics/handoff_to_ta | Reason: Intent diff (exp 'ambiguous' vs act 'logistics'); Action diff (exp 'ask_clarifying_question' vs act 'handoff_to_ta')
- **GS-021** (FAIL): Input: "Lớp mình mấy giờ bắt đầu học buổi tiếp theo ạ?" | Expected: logistics/handoff_to_ta | Actual: logistics/answer_briefly | Reason: Action diff (exp 'handoff_to_ta' vs act 'answer_briefly'); Hard condition failed

---
*The CSV preserves every PASS, FAIL, and FALLBACK row. The run is Gemini-only and stores no raw credential or raw Gemini response.*
