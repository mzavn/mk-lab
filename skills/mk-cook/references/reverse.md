# Mode `reverse` — xây ngược từ UI ra proposal

Người dùng đã dựng giao diện trước (vibe, prototype) và muốn khoá lại thành spec. Kết quả là **một proposal nháp** để người dùng duyệt — không sửa UC/ADR chính, không sửa code. Sau khi duyệt, đi như mọi proposal: mk-cook viết test bảo vệ hành vi đó (`apply`), mk-specs hợp nhất.

## 0. Điều kiện

Chỉ cho repo mk-specs mức 4 đã khởi tạo: có `specs/mk-specs.yml` **và** `specs/README.md` (bảng context, dải mã UC). Thiếu một trong hai, hoặc chỉ có `specs/PRD.md` → không tạo file nào; gợi ý: chưa cài mk-specs → `bash ~/.mk-lab/install.sh --project .`; đã cài → nhờ mk-specs "khởi tạo SDD cho repo này" (`init`, nhánh brownfield `workflow-bootstrap.md` §3) hoặc `promote` từ PRD.

## 1. Thu thập

1. Chạy giao diện (dev server của repo) và mở trên trình duyệt; đi qua từng màn người dùng chỉ định.
2. Ghi lại thứ thấy được, không đoán ý đồ: màn, khối, field (nhãn, kiểu, bắt buộc, giá trị mặc định), nút và điều xảy ra khi bấm, mọi thông báo (lỗi, thành công, rỗng), điều hướng.
3. Đọc code của các màn đó để biết luật thật: kiểm hợp lệ, gọi API nào, điều kiện hiện/ẩn, quyền. Code và giao diện nói khác nhau → ghi `[DIVERGENCE]`, không chọn bên nào.

## 2. Chuyển thành spec

| Thấy ở UI/code | Thành | Ghi chú |
|---|---|---|
| Field của form/bảng | Thuộc tính trong `entities` (tên nghiệp vụ, nghĩa, ràng buộc) | Không ghi kiểu dữ liệu/cột DB ở phần nghiệp vụ |
| Một việc người dùng làm trọn (đăng ký, đặt hàng) | UC (đề xuất ID theo dải của context) | Actor lấy từ persona nếu BR có |
| Mỗi thông báo lỗi/thành công/rỗng thấy được | AC Given/When/Then với dữ liệu cụ thể | Câu chữ thông báo chép đúng như UI đang hiện |
| Lựa chọn kỹ thuật đáng nhớ (thư viện, cách lưu) | ADR nháp, có phương án bị loại | Chỉ khi có lựa chọn thật |
| Chỗ không biết vì sao, giá trị tự đặt (giới hạn, thời hạn) | `[OPEN]` hỏi chủ sản phẩm | Không biến giá trị hiện tại thành luật âm thầm |
| Giao diện (màu, chữ, khoảng cách) | `DESIGN.md` (mode `design`, cách B) | Không đưa vào AC |

## 3. Viết proposal nháp

- `specs/changes/<yyMMdd>-<slug>/proposal.md` theo mẫu proposal của mk-specs; `- Status: draft`; `## Vì sao` ghi "xây ngược từ UI đã có" và trích lời người dùng.
- `## Thay đổi spec`: UC mới với AC `ADDED`; entity; `[OPEN]`/`[DIVERGENCE]` liệt kê rõ.
- AC mô tả **hành vi đang có**; hành vi người dùng muốn đổi → ghi riêng thành câu hỏi, không trộn vào AC.
- > 5 AC → kèm `plan.md` (chỉ để test bảo vệ, code đã có).
- Chạy tự soát của mk-specs (`review.md`) trước khi đưa người dùng.

## 4. Bàn giao

Nói rõ: proposal ở đâu, bao nhiêu UC/AC, các `[OPEN]` cần người dùng trả lời, `[DIVERGENCE]` cần chọn. Bước tiếp theo: người dùng duyệt (và reviewer kỹ thuật) → `apply` viết test cho từng AC (thường xanh ngay vì hành vi đã có — test đỏ cho thấy UI và AC lệch, quay lại hỏi) → mk-specs `merge`.
