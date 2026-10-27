"""Tests for mk-cook gate.py. Run: python3 -m unittest discover -s skills/mk-cook/scripts/tests"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True
GATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gate.py")
REVIEWERS = "- Người duyệt nghiệp vụ: chủ shop, 2026-10-27, chat · Người duyệt kỹ thuật: reviewer agent, 2026-10-27, APPROVE"

HEAD = """# 261027-don-hang: Đặt hàng có hạn thanh toán
- Status: {status}
- BR: BR-01
- Đụng tới: UC-101 (checkout), UC-102 (checkout)
{reviewers}
{extra}
## Vì sao
Khách bỏ giỏ hàng.

## Thay đổi spec

### BR-01
- MODIFIED In Scope: thêm hạn thanh toán

### UC-101 (Đặt hàng — checkout)
- MODIFIED Main Flow bước 3: giữ hàng 15 phút
- ADDED AC-1: Given giỏ có 1 món When đặt Then giữ hàng 15 phút
- MODIFIED AC-2, AC-3: 10 phút → 15 phút
  - Given đơn lúc 9:00
  - When 9:16
- DEPRECATED AC-4: bỏ giữ hàng vô hạn

### Entity
- Đơn.hạn_thanh_toán: thời điểm đặt + 15 phút

### UC-102 (Huỷ đơn)
- ADDED AC-3a (huỷ khi hết hạn):
  - Given đơn quá hạn
"""

EVIDENCE = """
## Bằng chứng nghiệm thu
- AC ↔ Test: UC-101 AC-1 ↔ `test_hold`; UC-101 AC-2 ↔ `test_expire`; UC-101 AC-3 ↔ `test_expire_msg`; UC-102 AC-3a ↔ `test_cancel`; UC-101 AC-4 ↔ test cũ đã xoá
- Trạng thái kiểm chứng: 42 test xanh; nút `<button>` có focus
"""


def run(*args, cwd=None):
    return subprocess.run([sys.executable, GATE, *args], capture_output=True, text=True, cwd=cwd)


class Gate(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.change = os.path.join(self.root, "specs", "changes", "261027-don-hang")
        os.makedirs(self.change)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, status="approved (sau review kỹ thuật 2026-10-27)", extra="", tail="", plan=None,
              reviewers=REVIEWERS, body=None):
        with open(os.path.join(self.change, "proposal.md"), "w", encoding="utf-8") as fh:
            fh.write(body if body is not None else HEAD.format(status=status, extra=extra, reviewers=reviewers) + tail)
        if plan is not None:
            with open(os.path.join(self.change, "plan.md"), "w", encoding="utf-8") as fh:
                fh.write(plan)

    def spec_body(self, changes, status="approved"):
        return f"# x\n- Status: {status}\n{REVIEWERS}\n\n## Thay đổi spec\n{changes}"

    def test_unapproved_or_unreviewed_proposal_is_blocked_without_listing_acs(self):
        for status, reviewers, why in (
                ("draft", REVIEWERS, "chưa approved"),
                ("approved", REVIEWERS.replace("reviewer agent, 2026-10-27, APPROVE", "chờ"), "người duyệt kỹ thuật"),
                ("approved", "- Người duyệt kỹ thuật: R, 2026-10-27", "người duyệt nghiệp vụ"),
                ("approved", REVIEWERS.replace("chủ shop, 2026-10-27, chat", "chờ"), "người duyệt nghiệp vụ"),
                ("archived (approved sau review kỹ thuật)", REVIEWERS, "đã hợp nhất")):
            self.write(status=status, reviewers=reviewers)
            res = run(self.change)
            self.assertEqual(res.returncode, 1, status + res.stdout)
            self.assertIn(why, res.stdout)
            self.assertNotIn("AC-1", res.stdout)
        self.write(status="implemented (code 07a8b84)")
        self.assertEqual(run(self.change).returncode, 0)
        self.write(status="`approved` (2026-10-27)")
        self.assertEqual(run(self.change).returncode, 0)
        self.write(status="**approved**")
        self.assertEqual(run(self.change).returncode, 0)
        for pending in ("đang chờ Minh", "TBD", "?", "chưa có", "(chờ)", '"chờ"'):
            self.write(reviewers=REVIEWERS.replace("reviewer agent, 2026-10-27, APPROVE", pending))
            self.assertIn("người duyệt kỹ thuật", run(self.change).stdout, pending)

    def test_approved_proposal_lists_each_ac_once_under_its_uc(self):
        self.write()
        res = run(self.change)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("UC-101: AC-1, AC-2, AC-3", res.stdout)
        self.assertIn("UC-102: AC-3a", res.stdout)
        self.assertEqual(res.stdout.count("AC-2"), 1)

    def test_new_uc_bare_acs_and_inline_uc_are_read(self):
        self.write(body=self.spec_body(
            "### UC-401 (mới, release): Phát hành\n- AC-1: Given tag v1.3.0 When tính Then v1.4.0\n"
            "- AC-1, AC-7…AC-9: test gắn tag (hành vi không đổi)\n"
            "### #4 (Low) — đường dẫn UTF-8\n- ADDED UC-305 AC-8: Given đường ngoài repo When gen Then từ chối\n"))
        res = run(self.change)
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("UC-401: AC-1", res.stdout)
        self.assertIn("UC-305: AC-8", res.stdout)
        self.assertNotIn("AC-7", res.stdout)  # no Given → not a new AC

    def test_slug_and_proposal_path_resolve_like_the_folder(self):
        self.write()
        for arg in ("261027-don-hang", os.path.join(self.change, "proposal.md")):
            res = run(arg, "--root", self.root)
            self.assertEqual(res.returncode, 0, arg + res.stdout + res.stderr)
        self.assertEqual(run("khong-co", "--root", self.root).returncode, 2)

    def test_more_than_five_acs_or_large_scope_needs_plan(self):
        one = "\n### UC-103\n- ADDED AC-1: Given a When b Then c\n"
        self.write(tail=one)  # 5 AC (DEPRECATED does not count)
        self.assertEqual(run(self.change).returncode, 0)
        self.write(tail=one + "- ADDED AC-2: Given a When b Then c\n")  # 6 AC
        res = run(self.change)
        self.assertEqual(res.returncode, 1)
        self.assertIn("cần plan.md", res.stdout)
        self.assertIn("6 AC", res.stdout)
        self.write(extra="- Quy mô: lớn")
        res = run(self.change)
        self.assertEqual(res.returncode, 1)
        self.assertIn("Quy mô: lớn", res.stdout)
        for scale in ("thường (thêm/sửa > 5 AC thì ghi `lớn`)", "không lớn"):
            self.write(extra="- Quy mô: " + scale)
            self.assertEqual(run(self.change).returncode, 0, scale)  # only the first word decides

    def test_plan_must_name_every_ac_exactly_once(self):
        plan = ("# Plan\n## Phase 1\n- AC: UC-101 AC-1, AC-2, AC-3\n"
                "## Phase 2\n- AC: UC-109 AC-9\n")
        self.write(extra="- Quy mô: lớn", plan=plan)
        res = run(self.change)
        self.assertEqual(res.returncode, 1)
        self.assertIn("plan.md thiếu: UC-102 AC-3a", res.stdout)
        self.assertIn("CẢNH BÁO", res.stdout)
        self.assertIn("UC-109 AC-9", res.stdout)
        self.write(extra="- Quy mô: lớn", plan=plan.replace("UC-109 AC-9", "UC-102 AC-3a, UC-101 AC-1"))
        res = run(self.change)
        self.assertEqual(res.returncode, 1)
        self.assertIn("nhiều phase: UC-101 AC-1", res.stdout)
        self.write(extra="- Quy mô: lớn", plan=plan.replace("UC-109 AC-9", "UC-102 AC-3a"))
        self.assertEqual(run(self.change).returncode, 0)

    def test_only_uc_ids_own_the_acs_after_them_in_plan_and_evidence(self):
        plan = ("# Plan\nTổng: UC-101 AC-1, AC-2, AC-3; UC-102 AC-3a\n"
                "## Phase 1\n- AC: UC-101 AC-1 (ADR-29), AC-2 (UTF-8)\n"
                "## Phase 2\n- AC: UC-102 AC-3a (BR-01); UC-101 AC-3\n")
        self.write(extra="- Quy mô: lớn", plan=plan)
        res = run(self.change)
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertNotIn("CẢNH BÁO", res.stdout)
        self.write(tail=EVIDENCE.replace("UC-101 AC-3 ↔ `test_expire_msg`; ", "UC-101 AC-1 ↔ t (SHA-256), AC-3; "))  # no plan needed: 4 AC
        self.assertEqual(run(self.change, "--done").returncode, 0)

    def test_done_needs_evidence_for_every_ac_and_no_placeholder(self):
        self.write(tail=EVIDENCE.replace("UC-101 AC-3 ↔ `test_expire_msg`; ", "")
                   + "- Rationale & Quyết định: <điền khi code xong>\n- Truy vết: commit <hash>\n")
        res = run(self.change, "--done")
        self.assertEqual(res.returncode, 1)
        self.assertIn("<hash>", res.stdout)
        self.assertIn("chưa nhắc: UC-101 AC-3", res.stdout)
        self.assertIn("<điền khi code xong>", res.stdout)
        self.assertNotIn("<button>", res.stdout)
        self.write(tail=EVIDENCE + "- Kết quả: p95 < 200 ms, khung > 375px\n")
        res = run(self.change, "--done")
        self.assertEqual(res.returncode, 0, res.stdout)
        self.write()
        self.assertEqual(run(self.change, "--done").returncode, 1)  # no evidence section at all

    def test_deprecated_only_passes_and_still_needs_evidence(self):
        changes = "### UC-101\n- DEPRECATED AC-4: bỏ giữ hàng vô hạn\n"
        self.write(body=self.spec_body(changes))
        res = run(self.change)
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("Bỏ (xoá/sửa test, code)", res.stdout)
        self.assertIn("UC-101: AC-4", res.stdout)
        self.write(body=self.spec_body(changes + "\n## Bằng chứng nghiệm thu\n- AC ↔ Test: đã xoá test cũ\n"))
        res = run(self.change, "--done")
        self.assertEqual(res.returncode, 1)
        self.assertIn("chưa nhắc: UC-101 AC-4", res.stdout)

    def test_no_ac_line_is_blocked(self):
        self.write(body=self.spec_body("### UC-101\n- MODIFIED Main Flow: chữ\n"))
        res = run(self.change)
        self.assertEqual(res.returncode, 1)
        self.assertIn("không AC thì không code", res.stdout)
        self.write(body=self.spec_body("### UC-101\n### AC-1: Hết hạn\n- Given a\n"))
        self.assertIn("`- ADDED AC-n: …`", run(self.change).stdout)  # heading-style AC gets a hint

    def test_unnumbered_scattered_or_ownerless_acs_are_blocked(self):
        cases = (
            ("### UC-101\n- ADDED AC: Given a When b Then c\n", "AC chưa có số"),
            ("### UC-101\n- MODIFIED AC-m: <AC cũ> → <AC mới>\n", "AC chưa có số"),
            ("### UC-101\n- MODIFIED AC-2 và AC-3: a\n", "tách dòng"),
            ("### UC-101\n- MODIFIED AC-2 (sửa Then), AC-3: a\n", "tách dòng"),
            ("### UC-101\n- MODIFIED AC-2/AC-3: a\n", "tách dòng"),
            ("### UC-101\n- MODIFIED AC-10 Given: \"x\" → \"y\"; AC-11 Then: \"p\" → \"q\"\n", "tách dòng"),
            ("### UC-101\n- MODIFIED AC-7, AC-8: \"a\" → \"b\". AC-9: \"c\" → \"d\"\n", "tách dòng"),
            ("### Ghi chú UTF-8\n- ADDED AC-9: Given a When b Then c\n", "AC không rõ thuộc UC nào: AC-9"),
            ("### UC-102 / UC-101 — symlink\n- ADDED AC-5: Given a When b Then c\n", "AC không rõ thuộc UC nào: AC-5"),
        )
        for changes, why in cases:
            self.write(body=self.spec_body(changes))
            res = run(self.change)
            self.assertEqual(res.returncode, 1, changes + res.stdout)
            self.assertIn(why, res.stdout)
        self.write(body=self.spec_body("### Ghi chú\n- ADDED AC-6: Given như AC-5 When b Then c\n### UC-101\n"))
        self.assertIn("AC không rõ thuộc UC nào: AC-6", run(self.change).stdout)
        self.write(body=self.spec_body("### UC-101\n- ADDED AC-7: Given dòng `- MODIFIED AC-10 Given: x; AC-11 Then: y` When chạy Then chặn\n"))
        self.assertEqual(run(self.change).returncode, 0)  # examples inside backticks are not AC lines
        body = ("### UC-101\n- ADDED **AC-1**: Given a\n1. ADDED AC-2: Given b\n#### UC-102\n- ADDED AC-3: Given c\n"
                "```\n- ADDED AC-9: Given ví dụ trong khối code\n```\n")
        res = run(self.change) if self.write(body=self.spec_body(body)) is None else None
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("UC-101: AC-1, AC-2", res.stdout)
        self.assertIn("UC-102: AC-3", res.stdout)
        self.assertNotIn("AC-9", res.stdout)

    def test_hostile_or_quoted_uc_pattern_and_bad_encoding(self):
        cfg = os.path.join(self.root, "specs", "mk-specs.yml")
        body = self.spec_body("### " + "A" * 30 + "-1 UC-101\n- ADDED AC-1: Given a When b Then c\n")
        for hostile in ("'([A-Z0-9]+)+Z'", "'(A|A)+Z'", "'(A*)*Z'", "'([A-Z0-9]+){20}Z'", "'(?:A+){15}Z'"):
            with open(cfg, "w", encoding="utf-8") as fh:
                fh.write(f"ids:\n  uc: {hostile}\n")
            self.write(body=body)
            start = time.monotonic()
            res = run(self.change, "--root", self.root)
            self.assertLess(time.monotonic() - start, 5, hostile)
            self.assertEqual(res.returncode, 0, hostile + res.stdout)  # falls back to the default pattern
        with open(cfg, "w", encoding="utf-8") as fh:
            fh.write('ids:\n  uc: "ORD-\\\\d{2}"\n')
        self.write(body=self.spec_body("### ORD-12\n- ADDED AC-1: Given a When b Then c\n"))
        self.assertIn("ORD-12: AC-1", run(self.change, "--root", self.root).stdout)
        with open(os.path.join(self.change, "proposal.md"), "w", encoding="utf-16") as fh:
            fh.write(body)
        res = run(self.change, "--root", self.root)
        self.assertEqual(res.returncode, 2)
        self.assertIn("UTF-8", res.stdout)

    def test_uc_pattern_comes_from_project_config(self):
        os.makedirs(os.path.join(self.root, "specs"), exist_ok=True)
        with open(os.path.join(self.root, "specs", "mk-specs.yml"), "w", encoding="utf-8") as fh:
            fh.write("version: 1\nids:\n  uc: 'ORD-\\d{2}'\n  br: 'BR-\\d+'\n")
        self.write(body=self.spec_body("### ORD-12 (Đặt)\n- ADDED AC-1: Given a When b Then c\n"))
        res = run("261027-don-hang", "--root", self.root)
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("ORD-12: AC-1", res.stdout)


if __name__ == "__main__":
    unittest.main()
