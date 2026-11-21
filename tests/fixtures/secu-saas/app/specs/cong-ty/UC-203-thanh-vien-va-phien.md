# UC-203: Thành viên và phiên đăng nhập
- Status: active
- BR: BR-01
- Owner: chủ sản phẩm (Hà)
- Actor: P1 (chủ), mọi thành viên
- Trigger: thành viên đăng nhập; chủ quản lý người trong công ty

## History
- v1 (2026-11-02): khởi tạo

## Main Flow
1. Thành viên đăng nhập bằng email và mật khẩu, nhận token phiên 12 giờ.
   - Kỹ thuật: `POST /dang-nhap`; các yêu cầu sau gửi `Authorization: Bearer <token>`
2. Thành viên đổi mật khẩu.
   - Kỹ thuật: `POST /doi-mat-khau`
3. Thành viên xem hồ sơ của mình và danh sách thành viên công ty.
   - Kỹ thuật: `GET /toi`, `GET /thanh-vien`
4. Chủ đổi vai và khoá thành viên nghỉ việc.
   - Kỹ thuật: `POST /thanh-vien/vai`, `POST /thanh-vien/khoa`

## Acceptance Criteria

### AC-1: Đăng nhập
- Given thành viên Lan, email lan@lam.example, mật khẩu đúng
- When Lan đăng nhập
- Then Lan nhận token, dùng được 12 giờ
- Tests: ⚠ Chưa có test

### AC-2: Sai thì báo chung, sai nhiều thì khoá tạm
- Given email không có hoặc mật khẩu sai
- When đăng nhập; hoặc sai 5 lần liền với một tài khoản
- Then báo cùng một câu "email hoặc mật khẩu không đúng"; sau 5 lần sai tài khoản bị khoá tạm 15 phút
- Tests: ⚠ Chưa có test

### AC-3: Khoá thành viên có hiệu lực ngay
- Given Lan đang đăng nhập trên hai máy
- When chủ công ty khoá Lan
- Then yêu cầu kế tiếp của Lan trên cả hai máy nhận "cần đăng nhập" (401); Lan không đăng nhập lại được
- Tests: ⚠ Chưa có test

### AC-4: Đổi mật khẩu thu hồi phiên khác
- Given Lan đăng nhập trên máy A và máy B
- When Lan đổi mật khẩu trên máy A
- Then phiên máy B nhận "cần đăng nhập"; máy A vẫn dùng tiếp
- Tests: ⚠ Chưa có test

### AC-5: Danh sách thành viên
- Given công ty Lam có 4 thành viên
- When một thành viên mở danh sách thành viên
- Then thấy tên, email, vai và trạng thái khoá của từng người trong công ty Lam
- Tests: ⚠ Chưa có test

### AC-6: Chủ đổi vai
- Given Lan là nhân viên
- When chủ công ty đổi Lan thành quản lý; một quản lý thử đổi vai người khác
- Then Lan có quyền quản lý từ yêu cầu kế tiếp; quản lý bị từ chối "không có quyền" (403)
- Tests: ⚠ Chưa có test
