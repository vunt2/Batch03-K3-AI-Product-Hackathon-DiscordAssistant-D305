# CP1 Canvas — Discord Learner Assistant (Nhóm D305)

1. **Hướng:** B — Trợ lý Học viên Discord; tối ưu nhận diện intent và phản hồi đúng mức.
2. **Job executor:** Học viên đang đăng câu hỏi trong Discord khóa học AI Thực Chiến.
3. **Pain:** Khi học viên hỏi ngắn, mơ hồ hoặc hỏi logistics, việc xác định sai loại câu hỏi có thể tạo phản hồi sai mức; sai deadline/link có thể khiến học viên nộp muộn hoặc nộp sai nơi.
4. **Evidence ban đầu:** Khảo sát $n=28$ học viên ($20/28 = 71.4\%$ xác nhận vướng đau) và mining $n=100$ tin nhắn Discord ($28\%$ logistics, $18\%$ mơ hồ). Quote: *"Anh ơi deadline CP3 chốt 23:59 hôm nay hay trưa mai vậy ạ?"* (`DC-MINING-014`).
5. **Lát cắt MỘT CÂU:** Khi một học viên đăng câu hỏi trong Discord khóa học, trợ lý phân loại intent và chọn hành động trả lời, hỏi lại, chuyển TA hoặc từ chối, để học viên nhận được hỗ trợ đúng mức mà không bị cung cấp thông tin thiếu căn cứ.
6. **Automation + willing users:** Conditional — case rõ phản hồi; case mơ hồ hỏi lại; logistics thiếu nguồn chuyển TA vì cost-of-error cao.
   **Willing users ($\ge 3$ người):**
   - Nguyễn Văn An (HV-012, Zone A)
   - Trần Thị Bình (HV-045, Zone A)
   - Lê Hoàng Cường (HV-089, Zone B)
7. **Phân công nhóm D305:**
   - **Hưng (Owner):** Evidence, Impact analysis, AI Spec (`spec.md`) & Kiểm tra CP3.
   - **Vũ (Owner):** System Prompt, Output Contract & Safety Design.
   - **Tùng (Owner):** Streamlit Prototype UI & Intent Engine Call.
   - **Phong (Owner):** Golden Set (22 cases), Run Evaluation (`run_eval.py`) & Reviewer.


