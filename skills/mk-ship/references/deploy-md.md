# `DEPLOY.md` — hợp đồng triển khai ở gốc repo

`DEPLOY.md` nói **cách** đưa repo lên từng môi trường: nền tảng, nhánh, lệnh, URL, đường dẫn cần kiểm, bí mật cần có,
cách quay lui. `ship.py check` và `ship.py smoke` đọc file này; agent chỉ chạy lệnh ghi ở đây. Nằm ở gốc repo như
`DESIGN.md`; sửa nó (cách triển khai, không phải hành vi sản phẩm) không cần thư mục change của mk-specs — nhưng
**không sửa để qua cổng** (SKILL.md cổng cứng 2).

## §1. Dò nền tảng (mode `tạo`)

Xét theo thứ tự, dừng ở dấu hiệu đầu tiên. Đọc tên file và vài khoá; không chạy gì.

| Thứ tự | Dấu hiệu | `- Nền tảng:` |
|---|---|---|
| 1 | `wrangler.json`, `wrangler.jsonc`, `wrangler.toml` có `pages_build_output_dir` | `cloudflare-pages` |
| 2 | `wrangler.json`, `wrangler.jsonc`, `wrangler.toml` (còn lại) | `cloudflare-workers` |
| 3 | `vercel.json` | `khác (vercel)` |
| 4 | `netlify.toml` | `khác (netlify)` |
| 5 | `fly.toml` | `khác (fly)` |
| 6 | `Dockerfile` | `khác (docker)` — hỏi chạy ở đâu (Fly, Railway, máy chủ riêng…) rồi ghi tên đó |
| 7 | không thấy gì | đưa lựa chọn (bên dưới) |

Không thấy gì → hỏi một câu, Workers đứng đầu:

1. **Cloudflare Workers (khuyên dùng)** — một Worker phục vụ cả API lẫn trang tĩnh (`assets.directory`), có môi
   trường, bí mật, quay lui bằng CLI; gói miễn phí đủ cho dự án nhỏ.
2. Cloudflare Pages — chỉ khi dự án đã dùng Pages; dự án mới nên dùng Workers + static assets.
3. Nền tảng khác người dùng đang dùng (Vercel, Netlify, Fly…) — `khác (<tên>)`, lệnh và cách quay lui do người dùng
   cung cấp.

Monorepo: dò trong từng thư mục ứng dụng (`apps/*`, `packages/*`); mỗi Worker một dòng môi trường (§3).

## §2. Định dạng mà `ship.py` đọc

```markdown
# Triển khai <tên dự án>
- Nền tảng: cloudflare-workers
- Cấu hình: wrangler.jsonc

## Môi trường
| Môi trường | Nhánh | Lệnh triển khai | URL |
|---|---|---|---|
| staging | * | `npx --no wrangler deploy --env staging` | https://dat-mon-staging.example.workers.dev |
| production | main | `npx --no wrangler deploy --env production` | https://dat-mon.example.com |

## Kiểm sau triển khai
| Đường dẫn | Mã | Có chữ |
|---|---|---|
| / | 200 | Đặt món |
| /api/health | 200 | — |
```

| Phần | Luật |
|---|---|
| `- Nền tảng:` | đúng một trong `cloudflare-workers`, `cloudflare-pages`, `khác (<tên>)`; thiếu hoặc khác → `CHẶN` |
| `- Cấu hình:` | tuỳ chọn; đường dẫn file wrangler từ gốc repo. Lệnh có `-c/--config` thì cờ đó thắng |
| Bảng | ô bỏ dấu backtick; gạch đứng trong ô viết `\|`; tìm cột theo tên tiêu đề |
| `Môi trường` | tên khớp `[A-Za-z0-9_-]+`, là giá trị của `--env` khi gọi `ship.py`. **Production** = `production`, `prod` hoặc đuôi `-production`/`-prod` (không phân biệt hoa thường); còn lại là môi trường thử. Không có dòng production nào → `CẢNH BÁO` |
| `Nhánh` | tên nhánh phải đang đứng (HEAD tách rời phải trùng đầu `refs/heads/<nhánh>` hoặc `refs/remotes/<remote>/<nhánh>`); `*` = nhánh nào cũng được; trống → `CHẶN` |
| `Lệnh triển khai` | một lệnh, ưu tiên `<wrangler> deploy …` (SKILL.md cổng cứng 6). Không đặt bí mật trong lệnh (`TOKEN=…`, `--var KEY:…`) — `check` chặn và không in lệnh |
| `URL` | gốc `http://` hoặc `https://`, không có `user:mật-khẩu@`; `smoke` ghép đường dẫn vào sau |
| `Đường dẫn` | bắt đầu bằng `/`; nên có ít nhất trang chủ và một đường API nhẹ |
| `Mã` | một số 100–599; mã 3xx → không theo chuyển hướng, so thẳng |
| `Có chữ` | chữ phải có trong trang (so sau chuẩn hoá NFC), viết không kèm dấu nháy; trống hoặc `—` = không kiểm chữ |

Các mục chữ tự do (agent đọc, `ship.py` không đọc):

- `## Bí mật cần có` — mỗi dòng một **tên** bí mật (không bao giờ giá trị). Workers: chỉ dùng khi cấu hình chưa có
  `secrets.required` cho môi trường đó.
- `## Trước khi triển khai` — bước riêng của dự án (build, migration). Lệnh lạ → hỏi trước lần chạy đầu trong phiên.
- `## Quay lui` — cách quay lui khi không dùng được `wrangler rollback` (Pages, nền tảng khác, lần triển khai đầu),
  và điều cần làm với dữ liệu.

## §3. Nhiều Worker, monorepo

Mỗi Worker một dòng môi trường, tên mang tiền tố ứng dụng, lệnh mang `-c` hoặc `--cwd`:

| Môi trường | Nhánh | Lệnh triển khai | URL |
|---|---|---|---|
| api-staging | * | `pnpm exec wrangler deploy -c apps/api/wrangler.jsonc --env staging` | https://api-staging.example.workers.dev |
| api-production | main | `pnpm exec wrangler deploy -c apps/api/wrangler.jsonc --env production` | https://api.example.com |
| web-production | main | `pnpm exec wrangler deploy --cwd apps/web --env production` | https://example.com |

`check` tìm cấu hình như wrangler: `-c/--config` (tính từ `--cwd` nếu có) → `- Cấu hình:` → trong thư mục `--cwd`
(mặc định gốc repo) theo thứ tự `wrangler.json` → `wrangler.jsonc` → `wrangler.toml`. Bảng `## Kiểm sau triển khai`
dùng chung; Worker cần đường dẫn riêng → chạy `smoke` với `--url` hoặc tách dự án.

## §4. Nền tảng khác

`check` vẫn kiểm `DEPLOY.md`, git, spec, bảo mật, file bí mật và lệnh; bỏ phần cấu hình Workers. Lệnh triển khai
không phải `<wrangler> deploy …` → luôn hiện nguyên văn và hỏi trước lần chạy đầu trong phiên.

| Nền tảng | Lệnh thường gặp (CLI cài trong dự án) | `## Quay lui` nên ghi |
|---|---|---|
| `khác (vercel)` | `npx --no vercel deploy --prod` | `npx --no vercel rollback <url bản trước>` hoặc "Promote" trên dashboard |
| `khác (netlify)` | `npx --no netlify deploy --prod` | dashboard → Deploys → "Publish deploy" bản trước |
| `khác (fly)` | `fly deploy` | `fly releases` → `fly deploy --image <ảnh bản trước>` |
| `khác (docker)` | lệnh của người dùng | cách chạy lại ảnh bản trước, do người dùng ghi |

Đăng nhập CLI các nền tảng này cũng theo cổng cứng 3: người dùng tự đăng nhập, agent không cầm token.

## §5. Khi `check` chặn vì `DEPLOY.md`

| Dòng `CHẶN:` | Ai làm gì |
|---|---|
| `chưa có DEPLOY.md` | mode `tạo` cùng người dùng, commit |
| `DEPLOY.md không có môi trường <tên>` | người dùng chọn: thêm dòng (cần nhánh, lệnh, URL) hay dùng môi trường có sẵn |
| `DEPLOY.md thiếu nhánh của <tên>` | người dùng ghi nhánh (hoặc `*`) |
| `đang ở nhánh …, môi trường … cần nhánh …` | chuyển nhánh / hợp nhất qua quy trình của repo; không sửa ô Nhánh để qua |
| `bí mật trong lệnh triển khai của …` | chuyển giá trị sang biến môi trường của máy/CI; nếu bí mật đã commit thì thu hồi/đổi khoá là việc của chủ dự án |

Mọi thay đổi `DEPLOY.md` phải commit trước khi chạy `check` lại (cây sạch là điều kiện của cổng).
