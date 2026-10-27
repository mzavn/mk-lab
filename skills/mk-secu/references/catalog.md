# Danh mục lớp lỗi (mã dùng ở `- Lớp:`)

Danh mục giúp **dò**, không thay cho bằng chứng: khớp dấu hiệu chỉ tạo *ứng viên*; ứng viên thành `xác nhận` khi đủ
sáu sự kiện và dấu vết (`SKILL.md`). Độ tin nguồn N1–N4 xem `audit.md` §2. Lỗi không thuộc lớp nào → `- Lớp: KHAC`
và nói rõ trong tiêu đề. Mỗi lớp: dấu hiệu · nguồn đáng ngại · khi nào nặng · khi nào hạ (hoặc bỏ) · cần chứng minh · sửa.

**Chọn lớp theo chỗ code sai, không theo hậu quả.** Tên file ghép từ tham số làm đọc được file khoá → `PATH-TRAVERSAL`
(không phải `SECRET`); template tắt escape làm lộ phiên → `XSS` (không phải `SESSION`); câu trừ số dư không điều kiện
cho hai yêu cầu song song cùng rút → `RACE` (không phải `AUTHZ`). Một gốc lỗi = một phát hiện; hậu quả dây chuyền ghi
ở `- Hậu quả:`; token đầu của `- Dấu vết:` là chỗ code sai (chỗ sẽ sửa), không phải route hay nguồn.

## Nhóm 1 — Quyền và danh tính

### IDOR — Đọc/sửa đối tượng của người khác
- Dấu hiệu: lấy bản ghi theo mã từ đường dẫn/tham số (`WHERE id = ?`, `findById`) mà không lọc theo người đang đăng nhập.
- Nguồn: N1 (mã đối tượng trên URL, body). Mã tuần tự hay UUID đều tính — UUID chỉ làm khó đoán, không phải kiểm quyền.
- Nặng khi: đối tượng chứa tiền, dữ liệu cá nhân, tài liệu; hoặc thao tác là sửa/xoá.
- Hạ/bỏ khi: dữ liệu công khai theo spec; có kiểm chủ ở tầng khác (middleware, policy, row-level security) — phải chỉ ra.
- Chứng minh: đường từ tham số tới truy vấn, và chỗ lẽ ra so `owner == người gọi` mà không có.
- Sửa: lọc theo chủ ngay trong truy vấn; trả "không tìm thấy" như đối tượng không tồn tại.

### AUTHZ — Thiếu kiểm quyền theo chức năng
- Dấu hiệu: route quản trị/nhân viên chỉ kiểm "đã đăng nhập"; vai đọc từ thứ người dùng gửi (header, body, cookie không ký); ẩn nút ở giao diện thay cho kiểm ở máy chủ.
- Nguồn: N1 (vai, cờ `isAdmin` do client gửi).
- Nặng khi: chức năng xoá, xuất dữ liệu, đổi vai, hoàn tiền.
- Hạ/bỏ khi: route không đăng ký ra ngoài (chỉ gọi nội bộ, chứng minh được); spec cho mọi vai làm việc đó.
- Chứng minh: bảng route → hàm, và vai thấp nhất gọi được.
- Sửa: kiểm vai ở máy chủ, từ dữ liệu mà client không tự sửa được.

### MASS-ASSIGN — Nhận nguyên body vào bản ghi
- Dấu hiệu: `Model.update(req.body)`, `**data`, vòng lặp gán mọi khoá; danh sách trường cho phép lẫn trường chỉ hệ thống hay người quản trị được đổi (vai, quyền, số dư, trạng thái xác minh, chủ sở hữu, định danh đăng nhập).
- Nguồn: N1 (khoá và giá trị trong body).
- Nặng khi: tự nâng vai, tự cộng tiền, đổi chủ sở hữu, đổi định danh đăng nhập (chiếm tài khoản).
- Hạ/bỏ khi: danh sách cho phép chỉ có trường vô hại; schema xác thực loại bỏ khoá lạ.
- Chứng minh: khoá nhạy cảm đi được tới câu ghi.
- Sửa: danh sách trường cho phép theo từng thao tác; trường nhạy cảm có luồng riêng.

### SESSION — Phiên, JWT, cookie
- Dấu hiệu: JWT chấp nhận `alg: none` hoặc không kiểm chữ ký (`decode` thay `verify`); khoá ký quá ngắn/dễ đoán (khoá nằm trong mã/git → `SECRET`); phiên không hết hạn, không thu hồi được khi đăng xuất/đổi mật khẩu; cookie phiên thiếu `HttpOnly`/`Secure`.
- Nguồn: N1 (token do client giữ).
- Nặng khi: giả được phiên người khác hoặc vai cao hơn.
- Hạ khi: chỉ thiếu cờ cookie mà không có đường XSS/mạng hở đi kèm (ghi `cần kiểm thêm`, nêu sự kiện thiếu).
- Chứng minh: chỗ tạo và chỗ kiểm token; giá trị nào client đổi được mà máy chủ vẫn nhận.
- Sửa: kiểm chữ ký với thuật toán cố định, hạn ngắn, khoá từ kho bí mật.

### WEAK-HASH — Băm mật khẩu yếu
- Dấu hiệu: mật khẩu lưu thẳng, hoặc băm bằng MD5/SHA-1/SHA-256 một lần, không muối.
- Nguồn: N2 (bảng mật khẩu khi DB bị lộ).
- Nặng khi: hệ thống có nhiều người dùng thật, mật khẩu có thể dùng lại ở nơi khác.
- Hạ/bỏ khi: hàm băm nhanh dùng cho việc không dính tới mật khẩu hay chữ ký (nhận diện nội dung, chia nhóm) — không phải lỗi.
- Chứng minh: hàm băm nằm trên đường lưu/kiểm **mật khẩu**.
- Sửa: bcrypt/scrypt/argon2 hoặc PBKDF2 nhiều vòng, có muối.

### RATE-LIMIT — Không giới hạn thử ở chỗ xác thực
- Dấu hiệu: đăng nhập, quên mật khẩu, OTP, mã mời không đếm số lần thử theo tài khoản/IP.
- Nguồn: N1 (yêu cầu lặp tự động).
- Nặng khi: OTP ngắn (4–6 số), không có khoá tạm; spec có AC khoá mà code không làm.
- Có AC đòi khoá/giới hạn mà chỉ app làm được (khoá theo tài khoản) và code không có → `xác nhận`
  (`code sai AC`); gateway không thay được. Không có AC và có thể có giới hạn ở tầng trước (gateway, WAF) không thấy trong
  repo → `cần kiểm thêm`. Giới hạn thấy được trong repo (cấu hình) → hạ mức hoặc bỏ.
- Chứng minh: hàm xử lý không có bộ đếm, không có middleware giới hạn trên route.
- Sửa: đếm theo tài khoản + IP, khoá tạm, trả lời giống nhau khi sai.

## Nhóm 2 — Dữ liệu chảy vào chỗ nguy hiểm

### SQLI — Chèn SQL/NoSQL
- Dấu hiệu: ghép chuỗi/f-string/template vào câu truy vấn; `raw()`, `$where`, toán tử Mongo lấy từ object người dùng gửi (`{"$ne": null}`).
- Nguồn: N1; N2 khi giá trị đã lưu được ghép lại vào câu khác.
- Nặng khi: đọc/sửa bảng khác, vượt điều kiện chủ sở hữu, đăng nhập không cần mật khẩu.
- Hạ/bỏ khi: phần ghép không mang N1 — hằng, hoặc giá trị đã bị kiểm khớp danh sách cho phép (vd trong module schema/validator dùng chung) trước khi tới đây; lần ngược tới nguồn, qua cả file khác — không phải lỗi.
- Chứng minh: giá trị N1 đi tới chuỗi SQL mà không qua tham số hoá hay danh sách cố định.
- Sửa: truy vấn tham số hoá; tên cột/hướng sắp xếp chọn từ danh sách cho phép.

### XSS — Chèn mã vào trang
- Dấu hiệu: `innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `|safe`, `mark_safe`, template tắt escape; ghép HTML bằng chuỗi.
- Nguồn: N1 (phản xạ) hoặc N2 (đã lưu — bình luận, tên, mô tả).
- Nặng khi: trang có phiên người khác (quản trị xem nội dung khách gửi), cookie phiên đọc được bằng script.
- Hạ/bỏ khi: giá trị đã escape đúng ngữ cảnh; CSP chặn script nội tuyến (vẫn ghi nếu có đường vòng).
- Chứng minh: giá trị đi từ nguồn tới chỗ render mà không qua escape.
- Sửa: để framework escape; HTML cho phép thì lọc bằng thư viện sanitize.

### CMDI — Chèn lệnh hệ điều hành
- Dấu hiệu: `os.system`, `exec`, `subprocess(..., shell=True)`, `child_process.exec`, backtick shell ghép đầu vào.
- Nguồn: N1; N2 (tên file đã lưu).
- Nặng khi: hầu như luôn nặng — chạy lệnh trên máy chủ.
- Hạ/bỏ khi: gọi bằng danh sách đối số, chương trình cố định, đầu vào không thể bắt đầu bằng `-` hoặc có `--` chặn.
- Chứng minh: đầu vào tới chuỗi lệnh đi qua shell.
- Sửa: gọi không qua shell với danh sách đối số; thư viện thay cho lệnh ngoài.

### PATH-TRAVERSAL — Đọc/ghi file ngoài thư mục cho phép
- Dấu hiệu: `open(dir + name)`, `path.join(base, req.query.file)`, `send_file` với tên do người dùng gửi; giải nén không kiểm `../`.
- Nguồn: N1 (tên file, đường dẫn, mục trong file nén).
- Nặng khi: đọc được cấu hình/khoá, ghi đè file mã.
- Hạ/bỏ khi: tên chỉ là khoá tra trong bảng; đường dẫn đã chuẩn hoá rồi kiểm nằm trong thư mục gốc.
- Chứng minh: đầu vào tới hàm mở file mà không chuẩn hoá + kiểm tiền tố.
- Sửa: tra tên qua bảng; hoặc `realpath` rồi kiểm nằm trong thư mục gốc.

### SSRF — Máy chủ đi lấy URL do người dùng chọn
- Dấu hiệu: tải ảnh/xem trước link/webhook từ URL người dùng gửi (`requests.get(url)`, `urlopen`, `fetch`).
- Nguồn: N1 (URL, tên miền, cổng).
- Nặng khi: máy chủ chạy trên cloud (địa chỉ metadata), có dịch vụ nội bộ, và nội dung lấy về được trả lại cho người gửi.
- Hạ khi: chỉ gọi tới danh sách tên miền cố định; nội dung không trả lại (SSRF mù — vẫn ghi, mức thấp hơn).
- Chứng minh: URL đi từ đầu vào tới hàm gọi mạng; không kiểm địa chỉ đích sau khi phân giải.
- Sửa: danh sách tên miền cho phép; chặn dải nội bộ sau khi phân giải; không theo chuyển hướng.

### DESERIAL — Giải tuần tự dữ liệu không tin
- Dấu hiệu: `pickle.loads`, `yaml.load` không `SafeLoader`, `unserialize`, `ObjectInputStream`, `Marshal.load` trên dữ liệu ngoài.
- Nguồn: N1 (cookie, body, file tải lên); N2 khi kẻ ngoài ghi được vào kho đó.
- Nặng khi: thường dẫn tới chạy mã.
- Hạ/bỏ khi: dữ liệu do chính app tạo và chỉ app ghi được (N3/N4) — chỉ ra không có đường ghi từ ngoài.
- Chứng minh: ai ghi được dữ liệu trước khi nó bị giải.
- Sửa: định dạng dữ liệu thuần (JSON) + kiểm schema.

### FILE-UPLOAD — Tải file lên
- Dấu hiệu: lưu file với tên/đuôi do người dùng gửi, vào thư mục web phục vụ trực tiếp; chỉ kiểm `Content-Type` hoặc đuôi phía client; không giới hạn cỡ.
- Nguồn: N1 (tên, đuôi, nội dung).
- Nặng khi: file được chạy (`.php`, `.jsp`) hoặc phục vụ cùng tên miền (HTML/SVG → XSS).
- Hạ khi: lưu ở kho riêng tên ngẫu nhiên, phục vụ với `Content-Disposition: attachment` từ tên miền khác.
- Chứng minh: đường từ file tải lên tới chỗ lưu và chỗ phục vụ.
- Sửa: đặt tên mới, kiểm nội dung thật, lưu ngoài thư mục web, giới hạn cỡ.

### LLM-TOOL — Chèn chỉ thị vào tính năng dùng LLM
- Dấu hiệu: nội dung người dùng/trang web/email ghép thẳng vào prompt của agent có công cụ (gửi mail, chạy SQL, gọi API, đọc file); đầu ra LLM được chạy như mã/SQL/HTML.
- Nguồn: N1 (cả nội dung gián tiếp: tài liệu, trang được tóm tắt). Đầu ra LLM coi như N1.
- Nặng khi: công cụ có quyền ghi, gửi ra ngoài, đọc dữ liệu người khác.
- Hạ khi: LLM không có công cụ, đầu ra chỉ hiển thị đã escape.
- Chứng minh: đường từ nội dung kém tin tới prompt, và công cụ nguy hiểm agent đó gọi được mà không cần người duyệt.
- Sửa: tách quyền công cụ theo người dùng, xác nhận trước hành động ghi, coi đầu ra LLM là dữ liệu.

## Nhóm 3 — Cấu hình, bí mật, phụ thuộc

### SECRET — Bí mật trong mã hoặc trong git
- Dấu hiệu: khoá API, mật khẩu DB, khoá ký phiên viết cứng; `.env`, khoá riêng nằm trong git (`secu.py scope` báo `NHẠY CẢM`); khoá server lộ ra bundle phía client (`NEXT_PUBLIC_…`, `VITE_…`).
- Nguồn: bất kỳ ai đọc được repo hoặc bundle.
- Nặng khi: khoá có quyền ghi/thanh toán, khoá ký phiên. Repo riêng tư **không** hạ mức: lịch sử git, bản fork, máy người cộng tác cũ vẫn giữ khoá.
- Hạ khi: giá trị rõ ràng giả/mẫu (`changeme`, `.env.example` không có giá trị thật) — khi đó không phải phát hiện.
- Chứng minh: file + dòng + khoá dùng để làm gì (che giá trị, giữ ≤ 4 ký tự đầu).
- Sửa: chuyển sang biến môi trường/kho bí mật **và** thu hồi/đổi khoá (gỡ khỏi code không xoá khỏi lịch sử git). Loại: `hạ tầng` (repo chưa có spec → `chưa có spec`; vẫn ghi thu hồi/đổi khoá ở `- Đề xuất sửa:`).

### DEBUG-ERROR — Chế độ debug, lỗi lộ chi tiết
- Dấu hiệu: `DEBUG = True`, `app.run(debug=True)`, trả stack trace/câu SQL/biến môi trường cho client; trang debug công khai.
- Nguồn: N1 (gây lỗi có chủ đích).
- Nặng khi: debugger tương tác (chạy mã), hoặc lỗi kèm bí mật.
- Hạ/bỏ khi: chỉ ở cấu hình dev được chọn bằng biến môi trường, không có đường bật ở production — không phải phát hiện.
- Chứng minh: cấu hình production thật sự dùng giá trị đó.
- Sửa: tắt theo môi trường, trả lỗi chung, ghi chi tiết vào log.

### CORS — Cho trang khác đọc dữ liệu có phiên
- Dấu hiệu: phản chiếu `Origin` hoặc `*` cùng `Access-Control-Allow-Credentials: true`; danh sách origin so khớp lỏng (`endswith`).
- Nguồn: trang độc mà người dùng đang đăng nhập mở.
- Nặng khi: API trả dữ liệu cá nhân bằng cookie phiên, cookie `SameSite=None`.
- Hạ/bỏ khi: API không dùng cookie (token trong header do JS tự gắn); dữ liệu công khai.
- Chứng minh: header CORS + cách xác thực + cookie gửi chéo trang được.
- Sửa: danh sách origin chính xác; không bật credentials khi không cần.

### CSRF — Thao tác thay người dùng từ trang khác
- Dấu hiệu: thao tác ghi bằng cookie phiên, không token CSRF, cookie không `SameSite=Lax/Strict`; thao tác ghi bằng `GET`.
- Nguồn: trang độc mà người dùng đang đăng nhập mở.
- Nặng khi: đổi email/mật khẩu, chuyển tiền, xoá.
- Hạ/bỏ khi: xác thực bằng header (Bearer) không tự gửi; cookie `SameSite=Strict`; framework có token mặc định đang bật.
- Chứng minh: request chéo trang mang được cookie và máy chủ không kiểm gì thêm.
- Sửa: `SameSite` + token CSRF cho thao tác ghi; không ghi bằng `GET`.

### DEP-NAME — Tên phụ thuộc lạ (slopsquatting)
- Dấu hiệu: gói trong file khai báo hoặc `import` không có trong kho chính thức, tên gần giống gói nổi tiếng, gói mới thêm không ai nhắc trong code review; script `postinstall` lạ.
- Nguồn: kẻ đăng ký trước tên gói mà AI hay bịa.
- Nặng khi: gói chạy lúc cài (script cài đặt) hoặc nằm trên đường xử lý dữ liệu nhạy cảm.
- Hạ khi: gói nội bộ có registry riêng cấu hình trong repo.
- Chứng minh: v1 không gọi mạng nên không tra được kho gói → thường là `cần kiểm thêm` ("Còn thiếu: tra tên gói trên kho chính thức"), trừ khi repo tự cho thấy (lockfile trỏ registry lạ).
- Sửa: dùng gói chính chủ, ghim phiên bản trong lockfile, xoá gói không dùng.

### RACE — Tranh chấp ở tiền, kho, lượt dùng
- Dấu hiệu: đọc số dư/tồn kho/lượt dùng mã giảm giá → kiểm → ghi ở hai câu riêng, không khoá, không giao dịch, không điều kiện trong câu ghi.
- Nguồn: N1 (gửi nhiều yêu cầu song song).
- Nặng khi: tiền, điểm, tồn kho, mã dùng một lần — spec thường có AC "không âm"/"một lần".
- Hạ khi: chạy một tiến trình một luồng theo cấu hình thấy được; câu ghi có điều kiện (`UPDATE … WHERE balance >= ?`) và kiểm số dòng bị đổi.
- Chứng minh: khoảng giữa lần đọc và lần ghi, và cách hai yêu cầu cùng lọt qua.
- Sửa: một câu ghi có điều kiện hoặc khoá hàng trong giao dịch; khoá duy nhất cho thao tác một lần.

## Không phải phát hiện

- "Nên thêm header X", "nên dùng thư viện Y", "nên log thêm" khi không có đường khai thác — đó là khuyến nghị.
- Phòng thủ chiều sâu: lớp bảo vệ thứ hai thiếu trong khi lớp thứ nhất đúng.
- Kẻ tấn công phải có sẵn quyền cao hơn thứ họ đạt được (quản trị "tấn công" chính dữ liệu mình quản).
- Code chết, test, script dev không chạy ở production (chỉ ra vì sao không chạy).
- Lỗ hổng của phụ thuộc theo CVE — v1 không tra mạng; nếu nghi, ghi vào `## Chưa soát`.
