# Script và test của skill

Đọc khi skill cần script. Script là nơi quyết định những gì phải giống nhau ở mọi model; chữ trong `SKILL.md` chỉ nói khi nào chạy, đọc kết quả thế nào. Mọi luật đánh dấu **[máy]** do `validate.py` kiểm.

## 1. Khi nào viết script

| Việc | Script hay chữ |
|---|---|
| Đếm, so khớp, tìm trường thiếu, kiểm định dạng file | script |
| Chặn/qua một cổng (đủ điều kiện chưa) | script — thoát mã + dòng lý do |
| Ghi/sửa một dòng cố định trong file người dùng (đánh dấu "đã làm") | script — chỉ đổi đúng dòng đó |
| Nhận định, phản biện, chọn phương án, viết câu | chữ (agent; agent riêng khi cần độc lập) |

Một script một việc rõ; nhiều việc gần nhau → lệnh con (`check`, `smoke`) trong cùng file.

## 2. Luật viết

1. **Python 3, chỉ thư viện chuẩn** **[máy]**. Chạy được từ Python 3.9 (macOS có sẵn) tới bản mới nhất; module chỉ có ở bản mới (vd `tomllib`) → có đường lui hoặc báo rõ.
2. Ngay sau các dòng import: `sys.dont_write_bytecode = True` — để không sinh `__pycache__` trong thư mục skill đã cài **[máy, với file chạy như lệnh]**.
3. **Đầu ra tất định**: cùng đầu vào → cùng từng byte. Sắp xếp mọi danh sách (theo đường dẫn, theo mã); không in thời gian, số ngẫu nhiên, thứ tự của `set`/`dict` chưa sắp; ngày tính theo UTC hoặc truyền vào bằng tham số (`--today`).
4. **Thoát mã có nghĩa**, ghi ở docstring đầu file: 0 xong/qua; 1 lỗi hoặc bị chặn; skill cần phân biệt "sai cách gọi" thì dùng thêm 2. Lỗi in một dòng `Lỗi: <lý do bằng lời thường>`, không văng traceback cho lỗi đoán trước được (file không có, sai định dạng, quyền).
5. Dòng in ra dành cho agent đọc: tiền tố cố định (`OK:`, `LỖI:`, `CHẶN:`, `Cảnh báo:`), mỗi ý một dòng, có `file:dòng` khi trỏ vào file.
6. **Chỉ đọc** là mặc định. Script cần ghi thì:
   - không ghi đè file đã có, trừ khi việc của script là sửa đúng file đó (mở `"x"` khi tạo mới);
   - không ghi xuyên symlink: kiểm `os.path.islink` / `os.path.lexists` trên file đích, từ chối khi là symlink;
   - không ghi dở: ghi vào file tạm cùng thư mục rồi `os.replace`; lỗi giữa chừng → xoá file tạm, file cũ nguyên vẹn;
   - không xoá file người dùng; chỉ ghi trong thư mục skill đã nói (thư mục nhật ký, thư mục tạm của phiên).
7. Đường dẫn và mẫu regex lấy từ file cấu hình/người dùng là **dữ liệu**: đường dẫn ra ngoài thư mục được phép → từ chối; regex dài hoặc có nhóm lặp lồng nhau → từ chối.
8. Không gọi mạng, trừ khi đó là việc của skill (và chỉ tới địa chỉ người dùng chỉ định). Không chạy lệnh lấy từ file người dùng.
9. Gọi git: `git --no-optional-locks …` khi chỉ đọc; không lệnh ghi git.
10. Docstring đầu file: một câu việc, cách gọi, thoát mã. Không cần thêm tài liệu khác cho script.

## 3. Test

- Mỗi script có test `unittest` trong `scripts/tests/test_<script>.py` **[máy: có ít nhất một `scripts/tests/test_*.py`]**. Khuôn: `assets/test_script.py.template`.
- **Test hành vi người dùng thấy**: chạy script bằng `subprocess` với `sys.executable` như agent sẽ chạy, kiểm dòng in ra, thoát mã, file tạo/đổi. Không test câu chữ của `SKILL.md`, không test hàm nội bộ chỉ để phủ dòng, không test "đã gọi hàm X".
- Dữ liệu test là dữ liệu giả trong `tempfile.mkdtemp()`, dọn bằng `addCleanup`; không đọc file thật của người dùng, không ghi vào thư mục skill.
- Mỗi tiêu chí chấp nhận một (hoặc vài) test; tên test nói tiêu chí: `test_khong_ghi_de_file_da_co`, `test_ac2_thieu_truong_bao_loi`.
- Có ghi file → test cả: ghi đè bị từ chối, symlink bị từ chối, lỗi giữa chừng không để file dở, chạy hai lần ra cùng kết quả.
- Viết test trước (đỏ), rồi script (xanh). Chạy trên Python cũ nhất và mới nhất có ở máy.
- Chạy test luôn kèm `PYTHONDONTWRITEBYTECODE=1`: `unittest` import file test trước khi dòng `sys.dont_write_bytecode = True` trong file kịp chạy, nên chỉ đặt cờ trong file thì vẫn sinh `__pycache__` cạnh test.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s <repo>/skills/mk-<tên>/scripts/tests
```

## 4. Gọi script trong `SKILL.md`

- Viết lệnh đầy đủ với `<skill>`: `python3 <skill>/scripts/<script>.py <file> [--out <file mới>]`.
- Nói agent làm gì với từng loại dòng in ra (`LỖI` → sửa gì, `Cảnh báo` → báo người dùng câu nào) và với từng thoát mã.
- Script báo lỗi → agent đọc lý do, báo người dùng; không sửa tay thay việc script từ chối làm.
