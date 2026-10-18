#!/usr/bin/env python3
"""Tell the user when a newer mk-specs release exists. Never updates anything, never fails the caller.

Usage (from the project root): python3 <skill>/scripts/check-update.py
- "In use" = project copy `.claude/skills/mk-specs` if present, else the global copy (~/.claude/skills, ~/.agents/skills),
  else the copy this script belongs to.
- "Latest" = highest tag vX.Y.Z of the skill repo, read with `git ls-remote --tags` (no download, nothing written, no code run).
- Project copy and global copy differ → one extra line (no network needed).
- MK_SKILLS_NO_UPDATE_CHECK=1 → no network. MK_SKILLS_REPO overrides the repo read for tags (tests, forks); the
  CHANGELOG link and curl line still point at mzavn/mk-lab.
The agent tells the user only lines containing "có bản mới" or "khác bản cài chung". Always exits 0.
"""
import os
import re
import shlex
import subprocess
import sys

sys.dont_write_bytecode = True
REPO = os.environ.get("MK_SKILLS_REPO") or "https://github.com/mzavn/mk-lab.git"
CHANGELOG = "https://github.com/mzavn/mk-lab/blob/main/CHANGELOG.md"
CURL = "curl -fsSL https://raw.githubusercontent.com/mzavn/mk-lab/main/install.sh | bash -s --"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
GLOBALS = [os.path.join(HOME, ".claude", "skills", "mk-specs"), os.path.join(HOME, ".agents", "skills", "mk-specs")]
PROJECT = os.path.join(os.getcwd(), ".claude", "skills", "mk-specs")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def version_of(skill_dir):
    try:
        with open(os.path.join(skill_dir, "SKILL.md"), encoding="utf-8") as fh:
            m = re.search(r'^\s*version:\s*"?([0-9.]+)"?', fh.read(), re.M)
    except OSError:
        return None
    return m.group(1) if m and SEMVER.match(m.group(1)) else None


def key(v):
    return tuple(int(x) for x in v.split("."))


def latest_tag():
    if REPO.startswith("-"):  # never let an env value become a git option (--upload-pack=…)
        return None
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_HTTP_LOW_SPEED_LIMIT": "1000", "GIT_HTTP_LOW_SPEED_TIME": "10"}
    try:
        res = subprocess.run(["git", "ls-remote", "--tags", "--refs", "--", REPO, "v*"], capture_output=True, text=True,
                             timeout=10, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if res.returncode:
        return None
    found = [m.group(1) for m in re.finditer(r"refs/tags/v(\d+\.\d+\.\d+)$", res.stdout, re.M)]
    return max(found, key=key) if found else ""


def update_command(has_project, has_global):
    scope = " ".join(([] if not has_global else ["--global"]) + (["--project ."] if has_project else [])) or "--global"
    for g in GLOBALS:
        try:
            with open(os.path.join(g, ".mk-specs-source"), encoding="utf-8") as fh:
                src = fh.readline().strip()
        except OSError:
            continue
        if src and os.path.isfile(os.path.join(src, "install.sh")):
            return f"bash {shlex.quote(os.path.join(src, 'install.sh'))} --update {scope}"
    return f"{CURL} --update {scope}"


def main():
    project = version_of(PROJECT)
    has_project = project is not None
    glob = next((v for v in [version_of(g) for g in GLOBALS] if v), None)
    in_use = project or glob or version_of(HERE)
    if project and glob and project != glob:
        print(f"mk-specs: bản trong project {project} khác bản cài chung {glob} — Claude Code đọc bản cài chung, scripts dùng bản project."
              f" Đồng bộ: {update_command(True, True)}")
    if os.environ.get("MK_SKILLS_NO_UPDATE_CHECK") == "1":
        print("mk-specs: đã tắt kiểm bản mới (MK_SKILLS_NO_UPDATE_CHECK=1).")
        return
    latest = latest_tag()
    if latest is None:
        print("mk-specs: không kiểm được bản mới (mất mạng hoặc GitHub không trả lời) — bỏ qua.")
        return
    if latest == "":
        print("mk-specs: repo chưa có bản phát hành nào (tag vX.Y.Z).")
        return
    if in_use is None:
        print(f"mk-specs: bản mới nhất v{latest}; chưa thấy bản cài nào. Cài: {CURL} --global")
        return
    if key(in_use) == key(latest):
        print(f"mk-specs: đang dùng bản mới nhất v{latest}.")
    elif key(in_use) > key(latest):
        print(f"mk-specs: đang dùng {in_use} — bản chưa phát hành (mới nhất đã phát hành: v{latest}).")
    else:
        major = key(latest)[0] > key(in_use)[0]
        print(f"mk-specs: có bản mới v{latest} (đang dùng {in_use})." + (" Đây là bản lớn — cần làm thêm bước, đọc CHANGELOG trước khi cập nhật." if major else ""))
        print(f"  Có gì mới: {CHANGELOG} · Cập nhật: {update_command(has_project, glob is not None)}")


if __name__ == "__main__":
    main()
