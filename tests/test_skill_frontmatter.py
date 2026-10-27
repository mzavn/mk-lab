"""Every skill in skills/ must load in agents that follow the Agent Skills format."""
import glob
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def front(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""


class SkillFrontmatter(unittest.TestCase):
    def test_each_skill_has_matching_name_and_description_within_limit(self):
        paths = sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")))
        self.assertGreaterEqual(len(paths), 2)
        for path in paths:
            folder = os.path.basename(os.path.dirname(path))
            fm = front(path)
            with self.subTest(skill=folder):
                name = re.search(r"^name: (.*)$", fm, re.M)
                desc = re.search(r"^description: '(.*)'$", fm, re.M)
                self.assertIsNotNone(name, "thiếu name")
                self.assertEqual(name.group(1).strip(), folder.replace("mk-", "mk:", 1))
                self.assertIsNotNone(desc, "description phải là một dòng trong dấu nháy đơn")
                self.assertLessEqual(len(desc.group(1).replace("''", "'")), 1024)
                self.assertRegex(fm, r'(?m)^  version: "\d+\.\d+\.\d+"$')


if __name__ == "__main__":
    unittest.main()
