# Cloudflare Workers (và Pages) cho mk-ship

Kiểm với wrangler 4.140.0 và tài liệu Cloudflare (2026-10-27). `<wrangler>` = bản cài trong dự án (SKILL.md). Mọi ví
dụ là dữ liệu giả.

## §1. `wrangler.jsonc` mẫu (mode `tạo`)

Cloudflare khuyên `wrangler.jsonc` cho dự án mới. Worker có API + trang tĩnh, hai môi trường:

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "dat-mon",
  "main": "src/index.ts",                // trang tĩnh thuần: bỏ "main", giữ "assets"
  "compatibility_date": "2026-10-27",    // = date -u +%F lúc tạo (ngày UTC)
  "observability": { "enabled": true },
  "assets": { "directory": "./public" },
  "env": {
    "staging": {
      "vars": { "APP_ENV": "staging", "API_URL": "https://dat-mon-staging.example.workers.dev" },
      "secrets": { "required": ["JWT_SECRET"] },
      "d1_databases": [{ "binding": "DB", "database_name": "dat-mon-staging", "database_id": "<mã sau khi tạo>" }]
    },
    "production": {
      "routes": [{ "pattern": "dat-mon.example.com/*", "zone_name": "example.com" }],
      "vars": { "APP_ENV": "production", "API_URL": "https://dat-mon.example.com" },
      "secrets": { "required": ["JWT_SECRET"] },
      "d1_databases": [{ "binding": "DB", "database_name": "dat-mon", "database_id": "<mã sau khi tạo>" }]
    }
  }
}
```

- `compatibility_date`: lấy bằng `date -u +%F`, không dùng ngày giờ máy — `check` chặn ngày sau hôm nay theo UTC. TOML
  phải viết chuỗi `"2026-10-27"`, không phải ngày trần.
- `routes` / tên miền: chỉ ghi cái người dùng đã có; agent không tạo hay đổi DNS.
- Dự án dùng `@cloudflare/vite-plugin`: cấu hình có thể không có `main` lẫn `assets.directory` (`check` chỉ cảnh báo);
  chọn môi trường bằng tiền tố `CLOUDFLARE_ENV=<tên>` trong lệnh.

`.gitignore` thêm dòng còn thiếu:

```gitignore
.wrangler/
.dev.vars*
.env*
!.env.example
!.dev.vars.example
dist/
```

(`dist/` = thư mục build thật của dự án.) `wrangler deploy --dry-run` tạo `.wrangler/`; thiếu dòng này thì lần `check`
sau báo cây chưa sạch.

## §2. Môi trường là Worker riêng

- `env.<x>` triển khai thành Worker riêng tên `<name>-<x>` (trừ khi `env.<x>.name` đặt khác).
- **Không thừa kế:** `vars`, binding (KV, D1, R2, Queues, Durable Objects…), `secrets`. Phải khai riêng cho từng
  `env.<x>`.
- **Thừa kế được (cần chú ý):** `routes`, `route`, `workers_dev` là khoá thừa kế — **không bao giờ đặt routes/tên miền
  ở gốc** khi cấu hình có `env.*`; khai riêng trong từng `env.<x>` để tránh staging vô tình nhận route của production.
  Các khoá thừa kế khác: `name`, `main`, `compatibility_date`, `assets`, `observability`…
- Chọn môi trường: `--env x`, `--env=x`, `-e x`, `-e=x`, hoặc tiền tố `CLOUDFLARE_ENV=x`. Mọi lệnh cho môi trường đó
  (`secret`, `d1 migrations`, `deployments`, `rollback`, `dry-run`) phải mang **cùng** cờ `--env`/`-c`/`--cwd` hoặc
  tiền tố `CLOUDFLARE_ENV=x` với lệnh triển khai trong `DEPLOY.md` — thiếu là thao tác lên Worker gốc, không phải
  `<name>-<x>`.

## §3. Bí mật

- Giá trị bí mật chỉ đi qua `<wrangler> secret put <TÊN> [--env x]` — **người dùng tự chạy và tự gõ giá trị**. Lệnh
  này tạo và triển khai ngay một phiên bản mới của Worker (production: hỏi như bước xác nhận trước khi họ chạy).
- **Lần triển khai đầu tiên khi có `secrets.required`** (Worker chưa từng tồn tại trên Cloudflare): wrangler từ chối
  `deploy` ("Worker does not exist yet … supply them via `--secrets-file`"), nhưng chạy `secret put` lên Worker chưa có
  thì wrangler lại tự tạo và xuất bản ngay một Worker nháp rỗng (`export default { fetch() {} }`, tự đồng ý khi không
  có TTY). Do đó: **không chạy `secret put` trước lần triển khai đầu**; nhờ người dùng tự chạy
  `<wrangler> deploy [--env x] --secrets-file <file-của-họ>` (file nằm ngoài git / đã ignore; agent KHÔNG đọc file này),
  hoặc chỉ deploy lần đầu không có `secrets.required` khi người dùng chủ động chọn vậy.
- `<wrangler> secret list [--env x]` chỉ in tên (mặc định JSON). Worker chưa từng triển khai → lệnh lỗi: mọi tên đều
  coi là thiếu; Worker sẽ chưa chạy đúng cho tới khi có bí mật.
- `secrets.required` (theo từng `env`) là nguồn tên bí mật cần có; `wrangler deploy` dừng khi thiếu tên trong danh
  sách. `## Bí mật cần có` trong `DEPLOY.md` chỉ dùng khi cấu hình chưa có `secrets.required`.
- Phát triển cục bộ: `.dev.vars`, `.dev.vars.<env>`, `.env`, `.env.<env>`, `.env.<env>.local` — không commit (bản
  `.example`, `.sample`, `.template`, `.dist` thì được). Agent không đọc giá trị trong các file này.
- `vars` là giá trị công khai (in trong dashboard, nằm trong git). Khoá tên trông như bí mật (`*_SECRET`, `*_TOKEN`,
  `*_PASSWORD`, `*_KEY` trừ `PUBLIC_KEY`/`SITE_KEY`/`PUBLISHABLE_KEY`, `apiKey`…) hoặc URL có mật khẩu → `check` chặn.

## §4. D1, KV, R2 và việc tự tạo tài nguyên

- Binding thiếu mã (`kv_namespaces[].id`, `d1_databases[].database_id`, `r2_buckets[].bucket_name`) → wrangler hiện nay
  **tự tạo** tài nguyên khi deploy và ghi mã vào file cấu hình (cây bẩn sau deploy, tài nguyên người dùng chưa duyệt).
  `check` cảnh báo. Cách làm: hỏi người dùng → tạo trước (`<wrangler> d1 create <tên>`, `<wrangler> kv namespace
  create <tên>`, `<wrangler> r2 bucket create <tên>`) → ghi mã vào cấu hình → commit → `check` lại. R2 và gói trả phí
  cần người dùng đồng ý rõ.
- D1 migration:
  - Xem: `<wrangler> d1 migrations list <db> --remote [--env x]` — `--env` chọn database của môi trường đó.
  - Áp: `<wrangler> d1 migrations apply <db> --remote [--env x]` — chỉ khi người dùng đồng ý, trước lệnh triển khai.
    Không có TTY thì lệnh không hỏi lại (có tạo bản sao lưu), nên đồng ý trong chat là cổng duy nhất.
  - Migration chạy khi code cũ còn phục vụ → phải tương thích ngược (thêm cột/bảng trước, bỏ sau ở lần sau).
  - Quay lui Worker không quay lui dữ liệu. Khôi phục D1 là Time Travel (`d1 time-travel restore`) — ngoài phạm vi
    agent, người dùng tự làm.
  - Không chạy `d1 execute … --remote` (SQL tuỳ ý lên dữ liệu thật).

## §5. `wrangler deploy --dry-run`

- Biên dịch và kiểm cấu hình, **không tải lên**, không cần đăng nhập. Chạy với đúng cờ `--env`/`-c`/`--cwd` của môi
  trường.
- Không kiểm: bí mật, tài nguyên từ xa, `compatibility_date` trong tương lai (`check` lo phần này).
- Chạy `build.command` của cấu hình nếu có → lệnh lạ hiện nguyên văn và hỏi trước (SKILL.md cổng cứng 6).
- Tạo `.wrangler/` (cần trong `.gitignore`).

## §6. Ghi phiên bản và quay lui

- **Trước** lệnh triển khai: `<wrangler> deployments status [--env x] [-c file]` → ghi mã phiên bản đang phục vụ. Lỗi
  vì Worker chưa có → "lần triển khai đầu, chưa có phiên bản trước".
- Lệnh triển khai in mã phiên bản mới (`Current Version ID`) — ghi lại để báo người dùng.
- Quay lui (chỉ đề xuất, hỏi trước):
  `[CLOUDFLARE_ENV=x] <wrangler> rollback <mã phiên bản đã ghi> [--env x] [-c file] --message "<lý do>"`.
  Lưu ý: `--message` không bỏ các câu hỏi xác nhận; **khi không có TTY wrangler tự động chọn "yes" cho mọi xác nhận**
  (kể cả cảnh báo "bí mật đã thay đổi kể từ phiên bản đó") — do đó sự đồng ý của người dùng trong chat là cổng duy
  nhất; nếu bí mật đã đổi thì phiên bản quay lui sẽ chạy với bí mật hiện tại.
  Không đưa mã → wrangler chọn bản **tải lên trước bản mới nhất**, có thể là phiên bản do `secret put` hay
  `versions upload` tạo, không phải bản tốt gần nhất.
- Giới hạn: chỉ quay về được 100 phiên bản gần nhất; bị từ chối khi đã đổi lớp Durable Object (tạo/xoá/đổi tên), hoặc
  khi KV/R2/Queue mà bản cũ dùng đã bị xoá. Tài nguyên gắn với Worker (D1, KV, R2) không đổi khi quay lui.
- Lịch sử: `<wrangler> deployments list [--env x]` — Cloudflare đã giữ, không ghi nhật ký triển khai vào repo.

## §7. Bản xem trước không phải môi trường thử

Version URL / preview (`<wrangler> versions upload`) chạy với **tài nguyên production** (cùng D1, KV, R2, bí mật) —
không dùng làm môi trường thử. Môi trường thử là `env.staging` với tài nguyên riêng.

## §8. Cloudflare Pages

- Nhận diện: cấu hình có `pages_build_output_dir`. Lệnh: `<wrangler> pages deploy <thư mục> --project-name <tên>
  [--branch <nhánh>]` — không có `--env`, không có `--dry-run`.
- Bí mật: `<wrangler> pages secret list --project-name <tên>`; đặt bằng `<wrangler> pages secret put` (người dùng chạy).
- Quay lui: không có lệnh CLI — dashboard → Deployments → "Rollback"; ghi các bước vào `## Quay lui` của `DEPLOY.md`.
- Dự án có sẵn thì giữ; gợi ý (không tự làm) chuyển sang Workers + static assets — Cloudflare khuyên vậy cho dự án mới.

## §9. Wrangler cũ hơn

Dự án ghim wrangler riêng. Lệnh báo cờ lạ (vd `whoami --json`, `deployments status`) → dùng dạng cũ (`whoami` rồi đọc
chữ, `deployments list`), **không coi là chưa đăng nhập**. `secrets.required` lạ với bản cũ chỉ là cảnh báo của
wrangler; khi đó so bí mật theo `## Bí mật cần có`. Gợi ý nâng wrangler như một việc riêng, không tự nâng.

## §10. Lệnh theo mức rủi ro

| Mức | Lệnh |
|---|---|
| Chạy được, chỉ đọc | `whoami --json`, `deploy --dry-run`, `deployments status`/`list`, `secret list`, `pages secret list`, `d1 migrations list --remote`, `versions list` |
| Chạy không hỏi (môi trường thử) / hỏi trong lượt (production) | đúng một lệnh `<wrangler> deploy …` / `<wrangler> pages deploy …` trong `DEPLOY.md` (SKILL.md cổng cứng 6) |
| Chỉ khi người dùng đồng ý | `d1 migrations apply --remote`, `d1 create`, `kv namespace create`, `r2 bucket create`, `rollback <mã>`, lệnh khác trong `DEPLOY.md`, `build.command` |
| Người dùng tự chạy | `login`, `secret put`, `pages secret put` |
| Không bao giờ | mọi lệnh con `delete`/`purge`, `d1 execute … --remote`, `d1 time-travel restore`, `versions deploy` chia phần trăm, `auth token`, `deploy --temporary` (trừ khi người dùng yêu cầu), đổi DNS/tên miền |

## §11. CI (chỉ để đọc thêm)

mk-ship không dựng CI/CD. Người dùng tự làm thì CI dùng `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` đặt trong
kho bí mật của CI, chạy cùng `ship.py check` rồi lệnh trong `DEPLOY.md`; token chỉ cấp quyền "Edit Workers" cho đúng
tài khoản.
