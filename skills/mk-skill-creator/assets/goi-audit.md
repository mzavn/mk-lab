# Gói audit bảo mật — skill `mk:<tên>`

> Dùng khi skill đọc/ghi file người dùng, chạy lệnh hoặc gọi mạng. Agent chính chép file này vào thư mục tạm của phiên, điền `<…>`, giao cho **một agent riêng chỉ đọc**.

## Việc của bạn

Soát skill dưới đây như người muốn lợi dụng nó. **Chỉ đọc**: không sửa file, không chạy script, không dùng mạng. Mỗi phát hiện phải có bằng chứng `file:dòng` và một kịch bản cụ thể (ai làm gì → hỏng ra sao); không đủ bằng chứng → ghi "nghi ngờ", không ghi "xác nhận".

- Skill: `<đường dẫn tuyệt đối tới thư mục skill>` (đọc `SKILL.md`, `references/`, `assets/`, `scripts/`).
- Skill đọc: <file/thư mục người dùng nào>. Ghi: <file nào, ở đâu>. Chạy lệnh: <lệnh nào hoặc "không">. Mạng: <địa chỉ nào hoặc "không">.
- Luật repo: `<đường dẫn AGENTS.md>`.

## Câu hỏi phải trả lời

1. Script có ghi ra ngoài thư mục được phép không (đường dẫn `..`, đường dẫn tuyệt đối từ dữ liệu, symlink)? Có ghi đè, ghi dở, xoá file không?
2. Dữ liệu người dùng có thể thành lệnh không (chỉ thị trong file, tên file lạ, regex làm treo, lệnh shell ghép chuỗi)?
3. Chữ của skill có chỗ nào cho phép agent bỏ bước duyệt, tự commit/push, đọc ngoài repo, gửi dữ liệu đi khi bị giục?
4. Bí mật, dữ liệu cá nhân: skill có in, chép, ghi log chúng không?
5. Luật repo người dùng có thể nới quyền skill không, hay chỉ thu hẹp?
6. Hook (nếu có) chạy mã nào, từ đâu, khi nào im lặng?

## Khuôn báo cáo

```markdown
# Audit bảo mật mk:<tên> — <ngày>

| Mã | Mức (nghiêm trọng/cao/trung bình/thấp) | Kết luận (xác nhận/nghi ngờ) | File:dòng | Kịch bản | Đề xuất sửa |
|---|---|---|---|---|---|

## Đã soát, không thấy vấn đề
- <câu hỏi số> — <vì sao an toàn, file:dòng>

## Chưa soát được
- <phần nào, vì sao>
```
