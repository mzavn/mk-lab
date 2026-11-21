# Business Requirements

## BR-01: Công ty nhỏ tự quản lý dự án và hoá đơn trên một dịch vụ dùng chung
- Status: active
- Owner: chủ sản phẩm Sổ Việc (Hà)

### Vì sao
Các công ty dịch vụ nhỏ đang lập hoá đơn bằng bảng tính, sai số liệu sau khi đã chốt sổ và lộ dữ liệu khi gửi file qua
lại. Họ cần một chỗ dùng chung, mỗi công ty chỉ thấy dữ liệu của mình, có trợ lý làm hộ việc lặp lại.

### Personas
- P1 (chủ công ty): tạo công ty, mời và khoá thành viên, chốt kỳ.
- P2 (kế toán): phát hành, huỷ, ghi thu, hoàn tiền hoá đơn; xem báo cáo doanh thu.
- P3 (quản lý dự án): tạo dự án, đặt ngân sách, lập hoá đơn nháp.
- P4 (nhân viên): xem dự án, tạo dự án mới.
- P5 (khách của công ty): mở link chia sẻ để xem hoá đơn, không có tài khoản.
- P6 (cổng thanh toán): báo tiền đã về.

### In Scope
- Dự án, ngân sách, hoá đơn, kỳ kế toán, báo cáo theo kỳ và theo dự án.
- Thành viên, vai, đăng nhập, khoá thành viên.
- Trợ lý gọi tool trong quyền của người đang dùng.

### Out of Scope
- Kết nối hoá đơn điện tử của cơ quan thuế.
- Một người thuộc nhiều công ty.

### Related Use Cases
- UC-201, UC-202, UC-203, UC-204
