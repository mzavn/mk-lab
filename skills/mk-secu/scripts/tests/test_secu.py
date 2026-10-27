"""Tests for mk-secu secu.py. Run: python3 -m unittest discover -s skills/mk-secu/scripts/tests

Secret-looking strings are joined at run time by `cat()` (a call, so the compiler cannot fold them into one constant,
not even in a .pyc); no real-format token is written in this file or its bytecode."""
import os
import shutil
import re
import stat
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SECU = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secu.py")
CATALOG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                       "references", "catalog.md")
CODES = {"IDOR", "AUTHZ", "MASS-ASSIGN", "SESSION", "WEAK-HASH", "RATE-LIMIT", "SQLI", "XSS", "CMDI", "PATH-TRAVERSAL",
         "SSRF", "DESERIAL", "FILE-UPLOAD", "LLM-TOOL", "SECRET", "DEBUG-ERROR", "CORS", "CSRF", "DEP-NAME", "RACE"}


def cat(*parts):
    return "".join(parts)


UC_FILE = """# UC-101: Xem đơn hàng
- Status: active

## Acceptance Criteria

### AC-1: Khách xem đơn của mình
- Given khách có đơn When mở đơn Then thấy đơn
- Tests: `test_orders.py`

### AC-2: Khách không xem được đơn người khác
- Given đơn của khách khác When mở Then KHÔNG thấy
- Tests: `test_orders.py`

### AC-3: Xem đơn không cần đăng nhập (deprecated v2: bỏ, xem AC-2)
- Given khách lạ When mở Then thấy

### AC-4: Báo lỗi deprecated cho mã đơn cũ
- Given mã đơn cũ When mở Then báo mã đã bỏ
"""

FINDING_1 = """### SEC-1: Xem đơn người khác qua mã đơn
- Kết luận: xác nhận
- Mức: cao
- Loại: code sai AC
- Lớp: IDOR
- AC: UC-101 AC-2
- Ai: khách đã đăng nhập
- Đầu vào: mã đơn trên đường dẫn
- Kiểm soát thiếu: so chủ đơn với người gọi
- Ranh giới: giữa hai khách
- Tài sản: đơn hàng, địa chỉ giao
- Hậu quả: đọc địa chỉ giao của khách khác
- Dấu vết:
  - `app/orders.py:12` nhận `order_id` từ đường dẫn
  - `app/db.py:30-34` truy vấn không lọc chủ đơn
- Đề xuất sửa: thêm điều kiện chủ đơn vào truy vấn
"""

FINDING_2 = """### SEC-2: Đăng nhập không giới hạn số lần thử
- Kết luận: xác nhận
- Mức: thấp
- Loại: thiếu AC
- Lớp: RATE-LIMIT
- Proposal: `261027-gioi-han-dang-nhap`
- Ai: người lạ trên mạng
- Đầu vào: cặp email/mật khẩu gửi liên tục
- Kiểm soát thiếu: giới hạn số lần thử
- Ranh giới: từ ngoài vào tài khoản
- Tài sản: tài khoản khách
- Hậu quả: dò được mật khẩu yếu
- Dấu vết: `login.py:8`
- Đề xuất sửa: khoá tạm sau 5 lần sai

Ví dụ yêu cầu (trong khối mã, không bị kiểm chỗ trống):

```http
POST /login <script>alert(1)</script>
```
"""

FINDING_3 = """### SEC-3: Upload có thể ghi đè file khác
- Kết luận: cần kiểm thêm
- Lớp: FILE-UPLOAD
- Ai: khách đã đăng nhập
- Dấu vết: `app/upload.py:20`
- Còn thiếu: Ranh giới — chưa rõ thư mục lưu có dùng chung giữa các khách
"""

FINDING_4 = """### SEC-4: SQL ghép chuỗi trong báo cáo nội bộ
- Kết luận: bác bỏ
- Lớp: SQLI
- Dấu vết: `app/report.py:40`
- Lý do bác: giá trị ghép là hằng trong code (N3), không ai ngoài điều khiển; kiểu `List<Order>` không liên quan
"""

HEAD = """# Báo cáo soát 261027-soat-don
- Phạm vi: `secu.py scope` — 12 file
- Spec: mức 4
- Người soát: agent A
- Người kiểm: agent B (lượt riêng)

Xem [SEC-1](#sec-1) và [OWASP](https://owasp.org).

## Phát hiện

"""

TAIL = """
## Chưa soát
- `assets/logo.png` (nhị phân)
"""


def report(*findings, head=HEAD, tail=TAIL):
    return head + "\n".join(findings) + tail


FULL = report(FINDING_1, FINDING_2, FINDING_3, FINDING_4)


def run(*args, cwd=None, env=None):
    return subprocess.run([sys.executable, SECU, *args], capture_output=True, text=True, cwd=cwd, env=env)


def write(path, content, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as fh:
        fh.write(content)


class Check(unittest.TestCase):
    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        write(os.path.join(self.root, "specs", "mk-specs.yml"), "version: 1\nids:\n  uc: 'UC-\\d{3}'\n")
        write(os.path.join(self.root, "specs", "orders", "UC-101-xem-don.md"), UC_FILE)
        os.makedirs(os.path.join(self.root, "specs", "changes", "261027-gioi-han-dang-nhap"))
        self.path = os.path.join(self.root, "specs", "security", "261027-soat-don.md")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def check(self, text, root=None):
        write(self.path, text)
        return run("check", self.path, "--root", root or self.root)

    def blocked(self, text, *needles, root=None):
        res = self.check(text, root=root)
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        for n in needles:
            self.assertIn(n, res.stdout)
        self.assertTrue(all(line.startswith("CHẶN:") for line in res.stdout.splitlines() if line.strip()), res.stdout)
        return res

    # UC-802 AC-6
    def test_valid_report_prints_summary_by_verdict_and_level(self):
        res = self.check(FULL)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("4 phát hiện · xác nhận 2 (cao 1, thấp 1) · cần kiểm thêm 1 · bác bỏ 1", res.stdout)
        self.assertNotIn("CHẶN", res.stdout)

    def test_summary_orders_levels_from_critical_and_handles_empty_report(self):
        crit = FINDING_2.replace("SEC-2", "SEC-5").replace("Mức: thấp", "Mức: nghiêm trọng")
        res = self.check(report(FINDING_1, FINDING_2, crit))
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("3 phát hiện · xác nhận 3 (nghiêm trọng 1, cao 1, thấp 1)", res.stdout)
        self.assertNotIn("trung bình", res.stdout)
        res = self.check(report())
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertEqual(res.stdout.strip(), "0 phát hiện")

    # UC-802 AC-1
    def test_confirmed_finding_needs_level_facts_fix_type_class_and_trace(self):
        cases = (
            ("- Mức: cao\n", "", "Mức"),
            ("- Mức: cao\n", "- Mức: rất cao\n", "Mức"),
            ("- Ai: khách đã đăng nhập\n", "", "Ai"),
            ("- Đầu vào: mã đơn trên đường dẫn\n", "- Đầu vào:\n", "Đầu vào"),
            ("- Kiểm soát thiếu: so chủ đơn với người gọi\n", "", "Kiểm soát thiếu"),
            ("- Ranh giới: giữa hai khách\n", "- Ranh giới: —\n", "Ranh giới"),
            ("- Tài sản: đơn hàng, địa chỉ giao\n", "", "Tài sản"),
            ("- Hậu quả: đọc địa chỉ giao của khách khác\n", "", "Hậu quả"),
            ("- Đề xuất sửa: thêm điều kiện chủ đơn vào truy vấn\n", "", "Đề xuất sửa"),
            ("- Loại: code sai AC\n", "- Loại: lỗi code\n", "Loại"),
            ("- Loại: code sai AC\n", "", "Loại"),
            ("- Lớp: IDOR\n", "- Lớp:\n", "Lớp"),
            ("  - `app/orders.py:12` nhận `order_id` từ đường dẫn\n  - `app/db.py:30-34` truy vấn không lọc chủ đơn\n",
             "  - orders.py dòng 12, không có token\n", "Dấu vết"),
        )
        for old, new, field in cases:
            self.assertIn(old, FINDING_1, old)
            res = self.blocked(report(FINDING_1.replace(old, new), FINDING_4), "SEC-1", field)
            self.assertNotIn("SEC-4", res.stdout)

    def test_trace_token_may_be_a_bare_file_or_a_line_range(self):
        for trace in ("`app.py:12`", "`src/a.js:3-9`", "xem `./web/x.ts:1` và `y.go:2`"):
            res = self.check(report(FINDING_2.replace("`login.py:8`", trace)))
            self.assertEqual(res.returncode, 0, trace + res.stdout)
        for trace in ("app.py:12", "`app.py`", "`app.py:dòng 3`"):
            self.blocked(report(FINDING_2.replace("`login.py:8`", trace)), "SEC-2", "Dấu vết")
        res = self.check(report(FINDING_2.replace("`login.py:8`", "`src/my app/login.py:8`")))
        self.assertEqual(res.returncode, 0, res.stdout)

    # UC-802 AC-1 (Lớp)
    def test_class_must_start_with_a_catalog_code(self):
        with open(CATALOG, encoding="utf-8") as fh:
            headings = set(re.findall(r"^### ([A-Z][A-Z0-9-]+) —", fh.read(), re.M))
        self.assertEqual(headings, CODES)
        for code in sorted(CODES) + ["KHAC", "IDOR (đọc đơn của khách khác)", "`SSRF` — ảnh đại diện"]:
            res = self.check(report(FINDING_1.replace("- Lớp: IDOR", "- Lớp: " + code)))
            self.assertEqual(res.returncode, 0, code + res.stdout)
        for bad in ("lỗi quyền truy cập", "IDORX", "idor", "Broken access control", "KHÁC"):
            res = self.blocked(report(FINDING_1.replace("- Lớp: IDOR", "- Lớp: " + bad)), "SEC-1", "Lớp")
            self.assertIn("catalog", res.stdout)
        self.blocked(report(FINDING_4.replace("- Lớp: SQLI", "- Lớp: tiêm SQL")), "SEC-4", "Lớp")

    # UC-802 AC-4 (heading level)
    def test_finding_heading_must_be_level_three(self):
        for heading in ("## SEC-5: tiêu đề", "#### SEC-5: tiêu đề", "### Sec-5: tiêu đề", "###SEC-5: tiêu đề"):
            body = report(FINDING_4 + "\n" + heading + "\n- Kết luận: bác bỏ\n- Lý do bác: x\n")
            line = (HEAD + FINDING_4 + "\n" + heading).count("\n") + 1
            self.blocked(body, f"dòng {line}: phát hiện phải là `### SEC-n:`")
        ok = self.check(report(FINDING_4 + "\n```md\n## SEC-9: ví dụ trong khối mã\n```\n"))
        self.assertEqual(ok.returncode, 0, ok.stdout)

    def test_hanging_uc_pattern_falls_back_to_the_default(self):
        write(os.path.join(self.root, "specs", "mk-specs.yml"), "ids:\n  uc: '(U+){20}-1'\n")
        write(self.path, report(FINDING_1.replace("- AC: UC-101 AC-2", "- AC: " + "U" * 30 + "-2 AC-1")))
        res = subprocess.run([sys.executable, SECU, "check", self.path, "--root", self.root],
                             capture_output=True, text=True, timeout=20)
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("SEC-1", res.stdout)

    # UC-802 AC-2
    def test_unconfirmed_and_rejected_findings_have_their_own_rules(self):
        self.blocked(report(FINDING_3.replace("- Lớp:", "- Mức: cao\n- Lớp:")), "SEC-3", "Mức")
        self.blocked(report(FINDING_3.replace("- Còn thiếu: Ranh giới — chưa rõ thư mục lưu có dùng chung giữa các khách\n", "")),
                     "SEC-3", "Còn thiếu")
        self.blocked(report(FINDING_4.replace("- Lý do bác:", "- Ghi chú:")), "SEC-4", "Lý do bác")
        for verdict in ("có thể", "an toàn", ""):
            self.blocked(report(FINDING_4.replace("- Kết luận: bác bỏ", "- Kết luận: " + verdict)), "SEC-4", "Kết luận")
        self.blocked(report(FINDING_4.replace("- Kết luận: bác bỏ\n", "")), "SEC-4", "Kết luận")
        ok = self.check(report(FINDING_3.replace("- Kết luận: cần kiểm thêm", "- Kết luận: **cần kiểm thêm**")))
        self.assertEqual(ok.returncode, 0, ok.stdout)

    # UC-802 AC-3
    def test_violated_ac_must_exist_and_be_live(self):
        self.blocked(report(FINDING_1.replace("- AC: UC-101 AC-2", "- AC: UC-101 AC-9")), "AC không có thật: UC-101 AC-9")
        self.blocked(report(FINDING_1.replace("- AC: UC-101 AC-2", "- AC: UC-777 AC-1")), "AC không có thật: UC-777 AC-1")
        self.blocked(report(FINDING_1.replace("- AC: UC-101 AC-2", "- AC: AC-2")), "SEC-1", "AC")
        self.blocked(report(FINDING_1.replace("- AC: UC-101 AC-2\n", "")), "SEC-1", "AC")
        res = self.blocked(report(FINDING_1.replace("- AC: UC-101 AC-2", "- AC: UC-101 AC-3")), "AC đã bỏ: UC-101 AC-3")
        self.assertNotIn("không có thật", res.stdout)
        # "deprecated" in a live AC title without the bracket is not a drop marker
        ok = self.check(report(FINDING_1.replace("- AC: UC-101 AC-2", "- AC: UC-101 AC-4")))
        self.assertEqual(ok.returncode, 0, ok.stdout)
        # AC-1 must not be satisfied by AC-10 nor by a UC copy inside changes/
        write(os.path.join(self.root, "specs", "changes", "x", "UC-102-moi.md"), "### AC-1: mới\n")
        self.blocked(report(FINDING_1.replace("- AC: UC-101 AC-2", "- AC: UC-102 AC-1")), "AC không có thật: UC-102 AC-1")

    def test_ac_lookup_follows_specs_dir_and_uc_pattern_of_the_target_repo(self):
        root = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, True)
        write(os.path.join(root, "specs", "mk-specs.yml"), 'specs_dir: docs/spec\nids:\n  uc: "CASE-\\\\d+"\n')
        write(os.path.join(root, "docs", "spec", "don", "CASE-7-don.md"), "## Acceptance Criteria\n### AC-1: a\n")
        os.makedirs(os.path.join(root, "docs", "spec", "changes", "261027-gioi-han-dang-nhap"))
        good = report(FINDING_1.replace("- AC: UC-101 AC-2", "- AC: CASE-7 AC-1"), FINDING_2)
        res = self.check(good, root=root)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.blocked(report(FINDING_1.replace("- AC: UC-101 AC-2", "- AC: CASE-7 AC-2")), "AC không có thật: CASE-7 AC-2",
                     root=root)
        self.blocked(report(FINDING_1), "SEC-1", "AC", root=root)  # UC-101 is not an id of this repo

    def test_without_spec_config_only_the_ac_form_is_checked(self):
        os.remove(os.path.join(self.root, "specs", "mk-specs.yml"))
        res = self.check(report(FINDING_1.replace("- AC: UC-101 AC-2", "- AC: UC-555 AC-9")))
        self.assertEqual(res.returncode, 0, res.stdout)

    def test_missing_ac_needs_an_existing_draft_proposal_and_wrong_rule_a_real_ac(self):
        self.blocked(report(FINDING_2.replace("261027-gioi-han-dang-nhap", "261027-khong-co")), "SEC-2", "261027-khong-co")
        self.blocked(report(FINDING_2.replace("- Proposal: `261027-gioi-han-dang-nhap`\n", "")), "SEC-2", "Proposal")
        wrong = FINDING_2.replace("- Loại: thiếu AC", "- Loại: luật sai")
        self.blocked(report(wrong), "SEC-2", "AC")
        self.blocked(report(wrong.replace("- Proposal:", "- AC: UC-101 AC-8\n- Proposal:")), "AC không có thật: UC-101 AC-8")
        ok = self.check(report(wrong.replace("- Proposal:", "- AC: UC-101 AC-1\n- Proposal:")))
        self.assertEqual(ok.returncode, 0, ok.stdout)

    # UC-802 AC-4
    def test_structure_ids_header_and_unsurveyed_section(self):
        self.blocked(report(FINDING_1, FINDING_2.replace("SEC-2", "SEC-1")), "SEC-1", "hai lần")
        for key in ("Phạm vi", "Spec", "Người soát", "Người kiểm"):
            line = next(ln for ln in HEAD.splitlines() if ln.startswith(f"- {key}:"))
            self.blocked(report(FINDING_4, head=HEAD.replace(line + "\n", "")), key)
            self.blocked(report(FINDING_4, head=HEAD.replace(line, f"- {key}:")), key)
        self.blocked(report(FINDING_4, head=HEAD.replace("- Spec: mức 4", "- Spec: có")), "Spec")
        ok = self.check(report(FINDING_4, head=HEAD.replace("- Spec: mức 4", "- Spec: chưa có")))
        self.assertEqual(ok.returncode, 0, ok.stdout)
        self.blocked(report(FINDING_4, tail="\n## Ghi chú\n- x\n"), "Chưa soát")

    def test_placeholders_outside_code_are_blocked(self):
        self.blocked(report(FINDING_4.replace("- Lý do bác: giá trị", "- Lý do bác: <lý do> giá trị")), "<lý do>")
        self.blocked(report(FINDING_4, head=HEAD.replace("— 12 file", "— <số> file")), "<số>")
        ok = self.check(report(FINDING_4.replace("- Lý do bác: giá trị", "- Lý do bác: `<lý do>` giá trị a < b > c")))
        self.assertEqual(ok.returncode, 0, ok.stdout)

    def test_relative_links_are_blocked_even_inside_code(self):
        for link in ("[db](../../src/db.js)", "`handlers[t](req)`", "[x](changes/a/proposal.md#ac)"):
            self.blocked(report(FINDING_4 + "\n" + link + "\n"), "link")
        self.blocked(report(FINDING_4 + "\n```js\nconst f = handlers[t](req)\n```\n"), "link")
        for link in ("[a](#sec-4)", "[b](https://example.com/x)", "[c](mailto:a@example.com)", "`handlers[t] (req)`"):
            ok = self.check(report(FINDING_4 + "\n" + link + "\n"))
            self.assertEqual(ok.returncode, 0, link + ok.stdout)

    # UC-802 AC-5
    def test_secret_values_are_blocked_by_line_without_echoing_them(self):
        body = "B7kQ2mX9pL4vR8nT1wY6"
        secrets = (
            cat("AK", "IA", "QWERTYUIOP234567"),
            cat("gh", "p_", body, "abcdefghij123456"),
            cat("github", "_pat_", "11ABCDEFG0123456789_abcdefgh"),
            cat("sk", "_live_", body),
            cat("rk", "_test_", body),
            cat("s", "k-", body, "xyz"),
            cat("xo", "xb-", "1234567890-abcdef"),
            cat("AI", "za", "Sy", "A" * 31, "x2"),
            cat("ey", "JhbGciOiJIUzI1NiJ9", ".ey", "JzdWIiOiIxMjM0NTYifQ", ".s1gnatureAbcdefghij"),
            cat("postgres://app:", "Pr0dPass", "word@db:5432/x"),
            cat("redis://:", "s3cretPw9", "@cache:6379"),
            cat("postgres://app:", "$ecretPassw0rd", "@db/shop"),
        )
        self.assertEqual(len(secrets[1]), 40)
        for secret in secrets:
            res = self.blocked(report(FINDING_4 + "\nGiá trị lộ: " + secret + "\n"), "che lại (giữ ≤ 4 ký tự đầu)")
            line = (HEAD + FINDING_4 + "\nGiá trị lộ").count("\n") + 1
            self.assertIn(f"dòng {line}", res.stdout, secret)
            self.assertNotIn(secret, res.stdout)
            self.assertNotIn(secret[4:12], res.stdout)
        key = cat("-----BEGIN RSA PRIVATE ", "KEY-----\n", "MIIEowIBAAKCAQEA", "x7Qz" * 10, "\n")
        self.blocked(report(FINDING_4 + "\n```\n" + key + "```\n"), "che lại")

    def test_masked_or_secret_like_text_is_not_blocked(self):
        for text in (cat("gh", "p_••••"), "task-management-dashboard-v2", "postgres://app:Pr0d…@db",
                     cat("-----BEGIN OPENSSH PRIVATE ", "KEY-----"), "mysql://u:ab*****@h", "risk-assessment-for-q3-2026-review",
                     cat("AK", "IA", "••••"), "postgres://app:${DB_PASSWORD}@db/shop", "amqp://bot:{password}@mq",
                     "mysql://root:%(db_pass)s@localhost/x", "postgres://app:<mật-khẩu>@db", "postgres://app:$DB_PASS@db"):
            res = self.check(report(FINDING_4 + "\nGiá trị: `" + text + "`\n"))
            self.assertEqual(res.returncode, 0, text + res.stdout)

    # UC-802 AC-7
    def test_fixed_line_needs_a_confirmed_finding_and_a_hex_hash(self):
        ok = self.check(report(FINDING_1 + "- Đã sửa: commit a1b2c3d\n"))
        self.assertEqual(ok.returncode, 0, ok.stdout)
        ok = self.check(report(FINDING_1 + "- Đã sửa: commit `" + "0123456789abcdef" * 2 + "01234567`\n"))
        self.assertEqual(ok.returncode, 0, ok.stdout)
        for bad in ("commit a1b2c3", "commit xyz1234", "commit sắp làm", "commit " + "a" * 41):
            self.blocked(report(FINDING_1 + "- Đã sửa: " + bad + "\n"), "SEC-1", "Đã sửa")
        self.blocked(report(FINDING_3 + "- Đã sửa: commit a1b2c3d\n"), "SEC-3", "Đã sửa")
        self.blocked(report(FINDING_4 + "- Đã sửa: commit a1b2c3d\n"), "SEC-4", "Đã sửa")

    def test_bad_call_or_unreadable_report_exits_2(self):
        self.assertEqual(run("check", os.path.join(self.root, "khong-co.md")).returncode, 2)
        self.assertEqual(run("check").returncode, 2)
        self.assertEqual(run("lam-gi").returncode, 2)
        write(self.path, b"\xff\xfe\x00", mode="wb")
        self.assertEqual(run("check", self.path, "--root", self.root).returncode, 2)


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class Scope(unittest.TestCase):
    def setUp(self):
        self.repo = os.path.realpath(tempfile.mkdtemp())
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        files = {
            "app.py": "print(1)\n",
            "src/api/orders.py": "x = 1\n",
            "src/api/users.py": "y = 2\n",
            "src/web/page.js": "let a\n",
            "logo.svg": "<svg/>\n",
            "packages/a/node_modules/lib/index.js": "z\n",
            "vendor/x.php": "<?php\n",
            "build/out.js": "o\n",
            "web/.next/cache.js": "c\n",
            "src/__pycache__/m.py": "m\n",
            "package-lock.json": "{}\n",
            "poetry.lock": "\n",
            "go.sum": "\n",
            "img/photo.PNG": "not really\n",
            "docs/manual.pdf": "x\n",
            "data/blob.dat": b"abc\x00def",
            "data/edge.txt": "a" * 1048576,
            "data/big.txt": "a" * 1048577,
            ".gitignore": "ignored.txt\n",
        }
        for rel, content in files.items():
            write(os.path.join(self.repo, rel), content, "wb" if isinstance(content, bytes) else "w")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "init")
        write(os.path.join(self.repo, "untracked.py"), "u\n")
        write(os.path.join(self.repo, "ignored.txt"), "i\n")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def listed(self, out):
        return [ln for ln in out.splitlines() if ln and not ln.startswith(("BỎ QUA:", "NHẠY CẢM:")) and "file cần soát" not in ln]

    # UC-803 AC-1
    def test_lists_tracked_files_and_each_skipped_file_with_reason(self):
        res = run("scope", cwd=self.repo)
        self.assertEqual(res.returncode, 0, res.stderr)
        listed = self.listed(res.stdout)
        self.assertEqual(listed, sorted(["app.py", "src/api/orders.py", "src/api/users.py", "src/web/page.js", "logo.svg",
                                         "data/edge.txt", ".gitignore"]))
        skipped = [ln for ln in res.stdout.splitlines() if ln.startswith("BỎ QUA:")]
        paths = [ln.split(": ", 1)[1].split(" (", 1)[0] for ln in skipped]
        self.assertEqual(paths, sorted(["packages/a/node_modules/lib/index.js", "vendor/x.php", "build/out.js",
                                        "web/.next/cache.js", "src/__pycache__/m.py", "package-lock.json", "poetry.lock",
                                        "go.sum", "img/photo.PNG", "docs/manual.pdf", "data/blob.dat", "data/big.txt"]))
        self.assertTrue(all(ln.endswith(")") and " (" in ln for ln in skipped), skipped)
        self.assertEqual(res.stdout.strip().splitlines()[-1], "7 file cần soát · 12 bỏ qua")
        self.assertNotIn("untracked.py", res.stdout)
        self.assertNotIn("ignored.txt", res.stdout)
        self.assertEqual(run("scope", cwd=self.repo).stdout, res.stdout)

    # UC-803 AC-2
    def test_changes_only_lists_modified_and_new_files(self):
        write(os.path.join(self.repo, "app.py"), "print(2)\n")
        write(os.path.join(self.repo, "src/web/staged.js"), "s\n")
        git(self.repo, "add", "src/web/staged.js")
        os.remove(os.path.join(self.repo, "src/api/users.py"))
        write(os.path.join(self.repo, "vendor/new.php"), "n\n")
        res = run("scope", "--thay-doi", cwd=self.repo)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(self.listed(res.stdout), ["app.py", "src/web/staged.js", "untracked.py"])
        self.assertIn("BỎ QUA: vendor/new.php", res.stdout)
        self.assertNotIn("users.py", res.stdout)
        self.assertNotIn("ignored.txt", res.stdout)

    def test_changes_against_a_base_branch_use_the_merge_base(self):
        git(self.repo, "checkout", "-q", "-b", "feat")
        write(os.path.join(self.repo, "src/api/orders.py"), "x = 2\n")
        git(self.repo, "commit", "-q", "-am", "feat")
        git(self.repo, "checkout", "-q", "main")
        write(os.path.join(self.repo, "src/web/page.js"), "let b\n")
        git(self.repo, "commit", "-q", "-am", "main moves on")
        git(self.repo, "checkout", "-q", "feat")
        write(os.path.join(self.repo, "app.py"), "print(3)\n")
        res = run("scope", "--thay-doi", "main", cwd=self.repo)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(self.listed(res.stdout), ["app.py", "src/api/orders.py", "untracked.py"])
        res = run("scope", "--thay-doi", "khong-co-nhanh", cwd=self.repo)
        self.assertEqual(res.returncode, 2)
        self.assertIn("khong-co-nhanh", res.stdout + res.stderr)

    # UC-803 AC-3
    def test_sensitive_files_are_flagged_before_skip_rules(self):
        pk = "-----BEGIN PRIVATE " + "KEY-----\nMIIE\n"
        sensitive = {".env": "A=1\n", "cfg/.env.local": "A=1\n", ".env.production": "A=1\n", ".env.development": "A=1\n",
                     ".env.staging": "A=1\n", "build/.env": "A=1\n", "vendor/x/id_rsa": "k\n", "id_dsa": "k\n",
                     "id_ecdsa": "k\n", "keys/id_ed25519": "k\n", "a.p12": b"\x00k", "b.pfx": "k\n", "c.jks": "k\n",
                     "d.keystore": "k\n", "infra/terraform.tfstate": "{}\n", "credentials.json": "{}\n",
                     "tls/server.pem": pk, "tls/server.key": pk}
        harmless = {".env.example": "A=\n", ".env.sample": "A=\n", ".env.template": "A=\n", ".env.dist": "A=\n",
                    "id_rsa.pub": "ssh-ed25519 AAAA\n", "tls/cert.pem": "-----BEGIN CERTIFICATE-----\n",
                    "slides.key": "keynote\n"}
        for rel, content in {**sensitive, **harmless}.items():
            write(os.path.join(self.repo, rel), content, "wb" if isinstance(content, bytes) else "w")
        git(self.repo, "add", "-f", "-A")
        git(self.repo, "commit", "-q", "-m", "keys")
        res = run("scope", cwd=self.repo)
        flagged = [ln for ln in res.stdout.splitlines() if ln.startswith("NHẠY CẢM:")]
        self.assertEqual(flagged, [f"NHẠY CẢM: {p} — file bí mật đang nằm trong git" for p in sorted(sensitive)])
        self.assertIn(".env.example", self.listed(res.stdout))
        self.assertIn("BỎ QUA: build/.env", res.stdout)

    # UC-803 AC-4
    def test_path_argument_or_subdirectory_limits_the_listing(self):
        for args, cwd in ((("scope", "src/api"), self.repo), (("scope",), os.path.join(self.repo, "src", "api")),
                          (("scope", os.path.join(self.repo, "src", "api")), tempfile.gettempdir())):
            res = run(*args, cwd=cwd)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual(self.listed(res.stdout), ["src/api/orders.py", "src/api/users.py"], args)
            self.assertIn("2 file cần soát · 0 bỏ qua", res.stdout)
        write(os.path.join(self.repo, "src/api/new.py"), "n\n")
        res = run("scope", "--thay-doi", cwd=os.path.join(self.repo, "src"))
        self.assertEqual(self.listed(res.stdout), ["src/api/new.py"])

    # UC-803 AC-5
    def test_outside_git_exits_2_with_advice(self):
        plain = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, plain, True)
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=os.path.dirname(plain))
        res = run("scope", cwd=plain, env=env)
        self.assertEqual(res.returncode, 2)
        self.assertIn("cần repo git — không có thì tự liệt kê file và ghi vào `- Phạm vi:`", res.stdout + res.stderr)

    def test_every_git_call_skips_optional_locks(self):
        real = shutil.which("git")
        bindir = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, bindir, True)
        log = os.path.join(bindir, "calls.log")
        shim = os.path.join(bindir, "git")
        write(shim, f'#!/bin/sh\nprintf "%s\\n" "$*" >> "{log}"\nexec "{real}" "$@"\n')
        os.chmod(shim, os.stat(shim).st_mode | stat.S_IEXEC)
        env = dict(os.environ, PATH=bindir + os.pathsep + os.environ.get("PATH", ""))
        write(os.path.join(self.repo, "app.py"), "print(9)\n")
        for args in (("scope",), ("scope", "--thay-doi"), ("scope", "--thay-doi", "main")):
            self.assertEqual(run(*args, cwd=self.repo, env=env).returncode, 0, args)
        with open(log, encoding="utf-8") as fh:
            calls = [ln for ln in fh.read().splitlines() if ln]
        self.assertTrue(calls)
        self.assertTrue(all(c.startswith("--no-optional-locks") for c in calls), calls)


if __name__ == "__main__":
    unittest.main()
