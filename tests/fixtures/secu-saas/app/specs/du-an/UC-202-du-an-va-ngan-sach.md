# UC-202: Dự án và ngân sách
- Status: active
- BR: BR-01
- Owner: chủ sản phẩm (Hà)
- Actor: P1 (chủ), P3 (quản lý), P4 (nhân viên)
- Trigger: công ty nhận việc mới; đầu quý điều chỉnh ngân sách

## History
- v1 (2026-11-02): khởi tạo

## Preconditions
- Người dùng đã đăng nhập (UC-203).

## Main Flow
1. Thành viên xem danh sách dự án của công ty.
   - Kỹ thuật: `GET /du-an`
2. Thành viên tạo dự án mới, hoặc sao chép một dự án có sẵn.
   - Kỹ thuật: `POST /du-an`, `POST /du-an/sao-chep`
3. Quản lý đặt ngân sách cho một dự án; đầu quý đặt ngân sách cho nhiều dự án một lượt.
   - Kỹ thuật: `POST /du-an/ngan-sach`, `POST /du-an/ngan-sach/hang-loat`
4. Quản lý lưu trữ dự án đã xong.
   - Kỹ thuật: `POST /du-an/luu-tru`
5. Thành viên xem các dòng hoá đơn đã phát hành của một dự án.
   - Kỹ thuật: `GET /bao-cao/du-an?du_an=`

## Acceptance Criteria

### AC-1: Ai cũng tạo được dự án
- Given nhân viên Lan của công ty Lam; dự án "Web Lam" ngân sách 80 000 000 đ
- When Lan tạo dự án "App Lam", rồi sao chép "Web Lam"
- Then có hai dự án mới của công ty Lam, cả hai ngân sách 0
- Tests: ⚠ Chưa có test

### AC-2: Chỉ chủ và quản lý đổi ngân sách
- Given nhân viên Lan, dự án "Web Lam" ngân sách 80 000 000 đ
- When Lan đặt ngân sách "Web Lam" thành 500 000 000 đ bằng bất kỳ đường nào
- Then Lan nhận "không có quyền" (403); ngân sách vẫn 80 000 000 đ
- Tests: ⚠ Chưa có test

### AC-3: Dự án đã lưu trữ giữ ngân sách
- Given dự án "Web Cũ" đã lưu trữ
- When quản lý đặt ngân sách cho "Web Cũ"
- Then bị từ chối; ngân sách không đổi
- Tests: ⚠ Chưa có test

### AC-4: Xem dòng hoá đơn của dự án
- Given dự án "Web Lam" có 2 hoá đơn đã phát hành, 1 nháp
- When một thành viên công ty Lam xem báo cáo dự án
- Then thấy các dòng của 2 hoá đơn đã phát hành, không thấy nháp
- Tests: ⚠ Chưa có test
