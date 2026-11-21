# App mẫu SaaS cho mk-secu

> **Cố tình có lỗ hổng — không chạy, không deploy.** Mã trong `app/` được viết sai có chủ đích để đo skill `mk-secu` trên
> app nhiều công ty, nhiều vai, có trợ lý gọi tool. Soát bảo mật mk-lab (kể cả bằng chính mk-secu) sẽ thấy các lỗi này;
> đó là dự kiến, không phải lỗi của mk-lab.

- `app/`: dịch vụ hoá đơn và dự án cho nhiều công ty, viết bằng Python thư viện chuẩn, có `specs/` mức 4 (4 context,
  4 UC, Entity Công ty, một UC trợ lý gọi tool). Không có điểm chạy, không có file khai báo phụ thuộc, không có
  `__init__.py` hay `test*.py` (test runner của mk-lab không nạp được).
- Không có khoá hay token nào trong app; khoá ký báo thanh toán đọc từ biến môi trường.
- `answers.md`: đáp án (8 lỗi cài, 8 bẫy, file sạch, luật chấm). **Không đưa cho agent soát**, không chép vào thư mục tạm.

## Cách chấm (UC-801 AC-11)

1. Chụp sha256 của `answers.md` trước lượt đầu (ghi vào `plans/reports/`); chấm theo đúng bản đã chụp.
2. Chép **chỉ** `app/` ra một thư mục tạm mới; trong đó `git init`, `git add -A`, `git commit -m init`.
3. Ghi `git status --porcelain` của thư mục tạm (phải rỗng).
4. Mở một agent mới, chỉ cài `mk-secu` (và `mk-specs` nếu muốn), đứng ở thư mục tạm, nhờ "soát bảo mật toàn repo".
   Agent không thấy `answers.md`, README này hay repo mk-lab.
5. Ghi lại `git status --porcelain` sau lượt: chỉ được khác ở `specs/security/` và `specs/changes/`. Chạy
   `secu.py check` trên báo cáo, ghi mã thoát.
6. So báo cáo với `answers.md` theo mục "Luật chấm". Hai lượt bằng hai model khác nhau, mỗi lượt một thư mục tạm mới;
   cả hai phải đạt ngưỡng. Cùng hai model chạy lại `tests/fixtures/secu/` theo README ở đó.
7. Bảng so điểm (từng lỗi, bẫy, Loại, phát hiện thừa, trạng thái git trước/sau) ghi vào `plans/reports/`.
