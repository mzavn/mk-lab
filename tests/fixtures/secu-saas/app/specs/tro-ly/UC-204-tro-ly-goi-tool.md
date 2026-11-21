# UC-204: Trợ lý gọi tool
- Status: active
- BR: BR-01
- Owner: chủ sản phẩm (Hà)
- Actor: mọi thành viên, trợ lý (model ngôn ngữ chạy ở dịch vụ trợ lý)
- Trigger: thành viên nhờ trợ lý trong khung chat

## History
- v1 (2026-11-02): khởi tạo

## Preconditions
- Thành viên đã đăng nhập (UC-203). Dịch vụ trợ lý gọi tool bằng token phiên của chính thành viên đó.

## Main Flow
1. Thành viên gõ yêu cầu; model chọn tool và điền tham số.
2. Dịch vụ trợ lý gọi tool.
   - Kỹ thuật: `POST /tro-ly/goi-tool` với `{"tool": ..., "args": {...}}`; tool: `tim_hoa_don`, `hoan_tien`, `doi_vai`
3. Với việc cần xác nhận, giao diện hiện màn hình xác nhận ngoài khung chat; thành viên đọc nội dung việc, nhập lại mật
   khẩu; giao diện nhận mã xác nhận và chuyển cho dịch vụ trợ lý.
   - Kỹ thuật: `POST /tro-ly/xac-nhan`

## Acceptance Criteria

### AC-1: Tool chạy trong quyền người dùng
- Given nhân viên Lan của công ty Lam
- When Lan nhờ trợ lý tìm hoá đơn của khách "Bắc"
- Then trợ lý chỉ trả hoá đơn của công ty Lam; tool ghi mà Lan không có quyền trên web thì bị từ chối như trên web
- Tests: ⚠ Chưa có test

### AC-2: Việc về tiền và quyền cần người dùng xác nhận
- Given kế toán Thu; hoá đơn 480 đã thu
- When model gọi tool hoàn tiền hay đổi vai, kể cả khi model tự điền tham số cho biết người dùng đã đồng ý
- Then việc chỉ chạy khi có mã xác nhận Thu vừa nhận ở màn hình xác nhận cho đúng việc và đúng nội dung đó; không có mã
  thì không hoàn tiền, không đổi vai
- Tests: ⚠ Chưa có test
