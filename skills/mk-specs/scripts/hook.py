#!/usr/bin/env python3
"""Claude Code PreToolUse hook for mk-specs (registered by SKILL.md frontmatter once the skill is invoked).

Guards two hard gates that can be checked by pattern, and stays silent everywhere else:
- Edit/Write/MultiEdit of the generated `traceability.md` / `open-issues.md` → deny (edit UC/ADR, run gen.py).
- `git commit -m "<subject>"` whose subject has no ID-shaped scope:
    level 4 (specs/mk-specs.yml, no unpromoted specs/PRD.md): scope must match ids.uc/br/adr or be an exempt scope;
    levels 1–3 (unpromoted specs/PRD.md): only `feat`/`fix` need a story code (`BOOK-01`, `CFG.AI-02`) or `specs`.
Allows whenever unsure: no mk-specs repo, message from a file/editor/heredoc/substitution, merge/revert/fixup subjects,
bad JSON, any error. Exit code is always 0; a block is a JSON `permissionDecision: deny`.
"""
import json
import os
import re
import shlex
import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in an installed copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

GENERATED = ("traceability.md", "open-issues.md")
STORY = re.compile(r"^[A-Z][A-Z0-9]*(?:\.[A-Z0-9]+)*-\d{2,}$")
SUBJECT = re.compile(r"^([a-z]+)(?:\(([^)]*)\))?!?: ")
SKIP_PREFIX = ("Merge ", "Revert ", "fixup!", "squash!", "amend!")


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": f"mk-specs: {reason}"}}, ensure_ascii=False))


def find_project(start):
    """Nearest ancestor holding specs/mk-specs.yml or specs/PRD.md → (root, level, cfg) or None."""
    d = os.path.realpath(start or ".")
    while True:
        cfg_path = os.path.join(d, "specs", "mk-specs.yml")
        prd = os.path.join(d, "specs", "PRD.md")
        has_cfg, has_prd = os.path.isfile(cfg_path), os.path.isfile(prd)
        if has_cfg or has_prd:
            lite = has_prd and not re.search(r"^- Status:\s*promoted", read(prd), re.M)
            cfg = load_cfg(cfg_path) if has_cfg else None
            if not lite and cfg is None:
                return None
            return d, (3 if lite else 4), cfg
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_cfg(path):
    """Config values the hook needs, without validating context folders (old templates still work)."""
    import mkspecs
    try:
        return mkspecs._merge(mkspecs.DEFAULTS, mkspecs.parse_yaml(read(path)) or {})
    except Exception:
        return None


def check_edit(tool_input, cwd):
    path = tool_input.get("file_path") or tool_input.get("path")
    if not path or os.path.basename(path) not in GENERATED:
        return
    path = os.path.realpath(os.path.join(cwd, path))
    found = find_project(os.path.dirname(path))
    if not found or found[2] is None:
        return
    root, _, cfg = found
    target = os.path.normcase(os.path.realpath(os.path.join(root, cfg["specs_dir"], os.path.basename(path))))
    if os.path.normcase(path) == target:
        deny(f"`{os.path.basename(path)}` là file sinh tự động — sửa UC/ADR rồi chạy gen.py, không sửa tay.")


def commit_target(command, cwd):
    """(directory, subject) of a plain `git commit -m …` in a command, or None when unsure."""
    unquoted = re.sub(r'"(?:[^"\\]|\\.)*"|\'[^\']*\'', "", command)
    if re.search(r"[()]|\bpushd\b|\bpopd\b", unquoted):
        return None  # subshells / directory stacks: target repo is not certain
    for segment in re.split(r"&&|\|\||;|\n", command):
        try:
            words = shlex.split(segment)
        except ValueError:
            return None
        if len(words) >= 2 and words[0] == "cd":
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        if not words or words[0] != "git":
            continue
        i, here = 1, cwd
        while i < len(words) and words[i].startswith("-"):
            if words[i] == "-C" and i + 1 < len(words):
                here = os.path.join(cwd, os.path.expanduser(words[i + 1]))
                i += 1
            i += 1
        if i >= len(words) or words[i] != "commit":
            continue
        args, message = words[i + 1:], None
        for j, a in enumerate(args):
            if a in ("-m", "--message") and j + 1 < len(args):
                message = args[j + 1]
            elif a.startswith("--message="):
                message = a.split("=", 1)[1]
            elif re.fullmatch(r"-[a-zA-Z]*m", a) and j + 1 < len(args):
                message = args[j + 1]
            elif re.fullmatch(r"-[a-zA-Z]*m.+", a) and not a.startswith("--"):
                message = a[a.index("m") + 1:]
            if message is not None:
                break
        if message is None or re.search(r"[$`]|<<", message):
            return None
        return here, message.split("\n", 1)[0].strip()
    return None


def subject_problem(subject, level, cfg):
    """Reason (Vietnamese) a commit subject lacks the ID scope this repo needs, or None. Shared with the repo git hook."""
    if not subject or subject.startswith(SKIP_PREFIX):
        return None
    m = SUBJECT.match(subject)
    kind = m.group(1) if m else None
    scopes = [s.strip() for s in (m.group(2) or "").split(",") if s.strip()] if m else []
    raw = (cfg or {}).get("metrics", {}).get("exempt_scopes")
    exempt = {str(s) for s in (["specs"] if raw is None else raw) if re.fullmatch(r"[\w.-]+", str(s))}
    if level == 3:
        if kind not in ("feat", "fix") or any(STORY.match(s) or s in exempt for s in scopes):
            return None
        return (f"commit `{subject}` thiếu mã story. Mẫu: `{kind or 'feat'}(BOOK-01): …` (mã trong specs/PRD.md); "
                f"việc không thuộc story nào dùng scope miễn trừ, vd `chore(specs): …`.")
    import mkspecs
    patterns = [p for p in (cfg["ids"].get(k) for k in ("uc", "br", "adr")) if p]
    try:
        for p in patterns:
            mkspecs.safe_regex(p, "ids")
    except mkspecs.ConfigError:
        return None  # a pattern that may hang: stand down rather than risk it
    if any(any(re.fullmatch(p, s) for p in patterns) for s in scopes) or (scopes and all(s in exempt for s in scopes)):
        return None
    return (f"commit `{subject}` thiếu ID UC/BR/ADR. Mẫu: `{kind or 'feat'}(UC-101): …`; việc toàn repo dùng scope miễn trừ "
            f"({', '.join(sorted(exempt)) or 'chưa khai'}), thêm scope vào `metrics.exempt_scopes` của specs/mk-specs.yml nếu cần.")


def check_commit(command, cwd):
    if "commit" not in command:
        return
    target = commit_target(command, cwd)
    if not target:
        return
    here, subject = target
    if not subject or subject.startswith(SKIP_PREFIX):
        return
    found = find_project(here)
    if not found:
        return
    _, level, cfg = found
    reason = subject_problem(subject, level, cfg)
    if reason:
        deny(reason)


def main():
    try:
        event = json.loads(sys.stdin.read())
        tool, tool_input = event.get("tool_name"), event.get("tool_input") or {}
        cwd = event.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        if tool in ("Edit", "Write", "MultiEdit"):
            check_edit(tool_input, cwd)
        elif tool == "Bash":
            check_commit(tool_input.get("command") or "", cwd)
    except Exception:
        pass  # a broken guard must never block work


if __name__ == "__main__":
    main()
