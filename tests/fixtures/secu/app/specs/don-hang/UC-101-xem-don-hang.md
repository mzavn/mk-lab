# UC-101: Xem đơn hàng
- Status: active
- BR: BR-01
- Owner: chủ tiệm (Mây)
- Actor: P1 (khách), P2 (nhân viên)
- Trigger: khách mở trang "Đơn của tôi"; nhân viên mở trang "Đơn cần làm"

## History
- v1 (2026-10-20): khởi tạo

## Preconditions
- Người dùng đã đăng nhập (UC-103).

## Main Flow
1. Khách xem danh sách đơn của mình, có thể tìm theo tên đơn.
   - Kỹ thuật: `GET /don?tim=`
2. Khách mở một đơn để xem tổng tiền, trạng thái và địa chỉ giao.
   - Kỹ thuật: `GET /don/xem?ma=`, trang in `GET /don/trang?ma=`
3. Khách xem lịch sử đơn theo trang, mới nhất trước.
   - Kỹ thuật: `GET /don/lich-su?trang=`

## Alternative Flows
- 1a. Nhân viên lọc mọi đơn theo trạng thái để làm bánh và giao.
  - Kỹ thuật: `GET /cua-hang/don?trang_thai=`

## Acceptance Criteria

### AC-1: Khách xem đơn của mình
- Given khách An có đơn 1001 "Bánh kem dâu", 350 000 đ
- When An mở đơn 1001
- Then An thấy tên đơn, tổng tiền, trạng thái và địa chỉ giao
- Tests: ⚠ Chưa có test

### AC-2: Khách không xem được đơn của người khác
- Given đơn 1002 thuộc khách Bình
- When An mở đơn 1002 bằng bất kỳ cách nào: xem chi tiết, trang in, danh sách, tìm kiếm, lịch sử
- Then An KHÔNG thấy bất kỳ thông tin nào của đơn 1002; nhận "không tìm thấy" như đơn không tồn tại
- Tests: ⚠ Chưa có test

### AC-3: Chưa đăng nhập thì không xem được đơn
- Given người chưa đăng nhập
- When mở danh sách hoặc một đơn
- Then nhận "cần đăng nhập"; KHÔNG thấy đơn nào
- Tests: ⚠ Chưa có test

### AC-4: Nhân viên xem mọi đơn theo trạng thái
- Given nhân viên Chi; khách An và Bình mỗi người có một đơn trạng thái `moi`
- When Chi lọc đơn `moi`
- Then Chi thấy cả hai đơn kèm địa chỉ giao; khách An làm cùng thao tác thì bị từ chối "không có quyền"
- Tests: ⚠ Chưa có test
