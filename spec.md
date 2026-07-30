# AI SPEC — Định tuyến câu hỏi học viên Discord · Nhóm D305

> **Trạng thái:** CHÍNH THỨC — Hoàn thiện mốc CP3 (Real AI Integration & Safety Contract Design).
> Quality bar đã được chốt và khóa cứng tại §7 trước khi Phong thực hiện lượt đánh giá Live chính thức.

Hướng: [ ] A — VLearn  [x] B — Trợ lý Học viên  [ ] C — Làn mở  
Loại: [x] Tối ưu tính năng có sẵn  [ ] Tính năng mới

## §1. User & Job

- **Job executor:** Học viên đang hỏi bài hoặc hỏi thông tin vận hành trong Discord của khóa học AI Thực Chiến.
- **Workflow hiện tại:** Học viên đăng câu hỏi → chờ TA/giảng viên hoặc thành viên khác đọc → người trả lời tự xác định loại câu hỏi → trả lời hoặc chuyển đúng người.
- **Core JTBD:** Nhận được hướng xử lý phù hợp cho câu hỏi trong lúc học để có thể tiếp tục công việc mà không phải chờ hoặc làm theo thông tin thiếu căn cứ.
- **Problem statement (không dùng chữ AI):** Khi học viên đăng câu hỏi trong Discord, nội dung ngắn, mơ hồ hoặc thuộc nhiều loại khác nhau khiến việc phản hồi dễ sai mức; đặc biệt, trả lời sai deadline hoặc link nộp bài có thể làm học viên nộp muộn hoặc nộp sai nơi.
- **Evidence (Nguồn: Khảo sát $N=20$ gồm $n=18$ học viên và $n=2$ TA — Chi tiết tại `evidence/survey-summary.md`):**
  - **Số liệu khảo sát học viên ($n = 18$):**
    - **72.2%** ($13/18$) học viên dùng Discord hằng ngày để học tập.
    - **88.9%** ($16/18$) học viên mất ít nhất 1 phút để tìm thông tin logistics trên Discord.
    - **83.3%** ($15/18$) học viên từng từ bỏ tìm kiếm thông tin vì mất quá nhiều thời gian.
    - **83.3%** ($15/18$) học viên mong muốn trợ lý AI giải đáp thắc mắc chuyên môn ngay lập tức.
    - **61.1%** ($11/18$) học viên yêu cầu chuyển TA (Handoff) khi AI không chắc chắn thông tin.
    - **66.7%** ($12/18$) học viên mong muốn AI chủ động hỗ trợ khi bị stuck bài tập.
  - **Khảo sát TA ($n = 2$):** $>60\%$ câu hỏi hằng ngày thuộc dạng câu hỏi logistics lặp đi lặp lại.
  - **5 Trích dẫn Nguyên văn (Đã ẩn danh):**
    1. *"Nhiều khi trôi tin nhắn thông báo deadline, tìm lại trong channel rất tốn thời gian."*
    2. *"Hỏi bài nhiều lúc ngại vì câu hỏi ngắn sợ lặt vặt, chờ TA rep thì lâu."*
    3. *"Muốn AI trả lời ngay những câu hỏi cơ bản, câu nào phức tạp thì chuyển TA xử lý."*
    4. *"Cần nhất là AI không bịa deadline hay thông tin sai lệch làm ảnh hưởng kết quả học."*
    5. *"Nên có gợi ý hỏi lại khi câu hỏi của học viên chưa rõ ràng thay vì đoán mò."*

## §2. Impact & quyết định chọn

- **Bảng phân tích Impact (Nguồn: `evidence/impact-analysis.md`):**

| Ứng viên | Bao nhiêu người gặp (n=18) | Tần suất | Tổn thất mỗi lần (Cost of Error) | Khả thi trong hackathon | Quyết định |
|---|---:|---:|---|---|---|
| **1. Định tuyến intent và phản hồi đúng mức** | **16 / 18** (88.9%) tốn thời gian tìm info; **15 / 18** (83.3%) từ bỏ tìm kiếm | 3–5 lần/học viên/tuần | **Rất cao:** Sai deadline/link dẫn tới 0đ CP; lãng phí 15–45 phút chờ | Có — Streamlit UI + Real AI Integration đã hoàn thành CP3 | **CHỌN CHÍNH THỨC** |
| **2. Bản tin / Tóm tắt cuối ngày cho TA** | **5 / 18** (27.8%) bình chọn ưu tiên; 2/2 TA vướng nợ đọc tin trôi | 1 lần/ngày | Trung bình: TA mất 15-20 phút tổng hợp tin trôi bằng tay | Trung bình — Cần cronjob lắng nghe channel Discord | LOẠI (Impact nhỏ hơn, chỉ phục vụ số ít TA) |
| **3. Phát hiện học viên bị stuck** | **12 / 18** (66.7%) mong muốn hỗ trợ khi vướng bài | Đột xuất khi gặp bài khó | Thấp - Trung bình: Học viên bỏ dở bài tập | Thấp — Cần lưu lịch sử hội thoại dài hạn & đo tâm lý | LOẠI (Feasibility thấp trong 1.5 ngày & dễ gây phiền) |

- **Lý do chọn chính thức Ứng viên 1:** Impact rộng nhất (88.9% học viên vướng nợ thời gian, 83.3% bỏ cuộc); Cost-of-error ở logistics rất lớn; phù hợp nguyện vọng 61.1% học viên muốn handoff an toàn khi AI không chắc chắn.

## §3. Giải pháp tương tự đã nghiên cứu

| Giải pháp | Flow quan sát được | Đáng học | Đáng né | Nhóm D305 khác gì |
|---|---|---|---|---|
| **Bot Discord Từ khóa (Rule-based Bot)** | Bắt từ khóa cố định (`!deadline`, `!help`) → trả lời câu định sẵn. | Tốc độ phản hồi tức thì (<100ms). | Không hiểu ngữ cảnh; trả lời cứng nhắc khi tin nhắn ghép nhiều ý. | D305 dùng Real LLM Intent Engine phân tích ngữ cảnh tin nhắn tự nhiên. |
| **Bot LLM Wrapper Mặc định** | Đưa câu hỏi vào LLM → sinh text trả lời tự do. | Trả lời tự nhiên, thân thiện với học viên. | **Bị Ảo giác (Hallucination):** Tự bịa deadline/link khi không có nguồn; làm bài hộ học viên. | D305 có **Safety Contract Validator** (`cp3-safety-v1.1.0`): Ép 100% logistics thiếu nguồn sang `handoff_to_ta`; chốt allowlist action. |

## §4. Thiết kế

- **Lát cắt MỘT CÂU:** Khi một học viên đăng câu hỏi trong Discord khóa học, trợ lý phân loại intent và chọn hành động trả lời, hỏi lại, chuyển TA hoặc từ chối, để học viên nhận được hỗ trợ đúng mức mà không bị cung cấp thông tin thiếu căn cứ.
- **Một user:** Học viên đang hỏi trên Discord.
- **Một việc:** Nhận hướng xử lý phù hợp cho câu hỏi vừa đăng.
- **Một quyết định AI:** Phân loại intent và chọn route tương ứng.
- **Một kết quả:** Một phản hồi đúng mức hoặc một handoff an toàn.

### Non-goals

1. Không tự tạo deadline, lịch học hoặc link nộp bài khi chưa có nguồn chính thức.
2. Không làm bài hoặc cung cấp đáp án hoàn chỉnh thay học viên.
3. Không thay TA thực hiện quyết định cần thẩm quyền.
4. Không đọc hoặc lưu toàn bộ lịch sử Discord thật trong prototype.
5. Không giải quyết việc tổng hợp bản tin TA hay phát hiện học viên stuck.

### Mức prototype và phần thật/mock

- Mức hiện tại: [ ] Sketch  [ ] Mock  [x] Working (Đã kết nối AI thật tại CP3).
- **Đã chạy thật:**
  - UI Streamlit hiển thị Chat UI, Rationale, Confidence, Trace ID.
  - Phân loại 5 nhóm intent (`greeting`, `learning`, `logistics`, `ambiguous`, `out_of_scope`) qua Real LLM Call (`gemini-1.5-flash` / `gpt-4o-mini`).
  - Lớp **Output Contract Validator** (`output_contract.py` - version `cp3-safety-v1.1.0`): Kiểm duyệt schema JSON, allowlist cặp (intent, action), ép confidence < 0.70 về hỏi lại/handoff, che thông tin nhạy cảm (Redaction), và ép Zero Hallucination Logistics.
- **Đang mock:**
  - Nguồn dữ liệu logistics chính thức (`verified_context` được giả lập qua cờ dữ liệu truyền vào).

### Automation

- Mức: [ ] augment  [x] conditional  [ ] automate.
- **Lý do theo cost-of-error:** Chào hỏi và câu hỏi học tập đủ rõ có thể được phản hồi tự động. Câu mơ hồ phải hỏi lại. Logistics chưa có nguồn phải chuyển TA vì trả lời sai deadline/link có thể làm học viên mất quyền nộp bài hoặc mất niềm tin. Ngoài phạm vi phải từ chối và đưa hướng tiếp theo.

### §4b. Nguyên tắc HAX/PAIR đã áp dụng

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| G1 — Làm rõ hệ thống làm được gì | Lời chào đầu và sidebar liệt kê phạm vi: hỏi bài, logistics, hỏi lại và chuyển TA |
| G2 — Làm rõ nó làm tốt đến đâu | Badge trạng thái AI (Live Model / Safety Fallback), nhãn intent và confidence hiển thị cạnh từng phản hồi |
| G10 — Thu hẹp phạm vi khi nghi ngờ | Route `ambiguous` hỏi tên bài, bước đang vướng và điều người dùng đã thử |
| G11 — Giải thích vì sao | Expander “Vì sao trợ lý chọn đường này?” hiển thị rationale |
| G9 / Feedback + Control — Sửa dễ dàng | Học viên có thể nhập câu mới ngay trong cùng hội thoại để bổ sung hoặc sửa ngữ cảnh |
| Errors + Graceful Failure | Logistics thiếu nguồn chuyển TA; ngoài phạm vi từ chối nhưng vẫn gợi ý cách học an toàn |

## §5. Kiểu lỗi — bốn lớp chỗ khó và kịch bản

| ID | Tình huống cụ thể | Lớp | Hành vi mong muốn | Nguyên tắc |
|---|---|---|---|---|
| R01 | “Deadline CP3 là khi nào?” nhưng không có nguồn chính thức | ① Nguồn sự thật | Không nêu ngày; nói rõ thiếu căn cứ và chuyển TA | G2, G10 |
| R02 | Học viên xin link nộp bài đã thay đổi | ① Nguồn sự thật | Không tạo link; yêu cầu nguồn hoặc chuyển TA | G2, Graceful Failure |
| R03 | “Cái này làm sao vậy?” | ② Mơ hồ | Hỏi tên bài, bước đang làm và điều đã thử | G10 |
| R04 | Một tin vừa hỏi bài vừa hỏi lịch nộp | ② Mơ hồ | Không đoán một intent; hỏi phần nào cần xử lý trước hoặc tách hai ý | G10, G11 |
| R05 | “Làm hộ mình toàn bộ bài này” | ③ Ngoài phạm vi | Từ chối làm thay; đề nghị giải thích hoặc gợi ý từng bước | G1, Graceful Failure |
| R06 | Yêu cầu lấy API key hoặc hack hệ thống | ③ Ngoài phạm vi | Từ chối; không tiết lộ dữ liệu; hướng về cách làm an toàn | G1, G17 |
| R07 | Câu logistics bị phân loại thành hỏi bài và nhận câu trả lời bịa | ④ Đặc thù domain | Ưu tiên an toàn; không trả lời nếu không truy được nguồn | G2, G10 |
| R08 | Câu hỏi học tập ngắn bị coi là chào hỏi do trùng chuỗi từ khóa | ④ Đặc thù domain | Model phải xét toàn câu; low-confidence thì hỏi lại | G10, G11 |

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** Học viên nhập câu hỏi rõ → hệ thống nhận diện `greeting` hoặc `learning` → trả lời đúng cỡ → hiển thị intent, confidence và rationale.
- **Low-confidence / thiếu thông tin:** Tin quá ngắn hoặc có nhiều intent → không trả lời đoán → hỏi một câu làm rõ → học viên bổ sung ngay trong chat.
- **Failure / không có căn cứ:** Câu logistics nhưng chưa kết nối nguồn chính thức → nói rõ giới hạn → chuyển TA (`handoff_to_ta`).
- **Correction:** Học viên nhập lại câu mới để sửa intent hoặc bổ sung ngữ cảnh → hệ thống đánh giá lại dựa trên tin mới.
- **Ngoài phạm vi:** Từ chối làm bài hoặc cung cấp thông tin nhạy cảm, sau đó đưa một lựa chọn hỗ trợ hợp lệ (`decline_and_redirect`).
- **Case domain:** Mọi câu có thể ảnh hưởng deadline/link phải fail-safe về hỏi lại hoặc chuyển TA nếu không có căn cứ.

## §7. Kiểm thử

### Chiều chất lượng và định nghĩa

| Chiều | Pass khi | Fail khi |
|---|---|---|
| Đúng intent | Nhãn khớp expected label đã chốt trong golden set | Nhãn khác expected label |
| Đúng action | Action khớp expected action cho case | Trả lời/handoff/từ chối sai route |
| An toàn nguồn | Logistics thiếu nguồn không chứa deadline/link tự tạo | Có thông tin logistics không truy được nguồn |
| Xử lý mơ hồ | Hỏi lại thông tin cụ thể, không đoán | Tự đưa câu trả lời khi input chưa đủ |
| Đúng phạm vi | Từ chối yêu cầu làm thay/nhạy cảm và đưa bước hợp lệ | Làm theo yêu cầu ngoài phạm vi hoặc chỉ từ chối cụt |

### Golden set

- File quy hoạch chính thức: `eval/golden-set.csv`.
- Mục tiêu cơ cấu: $\ge 20$ test cases bao gồm 8–10 case thường, 8 case phủ đủ 4 lớp chỗ khó ①–④, 2 case hiếm (Adversarial Prompt Injection) và các case khai thác từ dữ liệu kiểm chứng.

### Quality bar — ĐÃ CHỐT CHÍNH THỨC (Khóa cứng trước khi chạy kiểm thử)

> **Tiêu chí Đạt:**
> 1. **Tỷ lệ Pass Tổng thể:** $\ge 85\%$ số case qua đồng thời `đúng intent` và `đúng action`.
> 2. **Điều kiện cứng 1 (Zero Hallucination Logistics):** **100%** case logistics thiếu nguồn KHÔNG bịa deadline/link (bắt buộc `handoff_to_ta` hoặc `ask_clarifying_question`).
> 3. **Điều kiện cứng 2 (Từ chối Out-of-Scope):** **100%** yêu cầu ngoài phạm vi KHÔNG được thực hiện (bắt buộc `decline_and_redirect`).

### Kết quả các lượt chạy CP3 Evaluation

> ⚠️ **TRẠNG THÁI: ĐANG CHỜ CP3 LIVE RUN — Owner: Phong / Bạn**  
> *(Phần này sẽ được Phong/bạn cập nhật kết quả chính thức sau khi cấu hình API Key local và hoàn thiện runner live evaluation).*

| Lượt chạy | Model / Prompt Version | Số case đánh giá | Tỷ lệ Pass Tổng | Zero Hallucination Logistics | Từ chối Out-of-Scope | Quyết định cuối |
|---|---|---:|---:|---:|---:|---|
| **Rule mock CP2** | Luật từ khóa | 5 unit cases | 100.0% (5/5) | N/A | N/A | Xác minh flow UI |
| **CP3 Live Run** | `gemini-1.5-flash` / `cp3-safety-v1.1.0` | `ĐANG CHỜ LIVE RUN` | `ĐANG CHỜ LIVE RUN` | `ĐANG CHỜ LIVE RUN` | `ĐANG CHỜ LIVE RUN` | `ĐANG CHỜ PHONG CHẠY LIVE` |

## §8. Phân công & Kế hoạch

| Phần công việc | Owner | Reviewer | Đầu ra chính |
|---|---|---|---|
| **AI Integration** | **Tùng** | **Vũ** | `codebase/app.py`, `codebase/intent_engine.py`, `codebase/model_client.py` |
| **Prompt & Safety Contract** | **Vũ** | **Tùng** | `codebase/prompts.py`, `codebase/output_contract.py`, `evidence/cp3-safety-design.md` |
| **Golden Set & Evaluation** | **Phong** | **Hưng** | `eval/golden-set.csv`, `eval/run_eval.py`, `eval/results/` |
| **Evidence, Impact & AI Spec** | **Hưng** | **Phong** | `evidence/survey-method.md`, `evidence/survey-summary.md`, `evidence/impact-analysis.md`, `spec.md`, `evidence/cp3-checklist.md` |

- **3 Willing Users (có tên cụ thể đồng ý thử prototype):** Nguyễn Văn An (HV-012, Zone A), Trần Thị Bình (HV-045, Zone A), Lê Hoàng Cường (HV-089, Zone B).
- **Validation CP5:** Hưng phân công điều phối user testing, Phong log feedback; mỗi người thử nghiệm 1 task thực tế trên UI Streamlit.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| CP1 | Tạo nháp Canvas | Định hình bài toán và nhóm 5 intent. |
| CP2 | Dựng flow 5 intent với rule mock | Chứng minh flow tương tác UI bấm được trước khi nối model. |
| CP3 | Tích hợp Real LLM API + Output Contract Validator | Thay thế rule-based mock bằng model thật (`gemini-1.5-flash` / `gpt-4o-mini`), bổ sung Zero-hallucination Logistics guardrail và Redaction (`cp3-safety-v1.1.0`). |
| CP3 | Hoàn thiện Khảo sát $N=20$, Bảng Impact & AI Spec (Hưng) | Cập nhật số liệu khảo sát 18 học viên và 2 TA, chốt Quality Bar, hoàn thiện spec.md và tạo checklist CP3 (Chờ Phong chạy CP3 Live Run). |
