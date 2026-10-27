# Vòng đời một thay đổi hành vi

Áp dụng cho: tính năng mới, đổi luật (nhất là tiền), đổi API, đổi điều người dùng thấy. Sửa nhỏ giữ nguyên AC: xem §6.

```
change ──► tự soát ──► review hai phía ──► commit 1 (propose) ──► apply: test đỏ → code → xanh ──► commit 2 (code)
       ──► merge: UC/ADR/History/archive/gen/check ──► commit 3 (merge)
```

## 1. Đề xuất (mode `change`)

1. Đọc `specs/README.md`, UC/BR/ADR liên quan, `open-issues.md` (có `[OPEN]`/`[DIVERGENCE]` nào thay đổi này đóng được không).
2. Tạo `specs/changes/<yyMMdd>-<slug>/proposal.md` từ `assets/templates/proposal.md`. `yyMMdd` = ngày hôm nay, `slug` không dấu, gạch nối.
3. Điền:
   - **Vì sao**: vấn đề thật, trích nguyên lời người yêu cầu. Chưa nói giải pháp.
   - **BR**, **Đụng tới** (UC + context), **Đóng** (mục open-issues).
   - **Thay đổi spec**: delta `ADDED`/`MODIFIED`/`DEPRECATED` AC theo Given/When/Then, cụ thể tới con số; đoạn flow đổi viết bằng ngôn ngữ nghiệp vụ; entity mới/đổi. Mỗi AC nằm dưới `### UC-xxx` (hoặc ghi `ADDED UC-xxx AC-n`) để công cụ đếm được.
   - **Quyết định**: ADR nháp khi có lựa chọn đáng ghi — luôn có phương án bị loại.
   - **Thiết kế**: file/symbol, migration (ghi rõ sao lưu dữ liệu thật trước), rủi ro, phần nào AI làm / phần nào người quyết.
   - **Quy mô** + **plan**: thêm/sửa > 5 AC, hoặc thay đổi nhiều phần phụ thuộc nhau (vd giao diện + API + migration) → `- Quy mô: lớn` và `plan.md` cùng thư mục (mẫu `assets/templates/plan.md`): mỗi phase nêu `UC-xxx AC-n` nó làm, phụ thuộc, cách kiểm, cách quay lui; mọi AC thêm/sửa nằm trong đúng một phase.
4. Không AC thì không code. AC phải test được; không test được thì viết lại AC.
5. Proposal dài quá một màn hình đọc của người duyệt nghiệp vụ → tách thay đổi, hoặc dồn chi tiết kỹ thuật xuống "Thiết kế".
6. Tự soát (`references/review.md`): sửa lỗi của chính mình, hỏi người dùng các điểm cần quyết, điền `## Tự soát`. Chỉ sau đó mới đưa review hai phía.

## 2. Review hai phía

- **Nghiệp vụ** — chủ sản phẩm (hoặc người chịu hậu quả) đọc Vì sao + Thay đổi spec: đúng rule không, thiếu case "đương nhiên" nào không (tr.28–29, 53). Ghi tên + ngày + kênh vào `Người duyệt nghiệp vụ`.
- **Kỹ thuật** — một reviewer khác người viết: người, hoặc một phiên agent riêng (subagent, hoặc phiên chat mới) chỉ được giao proposal + code hiện có và các câu hỏi sau: khả thi không, đúng context không, AC test được không, exception thiếu không, migration an toàn không, có rule nào lẻn vào code mà spec không nói không. Khi xong việc thẩm định gói bằng chứng (`## Bằng chứng nghiệm thu`). Ghi kết luận vào `## Review kỹ thuật` và tên + ngày vào `Người duyệt kỹ thuật`. Sửa proposal theo nhận xét trước khi code. Chưa có ai review được → ghi `chờ`, Status `reviewing`, dừng.
- **Không ai tự duyệt**: agent viết proposal không đồng thời là reviewer kỹ thuật của nó; người yêu cầu không thay được bước review kỹ thuật (tr.42, 55).
- **Tiền, quyền truy cập, bảo mật**: AI chỉ nêu phương án + hệ quả; chủ sản phẩm chọn. Chưa chọn → Status `reviewing`, dừng.
- Chủ sản phẩm nói "cứ làm" (đã giao việc rõ): vẫn viết proposal và vẫn có review kỹ thuật, nhưng không cần chờ duyệt nghiệp vụ lần nữa — ghi `Người duyệt nghiệp vụ: <tên>, <ngày> (giao việc trực tiếp)`. Luật tiền/quyền/bảo mật mới phát sinh trong lúc làm vẫn phải hỏi.
- Duyệt xong: Status `approved`.

**Commit 1** — chỉ proposal: `docs(UC-xxx): propose <slug>`.

## 3. Thực hiện (mode `apply`)

Có skill `mk-cook` (một trong `.claude/skills/mk-cook`, `.agents/skills/mk-cook` của project; `~/.claude/skills/mk-cook`, `~/.agents/skills/mk-cook`) → làm theo `mk-cook`: nó chạy cổng bằng máy (duyệt, `plan.md`, bằng chứng), làn giao diện theo `DESIGN.md` và kiểm trên trình duyệt. Không có → làm theo các bước dưới đây.

1. Chỉ làm khi proposal `approved` (hoặc giao việc trực tiếp như trên) và commit 1 đã có.
2. Viết test cho từng AC mới/sửa **trước**, chạy thấy đỏ. Test kiểm hành vi, không mock lõi nghiệp vụ; test đầu tiên của một mẫu mới để người review kỹ (tr.27–28, 59). Bug tái hiện được → test đỏ trước, xanh sau.
3. Code tối thiểu cho các AC. Không thêm rule spec không nói.
4. Gặp câu hỏi nghiệp vụ hoặc tiền lệ mâu thuẫn mà spec chưa nói rõ → **dừng, không đoán**: tham vấn theo khuôn **Structured Consultation** (§5.8) gồm 4 phần:
   - *Bối cảnh & câu hỏi ngắn gọn*.
   - *Các phương án cân nhắc*.
   - *Điều khoản spec liên quan* (trích dẫn ID/AC đang làm, hoặc mục tiêu BR / Cổng cứng liên quan nếu chưa có điều khoản trực tiếp).
   - *Hệ quả cụ thể từng phương án*.
   Dính Cổng cứng 2 (tiền, quyền, bảo mật, pháp lý): agent chỉ đề xuất, bắt buộc dừng chờ chủ sản phẩm quyết. Chốt câu trả lời vào proposal / ADR ngay trong phiên, không đoán.
5. Test đỏ vì spec mơ hồ → về spec trước: chủ sản phẩm quyết → sửa AC → sửa test → sửa code (tr.39–40).
6. Ghi đường dẫn test vào dòng `- Tests:` của AC trong proposal (hoặc trực tiếp khi merge).
7. Chạy DoD của project (lệnh test/typecheck/build trong CLAUDE.md hoặc tương đương). Điền mục `## Bằng chứng nghiệm thu` vào proposal: AC ↔ test xanh, trạng thái DoD/CI, rationale tóm tắt giải pháp (tham chiếu consultation/ADR nếu có), link truy vết.

**Commit 2** — test + code: `feat(UC-xxx): …` / `fix(UC-xxx): …` / `refactor(UC-xxx): …`. Không gộp file spec chính vào commit này (proposal cập nhật giữa chừng thì được).

## 4. Hợp nhất (mode `merge`)

1. Chép delta vào UC chính: AC mới/sửa (kèm `- Tests:`), flow, exceptions, entity. Chữ mới theo ngôn ngữ nghiệp vụ; chi tiết kỹ thuật vào `## Traceability`. Toàn bộ gói `## Bằng chứng nghiệm thu` lưu vĩnh viễn trong proposal ở `specs/changes/archive/`, UC chỉ nhận dòng History mang hash commit code kèm link mở proposal, không chép nội dung gói bằng chứng vào UC (tránh phình UC).
2. Thêm dòng History mỗi UC bị đụng: `- vN (YYYY-MM-DD, commit \`<hash commit 2>\`): <đổi gì> (change [<slug>](../changes/archive/<slug>/proposal.md))`. Nếu đã ghi `chưa commit` thì chạy `python3 .claude/skills/mk-specs/scripts/commit-hash.py <hash>`.
3. ADR: chép vào `decisions.md` với ID kế tiếp (dòng mục lục + mục riêng), điền Verified in code; UC thêm vào dòng `- Decisions:`.
4. Đóng `[OPEN]`/`[DIVERGENCE]` đã giải quyết (xoá dòng, ghi vào History "đóng [OPEN] …").
5. Proposal: Status `archived`, dòng `Commit` điền hash; chuyển thư mục sang `specs/changes/archive/`. Sửa link tương đối bị lệch do chuyển thư mục.
6. `specs/README.md`: thêm một dòng banner "Hợp nhất change …" (gen.py tự giữ 5 dòng mới nhất); bảng chỉ mục UC nếu có UC mới/đổi tên/status.
7. Chạy `gen.py` rồi `verify.py` (xem traceability.md). Phải ra 0 unresolved.

8. **Norm encoding (§5.7)**: nếu trong quá trình apply/review có lỗi của agent bị sửa lặp lại qua 3 lần → đề xuất tạo một PR đưa điều khoản chuẩn mực vào `AGENTS.md` ngoài khối, kèm linter/sensor nếu kiểm tra được bằng máy.
**Commit 3** — `docs(UC-xxx): merge <slug>`.

## 5. Commit message

- Subject: `<type>(<ID>[,<ID>…]): <mô tả ngắn>`; ID là UC/BR/ADR đã có trong specs, ví dụ `feat(UC-204): hết hạn mã QR sau 15 phút`, `fix(UC-204,UC-207): …`, `docs(BR-03): làm rõ out of scope`, `docs(ADR-12): supersede by ADR-15`.
- type: `feat` · `fix` · `refactor` · `test` · `docs` · `chore` · `perf` · `build` · `ci`.
- Việc toàn repo không gắn được UC dùng scope miễn trừ trong `metrics.exempt_scopes` (mặc định `specs`, ví dụ `chore(specs): …`, `chore(deps): …`). Commit miễn trừ không tính vào Trace Ratio.
- Body (khuyến nghị): AC đã làm (`AC-1, AC-3`), link proposal, "AI usage" (AI sinh phần nào, người quyết phần nào).
- Mode `commit`: đọc `git diff --staged`, xác định UC/BR/ADR bị đụng (từ file spec, proposal, hoặc `## Traceability` trỏ tới file code), đề xuất subject đúng mẫu; không tìm được ID → hỏi, hoặc đề xuất mở proposal/sửa spec trước. Không tự commit nếu người dùng chưa yêu cầu.

## 6. Đường tắt: sửa nhỏ, không đổi hành vi

Typo, đổi chữ, refactor giữ nguyên AC, sửa test citation, bug fix không đổi AC, sửa token trong `DESIGN.md` (giao diện, không phải hành vi — hành vi vẫn ở AC), sửa `DEPLOY.md` (cách triển khai, không phải hành vi):
- Không cần thư mục change.
- Vẫn cập nhật spec trong cùng thay đổi: History của UC bị đụng, AC/`[OPEN]`/`[DIVERGENCE]` liên quan.
- Bug tái hiện được → test đỏ trước, xanh sau (test thuộc AC đang bị vi phạm; chưa có AC nào nói → đó là thay đổi hành vi, đi đường đầy đủ — trừ lỗi hạ tầng, xem dưới).
- Hai commit: code (`fix(UC-xxx): …`) rồi spec (`docs(UC-xxx): …`, History mang hash commit code); hoặc một commit nếu chỉ sửa spec.
- Lỗi hạ tầng (build, CI, typecheck, phụ thuộc, cấu hình) mà không Then nào của AC bị vi phạm: lệnh hỏng thất bại trước, thành công sau; không History UC; commit scope miễn trừ (`metrics.exempt_scopes`) hoặc mã ADR liên quan.
- Refactor lớn: không gộp với đổi luật trong cùng thay đổi; cần characterization test (workflow-bootstrap.md §3).
- Có skill `mk-fix` (một trong `.claude/skills/mk-fix`, `.agents/skills/mk-fix` của project; `~/.claude/skills/mk-fix`, `~/.agents/skills/mk-fix`) và người dùng báo lỗi hành vi của code → làm theo `mk-fix`: tra AC, xếp một trong bốn loại (`code sai AC` · `luật sai` · `thiếu AC` · `hạ tầng`), chỉ `code sai AC` và `hạ tầng` được sửa code ngay. Lỗi chữ trong spec vẫn theo mục này.

## 7. Đổi hướng giữa chừng

- Proposal sai sau khi đã duyệt → sửa proposal, ghi một dòng "Điều chỉnh YYYY-MM-DD: …" cuối `## Vì sao`, xin duyệt lại phần đổi.
- Bỏ thay đổi → Status `rejected` kèm lý do, chuyển vào `archive/`; không xoá.
- Hai change chạm cùng UC → change hợp nhất sau phải rebase delta lên UC đã đổi.

## 8. Definition of Done (chung)

Spec đã cập nhật · mọi AC đụng tới có test (hoặc `⚠ Chưa có test` + lý do) · `[DIVERGENCE]`/`[OPEN]` liên quan đã đóng hoặc ghi lý do giữ · gen + verify sạch · lệnh test/build của project xanh · đã chạy thử đường thay đổi · không còn `chưa commit` · ba commit (hoặc hai cho sửa nhỏ) có ID. Project thêm điều kiện riêng trong CLAUDE.md/AGENTS.md.
