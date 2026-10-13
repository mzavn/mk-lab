# Dự án nhỏ, MVP: PRD → wireframe → TDD (mode `prd`, `promote`)

Mọi bộ chuẩn về yêu cầu — ISO/IEC/IEEE 29148, GitHub Spec Kit, Kiro, BMAD, lộ trình vibecode — cùng một khung sáu phần: **vì sao** · **cái gì** (story + tiêu chí nghiệm thu) · **trông thế nào** · **làm thế nào** · **chia việc** · **quản trị** (duyệt, truy vết, lịch sử). Việc lớn chỉ điền thêm phần, không đổi định dạng. mk-specs vì thế có bốn mức trên cùng một khung; người dùng chọn kỹ tới đâu.

| Mức | Phần được điền | File trong `specs/` | Hợp khi |
|---|---|---|---|
| 1 · PRD | vì sao, cái gì, chia việc | `PRD.md` | thử ý tưởng, MVP vài ngày, công cụ nội bộ |
| 2 · + wireframe | + trông thế nào | + `wireframe.html` | có giao diện người dùng thấy |
| 3 · + TDD | + làm thế nào | + `TDD.md` | có CSDL, đăng nhập, tích hợp ngoài |
| 4 · SDD đầy đủ | + quản trị | BR/UC/AC/ADR, `traceability.md` | > 2 người, luật tiền/pháp lý, sống > 6 tháng (principles.md §5) |

Mức 1–3 là file này. Mức 4 là `init`/`change` của skill; từ mức 1–3 lên mức 4 dùng `promote` (§6).

## 1. Chọn mức

- Người dùng đã nói mức → dùng. Chưa nói → hỏi một câu, kèm đề xuất theo ba dấu hiệu: có giao diện không · có CSDL/đăng nhập/tích hợp không · có tiền, pháp lý, nhiều người, sống lâu không (có → đề xuất mức 4).
- Đã có `specs/PRD.md` → đọc dòng `- Mức:`; người dùng muốn kỹ hơn → làm tiếp phần của mức sau, không viết lại phần đã có.
- Không cần `specs/mk-specs.yml` ở mức 1–3, không cần cài vào project. Repo đã có file đó (cài `--project`) vẫn dùng được mức 1–3.

## 2. Phỏng vấn → `specs/PRD.md` (mọi mức)

Chép `assets/templates/prd.md` thành `specs/PRD.md`, rồi phỏng vấn theo thứ tự mục:

1. **Vì sao** (§1): vấn đề, người dùng, thành công khi, **ngoài phạm vi**. Hỏi "nếu chỉ làm được ba việc thì là gì?" và "cái gì chắc chắn chưa cần?".
2. **Tính năng** (§2): người dùng kể một tính năng → agent tự viết thành story `Là … tôi muốn … để …`, hỏi "xong khi nào?". Ưu tiên: việc nằm trong "ba việc" ở bước 1 là Must, không hỏi lại; chỉ hỏi Must/Should/Could cho phần còn lại. Luồng nhiều bước → tách nhiều story, mỗi story giao được giá trị riêng; màn dùng chung giữa hai story thì "Done khi" của story làm trước không đòi phần của story làm sau.
3. **Lỗi và biên** (§3), **dữ liệu chính** (§4): hỏi theo từng story Must, không hỏi chung chung.
4. **Thứ tự làm** (§7): agent đề xuất theo phụ thuộc + ưu tiên, người dùng sửa; không có ý kiến → giữ đề xuất.

Cách hỏi:
- Mỗi lượt tối đa 4 câu, mỗi câu có phương án gợi ý; dùng công cụ hỏi nếu agent có, không thì đánh số trong chat. Gom câu của nhiều mục vào một lượt khi được — mục tiêu ít lượt, không phải ít câu.
- **Phần nhạy cảm** (cùng danh sách ở mọi chỗ trong skill): tiền · quyền truy cập · bảo mật · dữ liệu cá nhân · pháp lý. Câu vừa có phần thường vừa có phần nhạy cảm → tách làm hai câu trước khi hỏi, để "tuỳ bạn" chỉ áp vào phần được phép.
- Người dùng nói "tuỳ bạn" → điền phương án gợi ý và ghi vào `Giả định` (§1) để họ thấy. Phần nhạy cảm không tự điền, ghi `[OPEN]`:
  - **tiền**: dòng tiền trong app (thanh toán, phí, hoàn tiền) **và** chi phí phát sinh cho chủ dự án (hosting, dịch vụ trả phí);
  - **quyền truy cập, bảo mật**: ai đăng nhập thế nào, ai xem/sửa được gì, xác minh người thao tác;
  - **dữ liệu cá nhân**: trường người dùng đã nêu thì dùng; ai xem được và giữ bao lâu thì hỏi;
  - **pháp lý**: điều khoản, hoá đơn, đồng ý của người dùng, quy định ngành.
- Người dùng không trả lời một giá trị mà "Done khi" cần → viết "Done khi" theo phương án đề xuất, gắn `[OPEN] Ox` ngay dòng đó; giá trị coi là chưa chốt.
- Không hỏi điều đọc được từ repo (stack hiện có, cấu trúc thư mục).
- Dừng hỏi khi mọi story Must có "Done khi" đo được (kể cả dòng gắn `[OPEN]`). Should/Could được phép mỏng.

Quy tắc viết:
- **Mã story vĩnh viễn**: tiền tố 2–4 chữ in hoa theo tính năng (`ORD`, `CFG.AI`) + số hai chữ số. Không đánh số lại, không dùng lại; bỏ story thì `Status: Dropped` + lý do.
- **Status story**: `Todo` · `Blocked ([OPEN] Ox)` khi một `[OPEN]` về phần nhạy cảm chặn nó · `In Progress` · `Partial` · `Done` · `Dropped`. `Blocked` là cách mức 1–3 "dừng chờ người quyết" (cổng cứng 2): không ai code story đó tới khi được trả lời. `[OPEN]` không nhạy cảm không chặn story.
- **`[OPEN]` chỉ một danh sách** ở PRD `## Câu hỏi mở`, đánh số `O1, O2…`, mỗi dòng ghi `chặn:` story nào (hoặc —); TDD và wireframe trỏ tới số đó, không chép lại.
- **Có câu trả lời cho `[OPEN]`**: sửa "Done khi"/TDD theo câu trả lời, bỏ nhãn `[OPEN] Ox` ở dòng liên quan, xoá dòng `Ox` khỏi danh sách (số không dùng lại), story `Blocked` → `Todo` ở §2 và §7, thêm dòng History, chạy lại `review` cho phần đổi. Ai sửa PRD lúc đó (agent soạn PRD hay agent đang code) đều làm như vậy.
- **"Done khi" dạng Given/When/Then rút gọn**, có con số, có dòng `KHÔNG:` khi cần — để lên mức 4 thành AC nguyên văn.
- PRD một màn hình đọc cho mỗi tính năng; chi tiết kỹ thuật để §6 hoặc `TDD.md`.
- Kỷ luật ở SKILL.md áp nguyên: không thêm story "phòng khi", ý ngoài yêu cầu → `Để sau` hoặc `Ngoài phạm vi`.

## 3. Wireframe → `specs/wireframe.html` (mức 2)

- **Một file HTML** cho **màn chính** — màn có nhiều story Must nhất; hoà thì màn người dùng chính dùng nhiều nhất. Có khung chung (đầu trang, điều hướng) thì thể hiện luôn. Các màn khác chỉ liệt kê ở PRD §5.
- Tự chứa: CSS inline, không tải gì từ mạng, mở thẳng bằng trình duyệt. Dữ liệu giả, không dữ liệu thật. Trang tĩnh, vài trạng thái chính vẽ sẵn cạnh nhau (trống, có dữ liệu, lỗi) là đủ; JS chỉ khi trạng thái không vẽ tĩnh được.
- Mỗi vùng/nút gắn story bằng `data-story="ORD-01"`; vùng chưa có story thì không vẽ, hoặc hỏi để thêm story.
- Hỏi người dùng 2–3 điểm trước khi vẽ (gom vào lượt hỏi chung nếu được): phong cách tham khảo (link/ảnh), màu thương hiệu, desktop hay mobile trước. Vẽ xong → người dùng mở xem → một vòng sửa trong mode này; chỉnh tiếp để tới lúc code. Chưa duyệt không chặn TDD: ghi `[OPEN]` "wireframe chưa duyệt" (không chặn story) rồi làm tiếp. Quyết định giao diện đáng nhớ ghi vào PRD §5.

## 4. Thiết kế kỹ thuật → `specs/TDD.md` (mức 3)

1. Phỏng vấn kỹ thuật: mỗi quyết định gồm vì sao quan trọng (một câu, ví dụ đời thường) · 2–3 phương án + ưu/nhược · đề xuất hợp với quy mô dự án. Quyết định có sẵn trong repo → ghi lại, không hỏi. Người dùng đã giao phần kỹ thuật ("tuỳ bạn, đơn giản nhất") → chọn theo đề xuất, trình **một lượt** tóm tắt các lựa chọn để họ phản đối nếu muốn, không hỏi từng cái; phần nhạy cảm (chi phí hosting, dịch vụ trả phí, quyền, bảo mật) vẫn hỏi riêng hoặc `[OPEN]`.
2. Chép `assets/templates/tdd.md`, điền. Bảng Stack giữ một cụm "phương án bị loại" mỗi hàng; §8 chỉ cho quyết định không phải chọn stack (vd chặn trùng giờ bằng ràng buộc dữ liệu). Lên mức 4: hàng Stack đáng nhớ và mục §8 đều thành ADR.
3. Chỉ viết luồng (§5) cho story có chỗ khó (tranh chấp, nhiều bước, tích hợp ngoài); story CRUD thường thì bảng §4 là đủ. §7 chỉ ghi điều đã chọn, không đoán cấu trúc thư mục khi chưa có code.
4. Phần nhạy cảm trong §6 do người quyết; chưa quyết → trỏ `[OPEN] Ox` của PRD.
5. Đơn giản nhất đủ cho các story Must: không microservice, hàng đợi, cache, phân quyền nhiều tầng khi PRD không đòi.
6. PRD §6 còn một dòng trỏ `TDD.md`.

## 5. Tự soát, rồi dừng trước khi code

1. Chạy mode `review` (review.md) cho cả bộ file của mức, gồm phần soát chéo §3b.
2. PRD: `Mức:` đúng; `## History` — PRD mới thì điền ngày cho dòng `v1`, sửa về sau thêm dòng `vN`. Story bị `[OPEN]` nhạy cảm chặn → `Blocked ([OPEN] Ox)` ở cả §2 và §7. `Status: ready` khi có ít nhất một story Must làm được ngay (không `Blocked`, phụ thuộc đã xong); không thì giữ `draft` và nói rõ đang chờ câu trả lời nào.
3. Báo người dùng: mức · file đã tạo · số story (Must/Should/Could) · story làm được đầu tiên ở §7 · `[OPEN]` còn lại, **trước hết** những `[OPEN]` khiến Must không giải được "Vấn đề" §1 hoặc "Thành công khi" không đo được (vẫn `ready` được, nhưng người dùng phải thấy ngay).
4. **Dừng.** Không code trong mode này. Bước kế là lập kế hoạch và code theo §7, bằng bất kỳ agent hay công cụ nào — hướng dẫn cho người code đã nằm ngay đầu `PRD.md`.
5. Gợi ý commit (không tự commit): `docs(specs): PRD mức <n> cho <tên app>` — scope `specs` dùng khi commit chỉ đổi file spec.

Sửa PRD về sau (thêm story, đổi "Done khi"): sửa thẳng file, thêm dòng History, chạy lại `review`. Không cần change folder ở mức 1–3.

## 6. Nâng lên mức 4 (mode `promote`)

Khi dự án có dấu hiệu ở bảng đầu file, hoặc người dùng yêu cầu. Chỉ chạy khi người dùng đồng ý.

1. Cài vào project (workflow-bootstrap.md §1); sửa `specs/mk-specs.yml`: `contexts` lấy từ nhóm tính năng (đề xuất, người dùng chốt), `metrics.since` = hôm nay.
2. Ánh xạ, chép mẫu rồi điền:

| Từ | Thành |
|---|---|
| PRD §1 (vấn đề, thành công khi, ngoài phạm vi, giới hạn) | `BR-01` trong `business-requirements.md` |
| Tính năng `[ORD]` | một UC (`UC-101…`) trong context tương ứng |
| Story Must/Should + "Done khi" | các AC của UC đó, giữ nguyên câu; dòng `KHÔNG:` thành hệ quả phủ định |
| PRD §3 | Exceptions của UC |
| PRD §4 + TDD §3 | `entities.md` (tên nghiệp vụ; cột/kiểu ở `## Traceability`) |
| TDD §2 (hàng đáng nhớ) + §8 | ADR trong `decisions.md`, giữ phương án bị loại |
| `[OPEN]` | `[OPEN]` trong UC tương ứng |

3. Mỗi UC: History `v1 (YYYY-MM-DD, chưa commit): dựng từ PRD story ORD-01, ORD-02`; `## Traceability` ghi `Story cũ: ORD-01, ORD-02` để `git log --grep` tìm được commit cũ.
4. **Đối chiếu với code đang chạy** — PRD có thể đã lệch code. Story `Done`: đọc code như workflow-bootstrap.md §3 bước 2; khớp → AC giữ nguyên, `Tests:` trỏ test nếu có, không có thì `⚠ Chưa có test`; lệch → `[DIVERGENCE]`, không tự chọn bên đúng. Story `Todo`/`Partial` → UC Status `spec-only`/`partial`.
5. `PRD.md`: `Status: promoted`, thêm dòng đầu "Đã nâng lên SDD ngày …, nguồn sự thật là `specs/README.md`". Giữ file và `wireframe.html`, `TDD.md`; không sửa cho khớp về sau.
6. Chạy `review` cho BR/UC vừa dựng, rồi gen.py + verify.py. Commit `chore(specs): promote PRD to SDD`. Từ đây mọi thay đổi hành vi đi đường `change`.
