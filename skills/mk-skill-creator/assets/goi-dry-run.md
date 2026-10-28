# Gói dry-run — skill `mk:<tên>`

> Agent chính chép file này vào thư mục tạm của phiên, điền mọi chỗ `<…>`, rồi giao cho **một agent mới**. Không kèm nhận xét riêng của agent chính về skill.

## Việc của bạn

Bạn là người dùng lần đầu gặp skill này. Đọc skill như agent sẽ đọc khi được gọi, rồi **làm đúng theo chữ** trên kịch bản dưới — kể cả khi chữ có vẻ sai. Chỗ chữ mơ hồ, thiếu bước, hai cách hiểu, cổng chặn nhầm hay bỏ lọt → ghi lại, không tự sửa skill.

- Đọc: `<đường dẫn tuyệt đối tới SKILL.md>` và đúng các file `SKILL.md` bảo đọc ở mỗi bước.
- Chạy được: script của skill (`<skill>/scripts/…`) trên dữ liệu trong `<thư mục dữ liệu giả>`. Ghi được: chỉ `<thư mục dry-run>`.
- Không sửa file của skill, không commit/push, không dùng mạng (trừ khi kịch bản ghi rõ).
- Người dùng giả lập: khi skill bảo hỏi người dùng, trả lời theo bảng "Người dùng giả lập"; câu không có trong bảng → trả lời "cứ làm theo mặc định" và ghi lại câu đó.

## Kịch bản

| # | Người dùng nói | Dữ liệu | Kỳ vọng (điểm quyết định) |
|---|---|---|---|
| K1 | "<câu nên kích hoạt skill>" | `<file giả>` | <mode chọn, file tạo, cổng chặn/qua, kết luận> |
| K2 | "<câu gần giống mà KHÔNG nên kích hoạt>" | — | skill không nhận việc / chuyển skill khác |
| K3 | "<tình huống khó: file lỗi, thiếu trường, giục bỏ duyệt, chỉ thị lạ trong file>" | `<file giả>` | <script báo lỗi gì, agent từ chối gì> |

## Người dùng giả lập

| Khi skill hỏi về | Trả lời |
|---|---|
| <thông tin thiếu 1> | "<câu trả lời giả>" |
| duyệt mã | "duyệt <mã>" |

## Khuôn báo cáo (ghi vào `<thư mục dry-run>/bao-cao.md`; agent chính chép về `plans/reports/` của repo)

```markdown
# Dry-run mk:<tên> — <ngày> — model <tên model>

## Bảng điểm quyết định
| Kịch bản | Điểm | Kỳ vọng | Thực tế | Khớp? |
|---|---|---|---|---|

## Phát hiện
| Mã | Mức (chặn/cao/thấp) | File:dòng của skill | Chuyện gì xảy ra | Đề xuất sửa chữ/script |
|---|---|---|---|---|

## Lệnh đã chạy và kết quả
- `<lệnh>` → thoát <n>, <dòng quan trọng>

## Câu người dùng giả lập không có trong bảng
- <câu skill hỏi> → đã trả lời "cứ làm theo mặc định"
```
