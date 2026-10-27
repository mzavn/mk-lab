# Nguyên nhân gốc, đỏ-xanh, lần thử, tham vấn

Đọc khi đã xếp `code sai AC` hoặc `hạ tầng` và sắp đổi code.

## 1. Truy ngược tới nguồn

Chỗ lỗi lộ ra (dòng ném ngoại lệ, chỗ hiện sai) hiếm khi là chỗ sai. Đi ngược luồng dữ liệu:

1. Từ chỗ lỗi lộ ra, hỏi: giá trị sai này đến từ đâu? Mở chỗ gọi/chỗ gán ngay trước đó.
2. Lặp lại tới khi gặp chỗ giá trị **bắt đầu** sai so với Then của AC (tính sai, đọc sai trường, đổi đơn vị, so sánh lệch biên, thứ tự xử lý sai, trạng thái dùng chung bị ghi đè).
3. Ghi `file:dòng` của chỗ đó vào `Nguyên nhân gốc:` kèm một câu vì sao. Ví dụ giả: `src/don/han.py:42 — cộng 15 phút vào giờ thanh toán thay vì giờ tạo đơn, nên đơn trả muộn được giữ thêm`.
4. Không đọc được tới nguồn bằng mắt → thêm log/in tạm ở từng tầng, chạy lại cách tái hiện, xem giá trị đổi ở đâu. Việc dò này **không** tính là lần thử (§4). Gỡ hết log tạm trước khi commit.

Dấu hiệu đang vá triệu chứng: thêm `if x is None: return` ở chỗ lỗi lộ ra; bắt ngoại lệ rồi bỏ qua; ép kiểu/làm tròn ở tầng hiển thị. Nếu cách sửa trông như vậy → hỏi tiếp "vì sao x là None?".

`hạ tầng`: nguyên nhân gốc là dòng cấu hình/phiên bản/lệnh (`package.json:18`, `.github/workflows/test.yml:31`), không phải "CI lỗi".

## 2. Đỏ trước, xanh sau

- Test phải đỏ **vì đúng lỗi đang báo**: đọc thông báo assert, so với Then. Đỏ vì fixture sai, đường dẫn import gõ sai trong chính test → chưa phải đỏ hợp lệ. Đỏ vì import/cú pháp hỏng trên môi trường repo khai hỗ trợ (lỗi chỉ hỏng trên CI, `ci-and-flaky.md` §1) → hợp lệ: đó chính là lỗi đang báo.
- Test kiểm điều người dùng thấy (Then), không kiểm chi tiết cài đặt; không mock lõi nghiệp vụ.
- Sau sửa: test đó xanh, rồi cả bộ test và DoD của repo (lệnh trong `AGENTS.md`). Dán dòng tóm tắt thật vào `Kiểm:`.
- Lỗi đã có test xanh mà vẫn xảy ra → test hiện có không kiểm đúng Then. Viết test mới tái hiện được; test cũ để nguyên trừ khi chứng minh sai (§3).

## 3. Không làm yếu test

Khi test của AC đỏ, những việc sau **không** được làm: nới assert (so lỏng hơn, bỏ một điều kiện, tăng sai số), đánh dấu bỏ qua/`skip`/`xfail`, xoá test, bọc chạy lại tự động, chỉnh AC cho khớp với code.

Ngoại lệ duy nhất: test viết sai so với AC. Khi đó phiếu phải có:

```text
AC (nguyên văn): <dán khối Given/When/Then từ ac.py>
Test đang kiểm: <dòng assert> — khác AC ở: <điểm khác>
Sửa test thành: <assert mới> — khớp Then ở: <chữ trong Then>
```

Không trích được chữ nào của AC chứng minh test sai → test đúng, code sai.

Test chập chờn do chính test (sinh dữ liệu ngoài AC, phụ thuộc thứ tự, giờ thật) cũng sửa theo mục này: trích AC, chỉ ra điểm test lệch; loại `hạ tầng`, commit `test(UC-xxx): …`, không History (`ci-and-flaky.md` §2).

## 4. Lần thử và tham vấn có cấu trúc

Một **lần thử** = một lần đổi code **nhằm sửa lỗi** rồi chạy lại cách tái hiện. Thêm log/in tạm để dò nguyên nhân (§1 bước 4) không tính. Đếm từ lần đổi code nhằm sửa đầu tiên cho lỗi này; đổi cách tiếp cận vẫn tính tiếp, không reset.

Lần thử không qua khi: cách tái hiện vẫn lỗi, **hoặc** lỗi hết nhưng test khác hỏng.

Sau lần thứ ba không qua → dừng đổi code (hoàn lại thay đổi dở nếu người dùng muốn, không tự xoá), gửi:

```text
Tham vấn — <UC-ID> AC-n: <triệu chứng>
Đã thử:
1. <đổi gì ở file:dòng> → <kết quả chạy lại: lỗi gì / test nào hỏng>
2. …
3. …
Giả thuyết còn lại: <điều nghi ngờ, kể cả AC/thiết kế có thể sai> — kiểm bằng <cách>
Câu hỏi: <điều cần người dùng trả lời/quyết để đi tiếp>
```

Không thử lần thứ tư khi chưa có trả lời. Ba lần hỏng thường do hiểu sai vấn đề: nguyên nhân ở tầng khác, AC mơ hồ (→ `luật sai`), hoặc hai AC mâu thuẫn.

## 5. Vùng ảnh hưởng

Trước khi báo xong, rà chỗ khác dùng cái vừa sửa:
- Mọi chỗ gọi hàm/đọc trường đã đổi (tìm theo tên); chỗ nào dựa vào hành vi cũ?
- AC khác của cùng UC và UC liên quan (`ac.py <UC-ID>`, `## Dependencies` của UC) — test của chúng còn xanh?
- Dữ liệu đã lưu theo cách sai (đơn cũ tính sai hạn): nêu cho người dùng, không tự chạy sửa dữ liệu thật.

Ghi những gì đã rà vào `Vùng ảnh hưởng:`; chỗ chưa rà ghi rõ "chưa rà".

## 6. Không tin "chắc là được rồi"

| Câu nói | Cần thay bằng |
|---|---|
| "Chắc là sửa xong" | lệnh + kết quả chạy thật |
| "Lỗi này không ảnh hưởng chỗ khác" | danh sách chỗ gọi đã rà |
| "Test cũ đỏ sẵn từ trước" | lệnh chạy trên commit trước khi sửa cho thấy đỏ |
| "Chỉ là lỗi môi trường" | khác biệt môi trường cụ thể đã tìm (`ci-and-flaky.md` §1) |
