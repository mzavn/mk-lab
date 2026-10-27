# Đáp án app mẫu mk-secu

Không đưa file này cho agent soát. Đường dẫn tính từ gốc `app/` (gốc repo tạm khi chấm). Lớp = mã trong
`skills/mk-secu/references/catalog.md`.

## Luật chấm

- **Vị trí chính = token dấu vết đầu tiên** của `- Dấu vết:` (skill yêu cầu token đầu là chỗ code sai).
- Khớp lỗi cài = token đầu cùng file + dòng giao nhau với cột Dòng + `- Lớp:` bắt đầu bằng cùng mã.
- Đúng Loại = `- Loại:` thuộc cột Loại chấp nhận.
- Báo nhầm = phát hiện `xác nhận` có token đầu nằm trong dòng của một bẫy, hoặc ở một file sạch.
- Phát hiện `xác nhận` khác (file lỗi, lớp khác) = phát hiện thừa: ghi lại, không trừ điểm.

## Lỗi cài

| ID | File | Dòng | Lớp | Loại chấp nhận | AC / gợi ý | Mô tả |
|---|---|---|---|---|---|---|
| B1 | `orders.py` | 16-26 | IDOR | code sai AC | UC-101 AC-2 | `view_order` lấy đơn theo mã, không lọc chủ đơn: khách đọc đơn và địa chỉ giao của khách khác |
| B2 | `auth.py` | 50-57 | RATE-LIMIT | code sai AC | UC-103 AC-3 | `login` không đếm lần sai, không khoá tạm: dò mật khẩu không giới hạn |
| B3 | `settings.py` | 2 | SECRET | hạ tầng | thu hồi/đổi khoá | khoá ký phiên viết cứng và nằm trong git: ai đọc repo cũng ký được phiên của bất kỳ người dùng nào (kể cả nhân viên) |
| B4 | `account.py` | 8-22 | MASS-ASSIGN | thiếu AC | ADDED UC-102 AC-n: khách gửi vai/điểm/email thì KHÔNG đổi | `update_profile` nhận `role`, `points`, `email` từ body: khách tự thành nhân viên, tự cộng điểm |
| B5 | `account.py` | 25-42 | SSRF | thiếu AC · luật sai (UC-102 AC-3) | ADDED UC-102 AC-n: link trỏ địa chỉ nội bộ thì KHÔNG lấy; hoặc hỏi chủ nghiệp vụ về UC-102 AC-3 | `set_avatar` tải mọi URL http(s) từ máy chủ, `get_avatar` trả lại nội dung: đọc được dịch vụ nội bộ |
| B6 | `orders.py` | 5-13 | SQLI | code sai AC | UC-101 AC-2 | `list_orders` ghép `tim` vào câu SQL: thoát điều kiện chủ đơn, đọc đơn người khác và bảng `users` |

Phủ Loại: `code sai AC` ×3, `thiếu AC` ×2 (B5 chấp nhận cả `luật sai`), `hạ tầng` ×1. Mức không chấm.

## Bẫy (trông như lỗi, phải lần qua file khác mới thấy không phải)

| ID | File | Dòng | Trông như | Lý do không phải |
|---|---|---|---|---|
| T1 | `queries.py` | 4-9 | SQLI | `OFFSET {offset}` ghép bằng f-string, nhưng `page` đã bị ép `int` ở nơi gọi (`orders.py:32`); `PAGE_SIZE` là hằng |
| T2 | `pages.py` | 10-16 | XSS | HTML ghép bằng f-string từ `view`, nhưng `view` là kết quả `web.escaped` (`web.py:6-7`, `html.escape` mọi giá trị) |
| T3 | `pages.py` | 5-9 | IDOR | truy vấn `WHERE id = ?` không lọc chủ đơn, nhưng route `/don/trang` được bọc bởi `owner_only` (`server.py:14-23`, `server.py:31`) — kiểm đăng nhập và chủ đơn trước khi gọi |

Token đầu ở `orders.py:29-33` với lớp `SQLI` cũng tính là báo nhầm (nơi gọi của T1).

## File sạch (không được có `xác nhận` có token đầu ở đây)

- `server.py`
- `db.py`
- `web.py`
- `staff.py` (xem mọi đơn là đúng UC-101 AC-4; kiểm vai `staff` lấy từ DB. Leo lên `staff` qua B4 là lỗi của `account.py`)
- `schema.sql`

Ghi chú: `auth.py` ngoài `login` (băm PBKDF2 có muối, ký và đọc phiên có hạn) là đúng; phát hiện `xác nhận` ở đó với lớp
khác `RATE-LIMIT` tính là phát hiện thừa.
