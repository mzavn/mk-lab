# Tự soát spec (mode `review`)

Agent đọc lại spec **mình vừa viết** trước khi đưa người duyệt: tự tìm mâu thuẫn, thiếu sót, phần thừa, chỗ đoán ý; sửa lỗi của chính mình, hỏi người dùng những điểm cần quyết. Ba nhịp: soát → hỏi có phương án → ghi câu trả lời. Mọi bước nằm trong file này; không cần skill hay công cụ nào khác ngoài `python3`.

**Khi nào chạy**
- Tự động, ngay sau khi viết xong: proposal ở mode `change` (trước commit 1), BR/UC đầu tiên hoặc baseline ở mode `init`, bộ `PRD.md`/`wireframe.html`/`TDD.md` ở mode `prd`, BR/UC dựng ở mode `promote`.
- Khi người dùng yêu cầu: "soát spec", "review proposal", "kiểm lại spec vừa viết".

**Không phải duyệt.** Tự soát không thay review hai phía (workflow-change.md §2): không điền `Người duyệt kỹ thuật`/`Người duyệt nghiệp vụ`, không đổi Status sang `approved`. Ở mức 1–3 (workflow-prd.md) không có review hai phía; khi nào PRD được `Status: ready` xem workflow-prd.md §5.

## 1. Xác định đối tượng

1. Người dùng chỉ file/thư mục → dùng đúng file đó.
2. Không chỉ → artifact vừa viết trong phiên này; không có → proposal mới nhất trong `specs/changes/` có Status `draft`/`reviewing`; không có proposal mà có `specs/PRD.md` chưa `promoted` → PRD cùng `wireframe.html`, `TDD.md` đi kèm.
3. Vẫn không xác định được → hỏi người dùng, dừng.

Đọc kèm: lời yêu cầu gốc của người dùng (nguyên văn), BR + UC + ADR + `entities.md` liên quan, `open-issues.md` (mức 4); mọi file của mức đang soát (mức 1–3).

## 2. Kiểm bằng máy

Chỉ khi repo có `specs/mk-specs.yml` (mức 4, hoặc mức 1–3 đã cài vào project):

```bash
python3 .claude/skills/mk-specs/scripts/audit.py     # mục thiếu, chữ kỹ thuật trong flow/AC
python3 .claude/skills/mk-specs/scripts/verify.py    # link, thẻ UC/AC, test được trích
```

Chỉ xét dòng thuộc đối tượng đang soát; lỗi cũ ở file khác ghi một dòng "đã có từ trước", không sửa (cùng lý do ở nguyên tắc "Sửa đúng chỗ" trong SKILL.md). Không có config → bỏ bước này, ghi "không chạy script (mức 1–3)"; kiểm link tương đối giữa các file bằng mắt.

## 3. Tự soát theo năm nhóm

Đọc từng câu của đối tượng, hỏi:

| Nhóm | Câu hỏi kiểm |
|---|---|
| **Đúng ý** | Mỗi AC/flow/entity truy được về lời yêu cầu hoặc BR không? Có chỗ nào mình chọn một cách hiểu trong nhiều cách mà không hỏi? Giá trị nào (thời hạn, ngưỡng, phí, quyền) mình tự đặt? |
| **Mâu thuẫn** | AC nào chọi AC khác (cùng Given, Then khác)? AC trái Out of Scope của BR, ADR đang `accepted`, bất biến trong `entities.md`, UC khác? Con số có khớp giữa Vì sao, AC, entity không? `ADDED AC-n` có trùng ID đã có? `MODIFIED`/`DEPRECATED` có trỏ tới AC có thật? |
| **Thiếu sót** | Thiếu Actor/Trigger? Biên đã rõ chưa (đúng 15 phút thì sao)? Hệ quả phủ định ("KHÔNG tạo đơn") khi cần? Exception đã có quyết định xử lý? Dữ liệu cũ khi đổi luật? Mục open-issues nào thay đổi này đóng được mà chưa ghi `Đóng`? Luật tiền/quyền/bảo mật/dữ liệu cá nhân/pháp lý nào chưa có người quyết? |
| **Thừa** | UC/AC/entity/ADR nào không ai yêu cầu? Cấu hình hoá, "để sau này mở rộng", exception cho tình huống không xảy ra được? Đoạn nào cắt đi người duyệt vẫn hiểu đủ? Proposal có quá một màn hình đọc? |
| **Kiểm được** | Given có dữ liệu cụ thể? Then đo được, không chứa "nhanh", "hợp lý", "thân thiện", "v.v."? Flow/AC đọc được với người không biết code? |

Xong các AC, đọc lại một lượt từ góc người duyệt nghiệp vụ: "ký vào đây thì mình đang đồng ý điều gì?" — câu trả lời phải trùng ý người yêu cầu.

Ở mức 1–3, "AC" trong bảng trên là dòng "Done khi", "BR/Out of Scope" là PRD §1, "UC" là tính năng.

### 3b. Soát chéo giữa các file (mức 1–3)

| Cặp | Câu hỏi kiểm |
|---|---|
| PRD tự thân | Các story Must gộp lại có giải được "Vấn đề" ở §1 không — còn đường nào (gọi điện, giấy, công cụ cũ) khiến vấn đề vẫn xảy ra? "Thành công khi" đo được bằng dữ liệu app ghi lại, hay phải đếm ngoài app? Mã story trùng hoặc đánh số lại? Story Must thiếu "Done khi" đo được? Story mâu thuẫn `Ngoài phạm vi`? "Done khi" của một story đòi điều thuộc story làm sau nó? Bảng §7 thiếu story Must, có story không tồn tại, thứ tự trái `Phụ thuộc`, phụ thuộc vòng, `Status` khác §2? Story chặn bởi `[OPEN]` nhạy cảm (tiền, quyền, bảo mật, dữ liệu cá nhân, pháp lý) mà chưa `Blocked`? Lỗi ở §3 trỏ story không có? |
| PRD ↔ wireframe | Mỗi `data-story` trỏ story có thật? Story Must có giao diện mà không có trên màn chính cũng không có trong danh sách màn §5? Nút/trường/màn trên wireframe mà PRD không nói (tính năng lẻn vào)? Chữ, số, trạng thái hiển thị khớp "Done khi"? |
| PRD ↔ TDD | Mỗi story Must có hành động (§4); story có chỗ khó có luồng (§5)? TDD có bảng, API, tính năng PRD không đòi (thừa)? Bảng dữ liệu khớp PRD §4? Stack hợp giới hạn PRD §1 (thời hạn, ngân sách, nền tảng)? Quyết định bảo mật/quyền/chi phí đã có người quyết hay trỏ `[OPEN]` của PRD? `[OPEN]` bị chép sang TDD thay vì trỏ số? |
| Wireframe ↔ TDD | Dữ liệu hiển thị trên màn chính có nguồn trong TDD §3? |

Câu hỏi ở §5 dưới đây: không hỏi lại điều đã hỏi trong lúc phỏng vấn; người dùng chưa trả lời thì đã là `[OPEN]`, chỉ hỏi phát hiện mới.

## 4. Phân loại phát hiện

| Loại | Ví dụ | Làm gì |
|---|---|---|
| **Lỗi của mình, một cách sửa hiển nhiên, không đổi nghĩa nghiệp vụ** | trùng ID AC, sót placeholder `<…>`, link hỏng, chữ kỹ thuật trong AC, thiếu dòng `- Tests:`, AC thừa mình tự thêm | Sửa ngay, ghi vào danh sách "Đã tự sửa" |
| **Cần người quyết** | nhiều cách hiểu, giá trị tự đặt, mâu thuẫn với BR/ADR, thiếu luật cho một nhánh, mọi thứ dính tiền/quyền/bảo mật/dữ liệu cá nhân/pháp lý | Thành câu hỏi (§5) |
| **Ngoài phạm vi** | lỗi ở UC không liên quan, ý tưởng mở rộng | Ghi một dòng trong báo cáo, không sửa, không hỏi |

Bỏ AC thừa do chính mình thêm là "tự sửa"; bỏ thứ người dùng đã nêu là "cần người quyết".

## 5. Hỏi người dùng

- Chỉ hỏi điểm quyết định thật — câu trả lời làm đổi AC, flow, entity hoặc phạm vi. Không hỏi điều repo, spec, code trả lời được; không bày lựa chọn giả.
- Mỗi câu: bối cảnh một dòng (trích chỗ trong spec), 2–4 phương án cụ thể kèm hệ quả, đánh dấu phương án đề xuất và lý do. Agent có sẵn công cụ hỏi người dùng thì có thể dùng (tối đa 4 câu một lượt); không có thì liệt kê đánh số trong chat như ví dụ dưới rồi dừng chờ — cả hai cách đều đủ.
- Mặc định 3–8 câu; spec đơn giản thì ít hơn, kể cả 0. Mức 1–3 vừa phỏng vấn xong: chỉ hỏi phát hiện mới, thường 0–3 câu. Ưu tiên câu làm đổi nhiều AC nhất.
- Tiền, quyền truy cập, bảo mật, dữ liệu cá nhân, pháp lý: được đề xuất nhưng **không** tự áp phương án đề xuất khi người dùng chưa chọn (cổng cứng 2).

Ví dụ:

```
Nhóm: Đúng ý
Câu hỏi: Proposal ghi mã QR hết hạn sau 15 phút. Đơn đã quét mã nhưng tiền về ở phút 16 thì sao?
1. Vẫn nhận tiền, ghi nhận đơn (Đề xuất — khách đã trả, từ chối gây khiếu nại)
2. Tự hoàn tiền, huỷ đơn
3. Giữ tiền, chuyển nhân viên xử lý tay
```

## 6. Ghi lại

1. Câu trả lời làm đổi spec → sửa delta trong proposal (hoặc BR/UC ở mode `init`, PRD/TDD/wireframe ở mode `prd`). Người dùng chưa trả lời / "để sau" → `[OPEN]` có ngữ cảnh, không đoán.
2. Proposal hoặc `PRD.md`: điền mục `## Tự soát` (mẫu `proposal.md`, `prd.md`):

```markdown
## Tự soát
- Ngày: YYYY-MM-DD · audit.py: <kết quả> · verify.py: <kết quả>   (mức 1–3 không config: "script: không chạy (mức 1–3)")
- Đã tự sửa: <mỗi ý một cụm ngắn, hoặc —>
- Đã hỏi (N câu): <câu hỏi ngắn> → <lựa chọn, ai trả lời>
- Còn mở: <[OPEN] mới, hoặc —>
```

3. Mode `init`: không có proposal → không thêm mục mới vào BR/UC; quyết định đi thẳng vào nội dung, phần chưa rõ thành `[OPEN]`, tóm tắt trong câu trả lời.

## 7. Báo kết quả

Một khối ngắn: đối tượng đã soát · lệnh đã chạy + kết quả thật · số lỗi đã tự sửa · số câu đã hỏi và quyết định · `[OPEN]` còn lại · kết luận: **sẵn sàng đưa review hai phía** (mức 4) / **sẵn sàng lập kế hoạch và code** (mức 1–3), hoặc **cần sửa tiếp** (nêu gì). Rồi dừng — không code trong mode này.
