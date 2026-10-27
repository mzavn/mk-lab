"""UC-403 rules (repo-only, never installed): markdown line limits, paths named in skill text exist, split files are reachable.

Paths are read from `SKILL.md` and `references/*.md` of each skill. A line is split on whitespace and `` ` ( ) [ ] " ' , ; | ``;
a token containing `references/`, `assets/` or `scripts/` is a path whose prefix (text before that part) decides where it
points: empty, `<skill>/`, or ending in `.claude/skills/<this skill>/` → this skill; `../` → the reading file's folder;
`<skill name>/` or `skills/<skill name>/` → that skill; anything else (`$d/`, `src/`…) → not a skill path. A rest holding
`* < > … { $` is a pattern, skipped. Ending `/` → must be a directory, else a file. Missing here but present in exactly one
other skill → fine (a mention of a sibling skill's file).
"""
import os
import re

SKILL_LIMIT = 300
OTHER_LIMIT = 400
SPLIT = re.compile(r"[\s`()\[\]\"',;|]+")
KINDS = ("references/", "assets/", "scripts/")
PATTERN_CHARS = set("*<>…{$")


def count_lines(path):
    with open(path, "rb") as fh:
        return fh.read().count(b"\n")


def is_skill_text(rel):
    parts = rel.split("/")
    return (len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md") or (
        len(parts) == 4 and parts[0] == "skills" and parts[2] == "references" and parts[3].endswith(".md"))


def line_problems(root, files):
    """Markdown (`*.md`, `*.md.template`) over its limit, sorted; other files are ignored."""
    out = []
    for rel in sorted(files):
        if not (rel.endswith(".md") or rel.endswith(".md.template")):
            continue
        limit = SKILL_LIMIT if is_skill_text(rel) else OTHER_LIMIT
        n = count_lines(os.path.join(root, rel))
        if n >= limit:
            out.append(f"{rel}: {n} dòng (giới hạn < {limit}) — tách thêm file theo chủ đề, không cắt ý")
    return out


def skill_texts(root, skill):
    base = os.path.join(root, "skills", skill)
    texts = [os.path.join(base, "SKILL.md")]
    ref = os.path.join(base, "references")
    if os.path.isdir(ref):
        texts += sorted(os.path.join(ref, n) for n in os.listdir(ref) if n.endswith(".md"))
    return [t for t in texts if os.path.isfile(t)]


def mentions(text):
    """(prefix, rest) for each path-like token, in order."""
    out = []
    for line in text.splitlines():
        for tok in SPLIT.split(line):
            tok = tok.rstrip(".:")
            for kind in KINDS:
                i = tok.find(kind)
                if i >= 0:
                    out.append((tok[:i], tok[i:]))
                    break
    return out


def target_base(root, skill, skills, prefix, reading_dir):
    """Directory the path is relative to, or None when the prefix is not a skill path."""
    if prefix in ("", "<skill>/") or prefix.endswith(f".claude/skills/{skill}/"):
        return os.path.join(root, "skills", skill)
    if prefix == "../":
        return os.path.dirname(reading_dir)
    for name in skills:
        if prefix in (f"{name}/", f"skills/{name}/"):
            return os.path.join(root, "skills", name)
    return None


def exists(base, rest):
    path = os.path.join(base, rest)
    return os.path.isdir(path) if rest.endswith("/") else os.path.isfile(path)


def path_problems(root, skills):
    """Paths named in skill text that do not exist, as `<file> → <path>`."""
    out = []
    for skill in skills:
        for text_path in skill_texts(root, skill):
            with open(text_path, encoding="utf-8") as fh:
                text = fh.read()
            rel_text = os.path.relpath(text_path, root)
            seen = set()
            for prefix, rest in mentions(text):
                if PATTERN_CHARS & set(rest) or (prefix, rest) in seen:
                    continue
                seen.add((prefix, rest))
                base = target_base(root, skill, skills, prefix, os.path.dirname(text_path))
                if base is None or exists(base, rest):
                    continue
                if prefix == "" and sum(exists(os.path.join(root, "skills", s), rest) for s in skills if s != skill) == 1:
                    continue
                out.append(f"{rel_text} → {prefix}{rest}")
    return out


def owner_problems(root, skills, files):
    """Files nobody points to: references, assets (per skill), guide/*.md (README), changelog/*.md (CHANGELOG)."""
    out = []
    for skill in skills:
        base = os.path.join(root, "skills", skill)
        texts = {}
        for p in skill_texts(root, skill):
            with open(p, encoding="utf-8") as fh:
                texts[p] = fh.read()
        skill_md = texts.get(os.path.join(base, "SKILL.md"), "")
        named = set()
        for p, text in texts.items():
            for prefix, rest in mentions(text):
                if target_base(root, skill, skills, prefix, os.path.dirname(p)) == base:
                    named.add(rest)
        backticked = set(re.findall(r"`([^`\s/]+)`", "\n".join(texts.values())))
        scripts = ""
        sdir = os.path.join(base, "scripts")
        if os.path.isdir(sdir):
            for n in sorted(os.listdir(sdir)):
                if n.endswith(".py"):
                    with open(os.path.join(sdir, n), encoding="utf-8") as fh:
                        scripts += fh.read()
        for rel in sorted(files):
            if not rel.startswith(f"skills/{skill}/"):
                continue
            inner = rel[len(f"skills/{skill}/"):]
            name = os.path.basename(inner)
            if inner.startswith("references/") and inner.count("/") == 1 and inner.endswith(".md"):
                if f"references/{name}" not in skill_md:
                    out.append(f"file mồ côi — agent không lần tới được: {rel}")
            elif inner.startswith("assets/"):
                folder = os.path.dirname(inner) + "/"
                owned = (inner in named
                         or (folder in named and folder in skill_md and name in backticked)
                         or f'"{name}"' in scripts)
                if not owned:
                    out.append(f"file mồ côi — agent không lần tới được: {rel}")
    for folder, parent in (("guide/", "README.md"), ("changelog/", "CHANGELOG.md")):
        children = [f for f in sorted(files) if f.startswith(folder) and f.endswith(".md") and f.count("/") == 1]
        if not children:
            continue
        ppath = os.path.join(root, parent)
        ptext = open(ppath, encoding="utf-8").read() if os.path.isfile(ppath) else ""
        out += [f"file mồ côi — agent không lần tới được: {f}" for f in children if f not in ptext]
    return out
