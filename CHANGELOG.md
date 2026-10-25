# Nhật ký thay đổi

Mỗi bản có số dạng `X.Y.Z`:

- **Số cuối (Z)** tăng: sửa lỗi nhỏ, cách dùng không đổi.
- **Số giữa (Y)** tăng: có thêm tính năng; cập nhật xong dùng tiếp bình thường.
- **Số đầu (X)** tăng: cập nhật xong bạn cần làm thêm một bước — bản đó sẽ ghi rõ bước gì.

Cập nhật: `bash ~/.mk-lab/install.sh --update`. Agent cũng tự nhắc khi có bản mới.

## Chưa phát hành

Dự kiến: v2.2.0

**Mới**

- **Tuỳ chọn cấu hình `layout`**: cho phép chọn trực tiếp giữa `layout: layers` (Biến thể 1 — Layer-first, mặc định theo sách SDD) hoặc `layout: contexts` (Biến thể 2 — Bounded Context ở gốc) trong `specs/mk-specs.yml` mà không cần cấu hình glob phức tạp.
- **Chuẩn hoá câu hỏi lựa chọn khi `init`**: khi khởi tạo đặc tả SDD mức 4 (`/mk:specs` mode `init`), agent hướng dẫn và đưa ra lựa chọn có cấu trúc giữa Biến thể 1 và Biến thể 2 nếu chưa được yêu cầu cụ thể.

## v2.1.0 — 25/10/2026

**Mới**

- **Cấu trúc Biến thể 1 là mặc định**: khi khởi tạo đặc tả SDD mức 4 (`/mk:specs` mode `init`), cấu trúc được tạo mặc định theo Biến thể 1 (Layer-first theo sách SDD của anh Huy: `business-requirements/`, `entities/`, `use-cases/<context>/`, `changes/`, `README.md`).
- **Tự động nhận diện cấu trúc**: script tự động nhận diện cả Biến thể 1 (`use-cases/*` và `use-cases`) lẫn Biến thể 2 (`*` khi context nằm trực tiếp dưới `specs/`), đảm bảo tương thích ngược 100%.
- **Bỏ qua thư mục `_templates/`**: nếu dự án có thư mục mẫu `specs/_templates/` hoặc `specs/templates/`, scripts tự động bỏ qua, không tính là context và không báo lỗi liên kết giả định.
- **Gom câu hỏi mở từ Thực thể**: `gen.py` tự động gom các dòng `[OPEN]` và `[DIVERGENCE]` từ `specs/entities/` và `specs/entities.md` vào `open-issues.md`.

## v2.0.0 — 20/10/2026

**Cần làm khi cập nhật — mọi máy**

1. **Lệnh test trong cấu hình phải được bạn cho phép một lần.** Repo nào có `tests.list_command` trong `specs/mk-specs.yml`: lần đầu kiểm spec sau khi cập nhật, `verify.py` (và `gen.py` khi `citation_style: name`) **không chạy** lệnh đó mà in nó ra và dừng (mã 3). Đọc lệnh; tin thì chạy lại một lần với `--trust-list-command` (agent sẽ hỏi bạn, không tự làm):
   `python3 .claude/skills/mk-specs/scripts/verify.py --trust-list-command`
   Máy nhớ lệnh đó cho đúng repo đó (`~/.config/mk-specs/trusted-commands`). Lệnh đổi (vd qua PR), repo ở thư mục khác hay worktree khác → hỏi lại. Không dùng `list_command` thì bỏ qua.
2. **CI:** pipeline nào chạy `verify.py` (hoặc `gen.py` khi `citation_style: name`, hay `npm run specs:check`) trên repo có `tests.list_command` sẽ **đỏ** tới khi bạn thêm `--trust-list-command` vào lệnh đó, vd `python3 .claude/skills/mk-specs/scripts/verify.py --trust-list-command` hoặc `npm run specs:check -- --trust-list-command`. Thêm cờ **trong cùng commit** cập nhật `.claude/skills/mk-specs` lên bản này — bản scripts cũ không biết cờ và báo `unrecognized arguments`. Hoặc truyền danh sách test có sẵn: `--tests list.json`.
3. **Bản cài chung không do `install.sh` tạo.** Nếu `~/.claude/skills/mk-specs` hoặc `~/.agents/skills/mk-specs` có sẵn mà không có file `.mk-specs-manifest` lẫn `.mk-specs-source` (vd chép tay, hoặc cài bằng công cụ khác), `install.sh --global`/`--update` giờ báo `was not installed by install.sh` và không đụng vào. Kiểm đó đúng là mk-specs của bạn rồi chạy **một lần** với `--force`: `bash ~/.mk-lab/install.sh --update --force` (lần sau chạy như thường). Cài bằng `install.sh` hay dòng curl thì không gặp.
4. Mỗi repo đã cài mk-specs: khối mk-specs trong `AGENTS.md` có chữ mới (luật riêng của repo không nới được cổng cứng; gặp mã 3 thì hỏi bạn) — `--update --project .` ghi lại khối, commit cùng `.claude/skills/mk-specs`.
5. Đã đặt quyền `Skill(mk-specs)` trong `permissions.allow` hoặc `permissions.deny`: thêm `Skill(mk:specs)` cạnh nó (rule cũ không khớp tên gọi mới — deny cũ sẽ không còn chặn).

**Cần làm khi cập nhật — thêm cho máy đã cài trước bản này có thư mục `~/.mk-skills`**

Thư mục clone và biến môi trường đổi theo tên mới của repo: `~/.mk-skills` → `~/.mk-lab`, `MK_SKILLS_…` → `MK_LAB_…`. Tên cũ không còn tác dụng. Làm một lần, theo thứ tự:

1. Đã đặt biến nào bắt đầu bằng `MK_SKILLS_` (vd `MK_SKILLS_NO_UPDATE_CHECK=1` hoặc `MK_SKILLS_HOME=…` trong `~/.zshrc`)? Đổi thành `MK_LAB_…` (`MK_LAB_NO_UPDATE_CHECK`, `MK_LAB_HOME`) rồi mở terminal mới. Không đặt biến nào thì bỏ qua.
2. Cài lại bản chung — lệnh clone vào `~/.mk-lab` và thay bản cũ:
   `curl -fsSL https://raw.githubusercontent.com/mzavn/mk-lab/main/install.sh | bash -s -- --global`
3. Xoá thư mục clone cũ `~/.mk-skills` khi cả hai đúng: `cat ~/.claude/skills/mk-specs/.mk-specs-source` in đường dẫn kết thúc bằng `.mk-lab` (không còn `.mk-skills`), và `git -C ~/.mk-skills status --short` không in gì (bạn không sửa gì trong đó). Rồi: `rm -rf ~/.mk-skills`. Không có thư mục này thì bỏ qua.
4. Mỗi repo đã cài mk-specs: `bash ~/.mk-lab/install.sh --update --project .` (clone tay: thay `~/.mk-lab` bằng nơi clone) rồi commit `.claude/skills/mk-specs` như mọi lần cập nhật. Chưa làm bước này thì trong repo đó biến tắt nhắc mới (`MK_LAB_NO_UPDATE_CHECK`) chưa có tác dụng.

Tự clone repo bằng tay (không ở `~/.mk-skills`) và không đặt biến nào: thay bước 2–3 bằng `bash <nơi clone>/install.sh --update` như mọi lần, rồi làm bước 4. Bỏ qua cả bốn bước thì lệnh cũ `bash ~/.mk-skills/install.sh --update` vẫn chạy, nhưng các biến `MK_SKILLS_…` không còn tác dụng (vd đã tắt nhắc bản mới thì sẽ được nhắc lại) — ít nhất hãy làm bước 1.

**Mới**

- `install.sh` cài được nhiều skill: thêm `--skill <tên>` (mặc định `mk-specs`, lệnh cũ chạy như trước). `--update` giờ cập nhật mọi skill đã cài bằng `install.sh`. Thư mục skill cùng tên mà không do `install.sh` tạo thì bị từ chối thay vì bị ghi đè.
- Tên gọi mới theo kiểu `bộ:tên`: trên Claude Code gõ **`/mk:specs`** (menu `/` hiện tên này). `mk:` là quy ước đặt tên của bộ skill này, không phải plugin Claude Code. Quen gõ `/mk-specs` thì vẫn chạy — nên chuyển dần sang `/mk:specs`. Thư mục cài, cấu hình và lệnh cài giữ nguyên `mk-specs`. Cập nhật cả bản cài chung lẫn bản trong project: nếu chỉ cập nhật bản project thì `/mk-specs` vẫn chạy bản chung cũ, còn `/mk:specs` chạy bản project. Quyền `Skill(…)`: xem bước 5 ở trên.

- **Hấp thu nền tảng phương pháp luận từ bài báo SDD (Díaz et al., arXiv:2609.00252, 2026):**
  - **Tham vấn có cấu trúc (Structured consultation):** Khi agent đang code (`mode apply`) mà gặp câu hỏi nghiệp vụ hoặc tiền lệ mâu thuẫn, agent dừng lại và hỏi theo khuôn 4 phần chuẩn mực (bối cảnh & câu hỏi · các phương án · điều khoản spec liên quan · hệ quả từng phương án); nếu dính tiền/quyền/bảo mật thì bắt buộc dừng chờ bạn chọn.
  - **Gói bằng chứng nghiệm thu (Evidence-backed acceptance):** Mẫu proposal có thêm mục `## Bằng chứng nghiệm thu` (AC ↔ test xanh, trạng thái DoD/CI, rationale giải pháp, link truy vết) để reviewer thẩm định nhanh mà không phải đọc mò diff; lưu ở archive không làm phình Use Case chính.
  - **Phân định 3 lớp tài liệu khi khởi tạo (`mode init`):** Hướng dẫn rõ ranh giới giữa System spec (luật bền vững nạp thường trực trong `AGENTS.md`), Feature spec (đặc tả theo việc trong `changes/`), và Skill (thủ tục on-demand) để tránh phình context và chống trôi dạt đặc tả.
  - **Mã hoá quy tắc (Norm encoding):** Quy tắc lặp 3 lần — khi lỗi của agent bị sửa lặp lại 3 lần thì tổng quát hoá thành điều khoản chuẩn mực đưa vào `AGENTS.md` ngoài khối, kèm linter/sensor nếu có thể.
  - **Thang tự chủ phân tầng (Graduated autonomy):** Cung cấp mẫu phân loại mức tự chủ của agent theo loại việc (vá nhỏ/deps → tự động; tính năng → tự động + tham vấn; tiền/quyền/bảo mật → duyệt plan trước).
  - **`audit.py` phát hiện AC không dạng kiểm được:** Báo cáo các AC thiếu mệnh đề `Then` (hoặc `Thì`), nhắc nhở nguyên tắc "ràng buộc không công cụ nào kiểm được là mong muốn chứ không phải ràng buộc".
**Sửa**

- Repo đổi tên thành **mk-lab** (`github.com/mzavn/mk-lab`, bộ skill lập trình). Lệnh cài, nhắc bản mới và link CHANGELOG giờ trỏ tên mới; địa chỉ cũ trên GitHub tự chuyển sang tên mới.
- **An toàn khi mở repo lạ:** lệnh test khai trong cấu hình của repo không còn tự chạy — chỉ chạy khi bạn đã cho phép đúng lệnh đó (xem "Cần làm" bước 1). Agent được dặn không tự cho phép thay bạn.
- `--update` và dòng cài `curl` chỉ lấy **bản đã phát hành** (tag `vX.Y.Z` mới nhất), không bao giờ chạy mã chưa phát hành; checkout đang ở bản chưa phát hành (vd nhánh `dev` của người đóng góp) thì `--update` từ chối kèm hướng dẫn. Dòng curl bị đứt mạng giữa chừng không chạy gì.
- Luật riêng trong `AGENTS.md`/`CLAUDE.md` của repo chỉ bổ sung hoặc thu hẹp quy trình; dòng đòi nới cổng cứng (vd "agent tự duyệt") bị agent bỏ qua và báo lại.
- Gỡ khỏi project kiểm cả bản `.agents/skills/mk-specs`: có sửa tay thì từ chối như bản `.claude`.
- Cấu hình của repo không đọc được file ngoài repo qua `decisions_file`, `contexts`, `contexts_glob`; công cụ sinh file không ghi xuyên qua symlink (file trong `specs/` là symlink → báo lỗi, không ghi gì); mẫu tìm kiếm có dạng lặp-luân-phiên dễ treo (vd `(a|aa)+`) bị từ chối; cấu hình sai kiểu báo một dòng thay vì lỗi dài.

## v1.5.1 — 14/10/2026

**Sửa**

- Cấu hình của repo không thể làm các lệnh kiểm tra treo máy nữa: mẫu tìm kiếm dễ gây treo bị từ chối kèm gợi ý cách viết lại.
- Cài, cập nhật, gỡ không bao giờ đi xuyên qua thư mục là đường tắt (symlink), tránh ghi đè hay xoá nhầm bản cài ở chỗ khác.
- Bản skill trong `.agents/skills` của project được kiểm sửa tay trước khi cập nhật, như bản trong `.claude/skills`.
- Gỡ khi chưa cài thì báo "chưa cài" thay vì "đã gỡ".
- Câu hỏi mở trong yêu cầu nghiệp vụ (BR) giờ cũng hiện trong danh sách câu hỏi mở chung.

## v1.5.0 — 14/10/2026

**Mới**

- **Chặn tự động trên Claude Code.** Sau khi gọi skill, Claude Code tự chặn hai lỗi hay gặp: sửa tay file tổng hợp do máy sinh (`traceability.md`, `open-issues.md`) và commit thiếu mã việc (UC hoặc mã story). Bị chặn thì agent thấy lý do và cách làm đúng. Ở repo không dùng mk-specs, hoặc khi không chắc, nó không chặn gì. Agent khác vẫn làm theo hướng dẫn như cũ. Cần cập nhật cả bản cài chung (`--update --global`), vì Claude Code đọc bản đó.

**Sửa**

- Project mới cài xong chạy kiểm tra được ngay, không còn báo thiếu thư mục mẫu `checkout`. Project cài từ trước mà vẫn báo lỗi này: mở `specs/mk-specs.yml`, xoá mục `checkout` trong `contexts` (thông báo lỗi giờ chỉ rõ cách sửa).
- Hướng dẫn cài tay (không dùng `install.sh`) nói đủ bước để lần cập nhật sau không bị từ chối.
- Vài chỗ hướng dẫn lệch với cách skill thực sự làm đã được sửa cho khớp.
- An toàn hơn khi mở repo lạ: lệnh cài một dòng không còn lấy nhầm skill nằm sẵn trong thư mục đang đứng; cấu hình của repo không thể trỏ ra ngoài repo; lệnh chạy test khai trong cấu hình được in ra trước khi chạy; kiểm bản mới không bị lợi dụng để chạy lệnh lạ.


## v1.4.0 — 14/10/2026

**Mới**

- **Hỏi rõ người dùng của bạn là ai.** Khi viết PRD, agent đưa một khung ngắn để bạn mô tả từng nhóm người dùng: họ là ai, dùng lúc nào, đang làm việc này bằng gì, khổ ở đâu, rành công nghệ tới đâu, thế nào là xong việc với họ, điều gì họ không chịu. Từ đó agent suy ra tính năng và giao diện, thay vì tự đoán.
- **Giải thích thuật ngữ cho người mới.** Hỏi "PRD là gì?", "Done khi là gì?" là agent giải thích bằng tiếng Việt kèm ví dụ và việc bạn cần làm tiếp. Tên gọi chuẩn (PRD, AC, UC…) vẫn giữ nguyên. Câu hỏi lựa chọn nói rõ chọn cái nào thì được gì, mất gì; cuối mỗi việc có dòng "Bước tiếp theo của bạn".
- **Nhắc khi có bản mới.** Mỗi lần làm việc, agent kiểm một lần xem có bản mới không và nhắc kèm cách cập nhật; bạn đồng ý mới cập nhật. Việc kiểm chỉ xem số phiên bản trên GitHub, không gửi gì đi. Không muốn được nhắc: đặt biến môi trường `MK_SKILLS_NO_UPDATE_CHECK=1`.
- Từ bản này, cập nhật chỉ nhận bản đã chốt (có trong nhật ký này), không nhận phần đang làm dở.

**Sửa**

- Phần mô tả skill dài quá giới hạn nên có agent có thể không nạp đủ — đã rút gọn.

## v1.3.0 — 13/10/2026

**Mới**

- **Chọn mức kỹ theo dự án.** Dự án nhỏ hay MVP chỉ cần một bản PRD (mô tả sản phẩm, các việc người dùng làm, thứ tự làm); muốn thì thêm bản phác màn hình chính, rồi thêm thiết kế kỹ thuật. Dự án lớn dùng đặc tả đầy đủ. Agent phỏng vấn bạn, viết file, tự soát, rồi dừng trước khi code.
- Dự án lớn dần: một câu là agent nâng PRD lên đặc tả đầy đủ, giữ nguyên mã từng việc.
- Câu hỏi về tiền, quyền truy cập, bảo mật chưa trả lời thì chỉ việc liên quan phải chờ; các việc khác vẫn làm tiếp.

## v1.2.1 — 08/10/2026

**Mới**

- Cài bằng một dòng lệnh, không cần tải repo về trước.
- Cập nhật bằng một lệnh.
- Có hướng dẫn cài từng bước (`INSTALL.md`) — đưa cho agent là nó tự cài.

**Sửa**

- Khi không cập nhật được vì có file bị sửa tay, giờ báo đúng file nào.

## v1.2.0 — 08/10/2026

**Mới**

- **Agent tự soát lại spec vừa viết:** tìm chỗ mâu thuẫn, thiếu, thừa, chỗ tự đoán; tự sửa lỗi của mình và hỏi bạn những điểm cần quyết.
- Agent hỏi lại khi yêu cầu chưa rõ, không tự thêm thứ bạn không cần, chỉ sửa đúng chỗ.
- Dùng được trên mọi máy chỉ cần Python và git, không phụ thuộc công cụ nào khác.

## v1.1.0 — 07/10/2026

**Mới**

- Cài vào project chạy lại bao nhiêu lần cũng được; dùng được với nhiều agent (Claude Code, Codex, Cursor, Copilot, Gemini…).

## v1.0.0 — 07/10/2026

- Bản đầu: agent làm theo đặc tả — viết yêu cầu, đề xuất thay đổi, code theo đặc tả, hợp nhất, và tự kiểm đặc tả có khớp với test không.
