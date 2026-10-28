#!/usr/bin/env python3
"""Kiểm cơ học một skill theo bộ chuẩn của bộ mk (chỉ đọc, đầu ra tất định).

Cách gọi: python3 validate.py <thư mục skill>
In theo thứ tự cố định: tên thư mục → frontmatter → cấu trúc → số dòng → nội dung → scripts. Mỗi nhóm đạt in một dòng
"OK: …"; mỗi vi phạm in một dòng "LỖI: <nhóm> — <chi tiết>". Dòng cuối "Kết quả: <n> lỗi".
Thoát 0 khi 0 lỗi; 1 khi có lỗi hoặc không kiểm được (dòng "Lỗi: …").

"File của skill" = file git theo dõi hoặc chưa theo dõi mà không bị git loại (git ls-files -co --exclude-standard);
thư mục không nằm trong git (hoặc không có git) → mọi file. Không đi theo symlink.
"""
import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
import sysconfig

sys.dont_write_bytecode = True

LIMIT = 300
OTHER_LIMIT = 400
DESC_LIMIT = 1024
AUTHOR = "mzavn"
DIR_RE = re.compile(r"mk-([a-z0-9]+(?:-[a-z0-9]+)*)")
TOP_DIRS = ("assets", "references", "scripts")
TOP_FILES = ("SKILL.md", "THIRD_PARTY_NOTICES.md",  # sau đây: file install.sh của mk-lab, mk-studio ghi vào bản cài
             ".mk-specs-manifest", ".mk-specs-source", ".mk-studio-manifest", ".mk-studio-source")
KEYS_ALLOWED = ("name", "description", "license", "metadata", "hooks", "allowed-tools", "compatibility")
JUNK_PARTS = ("__pycache__", ".DS_Store", "Thumbs.db")
HOME_PATH = re.compile("/" + "Users/[A-Za-z0-9._-]+")  # chia đôi để chính file này không tự khớp
PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_]*[:}]")
SPLIT = re.compile(r"[\s`()\[\]\"',;|]+")
KINDS = ("references/", "assets/", "scripts/")
PATTERN_CHARS = set("*<>…{$")
NEWER_STDLIB = {"tomllib", "graphlib", "zoneinfo", "_tomllib"}
MAIN_GUARD = re.compile(r"""^if\s+__name__\s*==\s*['"]__main__['"]\s*:""", re.M)
NO_BYTECODE = re.compile(r"^[ \t]*sys\.dont_write_bytecode[ \t]*=[ \t]*True\b", re.M)
CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f]")
SHOW = 60  # độ dài tối đa của giá trị lấy từ file in lại trong dòng LỖI


class Fail(Exception):
    pass


# ---------- đọc ----------

def read_text(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (UnicodeDecodeError, OSError):
        return None


def walk(root):
    """Mọi mục không phải thư mục (file, symlink, FIFO…) dưới root, dạng a/b, không đi theo symlink."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        for d in list(dirnames):
            if os.path.islink(os.path.join(dirpath, d)):
                dirnames.remove(d)
                filenames.append(d)
        for f in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/"))
    return sorted(out)


def git_visible(root):
    """Tập file git thấy (theo dõi + chưa theo dõi không bị loại), hoặc None khi không dùng được git."""
    try:
        res = subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", root,
                              "ls-files", "-co", "--exclude-standard", "-z", "--", "."],
                             capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    return {p.decode("utf-8", "surrogateescape") for p in res.stdout.split(b"\0") if p}


def skill_files(root):
    """(file của skill, file bị git loại). Ngoài git, hoặc git loại cả SKILL.md (thư mục dev-only) → mọi file."""
    every = walk(root)
    seen = git_visible(root)
    if seen is None or "SKILL.md" not in seen:
        return every, []
    return [p for p in every if p in seen], [p for p in every if p not in seen]


def show(value):
    value = str(value)
    return value if len(value) <= SHOW else value[:SHOW] + "…"


def is_junk(rel):
    parts = rel.split("/")
    return any(p in JUNK_PARTS for p in parts) or rel.endswith(".pyc")


def junk_root(rel):
    parts = rel.split("/")
    for i, p in enumerate(parts):
        if p == "__pycache__":
            return "/".join(parts[:i + 1]) + "/"
    return rel


# ---------- frontmatter ----------

def split_frontmatter(text):
    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r") == "---":
            return [ln.rstrip("\r") for ln in lines[1:i]]
    return None


def parse_frontmatter(lines):
    """{khoá gốc: (giá trị thô, [dòng con thụt lề])} theo thứ tự xuất hiện; khoá trùng → danh sách lỗi."""
    keys, dup, cur = {}, [], None
    for ln in lines:
        if not ln.strip() or ln.lstrip().startswith("#"):
            if cur is not None and not ln.strip():
                keys[cur][1].append(ln)
            continue
        m = re.match(r"([A-Za-z][\w-]*):(.*)$", ln)
        if m and not ln[0].isspace():
            cur = m.group(1)
            if cur in keys:
                dup.append(cur)
            keys[cur] = (m.group(2).strip(), [])
        elif cur is not None:
            keys[cur][1].append(ln)
    return keys, dup


def scalar(raw):
    """Giá trị một dòng: (chuỗi, lỗi hoặc None)."""
    if raw.startswith("'"):
        if len(raw) < 2 or not raw.endswith("'"):
            return None, "mở nháy đơn mà không đóng trên cùng dòng"
        inner = raw[1:-1]
        if re.search(r"(?<!')'(?!')", inner.replace("''", "")):
            return None, "nháy đơn bên trong phải viết ''"
        return inner.replace("''", "'"), None
    if raw.startswith('"'):
        try:
            val = json.loads(raw)
        except ValueError:
            return None, "chuỗi nháy kép không hợp lệ"
        return (val, None) if isinstance(val, str) else (None, "chuỗi nháy kép không hợp lệ")
    if raw[:1] in ("|", ">"):
        return None, "phải là một dòng, không dùng khối | hoặc >"
    if ": " in raw or " #" in raw:
        return None, "có ': ' hoặc ' #' mà không đặt trong nháy — YAML hiểu sai"
    return raw, None


def check_frontmatter(text, short):
    errs, info = [], {}
    if text.startswith("\ufeff"):
        return ["SKILL.md bắt đầu bằng BOM — lưu lại dạng UTF-8 không BOM"], info
    fm = split_frontmatter(text)
    if fm is None:
        return ["SKILL.md không mở đầu bằng khối --- … ---"], info
    keys, dup = parse_frontmatter(fm)
    errs += [f"khoá '{k}' lặp lại" for k in dup]
    errs += [f"khoá '{show(k)}' không thuộc chuẩn (chỉ {', '.join(KEYS_ALLOWED)})" for k in keys if k not in KEYS_ALLOWED]
    for k in ("name", "description", "license", "metadata"):
        if k not in keys:
            errs.append(f"thiếu '{k}'")

    info["hooks"] = "hooks" in keys
    if "name" in keys:
        name, err = scalar(keys["name"][0])
        if err:
            errs.append(f"name: {err}")
        elif name.count(":") != 1 or not name.startswith("mk:"):
            errs.append(f"name '{show(name)}' phải dạng mk:<tên> với đúng một dấu ':'")
        elif short is not None and name != f"mk:{short}":
            errs.append(f"name '{show(name)}' không khớp thư mục (cần mk:{short})")
        else:
            info["name"] = name

    if "description" in keys:
        raw, children = keys["description"]
        cont = [c for c in children if c.strip()]
        desc, err = scalar(raw) if raw else (None, "phải là một dòng (đang trống hoặc xuống dòng)")
        if err:
            errs.append(f"description: {err}")
        elif cont:
            errs.append("description: phải là một dòng (có dòng tiếp theo thụt lề)")
        elif not desc.strip():
            errs.append("description trống")
        else:
            if len(desc) > DESC_LIMIT:
                errs.append(f"description {len(desc)} ký tự (tối đa {DESC_LIMIT})")
            if short is not None and f"mk:{short}" not in desc:
                errs.append(f"description không có chữ 'mk:{short}' (người dùng gọi /mk:{short})")
            info["desc"] = len(desc)

    if "license" in keys:
        lic, err = scalar(keys["license"][0])
        if err or lic != "MIT":
            errs.append(f"license phải là MIT (đang: {show(keys['license'][0]) or 'trống'})")

    if "metadata" in keys:
        raw, children = keys["metadata"]
        sub = {}
        for c in children:
            m = re.match(r"\s+([A-Za-z][\w-]*):(.*)$", c)
            if m:
                sub[m.group(1)] = m.group(2).strip()
        if raw:
            errs.append("metadata phải là khối con (author, version) trên các dòng sau")
        author = sub.get("author")
        if author is None:
            errs.append("thiếu metadata.author")
        elif (scalar(author)[0] or "") != AUTHOR:
            errs.append(f"metadata.author phải là {AUTHOR} (đang: {show(author)})")
        version = sub.get("version")
        if version is None:
            errs.append("thiếu metadata.version")
        elif not re.fullmatch(r'"\d+\.\d+\.\d+"', version):
            errs.append(f'metadata.version phải dạng "X.Y.Z" có nháy kép (đang: {show(version)})')
        else:
            info["version"] = version.strip('"')
    return errs, info


# ---------- nội dung ----------

def mentions(text):
    """(số dòng, tiền tố, phần còn lại) của mỗi token trông như đường dẫn trong skill."""
    out = []
    for n, line in enumerate(text.split("\n"), 1):
        for tok in SPLIT.split(line):
            tok = tok.rstrip(".:")
            if "://" in tok:
                continue
            for kind in KINDS:
                i = tok.find(kind)
                if i >= 0:
                    out.append((n, tok[:i], tok[i:]))
                    break
    return out


def mention_base(root, dirname, prefix, reading_dir):
    if prefix in ("", "<skill>/") or prefix.endswith((f".claude/skills/{dirname}/", f".agents/skills/{dirname}/")):
        return root
    if prefix == "../" and reading_dir != root:
        return os.path.dirname(reading_dir)
    return None


def exists_here(root, base, rest):
    path = os.path.normpath(os.path.join(base, rest))
    if path != root and not path.startswith(root + os.sep):
        return True  # ngoài skill: không phải việc của kiểm này
    return os.path.isdir(path) if rest.endswith("/") else os.path.isfile(path)


def sibling_has(root, rest):
    """Có đúng một skill anh em (cùng thư mục cha) chứa đường dẫn này — câu nhắc file của skill khác."""
    parent = os.path.dirname(root)
    hits = 0
    for name in sorted(os.listdir(parent)):
        other = os.path.join(parent, name)
        if other == root or not DIR_RE.fullmatch(name) or not os.path.isfile(os.path.join(other, "SKILL.md")):
            continue
        p = os.path.join(other, rest)
        hits += os.path.isdir(p) if rest.endswith("/") else os.path.isfile(p)
    return hits == 1


def check_content(root, files, skill_text):
    errs = []
    dirname = os.path.basename(root)
    lines = skill_text.split("\n")
    m = skill_text.find("**Phạm vi.**")
    if m < 0:
        errs.append("SKILL.md thiếu đoạn **Phạm vi.** (Skill xử lý: … **Không** xử lý: …)")
    else:
        para = re.split(r"\r?\n[ \t]*\r?\n", skill_text[m:], maxsplit=1)[0]
        if "**Không**" not in para:
            errs.append("đoạn **Phạm vi.** thiếu phần **Không** xử lý")
    for heading in ("Trả lời người dùng", "Chính sách an toàn"):
        if not re.search(rf"^##\s+{heading}\s*$", skill_text, re.M):
            errs.append(f"SKILL.md thiếu mục '## {heading}'")
    for n, ln in enumerate(lines, 1):
        if PLACEHOLDER.search(ln):
            errs.append(f"SKILL.md:{n} còn chỗ trống mẫu {PLACEHOLDER.search(ln).group(0)}…")

    for rel in files:
        path = os.path.join(root, rel)
        if os.path.islink(path):
            continue
        text = read_text(path)
        if text is None:
            continue
        for n, ln in enumerate(text.split("\n"), 1):
            hit = HOME_PATH.search(ln)
            if hit:
                errs.append(f"{rel}:{n} có đường dẫn máy cá nhân dạng /Users/<tên>")

    texts = ["SKILL.md"] + [f for f in files if f.startswith("references/") and f.count("/") == 1 and f.endswith(".md")]
    count, named, bodies = 0, set(), {}
    for rel in texts:
        path = os.path.join(root, rel)
        if os.path.islink(path):
            continue
        text = skill_text if rel == "SKILL.md" else read_text(path)
        if text is None:
            continue
        bodies[rel] = text
        seen = set()
        for n, prefix, rest in mentions(text):
            if PATTERN_CHARS & set(rest) or (prefix, rest) in seen:
                continue
            seen.add((prefix, rest))
            base = mention_base(root, dirname, prefix, os.path.dirname(path))
            if base is None:
                continue
            count += 1
            target = os.path.relpath(os.path.normpath(os.path.join(base, rest)), root).replace(os.sep, "/")
            named.add(target + "/" if rest.endswith("/") else target)
            if exists_here(root, base, rest):
                continue
            if prefix == "" and sibling_has(root, rest):
                continue
            errs.append(f"{rel}:{n} nhắc {prefix}{rest} nhưng không có")
    errs += orphans(root, files, skill_text, named, bodies)
    return errs, count


def orphans(root, files, skill_text, named, bodies):
    """Reference không được SKILL.md nhắc, asset không ai nhắc — agent không lần tới được."""
    out = []
    backticked = set(re.findall(r"`([^`\s/]+)`", "\n".join(bodies.values())))
    scripts = ""
    for rel in files:
        if rel.startswith("scripts/") and rel.count("/") == 1 and rel.endswith(".py") \
                and not os.path.islink(os.path.join(root, rel)):
            scripts += read_text(os.path.join(root, rel)) or ""
    for rel in files:
        name = os.path.basename(rel)
        if is_junk(rel) or os.path.islink(os.path.join(root, rel)):
            continue
        if rel.startswith("references/") and rel.count("/") == 1 and rel.endswith(".md"):
            if f"references/{name}" not in skill_text:
                out.append(f"{rel} không được SKILL.md nhắc — agent không lần tới được")
        elif rel.startswith("assets/"):
            folder = os.path.dirname(rel) + "/"
            if not (rel in named or (folder in named and folder in skill_text and name in backticked)
                    or f'"{name}"' in scripts):
                out.append(f"{rel} không được SKILL.md, reference hay script nào nhắc — agent không lần tới được")
    return out


# ---------- scripts ----------

def is_stdlib(mod):
    names = getattr(sys, "stdlib_module_names", None)
    if names is not None:
        return mod in names
    if mod in sys.builtin_module_names or mod in NEWER_STDLIB or mod == "__future__":
        return True
    try:
        spec = importlib.util.find_spec(mod)
    except (ImportError, ValueError):
        return False
    if spec is None or not spec.origin:
        return False
    if spec.origin in ("built-in", "frozen"):
        return True
    origin = os.path.realpath(spec.origin)
    roots = {os.path.realpath(sysconfig.get_paths()[k]) for k in ("stdlib", "platstdlib")}
    return "site-packages" not in origin and any(origin.startswith(r + os.sep) for r in roots)


def local_modules(root, folder):
    out = set()
    for d in {folder, os.path.join(root, "scripts")}:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            p = os.path.join(d, name)
            if name.endswith(".py"):
                out.add(name[:-3])
            elif os.path.isfile(os.path.join(p, "__init__.py")):
                out.add(name)
    return out


def check_scripts(root, files):
    errs = []
    pys = [f for f in files if f.startswith("scripts/") and f.endswith(".py") and not os.path.islink(os.path.join(root, f))]
    for rel in pys:
        path = os.path.join(root, rel)
        text = read_text(path)
        if text is None:
            errs.append(f"{rel} không đọc được dạng UTF-8")
            continue
        try:
            tree = ast.parse(text, filename=rel)
        except SyntaxError as e:
            errs.append(f"{rel}:{e.lineno} lỗi cú pháp: {e.msg}")
            continue
        local = local_modules(root, os.path.dirname(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods = [(a.name.split(".")[0], node.lineno) for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                mods = [(node.module.split(".")[0], node.lineno)]
            else:
                continue
            for mod, line in mods:
                if mod not in local and not is_stdlib(mod):
                    errs.append(f"{rel}:{line} import '{mod}' không thuộc thư viện chuẩn")
        if not rel.startswith("scripts/tests/") and MAIN_GUARD.search(text) and not NO_BYTECODE.search(text):
            errs.append(f"{rel} chạy được như lệnh mà thiếu 'sys.dont_write_bytecode = True' (để không sinh __pycache__)")
    mains = [f for f in pys if f.count("/") == 1]
    tests = [f for f in pys if re.fullmatch(r"scripts/tests/test_[^/]+\.py", f)]
    if mains and not tests:
        errs.append("có script nhưng không có scripts/tests/test_*.py")
    return errs, len(pys), len(tests)


# ---------- chạy ----------

def run(root):
    """Danh sách dòng in ra và số lỗi."""
    out, total = [], 0

    def report(group, errs, ok):
        nonlocal total
        if errs:
            total += len(errs)
            out.extend(CONTROL.sub("?", f"LỖI: {group} — {e}") for e in errs)  # tên/chữ lấy từ file: không để ký tự điều khiển ra terminal
        else:
            out.append(f"OK: {group} ({ok})" if ok else f"OK: {group}")

    dirname = os.path.basename(root)
    m = DIR_RE.fullmatch(dirname)
    short = m.group(1) if m else None
    report("tên thư mục", [] if m else [f"'{dirname}' phải dạng mk-<tên> (chữ thường, số, gạch nối)"], dirname)

    skill_text = read_text(os.path.join(root, "SKILL.md"))
    if skill_text is None:
        raise Fail(f"{root}/SKILL.md không đọc được dạng UTF-8")
    errs, info = check_frontmatter(skill_text, short)
    report("frontmatter", errs,
           f"name {info.get('name')}, description {info.get('desc')}/{DESC_LIMIT} ký tự, license MIT, "
           f"author {AUTHOR}, version {info.get('version')}"
           + ("; có hooks — bắt buộc audit bảo mật" if info.get("hooks") else "") if not errs else "")

    files, hidden = skill_files(root)
    errs = []
    tops = sorted({f.split("/")[0] for f in files if not is_junk(f)})
    for top in tops:
        path = os.path.join(root, top)
        if top in TOP_FILES:
            if os.path.islink(path) or not os.path.isfile(path):
                errs.append(f"'{top}' phải là file")
        elif top in TOP_DIRS:
            if os.path.islink(path) or not os.path.isdir(path):
                errs.append(f"'{top}' phải là thư mục")
        else:
            errs.append(f"'{top}' không thuộc cấu trúc (chỉ SKILL.md, references/, assets/, scripts/, "
                        "THIRD_PARTY_NOTICES.md)")
    for f in files:
        if "/" in f and os.path.islink(os.path.join(root, f)):
            errs.append(f"{f} là symlink — skill không chứa symlink (không đọc đích)")
        elif not os.path.isfile(os.path.join(root, f)):
            errs.append(f"{f} không phải file thường (FIFO, socket, thiết bị) — không đọc")
        elif not os.access(os.path.join(root, f), os.R_OK):
            errs.append(f"{f} không đọc được (quyền)")
    for j in sorted({junk_root(f) for f in files if is_junk(f)}):
        errs.append(f"file rác {j} (xoá, hoặc thêm vào .gitignore)")
    skipped = sum(1 for f in hidden if is_junk(f))
    ok = ", ".join(t + ("/" if t in TOP_DIRS else "") for t in tops)
    if skipped:
        ok += f"; bỏ qua {skipped} file rác git đã loại"
    report("cấu trúc", errs, ok)
    # Các nhóm sau chỉ đọc file thường đọc được — symlink, FIFO, file khoá quyền đã báo ở trên, không mở.
    files = [f for f in files if os.path.isfile(os.path.join(root, f)) and not os.path.islink(os.path.join(root, f))
             and os.access(os.path.join(root, f), os.R_OK)]

    errs, counted = [], []
    for rel in ["SKILL.md"] + [f for f in files if f.endswith((".md", ".md.template")) and f != "SKILL.md"]:
        path = os.path.join(root, rel)
        if os.path.islink(path):
            continue
        try:
            with open(path, "rb") as fh:
                n = fh.read().count(b"\n")
        except OSError:
            continue  # đã báo ở nhóm cấu trúc
        main_text = rel == "SKILL.md" or (rel.startswith("references/") and rel.count("/") == 1 and rel.endswith(".md"))
        limit = LIMIT if main_text else OTHER_LIMIT
        if main_text:
            counted.append(n)
        if n >= limit:
            errs.append(f"{rel} {n} dòng (giới hạn < {limit}) — tách thêm file theo chủ đề, không cắt ý")
    report("số dòng", errs, f"SKILL.md {counted[0]}, {len(counted) - 1} reference, dài nhất {max(counted)}")

    errs, paths = check_content(root, files, skill_text)
    report("nội dung", errs, f"Phạm vi, Trả lời người dùng, Chính sách an toàn; {paths} đường dẫn có thật")

    errs, n_py, n_tests = check_scripts(root, files)
    report("scripts", errs, f"{n_py} file Python, chỉ thư viện chuẩn, {n_tests} file test" if n_py else "không có script")

    out.append(f"Kết quả: {total} lỗi")
    return out, total


def main(argv):
    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        print("Lỗi: cách gọi: python3 validate.py <thư mục skill>")
        return 1
    root = os.path.abspath(argv[0].rstrip("/") or "/")
    try:
        if not os.path.exists(root):
            raise Fail(f"không có {argv[0]}")
        if not os.path.isdir(root):
            raise Fail(f"{argv[0]} không phải thư mục")
        skill = os.path.join(root, "SKILL.md")
        if os.path.islink(skill) or not os.path.isfile(skill):
            raise Fail(f"{argv[0]} không có file SKILL.md")
        lines, total = run(root)
    except Fail as e:
        print(f"Lỗi: {e}")
        return 1
    print("\n".join(lines))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
