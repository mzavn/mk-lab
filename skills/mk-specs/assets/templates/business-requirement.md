<!-- Dùng một trong hai cách, cả repo theo một cách:
     (a) một file `specs/business-requirements.md`, mỗi BR là một mục `## BR-XX: …` (heading cấp 2, mục con cấp 3);
     (b) mỗi BR một file `specs/business-requirements/BR-XX-<slug>.md` (heading cấp 1, mục con cấp 2).
     Mẫu dưới theo cách (b). -->
# BR-XX: <Tên yêu cầu nghiệp vụ>
- Status: draft | approved | in-progress | done
- Owner: <người chịu trách nhiệm nghiệp vụ>
- Stakeholders: <ai chịu hậu quả>
- Target: <mốc thời gian nếu có>

## Background
<Vì sao có yêu cầu này: bối cảnh, phản hồi người dùng, quy định.>

## Personas
<Người dùng chính, 1–3 nhóm, mã P1, P2… vĩnh viễn; UC ghi `- Actor: P1 (<vai>)`. Ô chưa biết ghi `[OPEN]`.>

### P1 — <vai>
- Vai và số lượng: <ai, bao nhiêu người>
- Bối cảnh dùng: <lúc nào, ở đâu, thiết bị>
- Đang làm việc này bằng gì: <công cụ/cách hiện tại; có còn chạy song song không>
- Nỗi đau: <cụ thể, có ví dụ>
- Mức quen công nghệ: <thấp | vừa | cao — dấu hiệu>
- Thành công với họ là: <việc gì xong trong bao lâu>
- Không chấp nhận: <…>

## Goal
<Một câu đo được. Tránh "tối ưu", "cải thiện" khi chưa có số.>

## Success Metrics
- <chỉ số>: từ X → Y, đo bằng <công cụ>, mốc <thời điểm>

## In Scope
- <làm>

## Out of Scope
- <cố ý không làm — ghi rõ để chặn phình phạm vi>

## Related Use Cases
- UC-XXX: <tên>

## Constraints
- Technical: <…>
- Regulatory: <…>
- Timeline: <…>

## Open Questions
- [OPEN] <câu hỏi phía nghiệp vụ chưa trả lời>

## History
- v1 (YYYY-MM-DD, chưa commit): khởi tạo
