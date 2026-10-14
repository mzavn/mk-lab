# Cài mk-specs

Hướng dẫn ngắn cho cả người và agent. Nhờ agent cài, dán câu này:

> Đọc https://raw.githubusercontent.com/mzavn/mk-skills/main/INSTALL.md và cài mk-specs theo đó.

## Agent: làm theo thứ tự

1. **Kiểm điều kiện** — cần `bash`, `python3` ≥ 3.8, `git`:
   ```bash
   bash --version | head -1; python3 --version; git --version
   ```
   Thiếu cái nào → báo người dùng, dừng.

2. **Đã cài chưa?**
   ```bash
   grep -m1 -H 'version:' ~/.claude/skills/mk-specs/SKILL.md ~/.agents/skills/mk-specs/SKILL.md .claude/skills/mk-specs/SKILL.md 2>/dev/null
   cat ~/.claude/skills/mk-specs/.mk-specs-source 2>/dev/null
   ```
   Có `.mk-specs-source` → bước 3 dùng `bash <đường dẫn đó>/install.sh --update` thay cho `curl`.

3. **Cài chung cho máy** (`~/.claude/skills` và `~/.agents/skills`):
   ```bash
   curl -fsSL https://raw.githubusercontent.com/mzavn/mk-skills/main/install.sh | bash -s -- --global
   ```
   Lệnh clone vào `~/.mk-skills` rồi cài từ đó. Chạy lại không sao.

4. **Cài vào repo hiện tại** — chỉ khi người dùng muốn SDD đầy đủ (mức 4) cho repo này; chưa rõ thì hỏi. Dự án nhỏ làm PRD (mức 1–3) không cần bước này:
   ```bash
   bash ~/.mk-skills/install.sh --project .
   ```
   Chép skill vào `.claude/skills/mk-specs`, tạo `specs/mk-specs.yml` nếu chưa có, thêm khối mk-specs vào `AGENTS.md` và `@AGENTS.md` vào `CLAUDE.md`. Agent đọc `.agents/skills` (vd Codex) → thêm `--agents-dir`. Không muốn đụng `AGENTS.md`/`CLAUDE.md` → thêm `--no-agent-files`.

5. **Kiểm kết quả** — chạy lại lệnh ở bước 2: các bản phải cùng phiên bản; với bước 4, `AGENTS.md` có dòng `<!-- mk-specs:start`.

6. **Báo người dùng**: phiên bản đã cài, file đã tạo/sửa. Bước kế, tuỳ dự án: nhỏ/MVP → "Viết PRD cho app này theo mk-specs" (agent hỏi chọn mức 1–3, phỏng vấn, dừng trước khi code); lớn → "Khởi tạo SDD cho repo này theo mk-specs" (mode `init`). Không tự commit; người dùng muốn thì commit `chore(specs): adopt mk-specs`.

## Cập nhật

```bash
bash ~/.mk-skills/install.sh --check                         # có bản mới không (chỉ đọc, không sửa gì)
bash ~/.mk-skills/install.sh --update                        # bản cài chung
bash ~/.mk-skills/install.sh --update --global --project .   # đứng trong repo: cả hai
```

`--update` chỉ nhận bản đã phát hành ([CHANGELOG.md](CHANGELOG.md)). Bản tăng số đầu (X) cần làm thêm bước — CHANGELOG ghi rõ, đọc trước khi cập nhật. Sau khi cập nhật bản trong repo: commit `.claude/skills/mk-specs` (`chore(specs): update mk-specs to vX.Y.Z`). Agent tự nhắc khi có bản mới (một lần mỗi phiên); tắt bằng `MK_SKILLS_NO_UPDATE_CHECK=1`.

## Gặp lỗi

| Thông báo | Làm gì |
|---|---|
| `has edits not made by install.sh` | Có người sửa tay file trong skill (đã liệt kê). Luật riêng chuyển vào `AGENTS.md` ngoài khối mk-specs, rồi chạy lại với `--force` |
| `cannot fast-forward ~/.mk-skills` | Thư mục clone có sửa đổi riêng. Không cần giữ → `rm -rf ~/.mk-skills` rồi chạy lại lệnh `curl` |
| `--update needs a git checkout` | Bản tải về không phải clone git → dùng lệnh `curl` ở bước 3 |
| `git is required` / `cannot clone` | Cài git, kiểm mạng tới github.com |

## Gỡ

```bash
bash ~/.mk-skills/install.sh --uninstall --global
bash ~/.mk-skills/install.sh --uninstall --project .   # giữ specs/ và specs/mk-specs.yml
```
