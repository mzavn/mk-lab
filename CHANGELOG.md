# Nhật ký thay đổi

Mỗi bản có số dạng `X.Y.Z`:

- **Số cuối (Z)** tăng: sửa lỗi nhỏ, cách dùng không đổi.
- **Số giữa (Y)** tăng: có thêm tính năng; cập nhật xong dùng tiếp bình thường.
- **Số đầu (X)** tăng: cập nhật xong bạn cần làm thêm một bước — bản đó sẽ ghi rõ bước gì.

Cập nhật: `bash ~/.mk-lab/install.sh --update`. Agent cũng tự nhắc khi có bản mới.

## Chưa phát hành

Dự kiến: v2.0.0

**Cần làm khi cập nhật** (máy đã cài trước bản này — có thư mục `~/.mk-skills`)

Thư mục clone và biến môi trường đổi theo tên mới của repo: `~/.mk-skills` → `~/.mk-lab`, `MK_SKILLS_…` → `MK_LAB_…`. Tên cũ không còn tác dụng. Làm một lần, theo thứ tự:

1. Đã đặt biến nào bắt đầu bằng `MK_SKILLS_` (vd `MK_SKILLS_NO_UPDATE_CHECK=1` hoặc `MK_SKILLS_HOME=…` trong `~/.zshrc`)? Đổi thành `MK_LAB_…` (`MK_LAB_NO_UPDATE_CHECK`, `MK_LAB_HOME`) rồi mở terminal mới. Không đặt biến nào thì bỏ qua.
2. Cài lại bản chung — lệnh clone vào `~/.mk-lab` và thay bản cũ:
   `curl -fsSL https://raw.githubusercontent.com/mzavn/mk-lab/main/install.sh | bash -s -- --global`
3. Xoá thư mục clone cũ `~/.mk-skills` khi cả hai đúng: `cat ~/.claude/skills/mk-specs/.mk-specs-source` in đường dẫn kết thúc bằng `.mk-lab` (không còn `.mk-skills`), và `git -C ~/.mk-skills status --short` không in gì (bạn không sửa gì trong đó). Rồi: `rm -rf ~/.mk-skills`. Không có thư mục này thì bỏ qua.
4. Mỗi repo đã cài mk-specs: `bash ~/.mk-lab/install.sh --update --project .` (clone tay: thay `~/.mk-lab` bằng nơi clone) rồi commit `.claude/skills/mk-specs` như mọi lần cập nhật. Chưa làm bước này thì trong repo đó biến tắt nhắc mới (`MK_LAB_NO_UPDATE_CHECK`) chưa có tác dụng.

Tự clone repo bằng tay (không ở `~/.mk-skills`) và không đặt biến nào: thay bước 2–3 bằng `bash <nơi clone>/install.sh --update` như mọi lần, rồi làm bước 4. Bỏ qua cả bốn bước thì lệnh cũ `bash ~/.mk-skills/install.sh --update` vẫn chạy, nhưng các biến `MK_SKILLS_…` không còn tác dụng (vd đã tắt nhắc bản mới thì sẽ được nhắc lại) — ít nhất hãy làm bước 1.

**Mới**

- `install.sh` cài được nhiều skill: thêm `--skill <tên>` (mặc định `mk-specs`, lệnh cũ chạy như trước). `--update` giờ cập nhật mọi skill đã cài bằng `install.sh`. Thư mục skill cùng tên mà không do `install.sh` tạo thì bị từ chối thay vì bị ghi đè.

**Sửa**

- Repo đổi tên thành **mk-lab** (`github.com/mzavn/mk-lab`, bộ skill lập trình). Lệnh cài, nhắc bản mới và link CHANGELOG giờ trỏ tên mới; địa chỉ cũ trên GitHub tự chuyển sang tên mới.

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
