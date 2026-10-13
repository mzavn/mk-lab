# mk-skills

Bộ skill cho AI coding agent (Claude Code, omp và các agent đọc thư mục skill chuẩn). Hiện có một skill: **`mk-specs`** — Spec-Driven Development (SDD).

*English summary at the end.*

## mk-specs là gì

`mk-specs` dạy agent làm việc theo spec: người chốt *ý định* trong thư mục `specs/` (Business Requirement, Use Case, Entity, Acceptance Criteria, ADR), AI viết test và code theo spec; khi có gì sai thì sửa spec trước rồi mới sửa code.

Skill gồm:

- **Quy trình** cho từng việc: khởi tạo specs (dự án mới hoặc codebase đang chạy), đề xuất thay đổi, tự soát spec vừa viết, thực hiện, hợp nhất, viết commit, kiểm tra, rà soát.
- **Mẫu** UC, BR, ADR, proposal, entity, README cho `specs/`.
- **Scripts** (Python chuẩn, không cần cài thêm gì): sinh `traceability.md` (UC ↔ AC ↔ test) và `open-issues.md` (mọi `[DIVERGENCE]`/`[OPEN]`), kiểm mọi tên test được trích có thật và mọi link mở được, tính chỉ số AC Coverage / Spec Coverage / Trace Ratio, báo cáo vệ sinh spec.
- **Cổng cứng**: không AC thì không code; luật tiền / quyền truy cập / bảo mật do người quyết, AI chỉ đề xuất; spec không nói thì không đoán; không tự duyệt; commit spec trước code và mọi commit mang ID UC/BR/ADR.
- **Kỷ luật viết spec** (theo [Karpathy guidelines](https://github.com/multica-ai/andrej-karpathy-skills)): yêu cầu mơ hồ thì hỏi lại trước khi viết; chỉ viết UC/AC được yêu cầu, không thêm thứ "phòng khi"; chỉ sửa đúng chỗ thay đổi cần.

## Vì sao SDD

Khi AI viết phần lớn code, điều gì không được viết ra thì với AI coi như không tồn tại — nó lấp chỗ trống bằng xác suất. Spec rõ giúp AI đi nhanh *đúng hướng*; AC gắn test cho phép AI viết lại code mà vẫn biết hành vi có vỡ không; lịch sử quyết định nằm trong git chứ không nằm trong trí nhớ của ai. Xem `skills/mk-specs/references/principles.md`, kể cả phần "khi nào **không** nên dùng".

## Yêu cầu

- `bash` (macOS hoặc Linux), `python3` ≥ 3.8, `git`.
- Một coding agent bất kỳ. Agent có hỗ trợ skill (Claude Code, omp, Codex…) tự kích hoạt `mk-specs`; agent khác đọc `AGENTS.md` và được trỏ tới `SKILL.md` (markdown thường).

## Cài đặt

Hướng dẫn ngắn từng bước (đưa cho agent tự cài được): [INSTALL.md](INSTALL.md).

Nhanh nhất — không cần tự clone (script clone vào `~/.mk-skills`, đổi bằng biến `MK_SKILLS_HOME`):

```bash
curl -fsSL https://raw.githubusercontent.com/mzavn/mk-skills/main/install.sh | bash -s -- --global
```

Hoặc clone tay:

```bash
git clone https://github.com/mzavn/mk-skills.git
cd mk-skills

./install.sh --global                      # ~/.claude/skills/mk-specs và ~/.agents/skills/mk-specs
./install.sh --project ~/code/my-shop      # cài vào một project
./install.sh --global --project ~/code/my-shop   # cả hai
```

Đang đứng trong project:

```bash
cd ~/code/my-shop
bash ~/.mk-skills/install.sh --project .   # hoặc đường dẫn tới nơi đã clone mk-skills
```

`--project` làm gì (chạy lại bao nhiêu lần cũng được — **thiếu thì thêm, có rồi thì giữ hoặc cập nhật**):

| File | Lần đầu | Lần sau |
|---|---|---|
| `.claude/skills/mk-specs/` | chép skill | thay bằng bản mới (từ chối và liệt kê file nếu có sửa tay, trừ `--force`) |
| `specs/mk-specs.yml` | tạo từ mẫu | giữ nguyên |
| `AGENTS.md` | tạo, kèm khối `<!-- mk-specs:start … end -->` | chỉ thay phần trong khối khi khối đổi; phần còn lại của file không bị đụng |
| `CLAUDE.md` | tạo với dòng `@AGENTS.md` (hoặc thêm dòng đó lên đầu file có sẵn) | giữ nguyên |
| `GEMINI.md` | chỉ khi file đã có: thêm một dòng "Đọc và làm theo `AGENTS.md`" | giữ nguyên |
| `.agents/skills/mk-specs/` | chỉ với `--agents-dir` (agent đọc `.agents/skills`, vd Codex) | thay bằng bản mới (tự cập nhật khi thư mục đã có, không cần nhắc lại cờ) |

Không muốn đụng file hướng dẫn agent: thêm `--no-agent-files`.

### Dùng với nhiều agent

`AGENTS.md` là [định dạng mở](https://agents.md) mà phần lớn agent đọc (Codex, Cursor, Copilot, Windsurf, Aider, omp…; Gemini CLI/Antigravity khi cấu hình hoặc qua `GEMINI.md`). Claude Code đọc `CLAUDE.md` nên cần dòng `@AGENTS.md`. Khối `mk-specs` trong `AGENTS.md` ghi các cổng cứng và trỏ tới `.claude/skills/mk-specs/SKILL.md`, nên agent không hỗ trợ skill vẫn làm đúng quy trình. Luật riêng của repo viết trong `AGENTS.md`, ngoài khối.

- Luôn **chép**, không symlink — bản trong project được commit cùng repo, nên mọi người (và CI) chạy cùng một phiên bản scripts.
- Script in phiên bản cũ → mới sau mỗi lần cài.

Khi project dùng `npm`, thêm vào `package.json`:

```json
"specs:gen": "python3 .claude/skills/mk-specs/scripts/gen.py",
"specs:check": "python3 .claude/skills/mk-specs/scripts/verify.py"
```

## Cập nhật

Một lệnh — kéo bản mới nhất (chỉ fast-forward) rồi cài lại:

```bash
bash ~/.mk-skills/install.sh --update                          # chỉ bản cài chung
bash ~/.mk-skills/install.sh --update --global --project .     # đứng trong project: cả hai
```

Clone ở chỗ khác thì thay `~/.mk-skills` bằng đường dẫn đó (đường dẫn được ghi trong `~/.claude/skills/mk-specs/.mk-specs-source`). Chạy lại bao nhiêu lần cũng được: file đã xoá ở bản mới bị bỏ, `specs/mk-specs.yml` và phần ngoài khối `mk-specs` của `AGENTS.md` giữ nguyên. Bản trong project chỉ bị từ chối khi có file khác với bản `install.sh` đã chép (sửa tay, kể cả đã commit): script liệt kê file đó; luật riêng chuyển sang `AGENTS.md` ngoài khối, rồi chạy lại với `--force`.

Rồi trong project: chạy `specs:gen` — `traceability.md`/`open-issues.md` phải không đổi nếu spec không đổi — và commit `.claude/skills/mk-specs` (`chore(specs): update mk-specs to vX.Y.Z`). Khi mở project, agent so phiên bản bản cài chung với bản trong project; lệch thì báo kèm đúng lệnh cập nhật.

## Gỡ cài đặt

```bash
./install.sh --uninstall --global
./install.sh --uninstall --project ~/code/my-shop   # bỏ khối mk-specs trong AGENTS.md; giữ specs/, specs/mk-specs.yml và dòng @AGENTS.md
```

## Cấu hình `specs/mk-specs.yml`

Ví dụ cho một cửa hàng online:

```yaml
version: 1
language: vi
specs_dir: specs
contexts:
  - id: catalog
    title: "Danh mục (catalog)"
  - id: checkout
    title: "Đặt hàng (checkout)"
ids:
  uc: 'UC-\d{3}'
  br: 'BR-\d+'
  adr: 'ADR-\d+'
decisions_file: decisions.md
tests:
  list_command: "npx vitest list --json"   # in JSON [{file, name}]
  citation_style: pointer                  # pointer | name | both
readme:
  banner:
    match: '^> (Cập nhật|Hợp nhất) '
    keep: 5
  lines:
    - match: '^(?P<uc>\d+) UC · (?P<ac>\d+) AC · (?P<tested>\d+) AC có test'
metrics:
  since: "2026-01-31"                      # ngày áp dụng, mốc đo Trace Ratio
  exempt_scopes: [specs, deps]
```

Đủ các khoá và mặc định: `skills/mk-specs/references/traceability.md` §5; mẫu có chú thích: `skills/mk-specs/assets/mk-specs.yml.template`. File dùng **YAML rút gọn** (map, list, chuỗi có/không nháy, số, true/false/null, `[a, b]`, chú thích) để scripts không cần PyYAML.

## Các mode

Gọi bằng lời thường; agent tự chọn mode.

| Mode | Làm gì | Ví dụ câu lệnh |
|---|---|---|
| `init` | Dựng `specs/` cho dự án mới (BR → UC → AC) hoặc codebase đang chạy (5 bước brownfield) | "Khởi tạo SDD cho repo này theo mk-specs, đây là codebase đang chạy." |
| `change` | Viết proposal trong `specs/changes/<yyMMdd>-<slug>/`, tự soát, review hai phía | "Đề xuất thay đổi: mã QR thanh toán hết hạn sau 15 phút thay vì 5." |
| `review` | Tự soát spec/proposal vừa viết (tự chạy sau `change`/`init`): tìm mâu thuẫn, thiếu sót, phần thừa, chỗ đoán ý; tự sửa lỗi của mình, hỏi người dùng điểm cần quyết, ghi vào `## Tự soát` | "Soát lại proposal 260131-qr-het-han trước khi gửi duyệt." |
| `apply` | Test theo AC (đỏ → xanh) rồi code theo proposal đã duyệt | "Làm proposal 260131-qr-het-han đã duyệt." |
| `merge` | Hợp nhất vào UC/ADR, History có hash, archive, sinh lại file | "Hợp nhất change 260131-qr-het-han vào specs." |
| `check` | Chạy gen + verify, giải thích lỗi và chỉ số | "Kiểm spec và test có khớp nhau không." |
| `commit` | Viết commit `<type>(UC-xxx): …` từ diff đang stage | "Viết commit message cho thay đổi đang stage." |
| `audit` | Báo cáo mục thiếu, chữ kỹ thuật trong flow/AC, commit thiếu ID | "Rà soát chất lượng specs và quy trình SDD." |

## Cấu trúc repo

```
mk-skills/
├── install.sh
├── LICENSE
├── README.md
└── skills/mk-specs/
    ├── SKILL.md                 điểm vào: chọn mode, cổng cứng, scripts
    ├── references/              principles, artifacts, workflow-change, workflow-bootstrap, review, traceability, anti-patterns
    ├── assets/                  mk-specs.yml.template, templates/ (UC, BR, ADR, proposal, entities, README)
    └── scripts/                 gen.py, verify.py, audit.py, commit-hash.py, mkspecs.py, tests/
```

## Đóng góp

- Issue/PR bằng tiếng Việt hoặc tiếng Anh đều được. Commit theo Conventional Commits.
- Sửa scripts: giữ thư viện chuẩn, đầu ra tất định; chạy `python3 -m unittest discover -s skills/mk-specs/scripts/tests` và `bash -n install.sh`.
- Sửa skill: `SKILL.md` và mỗi reference dưới 300 dòng, không lặp nội dung giữa chúng; ví dụ dùng dữ liệu giả, không đưa thông tin riêng của dự án nào vào.
- Tăng `metadata.version` trong `SKILL.md` theo semver khi phát hành.

## Ghi công

Cảm ơn anh **Huy ([huynt.dev](https://huynt.dev))** với ebook *Spec Driven Development* — phương pháp trong `mk-specs` dựa trên ebook này (skill diễn giải lại, có ghi số trang để tra).

Phần "Kỷ luật khi viết spec" rút từ [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) (MIT).

Phần `mk-specs` thêm vào (đánh dấu ✚ trong references): đánh dấu `[DIVERGENCE]`/`[OPEN]` và luật trọng tài giữa specs/docs/plans, ma trận truy vết sinh tự động và kiểm bằng máy, ADR có phương án bị loại và "Verified in code", History mang hash commit, giới hạn README — rút ra từ việc vận hành SDD trên các dự án thật.

## Giấy phép

MIT — xem [LICENSE](LICENSE).

---

## English

**mk-specs** is an agent skill for Spec-Driven Development. Humans agree on intent in `specs/` (business requirements, use cases, entities, acceptance criteria, ADRs); the AI writes tests and code from the spec; when something is wrong, fix the spec first. It ships workflows (init, change, review, apply, merge, check, commit, audit), templates, and stdlib-only Python scripts that generate a UC ↔ AC ↔ test traceability matrix and an open-issues list, verify every cited test exists and every relative link resolves, and report AC Coverage, Spec Coverage and Trace Ratio. After writing a spec or proposal the agent self-reviews it (`review`): it fixes its own mistakes, asks the user about genuine decision points, and records the result in the proposal. Spec-writing discipline (ask before assuming, nothing speculative, surgical edits) follows the Karpathy guidelines.

Install with `./install.sh --global` (copies to `~/.claude/skills` and `~/.agents/skills`) and/or `./install.sh --project <repo>` (from inside a repo: `--project .`; idempotent — copies to `<repo>/.claude/skills`, creates `specs/mk-specs.yml` if missing, maintains a marked mk-specs block in `AGENTS.md` (the cross-agent standard) and adds `@AGENTS.md` to `CLAUDE.md`, so agents without skill support still follow the workflow; `--agents-dir` also copies to `.agents/skills`). Requirements: bash, python3 ≥ 3.8, git. Skill text is Vietnamese; generated files support `language: vi | en`.

Credits: thanks to Huy (huynt.dev) for the ebook *Spec Driven Development*, which the method follows; spec-writing discipline adapted from [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) (MIT). License: MIT.
