# Entity

## Công ty (companies)
- tên.
- Bất biến: mọi dự án, hoá đơn, kỳ, thành viên thuộc đúng một công ty; người dùng chỉ đọc và ghi bản ghi của công ty
  mình. Bản ghi của công ty khác coi như không tồn tại.

## Thành viên (users)
- email (duy nhất), tên, vai: `owner` (chủ), `accountant` (kế toán), `manager` (quản lý), `member` (nhân viên).
- băm mật khẩu, khoá TOTP (xác thực hai bước): chỉ hệ thống dùng.
- đã khoá: chủ công ty khoá khi người đó nghỉ việc. Người đã khoá không còn dùng được Sổ Việc.
- đếm lần sai, khoá tạm đến: chống dò mật khẩu.

## Phiên (sessions)
- token ngẫu nhiên (chỉ lưu băm), thành viên, hết hạn sau 12 giờ.

## Dự án (projects)
- tên, ngân sách (đồng), trạng thái `active` hoặc `archived`.
- Bất biến: dự án mới hoặc bản sao bắt đầu với ngân sách 0; chỉ chủ và quản lý đổi ngân sách; dự án đã lưu trữ không đổi
  ngân sách.

## Kỳ kế toán (periods)
- tháng (`YYYY-MM`), đã chốt hay chưa. Chủ công ty chốt kỳ; chốt rồi không mở lại.

## Hoá đơn (invoices)
- dự án, khách, các dòng (mô tả, số lượng, đơn giá), tổng tiền, kỳ, trạng thái `draft` (nháp), `issued` (đã phát hành),
  `paid` (đã thu), `void` (đã huỷ), thời điểm phát hành.
- Bất biến: hoá đơn thuộc kỳ đã chốt giữ nguyên khách, dòng, tổng tiền, kỳ, và giữ nguyên việc được tính hay không được
  tính vào doanh thu kỳ (nháp, đã huỷ không tính; đã phát hành, đã thu có tính).
- Ghi thu (`issued` → `paid`) vẫn được làm ở kỳ đã chốt: doanh thu kỳ không đổi, chỉ thêm khoản thu.
- Hoàn tiền là chứng từ riêng (refunds), không sửa hoá đơn gốc; tổng hoàn không vượt tổng tiền hoá đơn.

## Link chia sẻ (share_links)
- khoá ngẫu nhiên (chỉ lưu băm), một hoá đơn, hết hạn sau 30 ngày.

## Mã xác nhận (confirmations)
- người dùng, việc, nội dung việc, hết hạn sau 5 phút, dùng một lần.
