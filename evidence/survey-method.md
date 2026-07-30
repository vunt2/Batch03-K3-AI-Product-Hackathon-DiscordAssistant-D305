# Phương pháp Khảo sát Nỗi đau Học viên & TA (Survey Methodology)

## 1. Thông tin Khảo sát Tổng quan

- **Thời điểm khảo sát:** Ngày 1 Mini Hackathon AI (Khóa AI Thực Chiến).
- **Phương pháp lấy mẫu:** Mẫu thuận tiện (Convenience Sampling) từ học viên và trợ giảng đang tham gia trực tiếp tại zone lớp học và trên kênh Discord chính thức.
- **Quy mô mẫu:** Tổng số $N = 20$ người tham gia khảo sát.
- **Cấu trúc đối tượng:**
  - **18 Học viên** ($90.0\%$) đang học trực tiếp.
  - **2 Trợ giảng / Lab Coach (TA)** ($10.0\%$) đang hỗ trợ lớp.

---

## 2. Danh sách Câu hỏi Xác minh Nỗi đau (Survey Questions)

Khảo sát sử dụng bộ câu hỏi trắc nghiệm và câu hỏi mở được thiết kế riêng cho 2 nhóm đối tượng:

### 2.1 Bộ câu hỏi dành cho Học viên ($n = 18$)
1. **Tần suất sử dụng Discord:** Bạn có sử dụng Discord hằng ngày để trao đổi bài học không? (`Có` / `Không`)
2. **Thời gian tìm kiếm thông tin:** Bạn có tốn ít nhất 1 phút để tìm kiếm thông tin logistics (deadline, link nộp bài, lịch học) trên Discord không? (`Có` / `Không`)
3. **Từ bỏ tìm kiếm:** Bạn đã từng từ bỏ tìm thông tin trên Discord vì mất quá nhiều thời gian chưa? (`Có` / `Không`)
4. **Kỳ vọng phản hồi AI:** Bạn có muốn trợ lý AI trả lời ngay lập tức các thắc mắc chuyên môn / bài học không? (`Có` / `Không`)
5. **Ủy quyền an toàn (Handoff):** Bạn có đồng ý để AI chuyển câu hỏi cho TA khi AI không chắc chắn thông tin không? (`Có` / `Không`)
6. **Chủ động hỗ trợ khi bị Stuck:** Bạn có muốn AI chủ động gợi ý hỗ trợ khi phát hiện bạn bị tắc nghẽn (stuck) bài tập không? (`Có` / `Không`)
7. **Ưu tiên tính năng quan trọng nhất:** Tính năng nào bạn cảm thấy quan trọng nhất?
   - A. Giải đáp chuyên môn (Learning QA)
   - B. Quản lý / tóm tắt thông báo (Logistics/Notification management)
   - C. Tìm tài liệu học tập (Document search)
   - D. Nhắc deadline bài tập (Deadline reminders)
8. **Ý kiến mở:** Chia sẻ vướng mắc lớn nhất của bạn khi tương tác trên Discord khóa học.

### 2.2 Bộ câu hỏi dành cho TA / Lab Coach ($n = 2$)
1. **Khối lượng câu hỏi lặp lại:** Tỷ lệ câu hỏi logistics / lặp lại bạn phải trả lời hằng ngày trên Discord là bao nhiêu?
2. **Thách thức lớn nhất:** Vấn đề khó khăn nhất khi hỗ trợ học viên trên Discord là gì?

---

## 3. Quy tắc Xử lý Dữ liệu (Data Cleaning & Blank Rules)

1. **Xử lý câu trả lời trống:** Loại bỏ các bản ghi không hoàn thành tối thiểu 80% số câu hỏi bắt buộc. Các ô trả lời mở để trống được ghi nhận là "Không có ý kiến bổ sung".
2. **Quy tắc phân tách mẫu số:** Sử dụng nghiêm ngặt mẫu số $n = 18$ cho các chỉ số và tỷ lệ phần trăm liên quan đến trải nghiệm của học viên. Không dùng mẫu số tổng $N = 20$ cho các câu hỏi chỉ dành riêng cho học viên.

---

## 4. Hạn chế của Phương pháp & Biến số Bias (Limitations)

1. **Convenience Sampling Bias:** Mẫu được lấy thuận tiện từ những người sẵn sàng điền khảo sát trong giờ giải lao, có thể tập trung vào nhóm năng nổ hơn mức trung bình của lớp.
2. **Cỡ mẫu TA rất nhỏ ($n = 2$):** Do số lượng TA/Lab Coach có mặt tại zone lớp học có hạn ($2$ người), ý kiến nhóm TA chỉ mang tính định tính tham khảo, không đại diện cho toàn bộ đội ngũ trợ giảng.
