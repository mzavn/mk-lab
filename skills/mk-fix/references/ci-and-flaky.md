# Lỗi chỉ hỏng trên CI, test chập chờn

Hai trường hợp này vẫn đi đủ luồng chung (tái hiện → tra AC → xếp loại); file này thêm cách tái hiện, cách xếp loại riêng và cách chứng minh đã sửa.

## 1. Chỉ hỏng trên CI (máy local xanh)

### Tái hiện
1. Lấy log của lượt CI thất bại (người dùng dán, hoặc lệnh CLI của nền tảng nếu repo đã cấu hình và người dùng cho phép). Ghi mã lượt.
2. Tìm **bước hỏng đầu tiên**: đọc từ trên xuống, dừng ở bước đầu tiên thoát khác 0. Lỗi ở các bước sau thường là hệ quả. Trong bước đó, tìm dòng lỗi đầu tiên (không phải dòng tóm tắt cuối).
3. Liệt kê khác biệt môi trường giữa CI và máy local, đánh dấu cái nào đã kiểm:

| Khác biệt | Kiểm bằng |
|---|---|
| Phiên bản ngôn ngữ/runtime/công cụ | file cấu hình CI so với `--version` ở máy |
| Biến môi trường | biến khai trong CI so với máy (chỉ so tên, không in giá trị bí mật) |
| Hệ điều hành, shell, múi giờ, locale | image của CI; `uname`, `bash --version`, `TZ`, `LANG` |
| File khoá phụ thuộc | CI cài theo file khoá hay cài bản mới nhất; file khoá có được commit |
| Dữ liệu/trạng thái | thứ tự test, file sinh ra chỉ có ở máy dev, cache, quyền ghi thư mục |

4. Cố tái hiện local bằng cách đưa khác biệt nghi ngờ về máy (đổi phiên bản, đặt biến, chạy trong container cùng image). Tái hiện được local → sửa như thường. Không tái hiện được local → log CI là cách tái hiện; mọi lần thử được kiểm bằng lượt CI.

### Xếp loại: môi trường nào repo hứa hỗ trợ?
Tìm phiên bản/hệ điều hành repo khai hỗ trợ: `AGENTS.md`, README, CI matrix, `engines` (package.json), `requires-python`/`python_requires`, AC nói về môi trường.
- Môi trường hỏng **nằm trong** danh sách khai hỗ trợ và Then của một AC không đạt (kể cả test của AC đỏ vì import/cú pháp) → `code sai AC`: sửa code cho chạy được trên đó; đỏ vì import ở đây là đỏ hợp lệ (`root-cause.md` §2).
- **Không nằm trong** danh sách (CI chạy bản cũ không ai hứa) → `hạ tầng`: sửa cấu hình CI cho khớp điều đã khai.
- Không tìm thấy khai báo nào → hỏi người dùng repo hỗ trợ những phiên bản nào; không tự chọn.

### Bằng chứng sau sửa
- Lượt CI mới xanh, ghi mã lượt vào phiếu. Xanh ở máy local không đủ.
- Người dùng chưa cho push → không push; phiếu ghi `Kiểm: chờ CI` và báo "chưa xong — chờ lượt CI"; không báo xong.
- Mỗi lần đẩy để thử trên CI tính là một lần thử (cổng ba lần thử vẫn áp dụng).

### Thêm vào phiếu
```text
CI: lượt <mã> đỏ ở bước "<tên bước>": <dòng lỗi đầu tiên>
Khác biệt môi trường: <đã tìm> (đã kiểm: …; chưa kiểm: …)
Sau sửa: lượt <mã> xanh | chờ CI
```

## 2. Test chập chờn (lúc đỏ lúc xanh, code không đổi)

### Đo trước khi sửa
- Số lần chạy N = 20, hoặc số `AGENTS.md` của repo quy định.
- Chạy riêng test đó N lần liên tiếp, đếm số lần hỏng. Ví dụ (đổi theo bộ chạy test của repo):

```bash
fails=0; for i in $(seq 1 20); do python3 -m pytest tests/test_don.py::test_het_han -q >/dev/null 2>&1 || fails=$((fails+1)); done; echo "hỏng $fails/20"
```

- Hỏng ≥ 1 → đã tái hiện; ghi số. Hỏng 0 → **chưa tái hiện được**: không sửa; thử chạy cùng cả bộ test (lỗi do thứ tự/trạng thái dùng chung), song song, hoặc hỏi người dùng log lượt hỏng (`triage.md` §1).

### Tìm nguyên nhân
| Nhóm | Dấu hiệu | Hướng sửa |
|---|---|---|
| Thời gian | dùng giờ thật, `sleep`, hạn chót sát biên | tiêm đồng hồ giả, so theo sự kiện thay vì chờ |
| Thứ tự test | chỉ hỏng khi chạy cùng test khác | test tự dựng và dọn dữ liệu của mình |
| Trạng thái dùng chung | biến toàn cục, file tạm cố định, DB dùng chung, cache | tách theo test, thư mục tạm riêng |
| Mạng | gọi dịch vụ thật, cổng cố định | thay bằng bản giả ở ranh giới, cổng ngẫu nhiên do hệ điều hành cấp |
| Ngẫu nhiên | dữ liệu sinh ngẫu nhiên, thứ tự dict/set | cố định seed, sắp xếp trước khi so |

Nguyên nhân có thể nằm trong code chứ không trong test (race thật) → đó là `code sai AC`, sửa code.

Nguyên nhân nằm **trong chính test** (sinh dữ liệu ngoài AC, phụ thuộc thứ tự, giờ thật; code và mọi Then vẫn đúng) → loại `hạ tầng`; sửa test theo `root-cause.md` §3 (trích AC, chỉ điểm test lệch); commit `test(UC-xxx): …` với UC của AC mà test đó bảo vệ; không History UC.

### Không được dùng
Bọc chạy lại tự động (`retry`, `--reruns`, `flaky` decorator), đánh dấu bỏ qua, xoá test, **chỉ** tăng thời gian chờ/timeout. Tăng timeout chỉ chấp nhận khi đi kèm nguyên nhân đã chứng minh và giá trị có lý do.

### Đo sau khi sửa
Chạy lại đúng N lần như lúc đo trước: phải 0 lần hỏng. Rồi DoD của repo.

### Thêm vào phiếu
```text
Chập chờn: trước sửa hỏng <k>/<N>; sau sửa hỏng 0/<N> (lệnh: <lệnh lặp>)
Nguyên nhân: <thời gian | thứ tự test | trạng thái dùng chung | mạng | khác> — <file:dòng>
```
