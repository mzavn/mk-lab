"""UC-001: init.py tạo khung skill mk-<tên> từ mẫu, không ghi đè, khung điền xong qua được validate.py."""
import os
import re
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import INIT, VALIDATE, run, snapshot  # noqa: E402


class InitBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.skills = os.path.join(self.tmp, "skills")
        os.mkdir(self.skills)


class InitCreate(InitBase):
    def test_ac1_creates_skeleton_with_frontmatter_and_sections(self):
        res = run(INIT, "ghi-chu", "--path", self.skills)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        target = os.path.join(self.skills, "mk-ghi-chu")
        self.assertIn(f"Đã tạo: {target}", res.stdout)
        self.assertEqual(sorted(os.listdir(target)), ["SKILL.md"])
        with open(os.path.join(target, "SKILL.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertTrue(text.startswith("---\nname: mk:ghi-chu\n"))
        self.assertIn("\nlicense: MIT\n", text)
        self.assertIn("\n  author: mzavn\n", text)
        self.assertIn('\n  version: "0.1.0"\n', text)
        for part in ("**Phạm vi.**", "**Không**", "## Trả lời người dùng", "## Chính sách an toàn", "## Tài liệu"):
            self.assertIn(part, text)
        self.assertRegex(text, r"## Bước 1 ")
        self.assertRegex(text, r"\{\{[A-Z0-9_]+")
        self.assertNotIn("{{TEN}}", text)


class InitRefuses(InitBase):
    def test_ac2_existing_target_is_never_overwritten(self):
        target = os.path.join(self.skills, "mk-ghi-chu")
        os.mkdir(target)
        with open(os.path.join(target, "SKILL.md"), "w", encoding="utf-8") as fh:
            fh.write("bản cũ của tôi\n")
        before = snapshot(self.skills)
        res = run(INIT, "ghi-chu", "--path", self.skills)
        self.assertEqual(res.returncode, 1)
        self.assertRegex(res.stdout, r"^Lỗi: .*mk-ghi-chu đã có — không ghi đè")
        self.assertEqual(snapshot(self.skills), before)

    def test_ac2_existing_file_or_symlink_even_broken_is_refused(self):
        target = os.path.join(self.skills, "mk-ghi-chu")
        for kind in ("file", "link", "broken"):
            with self.subTest(kind=kind):
                if kind == "file":
                    with open(target, "w", encoding="utf-8") as fh:
                        fh.write("x")
                elif kind == "link":
                    os.mkdir(os.path.join(self.tmp, "that"))
                    os.symlink(os.path.join(self.tmp, "that"), target)
                else:
                    os.symlink(os.path.join(self.tmp, "nowhere"), target)
                res = run(INIT, "ghi-chu", "--path", self.skills)
                self.assertEqual(res.returncode, 1)
                self.assertIn("đã có — không ghi đè", res.stdout)
                if kind == "link":
                    self.assertEqual(os.listdir(os.path.join(self.tmp, "that")), [])
                os.remove(target)

    def test_ac3_bad_names_are_refused_without_creating_anything(self):
        for name in ("Ghi_Chu", "mk-ghi-chu", "mk:ghi-chu", "-a", "a--b", "", "ghi chu", "ghi-"):
            with self.subTest(name=name):
                res = run(INIT, "--path", self.skills, "--", name)
                self.assertEqual(res.returncode, 1, res.stdout)
                self.assertTrue(res.stdout.startswith("Lỗi: "), res.stdout)
                self.assertEqual(os.listdir(self.skills), [])

    def test_ac3_bad_path_is_refused(self):
        file_path = os.path.join(self.tmp, "a-file")
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write("x")
        link = os.path.join(self.tmp, "link-to-skills")
        os.symlink(self.skills, link)
        cases = {os.path.join(self.tmp, "khong-co"): "không có thư mục", file_path: "không phải thư mục",
                 link: "symlink", link + "/": "symlink"}
        for path, msg in cases.items():
            with self.subTest(path=path[len(self.tmp):]):
                res = run(INIT, "ghi-chu", "--path", path)
                self.assertEqual(res.returncode, 1)
                self.assertTrue(res.stdout.startswith("Lỗi: "))
                self.assertIn(msg, res.stdout)
        self.assertEqual(os.listdir(self.skills), [])

    def test_ac3_missing_path_option_exits_1(self):
        res = run(INIT, "ghi-chu")
        self.assertEqual(res.returncode, 1)
        self.assertTrue(res.stdout.startswith("Lỗi: "))


class InitThenValidate(InitBase):
    def test_ac4_skeleton_fails_until_placeholders_are_filled_then_passes(self):
        self.assertEqual(run(INIT, "ghi-chu", "--path", self.skills).returncode, 0)
        target = os.path.join(self.skills, "mk-ghi-chu")
        res = run(VALIDATE, target)
        self.assertEqual(res.returncode, 1)
        self.assertRegex(res.stdout, r"LỖI: nội dung — SKILL.md:\d+ còn chỗ trống mẫu")

        path = os.path.join(target, "SKILL.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        fills = {
            "MO_TA": 'Turn a messy note into a checklist. Use mk:ghi-chu when the user says "gom ghi chú".',
            "TIEU_DE": "gom ghi chú", "LUONG": "Đọc ghi chú → ghi checklist ra file mới",
            "XU_LY": "một file ghi chú", "KHONG_XU_LY": "gửi checklist đi",
            "BUOC_DOC": "Đọc file người dùng đưa.", "BUOC_LAM": "Ghi checklist ra file mới.",
        }
        text = re.sub(r"\{\{([A-Z0-9_]+)[^}]*\}\}", lambda m: fills.get(m.group(1), m.group(0)), text)
        text = re.sub(r"\n## Tài liệu\n.*\Z", "\n", text, flags=re.S)  # chưa có file nào: xoá bảng như mẫu dặn
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        res = run(VALIDATE, target)
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertTrue(res.stdout.rstrip().endswith("Kết quả: 0 lỗi"))


if __name__ == "__main__":
    unittest.main()
