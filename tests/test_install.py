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


class SymlinkedDestination(unittest.TestCase):
    """A skill folder that is a symlink is refused, never copied into or deleted through."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.proj = os.path.join(self.tmp, "proj")
        self.elsewhere = os.path.join(self.tmp, "elsewhere")
        os.makedirs(os.path.join(self.proj, ".claude", "skills"))
        os.makedirs(self.elsewhere)
        with open(os.path.join(self.elsewhere, "keep.txt"), "w") as fh:
            fh.write("keep")
        os.symlink(self.elsewhere, os.path.join(self.proj, ".claude", "skills", "mk-specs"))
        subprocess.run(["git", "init", "-q", self.proj], check=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_install_update_and_uninstall_refuse_symlinked_skill_folder(self):
        env = {**os.environ, "HOME": os.path.join(self.tmp, "home")}
        for args in (["--project", self.proj], ["--project", self.proj, "--force"], ["--uninstall", "--project", self.proj]):
            res = subprocess.run(["bash", INSTALL, *args], capture_output=True, text=True, env=env)
            self.assertNotEqual(res.returncode, 0, args)
            self.assertIn("symlink", res.stderr)
        self.assertEqual(os.listdir(self.elsewhere), ["keep.txt"])
        self.assertTrue(os.path.islink(os.path.join(self.proj, ".claude", "skills", "mk-specs")))


class ProjectCopies(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.proj = os.path.join(self.tmp, "proj")
        os.makedirs(self.proj)
        subprocess.run(["git", "init", "-q", self.proj], check=True)
        self.env = {**os.environ, "HOME": os.path.join(self.tmp, "home")}

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def install(self, *args):
        return subprocess.run(["bash", INSTALL, *args], capture_output=True, text=True, env=self.env)

    def test_hand_edit_in_agents_copy_is_not_overwritten(self):
        self.assertEqual(self.install("--project", self.proj, "--agents-dir", "--no-agent-files").returncode, 0)
        skill = os.path.join(self.proj, ".agents", "skills", "mk-specs", "SKILL.md")
        with open(skill, "a", encoding="utf-8") as fh:
            fh.write("\nluật riêng\n")
        res = self.install("--project", self.proj, "--no-agent-files")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn(".agents/skills/mk-specs", res.stderr)
        with open(skill, encoding="utf-8") as fh:
            self.assertIn("luật riêng", fh.read())

    def test_symlinked_parent_inside_project_is_refused(self):
        target = os.path.join(self.tmp, "global-skills")
        os.makedirs(os.path.join(target, "mk-specs"))
        with open(os.path.join(target, "mk-specs", "keep.txt"), "w") as fh:
            fh.write("keep")
        os.makedirs(os.path.join(self.proj, ".claude"))
        os.symlink(target, os.path.join(self.proj, ".claude", "skills"))
        for args in (["--project", self.proj], ["--uninstall", "--project", self.proj]):
            res = self.install(*args, "--no-agent-files")
            self.assertNotEqual(res.returncode, 0, args)
            self.assertIn("symlink", res.stderr)
        self.assertEqual(os.listdir(os.path.join(target, "mk-specs")), ["keep.txt"])

    def test_uninstall_when_nothing_installed_says_so(self):
        res = self.install("--uninstall", "--project", self.proj, "--no-agent-files")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("not installed", res.stdout)
        self.assertNotIn("removed", res.stdout)


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
