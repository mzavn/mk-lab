# TDD — <Tên app>
- PRD: [PRD.md](PRD.md) · Cập nhật: YYYY-MM-DD

> Thiết kế kỹ thuật cho các story trong PRD. Không thêm tính năng PRD không có; thấy thiếu thì sửa PRD trước.

## 1. Kiến trúc
```
<sơ đồ chữ: người dùng → giao diện → máy chủ/API → CSDL; dịch vụ ngoài>
```

## 2. Stack
<Chưa quyết: cột "Chọn" ghi `[OPEN] Ox` (số trong PRD), cột cuối liệt kê phương án đang xét.>

| Lớp | Chọn | Vì sao | Phương án bị loại / đang xét |
|---|---|---|---|
| Giao diện | | | |
| Máy chủ | | | |
| CSDL | | | |
| Đăng nhập | | | |
| Chạy ở đâu | | | |

## 3. Dữ liệu
| Bảng / collection | Ứng với (PRD §4) | Trường chính | Ràng buộc quan trọng |
|---|---|---|---|

## 4. API / hành động
| Story | Hành động | Đầu vào → đầu ra | Lỗi đã có quyết định |
|---|---|---|---|

## 5. Luồng cho story có chỗ khó
<Chỉ story có tranh chấp, nhiều bước, tích hợp ngoài; CRUD thường thì bảng §4 là đủ.>
### [<MÃ>-01]
1. <bước — ai gọi gì, dữ liệu đổi ra sao>

## 6. Bảo mật và quyền
- Đăng nhập: <cách> · Ai xem/sửa được gì: <…> · Bí mật để ở: <biến môi trường, không commit>
- <Mọi lựa chọn về quyền truy cập, dữ liệu cá nhân, tiền: ghi "người quyết: <tên>, <ngày>" hoặc trỏ `[OPEN] Ox` của PRD>

## 7. Quy ước và lệnh
<Chỉ ghi điều đã chọn; lệnh chạy/test/build điền khi đã có.>

## 8. Quyết định khác
<Quyết định không phải chọn stack (vd chặn trùng giờ bằng ràng buộc dữ liệu).>
- <Quyết định> — vì <lý do>; đã loại <phương án> vì <lý do>

<Câu hỏi mở: dùng danh sách ở PRD (`O1, O2…`), không chép sang đây.>
