# Thuật ngữ (glossary)

Tên chuẩn ngành giữ tiếng Anh — để tra được tài liệu khác, để AI và người code đọc thống nhất; tên file, ID, mã giữ nguyên.
Cột tiếng Việt là lời giải thích cho người mới, không phải tên thay thế. Agent trả lời "X là gì" theo bảng này (SKILL.md, "Trả lời người dùng").

## Phương pháp

| Thuật ngữ | Tiếng Việt | Nghĩa — ví dụ | Gặp nó thì bạn… |
|---|---|---|---|
| **SDD** (Spec-Driven Development) | Làm theo đặc tả | Viết rõ *muốn gì* trước (spec), AI code theo đó; sai thì sửa spec trước rồi sửa code. Khác "vibe code": nói miệng rồi để AI tự đoán | Chọn mức kỹ (1–4), trả lời câu hỏi phỏng vấn |
| **Spec** | Đặc tả | Tài liệu ghi điều sản phẩm phải làm, đủ rõ để người khác (hoặc AI) làm mà không đoán | Đọc và sửa khi thấy sai ý |
| **MVP** (Minimum Viable Product) | Bản nhỏ nhất dùng được | Bản đầu chỉ có vài việc cốt lõi để thử với người dùng thật, vd app đặt lịch chỉ có "đặt", "xem lịch", "huỷ" | Chọn "ba việc" quan trọng nhất |
| **Greenfield / Brownfield** | Dự án mới / code đang chạy | Greenfield viết spec từ ý tưởng; brownfield viết spec từ code + log + người vận hành, kể cả hành vi xấu | Nói cho agent biết repo đã có code chạy thật chưa |
| **Level** (mức 1–4) | Mức kỹ | 1 PRD · 2 + wireframe · 3 + TDD · 4 SDD đầy đủ; mức sau chỉ thêm phần | Chọn mức; lớn dần thì "nâng lên" (promote) |
| **Skill** (gọi `/mk:specs`) | Bộ hướng dẫn cho agent | Thư mục `mk-specs` dạy agent làm SDD. Trên Claude Code gọi thẳng bằng `/mk:specs` — kiểu `bộ:tên`: `mk` là tên bộ skill, `specs` là tên skill (`/mk-specs` cũng chạy); agent nào cũng tự đọc khi bạn nói việc liên quan spec | Gõ `/mk:specs` rồi nói việc, hoặc nói thẳng ("viết PRD cho app này") |
| **System spec / Feature spec** | Đặc tả hệ thống / Đặc tả tính năng | System spec ghi luật bền vững luôn nạp vào context (`AGENTS.md`); Feature spec là đề xuất thay đổi ngắn hạn (`specs/changes/`), xong thì đưa vào archive | Giữ luật chung ở `AGENTS.md`, chi tiết việc ở proposal |
| **Specification drift** | Trôi dạt đặc tả | Hiện tượng code và spec dần xa rời nhau do sửa code không cập nhật spec hoặc lười kiểm chứng | Chạy `audit.py`, `verify.py`, đưa kiểm spec vào CI |

## Mức 1–3 (dự án nhỏ, MVP)

| Thuật ngữ | Tiếng Việt | Nghĩa — ví dụ | Gặp nó thì bạn… |
|---|---|---|---|
| **PRD** (Product Requirements Document) | Tài liệu yêu cầu sản phẩm | File `specs/PRD.md`: vì sao làm, ai dùng, các story, thứ tự làm | Trả lời phỏng vấn, đọc lại, sửa chỗ sai ý |
| **Persona** | Chân dung người dùng | Một nhóm người dùng mô tả bằng 7 ô (vai, bối cảnh, đang làm bằng gì, nỗi đau, quen công nghệ, thành công, không chấp nhận); mã `P1`, `P2` | Điền khung; càng thật càng ra story đúng |
| **User story** | Câu chuyện người dùng | Một việc người dùng làm được, dạng "Là P1 (chủ tiệm), tôi muốn xem lịch trong ngày, để biết ai tới"; có mã cố định như `BOOK-01` | Xác nhận đúng việc họ cần |
| **MoSCoW** (Must / Should / Could / Won't) | Mức ưu tiên | Must = thiếu thì không ra mắt; Should = nên có; Could = để sau được; Won't = lần này không làm | Chọn Must thật ít |
| **Acceptance criteria** (trong PRD gọi là "Done khi") | Xong khi nào | Điều kiện đo được để nói story xong, vd "khách đặt 9:00 thì giờ đó không ai đặt được nữa" | Kiểm con số có đúng ý không |
| **Given / When / Then** | Cho trước / Khi / Thì | Cách viết "Done khi": dữ liệu ban đầu → hành động → kết quả thấy được | Đọc như một kịch bản thử |
| **Wireframe** | Bản phác màn hình | `specs/wireframe.html`: màn chính vẽ tĩnh, mở bằng trình duyệt, chưa có logic | Mở xem, nói chỗ nào sai |
| **TDD** (Technical Design Document) | Thiết kế kỹ thuật | `specs/TDD.md`: dùng công nghệ gì, lưu dữ liệu thế nào, các hành động chính. (Không phải Test-Driven Development) | Duyệt các lựa chọn; tiền/quyền thì bạn quyết |
| **Stack** | Bộ công nghệ | Các công nghệ chọn cho từng lớp: giao diện, máy chủ, CSDL, đăng nhập, nơi chạy | Nói "đơn giản nhất" nếu không có ý riêng |
| **Status** của PRD (`draft` / `ready`) | Trạng thái | `ready` = có ít nhất một việc Must làm được ngay; `draft` = còn chờ câu trả lời | Trả lời các `[OPEN]` đang chặn |
| **Giả định / Để sau / Ngoài phạm vi** | — | Giả định: điều agent tạm coi là đúng (thường do bạn nói "tuỳ bạn"); Để sau: có thể làm ở bản sau; Ngoài phạm vi: chắc chắn không làm bản này | Đọc Giả định, sửa chỗ sai |
| **Promote** | Nâng lên SDD đầy đủ | Dựng BR/UC/AC/ADR từ PRD, giữ mã story, đối chiếu code đang chạy | Làm khi dự án có nhiều người, tiền, sống lâu |

## Mức 4 (SDD đầy đủ)

| Thuật ngữ | Tiếng Việt | Nghĩa — ví dụ | Gặp nó thì bạn… |
|---|---|---|---|
| **BR** (Business Requirement) | Yêu cầu nghiệp vụ | Vì sao làm: mục tiêu đo được, người dùng, ngoài phạm vi. Mã `BR-01` | Chốt mục tiêu và điều không làm |
| **UC** (Use Case) | Ca sử dụng | Một việc người dùng/hệ thống làm từ đầu tới cuối: ai làm, khi nào, các bước, lỗi. Mã `UC-101` | Đọc luồng chính, bổ sung case "đương nhiên" |
| **AC** (Acceptance Criteria) | Tiêu chí nghiệm thu | Điều kiện đo được của một UC, mỗi cái có test. Mã `AC-1` trong UC | Kiểm đúng luật nghiệp vụ |
| **Entity** | Khái niệm nghiệp vụ | Thứ hệ thống quản lý: Đơn hàng, Lịch hẹn… — nghĩa, trạng thái, luật; không phải bảng CSDL | Kiểm tên gọi đúng cách cả nhà vẫn gọi |
| **ADR** (Architecture Decision Record) | Ghi chép quyết định | Một quyết định quan trọng: bối cảnh, chọn gì, **đã loại gì và vì sao**, ai quyết. Mã `ADR-01` | Quyết, hoặc hỏi lại khi thấy lý do yếu |
| **Proposal / change** | Đề xuất thay đổi | `specs/changes/<ngày>-<tên>/proposal.md`: đổi gì trong spec trước khi code | Duyệt phần nghiệp vụ |
| **Plan** (`plan.md`) | Kế hoạch làm | File cạnh proposal khi thay đổi lớn (> 5 AC thêm/sửa hoặc `- Quy mô: lớn`): các phase, mỗi phase nêu `UC-xxx AC-n` nó làm, phụ thuộc, cách kiểm, cách quay lui | Xem thứ tự làm có hợp lý không |
| **Context** | Vùng nghiệp vụ | Một mảng có ngôn ngữ riêng (catalog, checkout…); mỗi vùng một thư mục trong `specs/` | Gộp/tách khi thấy một từ mang hai nghĩa |
| **Traceability** | Truy vết | `traceability.md` sinh tự động: UC ↔ AC ↔ test; lỗi production tìm ra spec trong 1 phút | Xem AC nào chưa có test |
| **Characterization test** | Test chụp hành vi | Test ghi lại code cũ *đang* làm gì (đúng hay sai) trước khi sửa, để biết có đổi hành vi không | Đồng ý trước khi refactor code cũ |
| **AC Coverage / Spec Coverage / Trace Ratio** | Chỉ số | Tỉ lệ AC có test · UC đang chạy có AC có test · commit mang mã UC | Theo dõi Trace Ratio trước |
| **Structured consultation** | Tham vấn có cấu trúc | Khuôn hỏi 4 phần khi agent gặp mơ hồ lúc apply: câu hỏi · phương án · điều khoản spec liên quan · hệ quả từng phương án | Trả lời chọn phương án; tiền/quyền thì bạn quyết |
| **Evidence-backed acceptance** | Nghiệm thu dựa trên bằng chứng | Gói bằng chứng chứng minh hoàn thành thay đổi (AC ↔ test xanh, DoD/CI, rationale, link spec) trong proposal | Thẩm định gói bằng chứng thay vì đọc từng dòng diff code |
| **Norm encoding** | Mã hoá quy tắc | Quy tắc lặp 3 lần: lỗi sửa lặp lại 3 lần được tổng quát hoá thành điều khoản chuẩn mực đưa vào `AGENTS.md` ngoài khối | Duyệt PR thêm luật mới vào `AGENTS.md` |
| **Graduated autonomy** | Thang tự chủ phân tầng | Mức tự chủ của agent định rõ theo loại việc (vá nhỏ/deps: tự động; tính năng: tự động + tham vấn; bảo mật/tiền: duyệt plan trước) | Xem và điều chỉnh bảng tự chủ trong `AGENTS.md` |
| **mk:cook** | Skill làm code theo proposal | Skill thứ hai của mk-lab: cổng bằng máy trước khi code và trước khi báo xong, test trước theo AC, làn giao diện, ghi bằng chứng; cài `bash ~/.mk-lab/install.sh --global --skill mk-cook` (hoặc `--project .`) | Nhờ "làm proposal X" khi proposal đã duyệt |
| **DESIGN.md** | Hợp đồng giao diện | File ở gốc repo: token màu, chữ, khoảng cách, bề mặt, component kèm trạng thái, bố cục. Code giao diện chỉ dùng token trong đó; hành vi vẫn nằm ở AC | Duyệt khi tạo; muốn đổi giao diện thì sửa file này trước |
| **mk:fix** | Skill sửa lỗi theo spec | Skill của mk-lab: tái hiện lỗi, tra AC bằng `ac.py`, xếp loại rồi mới sửa; lỗi chưa có AC thành proposal nháp; cài `bash ~/.mk-lab/install.sh --global --skill mk-fix` | Báo "lỗi: …", "CI đỏ", "test chập chờn", "sửa <báo cáo> SEC-2" |
| **Loại lỗi** | Bug category | Một trong bốn, xét theo thứ tự (trừ hai AC đang chạy mâu thuẫn → `luật sai`, xét trước hết): `code sai AC` (AC đang chạy bị vi phạm — sửa code), `luật sai` (code đúng AC nhưng AC không như ý, hoặc hai AC mâu thuẫn — proposal), `thiếu AC` (chưa AC nào nói — proposal), `hạ tầng` (build/CI/phụ thuộc, không AC nào bị vi phạm — sửa thẳng) | "Lỗi này loại gì?" |
| **Tái hiện** (reproduce) | Làm lỗi hiện lại | Lệnh ở máy, log lượt CI hỏng, hoặc kịch bản tay cho thấy lỗi — có rồi mới sửa | "Chưa tái hiện được nên chưa sửa" |
| **Phiếu sửa lỗi** | Bug fix record | Triệu chứng · Tái hiện · Loại · AC · Nguyên nhân gốc (`file:dòng`) · Sửa · Kiểm · Vùng ảnh hưởng — trong câu trả lời và thân commit | Đọc khi duyệt commit `fix(UC-…)` |
| **mk:secu** | Skill soát bảo mật | Skill của mk-lab, chỉ đọc: hỏi đáp tập trung hoặc soát một phạm vi; ghi báo cáo `specs/security/<ngày-tên>.md`, không sửa code; cài `bash ~/.mk-lab/install.sh --global --skill mk-secu` | "Route này có lộ dữ liệu không?", "soát bảo mật nhánh này" |
| **Phát hiện** (`SEC-n`) | Security finding | Một lỗ hổng ứng viên trong báo cáo soát, gọi bằng `<ngày-tên> SEC-n`; cần sáu sự kiện (ai, đầu vào, kiểm soát thiếu, ranh giới, tài sản, hậu quả) + dấu vết `file:dòng` | Nhờ mk-fix "sửa 261027-toan-repo SEC-2" |
| **Kết luận / Mức** | Verdict / severity | `xác nhận` (có Mức: nghiêm trọng · cao · trung bình · thấp), `cần kiểm thêm` (không Mức, nêu điều còn thiếu), `bác bỏ` (nêu lý do) | Chỉ `xác nhận` mới cần sửa |
| **Độ tin nguồn** (N1–N4) | Trust level of data | N1 người dùng/bên ngoài gửi vào · N2 dữ liệu đã lưu từ người dùng · N3 cấu hình, code nội bộ · N4 hệ thống; cùng một đoạn code, an toàn hay nguy hiểm tuỳ dữ liệu từ đâu | Đọc trong báo cáo soát |
| **mk:ship** | Skill triển khai | Skill của mk-lab: đưa code đã commit lên môi trường theo `DEPLOY.md`, Cloudflare Workers trước; cổng `ship.py check` trước, `ship.py smoke` sau; cài `bash ~/.mk-lab/install.sh --global --skill mk-ship` | "deploy lên staging", "đẩy production" |
| **DEPLOY.md** | Hợp đồng triển khai | File ở gốc repo: nền tảng, môi trường (nhánh, lệnh, URL), kiểm sau triển khai, bí mật cần có, việc trước triển khai, cách quay lui; sửa không cần proposal | Mở khi hỏi "deploy thế nào?" |
| **Môi trường** (production / thử) | Environment | Nơi chạy bản triển khai. Tên `production`, `prod`, `…-production`, `…-prod` là production (cần bạn xác nhận, chặn chặt hơn); còn lại là thử | "staging", "production" |
| **Smoke** (kiểm sau triển khai) | Kiểm nhanh sau khi lên | Gọi vài đường dẫn trong `DEPLOY.md`, so mã HTTP và chữ cần có | Hỏng ở production → cân nhắc quay lui |
| **Rollback** | Quay lui | Trả bản đang chạy về phiên bản trước; không trả lại dữ liệu (D1/KV/R2) | Agent hỏi trước khi chạy |
| **mk:skill-creator** | Skill dựng skill | Skill của mk-lab để tạo, sửa, kiểm skill **của bộ mk** theo một chuẩn: `init.py` tạo khung, `validate.py` kiểm bằng máy, dry-run bằng agent khác; cài `bash ~/.mk-lab/install.sh --global --skill mk-skill-creator` | "tạo skill mới", "kiểm skill mk-ghi-chu" |
| **validate.py** (kiểm skill) | Kiểm skill bằng máy | Script của mk-skill-creator: in từng dòng `OK`/`LỖI` (tên, frontmatter, cấu trúc, số dòng, nội dung, scripts), thoát 1 khi có lỗi; chỉ đọc | Sửa từng dòng `LỖI` tới khi `Kết quả: 0 lỗi` |
| **init.py**, chỗ trống mẫu `{{…}}` | Khung skill | `init.py <tên> --path skills` tạo `skills/mk-<tên>/SKILL.md` từ khung; chỗ `{{…}}` là phần bạn (hoặc agent) phải điền trước khi kiểm | Điền hết rồi chạy `validate.py` |
| **THIRD_PARTY_NOTICES.md** | Thông báo giấy phép bên thứ ba | File giữ thông báo giấy phép của đoạn phỏng theo văn bản người khác; nằm ở gốc repo và trong thư mục skill có đoạn đó (đi theo bản cài) | Không cần làm gì; đừng xoá khi chép skill |

## Đánh dấu trong spec

| Dấu | Nghĩa | Gặp nó thì bạn… |
|---|---|---|
| `[OPEN] O1: …` | Câu hỏi chưa có câu trả lời | Trả lời; agent sửa spec theo câu trả lời |
| `[DIVERGENCE]` | Hai nguồn nói khác nhau (tài liệu vs code), chưa quyết bên nào đúng | Quyết bên đúng |
| `Blocked ([OPEN] O3)` | Story đang chờ câu trả lời về tiền, quyền truy cập, bảo mật, dữ liệu cá nhân hoặc pháp lý — không ai code nó | Trả lời O3 là story chạy tiếp |
| `⚠ Chưa có test` | AC chưa có test tự động, kèm lý do | Chấp nhận lý do hoặc yêu cầu thêm test |
| `Partial` | Story/UC mới làm một phần, phần thiếu ghi rõ | Quyết làm tiếp hay để sau |

## Git và phiên bản

| Thuật ngữ | Tiếng Việt | Nghĩa — ví dụ | Gặp nó thì bạn… |
|---|---|---|---|
| **Commit** | Lần lưu thay đổi | Một lần lưu mã nguồn vào lịch sử git, kèm một dòng mô tả | Commit sau mỗi việc xong |
| **Conventional commit** | Commit theo mẫu | `feat(BOOK-01): khách đặt lịch` — loại (`feat` thêm, `fix` sửa, `docs` tài liệu…) + mã story/UC | Nhìn mã là biết commit thuộc việc nào |
| **SemVer** (X.Y.Z) | Số phiên bản | Z tăng: sửa lỗi · Y tăng: thêm tính năng, cập nhật bình thường · X tăng: cập nhật cần bạn làm thêm bước | Gặp X mới thì đọc CHANGELOG trước khi cập nhật |
| **Release / tag** | Bản phát hành | Một số phiên bản đã chốt, không sửa lại; lỗi thì ra bản sau | Cập nhật bằng `install.sh --update` |
| **Hook** (Claude Code) | Lưới chặn tự động | Lệnh Claude Code tự chạy trước khi agent sửa file/chạy lệnh; mk-specs dùng để chặn sửa tay file sinh và commit thiếu mã | Bị chặn thì làm theo lý do nó in ra; không phải tắt |
| **Lệnh đã tin** (trusted command) | Lệnh test bạn đã cho phép | `tests.list_command` trong `specs/mk-specs.yml` là lệnh shell của repo; mk-specs chỉ chạy nó khi bạn đã đồng ý đúng lệnh đó cho repo ở đúng thư mục đó (ghi trong `~/.config/mk-specs/trusted-commands`, xoá dòng để thu hồi). Tin lệnh cũng là tin các file của repo mà lệnh gọi. Chưa đồng ý → kiểm spec dừng với mã 3 và in lệnh | Đọc lệnh; tin thì cho agent chạy lại với `--trust-list-command`, không thì dùng `--tests`; CI: thêm cờ vào pipeline |
| **CHANGELOG** | Nhật ký thay đổi | `CHANGELOG.md` của skill: mỗi bản có gì mới, viết bằng lời người dùng | Đọc trước khi cập nhật |
