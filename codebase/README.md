# D305 Discord Assistant (Learner & Labcoach Support)

Hệ thống trợ lý học tập và quản lý Handoff Queue hỗ trợ Learner và Labcoach dành cho khóa học AI Product Hackathon.

---

## 1. Mục tiêu Sản phẩm
D305 Discord Assistant giúp giải quyết hai bài toán chính trong hỗ trợ học tập:
1. **Phản hồi chính xác cho Learner:** Trả lời tự nhiên, thân thiện dựa trên 100% dữ liệu đã được xác minh (human-approved knowledge). Chatbot tuyệt đối không bịa đặt thông tin quy định hay logistics khi chưa có nguồn chính thức.
2. **Quản lý Handoff Queue tập trung cho Labcoach:** Tự động chuyển các câu hỏi chưa đủ căn cứ vào hàng chờ SQLite persistent. Cho phép Labcoach giải đáp, biến câu trả lời thành Knowledge Candidate, thực hiện quy trình Review, Publish công khai và tạo bản tổng hợp Daily Digest cuối ngày.

---

## 2. Hai Vai trò Trong Ứng dụng
- **Learner Workspace:** Giao diện cho học viên hỏi đáp về khóa học, nhận câu trả lời được gắn nhãn nguồn xác minh hoặc thông báo chuyển tiếp cho Labcoach.
- **Labcoach Workspace:** Giao diện cho đội ngũ hỗ trợ xử lý hàng chờ Handoff, duyệt Knowledge Candidates, Publish Knowledge mới và tải Báo cáo tổng hợp cuối ngày.

---

## 3. Danh sách Chức năng Đã Hoàn thiện
- **Gemini-only Engine:** Phân loại ý định (Intent), mức độ tin cậy và quyết định hành động bằng Gemini LLM với cơ chế Safety Fallback đóng mở an toàn.
- **Human-Approved Knowledge Retrieval:** Loader đọc và khớp thông tin chính xác từ các nguồn kiến thức đã duyệt.
- **Conversation Context v1:** Hiểu câu hỏi nối tiếp trong cùng phiên hội thoại nhưng không xem lịch sử chat là nguồn logistics chính thức.
- **Persistent Handoff Queue v1:** Lưu trữ hàng chờ câu hỏi vào SQLite database (`data/runtime/assistant.db`), đảm bảo không mất dữ liệu khi restart app.
- **Labcoach Response & Knowledge Candidate Capture:** Tự động capture câu trả lời của Labcoach thành Candidate mang trạng thái `pending_review` (chưa tự động đưa vào kho chính thức).
- **Knowledge Candidate Review v1:** Giao diện cho team xem, chỉnh sửa nội dung, nhập tên người duyệt và chuyển trạng thái candidate thành `approved_for_publish` hoặc `rejected`.
- **Knowledge Publisher Backend & UI:** Publish candidate đã duyệt thành file kiến thức `data/approved/labcoach-knowledge.json` với cơ chế ghi file atomic (temp file replace) và chống trùng lặp (collision detection) với kho gốc.
- **Dual-Source Knowledge Loader:** Loader tự động hợp nhất và khử trùng lặp (deduplicate) kiến thức từ cả `course-knowledge.json` và `labcoach-knowledge.json`.
- **Labcoach Daily Insights (Daily Digest):** Gom nhóm các câu hỏi lặp trùng dựa trên thuật toán Jaccard similarity và xuất báo cáo tổng hợp Markdown cuối ngày theo múi giờ `Asia/Bangkok`.

---

## 4. Cấu trúc Dữ liệu (Data Architecture)
- `data/approved/course-knowledge.json`: File chứa dữ liệu kiến thức khóa học chính thức ban đầu.
- `data/approved/labcoach-knowledge.json`: File chứa các kiến thức mới được Labcoach duyệt và publish.
- `data/runtime/assistant.db`: Database SQLite lưu trữ hàng chờ Handoffs và danh sách Knowledge Candidates.

---

## 5. Cài đặt Dependency & Cấu hình Môi trường

### Cài đặt Dependency
```bash
pip install -r codebase/requirements.txt
```

### Cấu hình file `.env` Local
Tạo file `codebase/.env` từ file mẫu `codebase/.env.example`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_TIMEOUT_SECONDS=30
ASSISTANT_DB_PATH=data/runtime/assistant.db
```

---

## 6. Hướng dẫn Chạy Local & Chạy Unit Tests

### Lệnh chạy ứng dụng Local
```bash
streamlit run codebase/app.py
```

### Lệnh chạy Unit Test Suite
```bash
python -m unittest discover -s codebase/tests -p "test_*.py"
```

---

## 7. Hướng dẫn Deploy lên Streamlit Cloud

### Cấu hình ứng dụng khi Deploy
- **Main file path:** `codebase/app.py`
- **Requirements file:** `codebase/requirements.txt`

### Cấu hình Streamlit Secrets
Trong phần cấu hình **App Settings -> Secrets** trên Streamlit Cloud, nhập thông tin:
```toml
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_TIMEOUT_SECONDS = "30"
ASSISTANT_DB_PATH = "data/runtime/assistant.db"
```
Ứng dụng tự động sử dụng `st.secrets` thông qua helper `load_runtime_secrets()`.

> **Lưu ý bảo mật:** Tuyệt đối không commit file `.env` chứa API Key thật hoặc file `secrets.toml` lên repository Git.

---

## 8. Quy trình Demo Hoàn chỉnh (End-to-End Flow)
1. **Learner đặt câu hỏi:** Đặt một câu hỏi logistics chưa có trong kho kiến thức cũ (ví dụ: *"Khi nào tổ chức thi thử?"*).
2. **Handoff tự động:** Bot nhận diện thiếu nguồn chính thức, phản hồi lịch sự và tạo một bản ghi Handoff `pending` trong SQLite queue.
3. **Labcoach xử lý:** Chuyển sang **Labcoach Workspace**, nhập câu trả lời chính xác cho Learner và bấm nút gửi.
4. **Candidate Capture & Review:** Hệ thống lưu câu trả lời thành Candidate `pending_review`. Đội ngũ hỗ trợ xem xét, chỉnh sửa văn phong, điền tên Người duyệt và bấm **"Duyệt để chờ publish"**.
5. **Publish Knowledge:** Tại mục *"Knowledge sẵn sàng publish"*, bấm **"Publish knowledge"**. Dữ liệu được ghi an toàn vào `labcoach-knowledge.json`.
6. **Chatbot cập nhật:** Chuyển lại **Learner Workspace**, đặt lại câu hỏi ban đầu. Bot lập tức tìm thấy kiến thức mới vừa publish và trả lời chính xác kèm nhãn nguồn đã xác minh.
7. **Tải Báo cáo Tổng hợp:** Cuối ngày, Labcoach vào mục *"Tổng hợp cuối ngày"* để xem thống kê câu lặp trùng và tải file Markdown `labcoach-digest-YYYY-MM-DD.md`.

---

## 9. Giới hạn Trung thực của Sản phẩm Demo (Limitations & Disclosures)
- **Lưu trữ SQLite trên PaaS / Cloud:** Khi deploy ứng dụng trên các dịch vụ đám mây có môi trường lưu trữ tạm (ephemeral storage như Streamlit Cloud miễn phí), file `assistant.db` và `labcoach-knowledge.json` có thể bị reset khi server restart.
- **Chưa có Authentication / Phân quyền:** Giao diện Labcoach View hiện tại mở công khai nhằm mục đích demo trải nghiệm. Chưa tích hợp hệ thống đăng nhập, phân quyền Role-Based Access Control (RBAC).
- **Phạm vi tích hợp:** Ứng dụng hiện tại chạy trên giao diện web Streamlit Demo, chưa kết nối trực tiếp bot Discord API thật.
- **Không tự động Publish:** Mọi kiến thức từ phản hồi của Labcoach phải qua bước duyệt thủ công của con người trước khi được publish cho Chatbot sử dụng.
- **Báo cáo Daily Digest:** Bản tổng hợp cuối ngày sử dụng các thuật toán gom nhóm và thống kê định tính chính xác, không dùng AI/LLM để bịa đặt hay diễn giải câu trả lời.
