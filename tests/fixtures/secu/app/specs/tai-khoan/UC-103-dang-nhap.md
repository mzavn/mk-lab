# UC-103: Đăng nhập
- Status: active
- BR: BR-01
- Owner: chủ tiệm (Mây)
- Actor: P1 (khách), P2 (nhân viên)
- Trigger: người dùng gửi email và mật khẩu

## History
- v1 (2026-10-20): khởi tạo

## Main Flow
1. Người dùng nhập email và mật khẩu.
   - Kỹ thuật: `POST /dang-nhap`
2. Hệ thống kiểm mật khẩu, mở phiên 7 ngày.

## Acceptance Criteria

### AC-1: Đăng nhập đúng
- Given khách An, email an@example.com, mật khẩu đúng
- When An đăng nhập
- Then An vào được, phiên còn hiệu lực 7 ngày
- Tests: ⚠ Chưa có test

### AC-2: Sai thì báo chung
- Given email không có hoặc mật khẩu sai
- When đăng nhập
- Then báo cùng một câu "email hoặc mật khẩu không đúng"; KHÔNG cho biết email có tồn tại hay không
- Tests: ⚠ Chưa có test

### AC-3: Khoá tạm sau 5 lần sai
- Given email an@example.com đã bị nhập sai mật khẩu 5 lần liên tiếp trong 15 phút
- When có người thử đăng nhập lần thứ 6 bằng email đó
- Then bị từ chối trong 15 phút, kể cả khi mật khẩu đúng
- Tests: ⚠ Chưa có test
