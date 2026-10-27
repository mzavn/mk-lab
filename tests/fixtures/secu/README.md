# App mẫu cho mk-secu

> **Cố tình có lỗ hổng — không chạy, không deploy.** Mã trong `app/` được viết sai có chủ đích để đo skill
> `mk-secu`. Soát bảo mật mk-lab (kể cả bằng chính mk-secu) sẽ thấy các lỗi này; đó là dự kiến, không phải lỗi của mk-lab.

- `app/`: cửa hàng bánh nhỏ viết bằng Python thư viện chuẩn, có `specs/` mức 4 (3 UC). Không có điểm chạy, không có
  file khai báo phụ thuộc, không có `__init__.py` hay `test*.py` (test runner của mk-lab không nạp được).
- Khoá bí mật cài trong app là chuỗi giả, không thuộc định dạng của nhà cung cấp nào.
- `answers.md`: đáp án (lỗi cài, bẫy, file sạch). **Không đưa cho agent soát.**

## Cách chấm (UC-801 AC-8)

1. Chép `app/` ra thư mục tạm, `git init`, `git add -A`, `git commit`.
2. Mở một agent khác, chỉ cài `mk-secu` (và `mk-specs` nếu muốn), đứng ở thư mục tạm, nhờ "soát bảo mật toàn repo".
   Ghi `git status --porcelain` trước và sau: chỉ được khác ở `specs/security/` và `specs/changes/`.
3. So báo cáo với `answers.md`: khớp = token dấu vết đầu tiên cùng file, dòng giao nhau với lỗi cài, cùng mã `- Lớp:`;
   `xác nhận` có token đầu ở bẫy hay file sạch là báo nhầm.
4. Làm hai lượt (hai agent mới). Cả hai lượt phải đạt: ≥ 5/6 lỗi cài là `xác nhận`, ≥ 5/6 đúng `Loại`,
   0 bẫy và 0 file sạch có `xác nhận`. Phát hiện thừa ghi lại trong báo cáo dry-run.
