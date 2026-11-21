# Lỗi máy hay làm — và người thật gặp gì

Danh mục này gom những mặc định mà máy (agent viết code, bộ khung giao diện có sẵn) hay chọn, đặt cạnh điều người thật làm và cảm thấy. Mỗi mục có:

- **Máy làm**: thói quen sinh ra lỗi.
- **Người thực tế**: điều xảy ra với người dùng, kèm nguồn: trang sách, hoặc ca thật đã ẩn danh từ hai dự án ("dự án funnel" bán khoá học, "dự án app thói quen").
- **Nguyên lý**: `NL-n` trong `references/principles.md`. **Bắt bằng**: mã đo trong `references/standards.md`, hoặc `kiểm tay`.
- **Mặc định tốt hơn**: điều nên làm ngay từ đầu.

Dùng thế nào: khi soi (`references/audit.md`), phát hiện trùng một mục ở đây thì ghi `- Mã: AI-n`; `ux.py check` từ chối mã `AI-n` không có trong file này. Khi cùng một `AI-n` xuất hiện ở ≥ 2 báo cáo, nó thành đề xuất cho `## Bài học` hoặc `## Luật đo` (`references/structure.md`). Khi viết hay duyệt code, đọc lướt danh mục như danh sách kiểm trước khi giao.

### AI-1: Ô nhập chữ nhỏ hơn 16px
- Máy làm: dùng cỡ chữ "nhỏ" mặc định của bộ khung cho mọi ô nhập, thường 14px hoặc nhỏ hơn.
- Người thực tế: chạm vào ô trên iPhone là cả trang phóng to và không tự thu lại; ở dự án app thói quen chủ sản phẩm tả là "focus khi viết, khó chịu".
- Nguyên lý: NL-14 · Bắt bằng: `input-size`
- Mặc định tốt hơn: mọi ô nhập, ô chọn, ô văn bản 16px ở mọi khổ.

### AI-2: Khoá phóng to để chữa phóng to
- Máy làm: sửa AI-1 bằng cách cấm phóng to trong thẻ `viewport`.
- Người thực tế: người mắt kém mất cách duy nhất để đọc; dự án funnel chủ ý không khoá vì lý do này (Krug, tr. 138; Norman, tr. 246).
- Nguyên lý: NL-14 · Bắt bằng: kiểm tay (đọc thẻ viewport)
- Mặc định tốt hơn: chữa gốc bằng ô 16px; khoá phóng to chỉ khi chủ sản phẩm chốt và ghi vào `## Gu đã chốt`.

### AI-3: Vùng chạm nhỏ theo cỡ biểu tượng
- Máy làm: nút đóng, nút menu chỉ to bằng biểu tượng 20–28px cộng chút đệm.
- Người thực tế: ngón tay chạm trượt, bấm nhầm nút bên cạnh; dự án funnel có nút đóng hộp thoại 28px trước khi sửa.
- Nguyên lý: NL-7, NL-14 · Bắt bằng: `tap-target`
- Mặc định tốt hơn: khung bấm 44×44 bằng kích thước tối thiểu, biểu tượng bên trong vẫn 20px.

### AI-4: Chữ màu trang trí, tương phản thấp
- Máy làm: lấy màu thương hiệu (cam, vàng, xanh lá tươi) tô cho chữ trạng thái hay chữ phụ.
- Người thực tế: chữ cam trên nền trắng chỉ khoảng 2:1, ngoài nắng gần như biến mất; chữ nhỏ cộng tương phản thấp là cặp tệ nhất (Krug, tr. 172).
- Nguyên lý: NL-14 · Bắt bằng: `contrast`, `contrast-large`
- Mặc định tốt hơn: màu trang trí cho viền, chấm, nền; chữ dùng màu đậm đã qua `ux.py contrast`.

### AI-5: Chữ gợi ý thay cho nhãn
- Máy làm: bỏ nhãn, ghi "Họ tên" mờ trong ô cho gọn.
- Người thực tế: gõ được hai chữ là quên ô này hỏi gì; chữ mờ dễ tưởng là đã điền (Krug, tr. 172).
- Nguyên lý: NL-9, NL-14 · Bắt bằng: `pattern-form`
- Mặc định tốt hơn: nhãn thật nằm trên ô; chữ gợi ý chỉ là ví dụ ("0901 234 567").

### AI-6: Nhiều nút chính cùng lúc
- Máy làm: mỗi lời kêu gọi đều "nổi bật": nút đặc màu ở hero, ở thẻ giá, ở thanh dính đáy, cùng lúc trên màn.
- Người thực tế: phải tự đoán nút nào là việc chính; dự án funnel chốt chỉ một nút chính tại mỗi vị trí cuộn, thanh dính đáy chỉ hiện khi nút hero đã khuất.
- Nguyên lý: NL-8 · Bắt bằng: `primary-cta`
- Mặc định tốt hơn: một nút chính mỗi khung nhìn; nút còn lại là nút phụ.

### AI-7: Video nằm dưới chữ
- Máy làm: xếp màn học theo thứ tự dữ liệu: tiêu đề, mô tả dài, rồi mới tới video.
- Người thực tế: người mở màn học để xem video, phải cuộn tìm; dự án funnel đổi thành video → tên bài → nội dung, thanh Trước/Tiếp neo đáy.
- Nguyên lý: NL-1 · Bắt bằng: `main-task-first-view` (khi video được đánh dấu là việc chính); phần còn lại của mẫu video bài học kiểm tay
- Mặc định tốt hơn: việc chính của màn nằm trong khung nhìn đầu ở điện thoại.

### AI-8: Nhãn tiếng Anh, tên bảng dữ liệu
- Máy làm: lấy tên trong code làm nhãn: "Dashboard", "Export CSV", "Funnel", "Lead", "Default".
- Người thực tế: tên lạ tạo dấu hỏi, người phải dừng đoán (Krug, tr. 26); dự án funnel phải lập từ điển chữ cấm và đổi hết sang tiếng Việt.
- Nguyên lý: NL-3, NL-12 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: gọi theo việc người làm ("Trang bán khoá", "Người đăng ký"); giữ tiếng Anh chỉ khi người dùng vẫn nói vậy (email, OTP).

### AI-9: Hàm tải dữ liệu nuốt lỗi thành rỗng giả
- Máy làm: viết `catch` trả danh sách rỗng hoặc `null` cho gọn.
- Người thực tế: mất mạng mà màn hiện "chưa có khoá học" hay "không tìm thấy"; ở dự án funnel người học tưởng khoá đã bị gỡ.
- Nguyên lý: NL-2, NL-15 · Bắt bằng: kiểm tay (cắt API rồi mở màn)
- Mặc định tốt hơn: chỉ "không có" thật mới là rỗng; lỗi khác hiện "Chưa tải được trang" và nút "Tải lại".

### AI-10: Hiện nguyên thẻ HTML như chữ
- Máy làm: in thẳng mô tả do trình soạn thảo lưu dạng HTML vào thẻ khoá học, thẻ meta.
- Người thực tế: khách thấy "<p>Học nấu…</p>" và nghĩ trang hỏng; ca thật ở dự án funnel.
- Nguyên lý: NL-13 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: một hàm chung đổi HTML sang chữ thường (bỏ thẻ, giải mã ký tự) cho mọi chỗ hiện tóm tắt.

### AI-11: Thanh điều khiển xuống hai hàng ở điện thoại
- Máy làm: cho phép xuống dòng tự do với thanh phân trang, thanh lọc, đầu trang.
- Người thực tế: ở 320–390px thanh thành hai hàng, ăn mất chiều cao; chủ dự án app thói quen gửi ảnh và yêu cầu "một hàng thôi".
- Nguyên lý: NL-11 · Bắt bằng: `one-row`
- Mặc định tốt hơn: một hàng; rút gọn chữ dưới khổ nhỏ ("1–5 / 15" thay câu đầy đủ), giữ vùng chạm.

### AI-12: Lớp nổi không cuộn được
- Máy làm: đặt tấm trượt hay hộp thoại cao bằng màn, không có vùng cuộn.
- Người thực tế: nội dung cao hơn màn thì phần cuối và nút lưu không với tới; ca thật ở dự án app thói quen, chủ phát hiện trên iPhone.
- Nguyên lý: NL-7 · Bắt bằng: `pattern-overlay` (đầu, hàng nút) và kiểm tay cuộn ở 390px
- Mặc định tốt hơn: đầu và hàng nút luôn thấy, chỉ thân cuộn; chừa vùng an toàn đáy màn.

### AI-13: Dải chip cuộn ngang
- Máy làm: xếp chip danh mục trong một hàng cuộn ngang để gọn.
- Người thực tế: chip ngoài mép không ai thấy, không ai biết phải vuốt (Krug, tr. 139–140).
- Nguyên lý: NL-1, NL-4 · Bắt bằng: kiểm tay (`overflow-x` không bắt cuộn bên trong khối)
- Mặc định tốt hơn: chip xuống dòng, thấy đủ; quá nhiều chip thì là bộ lọc khác, không phải dải dài hơn.

### AI-14: Nút gửi bấm được rồi mới báo lỗi
- Máy làm: để gửi tự do, kiểm sau, rồi bật thông báo nổi "Vui lòng nhập…".
- Người thực tế: thông báo biến mất trước khi kịp tìm ô sai; cả hai dự án đều sửa lỗi này.
- Nguyên lý: NL-6, NL-7 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: kiểm từng ô khi rời ô, lỗi nằm dưới đúng ô, cùng câu với máy chủ; bấm gửi khi còn sai thì đưa con trỏ về ô sai đầu tiên.

### AI-15: Báo lỗi mà không có bước tiếp
- Máy làm: "Tài khoản không hoạt động", "Đã xảy ra lỗi".
- Người thực tế: người không biết làm gì và tự trách mình (Norman, tr. 64–65); dự án app thói quen đổi thành câu kèm nút "Đăng ký" hay "Quên mật khẩu" điền sẵn email.
- Nguyên lý: NL-7, NL-10 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: nói chuyện gì xảy ra với cái gì, và một nút sửa ngay, giữ nguyên dữ liệu đã nhập.

### AI-16: Hai phần dính cùng tầng chồng nhau
- Máy làm: đặt cột dính của bảng và đầu trang dính cùng một mức chồng lớp.
- Người thực tế: cuộn lên thì cột bảng đè lên đầu trang; ca thật ở dự án app thói quen.
- Nguyên lý: NL-12 · Bắt bằng: kiểm tay (cuộn ở khổ nhỏ)
- Mặc định tốt hơn: một thang chồng lớp chung trong `DESIGN.md`; phần dính nằm ngoài khung tự cuộn.

### AI-17: Cú pháp mới làm trắng trang trên máy cũ
- Máy làm: dùng biểu thức chính quy nhìn lùi `(?<!…)` hay tính năng mới mà không xem trình duyệt hỗ trợ.
- Người thực tế: iPhone đời iOS cũ không đọc được cả tệp JS, trang trắng trơn; ca thật ở dự án app thói quen.
- Nguyên lý: NL-14 · Bắt bằng: kiểm tay (quét bản dựng, luật lint cấm cú pháp)
- Mặc định tốt hơn: liệt kê trình duyệt tối thiểu, chặn cú pháp vượt mức bằng lint.

### AI-18: Thành phần và hàm định dạng trùng lặp
- Máy làm: viết lại thẻ thống kê, hộp thoại, hàm định dạng ngày/tiền thay vì tìm cái có sẵn.
- Người thực tế: cùng một con số hiện hai kiểu ở hai màn; dự án funnel có hàng chục hàm định dạng lặp và năm kiểu hộp thoại.
- Nguyên lý: NL-12 · Bắt bằng: kiểm tay (review)
- Mặc định tốt hơn: một nguyên tố, một hàm; tìm trước khi viết (`references/structure.md`).

### AI-19: Bản cũ vẫn chạy sau khi triển khai
- Máy làm: coi triển khai xong là người dùng có bản mới.
- Người thực tế: tab mở từ hôm trước vẫn chạy mã cũ, bấm không ăn hoặc lỗi lạ; ca thật ở dự án funnel.
- Nguyên lý: NL-2 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: kiểm phiên bản khi mở trang và khi quay lại tab, tự tải lại, không cắt ngang lúc đang xem video.

### AI-20: Thêm tính năng, thêm lựa chọn
- Máy làm: thêm nút tìm, sắp xếp, phân trang vì "trang danh sách thì phải có", kể cả khi chưa chạy.
- Người thực tế: nút bấm không có tác dụng làm mất tin; mỗi lựa chọn thừa làm sản phẩm khó hiểu hơn (Norman, tr. 261–263).
- Nguyên lý: NL-11 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: chỉ hiện điều khiển đã chạy thật và phục vụ việc chính; thêm khi có nhu cầu đã ghi.

### AI-21: Lời chào và hướng dẫn dài
- Máy làm: mở trang bằng đoạn "Chào mừng bạn đến với…" và khối hướng dẫn sử dụng.
- Người thực tế: người quét, bỏ qua đoạn tự khen; hướng dẫn chỉ được đọc khi đã bí (Krug, tr. 59–61).
- Nguyên lý: NL-11 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: một câu nói sản phẩm khác gì; giao diện tự giải thích, gợi ý ngắn đặt ngay chỗ cần.

### AI-22: Dấu hiệu chỉ có khi rê chuột, nút phẳng như chữ
- Máy làm: tooltip, menu thả, đổi màu khi rê; nút không viền, không nền.
- Người thực tế: điện thoại không có rê chuột; người không biết chỗ nào bấm được (Krug, tr. 139–140; Norman, tr. 13–19).
- Nguyên lý: NL-4 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: thứ bấm được nhận ra bằng ít nhất hai dấu hiệu nhìn thấy (vị trí, hình, viền, màu).

### AI-23: Bắt người nhập đúng định dạng của máy
- Máy làm: cấm dấu cách trong số điện thoại, bắt ngày đúng một kiểu, báo lỗi sau khi gõ.
- Người thực tế: người bị "phạt" vì cách viết tự nhiên (Krug, tr. 153); máy nên tự hiểu các cách viết hợp lý (Norman, tr. 70–71).
- Nguyên lý: NL-6, NL-10 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: nhận "0901 234 567", "+84 901234567", tự chuẩn hoá bên trong.

### AI-24: Chặn nhầm người thật
- Máy làm: luật chống rác quá tay: chặn email có dấu `+`, tên ngắn, số có dấu cách.
- Người thực tế: khách thật bị từ chối và bỏ đi; dự án funnel chỉ chặn thứ không thể là thật, thứ đáng ngờ thì cách ly.
- Nguyên lý: NL-7, NL-10 · Bắt bằng: kiểm tay (cặp ca người thật trong AC, `references/needs.md`)
- Mặc định tốt hơn: mỗi luật chặn có ca "người thật không bị chặn" (`lan.nguyen+test@example.com`) và nói rõ chặn, gợi ý sửa hay cách ly.

### AI-25: Bấm xong không thấy gì đổi
- Máy làm: gửi yêu cầu rồi im lặng tới khi có phản hồi.
- Người thực tế: không thấy phản hồi thì người bấm lại, mạnh hơn, gây gửi đôi (Norman, tr. 23, 59).
- Nguyên lý: NL-2 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: thay đổi nhìn thấy ngay khi bấm, nút vào trạng thái đang gửi, rồi báo kết quả và trạng thái mới.

### AI-26: Thiếu trạng thái rỗng, đang tải, lỗi
- Máy làm: chỉ dựng màn với dữ liệu mẫu đầy đủ.
- Người thực tế: ngày đầu danh sách trống trơn không lời giải thích; mạng chậm thì màn trắng.
- Nguyên lý: NL-2, NL-3 · Bắt bằng: kiểm tay (bảng trạng thái ở `references/structure.md`)
- Mặc định tốt hơn: mỗi khối có dữ liệu đi qua đủ bảng trạng thái dùng chung trước khi giao.

### AI-27: Chế độ ẩn, cùng nút khác nghĩa
- Máy làm: một nút làm việc khác nhau tuỳ chế độ (xem/sửa, thật/thử) mà chế độ không hiện rõ.
- Người thực tế: người làm đúng thao tác nhưng sai chế độ, lỗi khó nhận ra (Norman, tr. 177–179).
- Nguyên lý: NL-7, NL-3 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: tránh chế độ; bắt buộc có thì chế độ hiện ở mọi điểm thao tác và khác biệt rõ.

### AI-28: Hỏi thông tin không cần
- Máy làm: form đăng ký đòi ngày sinh, địa chỉ, nghề nghiệp "cho đủ dữ liệu".
- Người thực tế: mỗi ô thừa rút bớt thiện chí, form dài có thể làm người bỏ đi ngay (Krug, tr. 151–153).
- Nguyên lý: NL-10 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: chỉ hỏi điều việc chính cần ngay bây giờ; hỏi thêm sau, khi có lý do người thấy được.

### AI-29: Mẫu tối thao túng
- Máy làm: ô đăng ký nhận tin tick sẵn, nút huỷ mờ nhạt, nhiều nút "Tải về" giả, đồng hồ đếm ngược bịa.
- Người thực tế: người làm điều không định làm, mất tin khi nhận ra (Krug, tr. 168–171).
- Nguyên lý: NL-15 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: lựa chọn mặc định có lợi cho người dùng; đường thoát rõ ngang đường vào; thuyết phục bằng thông tin thật.

### AI-30: Gián đoạn là mất dữ liệu đã gõ
- Máy làm: không lưu nháp; hết phiên hay chuyển tab là xoá form.
- Người thực tế: người bị gián đoạn liên tục, quay lại thì phải làm lại từ đầu (Norman, tr. 185–186, 199–201); dự án funnel giữ thông tin đã điền 30 ngày.
- Nguyên lý: NL-7, NL-9 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: giữ dữ liệu đã nhập qua lỗi, chuyển tab, tải lại; có lối xoá ("Không phải bạn? Xoá").

### AI-31: Viết hoa cả chữ cho nhãn tiếng Việt
- Máy làm: dùng `uppercase` cho huy hiệu, tiêu đề mục.
- Người thực tế: chữ hoa có dấu khó đọc, dài ra và xuống hai dòng ("ĐANG HỌC"); ca thật ở dự án funnel.
- Nguyên lý: NL-12, NL-14 · Bắt bằng: kiểm tay
- Mặc định tốt hơn: viết thường như câu; huy hiệu không xuống dòng.

### AI-32: Bỏ vòng sáng khi dùng phím Tab
- Máy làm: `outline: none` cho đẹp, không thay bằng gì.
- Người thực tế: người dùng bàn phím không biết mình đang ở đâu (Krug, tr. 162–163).
- Nguyên lý: NL-14 · Bắt bằng: kiểm tay (Tab qua cả trang)
- Mặc định tốt hơn: vòng sáng chung cho `:focus-visible`, đủ tương phản với nền.

### AI-33: Chữ đọc 14px trên điện thoại
- Máy làm: giữ cỡ chữ máy tính cho thân bài ở khổ nhỏ.
- Người thực tế: người cầm điện thoại xa mắt, phải nheo hoặc phóng to; dự án funnel nâng chữ đọc lên 16px.
- Nguyên lý: NL-14 · Bắt bằng: `body-text-mobile`, `text-min`
- Mặc định tốt hơn: chữ đọc 16px dưới 768px; chú thích nhỏ đánh dấu `data-text="caption"`.

### AI-34: Trang tràn ngang
- Máy làm: bảng rộng, ảnh cố định chiều rộng, chữ dài không ngắt.
- Người thực tế: cả trang lắc ngang khi cuộn, phần bên phải không ai thấy.
- Nguyên lý: NL-1 · Bắt bằng: `overflow-x`
- Mặc định tốt hơn: bảng cuộn trong khung riêng, ảnh co theo khung, chữ dài được ngắt.

### AI-35: Không có hoặc nhiều tiêu đề trang
- Máy làm: dùng thẻ chung chung cho tiêu đề, hoặc mỗi khối một `h1`.
- Người thực tế: trình đọc màn hình không tìm được tên trang; người nhìn không biết đâu là tiêu đề chính (Krug, tr. 78, 162).
- Nguyên lý: NL-8, NL-14 · Bắt bằng: `h1`
- Mặc định tốt hơn: đúng một `h1` mang tên trang, các cấp dưới theo thứ tự.

### AI-36: Bảng dữ liệu thiếu tìm và phân trang
- Máy làm: đổ hết dòng ra một bảng dài, không ô tìm, không "Hiển thị x–y / n".
- Người thực tế: người trong nhà mất thời gian cuộn tìm một học viên giữa vài trăm dòng.
- Nguyên lý: NL-12 · Bắt bằng: `pattern-data-table`
- Mặc định tốt hơn: theo mẫu `data-table` ở `references/patterns-app-web.md`; bỏ phần nào thì ghi lý do trong `## Mẫu`.
