# Cấu trúc skill, frontmatter, mô tả kích hoạt

Đọc khi tạo skill mới hoặc sửa tên, frontmatter, mô tả, bố cục file. Mọi luật đánh dấu **[máy]** do `validate.py` kiểm.

## 1. Tên

| Chỗ | Dạng | Ví dụ (giả) |
|---|---|---|
| Thư mục | `skills/mk-<tên>` — chữ thường, số, gạch nối giữa các phần **[máy]** | `skills/mk-ghi-chu` |
| Frontmatter `name` | `mk:<tên>` — đúng một dấu `:`, khớp thư mục **[máy]** | `name: mk:ghi-chu` |
| Người dùng gọi | `/mk:<tên>` (thư mục `/mk-<tên>` vẫn chạy) | `/mk:ghi-chu gom ghi chú tuần này` |
| Cài | `install.sh --skill mk-<tên>` — theo tên thư mục | `bash install.sh --global --skill mk-ghi-chu` |

Chọn tên: một hai từ nói đúng việc (`star`, `exec-review`, `specs`), không trùng skill cùng bộ, không tên chung chung (`helper`, `tool`). Tên đã phát hành thì không đổi — đổi là bản phá vỡ (`!`).

## 2. Frontmatter

```yaml
---
name: mk:ghi-chu
description: 'Turn a messy Vietnamese note into a tidy checklist file … Use mk:ghi-chu whenever … Vietnamese triggers: "gom ghi chú", "làm checklist".'
license: MIT
metadata:
  author: mzavn
  version: "0.1.0"
---
```

- Khoá gốc chỉ: `name`, `description`, `license`, `metadata`; thêm `hooks`, `allowed-tools`, `compatibility` khi thật cần **[máy]**.
- `license: MIT`, `metadata.author: mzavn` **[máy]**.
- `metadata.version: "X.Y.Z"` có nháy kép **[máy]**. Skill mới để `"0.1.0"`; về sau công cụ phát hành của repo đóng dấu số — không sửa tay khi repo có công cụ đó.
- `hooks` chỉ khi cần chặn bằng máy trong lúc agent làm việc (vd chặn sửa tay file sinh). Lệnh hook phải im lặng và thoát 0 khi không chắc, tìm script ở bản cài chung trước bản trong project, không đọc dữ liệu ngoài repo.

## 3. Mô tả kích hoạt (`description`)

Mô tả là thứ duy nhất agent đọc để quyết định có mở skill hay không. Viết "pushy": nói rõ khi nào **phải** dùng.

1. **Một dòng**, trong nháy đơn; nháy đơn bên trong viết `''` **[máy]**. Không dùng khối `>`/`|` **[máy]**.
2. **≤ 1024 ký tự** **[máy]**. Nhắm 700–1000: đủ trigger, không lan man.
3. Tiếng Anh cho phần chính (agent đọc ổn định ở mọi model), rồi `Vietnamese triggers:` với các câu người dùng hay gõ.
4. Thứ tự: làm gì (đầu vào → đầu ra) · điểm khác biệt (cổng, script, agent riêng) · không làm gì · `Use mk:<tên> whenever …` **[máy: có chữ `mk:<tên>`]** · trigger tiếng Việt.
5. Trigger lấy từ lời thật người dùng hay nói, kể cả khi họ không nhắc tên skill ("even if they don't say …").
6. Không hứa điều skill không làm; không nhắc tên skill hay công cụ của bộ khác.

Ví dụ (giả) — yếu → mạnh:

| Yếu | Mạnh |
|---|---|
| `'Helps with notes.'` | `'Turn a messy Vietnamese shopping or work note into a checklist file next to it, grouped by day, never editing the original. Use mk:ghi-chu whenever the user pastes or points to a note and wants it cleaned, grouped or turned into to-dos, even if they don''t say checklist. Vietnamese triggers: "gom ghi chú", "làm checklist", "dọn sổ đi chợ".'` |

Kiểm kích hoạt bằng dry-run (`references/quy-trinh.md` §4): 3 câu nên kích hoạt, 2 câu gần giống mà không nên.

## 4. Thư mục

```
skills/mk-<tên>/
├── SKILL.md              # luồng điều phối
├── references/           # chi tiết, đọc khi bước cần
├── assets/               # khuôn, mẫu, gói giao việc — chép rồi điền
└── scripts/              # Python thư viện chuẩn
    └── tests/            # unittest cho từng script
```

- Gốc skill chỉ 4 mục trên **[máy]**. Không `README.md`, `docs/`, `LICENSE` riêng trong skill. Ngoại lệ duy nhất: `THIRD_PARTY_NOTICES.md` khi skill có đoạn phỏng theo văn bản mà giấy phép gốc đòi giữ thông báo trong mọi bản sao (bản cài chỉ chép thư mục skill); `SKILL.md` không cần nhắc file này.
- Không file rác `__pycache__/`, `.DS_Store`, `*.pyc` trong file sẽ commit **[máy]** — repo nên có `.gitignore` loại chúng.
- Không đường dẫn máy cá nhân kiểu `/Users/<tên>` hay `~/<dự án riêng>` trong bất kỳ file nào **[máy với /Users]**; dùng `<skill>`, `<repo>`, `<thư mục nhật ký>`.
- Không symlink **[máy]** — bản cài chép symlink nguyên dạng, có thể trỏ ra ngoài.

## 5. Chia `SKILL.md` và references

- `SKILL.md` và mỗi file trong `references/` **dưới 300 dòng** **[máy]**. Dài quá → tách thêm reference theo chủ đề, `SKILL.md` trỏ sang; không cắt ý cho vừa.
- `SKILL.md` = luồng: bước đánh số, chọn mode, ai làm gì, lệnh nào, cổng nào. Bảng câu hỏi, khuôn báo cáo, danh mục dấu hiệu, luật định dạng → references hoặc assets.
- **Không lặp** một nội dung ở hai file. `SKILL.md` nhắc file kèm đường dẫn; reference không chép lại bước của `SKILL.md`.
- Mỗi mode/bước nêu đúng file phải đọc (bảng "Đọc"), để model nhỏ không đọc thừa, model lớn không đoán.
- Đường dẫn `references/…`, `assets/…`, `scripts/…` nhắc trong `SKILL.md` và references phải có thật **[máy]**. Đường dẫn mẫu có `<…>`, `*`, `{…}` được bỏ qua.
- `<skill>` = thư mục chứa `SKILL.md`; lệnh viết `python3 <skill>/scripts/<script>.py`, không viết đường dẫn cài cố định.

## 6. Nội dung bắt buộc của `SKILL.md`

1. Tiêu đề `# mk:<tên> — <một cụm nói việc>`.
2. Một dòng mô tả luồng: vào → các bước → ra.
3. Đoạn `**Phạm vi.** Skill xử lý: … **Không** xử lý: …` **[máy]**. Phần "Không" liệt kê việc gần giống người dùng dễ nhờ nhầm (đăng bài, commit, viết hộ, bịa số).
4. Bước đánh số (Bước 0 — mỗi lần kích hoạt; Bước 1…; hoặc bảng mode).
5. `## Trả lời người dùng` **[máy]** — mẫu ở `references/tuong-tac.md` §5.
6. `## Chính sách an toàn` **[máy]** — mẫu ở `references/tuong-tac.md` §6.
7. `## Tài liệu` ở cuối: bảng `| File | Ai đọc | Nội dung |`, mỗi file của skill một dòng ("Ai đọc": agent chính, subagent, script).

Ví dụ khung đầy đủ: `assets/SKILL.md.template` (điền mọi chỗ `{{…}}`).
