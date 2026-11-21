# specs/ — Đặc tả Sổ Việc

Sổ Việc là dịch vụ cho nhiều công ty nhỏ cùng dùng: mỗi công ty quản lý dự án, lập hoá đơn cho khách, chốt kỳ kế toán
và có một trợ lý gọi tool thay người dùng.

Quy trình: skill `mk-specs`, cấu hình `specs/mk-specs.yml`.

| Thư mục | Vai trò |
|---|---|
| `specs/` | Hành vi đã chốt — BR, UC, Entity, AC |
| `specs/changes/` | Đề xuất đang bàn |

## Context

| Context | Use case |
|---|---|
| `hoa-don` — Hoá đơn | UC-201 Hoá đơn và kỳ kế toán |
| `du-an` — Dự án | UC-202 Dự án và ngân sách |
| `cong-ty` — Công ty và thành viên | UC-203 Thành viên và phiên đăng nhập |
| `tro-ly` — Trợ lý | UC-204 Trợ lý gọi tool |

Business requirement: `business-requirements.md` (BR-01). Entity: `entities.md`.
