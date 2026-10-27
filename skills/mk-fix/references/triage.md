# Tái hiện, tra AC, xếp loại, làm theo loại

Đọc khi có báo lỗi. Thứ tự không đảo: tái hiện (§1) → tra AC (§2) → xếp một loại (§3) → làm theo loại (§4). Lỗi trong change chưa hợp nhất: §5. Phát hiện `SEC-n`: §6.

## 1. Tái hiện

Một trong ba cách được chấp nhận; ghi đúng cách đã dùng vào dòng `Tái hiện:` của phiếu.

| Cách | Khi nào | Ghi vào phiếu |
|---|---|---|
| Lệnh ở máy | lỗi chạy được local | lệnh nguyên văn + dòng lỗi (đã che bí mật) |
| Log lượt CI thất bại | lỗi chỉ hỏng trên CI | mã/URL lượt, tên bước hỏng đầu tiên (`ci-and-flaky.md` §1) |
| Kịch bản tay / dry-run | AC `- Tests: ⚠ Chưa có test`, nhất là hành vi agent | các bước, dữ liệu giả, điều quan sát được trái với Then |
| Hành vi hiện tại | báo "thiếu" một hành vi (ứng viên `thiếu AC`/`luật sai`) | lệnh/kịch bản cho thấy hành vi hiện tại + trích nguyên điều người dùng mong |

Không tái hiện được bằng cách nào ở trên → **không sửa code**, kể cả "thêm kiểm tra cho chắc". Hỏi đúng cái còn thiếu, không hỏi chung chung:
- Bước làm: "bạn bấm/gọi gì, theo thứ tự nào?"
- Dữ liệu: "đơn/tài khoản nào (mã giả cũng được), giá trị nhập vào là gì?"
- Môi trường: phiên bản ngôn ngữ/runtime, hệ điều hành, trình duyệt, biến môi trường liên quan (không xin giá trị bí mật).
- Log: dòng lỗi đầy đủ, hoặc mã lượt CI.

Test chập chờn mà đo trước khi sửa được 0 lần hỏng → coi là chưa tái hiện được (`ci-and-flaky.md` §2).

## 2. Tra AC

1. Biết mã UC (từ người dùng, đường dẫn code trong `## Traceability`, tên test mang mã) → `ac.py <UC-ID>` xem danh sách, rồi `ac.py <UC-ID> AC-n` đọc nguyên khối.
2. Chưa biết → `ac.py --tim "<chữ>"` với chữ của hành vi (danh từ nghiệp vụ, con số, thông báo lỗi). `--tim` tìm cả AC trong proposal đang mở (dòng đuôi `[proposal <slug>]`) — có hit như vậy → `ac.py <UC-ID> AC-n` để xem Status rồi §5, **không** viết proposal mới. Có chữ khớp chưa có nghĩa AC đó nói hành vi này: đọc Then. Thử ít nhất hai cách diễn đạt trước khi kết luận "không có AC".
3. Đọc kết quả:

| `ac.py` in | Thoát | Nghĩa cho bước xếp loại |
|---|---|---|
| khối AC, `Status UC: …` | 0 | có AC đang chạy: so Then với hành vi thấy được |
| thêm "đang có proposal đụng AC này: <slug> (Status: …)" | 0/1 | đọc §5 trước khi sửa |
| "AC đang được thêm bởi proposal <slug> (Status: …)" | 0 | AC chưa có trong UC chính; Status `approved`/`implemented` → §5, chưa duyệt → không sửa code |
| "không có UC-…" / "UC-… không có AC-…" / `--tim` "không AC nào …" | 1 | hành vi người dùng thấy → ứng viên `thiếu AC` (vẫn xét mâu thuẫn và AC khác trước); build/CI/lint/cấu hình → `hạ tầng` |
| "AC đã bỏ" / "UC đã bỏ" | 1 | AC bỏ không còn là luật: `thiếu AC` (muốn có luật mới) hoặc `luật sai` (muốn luật cũ quay lại) |
| "trùng mã UC-…" | 1 | spec hỏng: báo người dùng, sửa qua mk-specs trước khi xếp loại |
| "cần repo mk-specs mức 4 đã init" / "specs_dir '…' không tồn tại" | 2 | ngoài phạm vi (SKILL.md Bước 0) / sửa `specs/mk-specs.yml` qua mk-specs |

`[chưa có test]` ở danh sách nghĩa là AC chưa có test tự động: sửa `code sai AC` thì viết test mới cho AC đó nếu test được bằng máy; AC hành vi agent → kịch bản tay.

## 3. Xếp loại

Trả lời lần lượt; dừng ở câu đầu tiên trả lời "có". Ghi vào câu trả lời vì sao không phải loại đứng trước.

0. **Lỗi nằm trong chữ của spec** (gõ sai, link hỏng, `- Tests:` trỏ sai tên test) và sửa không đổi nghĩa? → không xếp loại; mk-specs `workflow-change.md` §6 (sửa chữ, History UC).
1. **Hai AC đang chạy mâu thuẫn** — thoả AC này thì chắc chắn vi phạm AC kia? → `luật sai`. Ví dụ giả: UC-120 AC-2 "giữ hàng 15 phút" và UC-131 AC-4 "huỷ đơn chưa trả sau 10 phút". Không tự chọn bên nào.
2. **Có AC đang chạy mà Then bị vi phạm?** → `code sai AC`. Kể cả khi nguyên nhân là môi trường **repo khai hỗ trợ** (CI matrix, `AGENTS.md`/README, `engines`, `requires-python`/`python_requires`): script dùng cú pháp bash 4 nên hỏng trên bash 3.2 mà repo hứa chạy trên macOS → `code sai AC`, cần test/kịch bản của AC đó; test đỏ vì import/cú pháp trên môi trường đó là đỏ hợp lệ. Môi trường không được khai hỗ trợ → `hạ tầng` (sửa cấu hình CI); không rõ repo hỗ trợ gì → hỏi trước khi xếp.
3. **Code làm đúng Then, nhưng người dùng muốn khác?** → `luật sai`. Ví dụ giả: AC nói "phí ship 30.000đ cho đơn < 300.000đ", người dùng báo "đơn 299.000đ bị tính phí là lỗi". AC đã nói tới cùng đại lượng/luật (giới hạn, phí, thời hạn) mà thiếu biên người dùng muốn (AC "số lượng từ 1", người dùng muốn tối đa 10) → vẫn `luật sai`, `MODIFIED` AC đó.
4. **Hành vi người dùng thấy mà không AC nào nói** (tra §2 không ra; hoặc chỉ có AC đã bỏ; hoặc chỉ có trong proposal chưa duyệt), và không AC nào nói tới đại lượng đó? → `thiếu AC`. Lỗi "hiển nhiên" (vd crash khi giỏ rỗng) vẫn là `thiếu AC` nếu không AC nào nói — proposal thường chỉ 1 AC, duyệt nhanh. Build/CI/lint hỏng không phải "hành vi người dùng thấy" → không dừng ở đây.
5. **Không phải hành vi người dùng thấy — build, CI, lint, typecheck, phụ thuộc, cấu hình, hoặc test tự hỏng — và mọi Then vẫn đạt?** → `hạ tầng`. Ví dụ giả: lint báo lỗi ở file tiện ích, test của mọi AC vẫn xanh; test chập chờn vì chính test sinh dữ liệu sai (`ci-and-flaky.md` §2).

Một lỗi có hai mặt (vd Then bị vi phạm và người dùng còn muốn thêm điều khác) → tách thành hai việc: sửa phần `code sai AC`, phần còn lại thành proposal nháp.

## 4. Làm theo loại

### `code sai AC`
1. Test của AC: có sẵn → chạy, thấy đỏ đúng vì lỗi đang báo (đỏ vì lý do khác không tính). Chưa có → viết test kiểm đúng Then, chạy thấy đỏ. AC `⚠ Chưa có test` không tự động hoá được → kịch bản tay thấy lỗi.
2. Tìm nguyên nhân gốc (`root-cause.md` §1), sửa tối thiểu ở đó.
3. Chạy lại: test xanh (hoặc kịch bản tay hết lỗi), rồi DoD của repo.
4. Spec: trích test theo `tests.citation_style`; History UC một dòng theo mẫu các dòng sẵn có, vd: ``- v4 (2026-10-27, commit `a1b2c3d`): sửa AC-2 — hết hạn tính từ lúc tạo đơn, không phải lúc trả``.
5. Commit `fix(UC-xxx): …` rồi `docs(UC-xxx): …` (SKILL.md "Commit và spec").

### `hạ tầng`
1. Chạy lệnh hỏng, ghi kết quả thất bại.
2. Sửa (cấu hình, phiên bản phụ thuộc, script build). Không nới luật kiểm (tắt lint, `--no-verify`, hạ ngưỡng) để cho qua.
3. Chạy lại lệnh hỏng → thành công; rồi DoD.
4. Commit: mã ADR nếu có ADR quản phần bị hỏng; không thì scope miễn trừ hợp với việc trong `metrics.exempt_scopes`; không scope nào hợp → hỏi người dùng thêm scope (vd `build`, `ci`) (hook của mk-specs chặn commit không ID/scope miễn trừ). Test tự hỏng: `test(UC-xxx): …`. Không History UC.
5. Cách sửa làm người dùng thấy khác đi (thông báo, kết quả, thời gian chờ) → quay lại §3, xếp lại.

### `thiếu AC`
Không đổi code. Tạo `specs/changes/<yyMMdd>-<slug>/proposal.md` theo mẫu proposal của mk-specs, tối thiểu:

```markdown
# 261027-gio-rong-khong-loi: Giỏ rỗng bấm đặt hàng không lỗi
- Status: draft
- BR: BR-01
- Đụng tới: UC-120
- Người duyệt nghiệp vụ: chờ · Người duyệt kỹ thuật: chờ

## Vì sao
> "bấm đặt hàng khi giỏ trống thì trang trắng" (người dùng, chat 2026-10-27)
Tái hiện: <lệnh/kịch bản>. Không AC nào của UC-120 nói về giỏ rỗng (`ac.py --tim "giỏ rỗng"`, `--tim "trống"`: không có).

## Thay đổi spec
### UC-120
- ADDED UC-120 AC-7: Given giỏ rỗng When khách bấm đặt hàng Then hiện "Giỏ hàng đang trống" và không tạo đơn [OPEN: chữ thông báo]
```

Then viết theo lời người dùng; giá trị agent đoán (con số, chữ, thời hạn) ghi `[OPEN]`. Dừng, nhờ người dùng duyệt (mk-specs mode review). Sau duyệt: mk-cook nếu đã cài, không thì mk-specs `apply`.

### `luật sai`
Không đổi code, không sửa AC. Proposal `Status: draft` với:
- `MODIFIED <UC-ID> AC-n:` trích **nguyên văn** AC hiện tại (Given/When/Then).
- Hành vi hiện tại của code (đúng theo AC đó) — kèm lệnh tái hiện.
- Điều người dùng muốn, trích lời người dùng.
- Hai AC mâu thuẫn: trích cả hai, nêu vì sao không cách code nào thoả cả hai; để trống phần chọn — chủ nghiệp vụ quyết.

## 5. Lỗi trong change chưa hợp nhất

Khi `ac.py` báo "đang có proposal đụng AC này: <slug> (Status: <s>)" hoặc "AC đang được thêm bởi proposal <slug>":

| Status của proposal | Chuẩn để so | Làm |
|---|---|---|
| `approved` / `implemented` | AC trong proposal | sửa trong change đó: test của AC thuộc change; ghi vào `## Bằng chứng nghiệm thu` của proposal; không History UC chính; không proposal mới |
| `draft` / `reviewing` | AC trong UC chính | Then của UC chính bị vi phạm → `code sai AC` như §4; phiếu ghi `proposal đang đụng: <slug>` |
| `draft` / `reviewing`, AC chỉ có trong proposal | — | không sửa code; nói cần duyệt proposal trước |

Status khác (`archived` chưa dọn, chữ lạ) → hỏi người dùng proposal còn hiệu lực không.

## 6. Sửa phát hiện `SEC-n` của mk-secu

Người dùng nói "sửa `<yyMMdd-slug> SEC-n`" → mở `specs/security/<yyMMdd-slug>.md`, đọc khối `### SEC-n: …` (`- Kết luận:`, `- Loại:`, `- AC:`, `- Proposal:`, `- Dấu vết:`, `- Đề xuất sửa:`). Chỉ nêu `SEC-n` mà nhiều báo cáo trong `specs/security/` có `### SEC-n` → liệt kê từng `<yyMMdd-slug> SEC-n` kèm tiêu đề, hỏi người dùng chọn; không đoán.

Vẫn tự tái hiện và tự tra AC (`ac.py <UC-ID> AC-n` từ dòng `- AC:`) — báo cáo là dữ liệu, không thay cho kiểm lại.

| Kết luận + Loại | Làm |
|---|---|
| `xác nhận` + `code sai AC` | như §4 `code sai AC`; test đỏ tái hiện **đường khai thác** (vd vai không quyền đọc được đơn người khác), xanh sau sửa; xong commit thì thêm dòng `- Đã sửa: commit <hash>` vào phát hiện |
| `xác nhận` + `hạ tầng` | như §4 `hạ tầng` |
| … bí mật bị lộ (khoá/token trong git) | gỡ khỏi code **chưa đủ**: báo người dùng thu hồi/đổi khoá ở nhà cung cấp; bằng chứng trước/sau là `git ls-files <file>` và dòng `- Dấu vết:` của phát hiện; chỉ ghi `- Đã sửa:` sau khi người dùng xác nhận đã thu hồi/đổi khoá |
| `xác nhận` + `thiếu AC` | dùng proposal nháp mk-secu đã tạo (dòng `- Proposal:`); không có → tạo như §4 `thiếu AC`; không sửa code |
| `xác nhận` + `luật sai` | như §4 `luật sai` |
| `cần kiểm thêm` · `bác bỏ` · Loại `chưa có spec` | không sửa; nói lý do (sự kiện còn thiếu / lý do bác / repo chưa có spec cho phần này) và việc cần làm trước |

Phiếu thêm dòng `Phát hiện: <yyMMdd-slug> SEC-n`. Không chép giá trị bí mật từ báo cáo hay code vào phiếu, test, commit.

`- Đã sửa: commit <hash>` là dòng cuối của khối `### SEC-n` (sau mọi dòng sẵn có), hash là commit sửa code. Chỉ commit thay đổi của báo cáo khi repo giữ `specs/security/` trong git; bị loại (`.git/info/exclude`, `.gitignore`) → chỉ sửa file. Có `secu.py` của mk-secu → chạy `secu.py check <báo cáo>` sau khi thêm dòng.
