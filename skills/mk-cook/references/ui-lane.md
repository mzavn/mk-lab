# Làn UI — giao diện theo spec

Vào từ mode `apply` khi proposal có màn hình. Mục tiêu: giao diện đúng AC, đúng `DESIGN.md`, đã xem tận mắt trên trình duyệt.

## 1. Đầu vào

| Nguồn | Dùng để | Không có thì |
|---|---|---|
| `DESIGN.md` (gốc repo) | token màu, chữ, khoảng cách, bề mặt; công thức component kèm trạng thái chung | Dừng, hỏi người dùng chọn 1 trong 3 cách tạo (`design-md.md`); không tự chọn, không code UI trước khi có file. Có `DESIGN.md` nhưng là tài liệu khác (kiến trúc, ghi chú) → hỏi; không ghi đè |
| `specs/wireframe.html` | bố cục, thứ tự khối, nội dung từng màn | Bố cục theo `DESIGN.md` § Bố cục + AC; ghi vào bằng chứng là "không có wireframe" |
| AC trong UC/proposal | hành vi, thông báo, luật hiển thị | Không có AC cho một màn → không dựng màn đó (ngoài phạm vi) |
| `entities` | field của form/bảng, ràng buộc, giá trị hợp lệ | Field AC không nói → hỏi, không đoán |

## 2. Bảng màn hình × trạng thái

Trước khi viết test, lập bảng (đưa vào bằng chứng nếu nhiều màn):

| Màn | Trạng thái | Nguồn luật | Kiểm bằng |
|---|---|---|---|
| Giỏ hàng | rỗng: "Chưa có món nào" + nút về menu | UC-101 AC-5 | test component |
| Giỏ hàng | lỗi mạng khi đặt | `DESIGN.md` › Thông báo lỗi chung | xem trình duyệt |
| Giỏ hàng | đang gửi | `DESIGN.md` › Nút (loading) | xem trình duyệt |

- **Trạng thái có luật nghiệp vụ riêng** (nội dung lỗi, rỗng, thiếu quyền, hết hạn, giới hạn số lượng) → phải có AC; thiếu AC → dừng, đề xuất thêm AC (tham vấn), không tự đặt câu chữ/luật.
- **Trạng thái chung** (đang tải, hover, focus, disabled, lỗi mạng chung) → theo công thức component trong `DESIGN.md`, kiểm trong bước 4, không thành AC.

## 3. Test và code

- Test theo AC kiểm thứ người dùng thấy: chữ hiển thị, phần tử có/không, giá trị sau thao tác, điều hướng. Dùng thư viện test UI repo đang dùng; repo chưa có → hỏi trước khi thêm công cụ.
- Code chỉ dùng token của `DESIGN.md` (biến CSS, theme, config Tailwind…). Không màu hex, khoảng cách, cỡ chữ "tự chọn" giữa file. Cần giá trị mới → đề xuất sửa `DESIGN.md`, người dùng duyệt, rồi mới dùng.
- Form: nhãn thật (không dùng placeholder làm nhãn), lỗi hiện dưới ô và đọc được bằng trình đọc màn hình; lúc nào hiện lỗi (khi rời ô hay khi bấm nút) theo AC — AC không nói thì hỏi, không tự chọn; ô nhập ≥ 16px (tránh phóng to trên mobile).
- Phần tử bấm được có trạng thái hover, focus nhìn thấy, active, disabled; vùng chạm ≥ 44×44px.

## 4. Kiểm trên trình duyệt (bắt buộc)

Chạy dev server của repo (lệnh trong `AGENTS.md`/`package.json`), mở bằng công cụ trình duyệt của agent:

1. Hai kích thước: 375px và desktop (≥ 1280px). Không cuộn ngang ở 375px; tiêu đề không tràn.
2. Đi qua từng dòng của bảng §2: tạo đúng điều kiện (dữ liệu rỗng, chặn mạng, tài khoản thiếu quyền giả) và nhìn kết quả.
3. Bàn phím: Tab đi hết phần tử bấm được theo thứ tự hợp lý, focus nhìn thấy.
4. Console: 0 lỗi, 0 cảnh báo mới do thay đổi này.
5. So với `wireframe.html` (nếu có): đủ khối, đúng thứ tự.
6. Tương phản chữ thường ≥ 4,5:1, chữ lớn ≥ 3:1 (kể cả chữ mờ, placeholder).

Không có công cụ trình duyệt → nói rõ giới hạn, đưa người dùng danh sách kiểm tay ở trên và chờ họ báo kết quả; bằng chứng ghi "người dùng <tên> xem ngày <ngày> bằng <trình duyệt>". Không tự ghi "đã kiểm giao diện" thay người dùng.

## 5. Ghi vào bằng chứng

Dòng "Trạng thái kiểm chứng" thêm: kích thước đã xem, trạng thái đã thử (theo bảng §2), console lỗi = 0, tương phản đạt, chỗ lệch wireframe (nếu có, kèm lý do). Ảnh chụp (nếu chụp) để ngoài git hoặc trong thư mục repo đã quy ước — không thêm file nhị phân vào repo khi người dùng chưa đồng ý.
