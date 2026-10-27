"""Every skill in skills/ must load in agents that follow the Agent Skills format, and the AGENTS.md block names it."""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def front(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""


def skill_names():
    return sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")))


class SkillFrontmatter(unittest.TestCase):
    def test_each_skill_has_matching_name_and_description_within_limit(self):
        names = skill_names()
        self.assertGreaterEqual(len(names), 2)
        for folder in names:
            fm = front(os.path.join(ROOT, "skills", folder, "SKILL.md"))
            with self.subTest(skill=folder):
                name = re.search(r"^name: (.*)$", fm, re.M)
                desc = re.search(r"^description: '(.*)'$", fm, re.M)
                self.assertIsNotNone(name, "thiếu name")
                self.assertEqual(name.group(1).strip(), folder.replace("mk-", "mk:", 1))
                self.assertIsNotNone(desc, "description phải là một dòng trong dấu nháy đơn")
                self.assertLessEqual(len(desc.group(1).replace("''", "'")), 1024)
                self.assertRegex(fm, r'(?m)^  version: "\d+\.\d+\.\d+"$')


class AgentsBlockNamesTheSuite(unittest.TestCase):
    """UC-102 AC-16: the mk-specs block in AGENTS.md lists every sibling skill of the checkout exactly once."""

    def setUp(self):
        self.proj = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.proj, ignore_errors=True)

    def run_files(self):
        script = os.path.join(ROOT, "skills", "mk-specs", "scripts", "agent-files.py")
        res = subprocess.run([sys.executable, script, self.proj], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stderr)
        return res.stdout

    def test_block_has_one_line_per_sibling_skill_and_the_priority_rule(self):
        self.run_files()
        with open(os.path.join(self.proj, "AGENTS.md"), encoding="utf-8") as fh:
            block = fh.read()
        siblings = [n for n in skill_names() if n != "mk-specs"]
        self.assertGreaterEqual(len(siblings), 4)
        for name in siblings:
            with self.subTest(skill=name):
                self.assertEqual(len(re.findall(rf"^- `{re.escape(name)}`:", block, re.M)), 1)
        self.assertIn("đã cài thì dùng trước skill khác cùng việc", block)
        self.assertIn("AGENTS.md (unchanged)", self.run_files())


if __name__ == "__main__":
    unittest.main()
