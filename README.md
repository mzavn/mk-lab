# mk-lab

Bộ skill **kỹ thuật & lập trình** cho AI coding agent (Claude Code, omp, Codex và các agent hỗ trợ chuẩn Agent Skills). 

Trọng tâm hiện tại là **`mk-specs`** — phương pháp luận và bộ công cụ **Spec-Driven Development (SDD)** được thiết kế chuyên biệt cho kỷ nguyên **Agentic Software Engineering (SE 3.0)**.

> **Cài đặt trước v2.0.0?** (máy có thư mục `~/.mk-skills` — tên cũ của repo): Xem các bước *"Cần làm khi cập nhật"* của bản v2.0.0 trong [CHANGELOG.md](CHANGELOG.md).

Bộ skill content & review đi kèm là **[mk-studio](https://github.com/mzavn/mk-studio)** (`/mk:star`, `/mk:exec-review`).

*English summary at the end.*

---

## mk-specs là gì?

`mk-specs` chuyển đổi cách làm việc với AI coding agent: **con người chốt ý định bằng đặc tả (spec) trong thư mục `specs/`, AI viết test và code theo spec; khi có sai lệch, sửa spec trước rồi mới sửa code.**

```
          [ Ý định con người ]
                   │
                   ▼
       [ specs/ (Hợp đồng gốc) ] ── (Nguồn sự thật tối cao)
         │                   │
         ▼                   ▼
[ Automated Tests ] ◄───► [ Source Code ]
  (Given-When-Then)       (AI sinh & refactor)
```

### Cách gọi lệnh
- **Claude Code:** Gõ `/mk:specs` rồi nêu yêu cầu (vd: `/mk:specs viết PRD cho tính năng thanh toán`). Thư mục cài đặt vẫn là `mk-specs`, gõ `/mk-specs` vẫn chạy bình thường.
- **Agent khác (omp, Codex…):** Nói bằng lời tự nhiên (vd: *"Khởi tạo SDD cho repo này"*, *"Đề xuất thay đổi: thêm cổng thanh toán QR"*). Agent tự nhận diện quy trình qua `AGENTS.md`.
- **Lưu ý quyền:** Tiền tố `mk:` là quy ước định danh riêng của bộ skill này, **không** phải plugin Claude Code tên `mk`. Nếu bạn cấu hình `permissions.allow` hoặc `permissions.deny` trong `settings.json`, hãy khai báo cả hai: `Skill(mk:specs)` và `Skill(mk-specs)`.

---

## Nền tảng phương pháp luận: Vì sao cần SDD?

Trong kỷ nguyên Agentic SE, khi AI có thể sinh hàng nghìn dòng code trong vài phút, **vấn đề của kỹ thuật phần mềm không còn là tốc độ viết code, mà là khả năng thẩm định, duy trì tính nhất quán và kiểm soát trôi dạt kiến trúc.** 

Theo nghiên cứu học thuật của **Díaz et al. (arXiv:2609.00252, 2026)**, "vibe coding" (lập trình hoàn toàn qua chat tự do) tạo ra nghịch lý năng suất: tăng tốc cá nhân nhưng làm nghẽn năng lực review của nhóm, mất khả năng truy vết và tích tụ nợ kỹ thuật.

`mk-specs` giải quyết bài toán này qua 4 cam kết cốt lõi:
1. **Mọi thay đổi có chủ đích bắt đầu từ spec:** Spec là bản hợp đồng nghiệm thu duy nhất trước khi viết code.
2. **Spec được quản lý phiên bản cùng với code:** Cùng nằm trong Git, tuân thủ cùng kỷ luật review, audit và rollback.
3. **Mọi artifact đều có nguồn gốc và truy vết (Traceability):** Code, test, tài liệu đều liên kết chặt chẽ về Use Case và Acceptance Criteria tương ứng.
4. **Spec là nguồn sự thật tối cao:** Khi code và spec mâu thuẫn, sửa spec trước hoặc sinh lại code, tuyệt đối không sửa ngầm vào code.

---

## 3 lớp tài liệu phân định rõ

Để tránh làm phình cửa sổ ngữ cảnh (context window) của AI và chống trôi dạt kiến trúc, `mk-specs` phân định ranh giới rõ ràng giữa 3 tầng tài liệu:

| Tầng tài liệu | Vị trí lưu trữ | Vòng đời & Bản chất | Trách nhiệm |
|---|---|---|---|
| **System Spec** | `AGENTS.md`, `CLAUDE.md` | **Luật chuẩn mực bền vững, nạp thường trực.** Định nghĩa kiến trúc, quy ước coding, cổng bảo mật và ranh giới bất biến của toàn dự án. | Tech Lead, Architect |
| **Feature Spec** | `specs/changes/`, `specs/<context>/` | **Đặc tả theo task, có vòng đời.** Mô tả thay đổi cụ thể, acceptance criteria và được lưu trữ (`archive/`) khi hoàn tất. | Developer, PM, Agent |
| **Procedural Skill** | `.claude/skills/mk-specs/` | **Thủ tục thực hiện, nạp theo nhu cầu (`on-demand`).** Hướng dẫn agent cách làm từng mode mà không làm bẩn context khi không cần tới. | Bộ công cụ `mk-specs` |

---

## 4 mức độ đặc tả linh hoạt trên cùng 1 khung

Không phải dự án nào cũng cần bộ spec đồ sộ. `mk-specs` cung cấp 4 mức độ kỹ lưỡng tăng dần trên cùng một khung cấu trúc. Mức sau kế thừa nguyên vẹn mức trước:

```
[Mức 1: PRD] ──► [+ Wireframe] ──► [+ TDD] ──► [Mức 4: SDD Đầy đủ]
 (Story ID)      (HTML độc lập)   (Tech spec)  (BR/UC/AC/ADR + Traceability)
```

| Mức | Đầu ra chính | Đặc điểm & Thời điểm áp dụng |
|---|---|---|
| **1 · PRD** | `specs/PRD.md` | Story có mã vĩnh viễn (`BOOK-01`), tiêu chí "Done khi", thứ tự thực hiện. Phù hợp làm MVP, thử nghiệm ý tưởng trong vài ngày. |
| **2 · + Wireframe** | + `specs/wireframe.html` | Thêm giao diện HTML tĩnh màn hình chính, tự đứng được, mở trực tiếp trên trình duyệt để chốt luồng trải nghiệm người dùng trước khi code. |
| **3 · + TDD** | + `specs/TDD.md` | Thêm thiết kế kỹ thuật: kiến trúc cơ sở dữ liệu, sơ đồ bảng, API contract, các quyết định công nghệ quan trọng. |
| **4 · SDD đầy đủ** | `specs/` (BR, UC, AC, ADR, Traceability) | Đầy đủ Use Case, Acceptance Criteria kiểm thử được, Architectural Decision Records (ADR), thư mục đề xuất thay đổi (`changes/`), sinh ma trận truy vết tự động. Dành cho dự án dài hạn (> 6 tháng), nhóm > 2 người, hoặc có ràng buộc pháp lý/dòng tiền. |

*Nâng cấp mượt mà:* Dự án bắt đầu ở mức 1–3 có thể dùng lệnh `promote` để tự động nâng cấp lên mức 4 khi quy mô mở rộng mà không làm gãy mã story hay cấu trúc đã có.

---

## 8 cơ chế Methodological Harness

Hệ thống cung cấp khung kỷ luật phương pháp luận (Methodological Harness) để quản trị hành vi của agent ở quy mô nhóm:

1. **Context Engineering:** Xây dựng môi trường thông tin chuẩn hóa qua `specs/` và `AGENTS.md`, biến tri thức dự án thành tài sản có phiên bản thay vì cấu hình cá nhân tản mát.
2. **Persistent Shared Knowledge:** Lưu trữ quyết định và căn nguyên (ADR), lịch sử thay đổi (`## History`), truy xuất lười (lazy retrieval) để các phiên làm việc sau kế thừa trọn vẹn quyết định của phiên trước.
3. **Executable Specifications:** Mọi Acceptance Criteria viết theo cấu trúc Given–When–Then kiểm thử được. Châm ngôn: *"Ràng buộc mà không công cụ nào kiểm được là mong muốn chứ không phải ràng buộc"*. Script `audit.py` tự động cảnh báo AC thiếu mệnh đề `Then`.
4. **Norm Encoding (Quy tắc lặp 3 lần):** Khi một lỗi hoặc quy ước phải sửa thủ công tới lần thứ 3 trong quá trình review, nó phải được chuẩn hóa thành điều khoản trong `AGENTS.md` (ngoài khối mk-specs) qua pull request, kèm bộ kiểm tra tự động (linter/test).
5. **Structured Consultation (Tham vấn có cấu trúc):** Khi agent gặp điểm mơ hồ trong lúc thực hiện (`apply`), agent **không tự suy đoán**. Agent phát hành *Consultation Request Pack* gồm 4 phần: (1) Câu hỏi · (2) Các phương án · (3) Điều khoản spec liên quan · (4) Hệ quả. Phán quyết của con người được ghi nhận vào spec hoặc ADR.
6. **Evidence-backed Acceptance (Nghiệm thu dựa trên bằng chứng):** Đơn vị hoàn thành không chỉ là "code chạy được", mà là **Gói bằng chứng** trong proposal: đối chiếu từng AC ↔ test đã chạy, kết quả DoD, lý do lựa chọn giải pháp và link quy ước đang hiệu lực.
7. **Graduated Autonomy (Thang tự chủ phân tầng):** Phân chia rõ mức độ tự chủ theo loại công việc: sửa lỗi nhỏ/cập nhật phụ thuộc chạy tự động; tính năng mới chạy tự động kèm tham vấn khi mơ hồ; logic dòng tiền/bảo mật/quyền hạn bắt buộc phải có plan được duyệt và kiểm tra từng bước.
8. **Drift Prevention (Phòng chống trôi dạt):** Giám sát liên tục sự sai lệch giữa tài liệu và mã nguồn qua các công cụ kiểm toán tự động (`audit.py`, `verify.py`, `open-issues.md`).

---

## 10 Modes làm việc linh hoạt

Agent tự động chọn mode xử lý dựa trên câu lệnh tự nhiên của bạn:

| Mode | Mục đích | Lệnh mẫu bằng lời tự nhiên |
|---|---|---|
| `prd` | Phỏng vấn & lập PRD (mức 1–3), wireframe, TDD cho dự án nhỏ | *"Viết PRD cho ứng dụng đặt lịch khám bệnh, mức 2."* |
| `promote` | Nâng cấp PRD lên cấu trúc SDD đầy đủ (mức 4) | *"Dự án đã mở rộng, nâng PRD này lên specs đầy đủ."* |
| `init` | Khởi tạo cấu trúc `specs/` cho dự án mới hoặc codebase đang chạy | *"Khởi tạo SDD cho repo này theo mk-specs (dự án brownfield)."* |
| `change` | Soạn đề xuất thay đổi trong `specs/changes/` kèm tự soát | *"Đề xuất thay đổi: thêm cơ chế xác thực 2 lớp qua email."* |
| `review` | Rà soát chéo độc lập spec/proposal, tìm mâu thuẫn và lỗ hổng | *"Soát lại proposal 261020-auth-2fa trước khi gửi duyệt."* |
| `apply` | Lập trình theo spec đã duyệt: viết test theo AC (đỏ -> xanh) rồi viết code | *"Thực hiện proposal 261020-auth-2fa đã được duyệt."* |
| `merge` | Hợp nhất thay đổi vào UC/ADR chính thức, lưu trữ proposal | *"Hợp nhất change 261020-auth-2fa vào hệ thống specs."* |
| `check` | Kiểm tra tính nhất quán giữa spec và test suite (`gen` + `verify`) | *"Kiểm tra xem toàn bộ spec và test có khớp nhau không."* |
| `commit` | Soạn commit message chuẩn Conventional Commits gắn mã UC/story | *"Viết commit message cho các thay đổi đang stage."* |
| `audit` | Quét vệ sinh toàn diện spec: mục thiếu, AC thiếu Then, commit thiếu ID | *"Rà soát chất lượng specs và mức độ tuân thủ quy trình SDD."* |

---

## Cài đặt nhanh

Xem hướng dẫn chi tiết tại [INSTALL.md](INSTALL.md).

### 1. Cài đặt toàn hệ thống (Global)
Cách nhanh nhất — tự động tải và cài đặt vào `~/.claude/skills` và `~/.agents/skills`:

```bash
curl -fsSL https://raw.githubusercontent.com/mzavn/mk-lab/main/install.sh | bash -s -- --global
```

Hoặc qua Git:
```bash
git clone https://github.com/mzavn/mk-lab.git ~/.mk-lab
bash ~/.mk-lab/install.sh --global
```

### 2. Cài đặt vào một dự án (Project-level)
Khuyên dùng cho các dự án áp dụng SDD mức 4:

```bash
cd ~/code/my-project
bash ~/.mk-lab/install.sh --project .
```

*Lệnh trên sẽ:*
- Sao chép bộ công cụ vào `.claude/skills/mk-specs` (và `.agents/skills` nếu có `--agents-dir`).
- Tạo file cấu hình `specs/mk-specs.yml` từ mẫu chuẩn nếu chưa có.
- Thêm khối định hướng `<!-- mk-specs:start ... end -->` vào `AGENTS.md` và gắn `@AGENTS.md` vào `CLAUDE.md`.

---

## Bảo mật & Ranh giới tin cậy (v2.0.0)

`mk-specs` được gia cố toàn diện chống các kỹ thuật tấn công qua Agentic workflows:

- **Kiểm soát lệnh test (`--trust-list-command`):** `tests.list_command` trong `specs/mk-specs.yml` là lệnh shell thực thi trên máy bạn. Script `verify.py`/`gen.py` **tuyệt đối không tự động chạy lệnh này trên repo lạ**. Lần đầu tiên gặp repo (hoặc khi lệnh bị sửa qua PR), script thoát mã 3 và yêu cầu bạn xác nhận bằng cờ `--trust-list-command`. Danh sách tin cậy được lưu trữ ngoài repo tại `~/.config/mk-specs/trusted-commands`.
- **Ranh giới an toàn cho Repo chưa tin:** Khi mở PR lạ hoặc repo chưa rõ nguồn gốc, **không bao giờ chạy scripts do chính repo đó cung cấp**. Hãy dùng bản cài chung toàn hệ thống để thẩm định:
  ```bash
  python3 ~/.claude/skills/mk-specs/scripts/verify.py --root .
  ```
- **Toàn vẹn phát hành:** Lệnh `--update` và đường dẫn cài đặt `curl` chỉ đưa checkout về **tag phát hành chính thức (`vX.Y.Z`)**, ngăn chặn việc thực thi các commit chưa gắn tag trên nhánh `main`.
- **Chống Path Traversal & Symlink:** Mọi đường dẫn cấu hình bắt buộc nằm trong repo; scripts từ chối đọc hoặc ghi đè xuyên qua symlink.
- **Phòng vệ ReDoS:** Bộ phân tích YAML rút gọn tích hợp cơ chế phát hiện các biểu thức chính quy nguy hiểm có nguy cơ gây treo CPU.
- **Claude Code Hook (`hook.py`):** Tự động bảo vệ các file ma trận sinh ra (`traceability.md`, `open-issues.md`) không bị sửa tay và chặn các commit thiếu mã định danh Use Case / Story.

---

## Cấu hình `specs/mk-specs.yml`

File cấu hình đặt tại `specs/mk-specs.yml`, sử dụng định dạng **YAML rút gọn** (không cần cài thêm PyYAML):

```yaml
version: 1
language: vi                 # vi | en — ngôn ngữ chữ sinh ra trong bảng
specs_dir: specs            # thư mục chứa toàn bộ đặc tả
contexts:
  - id: catalog
    title: "Danh mục sản phẩm (catalog)"
  - id: checkout
    title: "Đặt hàng & Thanh toán (checkout)"
ids:
  uc: 'UC-\d{3}'             # mẫu mã Use Case
  br: 'BR-\d+'              # mẫu mã Business Requirement
  adr: 'ADR-\d+'            # mẫu mã Quyết định Kiến trúc
decisions_file: decisions.md # file ghi nhận ADR
tests:
  list_command: "npx vitest list --json"   # lệnh liệt kê test (chỉ chạy khi đã tin)
  citation_style: pointer                  # pointer | name | both
metrics:
  since: "2026-01-31"                      # ngày bắt đầu tính Trace Ratio
  exempt_scopes: [specs, deps, release]    # các scope commit không bắt buộc mã UC
```

Thêm vào `package.json` để chạy thuận tiện:
```json
"scripts": {
  "specs:gen": "python3 .claude/skills/mk-specs/scripts/gen.py",
  "specs:check": "python3 .claude/skills/mk-specs/scripts/verify.py"
}
```

---

## Hỗ trợ đa Agent qua AGENTS.md

`AGENTS.md` là [chuẩn mở](https://agents.md) được hỗ trợ bởi hầu hết các AI coding agent hiện nay (Codex, Cursor, Copilot, Windsurf, Aider, omp…).

Khối `mk-specs` trong `AGENTS.md` chứa đầy đủ các cổng cứng và nguyên tắc tối thượng. Nhờ đó, **ngay cả những agent không có tính năng skill riêng vẫn tự động tuân thủ nghiêm ngặt quy trình SDD** khi đọc file này. Quy ước riêng của dự án được viết ở phần ngoài khối và có hiệu lực bổ sung hoặc thu hẹp quyền.

---

## Cập nhật & Gỡ cài đặt

### Cập nhật
```bash
bash ~/.mk-lab/install.sh --update                        # cập nhật bản cài chung toàn máy
bash ~/.mk-lab/install.sh --update --global --project .   # cập nhật cả bản máy và bản dự án
bash ~/.mk-lab/install.sh --check                         # kiểm tra xem có bản mới hay không
```

### Gỡ cài đặt
```bash
./install.sh --uninstall --global                         # gỡ bản toàn máy
./install.sh --uninstall --project ~/code/my-project      # gỡ khỏi dự án (giữ lại specs/ và AGENTS.md)
```

---

## Cấu trúc repository

```
mk-lab/
├── install.sh                       # Bộ cài đặt chuẩn POSIX (bash 3.2+)
├── INSTALL.md                       # Sổ tay hướng dẫn cài đặt chi tiết
├── CHANGELOG.md                     # Lịch sử phiên bản SemVer
├── LICENSE                          # Giấy phép nguồn mở MIT
├── README.md
├── tests/                           # Bộ kiểm thử cho installer
└── skills/mk-specs/
    ├── SKILL.md                     # Điểm điều phối chính: chọn mode, cổng cứng, scripts
    ├── references/                  # Phương pháp luận: principles, workflow, review, glossary...
    ├── assets/                      # Mẫu template: PRD, TDD, UC, BR, ADR, proposal, entities...
    └── scripts/                     # gen.py, verify.py, audit.py, hook.py, mkspecs.py...
```

---

## Ghi công

- Phương pháp luận SDD kế thừa và mở rộng từ tác phẩm *Spec Driven Development* của anh **Huy ([huynt.dev](https://huynt.dev))**.
- Nền tảng lý thuyết học thuật về SDD cho Agentic SE dựa trên công trình nghiên cứu của **Jessica Díaz, Joaquín Gayoso, Andrea Cimminio, Jorge Pérez (Universidad Politécnica de Madrid)** — *"Spec-Driven Development for Agentic Software Engineering: Harnessing Human–Agent Teamwork"* ([arXiv:2609.00252](https://arxiv.org/html/2609.00252v1), 2026).
- Kỷ luật tinh gọn đặc tả và phòng chống suy diễn lấy cảm hứng từ nguyên tắc kỹ thuật của **Andrej Karpathy** (MIT).
- Các đóng góp thực chiến độc quyền của `mk-specs` (đánh dấu ✚ trong references): Phân định 3 tầng tài liệu, ma trận truy vết tự động hóa, quy tắc DIVERGENCE, quy trình Consultation Request Pack và Command Security Allowlist.

---

## Giấy phép

Phát hành theo giấy phép nguồn mở [MIT License](LICENSE).

---

## English Summary

**mk-lab** is an engineering skill suite for AI coding agents. Its flagship skill, **`mk-specs`**, provides an industrial-grade **Spec-Driven Development (SDD)** discipline engineered for **Agentic Software Engineering (SE 3.0)**.

- **Grounding & Lineage:** Synthesizes academic foundations from Díaz et al. (*Spec-Driven Development for Agentic Software Engineering: Harnessing Human–Agent Teamwork*, arXiv:2609.00252, 2026), practitioner methodology from Huy (huynt.dev), and prompt discipline from Andrej Karpathy.
- **Three-Tier Architecture:** Separates durable, always-active project norms (*System Specs* in `AGENTS.md`) from scoped, ephemeral changes (*Feature Specs* in `specs/changes/`) and on-demand capabilities (*Procedural Skills* in `.claude/skills/`).
- **Four Scalable Tiers:** (1) PRD with durable story IDs and testable criteria; (2) + standalone HTML wireframes; (3) + Technical Design Documents (TDD); (4) Full enterprise SDD (BR, UC, AC, ADR, and automated traceability).
- **Eight Methodological Harness Mechanisms:** Context engineering, persistent transactive memory (ADRs & History), executable specifications (Given-When-Then), 3-strike norm encoding, structured 4-part consultation requests, evidence-backed acceptance packs, graduated autonomy levels, and automated drift auditing (`audit.py`).
- **Enterprise Security (v2.0.0):** Untrusted command gating via `--trust-list-command` (persisted in `~/.config/mk-specs/trusted-commands`), release tag verification for updates, path traversal guards, ReDoS mitigation, and Claude Code automated enforcement hooks (`hook.py`).

Invoke via `/mk:specs` or natural language. Install globally with `curl -fsSL https://raw.githubusercontent.com/mzavn/mk-lab/main/install.sh | bash -s -- --global`. Licensed under MIT.
