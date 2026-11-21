# Tầng 3 — Cấu trúc

Tầng này trả lời "sắp xếp ra sao" trước khi bàn màu, phông hay token. Thứ tự cố định, đi từ người tới pixel:

**hoạt động → hành trình → màn → việc chính → khối → mẫu chuẩn → nguyên tố + bảng trạng thái → token**

Mỗi bậc chỉ được quyết khi bậc trên đã rõ. Sai ở bậc trên thì đẹp ở bậc dưới không cứu được. Cách hỏi để có hoạt động, hành trình và việc chính nằm ở `references/needs.md`; mode `system` dùng thứ tự này ở `references/system.md`.

## Thiết kế theo hoạt động

Norman tách **hoạt động** (việc lớn người đang làm, ví dụ "cho nhà ăn tối") khỏi **tác vụ** (từng bước nhỏ, ví dụ "tìm công thức", "đặt nguyên liệu"). Sản phẩm nên lấy hoạt động làm khung: mô hình khái niệm của sản phẩm bám theo mô hình của hoạt động, và người chịu học thứ phức tạp nếu nó thiết yếu cho hoạt động, nhưng không chịu thứ tuỳ tiện (Norman, tr. 231–234). Điều khiển gom theo việc người đang làm tốt hơn gom theo bộ phận kỹ thuật, và chỉnh tay một chỗ không được huỷ cả hoạt động đang chạy (Norman, tr. 140–141).

Hệ quả cho bạn:
- Danh sách màn sinh ra từ hành trình, không từ bảng dữ liệu. "Màn Funnel", "màn Lead" là tên bảng; "Đăng ký học thử", "Học viên mới hôm nay" là tên việc.
- Mỗi nhóm người dùng một hành trình, gồm cả **người trong nhà** (chủ quán, nhân viên trực, người duyệt đơn): họ dùng trang quản trị nhiều giờ mỗi ngày.
- Việc phụ không được chen vào đường của việc chính.

## Các bậc

| Bậc | Câu hỏi | Ví dụ giả (khoá học "Nấu ăn tại gia" của chị Lan) |
|---|---|---|
| Hoạt động | Người đang cố làm việc lớn gì trong đời họ? | học nấu vài món để cuối tuần nấu cho nhà |
| Hành trình | Đi từ đâu, thiết bị gì, qua mấy bước tới việc chính? | thấy bài trên mạng xã hội → mở trên điện thoại → xem video thử → đăng ký → nhận bài học |
| Màn | Hành trình cần những màn nào, không hơn? | trang khoá học, form đăng ký, màn học, trang quản trị học viên |
| Việc chính | Ở màn này người đến để làm một việc gì? | màn học: xem video bài hôm nay |
| Khối | Màn chia thành vùng nào, vùng nào phục vụ việc chính? | video · tên bài · nội dung · thanh Trước/Tiếp |
| Mẫu chuẩn | Khối nào đã có mẫu chuẩn? | `lesson-video`, `form`, `data-table`, `overlay` |
| Nguyên tố + trạng thái | Khối dựng bằng nguyên tố chung nào, có những trạng thái nào? | nút, ô nhập, dòng danh sách; rỗng, đang tải, lỗi |
| Token | Màu, chữ, khoảng cách cụ thể | do mk-cook giữ |

Mẫu chuẩn: `form`, `lesson-video` ở `references/patterns-web.md`; `data-table`, `toolbar`, `overlay`, `mobile-header` ở `references/patterns-app-web.md`; `slide`, `image` ở `references/surfaces.md`.

## Nguyên tố: định nghĩa một lần cho cả bộ

Mỗi nguyên tố có **một** định nghĩa dùng cho mọi màn. Màn nào cần biến thể thì thêm biến thể vào định nghĩa chung, không tự viết bản riêng. Hai hộp thoại khác kiểu, hai hàm định dạng ngày là dấu hiệu bộ đã vỡ (xem `references/ai-mistakes.md`).

| Nguyên tố | Định nghĩa chung phải nói | Ghi chú |
|---|---|---|
| Nút | các bậc (chính, phụ, nguy hiểm), cỡ vùng chạm, trạng thái bấm/đang xử lý/khoá | một nút chính mỗi khung nhìn |
| Ô nhập | nhãn ngoài ô, chữ gợi ý, chỗ hiện lỗi, `inputmode`/`autocomplete` theo loại dữ liệu | cỡ chữ theo `input-size` |
| Thẻ | vùng bấm là cả thẻ hay chỉ nút, ảnh, tiêu đề, độ cao đều nhau trong một hàng | |
| Dòng danh sách | thông tin chính bên trái, hành động bên phải, cách chọn nhiều | |
| Lớp nổi | hộp thoại (xác nhận ngắn) và tấm trượt (form, đọc dài); đầu, thân cuộn, hàng nút | mẫu `overlay` |
| Trạng thái rỗng | câu nói vì sao rỗng và một nút làm bước tiếp | dùng chung cho mọi danh sách |

## Bảng trạng thái dùng chung

Mọi khối có dữ liệu đi qua cùng một bảng. Phần **hành vi** (người thấy gì, làm được gì) là luật nghiệp vụ, thành AC qua `references/needs.md`. Phần **hình thức** (màu, khung xương, chỗ đặt thông báo) là công thức trong `DESIGN.md`, không thành AC.

| Trạng thái | Khi nào | Thành AC (hành vi) | Công thức `DESIGN.md` (hình thức) |
|---|---|---|---|
| Rỗng | máy chủ trả danh sách rỗng thật | câu nói vì sao, nút bước tiếp ("Chưa có học viên — Chia sẻ link đăng ký") | minh hoạ hay không, cỡ chữ, vị trí |
| Đang tải | đang chờ dữ liệu | sau bao nhiêu giây hiện khung xương; quá bao lâu thì báo chậm | kiểu khung xương, hiệu ứng |
| Lỗi | mạng hoặc máy chủ hỏng (không phải rỗng) | không giả làm rỗng hay "không tìm thấy"; có nút "Tải lại"; dữ liệu đã nhập còn nguyên | màu, biểu tượng, chỗ đặt |
| Khoá / thiếu quyền | người chưa đăng nhập, chưa mua, không đủ quyền | ai thấy gì, nói rõ thiếu gì và lối mở khoá | kiểu ổ khoá, làm mờ |
| Đang gửi | đã bấm gửi, chưa có phản hồi | nút không gửi đôi; quá bao lâu thì báo | kiểu nút đang xử lý |
| Thành công | máy chủ xác nhận | điều gì xảy ra tiếp (ở lại, chuyển trang, giữ dữ liệu điền sẵn) | thông báo nổi bao lâu, chỗ đặt |

Quy tắc: mỗi màn trong danh sách màn ghi rõ trạng thái nào có, trạng thái nào không áp. Một trạng thái chưa ai nghĩ tới là chỗ máy sẽ tự bịa.

## Điều hướng là cấu trúc, không phải trang trí

Người thường vào giữa sản phẩm từ link trong tin nhắn, email hay kết quả tìm kiếm, không qua trang chủ (Krug, tr. 84). Vì vậy **mọi màn** phải tự trả lời được, chỉ bằng một cái nhìn mờ:

- **Đây là đâu?** Tên hoặc logo sản phẩm có mặt ở mọi màn, bấm về trang đầu.
- **Trang gì?** Mỗi màn có tên riêng, nổi nhất trang, và khớp chữ trên nút hay link người vừa bấm (Krug, tr. 78–80).
- **Đang ở đâu?** Mục hiện tại trong menu khác hẳn các mục khác, bằng ít nhất hai dấu hiệu như màu và độ đậm, vì dấu hiệu tinh tế bị người vội bỏ qua (Krug, tr. 81).
- **Đi tiếp đâu, tìm thế nào?** Thấy được các phần chính, lối trong phần hiện tại và ô tìm (nếu sản phẩm đủ lớn).

Phép thử nhanh (ý của Krug về "phép thử cốp xe", tr. 83–84): mở một màn sâu bất kỳ, nheo mắt hoặc cầm điện thoại xa ra, rồi chỉ tay vào từng thứ ở trên. Thiếu thứ nào là lỗi cấu trúc. Ngoại lệ: màn đang điền form (đăng ký, thanh toán) nên bớt điều hướng, chỉ giữ tên sản phẩm, đường về và thứ giúp điền (Krug, tr. 72).

## Năm mục của mk-ux trong DESIGN.md

`DESIGN.md` có hai chủ. mk-cook giữ phần token (màu, chữ, khoảng cách, thành phần) ở đầu tệp. mk-ux giữ đúng năm mục, đặt **sau** phần token, theo thứ tự dưới đây, tiêu đề viết đúng từng chữ. Chưa cài mk-cook thì phần token để `[điền: token — cài mk-cook]`; mk-ux không tự viết token.

mk-ux chỉ thêm hoặc sửa năm mục này qua bảng mã duyệt (`references/system.md`), không đổi token hay mục khác. Ngược lại, khi mk-cook tạo lại hoặc làm lại `DESIGN.md`, nó **phải giữ nguyên** năm mục này nếu đã có.

### `## Luật trải nghiệm`

Nguyên lý `NL-n` nào áp cho sản phẩm này, viết thành câu cụ thể của dự án. Đây là cổng của mode `system`: chưa duyệt thì chưa viết code màn nào.

```markdown
## Luật trải nghiệm
- Mỗi khung nhìn đúng một nút chính (NL-8).
- Lỗi luôn đi kèm một nút sửa ngay tại chỗ, không chỉ thông báo (NL-7).
- Nhãn tiếng Việt, không viết hoa cả chữ, không dùng tên bảng dữ liệu (NL-12).
```

### `## Mẫu`

Mẫu chuẩn nào dùng ở màn nào, và chỗ dự án lệch khỏi mẫu kèm lý do.

```markdown
## Mẫu
| Mẫu | Dùng ở | Lệch khỏi mẫu | Lý do |
|---|---|---|---|
| data-table | Học viên, Đơn bánh | bỏ chọn số dòng ở Đơn bánh | mỗi ngày dưới 30 đơn |
| form | Đăng ký học thử | — | — |
```

### `## Gu đã chốt`

Quyết định thẩm mỹ chủ sản phẩm đã chốt cho một phát hiện hạng `gu`. Mỗi dòng: quyết định · ngày · lý lẽ đã bị bác. Mode `audit` không nêu lại điều đã chốt; bản dựng làm trái dòng nào thì là phát hiện hạng `lệch hệ`.

```markdown
## Gu đã chốt
| Quyết định | Ngày | Lý lẽ đã bị bác |
|---|---|---|
| Nút xoá nền mờ, không đỏ đặc | 2026-11-21 | "đỏ đặc cho rõ là nguy hiểm" — đã có bước xác nhận nêu tên món |
| Chỉ giao diện sáng | 2026-11-21 | "thêm giao diện tối" — khách dùng ban ngày, tốn gấp đôi kiểm thử |
```

### `## Luật đo`

Ngưỡng số hình thức riêng của dự án, ghi đè bảng mặc định. Cú pháp, ngưỡng đọc được và ví dụ: `references/standards.md`.

```markdown
## Luật đo
| Mã | Lý do | Ngưỡng |
|---|---|---|
| body-text-mobile | khách lớn tuổi | 17px |
```

### `## Bài học`

Lỗi lặp lại từ ≥ 2 báo cáo soi (cùng `- Mã:`) đã biến thành luật, mẫu hay dòng đo. Mục này giữ lý do để không ai gỡ luật vì quên vì sao nó có.

```markdown
## Bài học
| Mã | Gặp ở | Đã thành |
|---|---|---|
| AI-1 | 261121-dang-ky, 261128-man-hoc | dòng `input-size` 16 trong Luật đo |
| tap-target | 261121-dang-ky, 261205-gio-hang | biến thể "nút biểu tượng 44×44" trong nguyên tố Nút |
```
