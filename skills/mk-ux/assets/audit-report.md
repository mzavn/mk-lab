# Báo cáo soi trải nghiệm — <yyMMdd>-<slug>

- Phạm vi: <màn / hành trình / tệp slide, hình, video>
- Bề mặt: <web · app-web · app · slide · image · video>
- Người dùng soi: <khách: …> · <trong nhà: …>
- Đo bằng máy: `ux.py score` · khổ 320, 390, 768, 1440 · `Kết quả: <a>/<b> lượt đạt · chưa kiểm <k> luật`
- Kiểm tay: <bề mặt hay phần nào kiểm tay, hoặc —>
- Soi bằng mắt người dùng: <agent soát, ngày — hoặc `chưa làm: <lý do, vd không có công cụ tạo agent; đã nhờ người dùng mở phiên mới>`> · ảnh trong thư mục tạm của phiên (không vào repo khi chưa được đồng ý)
- Dữ liệu: <giả / môi trường thử> — không chứa tên, email, số điện thoại khách thật

## 3 việc nên sửa trước

1. UX-<n> — <một câu, lời người dùng>
2. UX-<n> — <…>
3. UX-<n> — <…>

## Chưa kiểm bằng máy

- <màn>@<khổ> <mã> — <lý do> → đề xuất: <thuộc tính data-ux cho phần tử nào / kiểm tay>

## Phát hiện

<Mỗi dòng có danh sách giá trị: chọn đúng một giá trị trong danh sách (Phẩm chất được nhiều, ngăn bằng dấu phẩy); ghi chú thêm đặt sau dấu "—" hoặc trong ngoặc.>

### UX-1: <tên ngắn>
- Người dùng: <khách | trong nhà>
- Họ cảm thấy: "<lời người dùng, không thuật ngữ>"
- Hạng: <hỏng | lệch hệ | gu>
- Phẩm chất: <hợp lý | dễ dùng | tiện | gọn | hợp gu | đẹp> (một hay nhiều, ngăn bằng dấu phẩy)
- Nguyên lý: <NL-n, NL-m>
- Mã: <AI-n và/hoặc mã luật đo — tuỳ chọn, xoá dòng nếu không có>
- Điểm A: <hiện tại + bằng chứng: dòng `score`, ảnh, file:dòng>
- Điểm B: <đích đo được>
- Khoảng cách: <A → B cách bao xa, đo bằng gì>
- Tác động: <rất cao | cao | trung bình | thấp>
- Loại sửa: <trình bày | hành vi>
- Trạng thái: <mở | duyệt | đã sửa <commit 7–40 ký tự hex> | bỏ>

## Đo lại sau sửa

<Chỉ điền khi có mã `đã sửa`, lấy từ `ux.py score <mới> --baseline <cũ>`:>
Đo trước: <a>/<b> · Đo sau: <c>/<b>

## Còn thấy

- <≤ 5 dòng việc người dùng cần quyết; hoặc —>
