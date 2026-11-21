# UC-201: Hoá đơn và kỳ kế toán
- Status: active
- BR: BR-01
- Owner: chủ sản phẩm (Hà)
- Actor: P1 (chủ), P2 (kế toán), P3 (quản lý), P5 (khách), P6 (cổng thanh toán)
- Trigger: quản lý lập hoá đơn cho khách; kế toán xử lý hoá đơn; chủ chốt kỳ cuối tháng

## History
- v1 (2026-11-02): khởi tạo

## Preconditions
- Người dùng đã đăng nhập (UC-203), trừ khách mở link chia sẻ và cổng thanh toán.

## Main Flow
1. Quản lý lập hoá đơn nháp cho một dự án, kỳ đang mở, và sửa nháp.
   - Kỹ thuật: `POST /hoa-don`, `POST /hoa-don/sua`, xem `GET /hoa-don?ma=`
2. Kế toán phát hành, huỷ, khôi phục hoá đơn đã huỷ.
   - Kỹ thuật: `POST /hoa-don/phat-hanh`, `POST /hoa-don/huy`, `POST /hoa-don/khoi-phuc`
3. Kế toán gửi link chia sẻ cho khách; khách mở link xem hoá đơn.
   - Kỹ thuật: `POST /hoa-don/chia-se`, `GET /chia-se/hoa-don?khoa=&so_dong=&trang=`
4. Tiền về: cổng thanh toán báo về, hoặc kế toán ghi thu tay. Kế toán hoàn tiền khi cần.
   - Kỹ thuật: `POST /thanh-toan/bao`, `POST /hoa-don/ghi-thu`, `POST /hoa-don/hoan-tien`
5. Chủ chốt kỳ; kế toán xem báo cáo doanh thu theo kỳ.
   - Kỹ thuật: `POST /ky/chot`, `GET /bao-cao/doanh-thu?ky=`

## Acceptance Criteria

### AC-1: Lập và phát hành hoá đơn
- Given quản lý Minh của công ty Lam, dự án "Web Lam", kỳ 2026-11 đang mở
- When Minh lập nháp 2 dòng tổng 12 000 000 đ, kế toán Thu phát hành
- Then hoá đơn ở trạng thái đã phát hành, tính vào doanh thu 2026-11 của dự án "Web Lam"
- Tests: ⚠ Chưa có test

### AC-2: Không đụng được hoá đơn và báo cáo của công ty khác
- Given hoá đơn 501 thuộc công ty Lam; kế toán Quân thuộc công ty Đỏ
- When Quân đọc hay sửa hoá đơn 501, hay xem báo cáo doanh thu, báo cáo dự án, bằng bất kỳ đường nào
- Then Quân nhận "không tìm thấy" (404); KHÔNG thấy số liệu nào của công ty Lam
- Tests: ⚠ Chưa có test

### AC-3: Kỳ đã chốt không đổi số liệu
- Given kỳ 2026-10 của công ty Lam đã chốt; hoá đơn 480 (đã phát hành) và 481 (đã huỷ) thuộc kỳ đó
- When kế toán lập, sửa, phát hành, huỷ hay khôi phục hoá đơn của kỳ 2026-10, bằng bất kỳ đường nào
- Then nhận "kỳ đã chốt" (409); doanh thu 2026-10 không đổi
- Tests: ⚠ Chưa có test

### AC-4: Ghi thu ở kỳ đã chốt
- Given hoá đơn 480 đã phát hành, kỳ 2026-10 đã chốt
- When kế toán ghi thu hoặc cổng thanh toán báo đã thu hoá đơn 480
- Then hoá đơn 480 thành đã thu; doanh thu 2026-10 không đổi
- Tests: ⚠ Chưa có test

### AC-5: Phân quyền hoá đơn
- Given chủ, kế toán, quản lý, nhân viên của cùng công ty
- When mỗi người thử lập nháp, phát hành, huỷ, khôi phục, ghi thu, hoàn tiền, chia sẻ, xem báo cáo doanh thu
- Then quản lý chỉ lập và sửa nháp; chủ và kế toán làm được mọi việc; nhân viên bị từ chối "không có quyền" (403)
- Tests: ⚠ Chưa có test

### AC-6: Khách xem hoá đơn qua link
- Given hoá đơn 480 đã phát hành, kế toán tạo link chia sẻ
- When khách mở link (không đăng nhập)
- Then khách thấy tên khách, tổng tiền, trạng thái, các dòng của hoá đơn 480, không thấy hoá đơn nào khác; sau 30 ngày
  link trả "không tìm thấy"
- Tests: ⚠ Chưa có test

### AC-7: Cổng thanh toán báo về
- Given hoá đơn 480 đã phát hành 12 000 000 đ
- When cổng thanh toán gửi sự kiện đã thu có chữ ký đúng; gửi lại cùng mã sự kiện; một bên khác gửi chữ ký sai
- Then hoá đơn 480 thành đã thu và chỉ có một khoản thu; chữ ký sai nhận 401, không ghi gì
- Tests: ⚠ Chưa có test

### AC-8: Hoàn tiền không vượt số đã thu
- Given hoá đơn 480 đã thu 12 000 000 đ, đã hoàn 10 000 000 đ
- When kế toán hoàn thêm 3 000 000 đ
- Then bị từ chối "vượt số tiền đã thu" (409)
- Tests: ⚠ Chưa có test
