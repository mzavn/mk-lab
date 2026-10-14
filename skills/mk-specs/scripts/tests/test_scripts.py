"""Tests for mk-specs scripts. Run: python3 -m unittest discover -s skills/mk-specs/scripts/tests"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
sys.path.insert(0, SCRIPTS)
import mkspecs  # noqa: E402

CONFIG = textwrap.dedent("""\
    version: 1
    language: vi
    specs_dir: specs
    contexts:
      - id: checkout
        title: "Đặt hàng (checkout)"   # comment after a value
    ids:
      uc: 'UC-\\d{3}'
      br: 'BR-\\d+'
      adr: 'ADR-\\d+'
    tests:
      file_pattern: '[^`]+\\.test\\.ts'
      citation_style: pointer
    readme:
      banner:
        match: '^> (Cập nhật|Hợp nhất) '
        keep: 2
      lines:
        - match: '^(?P<uc>\\d+) UC · (?P<ac>\\d+) AC'
        - match: 'Trace Ratio (?P<trace_ratio>\\S+) \\((?P<traced>\\d+)/(?P<trace_total>\\d+)\\)'
    metrics:
      since: "2000-01-01"
      exempt_scopes: [specs]
    """)

UC = textwrap.dedent("""\
    # UC-101: Khách đặt hàng
    - Status: implemented
    - BR: BR-01

    ## History
    - v1 (2026-01-02, chưa commit): khởi tạo

    ## Main Flow
    1. Khách xác nhận giỏ hàng.

    ## Acceptance Criteria

    ### AC-1: Tạo đơn
    - Given giỏ có 2 món
    - When khách đặt
    - Then có 1 đơn
    - Tests: [`test/order.test.ts`](../../test/order.test.ts) › "đơn › tạo được" · "… › huỷ được"

    ### AC-2: Giỏ rỗng
    - Given giỏ rỗng
    - When khách đặt
    - Then KHÔNG tạo đơn
    - Tests: ⚠ Chưa có test (chờ e2e)

    ## Divergences & Open Questions
    - [OPEN] Giới hạn số món? Xem [BR](../business-requirements.md)
    """)

README = textwrap.dedent("""\
    # specs
    > Cập nhật 2026-01-01: một
    > Cập nhật 2026-01-03: ba
    > Hợp nhất change x ngày 2026-01-02: hai
    0 UC · 0 AC · …
    Trace Ratio — (0/0)
    """)


def run(script, root, *args):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, script), "--root", root, *args],
                          capture_output=True, text=True)


class YamlSubset(unittest.TestCase):
    def test_parses_nested_maps_lists_and_scalars(self):
        cfg = mkspecs.parse_yaml(CONFIG)
        self.assertEqual(cfg["contexts"], [{"id": "checkout", "title": "Đặt hàng (checkout)"}])
        self.assertEqual(cfg["ids"]["uc"], "UC-\\d{3}")
        self.assertEqual(cfg["readme"]["banner"]["keep"], 2)
        self.assertEqual(cfg["metrics"]["exempt_scopes"], ["specs"])
        self.assertEqual(mkspecs.parse_yaml("a: null\nb: true\nc: 'it''s # not a comment'\nd: \"x\\ny\""),
                         {"a": None, "b": True, "c": "it's # not a comment", "d": "x\ny"})

    def test_rejects_bad_indentation(self):
        with self.assertRaises(mkspecs.ConfigError):
            mkspecs.parse_yaml("a: 1\n   b: 2\n")


class Scripts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = self.root = self.tmp.name
        os.makedirs(os.path.join(r, "specs", "checkout"))
        os.makedirs(os.path.join(r, "test"))
        files = {
            "specs/mk-specs.yml": CONFIG,
            "specs/checkout/UC-101-dat-hang.md": UC,
            "specs/business-requirements.md": "# BR\n## BR-01: Bán được hàng\n",
            "specs/decisions.md": "# ADR\n## ADR-01: Dùng QR\n- [DIVERGENCE] tài liệu nói 10 phút, code 15\n",
            "specs/README.md": README,
            "test/order.test.ts": "",
        }
        for rel, text in files.items():
            with open(os.path.join(r, rel), "w", encoding="utf-8") as fh:
                fh.write(text)
        self.tests_json = os.path.join(r, "tests.json")
        with open(self.tests_json, "w", encoding="utf-8") as fh:
            json.dump([{"file": os.path.join(r, "test/order.test.ts"), "name": "đơn > tạo được"},
                       {"file": os.path.join(r, "test/order.test.ts"), "name": "đơn > huỷ được"}], fh)
        git = ["git", "-C", r, "-c", "user.name=t", "-c", "user.email=t@example.com"]
        subprocess.run(["git", "init", "-q", r], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        for msg in ["feat(UC-101): đặt hàng", "chore(specs): adopt", "fix: no id", "feat(UC-999): unknown id"]:
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", msg], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, rel):
        return mkspecs.read(os.path.join(self.root, rel))

    def test_gen_outputs_metrics_readme_and_is_deterministic(self):
        res = run("gen.py", self.root, "--verified-on", "2026-01-05")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("UC 1 · AC 2 · test 1 · no test 1 · divergence 1 · open 1", res.stdout)
        self.assertIn("Spec Coverage 100,0% (1/1 UC)", res.stdout)
        self.assertIn("Trace Ratio 33,3% (1/3", res.stdout)
        trace, oi = self.read("specs/traceability.md"), self.read("specs/open-issues.md")
        self.assertIn("(2026-01-05)", trace)
        self.assertIn("| ⚠ AC-2: Giỏ rỗng | ⚠ Chưa có test (chờ e2e) |", trace)
        self.assertIn("[`test/order.test.ts`](../test/order.test.ts)", trace)
        self.assertIn("Xem [BR](business-requirements.md)", oi)
        readme = self.read("specs/README.md")
        self.assertNotIn("2026-01-01", readme)
        self.assertIn("1 UC · 2 AC", readme)
        self.assertIn("Trace Ratio 33,3% (1/3)", readme)
        run("gen.py", self.root)
        self.assertEqual(trace, self.read("specs/traceability.md"))
        self.assertEqual(oi, self.read("specs/open-issues.md"))

    def test_verify_passes_then_fails_on_unknown_test_and_link(self):
        res = run("verify.py", self.root, "--tests", self.tests_json)
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("citations checked: 2, unresolved: 0", res.stdout)
        self.assertIn("PENDING", res.stdout)
        path = os.path.join(self.root, "specs/checkout/UC-101-dat-hang.md")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n### AC-3: x\n- Tests: [`test/order.test.ts`](../../test/nope.test.ts) › \"đơn › không có\"\n")
        res = run("verify.py", self.root, "--tests", self.tests_json)
        self.assertEqual(res.returncode, 1)
        self.assertIn("unresolved: 1", res.stdout)
        self.assertIn("LINK", res.stdout)

    def test_both_style_requires_id_in_test_name(self):
        cfg = os.path.join(self.root, "specs/mk-specs.yml")
        with open(cfg, "w", encoding="utf-8") as fh:
            fh.write(CONFIG.replace("citation_style: pointer", "citation_style: both"))
        res = run("verify.py", self.root, "--tests", self.tests_json)
        self.assertEqual(res.returncode, 1)
        self.assertIn("lacks 'UC-101 / AC-1'", res.stdout)

    def test_commit_hash_replaces_only_history_and_status(self):
        with open(os.path.join(self.root, "specs/README.md"), "a", encoding="utf-8") as fh:
            fh.write("- v9 thay `chưa commit` bằng hash\n")
        res = run("commit-hash.py", self.root, "abc1234")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("- v1 (2026-01-02, commit `abc1234`): khởi tạo", self.read("specs/checkout/UC-101-dat-hang.md"))
        self.assertIn("thay `chưa commit` bằng hash", self.read("specs/README.md"))

    def test_audit_reports_without_writing(self):
        before = self.read("specs/checkout/UC-101-dat-hang.md")
        res = run("audit.py", self.root)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("## Postconditions", res.stdout)
        self.assertIn("- fix: no id", res.stdout)
        self.assertIn("- feat(UC-999): unknown id", res.stdout)
        self.assertEqual(before, self.read("specs/checkout/UC-101-dat-hang.md"))

class AgentFiles(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def read(self, name):
        with open(os.path.join(self.root, name), encoding="utf-8") as fh:
            return fh.read()

    def run_files(self, *extra):
        res = subprocess.run([sys.executable, os.path.join(SCRIPTS, "agent-files.py"), self.root, *extra], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stderr)
        return res.stdout

    def test_fresh_project_gets_agents_block_and_claude_import_once(self):
        out = self.run_files()
        self.assertIn("AGENTS.md (created)", out)
        self.assertIn("@AGENTS.md created", out)
        agents = self.read("AGENTS.md")
        self.assertEqual(agents.count("<!-- mk-specs:start"), 1)
        self.assertEqual(self.read("CLAUDE.md"), "@AGENTS.md\n")
        again = self.run_files()
        self.assertIn("AGENTS.md (unchanged)", again)
        self.assertIn("@AGENTS.md unchanged", again)
        self.assertEqual(agents, self.read("AGENTS.md"))

    def test_existing_files_keep_own_rules_and_stale_block_is_replaced(self):
        with open(os.path.join(self.root, "AGENTS.md"), "w", encoding="utf-8") as fh:
            fh.write("# Luật repo\n\nGiữ nguyên dòng này.\n\n<!-- mk-specs:start v0.1 -->\ncũ\n<!-- mk-specs:end -->\n\n## Sau khối\nCũng giữ.\n")
        with open(os.path.join(self.root, "CLAUDE.md"), "w", encoding="utf-8") as fh:
            fh.write("# Claude riêng\n")
        with open(os.path.join(self.root, "GEMINI.md"), "w", encoding="utf-8") as fh:
            fh.write("# Gemini\n")
        out = self.run_files()
        self.assertIn("AGENTS.md (updated)", out)
        agents = self.read("AGENTS.md")
        self.assertIn("Giữ nguyên dòng này.", agents)
        self.assertIn("## Sau khối\nCũng giữ.", agents)
        self.assertNotIn("\ncũ\n", agents)
        self.assertEqual(self.read("CLAUDE.md"), "@AGENTS.md\n\n# Claude riêng\n")
        self.assertIn("AGENTS.md", self.read("GEMINI.md"))
        self.run_files("--uninstall")
        self.assertNotIn("mk-specs:start", self.read("AGENTS.md"))
        self.assertIn("Giữ nguyên dòng này.", self.read("AGENTS.md"))


class UpdateCheck(unittest.TestCase):
    """check-update.py: compare the version in use with the highest vX.Y.Z tag of the skill repo (read-only ls-remote)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        self.proj = os.path.join(self.tmp, "proj")
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(self.repo)
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        for cmd in (["git", "init", "-q"], ["git", "commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(cmd, cwd=self.repo, check=True, env=env)
        self.env = env

    def tag(self, *names):
        for n in names:
            subprocess.run(["git", "tag", n], cwd=self.repo, check=True, env=self.env)

    def install(self, where, version):
        d = os.path.join(where, "mk-specs")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
            fh.write(f'---\nname: mk-specs\nmetadata:\n  version: "{version}"\n---\n')
        return d

    def check(self, repo=None, **env):
        os.makedirs(self.proj, exist_ok=True)
        res = subprocess.run([sys.executable, os.path.join(SCRIPTS, "check-update.py")], cwd=self.proj, capture_output=True,
                             text=True, env={**self.env, "HOME": self.home, "MK_SKILLS_REPO": repo or self.repo, **env})
        self.assertEqual(res.returncode, 0, res.stderr)
        return res.stdout

    def test_newer_release_is_reported_with_update_command_for_project_copy(self):
        self.tag("v1.3.0", "v1.4.0", "v1.10.0", "release/x")
        self.install(os.path.join(self.home, ".claude", "skills"), "1.4.0")
        self.install(os.path.join(self.proj, ".claude", "skills"), "1.4.0")
        out = self.check()
        self.assertIn("có bản mới v1.10.0 (đang dùng 1.4.0)", out)
        self.assertIn("--project .", out)
        self.assertIn("CHANGELOG.md", out)
        self.assertNotIn("bản lớn", out)

    def test_project_copy_wins_over_global_copy(self):
        self.tag("v1.5.0")
        self.install(os.path.join(self.home, ".claude", "skills"), "1.5.0")
        self.install(os.path.join(self.proj, ".claude", "skills"), "1.4.0")
        out = self.check()
        self.assertIn("đang dùng 1.4.0", out)
        self.assertIn("bản trong project 1.4.0 khác bản cài chung 1.5.0", out)

    def test_major_release_warns_about_extra_steps(self):
        self.tag("v2.0.0")
        self.install(os.path.join(self.home, ".claude", "skills"), "1.4.0")
        self.assertIn("bản lớn", self.check())

    def test_latest_or_unreleased_copy_is_not_asked_to_update(self):
        self.tag("v1.4.0")
        self.install(os.path.join(self.home, ".claude", "skills"), "1.4.0")
        self.assertIn("đang dùng bản mới nhất v1.4.0", self.check())
        self.install(os.path.join(self.home, ".claude", "skills"), "1.5.0")
        out = self.check()
        self.assertIn("chưa phát hành", out)
        self.assertNotIn("có bản mới", out)

    def test_unreachable_repo_or_opt_out_never_fails(self):
        self.install(os.path.join(self.home, ".claude", "skills"), "1.4.0")
        self.assertIn("không kiểm được bản mới", self.check(repo=os.path.join(self.tmp, "missing")))
        self.assertIn("đã tắt", self.check(MK_SKILLS_NO_UPDATE_CHECK="1"))


if __name__ == "__main__":
    unittest.main()
