"""UC-403: markdown stays short enough to read whole, every path an agent is told to open exists, every split-out file is
reachable from its parent. Rules live in tests/docs_rules.py; these tests build small repos in a temp dir."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docs_rules as dr  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Tree(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def put(self, rel, text="x\n"):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return rel

    def lines(self, n):
        return "dòng\n" * n

    def all_files(self):
        out = []
        for base, _, names in os.walk(self.root):
            out += [os.path.relpath(os.path.join(base, n), self.root) for n in names]
        return sorted(out)


class LineLimits(Tree):
    def test_skill_text_under_300_other_markdown_under_400_python_free(self):
        files = [
            self.put("skills/a/SKILL.md", self.lines(300)),
            self.put("skills/a/references/ok.md", self.lines(299)),
            self.put("skills/a/references/long.md", self.lines(300)),
            self.put("README.md", self.lines(400)),
            self.put("INSTALL.md", self.lines(399)),
            self.put("skills/a/assets/DEPLOY.md.template", self.lines(400)),
            self.put("skills/a/scripts/big.py", self.lines(900)),
        ]
        problems = dr.line_problems(self.root, files)
        text = "\n".join(problems)
        self.assertIn("skills/a/SKILL.md: 300 dòng (giới hạn < 300)", text)
        self.assertIn("skills/a/references/long.md: 300 dòng (giới hạn < 300)", text)
        self.assertIn("README.md: 400 dòng (giới hạn < 400)", text)
        self.assertIn("skills/a/assets/DEPLOY.md.template: 400 dòng (giới hạn < 400)", text)
        self.assertEqual(len(problems), 4, text)  # ok.md, INSTALL.md, big.py pass


class Paths(Tree):
    def test_broken_paths_are_named_and_placeholders_globs_and_foreign_prefixes_are_skipped(self):
        self.put("skills/a/references/real.md", "Xem `../assets/r.md.template`.\nMở `references/khong-co.md`.\n")
        self.put("skills/a/assets/r.md.template")
        self.put("skills/a/scripts/gen.py")
        self.put("skills/b/assets/templates/proposal.md")
        self.put("skills/a/SKILL.md", "\n".join([
            "Đọc `references/real.md` rồi `references/x.md`.",
            "Chạy `python3 <skill>/scripts/gen.py`, `.claude/skills/a/scripts/gen.py` và `scripts/z.py`.",
            "Mẫu trong `assets/mau/` (chưa có).",
            "Bỏ qua: `references/cloudflare-*.md`, \"$d/scripts/hook.py\", `src/scripts/build.sh`, `<skill>/scripts/…`.",
            "Mẫu của skill khác: `assets/templates/proposal.md`.",
            "flowchart: A[assets/r.md.template] --> B",
        ]) + "\n")
        problems = dr.path_problems(self.root, ["a", "b"])
        text = "\n".join(problems)
        self.assertIn("skills/a/SKILL.md → references/x.md", text)
        self.assertIn("skills/a/SKILL.md → scripts/z.py", text)
        self.assertIn("skills/a/SKILL.md → assets/mau/", text)
        self.assertIn("skills/a/references/real.md → references/khong-co.md", text)
        self.assertEqual(len(problems), 4, text)


class Owners(Tree):
    def test_orphans_are_named_and_every_accepted_owner_form_counts(self):
        self.put("skills/a/SKILL.md", "Đọc `references/dung.md`. Mẫu trong `assets/templates/`: `use-case.md`.\n")
        self.put("skills/a/references/dung.md", "Mẫu `assets/report.md.template`.\n")
        self.put("skills/a/references/moi.md")
        self.put("skills/a/assets/report.md.template")
        self.put("skills/a/assets/templates/use-case.md")
        self.put("skills/a/assets/agents-block.md")
        self.put("skills/a/assets/mau.md")
        self.put("skills/a/scripts/write.py", 'open(os.path.join(SKILL, "assets", "agents-block.md"))\n')
        self.put("skills/a/scripts/tests/test_x.py", '"mau.md"\n')  # tests do not give ownership
        self.put("README.md", "Xem `guide/cai-dat.md`.\n")
        self.put("guide/cai-dat.md")
        self.put("guide/le.md")
        self.put("CHANGELOG.md", "Bản cũ: [v1](changelog/v1.md).\n")
        self.put("changelog/v1.md")
        self.put("changelog/v0.md")
        problems = dr.owner_problems(self.root, ["a"], self.all_files())
        text = "\n".join(problems)
        for orphan in ("skills/a/references/moi.md", "skills/a/assets/mau.md", "guide/le.md", "changelog/v0.md"):
            self.assertIn(f"file mồ côi — agent không lần tới được: {orphan}", text)
        self.assertEqual(len(problems), 4, text)


class CurrentTree(unittest.TestCase):
    def test_repository_passes_every_rule(self):
        out = subprocess.run(["git", "ls-files", "*.md", "*.md.template"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, "cần repo git (UC-403: không có git → lỗi, không bỏ qua)")
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        skills = sorted(n for n in os.listdir(os.path.join(ROOT, "skills"))
                        if os.path.isfile(os.path.join(ROOT, "skills", n, "SKILL.md")))
        problems = (dr.line_problems(ROOT, out.stdout.split()) + dr.path_problems(ROOT, skills)
                    + dr.owner_problems(ROOT, skills, tracked))
        self.assertEqual(problems, [], "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
