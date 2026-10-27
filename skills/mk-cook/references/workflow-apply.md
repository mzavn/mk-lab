# Mode `apply` — làm proposal đã duyệt

## 1. Trước khi code

1. Chạy cổng: `python3 <skill>/scripts/gate.py <slug>`. Thoát 1 → dừng (SKILL.md cổng cứng 1). Thoát 0 → giữ danh sách "Test cần viết" làm việc phải làm.
2. Đọc proposal (`## Vì sao`, `## Thay đổi spec`, `## Quyết định`, `## Thiết kế`), `plan.md` nếu có, UC chính và `entities` liên quan, ADR được nhắc. Code đụng tới: đọc trước, theo đúng cách repo đang viết (cấu trúc thư mục, tên, thư viện test).
3. Có `plan.md` → làm theo từng phase đúng thứ tự phụ thuộc; mỗi phase xong mới sang phase sau. Không có → làm theo thứ tự UC trong danh sách cổng.
4. Proposal có màn hình (Thay đổi spec/Thiết kế nhắc trang, form, bảng, nút; hoặc có `specs/wireframe.html`) → đọc `ui-lane.md` trước khi viết test.

## 2. Test trước theo AC

Với từng `<UC-ID> AC-n` trong danh sách cổng:

1. Viết test kiểm đúng Given/When/Then của AC: dữ liệu trong Given thành dữ liệu test thật (ngày, số tiền, vai), hành động trong When là thứ người dùng/hệ thống làm, Then kiểm kết quả thấy được — gồm cả hệ quả phủ định ("KHÔNG tạo đơn" → kiểm số đơn không đổi).
2. Tên test nói hành vi, không nói hàm (`test_don_qua_han_khong_thanh_toan_duoc`, không phải `test_check_expiry`). Repo dùng kiểu trích dẫn `name`/`both` (`tests.citation_style` trong `specs/mk-specs.yml`) → tên test mang `UC-xxx / AC-n`.
3. Chạy, thấy **đỏ vì đúng lý do** (hành vi chưa có), không phải vì lỗi cú pháp/import. Được tạo file/hàm rỗng (stub) để test chạy tới assert. Ghi lại lệnh và dòng lỗi — đưa vào bằng chứng.
4. Repo chưa có thư viện test giao diện → test phần logic của AC (hàm thuần: kiểm hợp lệ, tính toán, chọn thông báo) bằng thư viện test repo đang dùng; phần hiển thị kiểm trên trình duyệt (`ui-lane.md` §4). Không tự thêm thư viện test mới khi người dùng chưa đồng ý.
5. AC chỉ kiểm được bằng tay (hành vi agent, thao tác giao diện không có công cụ test) → ghi `⚠ Chưa có test (<lý do>)` và kịch bản kiểm tay; không bịa test giả.

Bug tái hiện được trong phạm vi proposal → test đỏ tái hiện trước, xanh sau.

AC `DEPRECATED` (cổng in ở mục "Bỏ"): xoá hoặc sửa test và code của hành vi bị bỏ; không để test chết; bằng chứng nhắc `<UC-ID> AC-n` kèm việc đã làm.

## 3. Code tối thiểu

- Chỉ đủ cho các AC; không thêm luật, cấu hình, "để sau mở rộng".
- Theo `## Thiết kế` và ADR trong proposal. Thấy thiết kế không khả thi → dừng, tham vấn (SKILL.md cổng cứng 3), sửa proposal rồi mới đi tiếp.
- Mỗi lần xanh một nhóm AC → chạy lại toàn bộ test đã viết của proposal (không chỉ test vừa sửa).
- 3 lần sửa liên tiếp không xanh → dừng, nêu đã thử gì, nghi ngờ ở đâu (AC, thiết kế, môi trường), hỏi người dùng.

## 4. DoD và chạy thử

1. Chạy DoD của project trong `AGENTS.md`/`CLAUDE.md` (test toàn bộ, typecheck, lint, build). Không có → hỏi lệnh, không tự đặt.
2. Chạy thử đường thay đổi như người dùng: gọi API, chạy CLI, mở màn hình (làn UI: trình duyệt thật). Test xanh chưa đủ.
3. Repo có script mk-specs: chạy `gen.py` rồi `verify.py` (lệnh `specs:gen`/`specs:check` nếu repo bọc sẵn). Không có thì bỏ qua — mk-cook không phụ thuộc mã mk-specs.

## 5. Commit code

- Commit test + code, subject mang ID: `feat(UC-204,UC-305): …` / `fix(UC-xxx): …` (luật commit của mk-specs; hook Claude Code của mk-specs có thể chặn commit thiếu ID). Không gộp UC/ADR chính vào commit này.
- Commit trước, bằng chứng sau: bằng chứng cần hash của commit này.

## 6. Bằng chứng và cổng `--done`

Điền `## Bằng chứng nghiệm thu` trong proposal (thay mọi chỗ trống mẫu):

```
- AC ↔ Test: UC-204 AC-9 ↔ `tests/test_layout.py` › "Layout › test_contexts_overrides" (đỏ → xanh); UC-207 AC-7 ↔ ⚠ kiểm tay: kịch bản …, kết quả …
- Trạng thái kiểm chứng: `npm test` → 42 passed; chạy thử: …; giao diện: 375px + 1280px, trạng thái lỗi/rỗng, console lỗi = 0
- Rationale & Quyết định: giải pháp chọn, vì sao; tham vấn/ADR nếu có
- Tính truy vết: commit `a1b2c3d`, file chính `src/…`
```

- Mỗi AC thêm/sửa/bỏ xuất hiện dạng `<UC-ID> AC-n` (cổng kiểm). Bằng chứng là nơi ghi AC ↔ test; dòng `- Tests:` trong UC chính do mk-specs `merge` ghi.
- Chạy `python3 <skill>/scripts/gate.py <slug> --done` tới khi thoát 0, rồi đổi `- Status:` thành `implemented (code <hash>)`.
- Trong lúc làm, người dùng trả lời câu hỏi làm đổi AC → ghi "Điều chỉnh <ngày>: …" vào proposal và xin duyệt lại phần đổi (mk-specs `workflow-change.md` §7); câu trả lời không đổi AC → ghi vào Rationale.

## 7. Bàn giao

- Báo người dùng: AC đã xanh, bằng chứng ở đâu, việc tiếp theo là mk-specs `merge` (hợp nhất vào UC, History mang hash, archive).
