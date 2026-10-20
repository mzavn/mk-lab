"""Installer tests (repo only, not shipped in the skill). Run: python3 -m unittest discover -s tests"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALL = os.path.join(ROOT, "install.sh")
# macOS ships bash 3.2 as /bin/bash: the multi-skill tests install for real with it (empty arrays under `set -u`).
BASH = "/bin/bash" if os.path.exists("/bin/bash") else "bash"
GIT_ID = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
          "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}
MANIFEST = ".mk-specs-manifest"
SOURCE_FILE = ".mk-specs-source"


def version(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip().startswith("version:"):
                return line.split(":", 1)[1].strip().strip('"')
    return None


def write_skill(checkout, name, ver):
    """A minimal skill: the installer tests must not depend on the content of any skill but mk-specs."""
    os.makedirs(os.path.join(checkout, "skills", name, "references"), exist_ok=True)
    with open(os.path.join(checkout, "skills", name, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write(f'---\nname: {name}\ndescription: test skill\nmetadata:\n  version: "{ver}"\n---\n# {name}\n')
    with open(os.path.join(checkout, "skills", name, "references", "a.md"), "w", encoding="utf-8") as fh:
        fh.write("a\n")


def set_version(skill_md, ver):
    with open(skill_md, encoding="utf-8") as fh:
        text = fh.read()
    with open(skill_md, "w", encoding="utf-8") as fh:
        fh.write(re.sub(r'^(\s*version:\s*)"[^"]*"', rf'\g<1>"{ver}"', text, count=1, flags=re.M))


def make_checkout(path):
    """Copy of the working tree's installer and mk-specs (uncommitted code included) plus a fake second skill `star`."""
    os.makedirs(os.path.join(path, "skills"))
    shutil.copy2(INSTALL, path)
    shutil.copytree(os.path.join(ROOT, "skills", "mk-specs"), os.path.join(path, "skills", "mk-specs"),
                    ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
    write_skill(path, "star", "1.5.1")


def snapshot(folder):
    """relative path → bytes of every file under folder ({} when missing)."""
    out = {}
    for base, _, files in os.walk(folder):
        for f in files:
            p = os.path.join(base, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, folder)] = fh.read()
    return out


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
        # Upstream = this working tree (uncommitted code included) released as v2.0.0, then one commit not released yet.
        self.upstream = os.path.join(self.tmp, "upstream")
        make_checkout(self.upstream)
        set_version(os.path.join(self.upstream, "skills", "mk-specs", "SKILL.md"), "2.0.0")
        git = lambda *a: subprocess.run(["git", "-C", self.upstream, *a], check=True, capture_output=True,
                                        env={**os.environ, **GIT_ID})
        git("init", "-q")
        git("add", "-A")
        git("commit", "-q", "-m", "release")
        git("tag", "-a", "v2.0.0", "-m", "mk-lab v2.0.0")
        set_version(os.path.join(self.upstream, "skills", "mk-specs", "SKILL.md"), "2.1.0")
        git("commit", "-q", "-am", "not released")
        # Hostile working directory that ships its own skill, plus files named like what BASH_SOURCE may report for a
        # piped script inside a function on some bash versions (`bash`, `main`).
        self.cwd = os.path.join(self.tmp, "repo", "skills", "mk-specs")
        os.makedirs(self.cwd)
        with open(os.path.join(self.cwd, "SKILL.md"), "w", encoding="utf-8") as fh:
            fh.write('---\nname: mk-specs\nmetadata:\n  version: "9.9.9"\n---\nfake\n')
        for name in ("bash", "main"):
            with open(os.path.join(self.tmp, "repo", name), "w", encoding="utf-8") as fh:
                fh.write("")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def pipe(self, env, script=None, cwd=None):
        if script is None:
            with open(INSTALL, "rb") as fh:
                script = fh.read()
        return subprocess.run(["bash", "-s", "--", "--global"], input=script, cwd=cwd or self.tmp, capture_output=True, env=env)

    def env(self, clone):
        return {**{k: v for k, v in os.environ.items() if not k.startswith(("MK_LAB_", "GIT_CONFIG_"))},
                "HOME": self.home, "MK_LAB_HOME": clone, "MK_LAB_REPO": self.upstream, "MK_LAB_NO_UPDATE_CHECK": "1"}

    def test_piped_run_ignores_skill_in_current_directory(self):
        res = self.pipe(self.env(os.path.join(self.tmp, "clone")), cwd=os.path.join(self.tmp, "repo"))
        self.assertEqual(res.returncode, 0, res.stderr.decode())
        installed = version(os.path.join(self.home, ".claude", "skills", "mk-specs", "SKILL.md"))
        self.assertEqual(installed, "2.0.0")
        self.assertNotEqual(installed, "9.9.9")

    def test_piped_run_installs_newest_tag_not_untagged_head(self):
        clone = os.path.join(self.tmp, "clone")
        rev = lambda repo, ref: subprocess.run(["git", "-C", repo, "rev-parse", ref], capture_output=True, text=True,
                                               check=True).stdout.strip()
        res = self.pipe(self.env(clone))
        self.assertEqual(res.returncode, 0, res.stderr.decode())
        self.assertEqual(version(os.path.join(self.home, ".claude", "skills", "mk-specs", "SKILL.md")), "2.0.0")
        self.assertEqual(rev(clone, "HEAD"), rev(self.upstream, "v2.0.0^{commit}"))
        subprocess.run(["git", "-C", self.upstream, "tag", "-a", "v2.1.0", "-m", "mk-lab v2.1.0"], check=True,
                       env={**os.environ, **GIT_ID})
        res = self.pipe(self.env(clone))
        self.assertEqual(res.returncode, 0, res.stderr.decode())
        self.assertEqual(version(os.path.join(self.home, ".claude", "skills", "mk-specs", "SKILL.md")), "2.1.0")
        self.assertEqual(rev(clone, "HEAD"), rev(self.upstream, "v2.1.0^{commit}"))

    def test_truncated_script_runs_nothing(self):
        with open(INSTALL, "rb") as fh:
            lines = fh.read().splitlines(keepends=True)
        self.assertEqual(lines[-1].strip(), b'main "$@"')
        clone = os.path.join(self.tmp, "clone")
        for n in range(1, len(lines)):  # the connection drops after line n: everything received but the last line
            self.pipe(self.env(clone), script=b"".join(lines[:n]))
            self.assertEqual(os.listdir(self.home), [], n)
            self.assertFalse(os.path.exists(clone), n)

    def test_default_repo_is_mzavn_mk_lab_for_clone_and_help(self):
        with open(INSTALL, "rb") as fh:
            script = fh.read()
        # No MK_LAB_REPO/MK_LAB_HOME: git rewrites only the mk-lab URL to the local upstream and refuses https,
        # so any other default URL fails instead of reaching GitHub.
        env = {**{k: v for k, v in os.environ.items() if not k.startswith(("MK_LAB_", "GIT_CONFIG_"))},
               "HOME": self.home, "MK_LAB_NO_UPDATE_CHECK": "1", "GIT_CONFIG_COUNT": "2",
               "GIT_CONFIG_KEY_0": f"url.{self.upstream}.insteadOf", "GIT_CONFIG_VALUE_0": "https://github.com/mzavn/mk-lab.git",
               "GIT_CONFIG_KEY_1": "protocol.https.allow", "GIT_CONFIG_VALUE_1": "never"}
        res = subprocess.run(["bash", "-s", "--", "--global"], input=script, cwd=self.tmp, capture_output=True, env=env)
        self.assertEqual(res.returncode, 0, res.stderr.decode())
        clone = os.path.join(self.home, ".mk-lab")
        origin = subprocess.run(["git", "-C", clone, "remote", "get-url", "origin"], capture_output=True, text=True)
        self.assertEqual(origin.stdout.strip(), "https://github.com/mzavn/mk-lab.git")
        with open(os.path.join(self.home, ".claude", "skills", "mk-specs", SOURCE_FILE), encoding="utf-8") as fh:
            self.assertEqual(fh.read().strip(), clone)
        res = subprocess.run(["bash", INSTALL, "--help"], capture_output=True, text=True, env=env)
        self.assertIn("curl -fsSL https://raw.githubusercontent.com/mzavn/mk-lab/main/install.sh | bash", res.stdout)
        self.assertNotIn("mzavn/mk-skills", res.stdout)

    def test_old_mk_skills_home_and_repo_are_ignored_and_left_untouched(self):
        git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout.strip()
        # Old checkout one commit behind upstream: if it were still used, the bootstrap would pull and move its HEAD.
        subprocess.run(["git", "-C", self.upstream, "commit", "-q", "--allow-empty", "-m", "newer"],
                       check=True, env={**os.environ, **GIT_ID})
        old = os.path.join(self.home, ".mk-skills")
        git("clone", "-q", self.upstream, old)
        git("-C", old, "reset", "-q", "--hard", "HEAD~1")
        old_head = git("-C", old, "rev-parse", "HEAD")
        with open(os.path.join(old, "mine.txt"), "w", encoding="utf-8") as fh:
            fh.write("my notes")
        other = os.path.join(self.tmp, "other")
        git("clone", "-q", self.upstream, other)
        with open(INSTALL, "rb") as fh:
            script = fh.read()
        env = {**{k: v for k, v in os.environ.items() if not k.startswith(("MK_LAB_", "MK_SKILLS_", "GIT_CONFIG_"))},
               "HOME": self.home, "MK_SKILLS_HOME": old, "MK_SKILLS_REPO": other,
               "MK_LAB_REPO": self.upstream, "MK_LAB_NO_UPDATE_CHECK": "1"}
        res = subprocess.run(["bash", "-s", "--", "--global"], input=script, cwd=self.tmp, capture_output=True, env=env)
        self.assertEqual(res.returncode, 0, res.stderr.decode())
        clone = os.path.join(self.home, ".mk-lab")
        self.assertEqual(git("-C", clone, "remote", "get-url", "origin"), self.upstream)
        with open(os.path.join(self.home, ".claude", "skills", "mk-specs", SOURCE_FILE), encoding="utf-8") as fh:
            self.assertEqual(fh.read().strip(), clone)
        self.assertEqual(git("-C", old, "rev-parse", "HEAD"), old_head)
        with open(os.path.join(old, "mine.txt"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "my notes")

    def test_installer_parses_on_system_bash(self):
        for bash in ("bash", "/bin/bash"):
            if shutil.which(bash) or os.path.exists(bash):
                self.assertEqual(subprocess.run([bash, "-n", INSTALL]).returncode, 0, bash)


class SkillCase(unittest.TestCase):
    """Checkout with mk-specs + a fake second skill `star`, fake HOME, installer run by the system bash."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(self.home)
        self.checkout = os.path.join(self.tmp, "checkout")
        make_checkout(self.checkout)
        self.env = {**{k: v for k, v in os.environ.items() if k != "MK_LAB_UPDATED"},
                    "HOME": self.home, "MK_LAB_NO_UPDATE_CHECK": "1", **GIT_ID}
        self.proj = os.path.join(self.tmp, "proj")
        os.makedirs(self.proj)
        subprocess.run(["git", "init", "-q", self.proj], check=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def install(self, *args):
        return subprocess.run([BASH, os.path.join(self.checkout, "install.sh"), *args],
                              capture_output=True, text=True, env=self.env)

    def ok(self, *args):
        res = self.install(*args)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        return res

    def h(self, *parts):
        return os.path.join(self.home, *parts)

    def p(self, *parts):
        return os.path.join(self.proj, *parts)

    def git(self, cwd, *args):
        subprocess.run(["git", "-C", cwd, *args], check=True, capture_output=True, env=self.env)

    def foreign(self, folder):
        os.makedirs(folder)
        with open(os.path.join(folder, "keep.txt"), "w") as fh:
            fh.write("keep")


class GlobalSkill(SkillCase):
    def test_global_install_of_star_adds_its_copies_and_leaves_mk_specs_alone(self):
        self.ok("--global")
        before = snapshot(self.h(".claude", "skills", "mk-specs")), snapshot(self.h(".agents", "skills", "mk-specs"))
        res = self.ok("--global", "--skill", "star")
        self.assertIn("star 1.5.1", res.stdout)
        for base in (".claude", ".agents"):
            dest = self.h(base, "skills", "star")
            for f in ("SKILL.md", os.path.join("references", "a.md"), MANIFEST, SOURCE_FILE):
                self.assertTrue(os.path.isfile(os.path.join(dest, f)), (dest, f))
            self.assertIn(f"global: {dest} (none → 1.5.1)", res.stdout)
        after = snapshot(self.h(".claude", "skills", "mk-specs")), snapshot(self.h(".agents", "skills", "mk-specs"))
        self.assertEqual(before, after)

    def test_bad_skill_arguments_are_refused_with_the_skill_list_and_install_nothing(self):
        for args in (["--global", "--skill", "khong-co"], ["--global", "--skill", "../x"], ["--global", "--skill", "-x"],
                     ["--global", "--skill"], ["--skill", "--global"], ["--global", "--skill="],
                     ["--global", "--skill", "star", "--skill", "star"], ["--global", "--skill=star", "--skill=mk-specs"],
                     ["--skill", "star", "--check"], ["--check", "--skill=star"]):
            res = self.install(*args)
            self.assertEqual(res.returncode, 1, args)
            self.assertIn("mk-specs, star", res.stderr, args)
        self.assertEqual(os.listdir(self.home), [])

    def test_global_star_refuses_a_folder_it_did_not_create_until_forced(self):
        self.foreign(self.h(".agents", "skills", "star"))
        res = self.install("--global", "--skill", "star")
        self.assertEqual(res.returncode, 1)
        self.assertIn("was not installed by install.sh", res.stderr)
        self.assertEqual(os.listdir(self.h(".agents", "skills", "star")), ["keep.txt"])
        self.assertFalse(os.path.exists(self.h(".claude", "skills", "star")))
        self.ok("--global", "--skill", "star", "--force")
        self.assertFalse(os.path.exists(self.h(".agents", "skills", "star", "keep.txt")))
        self.assertTrue(os.path.isfile(self.h(".agents", "skills", "star", MANIFEST)))

    def test_global_mk_specs_replaces_only_its_own_old_install(self):
        self.foreign(self.h(".agents", "skills", "mk-specs"))
        for args in (["--global"], ["--uninstall", "--global"]):
            res = self.install(*args)
            self.assertEqual(res.returncode, 1, args)
            self.assertIn("was not installed by install.sh", res.stderr)
            self.assertEqual(os.listdir(self.h(".agents", "skills", "mk-specs")), ["keep.txt"])
            self.assertFalse(os.path.exists(self.h(".claude", "skills", "mk-specs")))
        # An old copy of this kit (source file, no manifest) is still replaced without --force.
        with open(self.h(".agents", "skills", "mk-specs", SOURCE_FILE), "w") as fh:
            fh.write("/old/checkout\n")
        self.ok("--global")
        self.assertTrue(os.path.isfile(self.h(".agents", "skills", "mk-specs", MANIFEST)))
        self.assertFalse(os.path.exists(self.h(".agents", "skills", "mk-specs", "keep.txt")))
        shutil.rmtree(self.h(".agents", "skills", "mk-specs"))
        self.foreign(self.h(".agents", "skills", "mk-specs"))
        self.ok("--global", "--force")
        self.assertFalse(os.path.exists(self.h(".agents", "skills", "mk-specs", "keep.txt")))

    def test_help_shows_the_whole_header_including_skill_flag_and_curl_line(self):
        res = self.ok("--help")
        self.assertIn("--skill", res.stdout)
        self.assertIn("curl -fsSL", res.stdout)
        self.assertIn("MK_LAB_HOME", res.stdout)
        self.assertNotIn("set -euo", res.stdout)


class ProjectSkill(SkillCase):
    def test_project_install_of_star_touches_neither_config_nor_agent_files(self):
        with open(self.p("GEMINI.md"), "w", encoding="utf-8") as fh:
            fh.write("# Gemini\n")
        self.ok("--project", self.proj, "--skill", "star")
        self.assertTrue(os.path.isfile(self.p(".claude", "skills", "star", MANIFEST)))
        self.assertFalse(os.path.exists(self.p("specs")))
        self.assertFalse(os.path.exists(self.p("AGENTS.md")))
        self.assertFalse(os.path.exists(self.p("CLAUDE.md")))
        with open(self.p("GEMINI.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "# Gemini\n")
        self.assertFalse(os.path.exists(self.p(".agents")))
        self.ok("--project", self.proj, "--skill=star", "--agents-dir")
        self.assertTrue(os.path.isfile(self.p(".agents", "skills", "star", MANIFEST)))
        self.assertFalse(os.path.exists(self.p("AGENTS.md")))

    def test_hand_edit_in_project_star_is_not_overwritten(self):
        self.ok("--project", self.proj, "--skill", "star")
        skill = self.p(".claude", "skills", "star", "SKILL.md")
        with open(skill, "a", encoding="utf-8") as fh:
            fh.write("\nsửa tay\n")
        res = self.install("--project", self.proj, "--skill", "star")
        self.assertEqual(res.returncode, 1)
        self.assertIn("has edits not made by install.sh", res.stderr)
        with open(skill, encoding="utf-8") as fh:
            self.assertIn("sửa tay", fh.read())

    def test_committed_star_folder_without_manifest_blocks_every_destination(self):
        for foreign, other in ((".claude", ".agents"), (".agents", ".claude")):
            self.foreign(self.p(foreign, "skills", "star"))
            self.git(self.proj, "add", "-A")
            self.git(self.proj, "commit", "-q", "-m", "foreign star")
            res = self.install("--project", self.proj, "--skill", "star", "--agents-dir")
            self.assertEqual(res.returncode, 1, foreign)
            self.assertIn("was not installed by install.sh", res.stderr)
            self.assertEqual(os.listdir(self.p(foreign, "skills", "star")), ["keep.txt"])
            self.assertFalse(os.path.exists(self.p(other, "skills", "star")), foreign)
            self.git(self.proj, "rm", "-q", "-r", foreign)
            self.git(self.proj, "commit", "-q", "-m", "drop")


class UninstallSkill(SkillCase):
    def test_uninstalling_star_from_project_keeps_mk_specs_config_and_agent_files(self):
        self.ok("--project", self.proj)
        self.ok("--project", self.proj, "--skill", "star", "--agents-dir")
        kept = {f: snapshot(self.p(f)) for f in (os.path.join(".claude", "skills", "mk-specs"), "specs")}
        with open(self.p("AGENTS.md"), "rb") as fh:
            agents_md = fh.read()
        res = self.ok("--uninstall", "--project", self.proj, "--skill", "star")
        self.assertFalse(os.path.exists(self.p(".claude", "skills", "star")))
        self.assertFalse(os.path.exists(self.p(".agents", "skills", "star")))
        self.assertNotIn("kept specs/mk-specs.yml", res.stdout)
        self.assertEqual(kept, {f: snapshot(self.p(f)) for f in kept})
        with open(self.p("AGENTS.md"), "rb") as fh:
            self.assertEqual(fh.read(), agents_md)

    def test_uninstalling_star_refuses_any_copy_without_manifest_and_removes_nothing(self):
        self.ok("--global", "--skill", "star")
        os.remove(self.h(".claude", "skills", "star", MANIFEST))
        res = self.install("--uninstall", "--global", "--skill", "star")
        self.assertEqual(res.returncode, 1)
        self.assertIn("was not installed by install.sh", res.stderr)
        self.assertTrue(os.path.isdir(self.h(".claude", "skills", "star")))
        self.assertTrue(os.path.isdir(self.h(".agents", "skills", "star")))

        self.ok("--project", self.proj, "--skill", "star", "--agents-dir")
        os.remove(self.p(".agents", "skills", "star", MANIFEST))
        res = self.install("--uninstall", "--project", self.proj, "--skill", "star")
        self.assertEqual(res.returncode, 1)
        self.assertIn("was not installed by install.sh", res.stderr)
        self.assertTrue(os.path.isfile(self.p(".claude", "skills", "star", MANIFEST)))
        self.assertTrue(os.path.isdir(self.p(".agents", "skills", "star")))

    def test_uninstall_refuses_hand_edit_in_agents_copy(self):
        self.ok("--project", self.proj, "--agents-dir", "--no-agent-files")
        with open(self.p(".agents", "skills", "mk-specs", "SKILL.md"), "a", encoding="utf-8") as fh:
            fh.write("\nluật riêng\n")
        res = self.install("--uninstall", "--project", self.proj, "--no-agent-files")
        self.assertEqual(res.returncode, 1)
        self.assertIn("SKILL.md", res.stderr)
        self.assertTrue(os.path.isfile(self.p(".claude", "skills", "mk-specs", MANIFEST)))
        self.assertTrue(os.path.isfile(self.p(".agents", "skills", "mk-specs", MANIFEST)))
        self.ok("--uninstall", "--project", self.proj, "--no-agent-files", "--force")
        self.assertFalse(os.path.exists(self.p(".agents", "skills", "mk-specs")))


class UpdateSkills(SkillCase):
    """--update from a clone of a throwaway source repo built from the working tree, so uncommitted code is tested."""

    def setUp(self):
        super().setUp()
        self.source = self.checkout
        self.git(self.source, "init", "-q")
        self.commit_source("v1")
        self.tag_source("v1.5.1")
        self.checkout = os.path.join(self.tmp, "clone")
        subprocess.run(["git", "clone", "-q", self.source, self.checkout], check=True, env=self.env)

    def commit_source(self, msg):
        self.git(self.source, "add", "-A")
        self.git(self.source, "commit", "-q", "-m", msg)

    def tag_source(self, tag):
        self.git(self.source, "tag", "-a", tag, "-m", f"mk-lab {tag}")

    def bump_source(self, ver, release=True):
        for name in ("mk-specs", "star"):
            set_version(os.path.join(self.source, "skills", name, "SKILL.md"), ver)
        self.commit_source(f"bump {ver}")
        if release:
            self.tag_source(f"v{ver}")

    def test_update_takes_newest_tag_never_untagged_commits(self):
        self.ok("--global")
        self.bump_source("9.0.0")
        self.bump_source("9.1.0", release=False)
        res = self.ok("--update")
        self.assertIn("(v9.0.0)", res.stdout)
        self.assertEqual(version(self.h(".claude", "skills", "mk-specs", "SKILL.md")), "9.0.0")
        self.assertEqual(version(os.path.join(self.checkout, "skills", "mk-specs", "SKILL.md")), "9.0.0")

    def test_update_refuses_a_checkout_past_the_newest_release(self):
        with open(os.path.join(self.checkout, "notes.txt"), "w") as fh:
            fh.write("dev work")
        self.git(self.checkout, "add", "notes.txt")
        self.git(self.checkout, "commit", "-q", "-m", "local work")
        res = self.install("--update")
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertIn("past the newest release", res.stderr)
        self.assertEqual(os.listdir(self.home), [])

    def test_update_pulls_then_refreshes_every_global_skill(self):
        self.ok("--global")
        self.ok("--global", "--skill", "star")
        self.bump_source("9.0.0")
        res = self.ok("--update")
        self.assertIn("mk-lab: ", res.stdout)
        for name in ("mk-specs", "star"):
            for base in (".claude", ".agents"):
                self.assertIn(f"global: {self.h(base, 'skills', name)} (", res.stdout)
                self.assertEqual(version(self.h(base, "skills", name, "SKILL.md")), "9.0.0")
        self.assertRegex(res.stdout, r"\(1\.5\.1 → 9\.0\.0\)")

    def test_update_of_project_with_only_star_does_not_add_mk_specs(self):
        self.ok("--project", self.proj, "--skill", "star")
        self.bump_source("9.0.0")
        res = self.ok("--update", "--project", self.proj)
        self.assertIn("(1.5.1 → 9.0.0)", res.stdout)
        self.assertEqual(version(self.p(".claude", "skills", "star", "SKILL.md")), "9.0.0")
        for path in ((".claude", "skills", "mk-specs"), ("specs", "mk-specs.yml"), ("AGENTS.md",), ("CLAUDE.md",)):
            self.assertFalse(os.path.exists(self.p(*path)), path)
        self.assertFalse(os.path.exists(self.h(".claude")))

    def test_update_with_a_skill_added_upstream_installs_it_after_pulling(self):
        write_skill(self.source, "moi", "1.5.1")
        self.commit_source("add moi")
        self.tag_source("v1.6.0")
        res = self.ok("--update", "--global", "--skill", "moi")
        self.assertTrue(os.path.isfile(self.h(".claude", "skills", "moi", MANIFEST)))
        self.assertFalse(os.path.exists(self.h(".claude", "skills", "mk-specs")))
        self.assertIn("moi 1.5.1", res.stdout)

    def test_update_with_unknown_skill_pulls_but_installs_nothing(self):
        self.bump_source("9.0.0")
        res = self.install("--update", "--skill", "khong-co")
        self.assertEqual(res.returncode, 1)
        self.assertIn("mk-lab: ", res.stdout)
        self.assertIn("mk-specs, star", res.stderr)
        self.assertEqual(version(os.path.join(self.checkout, "skills", "star", "SKILL.md")), "9.0.0")
        self.assertEqual(os.listdir(self.home), [])


if __name__ == "__main__":
    unittest.main()
