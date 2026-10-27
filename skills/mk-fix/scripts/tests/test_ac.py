"""Tests for mk-fix ac.py. Run: python3 -m unittest discover -s skills/mk-fix/scripts/tests"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import unittest

sys.dont_write_bytecode = True
AC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ac.py")

CONFIG = """version: 1
language: vi
specs_dir: specs
layout: {layout}
ids:
  uc: {uc}
  br: 'BR-\\d+'
tests:
  file_pattern: '[^`]+/test_[\\w-]+\\.py'
  citation_style: {style}
"""

UC_101 = """# UC-101: Đặt hàng
- Status: {status}
- BR: BR-01

## Main Flow
1. Khách đặt hàng; hệ thống giữ hàng.

## Acceptance Criteria

### AC-1: Đặt hàng thành công
- Given giỏ có 2 món
- When khách đặt
- Then tạo đơn mới
- Tests: [`tests/test_don.py`](../../tests/test_don.py) › "test_dat_hang"

### AC-2: Giữ hàng 15 phút
- Given đơn tạo lúc 9:00
- When tới 9:14
- Then hàng vẫn được giữ cho khách
- Tests: ⚠ Chưa có test (smoke tay 2026-10-20)

### AC-3: Agent nhắc đúng lệnh (deprecated v6: chuyển sang UC-402 AC-1, AC-7)
- Given người dùng hỏi cập nhật
- When agent trả lời
- Then nhắc lệnh cũ
- Tests: ⚠ Chưa có test

### AC-4: AC thiếu Then bị chỉ ra, AC deprecated được bỏ qua
- Given UC có AC thiếu Then
- When chạy báo cáo
- Then AC đó bị liệt kê

## Dependencies
- UC-102
"""


def run(*args, cwd=None):
    return subprocess.run([sys.executable, AC, *args], capture_output=True, text=True, cwd=cwd)


class Repo(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.config()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def config(self, layout="contexts", uc="'UC-\\d+'", style="pointer", text=None):
        os.makedirs(os.path.join(self.root, "specs"), exist_ok=True)
        with open(os.path.join(self.root, "specs", "mk-specs.yml"), "w", encoding="utf-8") as fh:
            fh.write(text if text is not None else CONFIG.format(layout=layout, uc=uc, style=style))
        with open(os.path.join(self.root, "specs", "README.md"), "w", encoding="utf-8") as fh:
            fh.write("# Specs\n")

    def put(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return rel

    def uc101(self, rel="specs/checkout/UC-101-dat-hang.md", status="implemented"):
        return self.put(rel, UC_101.format(status=status))

    def ac(self, *args):
        return run(*args, "--root", self.root)

    def check(self, args, code, *needles):
        res = self.ac(*args)
        self.assertEqual(res.returncode, code, f"{args}\n{res.stdout}{res.stderr}")
        for needle in needles:
            self.assertIn(needle, res.stdout, args)
        return res


class OneAc(Repo):
    def test_prints_whole_ac_block_with_path_and_status_in_both_layouts(self):
        for layout, rel in (("contexts", "specs/checkout/UC-101-dat-hang.md"),
                            ("layers", "specs/use-cases/checkout/UC-101-dat-hang.md")):
            shutil.rmtree(os.path.join(self.root, "specs"))
            self.config(layout=layout)
            self.uc101(rel)
            res = self.check(("UC-101", "AC-2"), 0, rel, "implemented", "### AC-2: Giữ hàng 15 phút",
                             "- Given đơn tạo lúc 9:00", "- When tới 9:14", "- Then hàng vẫn được giữ cho khách",
                             "- Tests: ⚠ Chưa có test (smoke tay 2026-10-20)")
            self.assertNotIn("AC-3", res.stdout)  # block ends at the next heading
            self.assertNotIn("tạo đơn mới", res.stdout)
        self.assertNotIn("UC-102", self.ac("UC-101", "AC-4").stdout)  # last AC ends at `## Dependencies`
        self.put("specs/checkout/UC-102.md", UC_101.format(status="draft").replace("UC-101", "UC-102"))
        self.check(("UC-102", "AC-1"), 0, "specs/checkout/UC-102.md")  # file named exactly by the id

    def test_missing_uc_or_ac_exits_1_and_points_to_missing_ac(self):
        self.uc101()
        self.check(("UC-109", "AC-1"), 1, "không có UC-109", "thiếu AC")
        self.check(("UC-101", "AC-9"), 1, "UC-101 không có AC-9", "thiếu AC")
        self.check(("UC-10", "AC-1"), 1, "không có UC-10")  # UC-10 is not a prefix match of UC-101-…

    def test_deprecated_ac_or_uc_exits_1_but_word_deprecated_in_live_title_does_not(self):
        self.uc101()
        self.check(("UC-101", "AC-3"), 1, "(deprecated v6: chuyển sang UC-402 AC-1, AC-7)", "- Then nhắc lệnh cũ",
                   "AC đã bỏ", "thiếu AC", "luật sai")
        self.assertNotIn("đã bỏ", self.check(("UC-101", "AC-4"), 0).stdout)
        self.uc101(status="deprecated (thay bằng UC-120)")
        self.check(("UC-101", "AC-1"), 1, "UC đã bỏ", "- Then tạo đơn mới", "luật sai")


class ListMode(Repo):
    def lines(self, *args):
        return [ln for ln in self.check(args, 0).stdout.splitlines() if ln.startswith("AC-")]

    def test_lists_acs_in_file_order_with_markers(self):
        self.uc101()
        self.assertEqual(self.lines("UC-101"), [
            "AC-1: Đặt hàng thành công",
            "AC-2: Giữ hàng 15 phút [chưa có test]",
            "AC-3: Agent nhắc đúng lệnh (deprecated v6: chuyển sang UC-402 AC-1, AC-7) [bỏ]",
            "AC-4: AC thiếu Then bị chỉ ra, AC deprecated được bỏ qua [chưa có test]",
        ])
        self.check(("UC-109",), 1, "không có UC-109")

    def test_missing_tests_line_is_untested_only_for_pointer_style(self):
        for style in ("name", "both"):
            self.config(style=style)
            self.uc101()
            lines = self.lines("UC-101")
            self.assertIn("AC-4: AC thiếu Then bị chỉ ra, AC deprecated được bỏ qua", lines, style)
            self.assertIn("AC-2: Giữ hàng 15 phút [chưa có test]", lines, style)  # ⚠ counts in every style


class Search(Repo):
    def test_search_is_nfc_and_case_insensitive_ordered_by_uc_number(self):
        nfd = unicodedata.normalize("NFD", "số lượng")
        self.put("specs/kho/UC-101-dat-hang.md",
                 "# UC-101\n- Status: implemented\n\n## Acceptance Criteria\n\n"
                 "### AC-1: Số Lượng tối đa\n- Given a\n- Then b\n\n"
                 "### AC-2: Giá\n- Given giá\n- Then đúng\n\n"
                 f"### AC-3: Giỏ\n- Given giỏ\n- Then {nfd} cập nhật\n")
        self.put("specs/kho/UC-20-nhap-kho.md",
                 "# UC-20\n- Status: implemented\n\n## Acceptance Criteria\n\n"
                 "### AC-1: Nhập SỐ LƯỢNG âm (deprecated v2: bỏ)\n- Given a\n- Then b\n")
        self.put("specs/kho/UC-30-xuat-kho.md",
                 "# UC-30\n- Status: implemented\n\n## Main Flow\n1. Nhập số lượng\n\n"
                 "## Acceptance Criteria\n\n### AC-1: Xuất\n- Given a\n- Then b\n")
        res = self.check(("--tim", "SỐ LƯỢNG"), 0)
        hits = [ln for ln in res.stdout.splitlines() if ln.startswith("UC-")]
        self.assertEqual(len(hits), 3, res.stdout)
        self.assertTrue(hits[0].startswith("UC-20 AC-1: Nhập SỐ LƯỢNG âm"), hits)
        self.assertIn("[bỏ]", hits[0])
        self.assertIn("specs/kho/UC-20-nhap-kho.md", hits[0])
        self.assertEqual(hits[1], "UC-101 AC-1: Số Lượng tối đa · specs/kho/UC-101-dat-hang.md")
        self.assertEqual(hits[2], "UC-101 AC-3: Giỏ · specs/kho/UC-101-dat-hang.md")
        self.check(("--tim", "không ai viết chữ này"), 1)
        self.check(("--tim", unicodedata.normalize("NFD", "giỏ")), 0, "UC-101 AC-3: Giỏ")  # decomposed input too


PROPOSAL = """# 261027-gio-hang: Giỏ hàng
- Status: {status}

## Vì sao
Nhắc AC-1 ở đây không tính.

## Thay đổi spec

### UC-101 (Đặt hàng)
- MODIFIED AC-2, AC-3: 15 phút → 20 phút
- MODIFIED AC-9: AC không có thật
- MODIFIED Main Flow bước 1: chữ

### UC-109 (mới): Huỷ đơn
- ADDED AC-1: Given đơn quá hạn When hệ thống quét Then đơn bị huỷ
  - Given phụ: đơn có 2 món

### UC-110 (mới): Trả hàng
- AC-5: Given đơn đã giao When khách trả Then hoàn tiền

### Ghi chú
- ADDED UC-101 AC-7: Given khách VIP When đặt Then giữ hàng 30 phút

```
- ADDED UC-101 AC-8: Given ví dụ trong khối code
```

## Bằng chứng nghiệm thu
- AC ↔ Test: UC-101 AC-1
"""


class Proposals(Repo):
    def setUp(self):
        super().setUp()
        self.uc101()
        self.put("specs/changes/261027-gio-hang/proposal.md", PROPOSAL.format(status="approved (2026-10-27)"))
        self.put("specs/changes/archive/261001-cu/proposal.md",
                 PROPOSAL.format(status="archived").replace("gio-hang", "cu").replace("AC-2, AC-3", "AC-1"))

    def test_open_proposal_touching_ac_is_named_with_status_archive_ignored(self):
        for ac, code in (("AC-2", 0), ("AC-3", 1)):  # AC-3 is dropped, the proposal is still named
            self.check(("UC-101", ac), code, "đang có proposal đụng AC này: 261027-gio-hang (Status: approved)")
        res = self.check(("UC-101", "AC-1"), 0)
        self.assertNotIn("proposal", res.stdout)  # archive and prose/evidence mentions do not count

    def test_ac_being_added_by_proposal_exits_0_even_without_uc_file(self):
        self.put("specs/changes/261027-gio-hang/proposal.md", PROPOSAL.format(status="draft"))
        for uc, ac, line in (("UC-109", "AC-1", "ADDED AC-1: Given đơn quá hạn When hệ thống quét Then đơn bị huỷ"),
                             ("UC-110", "AC-5", "AC-5: Given đơn đã giao When khách trả Then hoàn tiền"),
                             ("UC-101", "AC-7", "ADDED UC-101 AC-7: Given khách VIP")):
            res = self.check((uc, ac), 0, "AC đang được thêm bởi proposal 261027-gio-hang", "draft", line)
            self.assertNotIn("thiếu AC", res.stdout)
        self.check(("UC-109", "AC-1"), 0, "Given phụ: đơn có 2 món")

    def test_modified_missing_ac_and_fenced_example_are_not_additions(self):
        # still names the proposal that touches the missing AC
        self.check(("UC-101", "AC-9"), 1, "UC-101 không có AC-9", "261027-gio-hang")
        self.check(("UC-101", "AC-8"), 1, "thiếu AC")

    def test_list_mode_names_proposals_and_acs_being_added_to_a_missing_uc(self):
        self.check(("UC-101",), 0, "đang có proposal đụng UC-101: 261027-gio-hang (Status: approved): AC-2, AC-3, AC-9, AC-7")
        res = self.check(("UC-109",), 0, "UC-109: AC đang được thêm bởi proposal 261027-gio-hang (Status: approved): AC-1")
        self.assertNotIn("thiếu AC", res.stdout)
        self.check(("UC-111",), 1, "không có UC-111")

    def test_search_also_finds_acs_in_open_proposals_after_main_spec_hits(self):
        path = "specs/changes/261027-gio-hang/proposal.md"
        res = self.check(("--tim", "VIP"), 0)
        self.assertEqual(res.stdout.strip().splitlines(), [
            f"UC-101 AC-7: Given khách VIP When đặt Then giữ hàng 30 phút · {path} [proposal 261027-gio-hang]"])
        hits = [ln for ln in self.check(("--tim", "GIỮ HÀNG"), 0).stdout.splitlines() if ln.startswith("UC-")]
        self.assertEqual(len(hits), 2, hits)
        self.assertTrue(hits[0].startswith("UC-101 AC-2: Giữ hàng 15 phút · specs/checkout/"), hits)
        self.assertTrue(hits[1].startswith("UC-101 AC-7: ") and hits[1].endswith("[proposal 261027-gio-hang]"), hits)
        hits = [ln.split(":")[0] for ln in self.check(("--tim", "đơn"), 0).stdout.splitlines()]
        self.assertEqual(hits, ["UC-101 AC-1", "UC-101 AC-2", "UC-109 AC-1", "UC-110 AC-5"])  # by UC number
        self.assertNotIn("261001-cu", self.check(("--tim", "phút"), 0).stdout)  # archive is not searched
        self.check(("--tim", "ví dụ trong khối"), 1)  # fenced example is not an AC


class Duplicates(Repo):
    def test_duplicate_uc_files_exit_1_in_every_mode(self):
        a = self.uc101("specs/checkout/UC-101-dat-hang.md")
        b = self.uc101("specs/kho/UC-101-giu-hang.md")
        self.put("specs/kho/UC-120-khac.md",
                 "# UC-120\n- Status: implemented\n\n## Acceptance Criteria\n\n### AC-1: Kiểm kê\n- Then ok\n")
        for args in (("UC-101",), ("UC-101", "AC-1"), ("--tim", "giữ hàng")):
            self.check(args, 1, "trùng mã UC-101", a, b)
        self.check(("--tim", "kiểm kê"), 0)  # duplicate UC not among the hits
        res = self.check(("--tim", "then"), 1, "trùng mã UC-101", "UC-120 AC-1: Kiểm kê")  # other hits still shown
        self.assertNotIn("UC-101 AC-", res.stdout)

    def test_changes_and_template_folders_are_not_uc_files(self):
        self.uc101()
        for rel in ("specs/changes/261027-x/UC-101-moi.md", "specs/_templates/UC-101.md",
                    "specs/templates/UC-101-mau.md", "specs/changes/archive/261001-y/UC-101-cu.md"):
            self.uc101(rel)
        self.assertNotIn("trùng", self.check(("UC-101", "AC-1"), 0).stdout)


class Arguments(Repo):
    def test_bad_arguments_exit_2_with_usage(self):
        self.uc101()
        for args in (("XX-1",), ("UC-101", "AC2"), ("UC-101", "ac-1"), (), ("UC-101", "AC-1", "AC-2"),
                     ("UC-101", "--tim", "x"), ("--tim", "  ")):
            res = self.ac(*args)
            self.assertEqual(res.returncode, 2, str(args) + res.stdout + res.stderr)
            self.assertIn("ac.py <UC-ID> [AC-n]", res.stdout + res.stderr)
        self.config(uc="'UC-\\d{3}'")
        self.check(("UC-1", "AC-1"), 2)

    def test_repo_not_initialised_or_missing_specs_dir_exits_2(self):
        for missing in ("README.md", "mk-specs.yml"):
            self.config()
            os.remove(os.path.join(self.root, "specs", missing))
            self.check(("UC-101", "AC-1"), 2, "cần repo mk-specs mức 4 đã init", "specs/" + missing)
        self.config(text="specs_dir: docs/khong-co\n")
        self.check(("UC-101", "AC-1"), 2, "specs_dir 'docs/khong-co' không tồn tại — sửa specs/mk-specs.yml")

    def test_root_defaults_to_cwd(self):
        self.uc101()
        res = run("UC-101", "AC-1", cwd=self.root)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("specs/checkout/UC-101-dat-hang.md", res.stdout)

    def test_specs_dir_and_uc_pattern_come_from_config(self):
        self.config(text="specs_dir: docs/specs\nids:\n  uc: 'ORD-\\d{2}'\n")
        self.put("docs/specs/ban/ORD-12-dat.md", UC_101.format(status="implemented").replace("UC-101", "ORD-12"))
        self.check(("ORD-12", "AC-1"), 0, "docs/specs/ban/ORD-12-dat.md")
        self.check(("UC-101", "AC-1"), 2)

    def test_hostile_uc_pattern_falls_back_to_default(self):
        self.uc101()
        for hostile in ("'([A-Z0-9]+)+Z'", "'(A|A)+Z'", "'" + "U" * 201 + "'"):
            self.config(text=f"ids:\n  uc: {hostile}\n")
            start = time.monotonic()
            self.check(("UC-101", "AC-1"), 0)
            self.assertLess(time.monotonic() - start, 5, hostile)

    def test_uc_pattern_with_counted_repeat_of_a_quantified_group_cannot_hang(self):
        self.put("specs/x/" + "a" * 31 + ".md", "# x\n")
        self.config(text="ids:\n  uc: '(a+){20}b'\n")
        start = time.monotonic()
        self.check(("--tim", "x"), 1)
        self.assertLess(time.monotonic() - start, 5)


if __name__ == "__main__":
    unittest.main()
