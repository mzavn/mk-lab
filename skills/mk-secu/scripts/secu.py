#!/usr/bin/env python3
"""mk-secu: check a security review report, or list the files a review must read. Read-only.

Usage:
  python3 <skill>/scripts/secu.py check <report.md> [--root DIR]
  python3 <skill>/scripts/secu.py scope [<path>] [--thay-doi [<base-branch>]]

check (root = --root, default cwd):
  - Header (before the first `## `/`### `): `- Phạm vi:`, `- Spec:` (`mức 4` | `chưa có`), `- Người soát:`,
    `- Người kiểm:`, none empty. `## Chưa soát` exists. `### SEC-n:` ids are unique.
  - `- Kết luận:` is `xác nhận` | `cần kiểm thêm` | `bác bỏ`. Only `xác nhận` has a `- Mức:`.
    xác nhận: Mức nghiêm trọng|cao|trung bình|thấp; Ai, Đầu vào, Kiểm soát thiếu, Ranh giới, Tài sản, Hậu quả,
    Đề xuất sửa not empty; Loại code sai AC|thiếu AC|luật sai|hạ tầng|chưa có spec; Lớp not empty;
    Dấu vết has a backticked `<path>:<line>` or `<path>:<a>-<b>` (path may hold spaces).
    `- Đã sửa: commit <7–40 hex>` only here. Any `- Lớp:` starts with a `### CODE —` code of the skill's
    references/catalog.md, or KHAC. A `SEC-n` heading of level other than 3 (outside fences) is blocked.
    cần kiểm thêm: `- Còn thiếu:`. bác bỏ: `- Lý do bác:`.
  - Loại code sai AC / luật sai: `- AC:` names `<UC-ID> AC-n`; when specs/mk-specs.yml exists, the UC file
    (`<UC-ID>-*.md` under specs_dir, not under changes/) has a `### AC-n` heading without `(deprecated`.
    Loại thiếu AC: `- Proposal:` slug is a folder in <specs_dir>/changes/.
  - No `<…>` placeholder outside backticks and ``` fences. No `](target)` anywhere (code included) whose
    target does not start with `#` or `<letters>:` (as mk-specs verify.py reads links).
  - No secret value (provider key formats, JWT, URL password, private key body): line numbers only.
  Passing prints `N phát hiện · xác nhận a (cao b, …) · cần kiểm thêm c · bác bỏ d`.
scope: tracked files (or, with --thay-doi, changed + untracked files; with a branch, also `<branch>...HEAD`),
  limited to <path> or the current subfolder, paths from the repo root; sensitive files flagged first, then
  skipped files listed with their reason. Every git call uses `git --no-optional-locks`.
Exit 0 pass · 1 blocked (`CHẶN:` lines) · 2 bad call / unreadable file / not a git repo / unknown branch.
Standard library only; output is deterministic.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata

sys.dont_write_bytecode = True

DEFAULT_UC = r"UC-\d+"
HEADER_KEYS = ("Phạm vi", "Spec", "Người soát", "Người kiểm")
SPEC_VALUES = ("mức 4", "chưa có")
VERDICTS = ("xác nhận", "cần kiểm thêm", "bác bỏ")
LEVELS = ("nghiêm trọng", "cao", "trung bình", "thấp")
TYPES = ("code sai AC", "thiếu AC", "luật sai", "hạ tầng", "chưa có spec")
FACTS = ("Ai", "Đầu vào", "Kiểm soát thiếu", "Ranh giới", "Tài sản", "Hậu quả")
FINDING = re.compile(r"^###\s+(SEC-\d+)\b")
TEMPLATE_PASSWORD = re.compile(r"\$\{[^}]+\}|\$[A-Z_][A-Z0-9_]*|\{\w*\}|%\(\w+\)s|<[^<>]+>")
HEADING = re.compile(r"^#{1,3}\s")
FIELD = re.compile(r"^- ([^:\n`]{1,40}):[ \t]*(.*)$")
BACKTICKS = re.compile(r"`[^`\n]*`")
PLACEHOLDER = re.compile(r"<(?![\s\d=<>-]|https?:)[^<>\n]+>")
LINK = re.compile(r"\]\(([^)\s]+)\)")
TRACE = re.compile(r"`[^`:\n]+:\d+(?:-\d+)?`")
HASH = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
AC_ID = re.compile(r"\bAC-\d+[a-z]?\b")
ID = re.compile(r"\b([A-Z][A-Z0-9]*-\d+[a-z]?)\b")
AC_HEADING = re.compile(r"^#{3,}\s+(AC-\d+[a-z]?)\b(.*)$")
QUANT = re.compile(r"[+*]|\{\d*(?:,\d*)?\}")
SECRETS = (
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}"),
    re.compile(r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{16,}"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    re.compile(r"\beyJ[\w-]{10,}\.eyJ[\w-]{10,}\.[\w-]{10,}"),
)
URL_PASSWORD = re.compile(r"[a-z][a-z0-9+.-]*://[^\s/:@]*:([^\s/@]+)@", re.I)
KEY_BEGIN = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
BASE64_LINE = re.compile(r"^\s*[A-Za-z0-9+/=]{16,}\s*$")

SKIP_DIRS = {"node_modules", "vendor", "dist", "build", ".next", "coverage", ".venv", "venv", "__pycache__"}
LOCK_NAMES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "Cargo.lock", "go.sum"}
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".tif", ".tiff", ".avif", ".heic", ".psd",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".zip", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar", ".tar", ".zst", ".jar", ".war",
    ".mp3", ".mp4", ".wav", ".ogg", ".flac", ".m4a", ".aac", ".mov", ".avi", ".mkv", ".webm",
    ".pdf",
}
MAX_BYTES = 1048576
SENSITIVE_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "credentials.json"}
SENSITIVE_EXT = {".p12", ".pfx", ".jks", ".keystore", ".tfstate"}
ENV_EXEMPT = {"example", "sample", "template", "dist"}
NOT_GIT = "cần repo git — không có thì tự liệt kê file và ghi vào `- Phạm vi:`"


class BadCall(Exception):
    pass


# ---------- spec config (approach copied from mk-cook gate.py; ADR-29: no cross-skill import) ----------

def may_hang(p):
    """True if a group holding a quantifier or `|` is itself repeated (nested repetition can backtrack forever)."""
    stack, i, n = [[False, False]], 0, len(p)  # per open group: [quantifier inside, `|` inside]
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
            m = QUANT.match(p, i + 1)
            if m and (quant or alt):
                return True
            stack[-1][0] |= quant or bool(m)
            stack[-1][1] |= alt
        elif c == "|":
            stack[-1][1] = True
        elif QUANT.match(p, i):
            stack[-1][0] = True
        i += 1
    return False


def yaml_scalar(cfg, key_re):
    """Value of a one-line YAML scalar `<key>: value` ('single', "double" with JSON escapes, or bare); None if absent."""
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
    """(has_config, specs_dir, uc_re) from <root>/specs/mk-specs.yml."""
    try:
        with open(os.path.join(root, "specs", "mk-specs.yml"), encoding="utf-8") as fh:
            cfg = fh.read()
    except (OSError, UnicodeDecodeError):
        return False, "specs", re.compile(DEFAULT_UC)
    specs_dir = yaml_scalar(cfg, r"^specs_dir:") or "specs"
    raw = yaml_scalar(cfg, r"^\s+uc:") or DEFAULT_UC
    if len(raw) > 200 or may_hang(raw):
        raw = DEFAULT_UC
    try:
        uc_re = re.compile(raw)
    except re.error:
        uc_re = re.compile(DEFAULT_UC)
    return True, specs_dir, uc_re


def is_uc(tok, uc_re):
    return len(tok) <= 32 and uc_re.fullmatch(tok) is not None


def pairs_in(text, uc_re):
    """[(uc, ac)] named in text: each AC-n belongs to the closest UC id before it (None if none)."""
    out, uc = [], None
    for m in re.finditer(r"\b[A-Z][A-Z0-9]*-\d+[a-z]?\b", text):
        tok = m.group(0)
        if AC_ID.fullmatch(tok):
            out.append((uc, tok))
        elif is_uc(tok, uc_re):
            uc = tok
    return out


def uc_acs(specs_root, uc):
    """{ac: heading rest} of the UC file under specs_root (changes/ excluded); None when no file."""
    found = None
    for dirpath, dirs, files in os.walk(specs_root):
        if os.path.normpath(dirpath) == os.path.normpath(specs_root):
            dirs[:] = [d for d in dirs if d != "changes"]
        dirs.sort()
        for f in sorted(files):
            if f == uc + ".md" or (f.startswith(uc + "-") and f.endswith(".md")):
                found = os.path.join(dirpath, f)
                break
        if found:
            break
    if not found:
        return None
    acs, fenced = {}, False
    with open(found, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.lstrip().startswith("```"):
                fenced = not fenced
                continue
            m = None if fenced else AC_HEADING.match(line.rstrip("\n"))
            if m and m.group(1) not in acs:
                acs[m.group(1)] = m.group(2)
    return acs


# ---------- check ----------

def norm(value):
    return unicodedata.normalize("NFC", value or "").strip().strip("`*_ ").strip()


def empty(value):
    return norm(value).strip("—–-. ") == ""


def choice(value, options):
    """The option the value starts with (case-insensitive, whole words), else None."""
    v = norm(value).lower()
    for opt in sorted(options, key=len, reverse=True):
        o = opt.lower()
        if v == o or (v.startswith(o) and not v[len(o)].isalnum()):
            return opt
    return None


def parse(text):
    """(header fields, findings [(SEC id, fields)], `## ` section titles). Lines inside ``` fences are ignored.

    A field value continues on following non-blank lines that are indented or are not a new `- ` field."""
    header, findings, sections = {}, [], []
    current, last, in_header, fenced = None, None, True, False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            last = None
            continue
        if fenced:
            continue
        if not line.strip():
            last = None
            continue
        if HEADING.match(line):
            if line.startswith("# "):  # the title line starts the header
                continue
            in_header, last, current = False, None, None
            m = FINDING.match(line)
            if m:
                current = {}
                findings.append((m.group(1), current))
            elif line.startswith("## "):
                sections.append(norm(line[3:]))
            continue
        m = FIELD.match(line)
        if m:
            target = header if in_header else current
            key = norm(m.group(1))
            last = None
            if target is not None and key not in target:
                target[key] = m.group(2)
                last = (target, key)
        elif last and (line[0].isspace() or not line.startswith("- ")):
            target, key = last
            target[key] += "\n" + line
    return header, findings, sections


def class_ok(value, codes):
    m = re.match(r"[`*\s]*([A-Z][A-Z0-9-]*)", value or "")
    return bool(m) and m.group(1) in codes


def catalog_codes():
    """Class codes of `### CODE — …` headings in ../references/catalog.md, plus KHAC."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "references", "catalog.md")
    try:
        with open(path, encoding="utf-8") as fh:
            codes = set(re.findall(r"^### ([A-Z][A-Z0-9-]+) —", fh.read(), re.M))
    except (OSError, UnicodeDecodeError):
        codes = set()
    if not codes:
        raise BadCall("không đọc được mã lớp trong references/catalog.md của skill — cài lại skill")
    return codes | {"KHAC"}


def check_finding(sid, f, cfg, codes, root, blocked):
    has_cfg, specs_dir, uc_re = cfg
    verdict = choice(f.get("Kết luận"), VERDICTS)
    if verdict is None:
        blocked.append(f"{sid}: `- Kết luận:` phải là xác nhận / cần kiểm thêm / bác bỏ")
        return None, None
    level = None
    if verdict == "xác nhận":
        level = choice(f.get("Mức"), LEVELS)
        if level is None:
            blocked.append(f"{sid}: thiếu `- Mức:` (nghiêm trọng / cao / trung bình / thấp)")
        for key in FACTS + ("Đề xuất sửa",):
            if empty(f.get(key)):
                blocked.append(f"{sid}: thiếu hoặc trống `- {key}:`")
        if choice(f.get("Loại"), TYPES) is None:
            blocked.append(f"{sid}: `- Loại:` phải là " + " / ".join(TYPES))
        if empty(f.get("Lớp")):
            blocked.append(f"{sid}: trống `- Lớp:` (mã lớp trong references/catalog.md)")
        if not TRACE.search(f.get("Dấu vết") or ""):
            blocked.append(f"{sid}: `- Dấu vết:` không có token dạng `đường-dẫn:số`")
    else:
        if not empty(f.get("Mức")):
            blocked.append(f"{sid}: chỉ phát hiện xác nhận có `- Mức:` (đang là {verdict})")
        if verdict == "cần kiểm thêm" and empty(f.get("Còn thiếu")):
            blocked.append(f"{sid}: cần kiểm thêm thiếu `- Còn thiếu:` (sự kiện còn thiếu)")
        if verdict == "bác bỏ" and empty(f.get("Lý do bác")):
            blocked.append(f"{sid}: bác bỏ thiếu `- Lý do bác:`")
    if not empty(f.get("Lớp")) and not class_ok(f["Lớp"], codes):
        blocked.append(f"{sid}: `- Lớp:` phải bắt đầu bằng một mã trong references/catalog.md (hoặc KHAC)")
    if "Đã sửa" in f:
        if verdict != "xác nhận":
            blocked.append(f"{sid}: `- Đã sửa:` chỉ dành cho phát hiện xác nhận")
        elif not re.search(r"commit\W*" + HASH.pattern, f["Đã sửa"]):
            blocked.append(f"{sid}: `- Đã sửa:` cần `commit <hash 7–40 ký tự hex>`")
    kind = choice(f.get("Loại"), TYPES)
    if kind in ("code sai AC", "luật sai"):
        pairs = [(u, a) for u, a in pairs_in(f.get("AC") or "", uc_re) if u]
        if not pairs:
            blocked.append(f"{sid}: Loại {kind} cần `- AC: <UC-ID> AC-n`")
        elif has_cfg:
            specs_root = os.path.join(root, specs_dir)
            for uc, ac in pairs:
                acs = uc_acs(specs_root, uc)
                if acs is None or ac not in acs:
                    blocked.append(f"{sid}: AC không có thật: {uc} {ac}")
                elif "(deprecated" in acs[ac].lower():
                    blocked.append(f"{sid}: AC đã bỏ: {uc} {ac}")
    elif kind == "thiếu AC":
        m = re.match(r"[`*\s]*([^\s`*]+)", f.get("Proposal") or "")
        slug = m.group(1) if m and not empty(m.group(1)) else None
        if not slug:
            blocked.append(f"{sid}: Loại thiếu AC cần `- Proposal: <yyMMdd-slug>` của proposal nháp")
        elif "/" in slug or slug.startswith(".") or not os.path.isdir(os.path.join(root, specs_dir, "changes", slug)):
            blocked.append(f"{sid}: proposal không có thật: {slug} (cần thư mục {specs_dir}/changes/{slug})")
    return verdict, level


def secret_lines(lines):
    hits = []
    for i, line in enumerate(lines):
        found = any(p.search(line) for p in SECRETS)
        for m in URL_PASSWORD.finditer(line):
            pw = m.group(1)
            template = TEMPLATE_PASSWORD.fullmatch(pw)  # ${VAR}, $VAR, {password}, %(pw)s, <mật-khẩu>
            if len(pw) >= 6 and not template and not any(c in pw for c in "•…*"):
                found = True
        if KEY_BEGIN.search(line) and i + 1 < len(lines) and BASE64_LINE.match(lines[i + 1]):
            found = True
        if found:
            hits.append(i + 1)
    return hits


def check(path, root):
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as e:
        raise BadCall(f"không đọc được báo cáo {path}: {e.__class__.__name__}")
    text = unicodedata.normalize("NFC", text)
    lines = text.split("\n")
    blocked = []
    header, findings, sections = parse(text)
    for key in HEADER_KEYS:
        if empty(header.get(key)):
            blocked.append(f"thiếu dòng đầu file `- {key}:` (hoặc trống)")
        elif key == "Spec" and choice(header[key], SPEC_VALUES) is None:
            blocked.append("`- Spec:` phải là `mức 4` hoặc `chưa có`")
    if not any(s.lower().startswith("chưa soát") for s in sections):
        blocked.append("thiếu mục `## Chưa soát`")
    seen = set()
    for sid, _ in findings:
        if sid in seen:
            blocked.append(f"{sid} xuất hiện hai lần")
        seen.add(sid)
    fenced = False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            h = re.match(r"^(#{1,6})\s*SEC-\d+\b", line, re.I)
            if h and not FINDING.match(line):
                blocked.append(f"dòng {i}: phát hiện phải là `### SEC-n:`")
            for m in PLACEHOLDER.finditer(BACKTICKS.sub("", line)):
                blocked.append(f"dòng {i}: còn chỗ trống mẫu {m.group(0)}")
        for m in LINK.finditer(line):
            target = m.group(1).split("#", 1)[0]
            if target and not re.match(r"^[a-z]+:", target):
                blocked.append(f"dòng {i}: link tương đối ]({m.group(1)}) — trích dẫn bằng `đường-dẫn:số` trong backtick")
    for n in secret_lines(lines):
        blocked.append(f"dòng {n}: báo cáo chứa giá trị bí mật — che lại (giữ ≤ 4 ký tự đầu)")
    cfg = spec_config(root)
    codes = catalog_codes()
    counts = {}
    for sid, f in findings:
        verdict, level = check_finding(sid, f, cfg, codes, root, blocked)
        counts.setdefault(verdict, []).append(level)
    if blocked:
        for b in blocked:
            print("CHẶN: " + b)
        return 1
    parts = [f"{len(findings)} phát hiện"]
    for v in VERDICTS:
        got = counts.get(v, [])
        if not got:
            continue
        part = f"{v} {len(got)}"
        if v == "xác nhận":
            part += " (" + ", ".join(f"{lv} {got.count(lv)}" for lv in LEVELS if got.count(lv)) + ")"
        parts.append(part)
    print(" · ".join(parts))
    return 0


# ---------- scope ----------

def git(top, *args, ok_codes=(0,)):
    cmd = ["git", "--no-optional-locks"] + (["-C", top] if top else []) + list(args)
    try:
        res = subprocess.run(cmd, capture_output=True)
    except OSError:
        raise BadCall(NOT_GIT)
    if res.returncode not in ok_codes:
        return None
    return res.stdout


def zlist(out):
    return [unicodedata.normalize("NFC", p) for p in out.decode("utf-8", "surrogateescape").split("\0") if p]


def sensitive(top, rel):
    name = os.path.basename(rel)
    ext = os.path.splitext(name)[1].lower()
    if name == ".env" or (name.startswith(".env.") and name.rsplit(".", 1)[1].lower() not in ENV_EXEMPT):
        return True
    if name in SENSITIVE_NAMES or ext in SENSITIVE_EXT:
        return True
    if ext in (".pem", ".key"):
        try:
            with open(os.path.join(top, rel), "rb") as fh:
                return b"PRIVATE KEY" in fh.read(MAX_BYTES)
        except OSError:
            return False
    return False


def skip_reason(top, rel):
    parts = rel.split("/")
    for d in parts[:-1]:
        if d in SKIP_DIRS:
            return f"thư mục {d}/"
    name = parts[-1]
    if name in LOCK_NAMES or name.endswith(".lock"):
        return "file khoá phụ thuộc"
    if os.path.splitext(name)[1].lower() in BINARY_EXT:
        return "nhị phân"
    full = os.path.join(top, rel)
    if os.path.islink(full):
        return None
    if os.path.isdir(full):
        return "thư mục con git"
    try:
        if os.path.getsize(full) > MAX_BYTES:
            return "lớn hơn 1 MiB"
        with open(full, "rb") as fh:
            if b"\0" in fh.read(8192):
                return "nhị phân"
    except OSError:
        return "không đọc được"
    return None


def scope(path, base):
    start = os.path.realpath(path) if path else os.getcwd()
    if path and not os.path.exists(start):
        raise BadCall(f"không có đường dẫn {path}")
    where = start if os.path.isdir(start) else os.path.dirname(start)
    out = git(None, "-C", where, "rev-parse", "--show-toplevel")
    if out is None:
        raise BadCall(NOT_GIT)
    top = os.path.realpath(out.decode("utf-8", "surrogateescape").strip())
    prefix = os.path.relpath(start, top).replace(os.sep, "/")
    if prefix.startswith("../") or prefix == "..":
        raise BadCall(f"{path} nằm ngoài repo {top}")
    prefix = "" if prefix == "." else prefix
    if base is None:
        files = set(zlist(git(top, "ls-files", "-z") or b""))
    else:
        has_head = git(top, "rev-parse", "--verify", "--quiet", "HEAD") is not None
        files = set(zlist(git(top, "ls-files", "-z", "--others", "--exclude-standard") or b""))
        if has_head:
            files |= set(zlist(git(top, "diff", "--name-only", "-z", "--diff-filter=d", "HEAD") or b""))
        else:
            files |= set(zlist(git(top, "ls-files", "-z") or b""))
        if base:
            if git(top, "rev-parse", "--verify", "--quiet", base + "^{commit}") is None:
                raise BadCall(f"nhánh gốc không tồn tại: {base}")
            out = git(top, "diff", "--name-only", "-z", "--diff-filter=d", base + "...HEAD")
            if out is None:
                raise BadCall(f"không so được với nhánh gốc: {base}")
            files |= set(zlist(out))
        files = {f for f in files if os.path.lexists(os.path.join(top, f))}
    files = sorted(f for f in files if not prefix or f == prefix or f.startswith(prefix + "/"))
    keep, skipped, flagged = [], [], []
    for rel in files:
        if sensitive(top, rel):
            flagged.append(rel)
        reason = skip_reason(top, rel)
        if reason:
            skipped.append((rel, reason))
        else:
            keep.append(rel)
    for rel in keep:
        print(rel)
    for rel, reason in skipped:
        print(f"BỎ QUA: {rel} ({reason})")
    for rel in flagged:
        print(f"NHẠY CẢM: {rel} — file bí mật đang nằm trong git")
    print(f"{len(keep)} file cần soát · {len(skipped)} bỏ qua")
    return 0


def main():
    ap = argparse.ArgumentParser(description="mk-secu: kiểm báo cáo soát (check), lấy phạm vi soát (scope)")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check", help="kiểm báo cáo soát")
    c.add_argument("report")
    c.add_argument("--root", default=".")
    s = sub.add_parser("scope", help="liệt kê file cần soát")
    s.add_argument("path", nargs="?")
    s.add_argument("--thay-doi", nargs="?", const="", default=None, metavar="NHÁNH_GỐC")
    args = ap.parse_args()
    if not args.cmd:
        ap.print_usage(sys.stderr)
        return 2
    try:
        if args.cmd == "check":
            return check(args.report, os.path.abspath(args.root))
        return scope(args.path, args.thay_doi)
    except BadCall as e:
        print(str(e))
        return 2


if __name__ == "__main__":
    sys.exit(main())
