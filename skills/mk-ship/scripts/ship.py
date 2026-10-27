#!/usr/bin/env python3
"""mk-ship: gate before a deploy (check) and HTTP check after it (smoke). Never runs a deploy.

Usage:
  python3 <skill>/scripts/ship.py check --env <name> [--root DIR]
  python3 <skill>/scripts/ship.py smoke --env <name> [--url <base>] [--timeout <seconds>] [--root DIR]

DEPLOY.md (repo root): `- Nền tảng: cloudflare-workers | cloudflare-pages | khác (<name>)`, optional
`- Cấu hình: <wrangler file>`, tables `## Môi trường` (| Môi trường | Nhánh | Lệnh triển khai | URL |) and
`## Kiểm sau triển khai` (| Đường dẫn | Mã | Có chữ |). Cells lose backticks; `\\|` is a literal pipe.

check (read-only; every git call uses `git --no-optional-locks`; dates in UTC). Lines in this order:
  DEPLOY.md (file, platform, environment row, a production row exists) → git (clean tree incl. untracked files
  not ignored, branch cell `*`/name, detached HEAD equal to refs/heads/<b> or refs/remotes/<r>/<b>) → spec
  (specs/mk-specs.yml present: proposals under <specs_dir>/changes/<slug>/, not archive/, first word of Status
  `implemented` blocks production / warns elsewhere, `approved` warns) → security (<specs_dir>/security/
  <yyMMdd-slug>.md, read like secu.py: confirmed findings not fixed by an ancestor commit of HEAD; nghiêm trọng
  blocks everywhere, cao — or a missing/unreadable level — blocks production, the rest warn; `cần kiểm thêm`
  counted in one warning) → config (cloudflare-workers only: -c/--config, else `- Cấu hình:`, else
  wrangler.json → wrangler.jsonc → wrangler.toml in --cwd; name, compatibility_date string YYYY-MM-DD not after
  today, main or assets.directory, env.<x> of --env/-e/CLOUDFLARE_ENV; bindings without ids warn) → secrets
  (secret-looking keys in vars, tracked .env/.dev.vars files, secrets assigned in the deploy command).
  Production = name production/prod or ending -production/-prod (case-insensitive).
  Exit 0 → summary line and `OK` (with `CẢNH BÁO:` lines) · 1 → `CHẶN:` lines · 2 → bad call, not a git repo.
smoke: GET <--url or the environment URL><path> per row, User-Agent mk-ship-smoke, ≤ 5 redirects on the same
  scheme+host+port, --timeout seconds in total per row, ≤ 1 MiB read, decoded by charset (default UTF-8), NFC.
  Prints `OK: <path>` / `HỎNG: <path> — <reason>`, then `<ok>/<total> OK`. Exit 0 all OK · 1 any failure ·
  2 bad DEPLOY.md/URL/status cell. Never prints page content or URL credentials.
Standard library only (tomllib when available); output is deterministic.
"""
import argparse
import datetime
import http.client
import json
import os
import re
import shlex
import socket
import subprocess
import sys
import threading
import time
import unicodedata
import urllib.parse

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

sys.dont_write_bytecode = True

ENV_NAME = re.compile(r"[A-Za-z0-9_-]+")
PLATFORMS = ("cloudflare-workers", "cloudflare-pages")
OTHER = re.compile(r"^khác\s*\(\s*([^()]*\S)\s*\)$")
CONFIG_NAMES = ("wrangler.json", "wrangler.jsonc", "wrangler.toml")
REPORT_NAME = re.compile(r"^\d{6}-[a-z0-9-]+\.md$")
FINDING = re.compile(r"^###\s+(SEC-\d+)\b")
HEADING = re.compile(r"^#{1,3}\s")
FIELD = re.compile(r"^- ([^:\n`]{1,40}):[ \t]*(.*)$")
HASH = re.compile(r"commit\W*([0-9a-fA-F]{7,40})(?![0-9A-Za-z])")
LEVELS = ("nghiêm trọng", "cao", "trung bình", "thấp")
VERDICTS = ("xác nhận", "cần kiểm thêm", "bác bỏ")
ASSIGN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", re.S)
URL_PASSWORD = re.compile(r"://[^\s/@:]*:[^\s/@]+@")
SAFE_LAST = {"URL", "URI", "ENDPOINT", "HEADER", "NAME", "ID", "TTL", "LENGTH", "TYPE", "ENABLED",
             "LIMIT", "MAX", "COUNT", "SIZE"}
SECRET_PARTS = {"SECRET", "TOKEN", "PASSWORD", "PASSWD", "PWD", "PASS", "PAT", "CREDENTIALS", "APIKEY"}
PUBLIC_BEFORE_KEY = {"PUBLIC", "PUBLISHABLE", "SITE", "CACHE", "SORT", "PARTITION", "IDEMPOTENCY"}
PLACEHOLDER = re.compile(r"<(?![\s\d=<>!/-]|https?:)[^<>\n]+>")
ENV_EXEMPT = {"example", "sample", "template", "dist"}
BINDINGS = (("kv_namespaces", "id"), ("d1_databases", "database_id"), ("r2_buckets", "bucket_name"))
MAX_BODY = 1048576
MAX_REDIRECTS = 5
USER_AGENT = "mk-ship-smoke"
URL_SAFE = "/?&=%:@!$'()*+,;~"
NO_TEXT = ("", "—", "–", "-")


class BadCall(Exception):
    pass


def nfc(text):
    return unicodedata.normalize("NFC", text or "")


def is_production(name):
    n = name.lower()
    return n in ("production", "prod") or n.endswith(("-production", "-prod"))


# ---------- DEPLOY.md ----------

def split_row(line):
    """Cells of a markdown table row: split on unescaped `|`, `\\|` kept as `|`, backticks dropped."""
    cells, cur, i, s = [], "", 0, line.strip()
    while i < len(s):
        if s[i] == "\\" and s[i + 1:i + 2] == "|":
            cur += "|"
            i += 2
            continue
        if s[i] == "|":
            cells.append(cur)
            cur = ""
        else:
            cur += s[i]
        i += 1
    cells.append(cur)
    if s.startswith("|"):
        cells = cells[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        cells = cells[:-1]
    return [c.replace("`", "").strip() for c in cells]


def unfenced(text):
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return out


def section_table(lines, title):
    """Rows (dicts keyed by lower-cased header) of the first table under `## <title>`; None without the section."""
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and nfc(line[3:]).strip().lower().startswith(title.lower()):
            start = i + 1
            break
    if start is None:
        return None
    rows, header = [], None
    for line in lines[start:]:
        if line.startswith("## ") or line.startswith("# "):
            break
        if not line.strip().startswith("|"):
            if header is not None and rows is not None and line.strip():
                break
            continue
        cells = split_row(line)
        if header is None:
            header = [nfc(c).lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-{2,}:?", c or "") or c == "" for c in cells) and not rows:
            continue
        rows.append({header[k] if k < len(header) else str(k): nfc(v) for k, v in enumerate(cells)})
    return rows


def cell(row, name, index):
    if name in row:
        return row[name]
    keys = list(row)
    return row[keys[index]] if index < len(keys) else ""


def header_value(lines, key):
    for line in lines:
        m = FIELD.match(line)
        if m and nfc(m.group(1)).strip() == key:
            return nfc(m.group(2)).replace("`", "").strip()
    return None


def placeholder_lines(text):
    """Line numbers holding a template placeholder `<…>` outside HTML comments, ``` fences and backticks."""
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    hits, fenced = [], False
    for n, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced and PLACEHOLDER.search(re.sub(r"`[^`\n]*`", "", line)):
            hits.append(n)
    return hits


class Deploy:
    def __init__(self, text):
        self.lines = [nfc(l) for l in unfenced(text)]
        self.placeholders = placeholder_lines(text)
        self.platform_raw = header_value(self.lines, "Nền tảng")
        self.config = header_value(self.lines, "Cấu hình") or None
        self.envs = section_table(self.lines, "Môi trường") or []
        self.smoke = section_table(self.lines, "Kiểm sau triển khai")

    def platform(self):
        v = (self.platform_raw or "").strip()
        if v.lower() in PLATFORMS:
            return v.lower()
        if OTHER.match(v):
            return v
        return None

    def env(self, name):
        for row in self.envs:
            if cell(row, "môi trường", 0) == name:
                return {"branch": cell(row, "nhánh", 1), "command": cell(row, "lệnh triển khai", 2),
                        "url": cell(row, "url", 3)}
        return None

    def has_production(self):
        return any(is_production(cell(r, "môi trường", 0)) for r in self.envs)


def read_deploy(root):
    try:
        with open(os.path.join(root, "DEPLOY.md"), encoding="utf-8-sig", errors="replace") as fh:
            return Deploy(fh.read())
    except OSError:
        return None


# ---------- git ----------

def git(root, *args, ok=(0,)):
    try:
        res = subprocess.run(["git", "--no-optional-locks", "-C", root] + list(args), capture_output=True)
    except OSError:
        return None
    return res.stdout if res.returncode in ok else None


def text_of(out):
    return nfc((out or b"").decode("utf-8", "surrogateescape")).strip()


def toplevel(path):
    out = git(path, "rev-parse", "--show-toplevel")
    return os.path.realpath(text_of(out)) if out is not None else None


def dirty_paths(root):
    out = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all") or b""
    items = out.decode("utf-8", "surrogateescape").split("\0")
    paths, i = set(), 0
    while i < len(items):
        rec = items[i]
        i += 1
        if len(rec) < 4:
            continue
        paths.add(nfc(rec[3:]))
        if rec[0] in "RC" or rec[1] in "RC":  # rename/copy: the source path follows as its own record
            if i < len(items) and items[i]:
                paths.add(nfc(items[i]))
            i += 1
    return sorted(paths)


def is_ancestor(root, commit):
    if git(root, "rev-parse", "--verify", "--quiet", commit + "^{commit}") is None:
        return False
    return git(root, "merge-base", "--is-ancestor", commit, "HEAD") is not None


# ---------- spec config (approach copied from mk-secu secu.py; ADR-29: no cross-skill import) ----------

def yaml_scalar(cfg, key_re):
    m = re.search(key_re + r"\s*(?:'([^'\n]*)'|\"((?:[^\"\\\n]|\\.)*)\"|([^\s#]+))", cfg, re.M)
    if not m:
        return None
    if m.group(2) is not None:
        try:
            return json.loads('"' + m.group(2) + '"')
        except ValueError:
            return None
    return m.group(1) if m.group(1) is not None else m.group(3)


def spec_config(root):
    """(has_config, specs_dir) from <root>/specs/mk-specs.yml."""
    try:
        with open(os.path.join(root, "specs", "mk-specs.yml"), encoding="utf-8") as fh:
            cfg = fh.read()
    except (OSError, UnicodeDecodeError):
        return False, "specs"
    return True, yaml_scalar(cfg, r"^specs_dir:") or "specs"


def first_word(value):
    m = re.match(r"[`*\s]*([^\s`*(]+)", value or "")
    return m.group(1).lower() if m else ""


def proposal_status(path):
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as fh:
            head = fh.read().split("\n## ", 1)[0]
    except OSError:
        return ""
    m = re.search(r"(?:^- |· )Status:\s*([^·\n]*)", head, re.M)
    return first_word(m.group(1)) if m else ""


def norm(value):
    return nfc(value).strip().strip("`*_ ").strip()


def choice(value, options):
    """The option the value starts with (case-insensitive, whole words), else None."""
    v = norm(value).lower()
    for opt in sorted(options, key=len, reverse=True):
        if v == opt or (v.startswith(opt) and not v[len(opt)].isalnum()):
            return opt
    return None


def findings(text):
    """[(SEC id, fields)] of a mk-secu report; lines inside ``` fences ignored, first value of a field wins."""
    out, current, fenced = [], None, False
    for line in nfc(text).split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if HEADING.match(line):
            m = FINDING.match(line)
            current = {} if m else None
            if m:
                out.append((m.group(1), current))
            continue
        m = FIELD.match(line)
        if m and current is not None:
            current.setdefault(norm(m.group(1)), m.group(2))
    return out


# ---------- wrangler config ----------

def strip_jsonc(text):
    """JSONC → JSON: drop // and /* */ comments and trailing commas outside strings; newlines kept."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("\n" * text.count("\n", i, j))
            i = j
        else:
            out.append(c)
            i += 1
    s = "".join(out)
    res, i, in_str = [], 0, False
    while i < len(s):
        c = s[i]
        if in_str:
            res.append(c)
            if c == "\\" and i + 1 < len(s):
                res.append(s[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            res.append(c)
        elif c == ",":
            j = i + 1
            while j < len(s) and s[j] in " \t\r\n":
                j += 1
            if j >= len(s) or s[j] not in "]}":
                res.append(c)
        else:
            res.append(c)
        i += 1
    return "".join(res)


def parse_jsonc(text):
    return json.loads(strip_jsonc(text))


def command_tokens(command):
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def command_flags(command):
    """{env, env_form, config, cwd} of a deploy command (`--env x`, `--env=x`, `-e x`, `-e=x`, CLOUDFLARE_ENV=x).

    env_form is "prefix" when the env comes from a CLOUDFLARE_ENV= assignment, "flag" for --env/-e, else None."""
    toks = command_tokens(command)
    flags = {"env": None, "env_form": None, "config": None, "cwd": None}
    names = {"--env": "env", "-e": "env", "--config": "config", "-c": "config", "--cwd": "cwd"}
    i = 0
    while i < len(toks) and ASSIGN.match(toks[i]):
        m = ASSIGN.match(toks[i])
        if m.group(1) == "CLOUDFLARE_ENV":
            flags["env"], flags["env_form"] = m.group(2), "prefix"
        i += 1
    for j, tok in enumerate(toks):
        key, _, val = tok.partition("=")
        if key in names:
            if val or "=" in tok:
                flags[names[key]] = val
            elif j + 1 < len(toks):
                flags[names[key]] = toks[j + 1]
            if names[key] == "env":
                flags["env_form"] = "flag"
    return flags


def load_config(path, rel, block, warn):
    """Parsed dict, or None (with a CHẶN/CẢNH BÁO line added)."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as e:
        block(f"không đọc được {rel}: {e.__class__.__name__}")
        return None
    if path.endswith(".toml"):
        if tomllib is None:
            warn(f"không đọc được {rel} (cần Python ≥ 3.11) — bỏ kiểm khoá bắt buộc, env, bí mật trong vars")
            return None
        try:
            data = tomllib.loads(raw.decode("utf-8-sig"))
        except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
            block(f"không đọc được {rel}: {e}")
            return None
    else:
        try:
            data = parse_jsonc(raw.decode("utf-8-sig"))
        except UnicodeDecodeError:
            block(f"không đọc được {rel}: không phải UTF-8")
            return None
        except ValueError as e:
            block(f"không đọc được {rel}: dòng {getattr(e, 'lineno', '?')}: {getattr(e, 'msg', e)}")
            return None
    if not isinstance(data, dict):
        block(f"không đọc được {rel}: gốc phải là một object")
        return None
    return data


def find_config(root, deploy, flags, block, warn):
    """(absolute path, path shown) of the wrangler config of a command, or (None, None)."""
    cwd = os.path.normpath(os.path.join(root, flags["cwd"])) if flags["cwd"] else root
    explicit = flags["config"] and os.path.normpath(os.path.join(cwd, flags["config"]))
    if not explicit and deploy.config:
        explicit = os.path.normpath(os.path.join(root, deploy.config))
        auto = next((os.path.join(cwd, n) for n in CONFIG_NAMES if os.path.isfile(os.path.join(cwd, n))), None)
        if auto is None or os.path.normpath(auto) != explicit:
            shown = os.path.relpath(explicit, root).replace(os.sep, "/")
            found = os.path.relpath(auto, root).replace(os.sep, "/") if auto else "không thấy file nào"
            warn(f"`- Cấu hình:` là {shown} nhưng lệnh không có -c — wrangler tự tìm được {found}; "
                 f"thêm `-c {shown}` vào lệnh")
    if explicit:
        rel = os.path.relpath(explicit, root).replace(os.sep, "/")
        if not os.path.isfile(explicit):
            block(f"không thấy file cấu hình {rel}")
            return None, None
        return explicit, rel
    found = [n for n in CONFIG_NAMES if os.path.isfile(os.path.join(cwd, n))]
    where = os.path.relpath(cwd, root).replace(os.sep, "/")
    prefix = "" if where == "." else where + "/"
    if not found:
        block(f"không thấy cấu hình wrangler ({', '.join(CONFIG_NAMES)}) ở {'gốc repo' if not prefix else where}")
        return None, None
    if len(found) > 1:
        warn(f"có nhiều file cấu hình wrangler: {', '.join(prefix + f for f in found)} — wrangler dùng {prefix + found[0]}")
    return os.path.join(cwd, found[0]), prefix + found[0]


def vite_plugin(root, cwd):
    for d in sorted({cwd, root}):
        try:
            with open(os.path.join(d, "package.json"), encoding="utf-8-sig") as fh:
                pkg = json.load(fh)
        except (OSError, ValueError):
            continue
        if not isinstance(pkg, dict):
            continue
        for key in ("dependencies", "devDependencies"):
            deps = pkg.get(key)
            if isinstance(deps, dict) and "@cloudflare/vite-plugin" in deps:
                return True
    return False


def check_config(data, rel, env_x, env_name, root, cwd, block, warn):
    """Required keys, env section, bindings; returns the env section used (or None)."""
    section = None
    if env_x:
        envs = data.get("env")
        section = envs.get(env_x) if isinstance(envs, dict) else None
        if not isinstance(section, dict):
            block(f"{rel}: không có `env.{env_x}` mà lệnh của {env_name} dùng")
            section = None

    def eff(key):
        if section is not None and key in section:
            return section[key]
        return data.get(key)

    if not isinstance(eff("name"), str) or not eff("name").strip():
        block(f"{rel}: thiếu `name`")
    date = eff("compatibility_date")
    if date is None:
        block(f"{rel}: thiếu `compatibility_date`")
    elif not isinstance(date, str):
        block(f'{rel}: `compatibility_date` phải là chuỗi "YYYY-MM-DD"')
    else:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                raise ValueError
            day = datetime.date.fromisoformat(date)
        except ValueError:
            block(f"{rel}: `compatibility_date` không phải ngày YYYY-MM-DD hợp lệ")
        else:
            today = datetime.datetime.now(datetime.timezone.utc).date()
            if day > today:
                block(f"{rel}: `compatibility_date` {date} sau ngày UTC hôm nay ({today.isoformat()})")
    assets = eff("assets")
    has_assets = isinstance(assets, dict) and isinstance(assets.get("directory"), str) and assets["directory"].strip()
    if not (isinstance(eff("main"), str) and eff("main").strip()) and not has_assets:
        if vite_plugin(root, cwd):
            warn(f"{rel}: không có `main` hay `assets.directory` — dự án dùng @cloudflare/vite-plugin, bỏ kiểm")
        else:
            block(f"{rel}: thiếu `main` (hoặc `assets.directory` cho trang tĩnh)")
    scope = section if env_x else data
    for key, id_key in BINDINGS:
        items = (scope or {}).get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and not item.get(id_key):
                label = item.get("binding") or "?"
                warn(f"{rel}: {key} {label} thiếu `{id_key}`: wrangler sẽ tự tạo tài nguyên và ghi mã vào file "
                     "cấu hình — tạo trước và commit")
    return section


# ---------- secrets ----------

def name_parts(name):
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name)
    return [p.upper() for p in re.split(r"[_\-]+", spaced) if p]


def secret_name(name):
    parts = name_parts(name)
    if not parts or parts[-1] in SAFE_LAST:
        return False
    if any(p in SECRET_PARTS for p in parts):
        return True
    return parts[-1] == "KEY" and (len(parts) == 1 or parts[-2] not in PUBLIC_BEFORE_KEY)


def secret_vars(data, section):
    keys = []
    for scope in (data, section):
        v = scope.get("vars") if isinstance(scope, dict) else None
        if not isinstance(v, dict):
            continue
        for k in sorted(v):
            val = v[k]
            if secret_name(k) or (isinstance(val, str) and URL_PASSWORD.search(val)):
                if k not in keys:
                    keys.append(k)
    return keys


def secret_file(path):
    name = path.rsplit("/", 1)[-1]
    if name in (".env", ".dev.vars"):
        return True
    for base in (".env.", ".dev.vars."):
        if name.startswith(base) and len(name) > len(base):
            return name.rsplit(".", 1)[1].lower() not in ENV_EXEMPT
    return False


def secret_command(command):
    toks = command_tokens(command)
    if URL_PASSWORD.search(command):
        return True
    in_var = False
    for tok in toks:
        m = ASSIGN.match(tok)
        if tok.startswith("--var="):
            in_var, tok = True, tok[len("--var="):]
        elif tok == "--var":
            in_var = True
            continue
        elif tok.startswith("-"):
            in_var = False
            continue
        elif m and not in_var:
            if secret_name(m.group(1)):
                return True
            continue
        if in_var and ":" in tok and secret_name(tok.split(":", 1)[0]):
            return True
    return False


# ---------- check ----------

def check(root, env_name):
    root = os.path.realpath(root)
    top = toplevel(root)
    if top is None:
        raise BadCall(f"không phải repo git: {root}")
    root = top
    out = []
    block = lambda msg: out.append("CHẶN: " + msg)  # noqa: E731
    warn = lambda msg: out.append("CẢNH BÁO: " + msg)  # noqa: E731
    prod = is_production(env_name)
    deploy = read_deploy(root)
    row, platform = None, None
    if deploy is None:
        block("chưa có DEPLOY.md — tạo cùng người dùng từ mẫu của mk-ship")
    else:
        platform = deploy.platform()
        if platform is None:
            block("DEPLOY.md thiếu hoặc sai `- Nền tảng:` — cần cloudflare-workers, cloudflare-pages hoặc khác (<tên>)")
        if not deploy.has_production():
            warn("DEPLOY.md không có môi trường production nào (production, prod, *-production, *-prod)")
        if deploy.placeholders:
            block("DEPLOY.md còn chỗ trống mẫu ở dòng " + ", ".join(str(n) for n in deploy.placeholders)
                  + " — điền hoặc xoá")
        row = deploy.env(env_name)
        if row is None:
            block(f"DEPLOY.md không có môi trường {env_name}")
        elif not row["command"]:
            block(f"DEPLOY.md thiếu lệnh triển khai của {env_name}")

    # git
    head = text_of(git(root, "rev-parse", "--verify", "--quiet", "HEAD"))
    if not head:
        block("chưa có commit nào")
    dirty = dirty_paths(root)
    if dirty:
        block("còn thay đổi chưa commit — chỉ triển khai cái đã commit")
        out.extend("  " + p for p in dirty)
    if row is not None and head:
        want = row["branch"]
        if not want:
            block(f"DEPLOY.md thiếu nhánh của {env_name}")
        elif want != "*":
            ref = text_of(git(root, "symbolic-ref", "--quiet", "HEAD"))
            current = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ""
            if current and current != want:
                block(f"đang ở nhánh {current}, môi trường {env_name} cần nhánh {want}")
            elif not current:
                refs = text_of(git(root, "for-each-ref", "--format=%(objectname) %(refname)", "refs/heads/",
                                   "refs/remotes/"))
                tips = set()
                for line in refs.splitlines():
                    obj, _, ref = line.partition(" ")
                    if ref == "refs/heads/" + want or re.fullmatch(r"refs/remotes/[^/]+/" + re.escape(want), ref):
                        tips.add(obj)
                if head not in tips:
                    block(f"HEAD tách rời, không trùng đầu nhánh {want}")

    # spec
    has_cfg, specs_dir = spec_config(root)
    if has_cfg:
        changes = os.path.join(root, specs_dir, "changes")
        try:
            slugs = sorted(d for d in os.listdir(changes) if d != "archive" and os.path.isdir(os.path.join(changes, d)))
        except OSError:
            slugs = []
        for slug in slugs:
            word = proposal_status(os.path.join(changes, slug, "proposal.md"))
            if word == "implemented":
                (block if prod else warn)(f"code xong nhưng spec chưa hợp nhất: {slug} — nhờ mk-specs merge")
            elif word == "approved":
                warn(f"proposal đã duyệt nhưng chưa code xong: {slug} — bản triển khai có thể thiếu thay đổi này")

    # security
    sec_dir = os.path.join(root, specs_dir, "security")
    try:
        reports = sorted(f for f in os.listdir(sec_dir) if REPORT_NAME.match(f))
    except OSError:
        reports = []
    unverified = 0
    for name in reports:
        try:
            with open(os.path.join(sec_dir, name), encoding="utf-8-sig", errors="replace") as fh:
                items = findings(fh.read())
        except OSError:
            continue
        for sid, f in items:
            verdict = choice(f.get("Kết luận"), VERDICTS)
            if verdict == "cần kiểm thêm":
                unverified += 1
            if verdict != "xác nhận":
                continue
            fixed = f.get("Đã sửa")
            m = HASH.search(fixed or "")
            if m and is_ancestor(root, m.group(1).lower()):
                continue
            level = choice(f.get("Mức"), LEVELS) or "cao"
            ref = f"{name[:-3]} {sid}"
            if norm(fixed).strip("—–-. "):
                ref += " (commit sửa chưa có trong bản triển khai)"
            msg = f"lỗ hổng {level} chưa sửa: {ref}"
            if level == "nghiêm trọng" or (level == "cao" and prod):
                block(msg)
            else:
                warn(msg)
    if unverified:
        warn(f"{unverified} phát hiện bảo mật cần kiểm thêm, chưa kết luận")

    # config (Workers only)
    data = section = None
    if row is not None and row["command"] and platform == "cloudflare-workers":
        flags = command_flags(row["command"])
        cwd = os.path.normpath(os.path.join(root, flags["cwd"])) if flags["cwd"] else root
        path, rel = find_config(root, deploy, flags, block, warn)
        if path:
            data = load_config(path, rel, block, warn)
            if data is not None:
                section = check_config(data, rel, flags["env"], env_name, root, cwd, block, warn)
                envs = data.get("env")
                if not flags["env"] and not prod and isinstance(envs, dict) and envs:
                    warn(f"lệnh của {env_name} không chọn env — sẽ triển khai Worker gốc")

    # secrets
    if data is not None:
        x, form = flags["env"], flags["env_form"]
        for key in secret_vars(data, section):
            put = f"wrangler secret put {key}"
            put = f"CLOUDFLARE_ENV={x} {put}" if x and form == "prefix" else (f"{put} --env {x}" if x else put)
            block(f"bí mật trong vars: {key} — dùng `{put}` (người dùng tự chạy); giá trị đã commit → chủ dự án "
                  "thu hồi/đổi khoá")
    tracked = (git(root, "ls-files", "-z") or b"").decode("utf-8", "surrogateescape").split("\0")
    for p in sorted(nfc(p) for p in tracked if p and secret_file(p)):
        block(f"file bí mật đang nằm trong git: {p}")
    if row is not None and row["command"] and secret_command(row["command"]):
        block(f"bí mật trong lệnh triển khai của {env_name} — dùng biến môi trường của máy/CI")

    for line in out:
        print(line)
    if any(l.startswith("CHẶN: ") for l in out):
        return 1
    kind = "production" if prod else "thử"
    print(f"Môi trường: {env_name} ({kind}) · Nền tảng: {platform} · Commit: {head[:7]} · Lệnh: {row['command']}")
    print("OK")
    return 0


# ---------- smoke ----------

def origin(parts):
    port = parts.port or (443 if parts.scheme == "https" else 80)
    return parts.scheme, (parts.hostname or "").lower(), port


def host_ok(parts):
    host = parts.hostname or ""
    if parts.netloc.startswith("["):
        return re.fullmatch(r"[0-9A-Fa-f:.]+", host) is not None
    return re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", host) is not None


def valid_url(url):
    """Parsed base URL; raises BadCall without echoing the URL."""
    bad = BadCall("URL không hợp lệ — cần http:// hoặc https://")
    try:
        parts = urllib.parse.urlsplit(url)
        parts.port  # noqa: B018 — raises on a bad port
    except ValueError:
        raise bad
    if parts.password is not None:
        raise BadCall("URL chứa mật khẩu — bỏ phần user:mật-khẩu@")
    if parts.scheme not in ("http", "https") or "@" in parts.netloc or not host_ok(parts):
        raise bad
    return parts


def show_host(parts):
    host = parts.hostname or "?"
    return f"{host}:{parts.port}" if parts.port else host


def fetch(url, deadline, follow, timeout):
    """(status, body bytes, charset) or raises _Fail(reason)."""
    home = origin(urllib.parse.urlsplit(url))
    for _ in range(MAX_REDIRECTS + 1):
        parts = urllib.parse.urlsplit(url)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _Fail(f"quá {timeout:g} giây")
        target = urllib.parse.quote(parts.path or "/", safe=URL_SAFE)
        if parts.query:
            target += "?" + urllib.parse.quote(parts.query, safe=URL_SAFE)
        conn = None
        try:
            cls = http.client.HTTPSConnection if parts.scheme == "https" else http.client.HTTPConnection
            conn = cls(parts.hostname, parts.port, timeout=remaining)
            conn.request("GET", target, headers={"User-Agent": USER_AGENT, "Accept": "*/*",
                                                 "Accept-Encoding": "identity"})
            resp = conn.getresponse()
            location = resp.getheader("Location")
            if follow and resp.status in (301, 302, 303, 307, 308) and location:
                try:
                    nxt = urllib.parse.urlsplit(urllib.parse.urljoin(url, location.strip()))
                    nxt_origin = origin(nxt)
                except ValueError:
                    raise _Fail("chuyển hướng không hợp lệ")
                if nxt.scheme not in ("http", "https") or not host_ok(nxt):
                    raise _Fail("chuyển hướng không hợp lệ")
                if nxt_origin[1] != home[1]:
                    raise _Fail(f"chuyển hướng ra ngoài: {show_host(nxt)}")
                if nxt_origin != home:
                    raise _Fail(f"chuyển hướng ra ngoài: {nxt.scheme}://{show_host(nxt)}")
                url = urllib.parse.urlunsplit((nxt.scheme, nxt.netloc, nxt.path, nxt.query, ""))
                continue
            body = b""
            while len(body) < MAX_BODY:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise socket.timeout()
                if conn.sock is not None:
                    conn.sock.settimeout(remaining)
                chunk = resp.read(min(65536, MAX_BODY - len(body)))
                if not chunk:
                    break
                body += chunk
            return resp.status, body, resp.headers.get_content_charset()
        except socket.timeout:
            raise _Fail(f"quá {timeout:g} giây")
        except ValueError:  # http.client.InvalidURL, bad IDNA host, control characters
            raise _Fail("URL không hợp lệ")
        except (OSError, http.client.HTTPException) as e:
            if isinstance(e, OSError) and e.strerror:
                detail = f"{e.__class__.__name__}: {e.strerror}"
            else:
                detail = e.__class__.__name__
            raise _Fail(f"không kết nối được: {detail}")
        finally:
            if conn is not None:
                conn.close()
    raise _Fail(f"quá {MAX_REDIRECTS} lần chuyển hướng")


def fetch_within(url, follow, timeout):
    """fetch() bounded by a wall-clock limit: a daemon thread joined for `timeout` seconds."""
    result = {}

    def run():
        try:
            result["ok"] = fetch(url, time.monotonic() + timeout, follow, timeout)
        except _Fail as e:
            result["fail"] = str(e)
        except Exception as e:  # never let one row kill the run
            result["fail"] = f"lỗi: {e.__class__.__name__}"

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(timeout)
    if worker.is_alive():
        raise _Fail(f"quá {timeout:g} giây")
    if "fail" in result:
        raise _Fail(result["fail"])
    return result["ok"]


class _Fail(Exception):
    pass


def smoke(root, env_name, url, timeout):
    top = toplevel(root)
    root = top or os.path.realpath(root)
    deploy = read_deploy(root)
    if deploy is None:
        raise BadCall("chưa có DEPLOY.md")
    if not deploy.smoke:
        raise BadCall("DEPLOY.md chưa có kiểm sau triển khai (bảng ## Kiểm sau triển khai)")
    if url is None:
        row = deploy.env(env_name)
        if row is None:
            raise BadCall(f"DEPLOY.md không có môi trường {env_name} — thêm dòng hoặc dùng --url")
        url = row["url"]
    base = valid_url(url)
    checks = []
    for r in deploy.smoke:
        path = cell(r, "đường dẫn", 0)
        code = cell(r, "mã", 1)
        want = cell(r, "có chữ", 2)
        if not re.fullmatch(r"\d{3}", code) or not 100 <= int(code) <= 599:
            raise BadCall(f"mã không hợp lệ ở dòng {path}")
        checks.append((path, int(code), "" if want in NO_TEXT else nfc(want)))
    root_url = urllib.parse.urlunsplit((base.scheme, base.netloc, base.path.rstrip("/"), "", ""))
    ok = 0
    for path, code, want in checks:
        full = root_url + (path if path.startswith("/") else "/" + path)
        try:
            status, body, charset = fetch_within(full, not 300 <= code < 400, timeout)
            if status != code:
                raise _Fail(f"mã {status} (cần {code})")
            if want:
                try:
                    page = body.decode(charset or "utf-8", "replace")
                except LookupError:
                    page = body.decode("utf-8", "replace")
                if want not in nfc(page):
                    raise _Fail(f'thiếu chữ "{want}"')
        except _Fail as e:
            print(f"HỎNG: {path} — {e}")
            continue
        ok += 1
        print(f"OK: {path}")
    print(f"{ok}/{len(checks)} OK")
    return 0 if ok == len(checks) else 1


def main():
    ap = argparse.ArgumentParser(description="mk-ship: kiểm trước khi triển khai (check), kiểm sau triển khai (smoke)")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check", help="kiểm trước khi triển khai")
    c.add_argument("--env", required=True)
    c.add_argument("--root", default=".")
    s = sub.add_parser("smoke", help="kiểm sau triển khai")
    s.add_argument("--env", required=True)
    s.add_argument("--url")
    s.add_argument("--timeout", type=float, default=10.0)
    s.add_argument("--root", default=".")
    args = ap.parse_args()
    if not args.cmd:
        ap.print_usage(sys.stderr)
        return 2
    if not ENV_NAME.fullmatch(args.env):
        print("tên môi trường không hợp lệ — chỉ chữ, số, _ và -")
        return 2
    try:
        if args.cmd == "check":
            return check(args.root, args.env)
        if not 0 < args.timeout <= 600:
            raise BadCall("--timeout phải trong khoảng (0, 600] giây")
        return smoke(args.root, args.env, args.url, args.timeout)
    except BadCall as e:
        print(str(e))
        return 2


if __name__ == "__main__":
    sys.exit(main())
