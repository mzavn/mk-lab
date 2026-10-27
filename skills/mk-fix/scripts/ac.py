#!/usr/bin/env python3
"""mk-fix ac: which acceptance criterion does a bug touch? Reads specs/ only; changes nothing.

  ac.py <UC-ID> AC-n | ac.py <UC-ID> | ac.py --tim "<chữ>"   [--root DIR, default cwd]
Config: `specs_dir`, `ids.uc`, `tests.citation_style` of specs/mk-specs.yml (defaults `specs`, `UC-\\d+`, `pointer`).
UC files: `<UC-ID>-*.md` / `<UC-ID>.md` under specs_dir except `changes/`, `_templates/`, `templates/`. AC: `### AC-n:
<title>` inside `## Acceptance Criteria`, up to the next heading; dropped if the title holds `(deprecated` or the UC is
`- Status: deprecated`. Open proposals: specs_dir/changes/<slug>/proposal.md (not archive/), AC lines read by the rules
of mk-cook gate.py (copied, not imported — ADR-29). Exit 0 found · 1 not found, dropped or duplicate UC id · 2 bad
arguments or no specs/mk-specs.yml. Standard library only; output is deterministic.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

sys.dont_write_bytecode = True

DEFAULT_UC = r"UC-\d+"
SKIP_DIRS = {"changes", "_templates", "templates"}
USAGE = ('cách gọi: python3 ac.py <UC-ID> [AC-n] [--root DIR]  ·  python3 ac.py --tim "<chữ>" [--root DIR]'
         '  (vd `ac.py UC-101 AC-2`)')
NO_AC = "gợi ý loại `thiếu AC`: viết proposal nháp thêm AC, không sửa code"
ID = re.compile(r"\b([A-Z][A-Z0-9]*-\d+[a-z]?)\b")
AC_ARG = re.compile(r"AC-\d+[a-z]?")
AC_HEAD = re.compile(r"^###\s+(AC-\d+[a-z]?)\b\s*:?\s*(.*?)\s*$")
ANY_HEAD = re.compile(r"^#{1,6}\s")
TESTS = re.compile(r"^\s*[-*]\s+Tests:\s*(.*)$")
BULLET = r"^\s*(?:[-*]|\d+[.)])\s+"
KEYWORD = re.compile(BULLET + r"(ADDED|MODIFIED|DEPRECATED)\b\s*(.*)$")
RUN = re.compile(r"^(?:([A-Z][A-Z0-9]*-\d+)\s+)?(AC-\d+[a-z]?(?:\s*,\s*AC-\d+[a-z]?)*)\b")
NEW_AC = re.compile(BULLET + r"(AC-\d+[a-z]?)\b[^:]*:(.*)$")
HEADING = re.compile(r"^(#{3,})\s")
QUANT = re.compile(r"[+*]|\{\d*(?:,\d*)?\}")


def section(text, title):
    """Body of `## <title>` up to the next `## ` heading, or None."""
    m = re.search(rf"^## {re.escape(title)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else None


def header_value(text, key):
    """Value of `<key>:` before the first `## `, up to ` · ` or line end; None if absent."""
    m = re.search(rf"(?:^- |· ){re.escape(key)}:\s*([^·\n]*)", text.split("\n## ", 1)[0], re.M)
    return m.group(1).strip() if m else None


def first_word(value):
    m = re.match(r"[`*\s]*([^\s`*(]+)", value or "")
    return m.group(1).lower() if m else ""


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


def config_value(cfg, key, indented):
    """Scalar `<key>:` of the simplified YAML config: quoted ('…' or JSON-style "…") or bare; None if absent."""
    lead = r"^\s+" if indented else r"^"
    m = re.search(lead + re.escape(key) + r":\s*(?:'([^'\n]*)'|\"((?:[^\"\\\n]|\\.)*)\"|([^\s#]+))", cfg, re.M)
    if not m or m.group(2) is None:
        return m and (m.group(1) if m.group(1) is not None else m.group(3))
    try:
        return json.loads('"' + m.group(2) + '"')
    except ValueError:
        return None


def uc_pattern(raw):
    """ids.uc compiled; default when absent, too long, may hang or invalid."""
    try:
        return re.compile(raw if raw and len(raw) <= 200 and not may_hang(raw) else DEFAULT_UC)
    except re.error:
        return re.compile(DEFAULT_UC)


def is_uc(tok, uc_re):
    return len(tok) <= 32 and uc_re.fullmatch(tok) is not None


def read(path):
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        return unicodedata.normalize("NFC", fh.read().replace("\r\n", "\n"))


def rel(path, root):
    return os.path.relpath(path, root).replace(os.sep, "/")


def uc_files(specs, uc_re):
    """{uc_id: [paths]} for `<UC-ID>-*.md` / `<UC-ID>.md` under specs, skipping change and template folders."""
    found = {}
    for top, dirs, files in os.walk(specs):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for stem in sorted(n[:-3] for n in files if n.endswith(".md")):
            cuts = [i for i, c in enumerate(stem) if c == "-"] + [len(stem)]
            uc = next((stem[:i] for i in cuts if is_uc(stem[:i], uc_re)), None)
            if uc:
                found.setdefault(uc, []).append(os.path.join(top, stem + ".md"))
    return found


def parse_uc(text):
    """(status first word, [AC dicts in file order]); AC dict: id, title, lines (block), dropped, tests."""
    status = first_word(header_value(text, "Status"))
    out, cur, fenced = [], None, False
    for line in (section(text, "Acceptance Criteria") or "").split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and ANY_HEAD.match(line):
            m = AC_HEAD.match(line)
            cur = {"id": m.group(1), "title": m.group(2), "lines": [line.rstrip()], "tests": None,
                   "dropped": status == "deprecated" or "(deprecated" in m.group(2).lower()} if m else None
            out += [cur] if cur else []
            continue
        if cur:
            cur["lines"].append(line.rstrip())
            t = TESTS.match(line)
            cur["tests"] = t.group(1).strip() if t and cur["tests"] is None else cur["tests"]
    for ac in out:
        ac["lines"] = "\n".join(ac["lines"]).rstrip().split("\n")
    return status, out


def proposal_acs(text, uc_re):
    """[(uc, ac, kind, lines)] of `## Thay đổi spec` — rules of mk-cook gate.py acs(); NEW_AC lines are ADDED."""
    body = section(text, "Thay đổi spec") or ""
    rows, out, owner, fenced = body.split("\n"), [], None, False
    for i, line in enumerate(rows):
        fence = line.lstrip().startswith("```")
        if fence or fenced:  # lines inside ``` fences are examples, not AC
            fenced ^= fence
            continue
        h = HEADING.match(line)
        if h:
            ucs = [t for t in ID.findall(line) if is_uc(t, uc_re)]
            if len(h.group(1)) == 3 or ucs:
                owner = ucs[0] if len(ucs) == 1 else None
            continue
        plain = line.replace("**", "")
        m = KEYWORD.match(plain)
        if m:
            run = RUN.match(m.group(2))
            if not run:
                continue
            inline = run.group(1)
            uc = inline if inline and is_uc(inline, uc_re) else owner
            ids, kind = re.findall(r"AC-\d+[a-z]?", run.group(2)), m.group(1)
        else:
            m = NEW_AC.match(plain)
            if not m or "Given" not in m.group(2):
                continue
            uc, ids, kind = owner, [m.group(1)], "ADDED"
        indent = len(line) - len(line.lstrip())
        block = [line.strip()]
        for nxt in rows[i + 1:]:
            if not nxt.strip() or len(nxt) - len(nxt.lstrip()) <= indent:
                break
            block.append(nxt.strip())
        out += [(uc, ac, kind, block) for ac in ids if uc]
    return out


def open_proposals(specs, uc_re):
    """[(slug, status word, uc, ac, kind, lines)] of specs/changes/<slug>/proposal.md, archive excluded, by slug."""
    changes, out = os.path.join(specs, "changes"), []
    for slug in sorted(os.listdir(changes)) if os.path.isdir(changes) else []:
        path = os.path.join(changes, slug, "proposal.md")
        if slug != "archive" and os.path.isfile(path):
            text = read(path)
            out += [(slug, first_word(header_value(text, "Status")) or "—") + r for r in proposal_acs(text, uc_re)]
    return out


def duplicate(uc, paths, root):
    print(f"trùng mã {uc}: " + " · ".join(rel(p, root) for p in paths) + " — đổi mã một file rồi chạy lại")
    return 1


def show_one(uc, ac_id, paths, root, props):
    hits, ac, status, acs = [p for p in props if p[2:4] == (uc, ac_id)], None, "", []
    if paths:
        status, acs = parse_uc(read(paths[0]))
        ac = next((a for a in acs if a["id"] == ac_id), None)
    if ac is None and any(k == "ADDED" for _, _, _, _, k, _ in hits):
        for slug, word, _, _, _, block in (h for h in hits if h[4] == "ADDED"):
            print(f"{uc} {ac_id}: AC đang được thêm bởi proposal {slug} (Status: {word})")
            print("\n".join("  " + ln for ln in block))
        return 0
    if ac is None:
        where = f" ({rel(paths[0], root)}; có: {', '.join(a['id'] for a in acs) or '—'})" if paths else ""
        print((f"{uc} không có {ac_id}" if paths else f"không có {uc}") + where + " — " + NO_AC)
    else:
        print(f"{uc} {ac_id} · {rel(paths[0], root)}\nStatus UC: {status or '—'}\n" + "\n".join(ac["lines"]))
    for slug, word in dict.fromkeys(h[:2] for h in hits):
        print(f"đang có proposal đụng AC này: {slug} (Status: {word})")
    if ac is None or not ac["dropped"]:
        return 1 if ac is None else 0
    what = "UC đã bỏ (Status: deprecated)" if status == "deprecated" else "AC đã bỏ (tiêu đề có `(deprecated`)"
    print(f"{what} — không sửa code theo AC này; gợi ý loại `thiếu AC` (proposal thêm AC mới) "
          "hoặc `luật sai` (proposal MODIFIED nếu muốn dùng lại luật cũ)")
    return 1


def show_list(uc, paths, root, props, style):
    by_slug = {}
    for slug, word, _, ac, kind, _ in (p for p in props if p[2] == uc):
        seen = by_slug.setdefault((slug, word), []) if paths or kind == "ADDED" else []
        if ac not in seen:
            seen.append(ac)
    if not paths and not by_slug:
        print(f"không có {uc} — {NO_AC}")
        return 1
    if paths:
        status, acs = parse_uc(read(paths[0]))
        print(f"{uc} · {rel(paths[0], root)}\nStatus UC: {status or '—'}"
              + (" — UC đã bỏ" if status == "deprecated" else ""))
        for ac in acs:
            untested = (ac["tests"] or "").startswith("⚠") or (ac["tests"] is None and style == "pointer")
            print(f"{ac['id']}: {ac['title']}" + (" [bỏ]" if ac["dropped"] else " [chưa có test]" if untested else ""))
    for (slug, word), ids in by_slug.items():
        what = f"đang có proposal đụng {uc}: {slug}" if paths else f"{uc}: AC đang được thêm bởi proposal {slug}"
        print(f"{what} (Status: {word}): {', '.join(ids)}")
    return 0


def search(needle, files, props, specs, root):
    """Main-spec hits by UC number then file order, each UC followed by its open-proposal hits; duplicates → 1."""
    key = unicodedata.normalize("NFC", needle).casefold()
    hits, dups = [], []
    by_number = lambda u: (int((re.findall(r"\d+", u) or [0])[-1]), u)  # noqa: E731
    for uc in sorted(set(files) | {p[2] for p in props}, key=by_number):
        for path in files.get(uc, []):
            acs = parse_uc(read(path))[1]
            found = [a for a in acs if key in "\n".join([a["title"]] + a["lines"][1:]).casefold()]
            if found and len(files[uc]) > 1:
                dups += [uc] if uc not in dups else []
                continue
            hits += [f"{uc} {a['id']}: {a['title']}{' [bỏ]' if a['dropped'] else ''} · {rel(path, root)}"
                     for a in found]
        for slug, _, _, ac, _, block in (p for p in props if p[2] == uc):
            if key in "\n".join(block).casefold():
                where = rel(os.path.join(specs, "changes", slug, "proposal.md"), root)
                hits.append(f"{uc} {ac}: {block[0].split(':', 1)[-1].strip()} · {where} [proposal {slug}]")
    if hits:
        print("\n".join(hits))
    elif not dups:
        print(f"không AC nào (kể cả trong proposal đang mở) có \"{needle}\" — nếu là hành vi người dùng thấy → "
              "`thiếu AC`; build/CI/lint/cấu hình → `hạ tầng` (thử chữ khác trước khi kết luận)")
    for uc in dups:
        duplicate(uc, files[uc], root)
    return 1 if dups or not hits else 0


class Parser(argparse.ArgumentParser):
    def error(self, message):
        print(USAGE)
        sys.exit(2)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = Parser(description="mk-fix ac")
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--tim")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    ids, tim = args.ids, args.tim
    bad = (ids or not tim.strip()) if tim is not None else not (
        1 <= len(ids) <= 2 and (len(ids) == 1 or AC_ARG.fullmatch(ids[1])))
    if bad:
        ap.error("")
    for need in ("mk-specs.yml", "README.md"):
        if not os.path.isfile(os.path.join(args.root, "specs", need)):
            print(f"mk-fix ac: cần repo mk-specs mức 4 đã init — chưa có specs/{need} (nhờ mk-specs `init` trước)")
            return 2
    cfg = read(os.path.join(args.root, "specs", "mk-specs.yml"))
    uc_re = uc_pattern(config_value(cfg, "uc", True))
    style = (config_value(cfg, "citation_style", True) or "pointer").lower()
    specs_dir = config_value(cfg, "specs_dir", False) or "specs"
    specs = os.path.join(args.root, specs_dir)
    if not os.path.isdir(specs):
        print(f"mk-fix ac: specs_dir '{specs_dir}' không tồn tại — sửa specs/mk-specs.yml")
        return 2
    if tim is None and not is_uc(ids[0], uc_re):
        print(f"mk-fix ac: '{ids[0]}' không khớp mã UC của repo (`ids.uc`: {uc_re.pattern})")
        ap.error("")
    files, props = uc_files(specs, uc_re), open_proposals(specs, uc_re)
    if tim is not None:
        return search(tim, files, props, specs, args.root)
    paths = files.get(ids[0], [])
    if len(paths) > 1:
        return duplicate(ids[0], paths, args.root)
    if len(ids) == 2:
        return show_one(ids[0], ids[1], paths, args.root, props)
    return show_list(ids[0], paths, args.root, props, style)


if __name__ == "__main__":
    sys.exit(main())
