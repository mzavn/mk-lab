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
    # default cwd has no specs/: the UC-file checks run only where a test writes specs/mk-specs.yml
    return subprocess.run([sys.executable, GATE, *args], capture_output=True, text=True,
                          cwd=cwd or tempfile.gettempdir())


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

    def project(self, specs_dir="specs"):
        os.makedirs(os.path.join(self.root, "specs"), exist_ok=True)
        with open(os.path.join(self.root, "specs", "mk-specs.yml"), "w", encoding="utf-8") as fh:
            fh.write(f"version: 1\nspecs_dir: {specs_dir}\nids:\n  uc: 'UC-\\d{{3}}'\n")

    def uc_file(self, rel, acs, extra=""):
        path = os.path.join(self.root, "specs", rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        heads = "".join(f"\n### {a}\n- Given a\n- When b\n- Then c\n" for a in acs)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f"# UC-201: Đặt\n- Status: implemented\n\n## History\n- v1\n{extra}\n"
                     f"## Main Flow\n### AC-50: tiêu đề ngoài mục AC không tính\n\n## Acceptance Criteria\n{heads}"
                     "```\n### AC-60: ví dụ trong khối code\n```\n")

    def gate(self, changes, done=False):
        evidence = "\n## Bằng chứng nghiệm thu\n- AC ↔ Test: UC-201 AC-9, AC-12, AC-14 ↔ `t`\n" if done else ""
        self.write(body=self.spec_body(changes) + evidence)
        return run(self.change, *(["--done"] if done else []), "--root", self.root)

    def test_added_ac_already_in_the_uc_file_is_blocked_with_the_next_number(self):
        self.project()
        taken = ("CHẶN: AC-9 đã có trong UC-201 — dùng số kế: AC-12 (nếu đang viết sẵn UC này cho change này: "
                 "thêm dòng History trỏ `changes/archive/261027-don-hang/proposal.md`)")
        for acs in (["AC-9", "AC-10", "AC-11"], ["AC-9: cũ (deprecated v3: bỏ)", "AC-10", "AC-11"]):
            self.uc_file("cook/UC-201-dat.md", acs)
            for changes in ("### UC-201\n- ADDED AC-9: Given a When b Then c\n",
                            "### UC-201 (mới)\n- AC-9: Given a When b Then c\n"):
                for done in (False, True):
                    res = self.gate(changes, done)
                    self.assertEqual(res.returncode, 1, changes + res.stdout)
                    self.assertIn(taken, res.stdout)
        res = self.gate("### UC-201\n- ADDED AC-12: Given a When b Then c\n")
        self.assertEqual(res.returncode, 0, res.stdout)
        for outside in ("AC-50", "AC-60"):  # headings outside `## Acceptance Criteria` or in a fence are not AC
            res = self.gate(f"### UC-201\n- ADDED {outside}: Given a When b Then c\n")
            self.assertEqual(res.returncode, 0, outside + res.stdout)
        for skipped in ("changes/261027-don-hang/UC-202-x.md", "_templates/UC-202.md", "templates/UC-202-y.md"):
            self.uc_file(skipped, ["AC-1"])
        res = self.gate("### UC-202\n- ADDED AC-1: Given a When b Then c\n")
        self.assertEqual(res.returncode, 0, res.stdout)  # UC files under changes/ and template folders do not count

    def test_uc_drafted_for_this_change_skips_only_the_taken_number_check(self):
        self.project()
        mine = "- v2 (change [x](../changes/archive/261027-don-hang/proposal.md))\n"
        self.uc_file("cook/UC-201-dat.md", ["AC-9", "AC-10", "AC-11"], extra=mine)
        for done in (False, True):
            res = self.gate("### UC-201\n- ADDED AC-9: Given a When b Then c\n", done)
            self.assertEqual(res.returncode, 0, res.stdout)
        self.uc_file("cook/UC-201-dat.md", ["AC-9", "AC-9", "AC-10"], extra=mine)
        res = self.gate("### UC-201\n- ADDED AC-9: Given a When b Then c\n")
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("hai tiêu đề `### AC-9`", res.stdout)
        self.uc_file("cook/UC-201-dat.md", ["AC-9"], extra=mine.replace("261027-don-hang", "261027-khac"))
        res = self.gate("### UC-201\n- ADDED AC-9: Given a When b Then c\n")
        self.assertIn("AC-9 đã có trong UC-201 — dùng số kế: AC-10", res.stdout)  # another change's draft

    def test_modified_or_deprecated_ac_must_exist_in_a_real_uc(self):
        self.project()
        for done in (False, True):
            for kind in ("MODIFIED", "DEPRECATED"):
                res = self.gate(f"### UC-201\n- {kind} AC-14: a → b\n", done)
                self.assertEqual(res.returncode, 1, kind + res.stdout)
                self.assertIn("CHẶN: không thấy file UC-201 — MODIFIED/DEPRECATED cần UC có thật", res.stdout)
            res = self.gate("### UC-201\n- MODIFIED AC-14: a\n- DEPRECATED AC-15: b\n", done)
            self.assertEqual(res.stdout.count("không thấy file UC-201"), 1, res.stdout)
            res = self.gate("### UC-201\n- ADDED AC-14: Given a When b Then c\n", done)
            self.assertEqual(res.returncode, 0, res.stdout)  # a new UC has no file yet
        self.uc_file("cook/UC-201-dat.md", ["AC-13"])
        for done in (False, True):
            for kind in ("MODIFIED", "DEPRECATED"):
                res = self.gate(f"### UC-201\n- {kind} AC-14: a → b\n", done)
                self.assertEqual(res.returncode, 1, kind + res.stdout)
                self.assertIn("CHẶN: UC-201 không có AC-14", res.stdout)
        self.uc_file("cook/UC-201-dat.md", ["AC-14"])
        res = self.gate("### UC-201\n- MODIFIED AC-14: a → b\n")
        self.assertEqual(res.returncode, 0, res.stdout)

    def test_several_files_with_one_uc_id_are_read_together(self):
        self.project()
        self.uc_file("cook/UC-201-dat.md", ["AC-1", "AC-2"])
        self.uc_file("cu/UC-201.md", ["AC-9"])
        res = self.gate("### UC-201\n- MODIFIED AC-1: a\n- MODIFIED AC-9: b\n")
        self.assertEqual(res.returncode, 0, res.stdout)
        res = self.gate("### UC-201\n- ADDED AC-2: Given a When b Then c\n")
        self.assertIn("AC-2 đã có trong UC-201 — dùng số kế: AC-10", res.stdout)

    def test_no_config_or_missing_specs_dir_skips_the_uc_file_checks(self):
        self.uc_file("cook/UC-201-dat.md", ["AC-9"])
        changes = "### UC-201\n- ADDED AC-9: Given a When b Then c\n- MODIFIED AC-14: a\n### UC-202\n- MODIFIED AC-1: a\n"
        res = self.gate(changes)
        self.assertEqual(res.returncode, 0, res.stdout)  # no specs/mk-specs.yml
        self.project(specs_dir="khong-co")
        res = self.gate(changes)
        self.assertEqual(res.returncode, 0, res.stdout)
        self.project()
        self.assertEqual(self.gate(changes).returncode, 1)


if __name__ == "__main__":
    unittest.main()
