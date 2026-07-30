# D305 Learner Assistant

Ứng dụng Streamlit dùng Gemini để phân loại câu hỏi, kiểm tra knowledge đã được
duyệt và vận hành luồng hỗ trợ Learner/Labcoach.

## Cấu hình local

Copy `codebase/.env.example` thành `codebase/.env`, sau đó điền:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_TIMEOUT_SECONDS=30
```

Không commit file `.env`. Ứng dụng tải file này bằng đường dẫn tuyệt đối dựa
trên vị trí code, nên có thể chạy lệnh từ thư mục gốc repository.

## Chạy ứng dụng

```powershell
python -m streamlit run codebase/app.py
```

Nếu key trống hoặc Gemini tạm thời lỗi, ứng dụng chuyển sang safety fallback,
không crash và không tự tạo thông tin logistics.

## Luồng demo

- Learner nhận câu trả lời từ nguồn approved khi có match chắc chắn.
- Câu mơ hồ được hỏi lại; yêu cầu làm hộ bị từ chối.
- Logistics không có nguồn phù hợp được đưa vào handoff queue.
- Labcoach trả lời, đánh dấu đã xử lý hoặc mở lại câu hỏi.
- Phản hồi Labcoach xuất hiện trong hội thoại Learner nhưng không tự động cập
  nhật knowledge base.
