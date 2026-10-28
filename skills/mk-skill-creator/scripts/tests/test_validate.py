"""UC-002: validate.py kiểm cơ học một skill theo bộ chuẩn — dòng OK/LỖI, thoát 0/1, chỉ đọc, tất định."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import GOOD_SKILL, VALIDATE, make_good, run, snapshot, write  # noqa: E402

HOME = "/" + "Users/lan/du-an"  # đường dẫn máy cá nhân giả, chia đôi để không tự khớp


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = make_good(self.tmp)

    def set_skill(self, old, new):
        path = os.path.join(self.root, "SKILL.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn(old, text)
        write(path, text.replace(old, new, 1))

    def check(self, expect_exit=1):
        res = run(VALIDATE, self.root)
        self.assertEqual(res.returncode, expect_exit, res.stdout + res.stderr)
        self.assertEqual(res.stderr, "")
        return res.stdout

    def assertError(self, out, group, text):
        lines = [ln for ln in out.splitlines() if ln.startswith(f"LỖI: {group} — ")]
        self.assertTrue(any(text in ln for ln in lines), f"không thấy LỖI {group} chứa {text!r} trong:\n{out}")


class Passing(Base):
    def test_ac1_good_skill_prints_only_ok_lines_and_exits_0(self):
        out = self.check(0)
        lines = out.splitlines()
        self.assertEqual([ln.split(" (")[0] for ln in lines[:-1]],
                         ["OK: tên thư mục", "OK: frontmatter", "OK: cấu trúc", "OK: số dòng", "OK: nội dung", "OK: scripts"])
        self.assertEqual(lines[-1], "Kết quả: 0 lỗi")

    def test_ac1_skill_without_scripts_or_references_passes(self):
        shutil.rmtree(os.path.join(self.root, "scripts"))
        shutil.rmtree(os.path.join(self.root, "references"))
        self.set_skill("Đọc `references/cach-gom.md`, chạy `python3 <skill>/scripts/gom.py <file>`.", "Đọc file.")
        self.assertIn("OK: scripts (không có script)", self.check(0))


class NameAndFrontmatter(Base):
    def test_ac2_bad_folder_name(self):
        bad = os.path.join(self.tmp, "Ghi_Chu")
        os.rename(self.root, bad)
        self.root = bad
        self.assertError(self.check(), "tên thư mục", "phải dạng mk-<tên>")

    def test_ac2_missing_frontmatter(self):
        write(os.path.join(self.root, "SKILL.md"), GOOD_SKILL.split("---\n", 2)[2])
        self.assertError(self.check(), "frontmatter", "không mở đầu bằng khối ---")

    def test_ac2_name_must_match_folder_with_one_colon(self):
        for bad in ("mk:ghi-chep", "mk:ghi:chu", "ghi-chu"):
            with self.subTest(name=bad):
                self.setUp()
                self.set_skill("name: mk:ghi-chu", f"name: {bad}")
                self.assertError(self.check(), "frontmatter", f"name '{bad}'")

    def test_ac2_missing_fields(self):
        cases = {"license: MIT\n": "thiếu 'license'", "  author: mzavn\n": "thiếu metadata.author",
                 '  version: "0.1.0"\n': "thiếu metadata.version"}
        for line, msg in cases.items():
            with self.subTest(missing=line.strip()):
                self.setUp()
                self.set_skill(line, "")
                self.assertError(self.check(), "frontmatter", msg)
        self.setUp()
        self.set_skill("description: '", "summary: '")
        out = self.check()
        self.assertError(out, "frontmatter", "thiếu 'description'")
        self.assertError(out, "frontmatter", "khoá 'summary' không thuộc chuẩn")

    def test_ac2_description_rules(self):
        cases = {
            "length": ("description: 'Turn", "description: '" + "x" * 1100 + " Turn", "ký tự (tối đa 1024)"),
            "no name": ("Use mk:ghi-chu whenever", "Use it whenever", "không có chữ 'mk:ghi-chu'"),
            "block": ("description: 'Turn", "description: >\n  'Turn", "phải là một dòng"),
            "folded": ("checklist\".'\n", "checklist\".'\n  more text\n", "phải là một dòng"),
            "plain colon": ("description: 'Turn a messy Vietnamese note into a tidy checklist file. Use mk:ghi-chu "
                            "whenever the user says \"gom ghi chú\", \"làm checklist\".'",
                            "description: Use mk:ghi-chu: gom ghi chú", "không đặt trong nháy"),
        }
        for label, (old, new, msg) in cases.items():
            with self.subTest(case=label):
                self.setUp()
                self.set_skill(old, new)
                self.assertError(self.check(), "frontmatter", msg)

    def test_ac2_license_author_version(self):
        cases = {"license: MIT": ("license: Apache-2.0", "license phải là MIT"),
                 "author: mzavn": ("author: lan", "metadata.author phải là mzavn"),
                 'version: "0.1.0"': ("version: 0.1.0", 'metadata.version phải dạng "X.Y.Z"')}
        for old, (new, msg) in cases.items():
            with self.subTest(field=old):
                self.setUp()
                self.set_skill(old, new)
                self.assertError(self.check(), "frontmatter", msg)

    def test_ac2_optional_keys_are_allowed(self):
        self.set_skill("license: MIT\n", "license: MIT\nallowed-tools: Read\nhooks:\n  PreToolUse: []\n")
        self.check(0)

    def test_ac2_bom_is_an_error(self):
        write(os.path.join(self.root, "SKILL.md"), "\ufeff" + GOOD_SKILL)
        self.assertError(self.check(), "frontmatter", "BOM")


class Structure(Base):
    def test_ac3_unknown_top_level_entry(self):
        write(os.path.join(self.root, "docs", "ghi-chu.md"), "x\n")
        write(os.path.join(self.root, "README.md"), "x\n")
        out = self.check()
        self.assertError(out, "cấu trúc", "'README.md' không thuộc cấu trúc")
        self.assertError(out, "cấu trúc", "'docs' không thuộc cấu trúc")

    def test_ac3_junk_outside_git_is_an_error(self):
        write(os.path.join(self.root, "scripts", "__pycache__", "gom.cpython-39.pyc"), "x")
        write(os.path.join(self.root, ".DS_Store"), "x")
        out = self.check()
        self.assertError(out, "cấu trúc", "file rác scripts/__pycache__/")
        self.assertError(out, "cấu trúc", "file rác .DS_Store")

    def test_ac3_junk_ignored_by_git_is_skipped_but_tracked_junk_is_not(self):
        if shutil.which("git") is None:
            self.skipTest("không có git")
        git = ["git", "-C", self.tmp]
        subprocess.run(git + ["init", "-q"], check=True)
        write(os.path.join(self.tmp, ".gitignore"), "__pycache__/\n.DS_Store\n")
        write(os.path.join(self.root, "scripts", "__pycache__", "gom.cpython-39.pyc"), "x")
        write(os.path.join(self.root, ".DS_Store"), "x")
        out = self.check(0)
        self.assertIn("bỏ qua 2 file rác git đã loại", out)
        subprocess.run(git + ["add", "-f", os.path.join(self.root, ".DS_Store")], check=True)
        self.assertError(self.check(), "cấu trúc", "file rác .DS_Store")

    def test_ac3_line_limit(self):
        write(os.path.join(self.root, "references", "cach-gom.md"), "dòng\n" * 300)
        self.assertError(self.check(), "số dòng", "references/cach-gom.md 300 dòng (giới hạn < 300)")
        write(os.path.join(self.root, "references", "cach-gom.md"), "dòng\n" * 299)
        self.check(0)

    def test_ac3_other_markdown_limit_is_400(self):
        self.set_skill("Đọc `references/cach-gom.md`", "Đọc `references/cach-gom.md`, chép `assets/mau.md`")
        write(os.path.join(self.root, "assets", "mau.md"), "dòng\n" * 399)
        self.check(0)
        write(os.path.join(self.root, "assets", "mau.md"), "dòng\n" * 400)
        self.assertError(self.check(), "số dòng", "assets/mau.md 400 dòng (giới hạn < 400)")

    def test_ac3_symlink_inside_skill_is_an_error_and_not_followed(self):
        outside = os.path.join(self.tmp, "ngoai.md")
        write(outside, f"bí mật ở {HOME}\n")
        os.symlink(outside, os.path.join(self.root, "references", "lien-ket.md"))
        out = self.check()
        self.assertError(out, "cấu trúc", "references/lien-ket.md là symlink")
        self.assertNotIn("máy cá nhân", out)

    def test_ac3_third_party_notices_file_is_allowed_at_root(self):
        write(os.path.join(self.root, "THIRD_PARTY_NOTICES.md"), "# Thông báo\n")
        self.check(0)

    def test_ac3_installed_copy_with_installer_files_passes(self):
        for name in (".mk-specs-manifest", ".mk-specs-source", ".mk-studio-manifest", ".mk-studio-source"):
            write(os.path.join(self.root, name), "x\n")
        self.check(0)

    def test_ac3_skill_ignored_entirely_by_git_is_checked_like_outside_git(self):
        if shutil.which("git") is None:
            self.skipTest("không có git")
        subprocess.run(["git", "-C", self.tmp, "init", "-q"], check=True)
        write(os.path.join(self.tmp, ".gitignore"), "mk-ghi-chu/\n")
        write(os.path.join(self.root, ".DS_Store"), "x")
        self.assertError(self.check(), "cấu trúc", "file rác .DS_Store")


class Content(Base):
    def test_ac4_personal_path_in_any_text_file(self):
        write(os.path.join(self.root, "references", "cach-gom.md"), f"# Cách gom\n\nMở {HOME}/note.md\n")
        self.assertError(self.check(), "nội dung", "references/cach-gom.md:3 có đường dẫn máy cá nhân")

    def test_ac4_missing_mentioned_paths(self):
        self.set_skill("Đọc `references/cach-gom.md`", "Đọc `references/khong-co.md` và `assets/mau/`")
        out = self.check()
        self.assertError(out, "nội dung", "SKILL.md:18 nhắc references/khong-co.md nhưng không có")
        self.assertError(out, "nội dung", "nhắc assets/mau/ nhưng không có")

    def test_ac4_mention_of_a_sibling_skill_file_is_fine_only_if_exactly_one_sibling_has_it(self):
        self.set_skill("Đọc `references/cach-gom.md`", "Đọc `references/cach-gom.md`, mẫu `assets/templates/proposal.md`")
        self.assertError(self.check(), "nội dung", "nhắc assets/templates/proposal.md nhưng không có")
        other = make_good(self.tmp, "mk-spec-gia")
        write(os.path.join(other, "assets", "templates", "proposal.md"), "x\n")
        self.check(0)
        third = make_good(self.tmp, "mk-spec-gia-2")
        write(os.path.join(third, "assets", "templates", "proposal.md"), "x\n")
        self.assertError(self.check(), "nội dung", "nhắc assets/templates/proposal.md nhưng không có")

    def test_ac4_path_prefix_rules(self):
        write(os.path.join(self.root, "references", "cach-gom.md"),
              "Xem `../scripts/gom.py`, `../assets/khong-co.md`, `src/references/a.md`, `references/<tên>.md`.\n")
        out = self.check()
        self.assertError(out, "nội dung", "references/cach-gom.md:1 nhắc ../assets/khong-co.md nhưng không có")
        self.assertNotIn("src/references", out)
        self.assertNotIn("<tên>", out)
        self.assertNotIn("../scripts/gom.py", out)

    def test_ac4_missing_sections_and_placeholders(self):
        cases = {
            "**Phạm vi.**": ("**Phạm vi.** Skill xử lý: một file ghi chú markdown. **Không** xử lý",
                             "Skill xử lý: một file ghi chú markdown. Không xử lý", "thiếu đoạn **Phạm vi.**"),
            "**Không**": ("**Không** xử lý", "Không xử lý", "thiếu phần **Không** xử lý"),
            "trả lời": ("## Trả lời người dùng", "## Cách nói", "thiếu mục '## Trả lời người dùng'"),
            "an toàn": ("## Chính sách an toàn", "## An toàn", "thiếu mục '## Chính sách an toàn'"),
            "chỗ trống": ("1. Đọc `references", "1. {{BUOC_1: đọc gì}} `references", "còn chỗ trống mẫu {{BUOC_1:"),
        }
        for label, (old, new, msg) in cases.items():
            with self.subTest(case=label):
                self.setUp()
                self.set_skill(old, new)
                self.assertError(self.check(), "nội dung", msg)


class Orphans(Base):
    def test_ac4_reference_not_named_in_skill_md(self):
        write(os.path.join(self.root, "references", "le.md"), "# Lẻ\n")
        self.assertError(self.check(), "nội dung", "references/le.md không được SKILL.md nhắc")

    def test_ac4_asset_owned_by_mention_folder_or_script(self):
        write(os.path.join(self.root, "assets", "mau.md"), "x\n")
        self.assertError(self.check(), "nội dung", "assets/mau.md không được SKILL.md, reference hay script nào nhắc")
        write(os.path.join(self.root, "references", "cach-gom.md"), "Chép `../assets/mau.md`.\n")
        self.check(0)
        write(os.path.join(self.root, "references", "cach-gom.md"), "# Cách gom\n")
        write(os.path.join(self.root, "scripts", "gom.py"), "import sys\n\nsys.dont_write_bytecode = True\nMAU = \"mau.md\"\n")
        self.check(0)


class Scripts(Base):
    def test_ac5_non_stdlib_import(self):
        write(os.path.join(self.root, "scripts", "gom.py"), "import sys\nimport requests\nfrom yaml import load\n"
              "import json, helper_x\nsys.dont_write_bytecode = True\n")
        write(os.path.join(self.root, "scripts", "helper_x.py"), "X = 1\n")
        out = self.check()
        self.assertError(out, "scripts", "scripts/gom.py:2 import 'requests' không thuộc thư viện chuẩn")
        self.assertError(out, "scripts", "scripts/gom.py:3 import 'yaml'")
        self.assertNotIn("'json'", out)
        self.assertNotIn("'helper_x'", out)

    def test_ac5_syntax_error(self):
        write(os.path.join(self.root, "scripts", "gom.py"), "def x(:\n")
        self.assertError(self.check(), "scripts", "scripts/gom.py:1 lỗi cú pháp")

    def test_ac5_entry_script_without_no_bytecode(self):
        write(os.path.join(self.root, "scripts", "gom.py"), "def main():\n    pass\n\n\nif __name__ == \"__main__\":\n    main()\n")
        self.assertError(self.check(), "scripts", "scripts/gom.py chạy được như lệnh mà thiếu 'sys.dont_write_bytecode = True'")
        write(os.path.join(self.root, "scripts", "gom.py"), "X = 1\n")  # mô-đun dùng chung, không chạy như lệnh
        self.check(0)

    def test_ac5_scripts_need_tests(self):
        shutil.rmtree(os.path.join(self.root, "scripts", "tests"))
        self.assertError(self.check(), "scripts", "có script nhưng không có scripts/tests/test_*.py")

    def test_ac5_test_files_do_not_need_the_no_bytecode_flag(self):
        write(os.path.join(self.root, "scripts", "tests", "test_gom.py"),
              "import unittest\n\n\nclass Gom(unittest.TestCase):\n    def test_x(self):\n        pass\n\n\n"
              "if __name__ == \"__main__\":\n    unittest.main()\n")
        self.check(0)

    def test_ac3_symlinks_in_scripts_are_errors_without_crashing(self):
        os.symlink(os.path.join(self.tmp, "khong-co.py"), os.path.join(self.root, "scripts", "hong.py"))
        os.mkdir(os.path.join(self.tmp, "thu-muc"))
        os.symlink(os.path.join(self.tmp, "thu-muc"), os.path.join(self.root, "scripts", "thu-muc.py"))
        out = self.check()
        self.assertError(out, "cấu trúc", "scripts/hong.py là symlink")
        self.assertError(out, "cấu trúc", "scripts/thu-muc.py là symlink")

    def test_ac3_unreadable_file_is_an_error_without_crashing(self):
        if os.geteuid() == 0:
            self.skipTest("root đọc được mọi file")
        path = os.path.join(self.root, "references", "cach-gom.md")
        os.chmod(path, 0)
        self.addCleanup(os.chmod, path, 0o644)
        self.assertError(self.check(), "cấu trúc", "references/cach-gom.md không đọc được")


class Hostile(Base):
    """Skill lạ không làm validate treo, văng lỗi, chạy lệnh hay lặp lại dữ liệu cá nhân."""

    def test_fifo_is_reported_not_opened(self):
        os.mkfifo(os.path.join(self.root, "references", "ong.md"))
        res = run(VALIDATE, self.root)  # không treo: không mở FIFO
        self.assertEqual(res.returncode, 1)
        self.assertIn("references/ong.md không phải file thường", res.stdout)

    def test_long_blank_script_is_checked_fast(self):
        import time
        write(os.path.join(self.root, "scripts", "gom.py"),
              "import sys\n" + "\n" * 100000 + "sys.dont_write_bytecode = True\nif __name__ == \"__main__\":\n    pass\n")
        start = time.monotonic()
        self.check(0)
        self.assertLess(time.monotonic() - start, 5)

    def test_control_characters_from_file_names_are_not_printed(self):
        write(os.path.join(self.root, "la\x1b[2J.txt"), "x\n")
        out = self.check()
        self.assertNotIn("\x1b", out)
        self.assertIn("'la?[2J.txt' không thuộc cấu trúc", out)

    def test_personal_path_value_is_not_echoed(self):
        write(os.path.join(self.root, "references", "cach-gom.md"), f"Mở {HOME}/note.md\n")
        out = self.check()
        self.assertNotIn("lan", out)
        self.assertIn("dạng /Users/<tên>", out)

    def test_repo_fsmonitor_command_is_not_run(self):
        if shutil.which("git") is None:
            self.skipTest("không có git")
        mark = os.path.join(self.tmp, "da-chay")
        hook = os.path.join(self.tmp, "hook.sh")
        write(hook, f"#!/bin/sh\ntouch {mark}\n")
        os.chmod(hook, 0o755)
        subprocess.run(["git", "-C", self.tmp, "init", "-q"], check=True)
        subprocess.run(["git", "-C", self.tmp, "config", "core.fsmonitor", hook], check=True)
        self.check(0)
        self.assertFalse(os.path.exists(mark))


class Prefixes(Base):
    def test_ac4_install_path_prefixes_point_to_this_skill(self):
        for prefix in (".claude/skills/mk-ghi-chu/", "~/.agents/skills/mk-ghi-chu/"):
            with self.subTest(prefix=prefix):
                self.setUp()
                self.set_skill("Đọc `references/cach-gom.md`", f"Đọc `{prefix}references/cach-gom.md` và `{prefix}references/x.md`")
                out = self.check()
                self.assertError(out, "nội dung", f"nhắc {prefix}references/x.md nhưng không có")
                self.assertNotIn("cach-gom.md nhưng", out)

    def test_ac4_scope_paragraph_may_wrap_onto_the_next_line(self):
        self.set_skill("một file ghi chú markdown. **Không** xử lý", "một file ghi chú markdown.\n**Không** xử lý")
        self.check(0)
        self.set_skill("markdown.\n**Không** xử lý", "markdown.\n \n**Không** xử lý")
        self.assertError(self.check(), "nội dung", "thiếu phần **Không** xử lý")


class Calling(Base):
    def test_ac6_bad_target(self):
        file_path = os.path.join(self.root, "SKILL.md")
        no_skill = os.path.join(self.tmp, "mk-trong")
        os.mkdir(no_skill)
        for target, msg in ((os.path.join(self.tmp, "khong-co"), "không có"), (file_path, "không phải thư mục"),
                            (no_skill, "không có file SKILL.md")):
            with self.subTest(target=os.path.basename(target)):
                res = run(VALIDATE, target)
                self.assertEqual(res.returncode, 1)
                self.assertTrue(res.stdout.startswith("Lỗi: "), res.stdout)
                self.assertIn(msg, res.stdout)
                self.assertNotIn("OK:", res.stdout)
        res = run(VALIDATE)
        self.assertEqual(res.returncode, 1)
        self.assertTrue(res.stdout.startswith("Lỗi: "))

    def test_ac7_deterministic_and_read_only(self):
        write(os.path.join(self.root, "README.md"), "x\n")
        write(os.path.join(self.root, "scripts", "gom.py"), "import requests\nimport yaml\n")
        before = snapshot(self.root)
        first = run(VALIDATE, self.root)
        second = run(VALIDATE, self.root)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.returncode, 1)
        self.assertEqual(snapshot(self.root), before)
        self.assertTrue(first.stdout.rstrip().endswith("Kết quả: 3 lỗi"), first.stdout)


if __name__ == "__main__":
    unittest.main()
