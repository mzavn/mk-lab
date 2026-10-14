# PRD — <Tên app>
- Mức: 1 (PRD) | 2 (+ wireframe) | 3 (+ TDD)
- Status: draft | ready
- Owner: <người quyết phạm vi>
- Cập nhật: YYYY-MM-DD
- Kèm theo: [wireframe](wireframe.html) · [TDD](TDD.md) <bỏ phần chưa có>

> <Một câu: app làm gì, cho ai.>
>
> **Khi code theo file này:** chọn story `Todo` đầu tiên ở §7 mà phụ thuộc đã `Done`, bỏ qua story `Blocked` → đổi `Status: In Progress` → code đúng "Done khi", không thêm điều PRD không nói; dòng gắn `[OPEN]` là giá trị tạm, giữ dễ đổi → đổi `Status` (Done, hoặc Partial + ghi phần thiếu) → commit `feat(<mã story>): …`. Mỗi lần đổi `Status`, đổi ở cả §2 và §7. PRD không trả lời được → hỏi chủ dự án, sửa PRD trước rồi mới code.

## 1. Vì sao
- Vấn đề: <vấn đề cụ thể, ai đang khổ vì nó>
- Giải pháp: <app giải quyết thế nào, một hai câu>
- Người dùng chính: P1, P2 (chi tiết ngay dưới)
- Nền tảng: Web | Mobile | Cả hai
- Thành công khi: <số đo + mốc, vd "tuần 1: 10 người dùng tạo ≥ 1 đơn">
- Ngoài phạm vi: <điều chắc chắn KHÔNG làm ở bản này>
- Giới hạn: <thời hạn, ngân sách, số người>
- Giả định: <điều đang coi là đúng mà chưa kiểm; ô chân dung người dùng để "tuỳ bạn" cũng ghi ở đây>

### Chân dung người dùng (Personas)
<1–3 nhóm, mỗi nhóm một mã P1, P2, P3 vĩnh viễn. Ô người dùng chưa nói: `(chưa nói)`. Bỏ nhóm: ghi "(bỏ: lý do)", không dùng lại mã.>

#### P1 — <vai, vd chủ tiệm>
- Vai và số lượng: <ai, bao nhiêu người>
- Bối cảnh dùng: <lúc nào, ở đâu, thiết bị gì>
- Đang làm việc này bằng gì: <Zalo, giấy, Excel, gọi điện… — đường cũ có còn chạy song song không>
- Nỗi đau: <cụ thể, có ví dụ, bao lâu một lần>
- Mức quen công nghệ: <thấp | vừa | cao — dấu hiệu, vd "chỉ dùng Zalo">
- Thành công với họ là: <việc gì xong trong bao lâu>
- Không chấp nhận: <vd không cài app, không nhớ mật khẩu, không nhập quá 3 ô>

### Suy ra từ chân dung
| Ô chân dung | Hệ quả cho sản phẩm | Ở đâu trong PRD |
|---|---|---|
| <P1 · Mức quen công nghệ: thấp> | <tối đa 3 bước, chữ to, không cần đăng nhập> | <story ORD-01, §5> |

## 2. Tính năng và story

### [<MÃ>] <Tên tính năng>

#### [<MÃ>-01] Là P1 (<vai>), tôi muốn <làm gì>, để <lý do>
- Ưu tiên: Must | Should | Could
- Status: Todo | Blocked ([OPEN] Ox) | In Progress | Partial | Done | Dropped
- Phụ thuộc: <mã story phải xong trước, hoặc —>
- Done khi:
  - Given <dữ liệu cụ thể> When <hành động> Then <kết quả đo được> <thêm `[OPEN] Ox` nếu giá trị chưa chốt>
  - Given … When … Then …
  - KHÔNG: <điều story này cố ý không làm>

### Để sau
- <tính năng> — <một dòng> (Could / Won't lần này)

## 3. Tình huống lỗi và biên
| Tình huống | Hành vi mong muốn | Story |
|---|---|---|
| <nhập sai, mất mạng, hết phiên, dịch vụ ngoài lỗi…> | <người dùng thấy gì, dữ liệu ra sao> | <mã> |

## 4. Dữ liệu chính
- <Tên nghiệp vụ>: <nghĩa; trạng thái; quan hệ; luật giá trị quan trọng>

## 5. Giao diện
<Mức 1: bỏ mục này hoặc chỉ liệt kê màn hình.>
- Màn chính: <tên> → [wireframe.html](wireframe.html)
- Màn khác: <tên — story liên quan>

## 6. Kỹ thuật
<Mức 1–2: stack một dòng mỗi lớp + lý do. Mức 3: một dòng trỏ [TDD.md](TDD.md).>

## 7. Thứ tự làm
| # | Story | Phụ thuộc | Status |
|---|---|---|---|
| 1 | [<MÃ>-01] <tên ngắn> | — | Todo |

## Câu hỏi mở
- [OPEN] O1: <câu hỏi> — <ai cần trả lời> · chặn: <mã story hoặc —>

## Tự soát
- Ngày: YYYY-MM-DD · script: không chạy (mức 1–3) | audit.py/verify.py: <kết quả>
- Đã tự sửa: <mỗi ý một cụm ngắn, hoặc —>
- Đã hỏi (N câu): <câu hỏi ngắn> → <lựa chọn, ai trả lời | chưa trả lời (Ox)>
- Còn mở: <O…, hoặc —>

## History
- v1 (YYYY-MM-DD): khởi tạo, mức <n>
