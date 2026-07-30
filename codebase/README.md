# Discord Learner Assistant — CP3 (AI Real Integration)

Streamlit prototype cho Trợ lý Học viên Discord kết nối model LLM thật (`gemini-1.5-flash` / `gpt-4o-mini`) và kiểm soát an toàn qua Output Contract Validator.

## Hướng dẫn cài đặt & cấu hình

### 1. Cài đặt thư viện
```powershell
cd codebase
python -m pip install -r requirements.txt
```

### 2. Cấu hình file môi trường `.env`
Tạo file `.env` trong thư mục `codebase/` từ template `.env.example`:
```powershell
cp .env.example .env
```

Mở file `.env` và điền thông số API key của bạn:
```env
MODEL_API_KEY=your_gemini_or_openai_api_key_here
MODEL_NAME=gemini-1.5-flash
```

*Lưu ý: Nếu không cấu hình `MODEL_API_KEY`, ứng dụng vẫn chạy ở chế độ **Safety Fallback** mà không bị crash.*

### 3. Chạy ứng dụng Streamlit
```powershell
python -m streamlit run app.py
```

### 4. Chạy Unit Tests
```powershell
python -m unittest discover -s tests -v
```

## Các tính năng & Safety Contract ở CP3

1. **AI Call thật:** Gọi model LLM phân loại 5 nhóm intent (`greeting`, `learning`, `logistics`, `ambiguous`, `out_of_scope`).
2. **Output Contract Validator:** Kiểm tra định dạng JSON, allowlist cặp (intent, action), ép confidence < 0.70 phải hỏi lại/handoff.
3. **Zero Hallucination Logistics:** Mọi câu hỏi logistics không có nguồn tài liệu xác minh sẽ bị tự động hủy câu trả lời của AI và chuyển sang `handoff_to_ta`.
4. **Credential Redaction:** Tự động lọc bỏ các API Key, Token, Password lỡ xuất hiện trong câu trả lời hoặc rationale.
