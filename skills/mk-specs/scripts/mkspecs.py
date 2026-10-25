"""Shared helpers for mk-specs scripts: config loading (YAML subset), spec discovery, metrics.

Standard library only. The config file `specs/mk-specs.yml` is parsed by `parse_yaml`, which supports
the subset documented in references/traceability.md: block mappings, block sequences (of scalars or
mappings), flow lists `[a, b]`, 'single'/"double"-quoted and plain scalars, ints, true/false/null,
and `#` comments. Anchors, multi-line scalars and flow mappings are not supported.
"""
import glob
import json
import os
import re
import subprocess
import sys

CONFIG_REL = os.path.join("specs", "mk-specs.yml")

IGNORED_SPECS_DIRS = {"changes", "_templates", "templates"}


class ConfigError(Exception):
    pass


# ── YAML subset ──

def _strip_comment(line):
    quote, i = None, 0
    while i < len(line):
        ch = line[i]
        if quote:
            if quote == '"' and ch == "\\":
                i += 1
            elif ch == quote and quote == "'" and line[i + 1:i + 2] == "'":
                i += 1
            elif ch == quote:
                quote = None
        elif ch in "'\"" and (i == 0 or line[i - 1] in " :[,-"):
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
        i += 1
    return line


def _split_flow(text):
    items, cur, quote = [], "", None
    for ch in text:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
            cur += ch
        elif ch == ",":
            items.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        items.append(cur.strip())
    return items


def _scalar(text):
    s = text.strip()
    if s.startswith("'"):
        if len(s) < 2 or not s.endswith("'"):
            raise ConfigError(f"unterminated quoted string: {s}")
        return s[1:-1].replace("''", "'")
    if s.startswith('"'):
        return json.loads(s)
    if s.startswith("["):
        if not s.endswith("]"):
            raise ConfigError(f"unterminated flow list: {s}")
        return [_scalar(x) for x in _split_flow(s[1:-1])]
    if s in ("null", "~", ""):
        return None
    if s in ("true", "false"):
        return s == "true"
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return s


_KEY = re.compile(r"""^(?:'((?:[^']|'')*)'|"((?:[^"\\]|\\.)*)"|([^'"\s][^:]*?))\s*:(?:\s+|$)""")


def _is_seq(content):
    return content == "-" or content.startswith("- ")


def _block(lines, i, indent):
    return _seq(lines, i, indent) if _is_seq(lines[i][1]) else _map(lines, i, indent)


def _map(lines, i, indent):
    out = {}
    while i < len(lines) and lines[i][0] == indent and not _is_seq(lines[i][1]):
        m = _KEY.match(lines[i][1])
        if not m:
            raise ConfigError(f"expected 'key: value', got: {lines[i][1]}")
        key = m.group(1).replace("''", "'") if m.group(1) is not None else (
            json.loads('"' + m.group(2) + '"') if m.group(2) is not None else m.group(3).strip())
        rest = lines[i][1][m.end():]
        i += 1
        if rest.strip():
            out[key] = _scalar(rest)
        elif i < len(lines) and (lines[i][0] > indent or (lines[i][0] == indent and _is_seq(lines[i][1]))):
            out[key], i = _block(lines, i, lines[i][0])
        else:
            out[key] = None
    if i < len(lines) and lines[i][0] > indent:
        raise ConfigError(f"unexpected indentation: {lines[i][1]}")
    return out, i


def _seq(lines, i, indent):
    out = []
    while i < len(lines) and lines[i][0] == indent and _is_seq(lines[i][1]):
        rest = lines[i][1][1:].lstrip()
        if not rest:
            i += 1
            if i < len(lines) and lines[i][0] > indent:
                item, i = _block(lines, i, lines[i][0])
            else:
                item = None
        elif _KEY.match(rest) and not rest.startswith(("'", '"', "[")) or re.match(r"""^['"][^'"]*['"]\s*:""", rest):
            sub = indent + len(lines[i][1]) - len(rest)
            lines[i] = (sub, rest)
            item, i = _map(lines, i, sub)
        else:
            item = _scalar(rest)
            i += 1
        out.append(item)
    return out, i


def parse_yaml(text):
    lines = []
    for raw in text.splitlines():
        if raw.strip() == "---":
            continue
        s = _strip_comment(raw).rstrip()
        if not s.strip():
            continue
        body = s.lstrip(" ")
        if body.startswith("\t"):
            raise ConfigError("tabs are not allowed for indentation")
        lines.append((len(s) - len(body), body))
    if not lines:
        return {}
    try:
        value, i = _block(lines, 0, lines[0][0])
    except (ValueError, RecursionError) as e:  # bad "\x" escape, huge int, lists nested thousands deep
        raise ConfigError(f"could not parse config: {str(e)[:120]}")
    if i != len(lines):
        raise ConfigError(f"could not parse line: {lines[i][1]}")
    return value


# ── config ──

DEFAULTS = {
    "version": 1,
    "language": "vi",
    "specs_dir": "specs",
    "layout": None,            # "layers" (Biến thể 1) | "contexts" (Biến thể 2)
    "contexts": None,          # [{id, title}] in output order
    "contexts_glob": None,     # e.g. "*" or "use-cases/*" when contexts is not listed
    "ids": {"uc": r"UC-\d+", "br": r"BR-\d+", "adr": r"ADR-\d+"},
    "decisions_file": "decisions.md",
    "tests": {
        "list_command": None,  # prints JSON [{"file": ..., "name": "describe > it"}] (vitest list --json)
        "file_pattern": r"[^`]+\.(?:test|spec)\.[cm]?[jt]sx?",
        "citation_style": "pointer",  # pointer | name | both
    },
    "readme": {
        "file": "README.md",
        "banner": {"match": r"^> (Cập nhật|Hợp nhất) ", "keep": 5},
        "lines": [],           # [{match: regex with named groups = metric keys}]
    },
    "metrics": {
        "since": None,         # YYYY-MM-DD; commits from this day count toward Trace Ratio
        "active_status": ["implemented", "partial"],
        "exempt_scopes": ["specs"],
    },
    "audit": {
        "required_sections": ["## History", "## Main Flow", "## Acceptance Criteria"],
        "recommended_sections": ["## Preconditions", "## Alternative Flows", "## Exceptions",
                                 "## Postconditions", "## Dependencies", "## Traceability",
                                 "## Divergences & Open Questions"],
        "metadata": ["Status", "BR"],
        "recommended_metadata": ["Owner"],
    },
}

TEXT = {
    "vi": {
        "no_test": "⚠ Chưa có test",
        "trace_head": (
            "# Traceability — UC ↔ AC ↔ Test\n\n"
            "> Sinh tự động từ các file `{specs}/*/UC-*.md` (dòng `- Tests:` dưới mỗi AC). Đừng sửa tay — sửa UC rồi sinh lại.\n"
            "> Mọi tên test ở đây đã được kiểm là có thật trong file test ({date}).\n\n"
            "| Context | UC | AC | Có test | ⚠ Chưa có test |\n|---|---|---|---|---|\n"
        ),
        "total": "Tổng",
        "oi_head": (
            "# Divergences & Open Questions — toàn bộ\n\n"
            "> Sinh tự động từ các dòng `[DIVERGENCE]` / `[OPEN]` trong `{specs}/`. Nguồn sự thật là file UC/ADR được link; sửa ở đó rồi sinh lại.\n"
            "> `[DIVERGENCE]` = tài liệu/plan nói một đằng, code làm một nẻo — **chưa quyết bên nào đúng**. `[OPEN]` = câu hỏi chưa có câu trả lời trong repo.\n"
            "> Danh sách đã lọc theo mức ảnh hưởng nằm ở `README.md` § \"Hàng đợi quyết định\".\n\n"
        ),
        "adr_section": "Quyết định (ADR)",
        "br_section": "Yêu cầu nghiệp vụ (BR)",
        "entity_section": "Thực thể (Entity)",
        "decimal": ",",
        "since_word": "từ",
    },
    "en": {
        "no_test": "⚠ No test",
        "trace_head": (
            "# Traceability — UC ↔ AC ↔ Test\n\n"
            "> Generated from `{specs}/*/UC-*.md` (the `- Tests:` line under each AC). Do not edit — edit the UC and regenerate.\n"
            "> Every test name here was checked to exist in its test file ({date}).\n\n"
            "| Context | UC | AC | Tested | ⚠ No test |\n|---|---|---|---|---|\n"
        ),
        "total": "Total",
        "oi_head": (
            "# Divergences & Open Questions — all\n\n"
            "> Generated from `[DIVERGENCE]` / `[OPEN]` lines in `{specs}/`. The linked UC/ADR file is the source of truth; edit there and regenerate.\n"
            "> `[DIVERGENCE]` = docs/plan say one thing, code does another — **not yet decided which is right**. `[OPEN]` = question without an answer in the repo.\n"
            "> The filtered list by impact lives in `README.md` § \"Decision queue\".\n\n"
        ),
        "adr_section": "Decisions (ADR)",
        "br_section": "Business requirements (BR)",
        "decimal": ".",
        "entity_section": "Entities",
        "since_word": "since",
    },
}


def _merge(base, over, key=""):
    """Defaults overlaid with the config; a value whose type cannot stand in for the default is refused (no traceback)."""
    if over is None:
        return base if key in ("ids", "tests", "readme", "metrics", "audit") else None
    if isinstance(base, dict):
        if not isinstance(over, dict):
            raise ConfigError(f"{key or 'config'} must be a mapping (key: value), got: {str(over)[:60]}")
        out = dict(base)
        for k, v in over.items():
            out[k] = _merge(base[k], v, f"{key}.{k}" if key else str(k)) if k in base else v
        return out
    if isinstance(base, list) and not isinstance(over, list):
        raise ConfigError(f"{key} must be a list, got: {str(over)[:60]}")
    return over


# Config regexes run on spec/test text. Heuristic (not a proof) against catastrophic backtracking: refuse a group that
# is repeated open-endedly ((…)+, (…)*, (…){2,}) while it, or a group inside it, has an open-ended quantifier or an
# alternation — (a+)+, (x(a+))*, (a|aa)+, (x(a|b))* — and very long patterns.
_Q = re.compile(r"[+*]|\{\d*,\d*\}")
MAX_REGEX = 500


def _may_hang(p):
    stack, i, n = [[False, False]], 0, len(p)  # per open group: [has quantifier inside, has alternation inside]
    while i < n:
        c = p[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":  # character class: nothing inside counts
            i += 2 if p[i + 1:i + 2] == "^" else 1
            i += 1 if p[i + 1:i + 2] == "]" else 0
            while i + 1 < n and p[i + 1] != "]":
                i += 2 if p[i + 1] == "\\" else 1
            i += 2
            continue
        if c == "(":
            stack.append([False, False])
        elif c == ")" and len(stack) > 1:
            quant, alt = stack.pop()
            m = _Q.match(p, i + 1)
            if m and (quant or alt):
                return True
            stack[-1][0] |= quant or bool(m)
            stack[-1][1] |= alt
            if m:
                i = m.end()
                continue
        elif c == "|":
            stack[-1][1] = True
        else:
            m = _Q.match(p, i)
            if m:
                stack[-1][0] = True
                i = m.end()
                continue
        i += 1
    return False


def safe_regex(pattern, key):
    pattern = str(pattern)
    if len(pattern) > MAX_REGEX or _may_hang(pattern):
        raise ConfigError(f"{key}: regex may hang (repeated group with a quantifier or '|' inside, or longer than {MAX_REGEX} "
                          f"chars): {pattern[:60]} — write it flat, e.g. 'UC-[\\d.]+' instead of 'UC-\\d+(?:\\.\\d+)*', "
                          "'[A-Z-]+' instead of '(U|UC|UC-)+'")
    try:
        re.compile(pattern)
    except re.error as e:
        raise ConfigError(f"{key}: invalid regex: {e}")
    return pattern


class Project:
    def __init__(self, root=".", config_path=None):
        self.root = os.path.abspath(root)
        path = config_path or os.path.join(self.root, CONFIG_REL)
        if not os.path.exists(path):
            raise ConfigError(f"config not found: {path} (run install.sh --project or mode init)")
        with open(path, encoding="utf-8") as fh:
            self.cfg = _merge(DEFAULTS, parse_yaml(fh.read()) or {})
        self.specs = self.inside(self.cfg["specs_dir"], self.root, "specs_dir")
        dec = self.cfg.get("decisions_file")
        self.decisions = self.inside(dec, self.specs, "decisions_file") if dec else None
        self.lang = self.cfg["language"] if self.cfg["language"] in TEXT else "vi"
        self.t = TEXT[self.lang]
        ids = self.cfg["ids"]
        for k in ("uc", "br", "adr"):
            if ids.get(k):
                safe_regex(ids[k], f"ids.{k}")
        if not ids.get("uc"):
            raise ConfigError("ids.uc is required (e.g. 'UC-\\d{3}')")
        safe_regex(self.cfg["tests"]["file_pattern"], "tests.file_pattern")
        rcfg = self.cfg["readme"]
        if rcfg.get("banner") is not None and not isinstance(rcfg["banner"], dict):
            raise ConfigError("readme.banner must be a mapping (match, keep) or null")
        if (rcfg.get("banner") or {}).get("match"):
            safe_regex(rcfg["banner"]["match"], "readme.banner.match")
        for spec in rcfg.get("lines") or []:
            if not isinstance(spec, dict):
                raise ConfigError(f"readme.lines items must be mappings with `match`, got: {str(spec)[:60]}")
            safe_regex(spec.get("match", ""), "readme.lines.match")
        self.uc_id = ids["uc"]
        self.id_patterns = [ids[k] for k in ("uc", "br", "adr") if ids.get(k)]
        self.uc_file = re.compile(rf"({self.uc_id})-.*\.md$")
        self.layout = self._validate_layout()
        self.contexts = self._contexts()

    def _validate_layout(self):
        raw = self.cfg.get("layout")
        if raw is None:
            return None
        val = str(raw).strip().lower()
        if val in ("layers", "bien-the-1", "1"):
            return "layers"
        if val in ("contexts", "bien-the-2", "2"):
            return "contexts"
        raise ConfigError(f"layout must be 'layers' (Biến thể 1) or 'contexts' (Biến thể 2), got: {str(raw)[:40]}")

    def _contexts(self):
        listed = self.cfg.get("contexts")
        if listed is not None and not isinstance(listed, list):
            raise ConfigError("contexts must be a list of {id, title}")
        if listed:
            out = []
            for c in listed:
                cid = c.get("id") if isinstance(c, dict) else c
                if not isinstance(cid, str) or not cid:
                    raise ConfigError(f"contexts: each item needs an id, got: {str(c)[:60]}")
                self.inside(cid, self.specs, "contexts[].id")
                out.append((cid, (c.get("title") if isinstance(c, dict) else None) or cid))
            missing = [c for c, _ in out if not os.path.isdir(os.path.join(self.specs, c))]
            if missing:
                raise ConfigError(f"context folder(s) missing under {self.cfg['specs_dir']}/: {', '.join(missing)} — "
                                  "create the folder or remove it from `contexts` in specs/mk-specs.yml "
                                  "(old templates listed an example `checkout`)")
            return out
        if self.layout == "contexts":
            patterns = ["*"]
        elif self.layout == "layers":
            patterns = ["use-cases/*", "use-cases"]
        elif self.cfg.get("contexts_glob"):
            patterns = [str(self.cfg["contexts_glob"])]
        elif os.path.isdir(os.path.join(self.specs, "use-cases")):
            patterns = ["use-cases/*", "use-cases"]
        else:
            patterns = ["*"]
        out = []
        seen = set()
        for pattern in patterns:
            self.inside(pattern, self.specs, "contexts_glob")
            for d in sorted(glob.glob(os.path.join(self.specs, pattern))):
                rel = os.path.relpath(d, self.specs).replace(os.sep, "/")
                if not self.is_inside(d):  # a folder linked to somewhere outside the repo is skipped, not read
                    continue
                first = rel.split("/", 1)[0]
                if first in IGNORED_SPECS_DIRS:
                    continue
                if os.path.isdir(d) and rel not in seen and any(self.uc_file.match(f) for f in os.listdir(d)):
                    seen.add(rel)
                    out.append((rel, rel))
        if "use-cases" not in seen and os.path.isdir(os.path.join(self.specs, "use-cases")):
            d = os.path.join(self.specs, "use-cases")
            if any(self.uc_file.match(f) for f in os.listdir(d)):
                seen.add("use-cases")
                out.append(("use-cases", "use-cases"))
        return out

    def uc_files(self, ctx):
        d = os.path.join(self.specs, ctx)
        files = [f for f in os.listdir(d) if self.uc_file.match(f)]
        return sorted(files, key=lambda f: natural_key(self.uc_file.match(f).group(1)))

    def known_ids(self):
        """IDs defined in specs: UC file names + headings `#… <ID>` (BR, ADR) outside changes/."""
        found = set()
        heading = re.compile(r"^#{1,6} (" + "|".join(f"(?:{p})" for p in self.id_patterns) + r")\b", re.M)
        for root, dirs, files in os.walk(self.specs):
            dirs[:] = [d for d in dirs if os.path.relpath(os.path.join(root, d), self.specs).split(os.sep)[0] not in IGNORED_SPECS_DIRS]
            for f in files:
                m = self.uc_file.match(f)
                if m:
                    found.add(m.group(1))
                if f.endswith(".md"):
                    found.update(heading.findall(read(os.path.join(root, f))))
        return found

    def is_inside(self, path):
        """True when path (symlinks resolved) lies in the repo."""
        root = os.path.realpath(self.root)
        try:
            return os.path.commonpath([os.path.realpath(path), root]) == root
        except ValueError:  # different drives on Windows
            return False

    def inside(self, rel, base, key):
        """Join a config path under base; refuse anything that resolves outside the repo (config is data)."""
        path = os.path.join(base, str(rel))
        if os.path.isabs(str(rel)) or not self.is_inside(path):
            raise ConfigError(f"{key} points outside the repo: {rel}")
        return path

    def test_list(self, tests_json=None, trust=False):
        """[(relative file, full test name)] from a JSON file or tests.list_command; None if unavailable.
        The command runs only when the user trusts it for this repo (see trust_file); otherwise exit EXIT_UNTRUSTED."""
        try:
            if tests_json:
                with open(tests_json, encoding="utf-8") as fh:
                    data = json.load(fh)
            else:
                cmd = self.cfg["tests"].get("list_command")
                if not cmd:
                    return None
                cmd = str(cmd)
                self._require_trust(cmd, trust)
                sys.stderr.write(f"mk-specs: running tests.list_command: {cmd}\n")
                res = subprocess.run(cmd, shell=True, cwd=self.root, capture_output=True, text=True)
                if res.returncode != 0:
                    sys.stderr.write(res.stderr)
                    raise ConfigError(f"tests.list_command failed ({res.returncode}): {cmd}")
                out = res.stdout
                start = out.find("[")
                data = json.loads(out[start:] if start >= 0 else out)
            return [(os.path.relpath(t["file"], self.root) if os.path.isabs(t["file"]) else t["file"], t["name"])
                    for t in data]
        except ConfigError as e:
            sys.exit(f"mk-specs: {e}")
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            sys.exit(f'mk-specs: test list is not JSON [{{"file": …, "name": …}}]: {str(e)[:120]}')

    def _require_trust(self, cmd, trust):
        """Return when `<repo real path>\\t<cmd>` is in the user's trusted list (added first with trust=True); else exit."""
        root, path = os.path.realpath(self.root), trust_file()
        if not (cmd.isprintable() and root.isprintable()):
            untrusted(ascii(cmd), path, "It contains control characters (tab, newline, escape…), so it cannot be trusted "
                                        "— pass --tests <list.json> instead.")
        if self.is_inside(path):
            untrusted(cmd, path, f"The trusted-commands list {path} resolves inside this repo, so it is ignored "
                                 "(set XDG_CONFIG_HOME to a folder outside the repo, or pass --tests <list.json>).")
        entry = f"{root}\t{cmd}"
        try:
            with open(path, encoding="utf-8") as fh:
                if entry in (line.rstrip("\n") for line in fh):
                    return
        except FileNotFoundError:
            pass
        except OSError as e:
            raise ConfigError(f"cannot read {path}: {e}")
        if not trust:
            untrusted(cmd, path, None)
        try:
            os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(entry + "\n")
        except OSError as e:
            raise ConfigError(f"cannot write {path}: {e} — pass --tests <list.json> instead")
        sys.stderr.write(f"mk-specs: trusted tests.list_command for {root} (saved in {path})\n")

    def commits(self):
        """Subjects of non-merge commits since metrics.since; None when not configured / not a git repo."""
        since = self.cfg["metrics"].get("since")
        if not since:
            return None
        since = str(since)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", since):
            since += "T00:00:00"
        res = subprocess.run(["git", "-C", self.root, "log", "--no-merges", f"--since={since}", "--format=%s"],
                             capture_output=True, text=True)
        if res.returncode != 0:
            return None
        return [l for l in res.stdout.split("\n") if l]

    def classify_commit(self, subject, known):
        """'traced' | 'exempt' | 'untraced' for a conventional-commit subject."""
        m = re.match(r"^[a-z]+(?:\(([^)]*)\))?!?: ", subject)
        scopes = [s.strip() for s in (m.group(1) or "").split(",")] if m else []
        if any(s in known and any(re.fullmatch(p, s) for p in self.id_patterns) for s in scopes):
            return "traced"
        if scopes and all(s in self.cfg["metrics"]["exempt_scopes"] for s in scopes):
            return "exempt"
        return "untraced"

    def pct(self, num, den):
        if not den:
            return "—"
        return f"{100 * num / den:.1f}%".replace(".", self.t["decimal"])


def natural_key(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def refuse_symlinks(*paths):
    """Exit before writing anything when one of the files to write is a symlink (a repo could link it anywhere)."""
    for path in paths:
        if path and os.path.islink(path):
            sys.exit(f"mk-specs: {path} is a symlink — refusing to write through it; replace it with a regular file")


def write_if_changed(path, text):
    refuse_symlinks(path)
    if os.path.exists(path) and read(path) == text:
        return False
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return True


# tests.list_command runs only when the user trusts it: exit code distinct from 1 (= the specs have errors).
EXIT_UNTRUSTED = 3


def trust_file():
    """The user's trusted list commands, outside every repo: one `<repo real path>\\t<command>` per line.
    $XDG_CONFIG_HOME/mk-specs/trusted-commands, else ~/.config/…; a relative XDG_CONFIG_HOME is ignored (XDG spec)."""
    base = os.environ.get("XDG_CONFIG_HOME", "")
    if not os.path.isabs(base):
        base = os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "mk-specs", "trusted-commands")


def untrusted(shown, path, reason):
    sys.stderr.write(
        "mk-specs: tests.list_command in specs/mk-specs.yml is not trusted for this repo, so it was NOT run:\n"
        f"  {shown}\n"
        + (f"{reason}\n" if reason else
           "It runs as a shell command with your permissions, together with the repo files it calls (scripts, test config).\n"
           "Read it. If you trust it, re-run with --trust-list-command (remembered in "
           f"{path} for this repo path and exactly this command; a changed command asks again).\n"
           "Or pass a test list instead: --tests <list.json>.\n")
        + "Agents: never add --trust-list-command yourself — show this command to the user and ask first.\n")
    sys.exit(EXIT_UNTRUSTED)


def load(argv_root=None, config=None):
    try:
        return Project(argv_root or os.getcwd(), config)
    except ConfigError as e:
        sys.exit(f"mk-specs: {e}")
