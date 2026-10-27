"""Tests for mk-ship ship.py. Run: python3 -m unittest discover -s skills/mk-ship/scripts/tests

Each test class names the AC it covers (UC-901 check, UC-902 smoke). Git runs in temporary repos with the user's
global and system config switched off. Secret-looking values are joined at run time by `cat()` so no real-format
token sits in this file or its bytecode."""
import contextlib
import datetime
import http.server
import importlib.util
import io
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
import urllib.parse
import unittest

sys.dont_write_bytecode = True
SHIP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ship.py")
TODAY = datetime.datetime.now(datetime.timezone.utc).date()
PAST = (TODAY - datetime.timedelta(days=3)).isoformat()
FUTURE = (TODAY + datetime.timedelta(days=3)).isoformat()


def cat(*parts):
    return "".join(parts)


def load_ship():
    spec = importlib.util.spec_from_file_location("mk_ship_under_test", SHIP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


ENV_TABLE = """## Môi trường
| Môi trường | Nhánh | Lệnh triển khai | URL |
|---|---|---|---|
| staging | * | `npx --no wrangler deploy --env staging` | https://dat-mon-staging.example.workers.dev |
| production | main | `npx --no wrangler deploy --env production` | https://dat-mon.example.com |
"""

SMOKE_TABLE = """## Kiểm sau triển khai
| Đường dẫn | Mã | Có chữ |
|---|---|---|
| / | 200 | Đặt món |
| /api/health | 200 | — |
"""


def deploy_md(platform="cloudflare-workers", env_table=ENV_TABLE, smoke=SMOKE_TABLE, extra=""):
    head = "# Triển khai dat-mon\n"
    if platform is not None:
        head += f"- Nền tảng: {platform}\n"
    return (head + extra + "\n" + env_table + "\n" + smoke + "\n## Bí mật cần có\n- JWT_SECRET\n\n"
            "## Trước khi triển khai\n- npm test\n\n## Quay lui\n- xem cloudflare\n")


WRANGLER = """{
  // cấu hình mẫu — chú thích dòng
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "dat-mon",
  "main": "src/index.ts",
  /* chú thích khối, có dấu phẩy, ] và } */
  "compatibility_date": "%s",
  "observability": { "enabled": true },
  "env": {
    "staging": { "vars": { "API_URL": "https://a.b/v1", "MAX_TOKENS": "512" }, },
    "production": { "routes": [ { "pattern": "dat-mon.example.com/*", "zone_name": "example.com" }, ], },
  },
}
""" % PAST


class Repo:
    """A temporary git repo with isolated git config; ship.py runs against it."""

    def __init__(self, case):
        self.case = case
        self.base = os.path.realpath(tempfile.mkdtemp())
        case.addCleanup(shutil.rmtree, self.base, True)
        self.root = os.path.join(self.base, "repo")
        os.makedirs(self.root)
        self.gitconfig = os.path.join(self.base, "gitconfig")
        write(self.gitconfig, "")
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=self.gitconfig, GIT_CONFIG_NOSYSTEM="1",
                        GIT_CEILING_DIRECTORIES=self.base)
        for k in list(self.env):
            if k.startswith("GIT_") and k not in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_CEILING_DIRECTORIES"):
                del self.env[k]
        self.git("init", "-q", "-b", "main")

    def git(self, *args):
        res = subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=t", "-c", "commit.gpgsign=false", *args],
                             cwd=self.root, env=self.env, capture_output=True, text=True)
        if res.returncode != 0:
            raise AssertionError(f"git {args}: {res.stderr}")
        return res.stdout.strip()

    def put(self, rel, content):
        write(os.path.join(self.root, rel), content)

    def commit(self, msg="m"):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def exclude(self, line):
        with open(os.path.join(self.root, ".git", "info", "exclude"), "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def ship(self, *args, timeout=30):
        return subprocess.run([sys.executable, SHIP, *args, "--root", self.root], capture_output=True, text=True,
                              env=self.env, timeout=timeout)

    def check(self, env_name="staging"):
        return self.ship("check", "--env", env_name)


def ready_repo(case, deploy=None, wrangler=WRANGLER, extra_files=None):
    r = Repo(case)
    r.put("DEPLOY.md", deploy if deploy is not None else deploy_md())
    if wrangler is not None:
        r.put("wrangler.jsonc", wrangler)
    r.put("src/index.ts", "export default {}\n")
    for rel, content in (extra_files or {}).items():
        r.put(rel, content)
    r.commit("init")
    return r


def lines(res):
    return res.stdout.splitlines()


# ---------------------------------------------------------------- UC-901 check


class CheckCalling(unittest.TestCase):
    def test_bad_env_name_exits_2(self):
        r = ready_repo(self)
        for bad in ("a b", "x;y", ""):
            res = r.check(bad)
            self.assertEqual(res.returncode, 2, (bad, res.stdout))

    def test_not_a_git_repo_exits_2(self):
        r = Repo(self)
        shutil.rmtree(os.path.join(r.root, ".git"))
        r.put("DEPLOY.md", deploy_md())
        res = r.check()
        self.assertEqual(res.returncode, 2, res.stdout)
        self.assertIn("không phải repo git", res.stdout)


class CheckDeployMd(unittest.TestCase):
    """UC-901 AC-1 and DEPLOY.md parsing rules."""

    def test_ac1_missing_deploy_md_blocks(self):
        r = Repo(self)
        r.put("wrangler.jsonc", WRANGLER)
        r.commit()
        res = r.check()
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("CHẶN: chưa có DEPLOY.md", res.stdout)

    def test_ac1_env_missing_from_table_blocks(self):
        table = ENV_TABLE.replace("| staging |", "| dev |")
        r = ready_repo(self, deploy=deploy_md(env_table=table))
        res = r.check("staging")
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("CHẶN: DEPLOY.md không có môi trường staging", lines(res))

    def test_platform_missing_or_unknown_blocks(self):
        for platform in (None, "heroku", "khác ()"):
            r = ready_repo(self, deploy=deploy_md(platform=platform))
            res = r.check()
            self.assertEqual(res.returncode, 1, (platform, res.stdout))
            self.assertIn("Nền tảng", res.stdout)

    def test_no_production_row_warns(self):
        table = "\n".join(l for l in ENV_TABLE.splitlines() if "production" not in l) + "\n"
        r = ready_repo(self, deploy=deploy_md(env_table=table))
        res = r.check()
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertTrue(any(l.startswith("CẢNH BÁO: DEPLOY.md không có môi trường production") for l in lines(res)))

    def test_production_rule_by_name(self):
        ship = load_ship()
        for name in ("production", "prod", "Production", "PROD", "api-production", "web-prod"):
            self.assertTrue(ship.is_production(name), name)
        for name in ("staging", "preprod", "production-eu", "dev", "prod2"):
            self.assertFalse(ship.is_production(name), name)

    def test_cells_drop_backticks_and_keep_escaped_pipes(self):
        ship = load_ship()
        self.assertEqual(ship.split_row(r"| a | `b \| c` | `d` |"), ["a", "b | c", "d"])


class CheckGit(unittest.TestCase):
    """UC-901 AC-2."""

    def test_ac2_every_kind_of_uncommitted_change_is_listed_sorted(self):
        r = ready_repo(self, extra_files={"a.txt": "a\n", "b.txt": "b\n", "c.txt": "c\n", "old.txt": "o\n",
                                          ".gitignore": "*.tmp\n"})
        r.put("a.txt", "a2\n")                      # modified
        r.put("b.txt", "b2\n")
        r.git("add", "b.txt")                       # staged
        os.remove(os.path.join(r.root, "c.txt"))    # deleted
        r.git("mv", "old.txt", "new.txt")           # renamed
        r.put("z/untracked.txt", "u\n")             # untracked, nested
        r.put("ignored.tmp", "x\n")                 # .gitignore
        r.put("excluded.log", "x\n")
        r.exclude("*.log")                          # .git/info/exclude
        globalignore = os.path.join(r.base, "globalignore")
        write(globalignore, "*.bak\n")
        write(r.gitconfig, f"[core]\n\texcludesFile = {globalignore}\n")
        r.put("global.bak", "x\n")                  # global excludes
        res = r.check()
        self.assertEqual(res.returncode, 1, res.stdout)
        out = lines(res)
        i = out.index("CHẶN: còn thay đổi chưa commit — chỉ triển khai cái đã commit")
        self.assertEqual(out[i + 1:i + 7], ["  a.txt", "  b.txt", "  c.txt", "  new.txt", "  old.txt",
                                            "  z/untracked.txt"])
        for name in ("ignored.tmp", "excluded.log", "global.bak"):
            self.assertNotIn(name, res.stdout)

    def test_ac2_wrong_branch_blocks_production(self):
        r = ready_repo(self)
        r.git("checkout", "-q", "-b", "dev")
        res = r.check("production")
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("CHẶN: đang ở nhánh dev, môi trường production cần nhánh main", lines(res))

    def test_ac2_star_branch_allows_any_branch(self):
        r = ready_repo(self)
        r.git("checkout", "-q", "-b", "dev")
        res = r.check("staging")
        self.assertEqual(res.returncode, 0, res.stdout)

    def test_ac2_empty_branch_cell_blocks(self):
        table = ENV_TABLE.replace("| staging | * |", "| staging |  |")
        r = ready_repo(self, deploy=deploy_md(env_table=table))
        res = r.check("staging")
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("CHẶN: DEPLOY.md thiếu nhánh của staging", lines(res))

    def test_ac2_detached_head(self):
        r = ready_repo(self)
        first = r.git("rev-parse", "HEAD")
        second = r.commit("two")
        r.git("checkout", "-q", "--detach", second)
        self.assertEqual(r.check("production").returncode, 0)          # equals refs/heads/main
        r.git("checkout", "-q", "--detach", first)
        res = r.check("production")
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("CHẶN: HEAD tách rời, không trùng đầu nhánh main", lines(res))
        r.git("update-ref", "refs/remotes/origin/main", first)          # equals refs/remotes/<remote>/main
        self.assertEqual(r.check("production").returncode, 0, r.check("production").stdout)


SPEC_YML = "version: 1\nlanguage: vi\n"


def proposal(status):
    return f"# 261027-x: thử\n- Status: {status}\n- Quy mô: nhỏ\n\n## Vì sao\n- Status: implemented (trong thân, bỏ qua)\n"


class CheckSpec(unittest.TestCase):
    """UC-901 AC-3."""

    def repo(self, files, yml=SPEC_YML):
        r = ready_repo(self)
        r.exclude("/specs/")
        r.exclude("/docs/")
        if yml is not None:
            r.put("specs/mk-specs.yml", yml)
        for rel, content in files.items():
            r.put(rel, content)
        return r

    def test_ac3_implemented_blocks_production_warns_staging(self):
        r = self.repo({"specs/changes/261027-dat-mon/proposal.md": proposal("implemented (code 1cbf29b)")})
        res = r.check("production")
        self.assertEqual(res.returncode, 1, res.stdout)
        msg = "code xong nhưng spec chưa hợp nhất: 261027-dat-mon — nhờ mk-specs merge"
        self.assertIn("CHẶN: " + msg, lines(res))
        res = r.check("staging")
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("CẢNH BÁO: " + msg, lines(res))

    def test_ac3_approved_warns_everywhere_draft_and_archive_ignored(self):
        r = self.repo({"specs/changes/261027-b/proposal.md": proposal("approved (sau review)"),
                       "specs/changes/261027-a/proposal.md": proposal("draft"),
                       "specs/changes/archive/261001-old/proposal.md": proposal("implemented")})
        for env_name in ("production", "staging"):
            res = r.check(env_name)
            self.assertEqual(res.returncode, 0, res.stdout)
            warn = [l for l in lines(res) if "261027-" in l]
            self.assertEqual(len(warn), 1, res.stdout)
            self.assertTrue(warn[0].startswith("CẢNH BÁO:") and "261027-b" in warn[0], warn)
            self.assertNotIn("261001-old", res.stdout)

    def test_ac3_specs_dir_from_config(self):
        r = self.repo({"docs/spec/changes/261027-c/proposal.md": proposal("implemented"),
                       "specs/changes/261027-d/proposal.md": proposal("implemented")},
                      yml="version: 1\nspecs_dir: docs/spec\n")
        res = r.check("production")
        self.assertIn("261027-c", res.stdout)
        self.assertNotIn("261027-d", res.stdout)

    def test_ac3_no_config_skips_spec_check_silently(self):
        r = self.repo({"specs/changes/261027-e/proposal.md": proposal("implemented")}, yml=None)
        res = r.check("production")
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertNotIn("261027-e", res.stdout)


def finding(n, verdict="xác nhận", level="cao", fixed=None, extra=""):
    out = f"### SEC-{n}: phát hiện {n}\n- Kết luận: {verdict}\n"
    if level is not None:
        out += f"- Mức: {level}\n"
    if fixed is not None:
        out += f"- Đã sửa: {fixed}\n"
    return out + "- Dấu vết: `src/index.ts:1`\n" + extra + "\n"


def sec_report(*findings):
    return ("# Báo cáo soát\n- Phạm vi: `secu.py scope`\n- Spec: chưa có\n- Người soát: a\n- Người kiểm: b\n\n"
            "## Phát hiện\n\n" + "".join(findings) + "## Chưa soát\n- —\n")


class CheckSecurity(unittest.TestCase):
    """UC-901 AC-4."""

    def repo(self, report, name="261027-soat-dat-mon.md", yml=SPEC_YML):
        r = ready_repo(self)
        r.exclude("/specs/")
        if yml is not None:
            r.put("specs/mk-specs.yml", yml)
        r.put("specs/security/" + name, report)
        return r

    def test_ac4_critical_blocks_every_environment(self):
        r = self.repo(sec_report(finding(1, level="nghiêm trọng")))
        for env_name in ("staging", "production"):
            res = r.check(env_name)
            self.assertEqual(res.returncode, 1, res.stdout)
            self.assertIn("CHẶN: lỗ hổng nghiêm trọng chưa sửa: 261027-soat-dat-mon SEC-1", res.stdout)

    def test_ac4_high_and_unreadable_level_block_production_warn_staging(self):
        r = self.repo(sec_report(finding(1, level="cao"), finding(2, level=None), finding(3, level="rất tệ")))
        res = r.check("production")
        self.assertEqual(res.returncode, 1, res.stdout)
        for n in (1, 2, 3):
            self.assertIn(f"CHẶN: lỗ hổng cao chưa sửa: 261027-soat-dat-mon SEC-{n}", lines(res))
        res = r.check("staging")
        self.assertEqual(res.returncode, 0, res.stdout)
        for n in (1, 2, 3):
            self.assertIn(f"CẢNH BÁO: lỗ hổng cao chưa sửa: 261027-soat-dat-mon SEC-{n}", lines(res))

    def test_ac4_fix_must_be_an_ancestor_of_head(self):
        r = ready_repo(self)
        r.exclude("/specs/")
        r.put("src/fix.ts", "fixed\n")
        good = r.commit("fix")
        r.git("checkout", "-q", "-b", "other")
        r.put("src/other.ts", "x\n")
        elsewhere = r.commit("fix elsewhere")
        r.git("checkout", "-q", "main")
        missing = "abcdef1234567"
        r.put("specs/security/261027-soat.md", sec_report(
            finding(1, fixed=f"commit {good[:7]}"), finding(2, fixed=f"commit {elsewhere}"),
            finding(3, fixed=f"commit {missing}"), finding(4, fixed="—")))
        res = r.check("production")
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertNotIn("SEC-1", res.stdout)
        note = " (commit sửa chưa có trong bản triển khai)"
        self.assertIn("CHẶN: lỗ hổng cao chưa sửa: 261027-soat SEC-2" + note, lines(res))
        self.assertIn("CHẶN: lỗ hổng cao chưa sửa: 261027-soat SEC-3" + note, lines(res))
        self.assertIn("CHẶN: lỗ hổng cao chưa sửa: 261027-soat SEC-4", lines(res))

    def test_ac4_medium_low_warn_unverified_counted_rejected_and_fenced_ignored(self):
        fenced = "```\n### SEC-9: ví dụ\n- Kết luận: xác nhận\n- Mức: nghiêm trọng\n```\n"
        r = self.repo(sec_report(finding(1, level="trung bình"), finding(2, level="thấp"),
                                 finding(3, verdict="cần kiểm thêm", level=None),
                                 finding(4, verdict="Cần kiểm thêm", level=None),
                                 finding(5, verdict="bác bỏ", level=None, extra=fenced)))
        res = r.check("production")
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("CẢNH BÁO: lỗ hổng trung bình chưa sửa: 261027-soat-dat-mon SEC-1", lines(res))
        self.assertIn("CẢNH BÁO: lỗ hổng thấp chưa sửa: 261027-soat-dat-mon SEC-2", lines(res))
        unverified = [l for l in lines(res) if "cần kiểm thêm" in l]
        self.assertEqual(unverified, ["CẢNH BÁO: 2 phát hiện bảo mật cần kiểm thêm, chưa kết luận"])
        self.assertNotIn("SEC-9", res.stdout)
        self.assertNotIn("SEC-5", res.stdout)

    def test_ac4_file_name_pattern_and_specs_dir(self):
        r = self.repo(sec_report(finding(1, level="nghiêm trọng")), name="ghi-chu.md")
        self.assertEqual(r.check("staging").returncode, 0)
        r = self.repo(sec_report(finding(1, level="nghiêm trọng")), yml=None)   # no mk-specs.yml: specs/security
        self.assertEqual(r.check("staging").returncode, 1)
        r = ready_repo(self)
        r.exclude("/specs/")
        r.exclude("/docs/")
        r.put("specs/mk-specs.yml", "specs_dir: docs/spec\n")
        r.put("docs/spec/security/261027-a.md", sec_report(finding(1, level="nghiêm trọng")))
        self.assertIn("261027-a SEC-1", r.check("staging").stdout)


class CheckConfig(unittest.TestCase):
    """UC-901 AC-5."""

    def test_ac5_no_config_blocks(self):
        r = ready_repo(self, wrangler=None)
        res = r.check()
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertTrue(any(l.startswith("CHẶN: không thấy cấu hình wrangler") for l in lines(res)), res.stdout)

    def test_ac5_lookup_order_warns_when_several(self):
        json_cfg = '{"name": "dat-mon", "main": "src/index.ts", "compatibility_date": "%s"}' % PAST
        r = ready_repo(self, extra_files={"wrangler.json": json_cfg})
        res = r.check()
        self.assertEqual(res.returncode, 1, res.stdout)   # wrangler.json wins and has no env.staging
        self.assertIn("CẢNH BÁO: có nhiều file cấu hình wrangler: wrangler.json, wrangler.jsonc — wrangler dùng "
                      "wrangler.json", lines(res))
        self.assertIn("CHẶN: wrangler.json: không có `env.staging` mà lệnh của staging dùng", lines(res))

    def test_ac5_config_flag_cwd_and_header_line(self):
        table = ENV_TABLE.replace("deploy --env staging", "deploy -c apps/api/wrangler.jsonc --env=staging") \
                         .replace("deploy --env production", "deploy --cwd apps/web -e production")
        r = ready_repo(self, deploy=deploy_md(env_table=table), wrangler=None,
                       extra_files={"apps/api/wrangler.jsonc": WRANGLER,
                                    "apps/web/wrangler.toml": f'name = "web"\nmain = "i.ts"\n'
                                                              f'compatibility_date = "{PAST}"\n[env.production]\n'})
        self.assertEqual(r.check("staging").returncode, 0, r.check("staging").stdout)
        self.assertEqual(r.check("production").returncode, 0, r.check("production").stdout)
        r = ready_repo(self, deploy=deploy_md(extra="- Cấu hình: `apps/x/wrangler.jsonc`\n"), wrangler=None,
                       extra_files={"apps/x/wrangler.jsonc": WRANGLER})
        self.assertEqual(r.check("staging").returncode, 0, r.check("staging").stdout)
        r = ready_repo(self, deploy=deploy_md(extra="- Cấu hình: apps/missing.jsonc\n"))
        res = r.check("staging")
        self.assertIn("CHẶN: không thấy file cấu hình apps/missing.jsonc", lines(res))

    def test_ac5_env_flag_forms(self):
        ship = load_ship()
        for cmd in ("npx --no wrangler deploy --env x", "npx --no wrangler deploy --env=x",
                    "pnpm exec wrangler deploy -e x", "yarn wrangler deploy -e=x",
                    "CLOUDFLARE_ENV=x npx --no wrangler deploy"):
            self.assertEqual(ship.command_flags(cmd)["env"], "x", cmd)
        flags = ship.command_flags("npx --no wrangler deploy --config a/w.toml --cwd b")
        self.assertEqual((flags["config"], flags["cwd"], flags["env"]), ("a/w.toml", "b", None))

    def test_ac5_missing_env_section_blocks(self):
        for flag in ("--env qa", "--env=qa", "-e qa", "-e=qa"):
            table = ENV_TABLE.replace("--env staging", flag)
            r = ready_repo(self, deploy=deploy_md(env_table=table))
            res = r.check("staging")
            self.assertEqual(res.returncode, 1, (flag, res.stdout))
            self.assertIn("CHẶN: wrangler.jsonc: không có `env.qa` mà lệnh của staging dùng", lines(res))
        table = ENV_TABLE.replace("`npx --no wrangler deploy --env staging`", "`CLOUDFLARE_ENV=qa npx --no wrangler deploy`")
        r = ready_repo(self, deploy=deploy_md(env_table=table))
        self.assertIn("env.qa", r.check("staging").stdout)

    def test_ac5_unreadable_config_names_line(self):
        r = ready_repo(self, wrangler='{\n  "name": "a",\n  "main": oops\n}\n')
        res = r.check()
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertTrue(any(l.startswith("CHẶN: không đọc được wrangler.jsonc: dòng 3") for l in lines(res)), res.stdout)

    def test_ac5_required_keys_and_dates(self):
        cases = (
            (WRANGLER.replace('"name": "dat-mon",', ""), "CHẶN: wrangler.jsonc: thiếu `name`"),
            (WRANGLER.replace(PAST, FUTURE), f"CHẶN: wrangler.jsonc: `compatibility_date` {FUTURE} sau ngày UTC hôm nay"),
            (WRANGLER.replace(PAST, "2026-02-30"), "CHẶN: wrangler.jsonc: `compatibility_date` không phải ngày YYYY-MM-DD hợp lệ"),
            (WRANGLER.replace(f'"compatibility_date": "{PAST}",', ""), "CHẶN: wrangler.jsonc: thiếu `compatibility_date`"),
            (WRANGLER.replace('"main": "src/index.ts",', ""),
             "CHẶN: wrangler.jsonc: thiếu `main` (hoặc `assets.directory` cho trang tĩnh)"),
        )
        for cfg, want in cases:
            r = ready_repo(self, wrangler=cfg)
            res = r.check()
            self.assertEqual(res.returncode, 1, (want, res.stdout))
            self.assertTrue(any(l.startswith(want) for l in lines(res)), (want, res.stdout))
        r = ready_repo(self, wrangler=WRANGLER.replace('"main": "src/index.ts",', '"assets": {"directory": "./public"},'))
        self.assertEqual(r.check().returncode, 0, r.check().stdout)

    def test_ac5_vite_plugin_downgrades_missing_main_to_warning(self):
        pkg = '{"devDependencies": {"@cloudflare/vite-plugin": "^1.0.0", "wrangler": "^4.0.0"}}'
        r = ready_repo(self, wrangler=WRANGLER.replace('"main": "src/index.ts",', ""), extra_files={"package.json": pkg})
        res = r.check()
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertTrue(any(l.startswith("CẢNH BÁO: wrangler.jsonc:") and "vite-plugin" in l for l in lines(res)))

    def test_ac5_toml_bare_date_must_be_string(self):
        toml = f'name = "dat-mon"\nmain = "src/index.ts"\ncompatibility_date = {PAST}\n[env.staging]\n'
        r = ready_repo(self, wrangler=None, extra_files={"wrangler.toml": toml})
        res = r.check()
        try:
            import tomllib  # noqa: F401
        except ImportError:
            self.skipTest("tomllib needs Python 3.11")
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn('CHẶN: wrangler.toml: `compatibility_date` phải là chuỗi "YYYY-MM-DD"', lines(res))

    def test_ac5_toml_without_tomllib_warns_and_skips(self):
        ship = load_ship()
        ship.tomllib = None
        r = ready_repo(self, wrangler=None, extra_files={"wrangler.toml": 'name = "x"\n'})
        out = io.StringIO()
        old = dict(os.environ)
        os.environ.update(r.env)
        try:
            with contextlib.redirect_stdout(out):
                code = ship.check(r.root, "staging")
        finally:
            os.environ.clear()
            os.environ.update(old)
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("CẢNH BÁO: không đọc được wrangler.toml (cần Python ≥ 3.11) — bỏ kiểm khoá bắt buộc, env, "
                      "bí mật trong vars", out.getvalue().splitlines())

    def test_ac5_bindings_without_id_warn_auto_provisioning(self):
        cfg = WRANGLER.replace('"staging": {', '"staging": { "kv_namespaces": [{"binding": "CACHE"}], '
                                              '"d1_databases": [{"binding": "DB", "database_name": "d"}], '
                                              '"r2_buckets": [{"binding": "FILES"}, {"binding": "OK", "bucket_name": "b"}],')
        r = ready_repo(self, wrangler=cfg)
        res = r.check()
        self.assertEqual(res.returncode, 0, res.stdout)
        warn = [l for l in lines(res) if "tự tạo tài nguyên" in l]
        self.assertEqual(len(warn), 3, res.stdout)
        self.assertTrue(all(l.startswith("CẢNH BÁO:") and "tạo trước và commit" in l for l in warn))
        self.assertTrue(any("CACHE" in l for l in warn) and any("DB" in l for l in warn) and any("FILES" in l for l in warn))

    def test_ac5_jsonc_strings_survive_comment_and_comma_stripping(self):
        ship = load_ship()
        text = ('{\n  // c\n  "a": "example.com/*", /* x */\n  "b": "https://a.b",\n  "c": "a,]",\n'
                '  "d": ["/api/*", ],\n  "e": "q\\"//x",\n}\n')
        data = ship.parse_jsonc(text)
        self.assertEqual(data, {"a": "example.com/*", "b": "https://a.b", "c": "a,]", "d": ["/api/*"], "e": 'q"//x'})


class CheckSecrets(unittest.TestCase):
    """UC-901 AC-6."""

    BLOCKED = ("JWT_SECRET", "GITHUB_TOKEN", "DB_PASSWORD", "OPENAI_API_KEY", "STRIPE_KEY", "PRIVATE_KEY", "apiKey",
               "DB_PWD", "CREDENTIALS", "KEY", "DB_PASS", "GITHUB_PAT")
    PASSED = ("MAX_TOKENS", "TOKEN_URL", "PUBLIC_KEY", "TURNSTILE_SITE_KEY", "STRIPE_PUBLISHABLE_KEY",
              "AWS_ACCESS_KEY_ID", "KEY_ID", "PASSWORD_MIN_LENGTH", "PRIVATE_BETA", "CSRF_TOKEN_HEADER", "API_URL",
              "CACHE_KEY", "TOKEN_LIMIT", "SORT_KEY", "PARTITION_KEY", "IDEMPOTENCY_KEY", "TOKEN_MAX", "RETRY_COUNT",
              "TOKEN_SIZE", "PATH", "PASSPORT_URL")

    def test_ac6_secret_name_rule_rows(self):
        ship = load_ship()
        for name in self.BLOCKED:
            self.assertTrue(ship.secret_name(name), name)
        for name in self.PASSED:
            self.assertFalse(ship.secret_name(name), name)

    def test_ac6_secret_in_vars_blocks_without_printing_value(self):
        value = cat("s3cr", "etvalue", "42")
        db = cat("postgres://u", ":", "pw", "x9z@db.example.com/app")
        cfg = WRANGLER.replace('"MAX_TOKENS": "512"', f'"MAX_TOKENS": "512", "JWT_SECRET": "{value}", "DATABASE_URL": "{db}"')
        cfg = cfg.replace('"observability"', f'"vars": {{ "apiKey": "{value}" }},\n  "observability"')
        r = ready_repo(self, wrangler=cfg)
        res = r.check()
        self.assertEqual(res.returncode, 1, res.stdout)
        hint = "(người dùng tự chạy); giá trị đã commit → chủ dự án thu hồi/đổi khoá"
        for key in ("JWT_SECRET", "DATABASE_URL", "apiKey"):
            self.assertIn(f"CHẶN: bí mật trong vars: {key} — dùng `wrangler secret put {key} --env staging` {hint}",
                          lines(res))
        table = ENV_TABLE.replace("`npx --no wrangler deploy --env staging`",
                                  "`CLOUDFLARE_ENV=staging npx --no wrangler deploy`")
        r = ready_repo(self, deploy=deploy_md(env_table=table), wrangler=cfg)
        self.assertIn(f"CHẶN: bí mật trong vars: JWT_SECRET — dùng `CLOUDFLARE_ENV=staging wrangler secret put "
                      f"JWT_SECRET` {hint}", lines(r.check()))
        self.assertNotIn("MAX_TOKENS", res.stdout)
        self.assertNotIn(value, res.stdout)
        self.assertNotIn("x9z", res.stdout)

    def test_ac6_tracked_secret_files_block_any_platform(self):
        files = {".env": "A=1\n", "apps/api/.dev.vars.staging": "A=1\n", "web/.env.production.local": "A=1\n",
                 ".env.example": "A=\n", ".dev.vars.example": "A=\n", "x/.env.sample": "A=\n", ".envrc": "A=\n",
                 ".env.template": "A=\n", "y/.dev.vars.dist": "A=\n"}
        r = ready_repo(self, deploy=deploy_md(platform="khác (vercel)"), wrangler=None, extra_files=files)
        res = r.check()
        self.assertEqual(res.returncode, 1, res.stdout)
        got = [l for l in lines(res) if l.startswith("CHẶN: file bí mật")]
        self.assertEqual(got, ["CHẶN: file bí mật đang nằm trong git: .env",
                               "CHẶN: file bí mật đang nằm trong git: apps/api/.dev.vars.staging",
                               "CHẶN: file bí mật đang nằm trong git: web/.env.production.local"])

    def test_ac6_secret_in_command_blocks_and_command_not_printed(self):
        token = cat("tok", "enval", "ue123")
        for cmd in (f"CLOUDFLARE_API_TOKEN={token} npx --no wrangler deploy --env staging",
                    f"npx --no wrangler deploy --env staging --var JWT_SECRET:{token}",
                    f"npx --no wrangler deploy --env staging --var=API_KEY:{token}"):
            table = ENV_TABLE.replace("npx --no wrangler deploy --env staging", cmd)
            r = ready_repo(self, deploy=deploy_md(env_table=table))
            res = r.check()
            self.assertEqual(res.returncode, 1, (cmd, res.stdout))
            self.assertIn("CHẶN: bí mật trong lệnh triển khai của staging — dùng biến môi trường của máy/CI", lines(res))
            self.assertNotIn(token, res.stdout)
            self.assertNotIn("Lệnh:", res.stdout)
        table = ENV_TABLE.replace("npx --no wrangler deploy --env staging",
                                  "CLOUDFLARE_ENV=staging npx --no wrangler deploy --var MAX_TOKENS:512")
        self.assertEqual(ready_repo(self, deploy=deploy_md(env_table=table)).check().returncode, 0)

    def test_ac6_vars_only_checked_for_workers(self):
        cfg = WRANGLER.replace('"MAX_TOKENS": "512"', '"JWT_SECRET": "x"')
        r = ready_repo(self, deploy=deploy_md(platform="cloudflare-pages"), wrangler=cfg)
        self.assertEqual(r.check().returncode, 0, r.check().stdout)


class CheckOk(unittest.TestCase):
    """UC-901 AC-7 and the order of lines."""

    def test_ac7_clean_production_prints_summary_and_ok(self):
        r = ready_repo(self)
        head = r.git("rev-parse", "HEAD")
        res = r.check("production")
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertEqual(lines(res), [
            f"Môi trường: production (production) · Nền tảng: cloudflare-workers · Commit: {head[:7]} · "
            "Lệnh: npx --no wrangler deploy --env production", "OK"])
        res = r.check("staging")
        self.assertEqual(lines(res)[0].split(" · ")[0], "Môi trường: staging (thử)")

    def test_ac7_other_platforms_skip_workers_config(self):
        for platform in ("khác (vercel)", "cloudflare-pages"):
            table = ENV_TABLE.replace("npx --no wrangler deploy --env production", "npx --no vercel deploy --prod")
            r = ready_repo(self, deploy=deploy_md(platform=platform, env_table=table), wrangler=None)
            res = r.check("production")
            self.assertEqual(res.returncode, 0, (platform, res.stdout))
            self.assertIn(f"Nền tảng: {platform}", res.stdout)

    def test_line_order_is_deploy_git_spec_security_config_secrets(self):
        table = "\n".join(l for l in ENV_TABLE.splitlines() if "| production |" not in l) + "\n"
        r = ready_repo(self, deploy=deploy_md(env_table=table),
                       wrangler=WRANGLER.replace('"MAX_TOKENS": "512"', '"JWT_SECRET": "x"').replace(PAST, FUTURE))
        r.exclude("/specs/")
        r.put("specs/mk-specs.yml", SPEC_YML)
        r.put("specs/changes/261027-a/proposal.md", proposal("implemented"))
        r.put("specs/security/261027-s.md", sec_report(finding(1, level="nghiêm trọng")))
        r.put("dirty.txt", "x\n")
        res = r.check("staging")
        self.assertEqual(res.returncode, 1, res.stdout)
        keys = ["không có môi trường production", "còn thay đổi chưa commit", "spec chưa hợp nhất",
                "lỗ hổng nghiêm trọng", "compatibility_date", "bí mật trong vars"]
        pos = [next(i for i, l in enumerate(lines(res)) if k in l) for k in keys]
        self.assertEqual(pos, sorted(pos), res.stdout)

    def test_check_is_deterministic_and_leaves_repo_clean(self):
        r = ready_repo(self)
        a, b = r.check("production"), r.check("production")
        self.assertEqual(a.stdout, b.stdout)
        self.assertEqual(r.git("status", "--porcelain"), "")


class CheckRound2(unittest.TestCase):
    """Round 2 (dry-run + code review): branch with a same-name tag, template placeholders, env not chosen,
    `- Cấu hình:` that wrangler would not find on its own."""

    def test_branch_name_with_same_name_tag(self):
        r = ready_repo(self)
        r.git("tag", "main")
        res = r.check("production")
        self.assertEqual(res.returncode, 0, res.stdout)

    def test_unfilled_template_placeholders_block(self):
        table = ENV_TABLE.replace("https://dat-mon.example.com", "https://<tên miền>")
        extra = "<!-- ghi chú có <tên> trong chú thích -->\n"
        md = deploy_md(env_table=table, extra=extra) + "- Lệnh mẫu: `wrangler d1 migrations list <db>`\n- <TÊN_BÍ_MẬT>\n"
        r = ready_repo(self, deploy=md)
        res = r.check("staging")
        self.assertEqual(res.returncode, 1, res.stdout)
        got = [l for l in lines(res) if "chỗ trống mẫu" in l]
        self.assertEqual(len(got), 1, res.stdout)
        self.assertTrue(got[0].startswith("CHẶN: DEPLOY.md còn chỗ trống mẫu ở dòng "), got)
        n_url = md.split("\n").index(next(l for l in md.split("\n") if "<tên miền>" in l)) + 1
        n_secret = md.split("\n").index("- <TÊN_BÍ_MẬT>") + 1
        self.assertIn(f"dòng {n_url}, {n_secret}", got[0])

    def test_test_env_command_without_env_warns_root_worker(self):
        table = ENV_TABLE.replace("npx --no wrangler deploy --env staging", "npx --no wrangler deploy")
        r = ready_repo(self, deploy=deploy_md(env_table=table))
        res = r.check("staging")
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("CẢNH BÁO: lệnh của staging không chọn env — sẽ triển khai Worker gốc", lines(res))
        r = ready_repo(self, deploy=deploy_md(env_table=table),
                       wrangler=WRANGLER.replace('"env": {', '"x_env": {'))   # no env.* → nothing to warn about
        self.assertNotIn("không chọn env", r.check("staging").stdout)

    def test_config_line_differs_from_wrangler_lookup_warns(self):
        r = ready_repo(self, deploy=deploy_md(extra="- Cấu hình: apps/api/wrangler.jsonc\n"),
                       extra_files={"apps/api/wrangler.jsonc": WRANGLER})
        res = r.check("staging")
        self.assertEqual(res.returncode, 0, res.stdout)
        warn = [l for l in lines(res) if "- Cấu hình:" in l]
        self.assertEqual(len(warn), 1, res.stdout)
        self.assertTrue(warn[0].startswith("CẢNH BÁO:") and "wrangler.jsonc" in warn[0] and "-c" in warn[0], warn)
        table = ENV_TABLE.replace("deploy --env staging", "deploy -c apps/api/wrangler.jsonc --env staging")
        r = ready_repo(self, deploy=deploy_md(env_table=table, extra="- Cấu hình: apps/api/wrangler.jsonc\n"),
                       extra_files={"apps/api/wrangler.jsonc": WRANGLER})
        self.assertNotIn("- Cấu hình:", r.check("staging").stdout)


# ---------------------------------------------------------------- UC-902 smoke


NFC_TEXT = unicodedata.normalize("NFC", "Đặt món")
NFD_TEXT = unicodedata.normalize("NFD", "Đặt món")


class Handler(http.server.BaseHTTPRequestHandler):
    routes = {}
    seen_agents = []

    def do_GET(self):
        Handler.seen_agents.append(self.headers.get("User-Agent"))
        route = Handler.routes.get(self.path.split("?")[0])
        if route is None:
            self.send_response(404)
            self.end_headers()
            return
        status, body, headers, delay = route
        if delay:
            time.sleep(delay)
        try:
            if callable(body):
                body(self)
                return
            self.send_response(status)
            for k, v in headers.items():
                self.send_header(k, v)
            data = body if isinstance(body, bytes) else body.encode("utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except OSError:
            pass

    def log_message(self, *args):
        pass


class Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False


class Smoke(unittest.TestCase):
    """UC-902 AC-1, AC-2, AC-3."""

    @classmethod
    def setUpClass(cls):
        cls.server = Server(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_address[1]
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        Handler.routes = {}
        self.repo = Repo(self)

    def route(self, path, status=200, body="", headers=None, delay=0):
        Handler.routes[path] = (status, body, headers or {"Content-Type": "text/html; charset=utf-8"}, delay)

    def smoke(self, rows, *args, env_table=ENV_TABLE, url=True, timeout=None):
        smoke = "## Kiểm sau triển khai\n| Đường dẫn | Mã | Có chữ |\n|---|---|---|\n" + "".join(
            f"| {p} | {c} | {t} |\n" for p, c, t in rows) if rows is not None else ""
        self.repo.put("DEPLOY.md", deploy_md(env_table=env_table, smoke=smoke))
        cmd = ["smoke", "--env", "staging"]
        if url is True:
            cmd += ["--url", self.base_url]
        elif url:
            cmd += ["--url", url]
        if timeout:
            cmd += ["--timeout", str(timeout)]
        return self.repo.ship(*cmd, *args)

    def test_ac1_one_ok_one_500(self):
        self.route("/", body=f"<h1>{NFC_TEXT}</h1>")
        self.route("/api/health", status=500, body="boom")
        res = self.smoke([("/", "200", "Đặt món"), ("/api/health", "200", "—")])
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertEqual(lines(res), ["OK: /", "HỎNG: /api/health — mã 500 (cần 200)", "1/2 OK"])
        self.assertNotIn("boom", res.stdout)
        self.assertIn("mk-ship-smoke", Handler.seen_agents)

    def test_ac1_all_ok_exits_0(self):
        self.route("/", body=f"<h1>{NFC_TEXT}</h1>")
        self.route("/api/health", body="ok")
        res = self.smoke([("/", "200", "Đặt món"), ("/api/health", "200", "")])
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertEqual(lines(res), ["OK: /", "OK: /api/health", "2/2 OK"])

    def test_ac1_env_url_from_table(self):
        self.route("/", body="x")
        table = ENV_TABLE.replace("https://dat-mon-staging.example.workers.dev", self.base_url + "/")
        res = self.smoke([("/", "200", "—")], env_table=table, url=False)
        self.assertEqual(res.returncode, 0, res.stdout)

    def test_ac2_missing_text(self):
        self.route("/", body="<h1>Thực đơn</h1>")
        res = self.smoke([("/", "200", "Đặt món")])
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertEqual(lines(res), ['HỎNG: / — thiếu chữ "Đặt món"', "0/1 OK"])

    def test_ac2_connection_refused(self):
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        res = self.smoke([("/", "200", "—")], url=f"http://127.0.0.1:{port}")
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertTrue(lines(res)[0].startswith("HỎNG: / — không kết nối được: "), res.stdout)

    def test_ac2_slow_response_times_out(self):
        self.route("/", body="x", delay=2.5)
        start = time.monotonic()
        res = self.smoke([("/", "200", "—")], timeout=1)
        self.assertLess(time.monotonic() - start, 2.4)
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertEqual(lines(res), ["HỎNG: / — quá 1 giây", "0/1 OK"])

    def test_ac2_redirect_to_other_host_is_not_followed(self):
        self.route("/", status=302, headers={"Location": "https://login.example.net/auth?next=/"})
        res = self.smoke([("/", "200", "—")])
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertEqual(lines(res)[0], "HỎNG: / — chuyển hướng ra ngoài: login.example.net")

    def test_ac2_same_origin_redirect_is_followed(self):
        self.route("/", status=301, headers={"Location": "/vi/"})
        self.route("/vi/", body=NFC_TEXT)
        res = self.smoke([("/", "200", "Đặt món")])
        self.assertEqual(res.returncode, 0, res.stdout)

    def test_ac2_redirect_loop_stops_after_five(self):
        self.route("/", status=302, headers={"Location": "/"})
        res = self.smoke([("/", "200", "—")])
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertEqual(lines(res), ["HỎNG: / — quá 5 lần chuyển hướng", "0/1 OK"])

    def test_ac2_trickling_body_hits_total_timeout(self):
        def trickle(h):
            h.send_response(200)
            h.send_header("Content-Type", "text/html")
            h.end_headers()
            for _ in range(10):
                h.wfile.write(b"x")
                h.wfile.flush()
                time.sleep(0.4)
        self.route("/", body=trickle)
        start = time.monotonic()
        res = self.smoke([("/", "200", "—")], timeout=1)
        self.assertLess(time.monotonic() - start, 2.0)
        self.assertEqual(lines(res), ["HỎNG: / — quá 1 giây", "0/1 OK"])

    def test_ac2_reads_at_most_one_mib(self):
        self.route("/", body="a" * (1048576 + 10) + NFC_TEXT)
        self.route("/head", body=NFC_TEXT + "a" * (1048576 + 10))
        res = self.smoke([("/", "200", "Đặt món"), ("/head", "200", "Đặt món")])
        self.assertEqual(lines(res), ['HỎNG: / — thiếu chữ "Đặt món"', "OK: /head", "1/2 OK"])

    def test_ac2_non_ascii_path_and_location_are_quoted(self):
        self.route(urllib.parse.quote("/thực-đơn"), body=NFC_TEXT)
        self.route("/cu", status=302, headers={"Location": "/caf\u00e9"})
        self.route("/caf%C3%A9", body="ok")
        res = self.smoke([("/thực-đơn", "200", "Đặt món"), ("/cu", "200", "—")])
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(lines(res), ["OK: /thực-đơn", "OK: /cu", "2/2 OK"])

    def test_ac2_redirect_to_other_port_scheme_or_bad_port(self):
        self.route("/port", status=302, headers={"Location": "http://127.0.0.1:1/"})
        self.route("/tls", status=302, headers={"Location": f"https://127.0.0.1:{self.port}/"})
        self.route("/bad", status=302, headers={"Location": "http://127.0.0.1:99999/"})
        res = self.smoke([("/port", "200", "—"), ("/tls", "200", "—"), ("/bad", "200", "—")])
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertEqual(lines(res), ["HỎNG: /port — chuyển hướng ra ngoài: http://127.0.0.1:1",
                                      f"HỎNG: /tls — chuyển hướng ra ngoài: https://127.0.0.1:{self.port}",
                                      "HỎNG: /bad — chuyển hướng không hợp lệ", "0/3 OK"])

    def test_ac3_unfilled_template_url_exits_2_without_traceback(self):
        res = self.smoke([("/", "200", "—")], url="https://<tên miền>")
        self.assertEqual((res.returncode, res.stderr), (2, ""), res.stdout + res.stderr)
        self.assertIn("URL không hợp lệ", res.stdout)
        self.assertNotIn("tên miền", res.stdout)
        table = ENV_TABLE.replace("https://dat-mon-staging.example.workers.dev", "https://<tên>-staging.<tk>.workers.dev")
        res = self.smoke([("/", "200", "—")], env_table=table, url=False)
        self.assertEqual((res.returncode, res.stderr), (2, ""), res.stdout + res.stderr)
        self.assertNotIn("<tên>", res.stdout)

    def test_ac2_nfd_page_matches_nfc_text(self):
        self.route("/", body=f"<p>{NFD_TEXT}</p>")
        res = self.smoke([("/", "200", NFC_TEXT)])
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertEqual(lines(res), ["OK: /", "1/1 OK"])

    def test_ac2_charset_from_header(self):
        self.route("/", body="café".encode("latin-1"), headers={"Content-Type": "text/html; charset=iso-8859-1"})
        res = self.smoke([("/", "200", "café")])
        self.assertEqual(res.returncode, 0, res.stdout)

    def test_ac3_no_smoke_table_exits_2(self):
        res = self.smoke(None)
        self.assertEqual(res.returncode, 2, res.stdout)
        self.assertIn("DEPLOY.md chưa có kiểm sau triển khai", res.stdout)

    def test_ac3_bad_url_exits_2(self):
        for url in ("ftp://example.com", "example.com", "http://"):
            res = self.smoke([("/", "200", "—")], url=url)
            self.assertEqual(res.returncode, 2, (url, res.stdout))
            self.assertIn("URL không hợp lệ", res.stdout)

    def test_ac3_url_with_password_exits_2_and_hides_it(self):
        pw = cat("hun", "ter", "22")
        url = cat("https://admin:", pw, "@example.com")
        res = self.smoke([("/", "200", "—")], url=url)
        self.assertEqual(res.returncode, 2, res.stdout)
        self.assertIn("URL chứa mật khẩu", res.stdout)
        self.assertNotIn(pw, res.stdout + res.stderr)
        table = ENV_TABLE.replace("https://dat-mon-staging.example.workers.dev", url)
        res = self.smoke([("/", "200", "—")], env_table=table, url=False)
        self.assertEqual(res.returncode, 2, res.stdout)
        self.assertNotIn(pw, res.stdout + res.stderr)

    def test_ac3_bad_status_cell_exits_2(self):
        for code in ("abc", "99", "600", "", "200 OK"):
            res = self.smoke([("/", "200", "—"), ("/x", code, "—")])
            self.assertEqual(res.returncode, 2, (code, res.stdout))
            self.assertIn("mã không hợp lệ ở dòng /x", res.stdout)

    def test_unknown_env_without_url_exits_2(self):
        table = ENV_TABLE.replace("| staging |", "| dev |")
        res = self.smoke([("/", "200", "—")], env_table=table, url=False)
        self.assertEqual(res.returncode, 2, res.stdout)


if __name__ == "__main__":
    unittest.main()
