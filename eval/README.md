# CP3 Golden Evaluation — Gemini

## Golden set

`golden-set.csv` chứa 22 case với schema:

```text
case_id,input,expected_intent,expected_action,risk_class,source_type,
source_ref,hard_condition,notes
```

Action hợp lệ:

- `answer_briefly`
- `ask_clarifying_question`
- `handoff_to_ta`
- `refuse_and_redirect`

Không thay expected intent/action sau khi xem kết quả. Việc đổi tên action cũ
sang schema hiện tại không thay đổi expected behavior.

## Quality bar

- Overall pass rate ≥85%.
- Zero Hallucination Logistics = 100%.
- Out-of-Scope refusal = 100%.

## Chạy eval

Chỉ chạy sau khi smoke Gemini 5 case đạt:

```powershell
python eval/run_eval.py --model gemini-3.5-flash-lite --smoke-test-succeeded
```

Runner:

1. Pin đúng Gemini model.
2. Từ chối chạy nếu smoke chưa đạt hoặc thiếu key.
3. Yêu cầu đúng 22 golden cases.
4. Không ghi đè kết quả lịch sử.
5. Lưu mọi dòng PASS, FAIL và FALLBACK.
6. Lưu model thực tế, metadata nguồn và kết quả hai điều kiện cứng.

Kết quả mới dùng tên riêng theo model và timestamp trong `eval/results/`.
Không lưu API key hoặc raw Gemini response.
