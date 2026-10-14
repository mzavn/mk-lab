#!/usr/bin/env bash
# Install the mk-specs skill (copies, never symlinks). Safe to re-run: missing pieces are added, existing ones kept or updated.
#   --global          → ~/.claude/skills/mk-specs and ~/.agents/skills/mk-specs
#   --project <dir>   → <dir>/.claude/skills/mk-specs, <dir>/specs/mk-specs.yml (template, only if missing),
#                       mk-specs block in <dir>/AGENTS.md, `@AGENTS.md` in CLAUDE.md, a pointer line in GEMINI.md if present
#   --agents-dir      → with --project: also copy to <dir>/.agents/skills/mk-specs (kept up to date once present)
#   --no-agent-files  → with --project: don't touch AGENTS.md / CLAUDE.md / GEMINI.md
#   --update          → first pull the latest release (fast-forward `main`), then install; alone = --update --global
#   --check           → only tell whether a newer release exists (reads tags, changes nothing)
#   --force           → overwrite a project copy that has local edits
#   --uninstall       → remove instead of install (with --global and/or --project; config and import lines are kept)
# Flags combine: install.sh --update --global --project .
# Without a clone: curl -fsSL https://raw.githubusercontent.com/mzavn/mk-skills/main/install.sh | bash -s -- --global
#   (clones to $MK_SKILLS_HOME, default ~/.mk-skills, then runs from there)
set -euo pipefail

SKILL=mk-specs
# Piped (`curl … | bash`) → BASH_SOURCE is empty: never trust the current directory, always bootstrap from the clone.
SELF="${BASH_SOURCE[0]:-}"
ROOT=""
if [ -n "$SELF" ] && [ -f "$SELF" ]; then ROOT="$(cd "$(dirname "$SELF")" && pwd)"; fi
SRC="$ROOT/skills/$SKILL"
MANIFEST=.mk-specs-manifest
SOURCE_FILE=.mk-specs-source  # global copies only: path of the mk-skills checkout, so agents can suggest the update command
REPO_URL="${MK_SKILLS_REPO:-https://github.com/mzavn/mk-skills.git}"
ARGS=("$@")

usage() { sed -n '2,14p' "$ROOT/install.sh" 2>/dev/null | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
die() { echo "install.sh: $*" >&2; exit 1; }

# Piped from curl (no checkout around the script): clone or refresh $MK_SKILLS_HOME and run the installer from there.
if [ -z "$ROOT" ] || [ ! -f "$SRC/SKILL.md" ]; then
  case " ${ARGS[*]-} " in *" --check "*)
    die "--check runs from a local copy: python3 ~/.claude/skills/mk-specs/scripts/check-update.py (nothing is downloaded)";;
  esac
  command -v git >/dev/null || die "git is required"
  home="${MK_SKILLS_HOME:-$HOME/.mk-skills}"
  if [ -d "$home/.git" ]; then
    git -C "$home" pull --ff-only -q || die "cannot fast-forward $home; fix or delete it, then re-run"
  else
    git clone -q --depth 1 "$REPO_URL" "$home" || die "cannot clone $REPO_URL"
  fi
  MK_SKILLS_UPDATED=1 exec bash "$home/install.sh" ${ARGS[@]+"${ARGS[@]}"}
fi

GLOBAL=0 FORCE=0 UNINSTALL=0 UPDATE=0 AGENTS_DIR=0 AGENT_FILES=1 PROJECTS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --global) GLOBAL=1 ;;
    --project) [ $# -ge 2 ] || die "--project needs a directory"; PROJECTS+=("$2"); shift ;;
    --project=*) PROJECTS+=("${1#--project=}") ;;
    --force) FORCE=1 ;;
    --agents-dir) AGENTS_DIR=1 ;;
    --no-agent-files) AGENT_FILES=0 ;;
    --uninstall) UNINSTALL=1 ;;
    --update) UPDATE=1 ;;
    --check) exec python3 "$SRC/scripts/check-update.py" ;;
    -h|--help) usage 0 ;;
    *) echo "install.sh: unknown option: $1" >&2; usage 1 ;;
  esac
  shift
done
if [ "$UPDATE" = 1 ]; then
  [ "$UNINSTALL" = 0 ] || die "--update and --uninstall do not combine"
  [ "$GLOBAL" = 1 ] || [ ${#PROJECTS[@]} -gt 0 ] || GLOBAL=1
  if [ -z "${MK_SKILLS_UPDATED:-}" ]; then
    git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 ||
      die "--update needs a git checkout of mk-skills ($ROOT is not one); reinstall with the curl line in --help"
    before="$(git -C "$ROOT" rev-parse --short HEAD)"
    git -C "$ROOT" pull --ff-only -q ||
      die "cannot fast-forward $ROOT (local commits or edits?); resolve them, then re-run"
    echo "mk-skills: $before → $(git -C "$ROOT" rev-parse --short HEAD)"
    MK_SKILLS_UPDATED=1 exec bash "$ROOT/install.sh" "${ARGS[@]}"  # the installer itself may have changed
  fi
fi
[ "$GLOBAL" = 1 ] || [ ${#PROJECTS[@]} -gt 0 ] || usage 1

VERSION="$(grep -m1 -E '^[[:space:]]*version:' "$SRC/SKILL.md" | sed -E 's/.*version:[[:space:]]*"?([^"]*)"?.*/\1/')"

# Checksum list of the installed files (manifest itself and caches excluded).
manifest_of() {
  (cd "$1" && find . -type f ! -name "$MANIFEST" ! -name "$SOURCE_FILE" ! -name '.DS_Store' ! -path '*/__pycache__/*' -print | LC_ALL=C sort |
    while IFS= read -r f; do printf '%s %s\n' "$(cksum < "$f" | tr -s ' ' | cut -d' ' -f1,2)" "$f"; done)
}

copy_skill() {
  local dest="$1" tmp
  mkdir -p "$(dirname "$dest")"
  tmp="$(mktemp -d "$(dirname "$dest")/.$SKILL.XXXXXX")"
  (cd "$SRC" && tar cf - --exclude '__pycache__' --exclude '.DS_Store' .) | (cd "$tmp" && tar xf -)
  manifest_of "$tmp" > "$tmp/$MANIFEST"
  rm -rf "$dest"
  mv "$tmp" "$dest"
}

# Local edits = files that differ from what install.sh last wrote (the manifest), whether committed or not: an
# update would overwrite them. A copy that still matches the manifest is always safe to replace. Without a
# manifest (copies older than the manifest), fall back to git: tracked files modified, or untracked files.
# Prints the offending paths.
has_local_edits() {
  local proj="$1" dest="$2" rel=".claude/skills/$SKILL" changed
  [ -d "$dest" ] || return 1
  if [ -f "$dest/$MANIFEST" ]; then
    changed="$(diff <(cat "$dest/$MANIFEST") <(manifest_of "$dest") | sed -n 's/^[<>] [0-9]* [0-9]* \.\///p' | LC_ALL=C sort -u)"
  elif git -C "$proj" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    changed="$(git -C "$proj" status --porcelain --untracked-files=all -- "$rel")"
  else
    changed="(no manifest and not a git repo — cannot tell)"
  fi
  [ -n "$changed" ] || return 1
  printf '%s\n' "$changed" | sed 's/^/  /' >&2
}

refuse_edits() {
  die "$1 has edits not made by install.sh (listed above); an update would overwrite them.
  Repo-specific rules belong in AGENTS.md outside the mk-specs block. Keep a copy if needed, then re-run with --force."
}

installed_version() {
  [ -f "$1/SKILL.md" ] && grep -m1 -E '^[[:space:]]*version:' "$1/SKILL.md" | sed -E 's/.*version:[[:space:]]*"?([^"]*)"?.*/\1/' || echo none
}

echo "mk-specs $VERSION"

if [ "$GLOBAL" = 1 ]; then
  for base in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
    dest="$base/$SKILL"
    if [ "$UNINSTALL" = 1 ]; then
      rm -rf "$dest" && echo "removed $dest"
    else
      old="$(installed_version "$dest")"
      copy_skill "$dest"
      echo "$ROOT" > "$dest/$SOURCE_FILE"
      echo "global: $dest ($old → $VERSION)"
    fi
  done
fi

for proj in ${PROJECTS[@]+"${PROJECTS[@]}"}; do
  [ -d "$proj" ] || die "project directory not found: $proj"
  proj="$(cd "$proj" && pwd)"
  dest="$proj/.claude/skills/$SKILL"
  if [ "$UNINSTALL" = 1 ]; then
    if [ "$FORCE" != 1 ] && has_local_edits "$proj" "$dest"; then refuse_edits "$dest"; fi
    rm -rf "$dest" && echo "removed $dest (kept specs/mk-specs.yml)"
    if [ -d "$proj/.agents/skills/$SKILL" ]; then rm -rf "$proj/.agents/skills/$SKILL" && echo "removed $proj/.agents/skills/$SKILL"; fi
    if [ "$AGENT_FILES" = 1 ]; then python3 "$SRC/scripts/agent-files.py" "$proj" --uninstall; fi
    continue
  fi
  if [ "$FORCE" != 1 ] && has_local_edits "$proj" "$dest"; then refuse_edits "$dest"; fi
  old="$(installed_version "$dest")"
  copy_skill "$dest"
  echo "project: $dest ($old → $VERSION)"
  cfg="$proj/specs/mk-specs.yml"
  if [ -f "$cfg" ]; then
    echo "config: $cfg (kept)"
  else
    mkdir -p "$proj/specs"
    cp "$SRC/assets/mk-specs.yml.template" "$cfg"
    echo "config: $cfg (created from template — edit contexts, ids, tests, metrics.since)"
  fi
  if [ "$AGENTS_DIR" = 1 ] || [ -d "$proj/.agents/skills/$SKILL" ]; then
    copy_skill "$proj/.agents/skills/$SKILL"
    echo "project: $proj/.agents/skills/$SKILL ($VERSION)"
  fi
  if [ "$AGENT_FILES" = 1 ]; then python3 "$SRC/scripts/agent-files.py" "$proj"; fi
done
