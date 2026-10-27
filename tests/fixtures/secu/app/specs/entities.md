# Entity

## Khách hàng (users)
- email: duy nhất, dùng để đăng nhập.
- tên hiển thị, số điện thoại: khách tự sửa.
- vai: `customer` hoặc `staff`; do chủ tiệm gán.
- điểm thưởng: tiệm cộng khi đơn hoàn tất.
- ảnh đại diện: ảnh khách chọn.

## Đơn hàng (orders)
- chủ đơn: một khách hàng.
- tên đơn, tổng tiền (đồng), trạng thái (`moi`, `dang-lam`, `da-giao`), địa chỉ giao, thời điểm tạo.
