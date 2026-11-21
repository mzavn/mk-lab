# Mode `system` — luật trải nghiệm, mẫu, gu trong design system

Đọc khi dự án mới cần đặt nền trước khi dựng màn, hoặc muốn chuẩn hoá một loại khối cho cả dự án ("data table nào cũng phải có…"). Cấu trúc năm mục và vị trí trong `DESIGN.md`: `references/structure.md`. Ngưỡng và cú pháp `## Luật đo`: `references/standards.md`.

## 1. Thứ tự cố định

Mỗi bước dùng kết quả bước trước; không nhảy cóc. `DESIGN.md` đã có và người dùng chỉ muốn đổi một luật/mẫu → bỏ bảng này, đi thẳng §2–§5.

| # | Bước | Ra gì | Nguồn |
|---|---|---|---|
| 1 | Chọn nguyên lý nặng ký cho sản phẩm | 3–5 `NL-n` ưu tiên kèm lý do (vd khách vào bằng điện thoại một tay → NL-4, NL-11) | `references/principles.md` |
| 2 | Màn chính và việc chính của từng màn | bảng màn · đến để làm gì · hành động cuối | `references/needs.md` §việc chính |
| 3 | Mẫu chuẩn dùng trong dự án | danh sách mẫu + mặc định đổi riêng (vd số dòng mỗi trang 20) | `references/patterns-app-web.md`, `references/patterns-web.md`, `references/surfaces.md` |
| 4 | Nguyên tố một lần cho cả bộ + bảng trạng thái dùng chung | nút, ô nhập, thẻ, dòng danh sách, lớp nổi, trạng thái rỗng; rỗng/đang tải/lỗi/khoá/đang gửi/thành công | `references/structure.md` |
| 5 | Token | màu, chữ, khoảng cách — **mk-cook mode `design`**; chưa cài mk-cook → để `[điền: token — cài mk-cook]`, mk-ux không tự viết token | — |
| 6 | Năm mục mk-ux trong `DESIGN.md` | `## Luật trải nghiệm`, `## Mẫu`, `## Gu đã chốt`, `## Luật đo`, `## Bài học` | `references/structure.md` §DESIGN.md |

**Cổng (một lần):** `DESIGN.md` chưa có → không viết code màn nào trước khi người dùng duyệt bảng của bước 1–3 và mục `## Luật trải nghiệm`. Trình trong một tin, kết bằng "Đúng thì trả lời `ok`, sai dòng nào thì sửa dòng đó."

## 2. Ghi vào `DESIGN.md` đã có

- Chỉ thêm/sửa năm mục của mk-ux, đặt **sau** phần token; không đổi token, không đổi mục khác, kể cả khi thấy "sai".
- Trình bảng mã trước khi ghi: `| Mã | Mục | Trước | Sau | Lý do |` (mã `D1`, `D2`…). Chỉ áp mã được gọi tên. **Mục mới** = tiêu đề `##` chưa có trong `DESIGN.md`: luôn duyệt từng mã. `duyệt tất cả` chỉ áp các mã sửa dòng trong mục đã có; mã tạo mục mới thì giữ lại và hỏi lại đúng mã đó ("D1 tạo mục `## Mẫu` mới — duyệt D1 không?").
- `DESIGN.md` là tài liệu khác (kiến trúc, ghi chú) → hỏi, không ghi đè.
- Thấy token sai (chữ vàng trên trắng) → ghi thành phát hiện `audit`, đề xuất người dùng sửa token qua mk-cook.

## 3. `## Luật đo` — mặc định và đổi riêng

- Bắt đầu từ bảng mặc định (`references/standards.md`); chỉ ghi dòng **khác** mặc định hoặc dòng tắt (`tắt`) kèm lý do ở cột Luật.
- Mỗi dòng: `| <mã> | <luật bằng lời, phục vụ NL-n> | <ngưỡng> |`. Mã lạ bị bỏ qua kèm cảnh báo; ngưỡng sai dạng làm `score` thoát 2 — chạy `ux.py score … --design DESIGN.md` một lần trên dữ liệu đo bất kỳ để kiểm cú pháp.
- **Trước khi đề xuất đổi ngưỡng**, có dữ liệu đo gần nhất → chạy `score` với ngưỡng mới trên bản chép `DESIGN.md` trong thư mục tạm, ghi vào bảng mã số phần tử và lượt đổi trạng thái ("chữ đọc 17px: thêm 31 phần tử trượt ở 320, 390"), để người dùng quyết có cái giá đó.
- Ngưỡng mới lệch với token (vd `## Luật đo` 17px mà token chữ đọc 16px) → nói rõ khi trình mã và đề xuất người dùng sửa token qua mk-cook; mk-ux không tự sửa token.
- Ngưỡng là số hình thức: không đưa vào AC (ADR-31).

## 4. `## Mẫu` — mặc định riêng của dự án

- Mỗi mẫu dự án dùng một dòng theo khuôn của `references/structure.md` (§`## Mẫu`): `| <mẫu> | <dùng ở> | <lệch khỏi mẫu> | <lý do> |`, vd `| data-table | Học viên | số dòng mặc định 20; bỏ cột phụ dưới 390px | danh sách dài, tư vấn lướt nhanh |`.
- Phần "Hỏi chủ sản phẩm" của mẫu (điền sẵn dữ liệu cá nhân, chống bot bằng dịch vụ ngoài, che giao diện trình phát bên thứ ba) chỉ ghi khi chủ sản phẩm đã trả lời, kèm ngày.

## 5. `## Gu đã chốt`

- Một dòng mỗi quyết định: `| <quyết định> | <ngày> | <lý lẽ đã bị bác> |`. Lý lẽ bị bác giúp agent sau không đề xuất lại.
- Chỉ ghi điều chủ sản phẩm đã nói rõ; agent không tự suy gu. Gu không bao giờ vào `## Luật đo`.

## 6. Dữ liệu chạy thử

Dựng hay soi đều dùng dữ liệu giả **khó** (tên dài có dấu, số tiền lớn, danh sách rỗng, một trang, ngày `dd/mm/yyyy`): bộ mẫu ở `references/needs.md` §dữ liệu khó.
