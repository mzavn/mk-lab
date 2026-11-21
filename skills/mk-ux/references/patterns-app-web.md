# Mẫu chuẩn cho `app-web` (quản trị, PWA, dashboard)

Bốn mẫu: `data-table` (kèm thanh trang `pager`), `toolbar`, `overlay`, `mobile-header`. Mỗi mẫu có 6 phần cố định và một dòng "Kiểm trước khi giao". Mã đo và ngưỡng nằm ở `references/standards.md`; tên nguyên lý `NL-n` ở `references/principles.md`; mẫu `form` và `lesson-video` ở `references/patterns-web.md`.

Cách đọc phần "Kiểm bằng": mã đo chỉ chạy khi trang có đánh dấu `data-ux` đúng tên. Không đánh dấu thì `scripts/ux.py score` ghi `CHƯA KIỂM`, không phải đạt. Phần không có mã là "kiểm tay" và báo cáo phải ghi đúng chữ đó.

Ví dụ trong file dùng dữ liệu giả: trang quản trị đơn hàng của chị Lan bán bánh mì.

## Mẫu `data-table`

Dùng khi: danh sách có thể dài hơn một màn (đơn hàng, học viên, giao dịch). Chủ sản phẩm nói gọn: "data table mặc định phải có search, phân trang, xem bao nhiêu 1 trang".

**Bắt buộc có**
- Ô tìm ngay trên bảng, gõ là lọc; nhãn hoặc kính lúp, không câu hướng dẫn dài trong ô (Krug, tr. 76).
- Sắp xếp theo cột: bấm tiêu đề cột để đổi chiều; cột đang sắp có mũi tên chỉ chiều, cột khác không.
- Phân trang kèm ô chọn số dòng mỗi trang: 5 · 10 · 20 · 50 · 100.
- Dòng tóm tắt dạng `Hiển thị 11–20 / 57` để người dùng biết mình đang ở đâu trong tổng.
- Đổi ô tìm, bộ lọc hoặc số dòng mỗi trang thì về trang 1 (tránh trang 4 rỗng vì kết quả chỉ còn 2 trang).
- Ngày, số tiền, trạng thái không xuống dòng (`white-space: nowrap`); cột số căn phải để so được hàng đơn vị.
- Chỉ hiện control đã chạy thật. Nút tìm, sắp xếp, phân trang bấm không có tác dụng thì ẩn tới khi làm xong.
- Đánh dấu: khối bảng `data-ux="data-table"`; bên trong có `data-ux="search"`, `data-ux="pager"`, `data-ux="page-size"`, `data-ux="range"`.

```html
<section data-ux="data-table">
  <label>Tìm đơn <input data-ux="search" type="search"></label>
  <div class="table-scroll"><table>…</table></div>
  <nav data-ux="pager" aria-label="Phân trang">
    <select data-ux="page-size" aria-label="Số dòng mỗi trang">…</select>
    <span data-ux="range" data-text="caption">11–20 / 57</span>
    <button aria-label="Trang trước">‹</button><span>2/6</span><button aria-label="Trang sau">›</button>
  </nav>
</section>
```

**Màn nhỏ** (< 768px)
- Thanh trang một hàng ở 320px. Cách làm: bỏ chữ "Hiện", đổi "Trang 2 / 6" thành `2/6`, bỏ đuôi tên đối tượng ("57 đơn" → "57"); từ khổ rộng hơn trả lại chữ đầy đủ. Chủ sản phẩm nói: "bóp chữ nhỏ để trên 1 hàng".
- Chữ phụ (dòng tóm tắt, số trang) được nhỏ tới sàn `text-min` khi đánh `data-text="caption"`; chữ trong ô bảng vẫn theo `body-text-mobile`.
- Nút mũi tên giữ vùng chạm theo `tap-target`. Chỉ hạ xuống 40px khi `DESIGN.md` mục `## Luật đo` ghi rõ `tap-target` 40×40.
- Cột phụ (mã nội bộ, ngày tạo) ẩn, hoặc gộp thành một dòng phụ nhỏ dưới tên ở cột đầu. Không giữ đủ 8 cột rồi bắt cuộn ngang cả trang.
- Bảng rộng chỉ cuộn ngang trong khung riêng bọc bảng (`overflow-x: auto` trên khung đó), trang không tràn (`overflow-x` = 0). Cột tên dính trái thì đặt lớp thấp hơn tiêu đề trang dính, để khi cuộn không đè lên nhau.

**Trạng thái**
| Trạng thái | Người dùng thấy |
|---|---|
| Đang tải | Khung xương đúng số dòng đang chọn; thanh trang giữ chỗ, bố cục không nhảy |
| Rỗng do lọc | "Không có đơn khớp 'bánh mì chả'" + nút "Xoá bộ lọc" |
| Rỗng thật (chưa có dữ liệu) | Một câu nói vì sao rỗng + lối tiếp ("Tạo đơn đầu tiên" hoặc link hướng dẫn) |
| Lỗi tải | "Chưa tải được danh sách" + nút "Tải lại"; không hiện bảng rỗng giả như thể không có dữ liệu |
| Một trang | Vẫn hiện dòng tóm tắt; mũi tên khoá kèm nhãn đọc được |
| Dữ liệu khó | Tên 60 ký tự, số tiền 9 chữ số, ngày đủ giờ phút: không vỡ hàng, không đè cột |

**Hỏi chủ sản phẩm**
- Mặc định bao nhiêu dòng mỗi trang và có nhớ lựa chọn giữa các lần mở không (khuyến nghị: 10 trên điện thoại, 20 trên máy tính; nhớ trong trình duyệt).
- Cột nào được ẩn trên điện thoại; cột nào luôn thấy vì người dùng dựa vào nó để quyết định (khuyến nghị: giữ tên + một cột trạng thái, cột còn lại gộp thành dòng phụ).
- Tìm có bỏ dấu không ("nguyen" ra "Nguyễn") (khuyến nghị: có).
- Có xuất file không, ai được xuất (dữ liệu cá nhân của khách) (khuyến nghị: chưa có lý do thì không làm; có thì chỉ vai quản trị).
- Người dùng trả lời "cứ làm" → dùng khuyến nghị, ghi "giả định" trong `ux-needs.md`.

**Phẩm chất / nguyên lý**
- Hợp lý, dễ dùng, tiện, gọn.
- NL-1 (thấy được có tìm, có trang tiếp), NL-2 (dòng tóm tắt báo vị trí, khung xương khi chờ), NL-8 (cột căn đều, lướt được), NL-11 (một hàng, gộp cột phụ), NL-12 (cùng một thanh trang cho mọi bảng), NL-7 (rỗng và lỗi có lối tiếp).

**Kiểm bằng**
- `pattern-data-table`: khối `data-table` thiếu `search`, `pager`, `page-size` hoặc `range` là trượt.
- `one-row` trên `pager`: các con trực tiếp lệch đỉnh quá ngưỡng là trượt.
- `overflow-x`, `tap-target`, `text-min`, `body-text-mobile`.
- Kiểm tay: sắp xếp đúng chiều, về trang 1 khi đổi lọc, ngày/tiền không xuống dòng, rỗng có lối tiếp, dữ liệu dài nhất.

Kiểm trước khi giao: ở 320px với dữ liệu dài nhất, thanh trang một hàng, trang không cuộn ngang, đổi lọc ở trang 3 thì về trang 1, và lọc ra rỗng có nút "Xoá bộ lọc".

## Mẫu `toolbar`

Dùng khi: hàng điều khiển trên một danh sách hoặc màn làm việc (tìm, lọc, thêm mới, quay lại).

**Bắt buộc có**
- Một hàng ở 320px. Ô tìm giãn lấp chỗ trống, các nút còn lại co theo nội dung.
- Nút chỉ có biểu tượng phải có `aria-label` bằng chữ người dùng (ví dụ "Thêm đơn", "Về danh sách"); thêm `title` để rê chuột cũng đọc được.
- Bộ lọc phụ gom vào một nút "Lọc" mở danh sách thả xuống; nút ghi số lọc đang bật, ví dụ "Lọc (2)".
- Tối đa một nút chính trong hàng (thường là "Thêm mới"); nút khác ở dạng phụ.
- Nút quay lại dạng biểu tượng nằm chung hàng với ô tìm, không chiếm riêng một hàng.
- Đánh dấu: `data-ux="toolbar"` trên khối hàng.

**Màn nhỏ**
- Không dùng `flex-wrap` cho hàng này; thiếu chỗ thì rút chữ thành biểu tượng kèm `aria-label`, hoặc gom thêm vào "Lọc".
- Không giấu control quan trọng sau thanh cuộn ngang mà không có dấu hiệu còn nữa.
- Vùng chạm mỗi nút theo `tap-target`.

**Trạng thái**
| Trạng thái | Người dùng thấy |
|---|---|
| Có lọc đang bật | Số trên nút "Lọc" + một lối "Xoá lọc" |
| Đang tìm | Danh sách bên dưới báo đang tải; ô tìm giữ chữ đã gõ |
| Nút không dùng được (thiếu quyền) | Ẩn, hoặc khoá kèm lý do khi rê/chạm; không bấm rồi mới báo lỗi |

**Hỏi chủ sản phẩm**
- Bộ lọc nào hay dùng tới mức được đứng ngoài, không gom vào "Lọc" (khuyến nghị: tối đa một).

**Phẩm chất / nguyên lý**
- Gọn, tiện, dễ dùng.
- NL-11 (một hàng), NL-4 (biểu tượng có nhãn đọc được), NL-12 (cùng vị trí trên mọi danh sách), NL-14 (`aria-label` cho trình đọc màn hình).

**Kiểm bằng**
- `one-row` trên `toolbar`; `tap-target`; `overflow-x`; `primary-cta`.
- Kiểm tay: mọi nút biểu tượng có `aria-label` đúng nghĩa; số trên "Lọc" khớp số lọc đang bật.

Kiểm trước khi giao: ở 320px hàng không xuống dòng, đọc to bằng trình đọc màn hình thì từng nút có tên.

## Mẫu `overlay`

Dùng khi: cần làm một việc phụ mà không rời màn (sửa đơn, xem chi tiết, xác nhận xoá).

**Bắt buộc có**
- Chọn đúng loại. Tấm trượt (sheet) cho form nhiều ô hoặc nội dung đọc dài. Hộp thoại giữa màn (dialog) chỉ cho xác nhận ngắn: một câu, hai nút.
- Đầu (tiêu đề + nút đóng) và hàng nút hành động luôn thấy; chỉ thân ở giữa cuộn. Thân cao hơn màn vẫn cuộn tới dòng cuối.
- Câu xác nhận nêu cả hành động và đối tượng: "Xoá đơn #1024 của chị Lan?", nút "Xoá đơn", không chỉ "OK" (Norman, tr. 203–204).
- Mở ra thì con trỏ bàn phím vào trong; Tab không chạy ra ngoài; Esc đóng; đóng xong con trỏ về nút đã mở nó.
- Một mẫu sheet và một mẫu dialog dùng chung cho cả sản phẩm, không mỗi màn một kiểu.
- Đánh dấu: `data-ux="overlay"`; phần đầu `data-ux="overlay-head"`; hàng nút `data-ux="overlay-actions"`.

**Màn nhỏ**
- Rộng hết màn; hàng nút chừa vùng an toàn đáy (`env(safe-area-inset-bottom)`) để không nằm dưới thanh home.
- Trang phía sau khoá cuộn; cuộn trong thân không kéo trang sau chạy theo.
- Thử ở khung thấp (390×844 và thấp hơn): nút cuối vẫn bấm được.

**Trạng thái**
| Trạng thái | Người dùng thấy |
|---|---|
| Đang lưu | Nút chính đổi chữ "Đang lưu…" và khoá, chống bấm hai lần |
| Lỗi lưu | Lỗi trong overlay, dữ liệu đã nhập còn nguyên |
| Đóng khi đang nhập dở | Hỏi "Bỏ thay đổi?" hoặc giữ bản nháp; không mất chữ im lặng |
| Lưu xong | Overlay đóng, màn sau báo kết quả ngay chỗ vừa đổi |

**Hỏi chủ sản phẩm**
- Thao tác không đảo ngược được (xoá vĩnh viễn, hoàn tiền) có cần bước xác nhận mạnh hơn không, hay cho hoàn tác trong vài giây (khuyến nghị: hoàn tác nếu làm được).

**Phẩm chất / nguyên lý**
- Hợp lý, dễ dùng, tiện.
- NL-6 (khoá trang sau, giữ Tab trong overlay), NL-7 (xác nhận nêu đối tượng, giữ dữ liệu khi lỗi), NL-2 (đang lưu, lưu xong), NL-12 (một mẫu dùng chung), NL-14 (bàn phím, Esc, trả con trỏ).

**Kiểm bằng**
- `pattern-overlay`: thiếu `overlay-head` hoặc `overlay-actions` là trượt.
- `tap-target` (nút đóng hay bị làm 28px), `overflow-x`, `primary-cta` (một nút chính trong overlay).
- Kiểm tay: đo khi overlay đang mở; cuộn thân tới cuối ở khung thấp; Tab, Esc, trả con trỏ; vùng an toàn trên máy thật.

Kiểm trước khi giao: mở overlay dài nhất ở 390×844, cuộn tới cuối, nút chính vẫn thấy và bấm được; Esc đóng và con trỏ về chỗ cũ.

## Mẫu `mobile-header`

Dùng khi: thanh đầu trang trên điện thoại (nút menu hoặc quay lại, tên màn hoặc tên người dùng, một hành động).

**Bắt buộc có**
- Một hàng. Thứ tự quen thuộc: quay lại hoặc menu bên trái, tên ở giữa hoặc ngay sau, tối đa một hành động bên phải.
- Chữ dài (email, tên lớp, tên khách) một dòng, cắt bằng dấu ba chấm, chữ đầy đủ trong `title`. Ví dụ `lan.nguyen+test@exa…`.
- Nút quay lại ghi rõ về đâu qua `aria-label` ("Về danh sách đơn").
- Chiều cao không đổi giữa các màn; phần dính nằm ngoài khung tự cuộn để không trôi trên iOS.
- Đánh dấu: `data-ux="mobile-header"`.

**Màn nhỏ**
- Chính là phạm vi của mẫu: kiểm ở 320px và 390px. Chữ phụ (email dưới tên) được nhỏ tới sàn `text-min` với `data-text="caption"`, không được xuống hai dòng.
- Không nhồi thêm nút; hành động thứ hai vào menu.

**Trạng thái**
| Trạng thái | Người dùng thấy |
|---|---|
| Chưa đăng nhập | Nút "Đăng nhập" thay chỗ tên |
| Tên quá dài | Ba chấm, chạm giữ hoặc rê thấy đủ |
| Đang ở màn sâu | Nút quay lại thay nút menu, tên màn hiện tại hiện rõ |

**Hỏi chủ sản phẩm**
- Thông tin cá nhân nào được hiện trên thanh đầu (email, mã học viên) khi người khác có thể nhìn màn hình (khuyến nghị: tên, ẩn email sau một chạm).

**Phẩm chất / nguyên lý**
- Gọn, hợp lý, hợp gu.
- NL-11 (một hàng), NL-1 (biết đang ở màn nào), NL-12 (vị trí quen thuộc), NL-14 (`aria-label` cho nút biểu tượng).

**Kiểm bằng**
- `one-row` trên `mobile-header`; `tap-target`; `overflow-x`; `text-min`.
- Kiểm tay: email dài nhất cắt đúng, `title` có chữ đầy đủ; thanh không trôi khi cuộn trên máy thật.

Kiểm trước khi giao: ở 320px với email 40 ký tự, thanh đầu vẫn một hàng và không đẩy nút nào xuống.
