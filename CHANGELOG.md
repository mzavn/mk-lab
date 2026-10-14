# Nhật ký thay đổi

Mỗi bản có số dạng `X.Y.Z`:

- **Số cuối (Z)** tăng: sửa lỗi nhỏ, cách dùng không đổi.
- **Số giữa (Y)** tăng: có thêm tính năng; cập nhật xong dùng tiếp bình thường.
- **Số đầu (X)** tăng: cập nhật xong bạn cần làm thêm một bước — bản đó sẽ ghi rõ bước gì.

Cập nhật: `bash ~/.mk-skills/install.sh --update`. Agent cũng tự nhắc khi có bản mới.

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
