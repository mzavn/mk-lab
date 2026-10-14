"""Installer tests (repo only, not shipped in the skill). Run: python3 -m unittest discover -s tests"""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALL = os.path.join(ROOT, "install.sh")


def version(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip().startswith("version:"):
                return line.split(":", 1)[1].strip().strip('"')
    return None


class PipedBootstrap(unittest.TestCase):
    """`curl … | bash` must install from the official clone, never from whatever sits in the current directory."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(self.home)
        # Upstream = a clone of this checkout with its own skill version.
        self.upstream = os.path.join(self.tmp, "upstream")
        subprocess.run(["git", "clone", "-q", ROOT, self.upstream], check=True)
        # Hostile working directory that ships its own skill.
        self.cwd = os.path.join(self.tmp, "repo", "skills", "mk-specs")
        os.makedirs(self.cwd)
        with open(os.path.join(self.cwd, "SKILL.md"), "w", encoding="utf-8") as fh:
            fh.write('---\nname: mk-specs\nmetadata:\n  version: "9.9.9"\n---\nfake\n')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_piped_run_ignores_skill_in_current_directory(self):
        with open(INSTALL, "rb") as fh:
            script = fh.read()
        env = {**os.environ, "HOME": self.home, "MK_SKILLS_HOME": os.path.join(self.tmp, "clone"),
               "MK_SKILLS_REPO": self.upstream, "MK_SKILLS_NO_UPDATE_CHECK": "1"}
        res = subprocess.run(["bash", "-s", "--", "--global"], input=script, cwd=os.path.join(self.tmp, "repo"),
                             capture_output=True, env=env)
        self.assertEqual(res.returncode, 0, res.stderr.decode())
        installed = version(os.path.join(self.home, ".claude", "skills", "mk-specs", "SKILL.md"))
        self.assertEqual(installed, version(os.path.join(self.upstream, "skills", "mk-specs", "SKILL.md")))
        self.assertNotEqual(installed, "9.9.9")

    def test_installer_parses_on_system_bash(self):
        for bash in ("bash", "/bin/bash"):
            if shutil.which(bash) or os.path.exists(bash):
                self.assertEqual(subprocess.run([bash, "-n", INSTALL]).returncode, 0, bash)


if __name__ == "__main__":
    unittest.main()
