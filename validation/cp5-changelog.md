# CP5 Changelog — Sau User Validation

| Phản hồi | Thay đổi | File chính | Trạng thái |
|---|---|---|---|
| Casual/trend bị chuyển Labcoach | Bổ sung casual routing và guard `greeting/answer_briefly` | `codebase/prompts.py`, `codebase/intent_engine.py` | Hoàn thành |
| Trả lời cứng, ít vui vẻ | Cập nhật phong cách hội thoại và biến thể fallback ngắn | `codebase/prompts.py`, `codebase/intent_engine.py` | Hoàn thành |
| Muốn có icon | Cho phép tối đa 1–2 emoji phù hợp ở casual/learning | `codebase/prompts.py` | Hoàn thành |
| Muốn nhớ người dùng | Trích xuất tên tự khai và lưu trong session; reset sẽ xóa | `codebase/conversation_context.py`, `codebase/app.py` | Hoàn thành |
| Không làm yếu safety | Contract fallback không bị casual guard ghi đè; logistics giữ nguyên nguồn approved | `codebase/intent_engine.py`, `codebase/prompts.py` | Hoàn thành |

## Không thay đổi

- Không thêm intent/action mới.
- Không tăng temperature toàn cục.
- Không lưu tên vào SQLite, handoff hoặc knowledge candidate.
- Không tự động coi phản hồi Labcoach là approved knowledge.
- Không thay đổi quality bar hoặc kết quả eval lịch sử.

## Dữ liệu self-test

Entry knowledge do thành viên team tự đóng vai Labcoach trong lúc thử không
được giữ trong `data/approved/`. Self-test chứng minh workflow UI nhưng không
đủ thẩm quyền để tạo nguồn chính thức.
