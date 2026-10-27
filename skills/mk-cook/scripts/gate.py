#!/usr/bin/env python3
"""mk-cook gate: may this change be coded (or reported done)? Reads the change folder only; changes nothing.

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
  Prints the AC list to write tests for (and the deprecated ones to remove).
--done also: `## Bằng chứng nghiệm thu` exists, has no `<…>` placeholder outside backticks, names every AC.
In plan.md and evidence, `UC-101 AC-1, AC-2` names both (each AC belongs to the closest ID before it).
Exit 0 pass · 1 blocked (reasons printed) · 2 bad arguments. Standard library only; output is deterministic.
"""
import argparse
import json
import os
import re
import sys

sys.dont_write_bytecode = True

PLAN_LIMIT = 5
DEFAULT_UC = r"UC-\d+"
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
QUANT = re.compile(r"[+*]|\{\d*,\d*\}")


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


def uc_pattern(root):
    """ids.uc of specs/mk-specs.yml, compiled; default when absent, too long, may hang or invalid."""
    try:
        with open(os.path.join(root, "specs", "mk-specs.yml"), encoding="utf-8") as fh:
            cfg = fh.read()
    except (OSError, UnicodeDecodeError):
        cfg = ""
    m = re.search(r"^\s+uc:\s*(?:'([^'\n]*)'|\"((?:[^\"\\\n]|\\.)*)\"|([^\s#]+))", cfg, re.M)
    raw = DEFAULT_UC
    if m and m.group(2) is not None:
        try:
            raw = json.loads('"' + m.group(2) + '"')
        except ValueError:
            pass
    elif m:
        raw = m.group(1) if m.group(1) is not None else m.group(3)
    if not raw or len(raw) > 200 or may_hang(raw):
        raw = DEFAULT_UC
    try:
        return re.compile(raw)
    except re.error:
        return re.compile(DEFAULT_UC)


def is_uc(tok, uc_re):
    return len(tok) <= 32 and uc_re.fullmatch(tok) is not None


def acs(text, uc_re):
    """(changed, deprecated, problems): changed/deprecated = [(uc, ac)] in order; uc None = owner unknown.

    `### ` heading sets the owner (exactly one UC id, else none); a deeper heading with one UC id sets it,
    one without UC ids keeps the parent's. Lines inside ``` fences are examples, not AC."""
    body = section(text, "Thay đổi spec") or ""
    changed, deprecated, problems, owner, fenced = [], [], [], None, False
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
            uc, ids, target = owner, [m.group(1)], changed
        for ac in ids:
            if (uc, ac) not in changed and (uc, ac) not in deprecated:
                target.append((uc, ac))
    return changed, deprecated, problems


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

    uc_re = uc_pattern(args.root)
    changed, deprecated, problems = acs(text, uc_re)
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
