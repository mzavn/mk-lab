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
| **Context** | Vùng nghiệp vụ | Một mảng có ngôn ngữ riêng (catalog, checkout…); mỗi vùng một thư mục trong `specs/` | Gộp/tách khi thấy một từ mang hai nghĩa |
| **Traceability** | Truy vết | `traceability.md` sinh tự động: UC ↔ AC ↔ test; lỗi production tìm ra spec trong 1 phút | Xem AC nào chưa có test |
| **Characterization test** | Test chụp hành vi | Test ghi lại code cũ *đang* làm gì (đúng hay sai) trước khi sửa, để biết có đổi hành vi không | Đồng ý trước khi refactor code cũ |
| **AC Coverage / Spec Coverage / Trace Ratio** | Chỉ số | Tỉ lệ AC có test · UC đang chạy có AC có test · commit mang mã UC | Theo dõi Trace Ratio trước |

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
| **CHANGELOG** | Nhật ký thay đổi | `CHANGELOG.md` của skill: mỗi bản có gì mới, viết bằng lời người dùng | Đọc trước khi cập nhật |
