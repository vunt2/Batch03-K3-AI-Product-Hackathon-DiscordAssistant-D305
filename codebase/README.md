# Discord Learner Assistant — CP2

Prototype Streamlit cho flow phân loại intent của Trợ lý Học viên Discord.

## Chạy local

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Sau đó mở địa chỉ Streamlit hiển thị trong terminal.

## Flow có thể demo

1. Chào hỏi → trả lời ngắn.
2. Hỏi bài → hướng dẫn học theo từng bước.
3. Hỏi logistics → chuyển TA vì CP2 chưa kết nối nguồn chính thức.
4. Câu hỏi mơ hồ → hỏi thêm ngữ cảnh.
5. Yêu cầu ngoài phạm vi → từ chối và định hướng cách học an toàn.

## Trạng thái mock

- `intent_engine.py` đang dùng luật từ khóa, không phải AI thật.
- Không có API key và không sử dụng dữ liệu người dùng thật.
- Ở CP3 có thể thay `classify_message()` bằng lời gọi model thật mà không đổi flow giao diện.
