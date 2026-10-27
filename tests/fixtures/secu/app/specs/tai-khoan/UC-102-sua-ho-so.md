# UC-102: Sửa hồ sơ
- Status: active
- BR: BR-01
- Owner: chủ tiệm (Mây)
- Actor: P1 (khách)
- Trigger: khách mở trang "Hồ sơ"

## History
- v1 (2026-10-20): khởi tạo

## Preconditions
- Khách đã đăng nhập (UC-103).

## Main Flow
1. Khách đổi tên hiển thị và số điện thoại.
   - Kỹ thuật: `POST /ho-so`
2. Khách dán đường link một ảnh trên mạng để làm ảnh đại diện; hệ thống lấy ảnh về và lưu.
   - Kỹ thuật: `POST /ho-so/anh`
3. Khách xem lại ảnh đại diện.
   - Kỹ thuật: `GET /ho-so/anh`

## Acceptance Criteria

### AC-1: Đổi tên và số điện thoại
- Given khách An tên "An", số 0901234567
- When An đổi tên thành "An Nguyễn", số 0912345678
- Then hồ sơ hiện tên và số mới
- Tests: ⚠ Chưa có test

### AC-2: Số điện thoại sai định dạng
- Given khách An
- When An nhập số "12345"
- Then báo "số điện thoại không hợp lệ"; KHÔNG đổi gì trong hồ sơ
- Tests: ⚠ Chưa có test

### AC-3: Đặt ảnh đại diện từ đường link
- Given link `https://anh.example/banh.jpg` trỏ tới một ảnh 50 KB
- When An đặt link đó làm ảnh đại diện
- Then ảnh hiện ở hồ sơ của An
- Tests: ⚠ Chưa có test
