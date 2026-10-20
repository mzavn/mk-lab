# Nguyên tắc SDD trong mk-specs

Nguồn: ebook *Spec Driven Development* của anh Huy (huynt.dev) và bài báo nghiên cứu *Spec-Driven Development for Agentic Software Engineering: Harnessing Human–Agent Teamwork* (Jessica Díaz, Joaquín Gayoso, Andrea Cimminio, Jorge Pérez — arXiv:2609.00252v1 [cs.SE], 2026, https://arxiv.org/html/2609.00252v1). Phần dưới là tổng hợp và diễn giải, có ghi trang sách (tr.) hoặc mục bài báo (§) để tra lại. mk-specs giữ thêm các cơ chế vận hành thực tế (đánh dấu ✚).

## 1. Triết lý

- Spec đứng giữa để người thống nhất *ý định*; AI viết code, test, tài liệu xoay quanh spec. Sai ở đâu thì **sửa spec trước, rồi mới sửa code** (tr.9).
- Điều gì không được viết ra thì với AI coi như không tồn tại. AI lấp chỗ trống bằng xác suất, không bằng hiểu biết nghiệp vụ (tr.7, 12).
- Test do AI tự sinh từ chính code nó viết chỉ chứng minh "code làm đúng cái code đang làm". Test phải đi từ AC (tr.8).
- Spec không cần hoàn hảo ngày đầu, chỉ cần đủ rõ để bắt đầu rồi lớn dần qua demo, test, bug (tr.9). Spec tốt là spec chịu được việc học thêm (tr.17).
- Không phải waterfall: spec là Markdown trong git, review như code, bản đầu 1–2 trang, sai thì sửa (tr.10–11).
- Lời AI giải thích "vì sao code thế này" chỉ là dựng lại từ code, không phải ý định ban đầu (tr.6).
- Ràng buộc không có công cụ nào kiểm được là một mong muốn chứ không phải ràng buộc (§5.5). Mọi ràng buộc phải đo được hoặc quy về Given/When/Then có test.
- Trôi dạt đặc tả (specification drift, §8.2) xảy ra khi code và spec dần xa rời nhau do sửa code không cập nhật spec; phòng ngừa bằng audit định kỳ và kiểm tra tự động trong CI.

## 2. Sáu nguyên tắc và câu hỏi kiểm

| # | Nguyên tắc | Làm thế nào trong mk-specs | Câu hỏi kiểm |
|---|---|---|---|
| 1 | **Requirements-Driven** — spec dẫn code (tr.23–24) | Khái niệm mới (trường, trạng thái, luồng, quyền, chính sách) vào spec trước hoặc cùng lúc; "spec đã cập nhật" nằm trong DoD; proposal được commit trước code | Thay đổi này có mục spec chưa? |
| 2 | **AI-Assisted** — AI làm phần lặp, người giữ quyết định (tr.24–25) | AI viết proposal, test theo AC, code, tài liệu; **người quyết** tiền, quyền truy cập, bảo mật, pháp lý, kiến trúc lớn | Đoạn nào AI đề xuất, đoạn nào người quyết? |
| 3 | **Iterative Improvement** — spec tốt lên mỗi vòng (tr.25–26) | Mỗi UC/BR có `## History`; AC lỗi thời đánh dấu deprecated, không xoá; quay lại sửa artifact trước là bình thường | Vòng phản hồi gần nhất dạy spec điều gì? |
| 4 | **Test-Protected** — test là hàng rào cho AI viết lại (tr.27–28) | Mỗi AC ≥ 1 test kiểm *hành vi*, không kiểm chi tiết cài đặt; test đầu tiên của một mẫu do người viết/review kỹ; trỏ test qua dòng `- Tests:` ✚ | Mỗi AC có test chưa? |
| 5 | **Stakeholder-Centric** — spec chỉ có giá trị khi người chịu hậu quả đã đọc (tr.28–29) | Duyệt hai phía: chủ sản phẩm duyệt nghiệp vụ, reviewer duyệt kỹ thuật; không ai tự duyệt | Ai phía nghiệp vụ đã đọc? |
| 6 | **Traceable** — từ code ra spec, từ spec ra test (tr.29–30) | ID UC/BR/ADR trong mọi commit subject; `traceability.md` sinh tự động + kiểm bằng máy ✚; History mang hash commit ✚ | Lỗi production thì tìm ra spec trong 1 phút không? |

Team mới thường đạt 2/6; đủ 6/6 mới gọi là trưởng thành, lộ trình khoảng 90 ngày (tr.31, 61–62).

## 3. Người quyết, AI đề xuất

- **AI hợp**: CRUD, mapping, boilerplate, đổi tên, sinh test theo AC có sẵn, viết tài liệu, nháp proposal, rà soát chéo (tr.25).
- **Người quyết**: luật tiền (hoàn tiền, hạn mức, phí, thuế), quyền truy cập dữ liệu, bảo mật, pháp lý, kiến trúc lõi. AI chỉ được nêu phương án + hệ quả, rồi dừng chờ (tr.25, 54).
- Khi AI đang làm mà gặp câu hỏi nghiệp vụ spec chưa nói: **không đoán**. Ghi `[OPEN]` hoặc đề xuất sửa spec, hỏi chủ sản phẩm, rồi mới làm tiếp (tr.39, 54).
- Review luôn hỏi "rule này đến từ spec nào?"; không trả lời được thì không merge (tr.25).
- Ghi lại AI đã làm gì trong commit body hoặc proposal ("AI usage") để biết nguồn gốc quyết định khi debug (tr.59, 75).
- **Thang tự chủ phân tầng** (Graduated autonomy, §5.10): mức tự chủ của agent được định rõ theo loại việc trong `AGENTS.md` (vá phụ thuộc/lỗi nhỏ: tự động hoàn toàn; tính năng thường: tự động + tham vấn khi mơ hồ; tiền/quyền/bảo mật: duyệt plan trước + review từng bước). Người chuyển từ viết từng dòng code sang điều phối (orchestration, §6.2), định chuẩn và thẩm định bằng chứng.

## 4. Nguồn sự thật và trọng tài ✚

| Nơi | Vai trò | Khi lệch |
|---|---|---|
| `specs/` | Hành vi đã chốt — chuẩn để review và viết test | — |
| `specs/changes/` | Đề xuất đang bàn | Chưa có hiệu lực tới khi hợp nhất |
| `docs/` (hoặc tương đương) | Ý định, nguyên lý | Mở `[DIVERGENCE]`, chủ sản phẩm quyết, rồi sửa bên sai |
| `plans/`, báo cáo | Lịch sử | Không sửa cho khớp |

Code lệch spec chỉ có hai khả năng: bug, hoặc spec chưa cập nhật. Không có trường hợp thứ ba.

### Ba lớp tài liệu phân biệt (§4.1) ✚

1. **System specification (Đặc tả hệ thống)**: Mô tả thế giới bền vững của dự án (kiến trúc, quy ước, mô hình thực thể, luật chuẩn mực). Luôn được nạp vào context của mọi phiên agent qua `AGENTS.md` / `CLAUDE.md`.
2. **Feature specification (Đặc tả tính năng)**: Mô tả thay đổi cụ thể đang làm (`specs/changes/`), có vòng đời ngắn (propose → apply → archive). Xong việc thì lưu trữ vĩnh viễn ở archive.
3. **Skill (Thủ tục theo nhu cầu)**: Hướng dẫn quy trình thực hiện ("làm X như thế nào", vd `SKILL.md`), chỉ nạp on-demand khi kích hoạt, không nạp thường trực để tránh ô nhiễm context window.

Trộn lẫn 3 lớp là lỗi phổ biến: đưa chi tiết tính năng tạm thời vào system spec gây phình context và cứng nhắc; ngược lại đưa luật toàn cục vào proposal khiến các phiên agent sau trôi dạt kiến trúc.

## 5. Khi nào dùng, khi nào không

**Nên dùng** (tr.64–65) khi có ít nhất một: hệ thống sống > 6 tháng; > 2 người cùng làm (tính cả AI agent thay phiên); có luật tiền, hợp đồng, pháp lý, quyền truy cập; có khả năng đổi người; AI sinh phần lớn code; đây là phần lõi sản phẩm. Quy tắc gọn: chi phí bảo trì + onboard về sau lớn hơn chi phí viết spec từ đầu.

**Không nên dùng** (tr.64):
- Prototype sống < 1 tuần, spike kỹ thuật, script chạy một lần.
- Side project một người, không ai khác phải hiểu — README ngắn là đủ.
- Tổ chức không có ai chịu trách nhiệm làm rõ nghiệp vụ: sửa chuyện ai làm chủ trước, SDD không thay được.
- Một phần repo: có thể chỉ áp dụng cho module nóng hoặc phần có luật tiền/pháp lý (tr.62).

## 6. Hiểu nhầm cần gỡ (tr.65–66)

| Hiểu nhầm | Thực tế |
|---|---|
| SDD là waterfall mới | Spec nhỏ, sửa liên tục, review như code |
| SDD làm chậm | Tuần đầu chậm hơn; từ tháng thứ ba ổn định hơn, onboard nhanh hơn |
| Chỉ cho doanh nghiệp lớn | Nhóm nhỏ, kể cả một người + AI, vẫn được lợi khi có luật tiền/quyền |
| Bắt buộc DDD + Hexagonal | Chỉ cần "DDD nhẹ": tên nghiệp vụ, context, entity; Hexagonal tuỳ chọn |
| AI giỏi thì không cần spec | AI càng nhanh, spec mơ hồ càng đưa sai hướng nhanh hơn (tr.66, 68) |

## 7. Chỉ số trưởng thành (tóm tắt, chi tiết ở traceability.md)

AC Coverage, Spec Coverage, Trace Ratio — đo, không đếm dòng spec hay số UC đóng mỗi tuần (tr.60–61). Tuần đầu chỉ cần theo dõi một chỉ số: tỉ lệ commit có ID (tr.63).
