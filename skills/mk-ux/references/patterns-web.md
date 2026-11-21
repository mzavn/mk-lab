# Mẫu chuẩn cho `web` (trang công khai, trang bán hàng, trang học)

Hai mẫu đầy đủ: `form`, `lesson-video`. Sau đó là luật nền của mọi trang web, viết gọn (không phải mẫu 6 phần): điều hướng, tên trang, ô tìm, trang chủ, nội dung lướt được, một nút chính mỗi khung nhìn. Mã đo ở `references/standards.md`; nguyên lý ở `references/principles.md`; mẫu quản trị ở `references/patterns-app-web.md`.

Phần "Kiểm bằng": mã đo chỉ chạy khi trang có `data-ux` đúng tên; không có thì `scripts/ux.py score` ghi `CHƯA KIỂM`. Phần còn lại là "kiểm tay".

Ví dụ dùng dữ liệu giả: khoá học "Nấu ăn tại gia" của chị Lan, SĐT `0901 234 567`, email `lan.nguyen+test@example.com`.

## Mẫu `form`

Dùng khi: người dùng nhập thông tin để đăng ký, mua, liên hệ, đăng nhập.

**Bắt buộc có**
- Nhãn thật nằm ngoài ô, gắn với ô (`<label for>`); chữ gợi ý trong ô không thay nhãn vì biến mất khi gõ (Krug, tr. 172).
- Ô bắt buộc có dấu `*`, và một dòng nói `*` nghĩa là bắt buộc. Chỉ hỏi ô thật cần cho việc này (Krug, tr. 153).
- Lỗi hiện ngay dưới ô khi người dùng rời ô, bằng đúng câu máy chủ sẽ trả, nối với ô qua `aria-describedby`, có `role="alert"`. Câu lỗi nói cách sửa: "Số điện thoại chưa đúng (ví dụ: 0901 234 567)".
- Gợi ý khi gõ nhầm tên miền email: `lan.nguyen@gmial.com` → "Ý bạn là @gmail.com?" kèm nút nhận gợi ý một chạm. Gợi ý không chặn gửi; máy chủ vẫn kiểm lại.
- Bàn phím đúng loại: email `type="email"` `autocomplete="email"`; điện thoại `type="tel"` `autocomplete="tel"`; họ tên `autocomplete="name"`; mã OTP `inputmode="numeric"` `autocomplete="one-time-code"`.
- Hệ thống tự chuẩn hoá số điện thoại: nhận `0901 234 567`, `0901-234-567`, `+84 901 234 567` như nhau; không bắt người dùng gõ theo định dạng của máy (Krug, tr. 153).
- Bấm gửi khi còn lỗi: đưa con trỏ về ô lỗi đầu tiên, nói lỗi ngay ở ô đó; không chỉ bật thông báo nổi "Vui lòng nhập…" rồi biến mất.
- Người thật không bị chặn nhầm: tên có dấu, email có dấu `+`, số di động đang cấp đều qua. Luật chặn chỉ dành cho thứ không thể là dữ liệu thật.
- Đánh dấu: `data-ux="form"` trên khối form.

**Màn nhỏ** (< 768px)
- Một cột; nhãn trên ô; nút gửi rộng hết cột.
- Cỡ chữ ô nhập theo `input-size` (dưới ngưỡng thì iOS phóng to khi chạm). Không khoá phóng to của trình duyệt để chữa việc này; người mắt kém cần tự phóng.
- Chữ chân form (điều khoản, câu nhắc dưới nút) 12px, đánh `data-text="caption"`, nằm một hàng từ 360px; ở 320px chia hai hàng đều.

**Trạng thái**
| Trạng thái | Người dùng thấy |
|---|---|
| Đang gửi | Nút đổi "Đang gửi…" và khoá, chống gửi hai lần (Norman, tr. 59) |
| Lỗi từng ô | Câu lỗi dưới ô, viền ô đổi màu kèm chữ, không chỉ đổi màu |
| Lỗi mạng hoặc máy chủ | Một câu chung trên nút + "Thử lại"; mọi chữ đã nhập còn nguyên |
| Trùng SĐT hoặc email | Nói ô nào trùng và cho lối sửa: "Số này đã đăng ký với email l\*\*\*@example.com. Gõ nhầm? Sửa thông tin" |
| Điền sẵn | Báo "Đã điền sẵn thông tin lần trước" + lối "Không phải bạn? Xoá" |
| Thành công | Nói đã xong gì và bước tiếp theo ("Kiểm tra email để vào học") |

**Hỏi chủ sản phẩm**
- Điền sẵn dữ liệu cá nhân bao lâu (ví dụ 30 ngày), còn giữ sau khi đăng xuất không, và xoá khi nào. Khuyến nghị: có lối xoá ngay trên form.
- Chống bot bằng dịch vụ ngoài (gửi dữ liệu trình duyệt cho bên thứ ba) hay chỉ bằng lớp tự làm (ô bẫy ẩn, gửi quá nhanh, giới hạn số lần). Dữ liệu đáng ngờ thì chặn hay chỉ cách ly để xem lại.
- Cùng SĐT hoặc email nhưng khác người: gộp, hỏi mã xác nhận, hay báo trùng. Khuyến nghị: không cấp quyền vào tài khoản có sẵn khi chưa xác nhận qua kênh của chủ tài khoản.

**Phẩm chất / nguyên lý**
- Hợp lý, dễ dùng, tiện.
- NL-7 (lỗi sớm, đúng ô, nói cách sửa, không bắt làm lại; Norman, tr. 64–65, 199), NL-6 (hệ thống tự chuẩn hoá), NL-9 (nhãn luôn thấy), NL-2 (đang gửi, thành công), NL-10 (điền sẵn, không gõ lại; Krug, tr. 151–152), NL-14 (nhãn gắn ô, `role="alert"`), NL-15 (nói rõ dữ liệu dùng để làm gì).

**Kiểm bằng**
- `pattern-form`: mọi ô nhập trong khối `form` phải có nhãn (`label-all`).
- `input-size`, `tap-target`, `contrast` (chữ lỗi, viền ô), `text-min` (chữ chân form).
- Kiểm tay: lỗi khi rời ô khớp câu máy chủ, gợi ý email, bàn phím trên điện thoại thật, chuẩn hoá SĐT, giữ dữ liệu khi lỗi mạng.

Kiểm trước khi giao: trên điện thoại, gõ `0901-234-567` và `lan.nguyen@gmial.com`, rời ô, thấy gợi ý email; gửi khi mất mạng rồi thử lại, không ô nào bị xoá.

## Mẫu `lesson-video`

Dùng khi: màn học một bài, nội dung chính là video.

**Bắt buộc có**
- Video là thứ đầu tiên của màn, không phải cuộn tìm. Tiêu đề bài ngay dưới video, rồi tới nội dung bài.
- Khung video giữ đúng tỉ lệ ngay từ lúc tải (ví dụ 16:9), để chữ bên dưới không nhảy.
- Thanh "Trước / Tiếp" neo đáy màn, một hàng; nội dung chừa khoảng dưới bằng chiều cao thanh để dòng cuối không bị che.
- Tên nút nói rõ đi đâu khi đủ chỗ ("Tiếp: Kho quẹt tôm"); bài cuối thì nút tiếp đổi thành bước kết thúc, không dẫn vào chỗ rỗng.
- Không tự tải lại trang giữa lúc đang xem (ví dụ khi có bản mới); chờ lúc mở trang hoặc quay lại tab.
- Đánh dấu: trình phát `data-ux="main-task"`; khối bài `data-ux="lesson-video"`; thanh Trước/Tiếp `data-ux="one-row"`.

**Màn nhỏ**
- Video rộng hết màn, nằm trong khung nhìn đầu tiên ở 320px và 390px.
- Thanh Trước/Tiếp chừa vùng an toàn đáy; nút theo `tap-target`.

**Trạng thái**
| Trạng thái | Người dùng thấy |
|---|---|
| Đang tải | Khung đúng tỉ lệ với nền giữ chỗ |
| Video lỗi hoặc mất mạng | "Chưa tải được video" + "Tải lại"; không hiện trang "không tìm thấy" giả |
| Chưa có quyền xem | Nói vì sao và lối mở khoá (đăng ký, đăng nhập) |
| Bài đầu / bài cuối | Nút không dùng được ẩn hoặc khoá kèm nhãn; bài cuối có bước kết thúc |

**Hỏi chủ sản phẩm**
- Có che giao diện của trình phát bên thứ ba (nút, logo, gợi ý video khác) không. Việc này có thể trái điều khoản của nền tảng video; chủ sản phẩm phải tự đọc điều khoản và quyết.
- Có nhớ chỗ đang xem dở và tự chuyển bài khi hết video không.

**Phẩm chất / nguyên lý**
- Hợp lý, tiện, dễ dùng.
- NL-1 (thấy ngay việc chính là xem), NL-5 (Trước trái, Tiếp phải), NL-2 (đang tải, lỗi có lối tiếp), NL-11 (không chen gì giữa video và tiêu đề), NL-13 (màn kết bài).

**Kiểm bằng**
- `main-task-first-view` (< 768px): đỉnh `main-task` phải nằm trong khung nhìn đầu.
- `one-row` trên thanh Trước/Tiếp; `tap-target`; `overflow-x`.
- Khối `lesson-video` chưa có phép đo riêng: `score` ghi `CHƯA KIỂM`, phần còn lại kiểm tay (tỉ lệ khung khi tải, dòng cuối không bị che, bài cuối, không tải lại giữa chừng).

Kiểm trước khi giao: mở bài ở 320px, video nằm trong màn đầu; cuộn tới dòng cuối nội dung, thanh Trước/Tiếp không che chữ.

## Luật nền của mọi trang web

Không phải mẫu 6 phần: mỗi luật một ý, một phép thử, nguyên lý và cách kiểm.

### Điều hướng
- Ở bất kỳ trang nào, kể cả khi vào thẳng từ link ngoài, nhìn lướt vẫn trả lời được: đây là trang web nào, trang này là gì, các mục chính, đang đứng ở đâu, tìm ở đâu (phép thử "thả vào trang sâu", Krug, tr. 83–84).
- Thanh điều hướng cùng chỗ, cùng cách hoạt động trên mọi trang; logo bấm về trang chủ (Krug, tr. 71–74). Mục đang ở được tô bằng ít nhất hai khác biệt, ví dụ màu và đậm (Krug, tr. 81).
- Màn form thanh toán hoặc đăng ký: rút thanh điều hướng còn logo và lối giúp điền, để người dùng không bị kéo đi (Krug, tr. 72).
- NL-1, NL-12. Phẩm chất: dễ dùng, hợp lý. Kiểm tay.

### Tên trang khớp chữ vừa bấm
- Mọi trang có tên, là chữ lớn nhất của phần nội dung, đặt ngay đầu phần riêng của trang (Krug, tr. 78–80).
- Tên trang trùng với chữ trên link hoặc nút người dùng vừa bấm. Bấm "Học thử miễn phí" thì trang mở ra tên là "Học thử miễn phí", không phải "Đăng ký tài khoản".
- Mỗi trang đúng một `h1`.
- NL-5, NL-3. Phẩm chất: hợp lý. Kiểm bằng `h1`; khớp chữ là kiểm tay.

### Ô tìm
- Trang có nhiều nội dung thì mọi trang có ô tìm hoặc lối tới trang tìm. Dạng quen thuộc: một ô, một nút, chữ "Tìm" hoặc kính lúp; không câu hướng dẫn dài, không chọn phạm vi ngay trên ô (Krug, tr. 76).
- Không có kết quả: nói rõ đã tìm gì và gợi ý bước tiếp.
- NL-12, NL-1. Phẩm chất: tiện, gọn. Kiểm tay.

### Trang chủ
- Trong một lần liếc, người lạ trả lời được bốn câu: đây là gì, dành cho ai, làm được gì ở đây, bắt đầu từ đâu (ý của Krug, tr. 89–90, 96–97).
- Có một câu ngắn ngay cạnh tên hoặc ở đầu nội dung nói lợi ích cụ thể; không dùng khẩu hiệu chung chung (Krug, tr. 94–95).
- Điểm bắt đầu trông như điểm bắt đầu và có nhãn rõ ("Xem khoá học", "Đăng nhập").
- Thêm khối quảng bá mới thì quyết định bỏ hoặc luân phiên khối nào (Krug, tr. 97–98).
- NL-1, NL-3, NL-11. Phẩm chất: hợp lý, gọn. Kiểm tay; cách thử với người ngoài ở `references/audit.md`.

### Nội dung lướt được
- Người dùng liếc, không đọc từng chữ (Krug, tr. 30). Tiêu đề tự đủ nghĩa; khoảng trên tiêu đề lớn hơn khoảng dưới để tiêu đề dính vào đoạn nó dẫn (Krug, tr. 50).
- Ba ý trở lên thì gạch đầu dòng; đoạn ngắn; bỏ câu chào hỏi và khối hướng dẫn không ai đọc (Krug, tr. 59–61).
- Một màu cho mọi link chữ; chữ không bấm được không dùng màu link (Krug, tr. 48).
- NL-8, NL-11. Phẩm chất: dễ dùng, gọn. Kiểm bằng `body-text-mobile`, `contrast`; cấu trúc là kiểm tay.

### Một nút chính mỗi khung nhìn
- Tại mỗi vị trí cuộn, tối đa một nút chính giao khung nhìn. Trang dài được có nhiều nút đăng ký, miễn không hai nút chính cùng lúc trong một màn.
- Thanh nút dính đáy chỉ hiện khi nút chính phía trên đã cuộn khỏi màn.
- Đánh dấu: nút chính `data-ux="primary"`.
- NL-4, NL-11, NL-15 (không dồn ép bằng nhiều nút giống nhau). Phẩm chất: hợp lý, gọn. Kiểm bằng `primary-cta`.
