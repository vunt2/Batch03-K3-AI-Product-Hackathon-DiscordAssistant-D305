# CP1 Canvas — Discord Learner Assistant (Nhóm D305)

1. **Hướng:** B — Trợ lý Học viên Discord; tối ưu nhận diện intent và phản hồi đúng mức.
2. **Job executor:** Học viên đang đăng câu hỏi trong Discord khóa học AI Thực Chiến.
3. **Pain:** Khi học viên hỏi ngắn, mơ hồ hoặc hỏi logistics, việc xác định sai loại câu hỏi có thể tạo phản hồi sai mức; sai deadline/link có thể khiến học viên nộp muộn hoặc nộp sai nơi.
4. **Evidence ban đầu (Khảo sát thực tế $N=20$, $n=18$ học viên):**
   - $16/18$ học viên (**88.9%**) mất ít nhất 1 phút để tìm thông tin logistics trên Discord.
   - $15/18$ học viên (**83.3%**) từng từ bỏ tìm kiếm vì trôi tin nhắn quá nhanh.
   - $11/18$ học viên (**61.1%**) yêu cầu AI phải chuyển sang TA khi không chắc chắn thông tin.
   - *Quote mạnh nhất:* *"Cần nhất là AI không bịa deadline hay thông tin sai lệch làm ảnh hưởng kết quả học."* (`survey-summary.md`)
5. **Lát cắt MỘT CÂU:** Khi một học viên đăng câu hỏi trong Discord khóa học, trợ lý phân loại intent và chọn hành động trả lời, hỏi lại, chuyển TA hoặc từ chối, để học viên nhận được hỗ trợ đúng mức mà không bị cung cấp thông tin thiếu căn cứ.
6. **Automation + willing users:** Conditional — case rõ phản hồi; case mơ hồ hỏi lại; logistics thiếu nguồn chuyển TA vì cost-of-error cao.
   **3 Willing users (có tên cụ thể đồng ý thử prototype):**
   - Nguyễn Văn An (HV-012, Zone A)
   - Trần Thị Bình (HV-045, Zone A)
   - Lê Hoàng Cường (HV-089, Zone B)
7. **Phân công nhóm D305:**
   - **Tùng:** AI integration (Model client & Streamlit prototype UI).
   - **Vũ:** Prompt & safety contract (System prompt & Output contract validator).
   - **Phong:** Golden set & evaluation (Golden set csv & eval runner).
   - **Hưng:** Evidence, impact & spec (Survey analysis, impact analysis & AI spec).
