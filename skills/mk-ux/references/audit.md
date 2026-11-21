# Mode `audit` và `improve` — soi, bàn giao sửa, đo lại, bài học

Đọc khi người dùng nhờ xem một giao diện, slide, hình hay video, gửi ảnh/video góp ý, hoặc gọi tên mã `UX-n` để sửa. Ngưỡng và cách đọc dòng `score`: `references/standards.md`. Danh mục lỗi AI: `references/ai-mistakes.md`. Khuôn báo cáo: `assets/audit-report.md`.

## 1. Chuẩn bị

1. Xác định bề mặt: `web`, `app-web` đo bằng máy; `app`, `slide`, `image`, `video` kiểm tay theo `references/surfaces.md`. Slide dạng HTML đo như `web`.
2. Đọc `DESIGN.md` (gồm `## Gu đã chốt`, `## Luật đo`, `## Mẫu`) và spec màn liên quan (UC, AC) nếu có.
3. Liệt kê hành trình cần soi cho từng nhóm người dùng (khách, người trong nhà): việc chính, số bước tới việc chính. Suy được nhóm người dùng và việc chính từ spec hoặc chính trang → ghi là "giả định" trong báo cáo; không suy được việc chính của một nhóm → hỏi một lượt (`references/needs.md` §câu hỏi).
4. Tạo thư mục tạm của phiên; JSON đo và ảnh chụp chỉ để trong đó.

## 2. Đo (bề mặt đo được)

1. Dùng địa chỉ người dùng đưa. Cần chạy dev server theo lệnh trong `AGENTS.md`/`package.json` → in đúng lệnh và hỏi người dùng một câu trước khi chạy. Ưu tiên môi trường có dữ liệu giả.
2. Mỗi màn × mỗi khổ (320, 390, 768, 1440): đổi bề rộng cửa sổ, đặt `window.MK_UX_SCREEN`, chạy `assets/measure.js`, lưu `<màn>@<khổ>.json`. Không đổi được bề rộng → dừng phần đo, ghi giới hạn, kiểm tay.
3. `python3 <skill>/scripts/ux.py score <thư mục> --design DESIGN.md` (bỏ `--design` khi dự án chưa có).
4. `CHƯA KIỂM … chưa đánh dấu` → đề xuất đúng thuộc tính `data-ux` cho phần tử nghi (nút lớn nhất trong khung đầu, khối bảng…), ghi vào báo cáo; không đoán theo màu.
5. Chụp ảnh từng màn ở 390 và 1440 cho lượt soi bằng mắt.

## 3. Soi bằng mắt người dùng

1. Đi hành trình thật: ghi chỗ phải dừng lại tự hỏi, chỗ bấm nhầm, chỗ phải cuộn để tới việc chính, chỗ phải gõ lại điều đã gõ. Dùng phép thử của từng `NL-n` (`references/principles.md`).
2. Giao agent riêng chỉ đọc bằng `assets/independent-review.md` (đường dẫn ảnh, kết quả `score`, `## Gu đã chốt`, danh sách hành trình). Agent soát không sửa file, không chạy lệnh.
3. Gộp: một vấn đề một phát hiện; số máy đo và nhận định của agent soát ghi rõ nguồn.

## 4. Viết phát hiện

- Khuôn `### UX-n` và giá trị hợp lệ: `assets/audit-report.md`. Mỗi phát hiện một "Họ cảm thấy" bằng lời người dùng, không bằng thuật ngữ.
- **Hạng:** `hỏng` (máy đo trượt, chức năng sai, người dùng bị kẹt) · `lệch hệ` (bản dựng trái `DESIGN.md`, mẫu chuẩn, hay một dòng `## Gu đã chốt`) · `gu` (khẩu vị, không có luật nào nói). Bản dựng **đúng** gu đã chốt → không nêu, không đề xuất đổi gu.
- **Tìm gốc** bằng năm lần "vì sao" tới chỗ sửa một lần cho cả bộ (component chung, token, hàm tải dữ liệu), không dừng ở màn đang xem.
- **Mã:** gắn `AI-n` khi khớp một lỗi trong `references/ai-mistakes.md`, hoặc mã luật đo — để đếm bài học.
- **Loại sửa:** `hành vi` khi đổi điều người dùng thấy/làm được hay luật dữ liệu (thêm bước, đổi thứ tự việc chính, đổi chữ thông báo, thêm/bỏ một nút, chặn hay cách ly dữ liệu); `trình bày` khi chỉ đổi hình thức mà người dùng vẫn làm đúng các bước cũ (cỡ chữ, vùng chạm, màu, khoảng cách, gộp một hàng, đánh dấu nút chính đã có).
- Đầu báo cáo: "3 việc nên sửa trước" xếp theo tác động rồi khoảng cách; dòng `Kết quả:` của `score`.
- Lưu `<specs_dir>/ux/<yyMMdd>-<slug>.md` (repo không theo spec → hỏi chỗ lưu); chạy `python3 <skill>/scripts/ux.py check <báo cáo>` tới khi thoát 0; trình bảng tóm tắt và câu duyệt mẫu: "Duyệt mã nào? Ví dụ: `duyệt UX-1 UX-3`."

## 5. Sửa (mode `improve`)

mk-ux **không sửa code dự án**. Với từng mã người dùng gọi tên:

| Loại / hạng | Làm |
|---|---|
| `hành vi` | Viết proposal `draft` qua mk-specs (AC hành vi; số hình thức → `## Luật đo`); người duyệt nghiệp vụ duyệt; mk-cook làm code. |
| `trình bày`, luật đã có (bảng mặc định `references/standards.md` hoặc `## Luật đo`/`## Mẫu` của `DESIGN.md`) | Bàn giao mk-cook (làn UI) hoặc mk-fix: mã `UX-n`, luật bị trái, phần tử, cách kiểm (`score` dòng nào phải hết). Không đề xuất thêm dòng `DESIGN.md` khi mặc định đã đủ. |
| `trình bày`, luật chưa có ở cả hai nơi | Đề xuất dòng `## Luật đo`/`## Mẫu` bằng bảng mã (`references/system.md` §2), duyệt xong mới bàn giao. |
| `gu` | Chỉ đi tiếp khi chủ sản phẩm gọi đúng mã; chốt xong → đề xuất dòng `## Gu đã chốt`. |

"Sửa hết đi" không phải duyệt hàng loạt: liệt kê lại mọi mã theo loại; chỉ mã người dùng gọi tên mới đi tiếp. Mã `trình bày` chưa được gọi tên cũng không tự bàn giao — hỏi một câu gom các mã đó ("Bàn giao luôn UX-3, UX-7, UX-9 (trình bày) cho mk-cook?"); mã `hành vi`, `gu` hỏi riêng. Mã đo `main-task-first-view` và `pattern-*` thường là `hành vi` (đổi bố cục, thêm điều khiển); các mã đo khác thường là `trình bày`.

Sau khi mk-cook/mk-fix báo đã commit: đo lại ở cùng khổ, `ux.py score <mới> --baseline <cũ> --design DESIGN.md`; điền `- Trạng thái: đã sửa <commit>` và dòng `Đo trước: a/b · Đo sau: c/b` vào báo cáo; `check` thoát 0. `MỚI HỎNG` → báo ngay, không gộp vào "đã cải thiện". Tối đa 3 vòng đo–sửa cho một mã; còn lỗi → mục "Còn thấy" ≤ 5 dòng cho người dùng quyết.

Đổi `## Luật đo` sau khi báo cáo đã viết → chấm lại bằng ngưỡng mới, cập nhật "Điểm B" của phát hiện bị ảnh hưởng và dòng `Kết quả:` trước khi trình tiếp.

## 6. Bài học

- Cùng một `- Mã:` xuất hiện ở ≥ 2 báo cáo trong `<specs_dir>/ux/` → đề xuất một dòng `## Bài học` (lỗi · cách tránh · mã luật nếu đo được) và, nếu đo được, dòng `## Luật đo`/`## Mẫu`.
- Lần soi sau đọc `## Bài học` trước; lỗi đã thành luật được `score` bắt tự động.

## 7. Thử với người thật (khi được)

Khuyến nghị cho chủ sản phẩm: 3 người dùng thật, mỗi người 15 phút, giao việc thật ("đăng ký học thử", "tìm học viên có số đuôi 4567"), người quan sát không gợi ý; ghi chỗ khựng, chỗ hỏi lại. Kết quả vào báo cáo như một nguồn bằng chứng của "Điểm A"; sửa chỗ nghiêm trọng nhất trước.
