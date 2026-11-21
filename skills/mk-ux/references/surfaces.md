# Bề mặt: cái nào máy đo, cái nào kiểm tay

Sáu bề mặt. Hai bề mặt đo bằng máy (`assets/measure.js` rồi `scripts/ux.py score`); bốn bề mặt kiểm tay bằng danh sách dưới đây. Mã đo và ngưỡng ở `references/standards.md`; mẫu cho `web` và `app-web` ở `references/patterns-web.md` và `references/patterns-app-web.md`; cách viết phát hiện ở `references/audit.md`.

## Bảng bề mặt

| Bề mặt | Ví dụ | Cách kiểm | Kiểm sâu (tuỳ chọn) |
|---|---|---|---|
| `web` | trang bán hàng, trang học, blog | đo bằng máy ở 320, 390, 768, 1440 + kiểm tay phần không đo được | thử với 3 người ngoài theo `references/audit.md` |
| `app-web` | trang quản trị, PWA, dashboard | đo bằng máy như `web`, thêm mẫu bảng, thanh công cụ, overlay | chạy với dữ liệu dài nhất và danh sách rỗng |
| `app` | ứng dụng iOS, Android | kiểm tay | thử trên máy thật, chữ hệ thống phóng to tối đa |
| `slide` | bài giảng, bài thuyết trình | kiểm tay; slide làm bằng HTML thì đo được như `web` | chiếu thử ở phòng thật hoặc chia sẻ màn hình nhỏ |
| `image` | ảnh quảng cáo, ảnh bìa, ảnh đăng mạng xã hội | kiểm tay | xem thử ở cỡ thu nhỏ trên điện thoại |
| `video` | video bài học, video ngắn | kiểm tay | xem trên điện thoại khi tắt tiếng |

Luật báo cáo cho bốn bề mặt kiểm tay:
- Mỗi mục ghi `kiểm tay: đạt`, `kiểm tay: trượt` hoặc `kiểm tay: chưa xem`, kèm ai xem và xem trên gì.
- Không bao giờ ghi "đạt" như thể máy đã đo. `score` không có dữ kiện cho các bề mặt này; đánh `data-ux="slide"` hoặc `data-ux="image"` trên trang HTML chỉ cho ra `CHƯA KIỂM` (mẫu chưa có phép đo).
- Mỗi mục có mã (`APP-n`, `SLIDE-n`, `IMG-n`, `VID-n`), nguyên lý `NL-n` và phẩm chất, để phát hiện trỏ về đúng chỗ.

## `app` (ứng dụng cài trên máy)

| Mã | Kiểm gì | Nguyên lý | Phẩm chất |
|---|---|---|---|
| APP-1 | Vùng chạm theo hướng dẫn của nền tảng (iOS 44pt, Android 48dp), nút cạnh nhau không dính | NL-14, NL-7 | dễ dùng |
| APP-2 | Bật cỡ chữ hệ thống lớn nhất: chữ không cắt, nút không đè nhau | NL-14 | dễ dùng |
| APP-3 | Nút quay lại và cử chỉ vuốt về chạy đúng như ứng dụng khác của nền tảng | NL-12 | dễ dùng |
| APP-4 | Nội dung và nút không nằm dưới tai thỏ, thanh trạng thái, thanh home | NL-11 | hợp lý |
| APP-5 | Bàn phím mở ra không che ô đang nhập và nút gửi | NL-1, NL-6 | tiện |
| APP-6 | Xin quyền (thông báo, vị trí, ảnh) đúng lúc cần, nói vì sao; từ chối vẫn dùng được phần khác | NL-15, NL-10 | hợp lý |
| APP-7 | Mất mạng: báo rõ, giữ dữ liệu đã nhập, tự gửi lại hoặc có nút thử lại | NL-2, NL-7 | hợp lý |
| APP-8 | Mở từ thông báo hoặc link: vào đúng màn đó, không về màn đầu | NL-10 | tiện |
| APP-9 | Thao tác lâu có tiến độ; chạm có phản hồi ngay | NL-2 | dễ dùng |
| APP-10 | Màn đầu tiên chỉ ra được một việc chính và trạng thái hiện tại | NL-1, NL-3 | hợp lý |

Kiểm trước khi giao: chạy trên một máy thật mỗi nền tảng, chữ hệ thống lớn nhất, chế độ máy bay một lần.

## Mẫu `slide`

Dùng khi: một bộ slide để giảng hoặc trình bày. Chủ sản phẩm nói: "slide thì lại ít chữ, nhiều hình minh họa".

**Bắt buộc có**
- Một ý mỗi slide; tiêu đề slide là câu nói ra ý đó ("Bánh mì nóng bán gấp đôi lúc 6 giờ sáng"), không chỉ là chủ đề ("Doanh số").
- Hình minh hoạ có thông tin chiếm phần lớn diện tích; ảnh trang trí cho vui thì bỏ, vì người xem lờ nó đi.
- Chữ ít và to: đọc được từ cuối phòng hoặc khi chia sẻ màn hình lên điện thoại.
- Số liệu thành biểu đồ hoặc bảng nhỏ, tô điểm đúng con số cần nhớ; không dán bảng 12 cột.
- Cùng vị trí tiêu đề, cùng bộ màu, cùng cỡ chữ cho cả bộ.
- Slide làm bằng HTML: đánh `data-ux="slide"` cho từng slide; phần chữ, tương phản, tràn khung đo như `web`.

**Màn nhỏ**
- Người xem qua điện thoại khi họp trực tuyến hoặc xem lại: thử thu slide còn cỡ một màn điện thoại, chữ chính vẫn đọc được.

**Trạng thái**
- Slide mở đầu: một câu nói buổi này giúp người xem được gì.
- Slide kết: điều cần nhớ và việc làm tiếp; người xem nhớ rõ nhất phần đầu và phần cuối.
- Slide dữ liệu khó: số dài, tên dài nhất vẫn nằm gọn trong khung.

**Hỏi chủ sản phẩm**
- Slide dùng để chiếu kèm lời giảng hay gửi cho người tự đọc. Gửi tự đọc thì cần thêm chữ hoặc ghi chú; khuyến nghị tách hai bản thay vì nhồi chữ vào bản chiếu.

**Phẩm chất / nguyên lý**
- Gọn, hợp lý, đẹp.
- NL-8 (một ý nổi nhất, lướt được), NL-11 (ít chữ), NL-12 (nhất quán cả bộ), NL-13 (mở và kết), NL-14 (chữ to, tương phản đủ).

**Kiểm bằng**
| Mã | Kiểm gì | Nguyên lý | Phẩm chất |
|---|---|---|---|
| SLIDE-1 | Mỗi slide một ý; tiêu đề là câu nói ra ý đó | NL-8 | hợp lý |
| SLIDE-2 | Hình có thông tin chiếm phần lớn; không ảnh trang trí | NL-11 | gọn |
| SLIDE-3 | Chữ đọc được khi thu cỡ màn điện thoại | NL-14 | dễ dùng |
| SLIDE-4 | Số liệu là biểu đồ hoặc bảng nhỏ, có tô điểm con số chính | NL-8, NL-9 | hợp lý |
| SLIDE-5 | Tiêu đề, màu, cỡ chữ nhất quán cả bộ | NL-12 | hợp gu |
| SLIDE-6 | Có slide mở nói lợi ích và slide kết nói việc tiếp | NL-13 | hợp lý |

Slide HTML thêm mã đo `text-min`, `contrast`, `contrast-large`, `overflow-x`; phần còn lại kiểm tay.

Kiểm trước khi giao: lướt cả bộ, mỗi slide nói lại được ý chính trong một câu; slide nào phải đọc quá ba dòng chữ thì cắt.

## Mẫu `image`

Dùng khi: một ảnh đứng riêng mang thông điệp (quảng cáo, ảnh bìa, ảnh đăng bài, ảnh thu nhỏ của video).

**Bắt buộc có**
- Một thông điệp; một điểm nhìn chính.
- Chữ và chi tiết quan trọng nằm trong vùng giữa an toàn, không sát mép, vì mỗi nơi hiển thị cắt ảnh một kiểu.
- Tỉ lệ đúng kênh đăng (vuông, dọc, ngang, ảnh bìa) theo hướng dẫn hiện hành của kênh; không kéo giãn một ảnh dùng cho mọi kênh.
- Chữ trên ảnh tách rõ khỏi nền (lớp nền đặc hoặc vùng ảnh đơn giản); chữ ít.
- Ảnh trong trang HTML có `alt` nói thông điệp; ảnh trang trí để `alt=""`.

**Màn nhỏ**
- Xem thử ở cỡ thu nhỏ như trong bảng tin điện thoại: thông điệp vẫn đọc được trong một cái liếc.

**Trạng thái**
- Bản nhiều kênh: mỗi tỉ lệ một bản dàn lại, không cắt máy móc.
- Dữ liệu khó: tên khoá học dài nhất, giá có nhiều chữ số vẫn nằm trong vùng an toàn.

**Hỏi chủ sản phẩm**
- Ảnh đăng những kênh nào (quyết định tỉ lệ và vùng an toàn).
- Ảnh có dùng hình người thật hoặc ảnh khách không; đã có đồng ý chưa.

**Phẩm chất / nguyên lý**
- Hợp lý, đẹp, hợp gu.
- NL-8 (một điểm nhìn), NL-11 (ít chữ), NL-14 (tương phản chữ trên ảnh, `alt`), NL-15 (không giật tít sai sự thật).

**Kiểm bằng**
| Mã | Kiểm gì | Nguyên lý | Phẩm chất |
|---|---|---|---|
| IMG-1 | Một thông điệp, một điểm nhìn chính | NL-8 | hợp lý |
| IMG-2 | Chữ và chi tiết chính nằm trong vùng giữa an toàn | NL-11 | hợp lý |
| IMG-3 | Tỉ lệ đúng từng kênh đăng | NL-12 | gọn |
| IMG-4 | Đọc được ở cỡ thu nhỏ trên điện thoại | NL-14 | dễ dùng |
| IMG-5 | Chữ trên ảnh tách rõ khỏi nền | NL-14 | đẹp |
| IMG-6 | Lời trên ảnh khớp với nội dung thật phía sau | NL-15 | hợp lý |

Tương phản chữ trên ảnh máy không đo được (nền ảnh ghi `CHƯA KIỂM`); công cụ `ux.py contrast` chỉ dùng khi bạn tự lấy được hai mã màu.

Kiểm trước khi giao: thu ảnh còn cỡ ngón tay cái, vẫn nói lại được thông điệp; cắt theo từng kênh không mất chữ.

## `video`

Danh sách cấu trúc, chưa phải mẫu đầy đủ.

| Mã | Kiểm gì | Nguyên lý | Phẩm chất |
|---|---|---|---|
| VID-1 | Mở đầu giữ chân: vài giây đầu nói ngay người xem được gì, không màn chào dài | NL-1, NL-13 | hợp lý |
| VID-2 | Một ý mỗi đoạn; chuyển đoạn có dấu hiệu rõ (tiêu đề, chương) | NL-8 | dễ dùng |
| VID-3 | Có phụ đề, đọc được: đủ to, tách khỏi nền, đúng lời nói | NL-14 | dễ dùng |
| VID-4 | Chữ và chi tiết chính nằm trong vùng an toàn, không bị nút của trình phát che | NL-11 | hợp lý |
| VID-5 | Tỉ lệ khung đúng nơi phát (ngang cho bài học, dọc cho video ngắn) | NL-12 | gọn |
| VID-6 | Xem khi tắt tiếng vẫn hiểu ý chính | NL-9, NL-14 | tiện |
| VID-7 | Kết thúc nói điều cần nhớ và việc làm tiếp | NL-13 | hợp lý |
| VID-8 | Âm lượng đều giữa các đoạn, lời nói rõ hơn nhạc nền | NL-14 | dễ dùng |

Lộ trình sau, chưa có trong bản này: phân tích video sâu (đo nhịp cắt, độ dài từng đoạn) và vị trí phụ đề theo từng nền tảng. Hiện ghi "kiểm tay" cho mọi mục trên.

Kiểm trước khi giao: xem trên điện thoại khi tắt tiếng, từ đầu tới cuối, ghi kết quả từng mã `VID-n`.
