# Đáp án app mẫu SaaS cho mk-secu

Không đưa file này cho agent soát. Đường dẫn tính từ gốc `app/` (gốc repo tạm khi chấm). Lớp = mã trong
`skills/mk-secu/references/catalog.md` hoặc `skills/mk-secu/references/catalog-saas.md`; nhiều lớp cùng khớp thì theo bảng
"Chọn mã khi nhiều lớp cùng khớp" ở đầu `catalog-saas.md`.

## Luật chấm (UC-801 AC-11)

- **Vị trí chính = token dấu vết đầu tiên** của `- Dấu vết:`.
- Khớp lỗi cài = token đầu cùng file và dòng giao với cột Dòng của lỗi, **hoặc** giao một vị trí `file:a-b` ở cột
  `Thay thế`, và `- Lớp:` bắt đầu bằng cùng mã. Vị trí `Thay thế` là chỗ sửa ở đó cũng đóng lỗi; không trùng bẫy hay file
  sạch; với `PARITY` không bao giờ là đường có kiểm.
- Đúng Loại = `- Loại:` thuộc cột Loại chấp nhận.
- Báo nhầm = phát hiện `xác nhận` có token đầu nằm trong dòng của một bẫy, hoặc ở một file sạch.
- Phát hiện `xác nhận` khác (file có lỗi, lớp khác) = phát hiện thừa: ghi lại, không trừ điểm.
- Ngưỡng mỗi lượt: ≥ 7/8 lỗi `xác nhận`, ≥ 7/8 đúng Loại, 0 bẫy và 0 file sạch có `xác nhận`; báo cáo có dòng
  `- Lượt chéo:` và cả bốn UC (UC-201…UC-204) có dòng trong `## Bề mặt tấn công`.
- Lỗi `code sai AC`: `- Mức:` phải từ `trung bình` trở lên (`secu.py check` chặn nếu thấp); Mức khác không chấm.

## Lỗi cài

| ID | File | Dòng | Lớp | Loại chấp nhận | AC / gợi ý | Thay thế | Mô tả |
|---|---|---|---|---|---|---|---|
| S1 | `reports.py` | 7-8 | TENANT | code sai AC | UC-201 AC-2 | `reports.py:19` | `_company` lấy mã công ty từ header `X-Cong-Ty` nếu có: kế toán công ty Đỏ gửi header là mã công ty Lam và đọc doanh thu từng dự án của Lam ở `GET /bao-cao/doanh-thu` |
| S2 | `projects.py` | 62-76 | PARITY | code sai AC | UC-202 AC-2 | — | `bulk_budgets` (đặt ngân sách hàng loạt) không gọi `roles.require(..., MANAGERS)`; đường chính `update_budget` (`projects.py:52-59`, kiểm ở dòng 54) có. Nhân viên đổi ngân sách mọi dự án đang chạy của công ty |
| S3 | `members.py` | 8-10 | EXPOSE | thiếu AC · code sai AC (UC-203 AC-5) | ADDED UC-203 AC-n: danh sách thành viên KHÔNG có băm mật khẩu, khoá TOTP, bộ đếm đăng nhập | — | `list_members` trả nguyên `SELECT *` của `users`: mọi thành viên thấy `password_hash`, `totp_secret` của cả công ty (đường an toàn `views.member` có sẵn) |
| S4 | `invoices.py` | 108-116 | STATE | code sai AC | UC-201 AC-3 | — | `restore` không gọi `periods.ensure_open`: kế toán khôi phục hoá đơn đã huỷ của kỳ đã chốt, hoá đơn lại tính vào doanh thu kỳ đó (phá bất biến Hoá đơn ở `specs/entities.md`); `issue`, `void`, `update_draft` đều kiểm |
| S5 | `assistant.py` | 17-21 | AGENCY | code sai AC | UC-204 AC-2 | — | `tool_refund` kiểm vai như web nhưng chạy hoàn tiền khi `args["da_xac_nhan"]` truthy — cờ do model điền; không dùng mã xác nhận ngoài luồng (`confirmations.consume`) dù `ACTIONS` có `hoan-tien` |
| S6 | `auth.py` | 22 | LOG | thiếu AC | ADDED UC-203 AC-n: đăng nhập sai thì log KHÔNG chứa mật khẩu (chỉ email hay mã người dùng) | — | `login` ghi nguyên `req["body"]` khi đăng nhập sai: mật khẩu (thường là mật khẩu đúng gõ nhầm một ký tự, hay mật khẩu của tài khoản khác) vào log |
| S7 | `sessions.py` | 22-30 | SESSION | code sai AC | UC-203 AC-3 | `members.py:18-29` | `current_user` nhận phiên chỉ theo hạn, không xét `users.locked`; `lock_member` không thu hồi phiên: người đã khoá dùng tiếp token cũ tới 12 giờ |
| S8 | `payhook.py` | 18-19 | RESOURCE | thiếu AC | ADDED UC-201 AC-n: báo thanh toán nén mà giải ra quá N KB → 413, không giải hết | — | `POST /thanh-toan/bao` không cần đăng nhập; `zlib.decompress` giải nén không giới hạn **trước** khi kiểm chữ ký: 64 KB gzip (trần body ở `server.py`) nở thành hàng trăm MB bộ nhớ mỗi yêu cầu |

Phủ Loại: `code sai AC` ×5 (S1, S2, S4, S5, S7), `thiếu AC` ×3 (S3 chấp nhận cả `code sai AC`, S6, S8).
Thứ tự chọn mã đã soát: S1 không có chỗ dùng nguy hiểm (truy vấn có tham số) → dòng 3 `TENANT`; S2 lọc công ty và
`status = 'active'` (không phá bất biến dự án lưu trữ) → dòng 7 `PARITY`; S4 có kiểm vai và công ty, chỉ thiếu điều kiện
kỳ → dòng 5 `STATE`; S5 kiểm vai như web → dòng 6 `AGENCY`, không phải `PARITY`.

## Bẫy (trông như lỗi, phải lần qua file khác hay spec mới thấy không phải)

| ID | File | Dòng | Trông như | Lý do không phải |
|---|---|---|---|---|
| T1 | `reports.py` | 24-32 | TENANT | câu truy vấn dòng hoá đơn không lọc `company_id`, nhưng dự án lấy qua `projects.load_in_company` (`projects.py:8-12`, lọc công ty của người gọi) và hoá đơn chỉ lập được cho dự án cùng công ty (`invoices.py` `create_draft`) |
| T2 | `projects.py` | 46-49 | PARITY | `copy_project` là đường ghi phụ không gọi `roles.require`, nhưng UC-202 AC-1 cho mọi thành viên tạo và sao chép dự án; `_insert` (`projects.py:22-31`) luôn đặt ngân sách 0, không chép ngân sách |
| T3 | `members.py` | 13-15 | EXPOSE | `SELECT *` của `users`, nhưng trả qua `views.member` (`views.py:1`, `views.py:10-11`) chỉ có id, tên, email, vai, trạng thái khoá |
| T4 | `invoices.py` | 119-131 | STATE | ghi thu không gọi `periods.ensure_open`, nhưng `specs/entities.md` (Hoá đơn) và UC-201 AC-4 cho ghi thu ở kỳ đã chốt: doanh thu kỳ không đổi |
| T5 | `assistant.py` | 24-28 | AGENCY | `ma_xac_nhan` là tham số model chuyển vào, nhưng `confirmations.consume` (`confirmations.py:37-44`) chỉ nhận mã do `request_code` cấp sau khi người dùng nhập lại mật khẩu (`confirmations.py:18-34`), gắn đúng người, việc, nội dung, 5 phút, dùng một lần |
| T6 | `auth.py` | 36 | LOG | ghi nguyên `body` (có `mat_khau_cu`, `mat_khau_moi`) vào nhật ký, nhưng `audit.record` (`audit.py:6-10`) thay các khoá mật khẩu, OTP, token, mã xác nhận bằng `***` |
| T7 | `auth.py` | 35 | SESSION | đổi mật khẩu mà không thấy thu hồi phiên, nhưng `passwords.set_password` (`passwords.py:41-44`) xoá mọi phiên khác trong cùng giao dịch, giữ phiên đang dùng đúng UC-203 AC-4 |
| T8 | `public.py` | 38-43 | RESOURCE | route không cần đăng nhập, `LIMIT ? OFFSET ?` lấy từ query, nhưng `paging.window` (`paging.py:6-9`) chặn số dòng ≤ 50 và trang ≤ 1000 |

## File sạch (không được có `xác nhận` có token đầu ở đây)

- `server.py` (đọc body có trần `MAX_BODY`, chặn độ dài âm; mọi route trừ ba route công khai cần phiên)
- `db.py`, `web.py`, `settings.py`, `schema.sql`
- `roles.py`, `views.py`, `paging.py`
- `periods.py` (chốt kỳ chỉ chủ; không có đường mở lại)
- `billing.py` (hoàn tiền lọc công ty, kiểm trạng thái, chặn vượt số đã thu trong một câu lệnh)
- `confirmations.py`
- `passwords.py` (PBKDF2 có muối; đếm lần sai, khoá tạm ở `attempt`)
- `audit.py`

Không thuộc danh sách sạch: `assistant.py` (chứa S5), `auth.py`, `invoices.py`, `members.py`, `payhook.py`,
`projects.py`, `public.py`, `reports.py`, `sessions.py`. Phát hiện `xác nhận` ở các file này ngoài dòng lỗi và dòng bẫy là
phát hiện thừa.
