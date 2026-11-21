# Mode `needs` — nhu cầu thật thành AC hành vi

Biến yêu cầu "làm màn X" thành hành trình, việc chính từng màn, câu hỏi cho chủ sản phẩm và AC nháp có số hành vi — trước khi viết code. Vì sao phải làm vậy: `references/principles.md`. Ngưỡng hình thức (cỡ chữ, vùng chạm, tương phản): `references/standards.md`, không thuộc mode này.

## Đầu vào

- Yêu cầu của người dùng, hoặc proposal/UC đang soạn có màn hình hay sản phẩm cho người xem.
- `DESIGN.md` nếu có (đọc `## Mẫu`, `## Gu đã chốt`, `## Bài học` để không hỏi lại điều đã chốt).
- Dữ liệu thật đọc được (đếm số dòng, số lead, tỷ lệ thiết bị) — chỉ đọc, chỉ lấy con số, không chép dữ liệu khách.
- Không có thì hỏi: ai dùng, từ đâu tới, trên thiết bị gì. Không đoán.

## Các bước

1. Lập hoạt động và hành trình cho **mỗi** nhóm người dùng, luôn gồm người trong nhà.
2. Lập bảng việc chính từng màn.
3. Đi qua bảy giai đoạn hành động bằng bộ câu hỏi bên dưới.
4. Hỏi riêng người trong nhà và hỏi về dữ liệu bẩn.
5. Gắn bộ dữ liệu khó tiếng Việt vào AC.
6. Khối nào khớp mẫu chuẩn: kéo phần **Bắt buộc có**; phần **Hỏi chủ sản phẩm** thành câu hỏi kèm khuyến nghị.
7. Viết AC nháp theo khuôn; tự soát từ cấm.
8. Ghi `ux-needs.md`; AC chuyển vào proposal qua mk-specs.

## 1. Hoạt động → hành trình

Hoạt động là việc lớn ("đi học nấu ăn", "chăm khách mới"); hành trình là đường đi tới việc chính trong hoạt động đó.

Nhóm nào không dùng màn này trực tiếp (vd khách không thấy trang quản trị) vẫn ghi một dòng với "không dùng trực tiếp" và việc của họ bị ảnh hưởng thế nào (vd "được gọi lại đúng người, đúng lúc") — nhu cầu của họ đi vào màn qua người trong nhà.

| Ai | Từ đâu | Thiết bị | Việc chính | Số bước tới việc chính |
|---|---|---|---|---|
| Khách mới | link Zalo / quảng cáo / tìm kiếm | điện thoại 390px | … | hiện tại n · mục tiêu m |
| Khách cũ | email nhắc / lưu trang | … | … | … |
| Tư vấn viên | trang quản trị, mỗi sáng | điện thoại + máy tính | … | … |
| Vận hành | trang quản trị, cuối tuần | máy tính 1440px | … | … |

- Một bước = một lần bấm, gõ hoặc cuộn qua hết một màn. Đếm trên đường thật, không trên sơ đồ.
- "Từ đâu" quyết định khung đầu: vào thẳng từ link thì màn đó phải tự nói đây là đâu (NL-1).

## 2. Việc chính từng màn

| Màn | Đến để làm gì | So sánh bằng gì | Hành động cuối |
|---|---|---|---|
| … | một câu, một việc | con số, mốc, hình người dùng dùng để quyết | một nút / một kết quả |

- Mỗi màn đúng một việc chính và một hành động chính (đo bằng `primary-cta`, `main-task-first-view` ở `references/standards.md`).
- "So sánh bằng gì" là thứ phải nổi nhất trên màn: giá, lịch, số chưa gọi, trạng thái.

## 3. Câu hỏi theo bảy giai đoạn hành động

Hỏi cho từng màn, từng nhóm người dùng. Cột cuối là nhu cầu thầm kín hay gặp — người ta ít khi tự nói ra.

| Giai đoạn | Phía | Câu hỏi | Nhu cầu thầm kín cần soi |
|---|---|---|---|
| Muốn gì | mục tiêu | Họ tới đây để xong việc gì? Xong thì họ đi đâu? | Lười cuộn: muốn bấm một cái là xem video, là thấy giá |
| Làm được gì | thực hiện | Họ thấy những lựa chọn nào trong khung đầu? Có lựa chọn nào thừa? | Biết ngay nút nào cần bấm |
| Làm thế nào | thực hiện | Cái nổi bật nhất có đúng là việc chính không? | Cái nổi bật nhất giữa một đống thứ cùng nổi |
| Làm ra sao | thực hiện | Họ phải gõ gì? Hệ đã biết gì mà vẫn bắt gõ? | Điền rồi thì lần sau không phải điền lại |
| Vừa xảy ra gì | đánh giá | Bấm xong thấy gì trong 0,1 giây? Việc lâu thấy gì? | Không phải bấm lại vì tưởng chưa nhận |
| Nghĩa là gì | đánh giá | Thông báo có nói với cái gì, trạng thái mới là gì? | Không phải đoán "đã gửi chưa, ai nhận" |
| Đã đạt chưa | đánh giá | Họ biết xong chưa, tiếp theo là gì, khi nào? | Có bằng chứng giữ lại được (mã, lịch, tin nhắn) |

## 4. Câu hỏi cho người trong nhà

Tư vấn viên và vận hành dùng màn quản trị hàng trăm lần mỗi ngày; mỗi giây thừa nhân lên rất lớn.

- Tìm một khách bằng 4 số cuối SĐT được không, có cần gõ đủ số hay đúng dấu?
- Gọi, nhắn Zalo, copy số có bấm một lần là xong không, hay phải mở chi tiết rồi chọn chữ?
- Lead trùng hoặc bị cách ly có thấy ngay trên danh sách không, có ghi vì sao không?
- Xuất CSV có đúng những cột họ dán vào nơi khác, đúng thứ tự, mở bằng Excel không vỡ dấu không?
- Lọc "hôm nay chưa gọi" có một chạm không, có nhớ bộ lọc khi quay lại không?
- Trên điện thoại, việc chính của họ (gọi khách tiếp theo) có nằm trong khung đầu không?
- Họ đánh dấu "đã gọi" thế nào, sai thì hoàn tác được không?

## 5. Dữ liệu bẩn — chặn, gợi ý sửa, cách ly

Mỗi luật chặn phải đi kèm một cặp **người thật không bị chặn**, và nói rõ xử lý bằng một trong ba cách: **chặn** (không cho gửi, nói cách sửa), **gợi ý sửa** (cho gửi, đề xuất sửa một chạm), **cách ly** (nhận nhưng tách riêng cho người trong nhà xem, có lý do).

| Dữ liệu bẩn | Đề xuất xử lý | Người thật không bị chặn |
|---|---|---|
| Bot điền form | cách ly; không báo cho bot biết | Người dùng tự điền của trình duyệt, gõ nhanh vẫn qua |
| Email đuôi `.con` | gợi ý sửa "Ý bạn là `.com`?" | `.co`, `.vn`, `.com.vn` không bị gợi ý sai |
| Tên miền `gmial.com` | gợi ý sửa sang `gmail.com` | Tên miền lạ hợp lệ (`example.com`) gửi được khi người giữ nguyên |
| SĐT `0123456789` | chặn, nói "số này chưa đúng, kiểm lại giúp" | `0901 234 567`, `+84 901 234 567`, `84901234567` được nhận và chuẩn hoá |
| Email `a@gmail.com` | gợi ý sửa; giữ nguyên thì cách ly | `lan.nguyen+test@example.com` (có `+`) qua bình thường |
| SĐT của người này, email của người kia | cách ly, ghi "SĐT trùng lead khác với email khác" | Hai người một nhà dùng chung SĐT: đánh dấu, không xoá |
| Gửi trùng nhiều lần | gộp, giữ lần mới nhất, ghi số lần | Người gửi lại để sửa thông tin: bản mới được giữ |

- Ngưỡng cụ thể (bao nhiêu giây thì coi là bot, giữ bao nhiêu ngày) là câu hỏi cho chủ sản phẩm, không tự đặt.
- Mọi lead cách ly phải hiện được cho người trong nhà kèm lý do (mục 4).

## 6. Dữ liệu khó tiếng Việt

Gắn vào AC (cột "Given") để màn được thử bằng dữ liệu thật của khách Việt, không bằng "John Doe".

| Loại | Giá trị mẫu | Soi gì |
|---|---|---|
| Tên dài 5 chữ có dấu | `Nguyễn Thị Ngọc Bích Trâm` | Xuống dòng, cắt chữ, ô hẹp |
| Chữ HOA có dấu chồng | `NGUYỄN THỊ HỒNG HẠNH` | Dấu bị cắt mất phía trên |
| Chữ dạng tổ hợp (NFD) | `Nguyễn` gõ từ máy Mac/tệp cũ | Tìm `Nguyễn` dạng dựng sẵn vẫn khớp |
| Tìm không dấu | `nguyen` | Có khớp `Nguyễn` không — hỏi chủ, khuyến nghị có |
| SĐT nhiều dạng | `0901 234 567` · `+84 901 234 567` · `0901234567` | Nhận cả ba, lưu một dạng, tìm 4 số cuối `4567` |
| Email có `+` | `lan.nguyen+test@example.com` | Không bị báo sai |
| Tiền | `1.284.500 ₫` | Dấu chấm ngăn nghìn, ký hiệu sau số, không vỡ dòng |
| Số lớn | `12.480.000.000 ₫` · `128.456 học viên` | Cột không tràn, không thành `1.2e10` |
| Ngày | `05/03/2026` là 5 tháng 3 | dd/mm/yyyy ở mọi nơi, kể cả file xuất |
| Danh sách rỗng | 0 dòng | Có câu nói vì sao rỗng và việc tiếp theo |
| Một dòng / đúng trang | 1 dòng · 25 dòng · 26 dòng | Phân trang và "Hiển thị x–y / n" đúng ở biên |

## 7. Kéo mẫu chuẩn

Khối nào khớp một trong tám mẫu (`data-table`, `toolbar`, `form`, `overlay`, `mobile-header`, `lesson-video`, `slide`, `image`): mở hợp đồng mẫu theo tên trong `references/patterns-app-web.md`, `references/patterns-web.md` hoặc `references/surfaces.md`.

- **Bắt buộc có** → mỗi phần thành một AC hành vi, hoặc ghi rõ phần nào người dùng bỏ và vì sao.
- **Hỏi chủ sản phẩm** → thành câu hỏi kèm khuyến nghị và một ví dụ, không tự thành AC. Ví dụ dạng:

> Hỏi: Khách cũ mở lại form có điền sẵn tên, SĐT, email không? Khuyến nghị: có, kèm nút "Không phải bạn? Xoá" — vì khách quay lại không phải gõ lại 3 ô; đổi lại máy dùng chung sẽ lộ thông tin, nên có nút xoá.

- Chủ trả lời thì ghi câu trả lời vào `ux-needs.md`; lúc đó mới viết AC tương ứng.
- Chủ nói "cứ làm theo mặc định" → chọn khuyến nghị, ghi "giả định" kèm ngày; **trừ** câu chạm tiền, quyền truy cập, dữ liệu cá nhân hay dịch vụ bên ngoài — các câu đó để `chờ`, không viết AC, nhắc lại ở cuối lượt.

## 8. Khuôn AC

```
AC-n: Given <ai> <dữ liệu / trạng thái, có số> When <làm gì, ở khổ nào> Then <thấy gì / hệ làm gì, có số>
```

- AC mang **số hành vi**: số ngày, số bước, số lần bấm, số dòng, số ô điền sẵn, khổ màn (320, 390, 768, 1440), dữ liệu khó ở mục 6.
- **Số hình thức** (cỡ chữ, vùng chạm, màu, tương phản, nằm một hàng) không vào AC; chúng vào `## Luật đo` của `DESIGN.md` qua mode `system` (ranh giới ADR-31).
- Từ cấm trong AC: "dễ dùng", "thân thiện", "đẹp", "trực quan", "hiện đại", và mọi cỡ px của chữ hay nút. Gặp thì hỏi lại: "dễ dùng nghĩa là làm được gì, trong mấy bước?"
- Mỗi AC thử được bằng cách làm theo trên màn thật; không thử được thì chưa phải AC.

## 9. Ca mẫu (dữ liệu giả)

### Ca 1: form đăng ký học "Nấu ăn tại gia"

| Ai | Từ đâu | Thiết bị | Việc chính | Số bước |
|---|---|---|---|---|
| Khách mới | link Zalo của chị Lan | điện thoại 390px | xem bài thử rồi đăng ký | hiện tại 6 · mục tiêu 3 |
| Khách cũ | email nhắc khoá mới | điện thoại 390px | đăng ký lại không gõ lại | mục tiêu 2 |
| Tư vấn viên | trang quản trị | điện thoại | gọi khách vừa đăng ký | mục tiêu 2 |

| Màn | Đến để làm gì | So sánh bằng gì | Hành động cuối |
|---|---|---|---|
| Trang khoá | quyết có học không | video bài thử, học phí `1.284.500 ₫`, lịch | "Đăng ký" |
| Form | gửi thông tin | 3 ô, biết ai sẽ gọi lại | "Gửi đăng ký" |
| Xong | biết bước tiếp | thời gian gọi lại, mã đăng ký | lưu / mở Zalo |

AC nháp:
- AC-1: Given khách mở trang khoá ở 390px When chưa cuộn Then thấy tên khoá, học phí và nút xem bài thử; bấm 1 lần là video phát.
- AC-2: Given khách đã đăng ký trong 30 ngày When mở lại form ở 390px Then 3 ô đã điền sẵn, có nút "Không phải bạn? Xoá".
- AC-3: Given khách gõ SĐT `+84 901 234 567` và email `lan.nguyen+test@example.com` When bấm "Gửi đăng ký" Then đăng ký được nhận, SĐT lưu dạng `0901234567`.
- AC-4: Given khách gõ email `lan@gmial.com` When rời ô email Then thấy gợi ý `lan@gmail.com`, nhận gợi ý bằng 1 lần bấm; giữ nguyên vẫn gửi được.
- AC-5: Given khách bấm "Gửi đăng ký" 3 lần liên tiếp When mạng chậm Then chỉ 1 đăng ký được tạo và nút báo đang gửi từ lần bấm đầu.
- AC-6: Given đăng ký thành công When màn xong hiện Then có mã đăng ký, thời gian tư vấn gọi lại và nút mở Zalo.

Câu hỏi chủ sản phẩm: có dùng dịch vụ chống bot bên ngoài không (khuyến nghị: chưa, dùng ô bẫy và cách ly trước — không thêm bước cho khách); có che giao diện của trình phát video bên thứ ba không (khuyến nghị: không che nút phát và tua).

### Ca 2: trang quản trị danh sách học viên

| Ai | Từ đâu | Thiết bị | Việc chính | Số bước |
|---|---|---|---|---|
| Tư vấn viên | mở trang mỗi sáng | điện thoại 390px | gọi người chưa gọi hôm nay | mục tiêu 2 |
| Vận hành | cuối tuần | máy tính 1440px | xuất danh sách cho lớp mới | mục tiêu 3 |

| Màn | Đến để làm gì | So sánh bằng gì | Hành động cuối |
|---|---|---|---|
| Danh sách | tìm và gọi | số chưa gọi hôm nay, trạng thái | gọi / Zalo / copy |
| Lead cách ly | duyệt lead nghi ngờ | lý do cách ly | nhận / bỏ |

AC nháp (phần **Bắt buộc có** của mẫu `data-table`):
- AC-1: Given 128.456 học viên When gõ `4567` vào ô tìm Then chỉ còn các dòng có SĐT kết thúc bằng `4567`.
- AC-2: Given danh sách When bấm tiêu đề cột "Ngày đăng ký" Then sắp theo ngày dd/mm/yyyy, bấm lần 2 đảo chiều.
- AC-3: Given 26 dòng khớp và 25 dòng mỗi trang When xem trang 2 Then thấy "Hiển thị 26–26 / 26" và nút về trang 1.
- AC-4: Given người dùng chọn 50 dòng mỗi trang When tải lại trang Then vẫn 50 dòng mỗi trang.
- AC-5: Given bộ lọc "Hôm nay chưa gọi" không khớp ai When áp lọc Then thấy câu "Hôm nay đã gọi hết" và nút bỏ lọc.
- AC-6: Given tư vấn viên ở 390px When chạm biểu tượng gọi trên dòng `Nguyễn Thị Ngọc Bích Trâm` Then điện thoại mở cuộc gọi tới đúng số đó sau 1 chạm.
- AC-7: Given lead bị cách ly vì "SĐT trùng lead khác với email khác" When mở danh sách Then dòng đó mang nhãn cách ly và đọc được lý do không cần mở chi tiết.
- AC-8: Given vận hành bấm "Xuất CSV" When mở tệp bằng Excel Then tên có dấu không vỡ, ngày dạng dd/mm/yyyy, cột đúng thứ tự đã chốt.

## Đầu ra

- Hành trình, bảng việc chính, câu hỏi và câu trả lời ghi vào `<specs_dir>/changes/<slug>/ux-needs.md` theo khuôn `assets/ux-needs.md`.
- AC nháp chuyển vào proposal qua mk-specs; proposal chỉ nhận AC, không nhận bảng.
- Câu hỏi chưa có câu trả lời giữ nguyên trong `ux-needs.md`, không biến thành AC.
