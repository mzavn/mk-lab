# Mode `design` — tạo hoặc làm lại `DESIGN.md`

`DESIGN.md` ở **gốc repo** (cạnh `AGENTS.md`) là hợp đồng giao diện: mọi code UI dùng token của nó. Nó không phải hành vi nên sửa không cần proposal; nhưng AC không được chứa giá trị token (AC nói "hiện thông báo lỗi", `DESIGN.md` nói thông báo lỗi trông thế nào). Mẫu: `assets/DESIGN.md.template`.

Gốc repo đã có `DESIGN.md` mà là tài liệu khác (kiến trúc, ghi chú thiết kế phần mềm) → hỏi người dùng đặt tên khác hay dời file cũ; không ghi đè.

Chọn một trong 3 cách — hỏi người dùng khi họ chưa nói:

| Cách | Hợp khi | Kết quả |
|---|---|---|
| A. Từ trang mẫu | người dùng đưa URL muốn "giống style" | `DESIGN.md` đo từ trang thật + `design-demo.html` (tuỳ chọn) |
| B. Từ code có sẵn | repo đã có giao diện, chưa có tài liệu design | `DESIGN.md` trích từ CSS/theme/config đang chạy |
| C. Từ brief | dự án mới, chưa có gì để đo | `DESIGN.md` từ hướng thẩm mỹ người dùng chọn |

## A. Từ trang mẫu

Luật cứng: **không đoán giá trị** — mọi màu, cỡ, khoảng cách, shadow lấy từ style tính được của trang thật; **không chép** chữ, logo, ảnh của trang mẫu — chỉ lấy token và cách dựng.

1. Mở trang bằng công cụ trình duyệt (desktop 1440px và 375px). Cuộn qua từng đoạn trước khi chụp toàn trang — trang hay ẩn nội dung tới khi cuộn tới. Có nút sáng/tối → bấm, đo cả hai bộ.
2. Lấy biến CSS ở gốc: duyệt `getComputedStyle(document.documentElement)`, giữ các biến `--*` về màu, chữ, khoảng cách, radius, shadow. Trang không dùng biến → đo `getComputedStyle` trên phần tử mẫu: `h1`–`h3`, `p`, nút chính/phụ, link, ô nhập, thẻ (card), nav, footer, `code`.
3. Đọc cấu trúc thật: class và thứ tự thẻ của header, khối chính, lưới thẻ, footer. HTML bị nén một dòng → lưu ra file tạm, cắt đoạn quanh một chuỗi chữ độc nhất rồi mới đọc; không đọc nguyên dòng dài.
4. Gom thành thang: màu thành vai trò (nền, bề mặt, chữ chính/phụ, viền, nhấn, trạng thái); cỡ chữ thành thang có tỉ lệ; khoảng cách về bội số chung (thường 4px). Giá trị lẻ xuất hiện một lần → ghi chú, không thành token. Mỗi token ghi **nguồn đo** (selector + thuộc tính, vd `button.primary` › `background-color`) ở cột Nguồn của mẫu.
5. Viết `DESIGN.md` theo mẫu, dòng Nguồn ghi "đo từ trang mẫu ngày …". URL trang mẫu ghi vào câu trả lời và thân commit, **không** ghi vào `DESIGN.md` (tên miền thường là thương hiệu — bước 8 phải 0 kết quả).
6. (Tuỳ chọn — chỉ khi người dùng muốn) `design-demo.html` một file ở gốc repo: CSS thuần với đúng token, các khối mẫu dùng chữ giữ chỗ ("Thương hiệu của bạn"), có nút đổi sáng/tối nếu trang mẫu có. Không dùng CDN biên dịch lúc chạy.
7. Kiểm: mở `design-demo.html` (hoặc một màn đã áp token) trên trình duyệt, so ảnh với trang mẫu ở cùng kích thước, đổi sáng/tối, console 0 lỗi.
8. Kiểm không chép: tìm trong `DESIGN.md` và `design-demo.html` tên thương hiệu, tiêu đề, câu chữ nổi bật và tên miền ảnh của trang mẫu — phải 0 kết quả.
9. Xoá file tạm (HTML đã lưu, đoạn cắt). Còn lại: `DESIGN.md` (+ `design-demo.html` nếu người dùng muốn giữ).

## B. Từ code có sẵn

1. Tìm nguồn token: biến CSS (`:root`), file theme, `tailwind.config.*`, design token JSON, thư viện component đang dùng.
2. Đếm giá trị thật đang dùng trong code (màu hex/rgb, khoảng cách, cỡ chữ, radius). Giá trị dùng nhiều → token; giá trị lẻ → liệt kê ở mục "Lệch cần dọn" (không tự sửa code).
3. Mở vài màn chính trên trình duyệt để ghi công thức component và trạng thái thật (hover, focus, lỗi, rỗng).
4. Viết `DESIGN.md`; mục "Lệch cần dọn" để người dùng quyết có mở proposal dọn hay không.

## C. Từ brief

1. Hỏi tối đa 3 điều: sản phẩm cho ai, dùng ở đâu/lúc nào (văn phòng, điện thoại ngoài trời…), cảm giác muốn có (vd tin cậy, vui, gọn). Có trang người dùng thích → chuyển sang cách A.
2. Chọn một hướng rõ ràng, nói một câu: "<hướng> cho <người dùng>: <bảng màu 5 chữ>, <kiểu chữ>, <bố cục>, <một điểm nhớ>". Một chiều được nổi bật (chữ, màu, bố cục hoặc chuyển động), các chiều còn lại tiết chế.
3. Ràng buộc đo được: khoảng cách theo thang 4px; tối đa 2 họ chữ (một tiêu đề, một nội dung), kiểm hiển thị đủ dấu tiếng Việt; chữ nội dung 16–18px, dòng 1,5–1,7; tương phản chữ ≥ 4,5:1; không dùng đen/trắng tuyệt đối; một hệ bo góc; một kiểu đổ bóng/viền cho bề mặt.
4. Tránh mặc định "AI làm": tím gradient trên nền trắng, hero giữa + ba thẻ bằng nhau, chữ gradient, kính mờ khắp nơi, emoji làm icon, số liệu bịa tròn trịa.
5. Viết `DESIGN.md`; xem token trên trình duyệt bằng `design-demo.html` (khối mẫu, chữ giữ chỗ) trước khi người dùng duyệt. Không dựng màn hình của proposal ở bước này — màn hình đi theo test trước (`ui-lane.md`).

## Kiểm `DESIGN.md` trước khi giao

- Đủ mục của mẫu; mỗi token có giá trị cụ thể và "dùng cho".
- Có bộ màu tối nếu sản phẩm có chế độ tối.
- Mỗi component có trạng thái: mặc định, hover, focus, active, disabled, đang tải, lỗi (khi áp dụng).
- Không chứa tên, logo, câu chữ của trang mẫu.
- Người dùng đã xem màn mẫu/demo trên trình duyệt và đồng ý.
