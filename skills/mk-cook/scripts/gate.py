#!/usr/bin/env python3
"""mk-cook gate: may this change be coded (or reported done)? Reads the change folder and UC files; changes nothing.

Usage (from the project root):
  python3 <skill>/scripts/gate.py <change>           before coding
  python3 <skill>/scripts/gate.py <change> --done    before reporting done
  <change> = change folder, its proposal.md, or a slug under <root>/specs/changes/  (--root DIR, default cwd)

Before coding:
  - `- Status:` first word is `approved` or `implemented`; business and technical reviewers are named (not `chờ`).
  - `## Thay đổi spec` has AC lines: `ADDED|MODIFIED|DEPRECATED [<UC-ID>] AC-n(, AC-m)*: …`, or `- AC-n: Given …`
    (a new UC listing its AC). The owner UC is the inline ID, else the `### …` heading holding exactly one ID that
    matches `ids.uc` of specs/mk-specs.yml (default `UC-\\d+`). Unnumbered, scattered or ownerless AC → blocked.
  - More than 5 added/modified AC, or `- Quy mô: lớn` → plan.md names each one in exactly one `## ` phase.
  - UC files of the repo (`<UC-ID>-*.md` / `<UC-ID>.md` under `specs_dir` of specs/mk-specs.yml, except `changes/`,
    `_templates/`, `templates/`; AC = `### AC-n` heading inside `## Acceptance Criteria`, deprecated ones too; several
    files with one id are read together): ADDED AC-n already there → blocked with the next free number, unless the
    file holds `<slug>/proposal.md` (drafted for this change; then only two `### AC-n` headings block); MODIFIED or
    DEPRECATED needs the UC file and the AC heading. No config or no specs_dir → these checks are skipped.
  Prints the AC list to write tests for (and the deprecated ones to remove).
--done also: `## Bằng chứng nghiệm thu` exists, has no `<…>` placeholder outside backticks, names every AC.
In plan.md and evidence, `UC-101 AC-1, AC-2` names both (each AC belongs to the closest ID before it).
Exit 0 pass · 1 blocked (reasons printed) · 2 bad arguments. Standard library only; output is deterministic.
UC-file reading is copied from mk-fix ac.py, not imported (ADR-29).
"""
import argparse
import json
import os
import re
import sys
import unicodedata

sys.dont_write_bytecode = True

PLAN_LIMIT = 5
DEFAULT_UC = r"UC-\d+"
SKIP_DIRS = {"changes", "_templates", "templates"}
AC_HEAD = re.compile(r"^###\s+(AC-(\d+)[a-z]?)\b")
ID = re.compile(r"\b([A-Z][A-Z0-9]*-\d+[a-z]?)\b")
BULLET = r"^\s*(?:[-*]|\d+[.)])\s+"
KEYWORD = re.compile(BULLET + r"(ADDED|MODIFIED|DEPRECATED)\b\s*(.*)$")
RUN = re.compile(r"^(?:([A-Z][A-Z0-9]*-\d+)\s+)?(AC-\d+[a-z]?(?:\s*,\s*AC-\d+[a-z]?)*)\b")
AC_ID = re.compile(r"\bAC-\d+[a-z]?\b")
UNNUMBERED = re.compile(r"\bAC(?:\b(?!-)|-(?!\d))")
SCATTERED = re.compile(r"(?:[;.]\s+)(AC-\d+[a-z]?)\b[^:;]{0,40}:")
NEW_AC = re.compile(BULLET + r"(AC-\d+[a-z]?)\b[^:]*:(.*)$")
HEADING = re.compile(r"^(#{3,})\s")
BACKTICKS = re.compile(r"`[^`\n]*`")
PLACEHOLDER = re.compile(r"<(?![\s\d=<>-]|https?:)[^<>\n]+>")
QUANT = re.compile(r"[+*]|\{\d*(?:,\d*)?\}")


def section(text, title):
    """Body of `## <title>` up to the next `## ` heading, or None."""
    m = re.search(rf"^## {re.escape(title)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else None


def header(text):
    return text.split("\n## ", 1)[0]


def header_value(text, key):
    """Value of `<key>:` in the header (before the first `## `), up to ` · ` or line end; None if absent."""
    m = re.search(rf"(?:^- |· ){re.escape(key)}:\s*([^·\n]*)", header(text), re.M)
    return m.group(1).strip() if m else None


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


def project_config(root):
    """Text of specs/mk-specs.yml, or None when absent or unreadable."""
    try:
        with open(os.path.join(root, "specs", "mk-specs.yml"), encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


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


def uc_pattern(cfg):
    """ids.uc of the config, compiled; default when absent, too long, may hang or invalid."""
    raw = config_value(cfg or "", "uc", True)
    try:
        return re.compile(raw if raw and len(raw) <= 200 and not may_hang(raw) else DEFAULT_UC)
    except re.error:
        return re.compile(DEFAULT_UC)


def is_uc(tok, uc_re):
    return len(tok) <= 32 and uc_re.fullmatch(tok) is not None


def acs(text, uc_re):
    """(changed, deprecated, problems, added): changed/deprecated = [(uc, ac)] in order; uc None = owner unknown;
    added = the changed pairs that are new (`ADDED` or `- AC-n: Given …`), the rest of changed is MODIFIED.

    `### ` heading sets the owner (exactly one UC id, else none); a deeper heading with one UC id sets it,
    one without UC ids keeps the parent's. Lines inside ``` fences are examples, not AC."""
    body = section(text, "Thay đổi spec") or ""
    changed, deprecated, problems, added, owner, fenced = [], [], [], set(), None, False
    split = "tách dòng (mỗi dòng một AC hoặc một dãy `AC-1, AC-2` ngay sau từ khoá)"
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        h = HEADING.match(line)
        if h:
            ucs = [t for t in ID.findall(line) if is_uc(t, uc_re)]
            if len(h.group(1)) == 3 or ucs:
                owner = ucs[0] if len(ucs) == 1 else None
            continue
        line = line.replace("**", "")
        m = KEYWORD.match(line)
        if m:
            kind, rest = m.group(1), m.group(2)
            run = RUN.match(rest)
            head = BACKTICKS.sub("", rest).split(":", 1)[0]
            if not run:
                if AC_ID.search(head):
                    problems.append(f"{split}: {line.strip()}")
                elif UNNUMBERED.search(head):
                    problems.append(f"AC chưa có số: {line.strip()}")
                continue
            after = BACKTICKS.sub("", rest[run.end():])
            others = set(AC_ID.findall(after.split(":", 1)[0])) - set(AC_ID.findall(run.group(2)))
            if others or SCATTERED.search(after):
                problems.append(f"{split}: {line.strip()}")
            inline = run.group(1)
            uc = inline if inline and is_uc(inline, uc_re) else owner
            ids = re.findall(r"AC-\d+[a-z]?", run.group(2))
            target = deprecated if kind == "DEPRECATED" else changed
        else:
            m = NEW_AC.match(line)
            if not m or "Given" not in m.group(2):
                continue
            uc, ids, target, kind = owner, [m.group(1)], changed, "ADDED"
        for ac in ids:
            if (uc, ac) not in changed and (uc, ac) not in deprecated:
                target.append((uc, ac))
                if kind == "ADDED":
                    added.add((uc, ac))
    return changed, deprecated, problems, added


def read_text(path):
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        return unicodedata.normalize("NFC", fh.read().replace("\r\n", "\n"))


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


def uc_headings(text):
    """[(ac, number)] of `### AC-n` headings inside `## Acceptance Criteria`, deprecated ones included, repeats kept."""
    out, fenced = [], False
    for line in (section(text, "Acceptance Criteria") or "").split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        m = None if fenced else AC_HEAD.match(line)
        if m:
            out.append((m.group(1), int(m.group(2))))
    return out


def check_numbers(cfg, root, slug, changed, deprecated, added, uc_re):
    """Blocks from the repo's UC files: ADDED number already taken, MODIFIED/DEPRECATED AC or UC missing.
    No config or no specs_dir → []."""
    specs = os.path.join(root, config_value(cfg, "specs_dir", False) or "specs") if cfg is not None else None
    if not specs or not os.path.isdir(specs):
        return []
    files, mine, blocked, heads, drafted = uc_files(specs, uc_re), f"{slug}/proposal.md", [], {}, {}
    for uc in dict.fromkeys(u for u, _ in changed + deprecated):
        texts = [read_text(p) for p in files.get(uc, [])]
        heads[uc] = [h for t in texts for h in uc_headings(t)] if texts else None
        drafted[uc] = any(mine in t for t in texts)
    missing_uc = set()
    for uc, ac in changed + deprecated:
        have = heads[uc]
        if (uc, ac) in added:
            if have is None:
                continue
            ids = [a for a, _ in have]
            if drafted[uc] and ids.count(ac) > 1:
                blocked.append(f"{uc} có hai tiêu đề `### {ac}` — đổi số một cái")
            elif not drafted[uc] and ac in ids:
                nxt = max(n for _, n in have) + 1
                blocked.append(f"{ac} đã có trong {uc} — dùng số kế: AC-{nxt} (nếu đang viết sẵn UC này cho change này: "
                               f"thêm dòng History trỏ `changes/archive/{slug}/proposal.md`)")
        elif have is None:
            if uc not in missing_uc:
                missing_uc.add(uc)
                blocked.append(f"không thấy file {uc} — MODIFIED/DEPRECATED cần UC có thật")
        elif ac not in [a for a, _ in have]:
            blocked.append(f"{uc} không có {ac}")
    return blocked


def pairs_in(text, uc_re):
    """[(uc, ac)] named in text, with repeats: each AC-n belongs to the closest UC id before it."""
    out, current = [], None
    for tok in ID.findall(text):
        if tok.startswith("AC-"):
            if current:
                out.append((current, tok))
        elif is_uc(tok, uc_re):
            current = tok
    return out


def resolve(arg, root):
    for cand in (arg, os.path.join(root, "specs", "changes", arg)):
        if os.path.isdir(cand) and os.path.isfile(os.path.join(cand, "proposal.md")):
            return os.path.join(cand, "proposal.md")
        if os.path.isfile(cand) and cand.endswith(".md"):
            return cand
    return None


def first_word(value):
    m = re.match(r"[`*\s]*([^\s`*(]+)", value or "")
    return m.group(1).lower() if m else ""


def reviewed(value):
    v = (value or "").strip().strip("\"'`*()[] ").lower()
    return bool(v) and "chờ" not in v and not v.startswith(("<", "—", "-", "?", "chưa", "tbd", "todo", "n/a"))


def check_plan(plan_text, changed, uc_re):
    """(blocked, warnings) for plan.md: every changed AC in exactly one `## ` phase (text before the first is not one)."""
    blocked, warnings, where = [], [], {}
    for i, part in enumerate(re.split(r"^## ", plan_text, flags=re.M)[1:], 1):
        for pair in set(pairs_in(part, uc_re)):
            where.setdefault(pair, []).append(i)
    missing = [f"{u} {a}" for u, a in changed if (u, a) not in where]
    twice = [f"{u} {a}" for u, a in changed if len(where.get((u, a), [])) > 1]
    extra = sorted(f"{u} {a}" for u, a in where if (u, a) not in changed)
    if missing:
        blocked.append("plan.md thiếu: " + ", ".join(missing))
    if twice:
        blocked.append("plan.md đặt AC ở nhiều phase: " + ", ".join(twice))
    if extra:
        warnings.append("plan.md nhắc AC không có trong proposal: " + ", ".join(extra))
    return blocked, warnings


def main():
    ap = argparse.ArgumentParser(description="mk-cook gate")
    ap.add_argument("change")
    ap.add_argument("--done", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    path = resolve(args.change, args.root)
    if not path:
        print(f"mk-cook gate: không thấy proposal cho '{args.change}' (thư mục change, proposal.md, hoặc slug trong specs/changes/)")
        return 2
    try:
        with open(path, encoding="utf-8-sig") as fh:
            text = fh.read()
    except UnicodeDecodeError:
        print(f"mk-cook gate: {path} không phải UTF-8 — lưu lại bằng UTF-8 rồi chạy lại")
        return 2
    print(f"mk-cook gate: {os.path.relpath(path, args.root)}")

    status = header_value(text, "Status") or ""
    word = first_word(status)
    if word == "archived":
        return report(["proposal đã hợp nhất (archived) — mở change mới nếu cần đổi tiếp"], [])
    if word not in ("approved", "implemented"):
        return report([f"Status '{status or '—'}' chưa approved — chờ người duyệt nghiệp vụ và kỹ thuật"], [])
    blocked = []
    for key, who in (("Người duyệt nghiệp vụ", "nghiệp vụ"), ("Người duyệt kỹ thuật", "kỹ thuật")):
        if not reviewed(header_value(text, key)):
            blocked.append(f"thiếu người duyệt {who} (dòng `{key}:` trống, `chờ` hoặc không có) — không tự duyệt")
    if blocked:
        return report(blocked, [])

    cfg = project_config(args.root)
    uc_re = uc_pattern(cfg)
    changed, deprecated, problems, added = acs(text, uc_re)
    if not changed and not deprecated and not problems:
        hint = ""
        if re.search(r"^#{3,}\s+AC-\d", section(text, "Thay đổi spec") or "", re.M):
            hint = " (AC đang viết dạng tiêu đề `### AC-n` — trong proposal viết `- ADDED AC-n: …` dưới `### <UC-ID>`)"
        return report(["không có AC nào ADDED/MODIFIED/DEPRECATED trong `## Thay đổi spec` — không AC thì không code" + hint], [])
    blocked += problems
    orphans = [a for u, a in changed + deprecated if u is None]
    if orphans:
        blocked.append("AC không rõ thuộc UC nào: " + ", ".join(orphans)
                       + " — đặt dưới `### <UC-ID>` (một mã) hoặc ghi `ADDED <UC-ID> AC-n: …`")
    changed = [(u, a) for u, a in changed if u]
    deprecated = [(u, a) for u, a in deprecated if u]
    slug = os.path.basename(os.path.dirname(os.path.abspath(path)))
    blocked += check_numbers(cfg, args.root, slug, changed, deprecated, added, uc_re)

    warnings, plan_note = [], "không cần"
    large = first_word(header_value(text, "Quy mô")) == "lớn"
    plan_path = os.path.join(os.path.dirname(path), "plan.md")
    if os.path.isfile(plan_path):
        with open(plan_path, encoding="utf-8-sig", errors="replace") as fh:
            b, w = check_plan(fh.read(), changed, uc_re)
        blocked += b
        warnings += w
        plan_note = "có, khớp" if not b else "có, chưa khớp"
    elif len(changed) > PLAN_LIMIT or large:
        why = f"{len(changed)} AC thêm/sửa (> {PLAN_LIMIT})" if len(changed) > PLAN_LIMIT else "dòng `- Quy mô: lớn`"
        blocked.append(f"cần plan.md cạnh proposal vì {why}: mỗi phase nêu `<UC-ID> AC-n` nó làm")
        plan_note = "thiếu"

    if args.done:
        evidence = section(text, "Bằng chứng nghiệm thu")
        if evidence is None:
            blocked.append("chưa có mục `## Bằng chứng nghiệm thu`")
        else:
            holes = sorted(set(PLACEHOLDER.findall(BACKTICKS.sub("", evidence))))
            if holes:
                blocked.append("bằng chứng còn chỗ trống mẫu: " + ", ".join(holes))
            have = set(pairs_in(evidence, uc_re))
            missing = [f"{u} {a}" for u, a in changed + deprecated if (u, a) not in have]
            if missing:
                blocked.append("bằng chứng chưa nhắc: " + ", ".join(missing))

    print(f"Status: {word} · {len({u for u, _ in changed + deprecated})} UC · {len(changed)} AC thêm/sửa"
          f" · {len(deprecated)} AC bỏ · plan.md: {plan_note}")
    if not args.done:
        for title, pairs in (("Test cần viết (đỏ trước khi code):", changed), ("Bỏ (xoá/sửa test, code):", deprecated)):
            if pairs:
                print(title)
                for u in dict.fromkeys(u for u, _ in pairs):
                    print(f"  {u}: " + ", ".join(a for x, a in pairs if x == u))
    return report(blocked, warnings)


def report(blocked, warnings):
    for w in warnings:
        print(f"CẢNH BÁO: {w}")
    for b in blocked:
        print(f"CHẶN: {b}")
    print("CHẶN" if blocked else "OK")
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
