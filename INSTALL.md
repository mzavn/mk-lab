# Cài mk-specs (bộ mk-lab)

Hướng dẫn ngắn cho cả người và agent. Nhờ agent cài, dán câu này:

> Đọc https://raw.githubusercontent.com/mzavn/mk-lab/main/INSTALL.md và cài mk-specs theo đó.

Máy đã cài trước v2.0.0 (có thư mục `~/.mk-skills` — tên cũ của repo): làm các bước "Cần làm khi cập nhật" của bản v2.0.0 trong [CHANGELOG.md](CHANGELOG.md).

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
   curl -fsSL https://raw.githubusercontent.com/mzavn/mk-lab/main/install.sh | bash -s -- --global
   ```
   Lệnh clone vào `~/.mk-lab` rồi cài từ đó. Chạy lại không sao.

4. **Cài vào repo hiện tại** — chỉ khi người dùng muốn SDD đầy đủ (mức 4) cho repo này; chưa rõ thì hỏi. Dự án nhỏ làm PRD (mức 1–3) không cần bước này:
   ```bash
   bash ~/.mk-lab/install.sh --project .
   ```
   Chép skill vào `.claude/skills/mk-specs`, tạo `specs/mk-specs.yml` nếu chưa có, thêm khối mk-specs vào `AGENTS.md` và `@AGENTS.md` vào `CLAUDE.md`. Agent đọc `.agents/skills` (vd Codex) → thêm `--agents-dir`. Không muốn đụng `AGENTS.md`/`CLAUDE.md` → thêm `--no-agent-files`.

5. **Kiểm kết quả** — chạy lại lệnh ở bước 2: các bản phải cùng phiên bản; với bước 4, `AGENTS.md` có dòng `<!-- mk-specs:start`.

6. **Báo người dùng**: phiên bản đã cài, file đã tạo/sửa, cách gọi (Claude Code: gõ `/mk:specs` rồi nói yêu cầu; agent khác: nói thẳng). Bước kế, tuỳ dự án: nhỏ/MVP → "Viết PRD cho app này theo mk-specs" (agent hỏi chọn mức 1–3, phỏng vấn, dừng trước khi code); lớn → "Khởi tạo SDD cho repo này theo mk-specs" (mode `init`). Không tự commit; người dùng muốn thì commit `chore(specs): adopt mk-specs`.

## Skill khác trong repo: mk-cook, mk-fix, mk-secu, mk-ship

Ngoài `mk-specs`, repo có bốn skill lập trình bám spec (cài khi người dùng muốn; `mk-cook`, `mk-fix` cần repo đã dùng mk-specs mức 4; `mk-secu`, `mk-ship` dùng được ở repo bất kỳ):

| Skill | Gọi | Dùng khi |
|---|---|---|
| `mk-cook` | `/mk:cook` | làm proposal đã duyệt thành code có test theo AC, giao diện theo `DESIGN.md` |
| `mk-fix` | `/mk:fix` | sửa lỗi: tái hiện, tra AC, xếp loại rồi mới sửa |
| `mk-secu` | `/mk:secu` | soát bảo mật chỉ đọc, báo cáo trong `specs/security/` |
| `mk-ship` | `/mk:ship` | triển khai theo `DEPLOY.md`, Cloudflare Workers trước |

```bash
bash ~/.mk-lab/install.sh --global --skill mk-cook     # chung cho máy (tương tự mk-fix, mk-secu, mk-ship)
bash ~/.mk-lab/install.sh --project . --skill mk-cook  # vào repo hiện tại (commit .claude/skills/mk-cook)
```

Chọn skill bằng `--skill <tên>` (mặc định `mk-specs`). Skill khác `mk-specs` chỉ được chép thư mục skill — không tạo cấu hình, không đụng `AGENTS.md`/`CLAUDE.md`. `--update` không kèm `--skill` cập nhật mọi skill đã cài bằng `install.sh`. Checkout cũ (≤ v1.5.1) chưa biết `--skill`: chạy `install.sh --update` trước rồi mới chạy lệnh có `--skill`.

## Cập nhật

```bash
bash ~/.mk-lab/install.sh --check                         # có bản mới không (chỉ đọc, không sửa gì)
bash ~/.mk-lab/install.sh --update                        # bản cài chung: mọi skill đã cài bằng install.sh
bash ~/.mk-lab/install.sh --update --global --project .   # đứng trong repo: cả hai
```

`--update` chỉ đưa checkout tới tag phát hành mới nhất `vX.Y.Z` ([CHANGELOG.md](CHANGELOG.md)), không bao giờ chạy commit chưa gắn tag. Bản tăng số đầu (X) cần làm thêm bước — CHANGELOG ghi rõ, đọc trước khi cập nhật. Sau khi cập nhật bản trong repo: commit `.claude/skills/mk-specs` (`chore(specs): update mk-specs to vX.Y.Z`). Agent tự nhắc khi có bản mới (một lần mỗi phiên); tắt bằng `MK_LAB_NO_UPDATE_CHECK=1`.

## Gặp lỗi

| Thông báo | Làm gì |
|---|---|
| `has edits not made by install.sh` | Có người sửa tay file trong skill (đã liệt kê). Luật riêng chuyển vào `AGENTS.md` ngoài khối mk-specs, rồi chạy lại với `--force` |
| `cannot fast-forward ~/.mk-lab` | Thư mục clone do installer quản có sửa đổi riêng. Không cần giữ → `rm -rf ~/.mk-lab` rồi chạy lại lệnh `curl` |
| `cannot fast-forward <clone tay>` / `is past the newest release` | Checkout tự clone có commit riêng hoặc đang ở bản chưa phát hành (vd nhánh `dev` của người đóng góp). **Đừng xoá** — `--update` chỉ nhận bản phát hành: cài thẳng bản đang có, bỏ `--update` (vd `install.sh --global --project .`), hoặc tự đưa checkout về `main` rồi chạy lại. Thư mục `~/.mk-lab` (do installer quản) → `rm -rf ~/.mk-lab` rồi chạy lại lệnh `curl` |
| `no release tag` | Repo nguồn (vd bản fork qua `MK_LAB_REPO`) chưa có tag `vX.Y.Z` nào |
| `was not installed by install.sh` | Đã có thư mục skill cùng tên (vd `~/.claude/skills/<tên>`, kể cả `mk-specs`) không do installer tạo — có thể là skill khác. Hỏi người dùng; giữ thì đổi tên thư mục đó, bỏ thì chạy lại với `--force` (với `mk-specs`: xem CHANGELOG v2.0.0 "Cần làm" bước 3) |
| `tests.list_command … is not trusted` (verify.py/gen.py thoát mã 3) | Lệnh test của repo chưa được người dùng tin. Cho người dùng xem nguyên lệnh và hỏi; đồng ý thì chạy lại với `--trust-list-command`, không thì `--tests <list.json>`. Không tự thêm cờ |
| `unknown option: --skill` | Installer cũ (≤ v1.5.1) → chạy `install.sh --update` trước |
| `no skill named '…'` | Tên sau `--skill` không có trong `skills/` của checkout (thông báo kèm danh sách skill có) |
| `--update needs a git checkout` | Bản tải về không phải clone git → dùng lệnh `curl` ở bước 3 |
| `git is required` / `cannot clone` | Cài git, kiểm mạng tới github.com |

## Gỡ

```bash
bash ~/.mk-lab/install.sh --uninstall --global
bash ~/.mk-lab/install.sh --uninstall --project .   # giữ specs/ và specs/mk-specs.yml
bash ~/.mk-lab/install.sh --uninstall --global --skill <tên>   # chỉ gỡ skill đó
```
