# Nguyên lý (tầng 0–1)

File này trả lời "vì sao" và "cái gì": phục vụ ai, và mười lăm nguyên lý để phục vụ. Ngưỡng đo nằm ở `references/standards.md`; cách sắp màn, khối, mẫu ở `references/structure.md`; cách lấy nhu cầu ở `references/needs.md`.

## 0. Mục đích

- Thiết kế để phục vụ con người, gồm hai nhóm: **khách** (người xem, người mua, người học) và **người trong nhà** (tư vấn, vận hành, quản trị). Người trong nhà dùng sản phẩm mỗi ngày, hàng trăm lần; bỏ quên họ là bỏ quên một nửa.
- Bắt đầu từ **hoạt động** (việc lớn người ta đang làm), rồi mới tới tác vụ và màn hình. Một màn tồn tại vì nó phục vụ một việc chính trong hoạt động đó (Norman, tr. 231–234).
- Thiết kế là giao tiếp: nhà thiết kế không đứng cạnh người dùng để giải thích, nên mọi thứ phải nói qua chính sản phẩm — màn hình, chữ, thông báo, email (Norman, tr. 31–32).
- Người dùng làm sai là do thiết kế chưa tốt, không phải do họ kém. Họ thường tự trách mình và im lặng, nên chỗ họ vấp là dữ liệu để sửa (Norman, tr. 61–66).

## Phép thử bao trùm

Ở mọi khung hình — màn hình, slide, khung video — người dùng tự trả lời được bảy câu theo bảy giai đoạn hành động: **muốn gì · làm được gì · làm thế nào · làm ra sao · vừa xảy ra gì · nghĩa là gì · đã đạt chưa** (Norman, tr. 41, 71). Ba câu đầu sau "muốn gì" là phía thực hiện, ba câu cuối là phía đánh giá.

Họ không phải dừng lại tự hỏi "cái này là gì". Tốt nhất là khung hình tự hiển nhiên; nếu thứ đó buộc phải mới hoặc phức tạp thì ít nhất nó tự giải thích được bằng bố cục, tên gọi và vài chữ (Krug, tr. 22, 28–29). Phức tạp vì việc thật sự phức tạp thì được; rối thì không (Norman, tr. 247).

## Mười lăm nguyên lý

Mỗi nguyên lý: một câu, phép thử nhìn là trả lời được, phẩm chất chính, nguồn, một ca giả.

### NL-1: Khám phá được
Từ bất kỳ màn nào, kể cả vào thẳng từ link ngoài, người dùng thấy ngay đây là đâu, đang ở trạng thái nào, làm được gì, ở đâu và bằng cách nào — nhờ dấu hiệu, ánh xạ, ràng buộc và mô hình, không nhờ trang hướng dẫn.
- Phép thử: che hết dòng hướng dẫn, người mới vẫn chỉ ra được hành động chính và trạng thái hiện tại trong 5 giây.
- Phẩm chất: dễ dùng
- Nguồn: Norman, tr. 3, 10, 72; Krug, tr. 69, 83–84
- Ca: trang khoá "Nấu ăn tại gia" mở từ tin nhắn Zalo chỉ có video và chữ, không có tên khoá, không có nút đăng ký trong khung đầu.

### NL-2: Phản hồi, báo trước, nhịp thời gian
Trước khi bấm, người dùng biết bấm sẽ ra gì; sau khi bấm, trong khoảng 0,1 giây có dấu hiệu nói rõ điều gì vừa xảy ra với cái gì; việc lâu có tiến độ và ước lượng thận trọng; thông báo được xếp hạng để cái quan trọng không chìm giữa cái vặt.
- Phép thử: xem ghi màn hình — mỗi lần bấm có thay đổi nhìn thấy ngay, việc trên 1 giây có tiến độ, nhãn nút nêu cả hành động lẫn đối tượng.
- Phẩm chất: dễ dùng
- Nguồn: Norman, tr. 23–25, 60–61, 71–72; Krug, tr. 81, 140–141
- Ca: chị Lan bấm "Gửi" form đặt bánh mì, nút không đổi gì trong 3 giây nên chị bấm thêm hai lần, tạo ba đơn.

### NL-3: Mô hình khái niệm và hình ảnh hệ thống
Màn hình, chữ, email, tin nhắn cùng kể một câu chuyện về cách hệ hoạt động, đủ để người dùng đoán trước kết quả; ngay vài giây đầu phải cho đúng bức tranh tổng thể, và người hiểu sai một chút vẫn làm xong việc.
- Phép thử: viết được một câu "hệ này hoạt động thế nào" chỉ từ những gì nhìn thấy, và cùng một thứ mang cùng một tên ở mọi nơi.
- Phẩm chất: hợp lý
- Nguồn: Norman, tr. 25–32; Krug, tr. 33–35, 89–90
- Ca: màn quản trị gọi là "Lead", email báo gọi là "Khách tiềm năng", file xuất ghi "Contact" — người vận hành tưởng ba loại khác nhau.

### NL-4: Dấu hiệu
Mọi thứ bấm, nhập, kéo được đều nhận ra bằng ít nhất hai tín hiệu nhìn thấy (vị trí, hình dạng, màu, viền, nhãn), không phụ thuộc rê chuột hay cử chỉ ẩn, và không có gì trông bấm được mà lại không bấm được.
- Phép thử: bỏ hết màu trang trí, các điều khiển vẫn nhận ra được; không có dòng chữ chỉ để giải thích cách dùng một điều khiển.
- Phẩm chất: dễ dùng
- Nguồn: Norman, tr. 13–19; Krug, tr. 46–48, 139–140
- Ca: nút "Xem video bài 1" là chữ xám không viền, người xem trên điện thoại không biết chạm vào đâu.

### NL-5: Ánh xạ
Điều khiển nằm ngay trên hoặc sát thứ nó tác động; chữ trên nút, link báo đúng nơi nó dẫn tới và trang đích mang đúng tên vừa bấm; hướng (trước/sau, tăng/giảm) theo quy ước của người dùng.
- Phép thử: hành động theo dòng nằm trên dòng đó; tiêu đề trang đích trùng chữ trên nút vừa bấm.
- Phẩm chất: dễ dùng
- Nguồn: Norman, tr. 20–22, 113–122; Krug, tr. 54, 80
- Ca: nút "Gọi" của học viên nằm ở thanh công cụ trên cùng, cách dòng đang chọn 600px, tư vấn viên gọi nhầm người.

### NL-6: Ràng buộc
Lựa chọn sai bị loại hoặc nhìn là biết sai từ trước khi chọn; thao tác nguy hiểm có chốt chặn vừa đủ; còn định dạng dữ liệu thì hệ tự chuẩn hoá, không bắt người nhập theo cách của máy.
- Phép thử: lựa chọn không hợp lệ đã ẩn hoặc mờ trước khi bấm; ô số điện thoại nhận cả dấu cách và `+84`.
- Phẩm chất: hợp lý
- Nguồn: Norman, tr. 123–145; Krug, tr. 72, 153
- Ca: form đặt bánh mì cho chọn ngày giao là hôm qua, rồi mới báo lỗi sau khi bấm "Gửi".

### NL-7: Thiết kế cho lỗi
Giả định lỗi sẽ xảy ra: thứ dễ nhầm thì làm khác hẳn và đặt xa nhau, chế độ hiện tại luôn nhìn thấy, giá trị lệch xa mức thường thì hỏi lại, sai thì quay lại được và có hoàn tác, bị gián đoạn thì quay về vẫn còn nguyên dữ liệu.
- Phép thử: nút xoá khác hẳn nút lưu và không đứng sát; sau khi xoá có "Hoàn tác"; thông báo lỗi giữ nguyên dữ liệu đã nhập.
- Phẩm chất: hợp lý
- Nguồn: Norman, tr. 170–179, 198–210; Krug, tr. 33, 155
- Ca: chị Lan gõ giá bánh `250000` thay vì `25000`, hệ lưu luôn không hỏi lại.

### NL-8: Lướt và gom nhóm
Người dùng lướt chứ không đọc, nên độ nổi tỷ lệ với độ quan trọng, thứ liên quan đứng gần và trông giống nhau, thứ thuộc nhau thì lồng nhau, và trang chia thành vùng gọi tên được.
- Phép thử: nheo mắt nhìn màn, chỉ ra được cái quan trọng nhất và đặt tên được từng vùng.
- Phẩm chất: gọn
- Nguồn: Krug, tr. 31–32, 44–46, 49–52; Norman, tr. 22, 175
- Ca: trang khoá học có năm khối cùng cỡ, cùng màu nền, khách không biết khối nào là giá và lịch học.

### NL-9: Tri thức ngoài thế giới
Đặt điều cần biết lên màn để không ai phải nhớ quá 3–5 mục hay một mã tuỳ ý; mỗi lựa chọn trả lời được ngay, không mơ hồ — ba bước dễ hơn một bước phải cân nhắc — và người thạo vẫn có lối tắt.
- Phép thử: thông tin cần ở bước sau vẫn còn trên màn, không chỉ hiện trong thông báo tự tắt; không bước nào bắt nhớ mã.
- Phẩm chất: dễ dùng
- Nguồn: Norman, tr. 94, 100, 110; Krug, tr. 54–55
- Ca: mã đơn bánh mì chỉ hiện 3 giây trong thông báo nổi, khách phải gọi điện hỏi lại.

### NL-10: Giếng thiện chí
Mỗi trở ngại rút bớt thiện chí và một trở ngại lớn có thể rút cạn, nên phải nói thẳng điều người dùng muốn biết, chỉ hỏi điều thật cần, giữ nguyên công sức họ đã bỏ ra, hướng dẫn thay vì trách, và xin lỗi khi không làm được.
- Phép thử: giá, phí, lịch nằm ở chỗ thấy được không cần hỏi; form không có ô nào bỏ đi mà việc vẫn chạy; lỗi nói cách sửa.
- Phẩm chất: tiện
- Nguồn: Krug, tr. 151–155; Norman, tr. 61–66
- Ca: form đăng ký "Nấu ăn tại gia" hỏi nghề nghiệp, ngày sinh, địa chỉ trước khi cho xem học phí.

### NL-11: Tiết kiệm không gian và chữ
Bỏ chữ chào hỏi, hướng dẫn thừa, tính năng không phục vụ hoạt động chính; nhưng không giấu dấu hiệu, trạng thái hay lời giải thích mà người mới cần chỉ để cho gọn.
- Phép thử: chỉ ra được lý do có mặt của từng khối; bỏ một khối thì việc chính không mất gì.
- Phẩm chất: gọn
- Nguồn: Krug, tr. 59–61, 92–93, 138; Norman, tr. 110, 247, 261–263
- Ca: khung đầu trên điện thoại là đoạn "Chào mừng bạn đến với..." bốn dòng, nút đăng ký nằm dưới màn thứ hai.

### NL-12: Quy ước và nhất quán
Theo quy ước người dùng đã quen và giữ một cách làm cho một việc ở mọi màn; chỉ phá khi cách mới rõ hơn hẳn và đổi đồng loạt; khi nhất quán làm mờ nghĩa thì chọn rõ ràng.
- Phép thử: cùng một thao tác có cùng hình thức và vị trí ở mọi màn; logo về trang chủ, tìm kiếm có ô và kính lúp.
- Phẩm chất: hợp lý
- Nguồn: Krug, tr. 36–44; Norman, tr. 128–129, 149–155
- Ca: danh sách học viên phân trang ở dưới, danh sách đơn hàng lại phân trang ở trên với nút khác kiểu.

### NL-13: Cảm xúc ba mức
Chăm cả ba mức — ấn tượng tức thì khi nhìn, kỳ vọng được đáp ứng khi dùng, và điều đọng lại sau đó — nhưng niềm vui chỉ là điểm cộng sau khi đã dùng được; đặc biệt đừng để người dùng bực ở bước kết thúc, vì đó là điều họ nhớ và kể lại.
- Phép thử: màn kết thúc, slide cuối, cảnh cuối video nói rõ đã xong gì và tiếp theo là gì.
- Phẩm chất: hợp gu
- Nguồn: Norman, tr. 49–56; Krug, tr. 121, 143, 154
- Ca: đăng ký khoá học xong chỉ hiện "Thành công", không nói khi nào học, học ở đâu, liên hệ ai.

### NL-14: Thiết kế bao gồm và tiếp cận
Thiết kế cho dải người thật chứ không cho người trung bình: trước hết bỏ chỗ làm mọi người bối rối, rồi bảo đảm phóng chữ được, tương phản đủ, nhãn cho ô nhập, tiêu đề đúng cấp, ảnh có mô tả, dùng được bằng bàn phím.
- Phép thử: phóng chữ 200% vẫn đọc và bấm được; mỗi ô nhập có nhãn nhìn thấy; Tab đi hết các điều khiển theo thứ tự hợp lý.
- Phẩm chất: dễ dùng
- Nguồn: Norman, tr. 243–247; Krug, tr. 156–163
- Ca: mẹ chị Lan 62 tuổi phóng chữ điện thoại lên, nút "Đặt bánh" bị chữ đè mất một nửa.

### NL-15: Thẳng thắn, không thao túng
Không dùng giao diện để đẩy người dùng làm điều họ không định làm: không giấu phí, không ô đồng ý tích sẵn, không nút từ chối viết kiểu làm người ta xấu hổ, không đếm ngược giả; mọi đánh đổi bất lợi cho người dùng là quyết định có chủ ý, ghi lý do.
- Phép thử: nút từ chối nhìn thấy và trung tính như nút đồng ý; tổng tiền ở bước cuối bằng tổng tiền đã thấy ở bước đầu.
- Phẩm chất: hợp lý
- Nguồn: Krug, tr. 152–154, 168–171; Norman, tr. 255–257
- Ca: trang "Nấu ăn tại gia" có đồng hồ "Còn 2 suất" chạy lại từ đầu mỗi lần tải trang.

## Quy luật nhận thức làm cơ sở

Không phải nguyên lý riêng; là bằng chứng phía sau các NL. Ngưỡng cụ thể nằm ở `references/standards.md`.

| Quy luật | Nghĩa với thiết kế | Bề mặt |
|---|---|---|
| Fitts (Fitts, 1954) | Đích xa và nhỏ thì chậm và trượt nhiều; nút chính to, gần ngón cái | `web`, `app-web`, `app` |
| Hick (Hick–Hyman) | Càng nhiều lựa chọn ngang hàng càng lâu quyết; gom và ẩn bớt lựa chọn phụ | mọi bề mặt |
| Trí nhớ làm việc 3–5 mục (Norman, tr. 92–94) | Không bắt nhớ từ màn này sang màn khác; mỗi nhóm ít mục | mọi bề mặt |
| Gestalt: gần, giống, khung chung (Norman, tr. 22) | Khoảng cách và khung nói thứ nào thuộc nhau | mọi bề mặt |
| Jakob (Nielsen) | Người dùng ở nơi khác phần lớn thời gian, nên mong mọi nơi chạy giống nhau | `web`, `app-web`, `app` |
| Tesler (bảo toàn độ phức tạp) | Phức tạp không biến mất; hệ gánh thay người dùng (chuẩn hoá SĐT, điền sẵn) | `web`, `app-web`, `app` |
| Thời gian đáp ứng 0,1 / 1 / 10 giây (Miller; Nielsen) | 0,1 s thấy tức thì; 1 s vẫn liền mạch; quá 10 s cần tiến độ, không thì bỏ đi | `web`, `app-web`, `app`, `video` |
| Thẩm mỹ – dễ dùng (Kurosu & Kashimura) | Thứ trông đẹp được cho là dễ dùng hơn, nên đẹp có thể che lỗi khi thử | mọi bề mặt |
| Đỉnh – kết (Kahneman; NN/g) | Người ta nhớ lúc căng nhất và lúc kết thúc, không nhớ trung bình | `web`, `app-web`, `slide`, `video` |
| von Restorff (cô lập) | Thứ khác biệt được nhớ; chỉ một thứ được khác biệt mỗi khung | mọi bề mặt |
| Ưu thế hình ảnh (Paivio) | Hình được nhớ hơn chữ; slide một ý một hình | `slide`, `image`, `video` |
| Mẫu chữ F, mù banner (NN/g) | Mắt quét đầu dòng và đầu trang; thứ trông như quảng cáo bị bỏ qua | `web`, `app-web` |

## Sáu phẩm chất — thứ tự giải xung đột

Khi hai phẩm chất kéo hai hướng, cái đứng trước thắng. Đây là thứ tự **giải xung đột**, không phải thứ tự **bỏ qua**: sản phẩm tốt có đủ cả sáu.

| # | Phẩm chất | Câu kiểm |
|---|---|---|
| 1 | hợp lý | Đúng việc, đúng người, đúng dữ liệu, không lừa — có ai bị dẫn sai không? |
| 2 | dễ dùng | Người mới tự làm được việc chính lần đầu, không ai chỉ — có không? |
| 3 | tiện | Người dùng lần thứ mười có phải làm lại, gõ lại, cuộn tìm cái đã biết không? |
| 4 | gọn | Có khối, chữ, nút nào bỏ đi mà việc chính không mất gì không? |
| 5 | hợp gu | Có khớp `## Gu đã chốt` và tính cách sản phẩm, khớp các màn còn lại không? |
| 6 | đẹp | Ấn tượng một giây đầu hài hoà, chỉn chu, hay chói và cẩu thả? |

Ví dụ: nút xoá nền mờ trông đẹp hơn nhưng khó nhận ra → dễ dùng thắng đẹp. Đẹp và gu vẫn phải làm, chỉ không được trả bằng dễ dùng.

## Ba hạng phát hiện

| Hạng | Khi nào | Ví dụ |
|---|---|---|
| hỏng | Người dùng không làm được, làm sai, hoặc trượt một luật đo; vi phạm phép thử của một NL | Ô nhập bị bàn phím che, không bấm "Gửi" được |
| lệch hệ | Làm được nhưng khác `## Luật đo`, `## Mẫu`, `## Gu đã chốt` hoặc khác các màn khác của cùng sản phẩm | Một danh sách phân trang khác kiểu mọi danh sách còn lại |
| gu | Không ai bị chặn, không lệch hệ; chỉ là lựa chọn thẩm mỹ cần chủ sản phẩm chốt | Bo góc nút 6 hay 10 |

Hạng `gu` không sửa tự động: chủ sản phẩm chọn, rồi ghi vào `## Gu đã chốt` để lần sau thành chuẩn.
