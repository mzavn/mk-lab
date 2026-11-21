# Danh mục lớp lỗi — app nhiều công ty, nhiều vai, có agent

Đọc cùng `catalog.md` ở cả hai mode, mọi repo: cùng luật dùng (khớp dấu hiệu chỉ là *ứng viên*; sáu sự kiện + dấu
vết mới thành `xác nhận`), cùng nhãn trường. Lỗi ở nhóm này thường không lộ ra từ một dòng code: phải đặt cạnh AC
(công ty nào thấy gì, vai nào ghi gì, số liệu nào đã chốt) và Entity. Vi phạm AC bảo mật đang chạy → `- Mức:` không
dưới `trung bình` (`audit.md` §7). Mã ở đây và ở `catalog.md` không trùng nhau.

## Chọn mã khi nhiều lớp cùng khớp

Đi từ trên xuống, dừng ở dòng đầu tiên đúng:

| # | Dòng |
|---|---|
| 0 | Dữ liệu N1 tới một chỗ dùng nguy hiểm (câu SQL, HTML, lệnh, đường dẫn file, URL gọi ra, giải tuần tự) → mã của chỗ dùng đó (`SQLI`, `XSS`, `CMDI`, `PATH-TRAVERSAL`, `SSRF`, `DESERIAL`), kể cả khi hậu quả là vượt công ty hay lộ trường. |
| 1 | Bí mật viết cứng trong mã (kể cả trong lời gọi log) → `SECRET`. |
| 2 | Chỉ lọt khi hai yêu cầu chạy song song → `RACE`; lọt cả khi gọi lần lượt → xét tiếp. |
| 3 | Spec/schema có khái niệm công ty và người gọi tới được bản ghi của công ty khác, qua bất kỳ đường nào (truy vấn thiếu lọc, mã công ty từ body/header, cache, job, đường phụ, nhận cả body) → `TENANT`. App không có khái niệm công ty → không dùng `TENANT`. |
| 4 | Nhận nguyên body, hoặc danh sách trường cho phép lẫn trường hệ thống → `MASS-ASSIGN`. |
| 5 | Bản ghi đã chốt hay bất biến Entity bị phá khi gọi lần lượt, kể cả khi đường chính có chặn (khôi phục, nhập, tính lại, đổi trạng thái không qua điều kiện nguồn) → `STATE`. |
| 6 | Chữ kém tin vào prompt, hoặc đầu ra LLM bị chạy → `LLM-TOOL`. Tool kiểm đúng luật quyền như đường web nhưng ghi tiền/quyền/gửi ra ngoài không cần xác nhận ngoài luồng, cờ xác nhận do model điền, tool đã gỡ vẫn gọi được, token rộng hơn việc → `AGENCY`. Có cả hai → hai phát hiện, mỗi phát hiện một token đầu. |
| 7 | Một **đường ghi** khác tới cùng đối tượng có kiểm luật quyền (chỉ ra được `file:dòng`) mà đường này thiếu, kể cả tool gọi thẳng lớp lưu trữ → `PARITY`. |
| 8 | Token thật còn được nhận sau khi quyền đổi (khoá, nghỉ việc, đổi mật khẩu); token trung gian dùng được ở API → `SESSION`. |
| 9 | Chỉ một đường: thiếu kiểm chủ → `IDOR`, thiếu kiểm vai → `AUTHZ`. |
| 10 | Có quyền với bản ghi nhưng không với trường: trong phản hồi thành công hay file xuất → `EXPOSE`; trong lỗi/stack trace → `DEBUG-ERROR`; ghi vào log/nhật ký/hàng đợi → `LOG`. |
| 11 | Chi phí của một yêu cầu không cần đăng nhập → `RESOURCE`; không có bộ đếm số lần thử → `RATE-LIMIT`; loại/nội dung file → `FILE-UPLOAD`. |

Không dòng nào đúng → mã có dấu hiệu khớp trong danh mục.

## Nhóm 4 — App nhiều công ty, nhiều vai, có agent

### TENANT — Đọc/ghi chéo công ty
- Dấu hiệu: truy vấn, JOIN hay truy vấn con theo mã lấy từ yêu cầu mà không có điều kiện công ty; mã công ty đọc từ
  body, header, tham số thay vì từ phiên đã ký; khoá cache không chứa mã công ty; job/hàng đợi tin mã công ty ghi trong
  payload; hàm chặn cho qua khi không xác định được công ty (chặn mở).
- Nguồn: N1 (mã bản ghi, mã công ty client gửi); N2 khi payload của job sinh từ yêu cầu người dùng.
- Nặng khi: tới được tiền, hoá đơn, dữ liệu cá nhân của công ty khác, hoặc ghi/xoá được — thường `nghiêm trọng`/`cao`.
- Hạ/bỏ khi: app không có khái niệm công ty (xét `IDOR`/`AUTHZ`); lọc công ty nằm ở tầng chắc chắn chạy cho bảng đó
  (row-level security đang bật, phạm vi truy vấn mặc định không tắt được) — chỉ ra `file:dòng`.
- Chứng minh: chỗ công ty của người gọi được xác lập từ phiên, và chỗ truy vấn/khoá cache/job không dùng giá trị đó.
- Sửa: lấy công ty từ phiên đã ký và đưa vào mọi truy vấn, khoá cache, payload job; không xác định được → từ chối;
  bản ghi của công ty khác trả "không tìm thấy".
- Gợi ý AC: Given nhân viên công ty B có mã đơn của công ty A When mở hoặc sửa đơn đó Then 404 như đơn không tồn tại.

### PARITY — Đường ghi phụ bỏ kiểm quyền mà đường chính có
- Dấu hiệu: cùng một thứ ghi được bằng vài lối (form sửa, sao chép, khôi phục, nhập file, làm hàng loạt, tool của agent,
  API nội bộ lỡ đăng ký ra ngoài); đường chính gọi hàm kiểm quyền/policy, đường phụ gọi thẳng lớp lưu trữ.
- Nguồn: N1 (yêu cầu gửi tới đường phụ, kể cả qua agent).
- Nặng khi: đường phụ cho vai thấp làm điều đường chính cấm: đổi quyền, ghi tiền, sửa bản ghi của người khác.
- Hạ/bỏ khi: đường phụ đi qua cùng lớp dịch vụ có kiểm; chỉ vai được spec cho phép mới gọi tới đường phụ.
- Chứng minh: hai vị trí — **token đầu của `- Dấu vết:` là đường yếu** (chỗ sẽ sửa), token sau là đường có kiểm làm
  đối chứng. `secu.py check` chặn PARITY `xác nhận` không có token thứ hai ở vị trí khác.
- Sửa: dời kiểm quyền xuống lớp dùng chung mà mọi đường ghi đều phải qua; tool của agent gọi lớp dịch vụ đó.
- Gợi ý AC: Given vai X không được đổi Y When đổi Y qua form, sao chép, nhập file, hàng loạt hay tool Then KHÔNG đổi
  (một AC kể đủ mọi đường ghi).

### EXPOSE — Trả thừa trường
- Dấu hiệu: trả nguyên object lưu trữ (tuần tự hoá mặc định, `SELECT *` rồi trả thẳng); băm mật khẩu, khoá TOTP, token
  khôi phục có trong phản hồi; số dư, giá vốn, lương tới tay vai không được xem; phản hồi của thao tác ghi gửi lại cả
  bản ghi đầy đủ; xuất CSV/Excel bỏ bước che mà màn hình có.
- Nguồn: N1 (người gọi được xem bản ghi đó, nhưng trường kia lẽ ra phải ẩn với họ).
- Nặng khi: bí mật xác thực (băm, khoá TOTP, token) → `cao`; trường nghiệp vụ nhạy cảm → `trung bình`.
- Hạ/bỏ khi: spec cho vai đó xem trường đó; schema đầu ra loại trường trước khi trả — chỉ ra.
- Chứng minh: hàm dựng phản hồi hay file xuất, trường nhạy cảm đi qua được, và vai thấp nhất gọi tới.
- Sửa: schema đầu ra theo vai (danh sách trường cho phép); xuất file dùng chung hàm che với màn hình.
- Gợi ý AC: Given vai nhân viên When xem hoặc xuất danh sách khách Then dữ liệu trả về KHÔNG có giá vốn, băm mật khẩu.

### STATE — Bất biến nghiệp vụ bị phá
- Dấu hiệu: kỳ hay hoá đơn đã chốt vẫn đổi qua khôi phục, nhập lại, tính lại; webhook thanh toán không nhớ mã sự kiện
  đã xử lý (gửi lại là cộng lần nữa); đổi trạng thái không kiểm trạng thái nguồn (gán thẳng từ body, huỷ đơn đã giao);
  số liệu lệch vì tham số do người kém tin chọn (JOIN nhân dòng theo bộ lọc client gửi).
- Nguồn: N1 (yêu cầu gọi lần lượt, webhook gửi lại).
- Nặng khi: tiền trong bản ghi đã chốt, số liệu kế toán/thuế, tồn kho đã khoá sổ.
- Hạ/bỏ khi: sai số tính toán không ai ngoài điều khiển được — đó là bug, không phải phát hiện bảo mật; ràng buộc duy
  nhất ở DB chặn lần xử lý thứ hai — chỉ ra.
- Chứng minh: bất biến (AC hoặc Entity), chuỗi gọi lần lượt phá nó, và chỗ thiếu điều kiện nguồn.
- Sửa: điều kiện trạng thái nguồn ngay trong câu ghi; bản ghi đã chốt chỉ đọc ở lớp dùng chung; lưu mã sự kiện
  webhook với ràng buộc duy nhất.
- Gợi ý AC: Given kỳ đã chốt When khôi phục, nhập lại hoặc tính lại Then số liệu của kỳ đó KHÔNG đổi.

### AGENCY — Agent quá quyền
- Dấu hiệu: cờ "đã xác nhận" là tham số của tool do model điền; tool ghi tiền, đổi quyền, gửi ra ngoài chạy ngay mà
  không có xác nhận ngoài luồng (người dùng bấm trên giao diện, ngoài cuộc chat); tool gắn nhãn chỉ đọc nhưng có ghi;
  tool đã gỡ khỏi danh sách vẫn gọi được ở bộ điều phối; token của agent đọc được bí mật trong khi có tool viết chữ tự
  do ra ngoài.
- Nguồn: N1 (prompt, nội dung đưa vào agent); đầu ra model coi như N1.
- Nặng khi: tiền, chốt kỳ, đổi quyền, gửi dữ liệu ra ngoài mà không có xác nhận ngoài luồng → `nghiêm trọng`.
- Hạ/bỏ khi: xác nhận đi qua kênh model không giả được (nút trên giao diện, chữ ký phía máy chủ); tool chỉ đọc dữ liệu
  của chính người đang dùng.
- Chứng minh: tool, quyền thực của nó, và chỗ xác nhận lẽ ra phải nằm ngoài tầm với của model.
- Sửa: xác nhận ngoài luồng cho tool nguy hiểm; máy chủ kiểm danh sách tool mỗi lần gọi; token của agent chỉ vừa đủ
  cho việc.
- Gợi ý AC: Given agent đề xuất chuyển tiền When người dùng chưa bấm xác nhận trên giao diện Then KHÔNG chuyển, kể cả
  khi tham số tool ghi là đã xác nhận.

### LOG — Dữ liệu nhạy cảm vào log
- Dấu hiệu: middleware ghi nguyên body/header của mọi yêu cầu; mật khẩu, token, OTP, số thẻ trong lời gọi log; lỗi
  của dịch vụ gửi mail/SMS ghi kèm người nhận; chuỗi người dùng có ký tự xuống dòng ghi thẳng (giả được dòng log);
  nhật ký kiểm toán lấy mã client gửi làm khoá. Bí mật viết cứng trong lời gọi log → `SECRET`.
- Nguồn: N1 (body, header); người nhận không đáng là ai đọc được log (vận hành, dịch vụ log bên ngoài).
- Nặng khi: mật khẩu, token còn hạn → `cao`; dữ liệu cá nhân → `trung bình`.
- Hạ/bỏ khi: bộ lọc che trường chạy trước khi ghi (cấu hình thấy được trong repo); log chỉ bật ở môi trường dev.
- Chứng minh: lời gọi log và đường dữ liệu nhạy cảm tới được đó.
- Sửa: chỉ ghi trường trong danh sách cho phép; che trước khi ghi; bỏ ký tự xuống dòng; khoá kiểm toán do máy chủ sinh.
- Gợi ý AC: Given yêu cầu đăng nhập When hệ thống ghi log Then log KHÔNG chứa mật khẩu hay token.

### RESOURCE — Một yêu cầu không cần đăng nhập làm cạn tài nguyên
- Dấu hiệu: đọc hết body không giới hạn cỡ; giải nén không giới hạn tổng cỡ hay số mục; `limit`/`page_size` lấy từ
  query không có chặn trên; regex có lượng từ lồng nhau chạy trên đầu vào; route công khai trả mọi dòng của bảng.
- Nguồn: N1 trên đường **không cần đăng nhập**.
- Nặng khi: một yêu cầu nhỏ gây chi phí lớn hơn nhiều bậc (vài KB gửi lên → hàng GB bộ nhớ hay hàng phút CPU).
- Hạ/bỏ khi: cần đăng nhập → không phải phát hiện; giới hạn ở tầng trước thấy được trong repo; chi phí cố định theo
  thiết kế, không tăng theo cỡ đầu vào (vd băm mật khẩu ở mức khuyến nghị khi đăng nhập) → không phải phát hiện; vấn
  đề là số lần thử (`RATE-LIMIT`) hay loại file (`FILE-UPLOAD`).
- Chứng minh: đầu vào cụ thể và bậc chi phí nó gây ra (vd body 1 GB bị đọc trọn vào bộ nhớ).
- Sửa: giới hạn cỡ body, cỡ giải nén, chặn trên cho `limit`; viết lại regex không lồng lượng từ.
- Gợi ý AC: Given khách chưa đăng nhập When gửi body lớn hơn N MB Then nhận 413 và máy chủ không đọc hết body.
