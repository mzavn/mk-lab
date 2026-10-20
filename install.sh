#!/usr/bin/env bash
# Install a skill of mk-lab (copies, never symlinks). Safe to re-run: missing pieces are added, existing ones kept or updated.
#   --skill <name>    → which skill (default mk-specs; also --skill=<name>); the ones below say mk-specs, read <name>
#   --global          → ~/.claude/skills/mk-specs and ~/.agents/skills/mk-specs
#   --project <dir>   → <dir>/.claude/skills/mk-specs, <dir>/specs/mk-specs.yml (template, only if missing),
#                       mk-specs block in <dir>/AGENTS.md, `@AGENTS.md` in CLAUDE.md, a pointer line in GEMINI.md if present
#                       (other skills: only the skill folder — no config, no agent files)
#   --agents-dir      → with --project: also copy to <dir>/.agents/skills/mk-specs (kept up to date once present)
#   --no-agent-files  → with --project: don't touch AGENTS.md / CLAUDE.md / GEMINI.md
#   --update          → first move the checkout to the newest release (tag vX.Y.Z, fast-forward only), then install;
#                       alone = --update --global. Refuses a checkout past that release (unreleased commits).
#                       Without --skill: refreshes every skill install.sh put there (mk-specs if none yet)
#   --check           → only tell whether a newer release exists (reads tags, changes nothing; not with --skill)
#   --force           → overwrite a project copy that has local edits, or a skill folder install.sh did not create
#                       (no .mk-specs-manifest; for global mk-specs a folder with .mk-specs-source is replaced anyway)
#   --uninstall       → remove instead of install (with --global and/or --project; config and import lines are kept)
# Flags combine: install.sh --update --global --project .
# Without a clone: curl -fsSL https://raw.githubusercontent.com/mzavn/mk-lab/main/install.sh | bash -s -- --global
#   (clones the newest release tag to $MK_LAB_HOME, default ~/.mk-lab, then runs from there)
set -euo pipefail
# Piped (`curl … | bash`) → BASH_SOURCE is empty: never trust the current directory, always bootstrap from the clone.
# Read here, at top level: inside a function some bash versions report the shell's own name for a piped script.
SELF="${BASH_SOURCE[0]:-}"

# Everything below is one function, called on the last line: a `curl | bash` cut short runs nothing.
main() {
DEFAULT_SKILL=mk-specs
ROOT=""
if [ -n "$SELF" ] && [ -f "$SELF" ]; then ROOT="$(cd "$(dirname "$SELF")" && pwd)"; fi
MANIFEST=.mk-specs-manifest
SOURCE_FILE=.mk-specs-source  # global copies only: path of the mk-lab checkout, so agents can suggest the update command
REPO_URL="${MK_LAB_REPO:-https://github.com/mzavn/mk-lab.git}"
ARGS=("$@")

# The comment block at the top of this file, whatever its length.
usage() { awk 'NR == 1 { next } !/^#/ { exit } { sub(/^# ?/, ""); print }' "$ROOT/install.sh" 2>/dev/null; exit "${1:-0}"; }
die() { echo "install.sh: $*" >&2; exit 1; }
skill_list() {
  local f
  for f in "$ROOT"/skills/*/SKILL.md; do [ -f "$f" ] && basename "$(dirname "$f")"; done | LC_ALL=C sort | paste -sd, - | sed 's/,/, /g'
}
die_skill() { die "$* (skills: $(skill_list))"; }

# Newest release tag vX.Y.Z (by version, not by text) among the tag names on stdin; empty when there is none.
newest_tag() { grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -t. -k1.2,1n -k2,2n -k3,3n | tail -n 1 || true; }

# Move checkout $1 to the newest release tag of its remote, fast-forward only: code that has no release tag is never
# pulled in to run. $2 = the way out when the checkout cannot get there (own commits, or already past that release).
to_release() {
  local dir="$1" other="$2" tag
  git -C "$dir" fetch -q --tags || die "cannot fetch release tags into $dir"
  tag="$(git -C "$dir" tag -l 'v*' | newest_tag)"
  [ -n "$tag" ] || die "no release tag (vX.Y.Z) in $dir"
  git -C "$dir" merge --ff-only -q "$tag^{commit}" ||
    die "cannot fast-forward $dir to $tag (local commits or edits?); resolve them, or $other"
  [ "$(git -C "$dir" rev-parse HEAD)" = "$(git -C "$dir" rev-parse "$tag^{commit}")" ] ||
    die "$dir is past the newest release $tag (commits not released) — --update installs releases only; $other"
  RELEASE="$tag"
}

# Piped from curl (no checkout around the script): clone or refresh $MK_LAB_HOME at the newest release, run from there.
if [ -z "$ROOT" ] || [ ! -f "$ROOT/skills/$DEFAULT_SKILL/SKILL.md" ]; then
  case " ${ARGS[*]-} " in *" --check "*)
    die "--check runs from a local copy: python3 ~/.claude/skills/mk-specs/scripts/check-update.py (nothing is downloaded)";;
  esac
  command -v git >/dev/null || die "git is required"
  home="${MK_LAB_HOME:-$HOME/.mk-lab}"
  if [ -d "$home/.git" ]; then
    to_release "$home" "delete $home (installer-managed) and re-run this line"
  else
    tag="$(git ls-remote --tags --refs -- "$REPO_URL" 'v*' | sed 's|.*refs/tags/||' | newest_tag)" ||
      die "cannot read the release tags of $REPO_URL"
    [ -n "$tag" ] || die "no release tag (vX.Y.Z) at $REPO_URL"
    { git init -q "$home" && git -C "$home" remote add origin "$REPO_URL" &&
      git -C "$home" fetch -q --depth 1 origin "+refs/tags/$tag:refs/tags/$tag" &&
      git -C "$home" -c advice.detachedHead=false checkout -q "$tag^{commit}"; } || die "cannot clone $REPO_URL ($tag)"
  fi
  MK_LAB_UPDATED=1 exec bash "$home/install.sh" ${ARGS[@]+"${ARGS[@]}"}
fi

# Only the syntax of --skill is checked here: the skill may exist only after --update has pulled.
set_skill() {
  [ -z "$SKILL_ARG" ] || die_skill "--skill given more than once"
  printf '%s\n' "$1" | grep -qE '^[a-z0-9][a-z0-9-]*$' || die_skill "--skill needs a skill name, got '$1'"
  SKILL_ARG="$1"
}

GLOBAL=0 FORCE=0 UNINSTALL=0 UPDATE=0 CHECK=0 AGENTS_DIR=0 AGENT_FILES=1 PROJECTS=() SKILL_ARG=""
while [ $# -gt 0 ]; do
  case "$1" in
    --global) GLOBAL=1 ;;
    --project) [ $# -ge 2 ] || die "--project needs a directory"; PROJECTS+=("$2"); shift ;;
    --project=*) PROJECTS+=("${1#--project=}") ;;
    --skill) [ $# -ge 2 ] || die_skill "--skill needs a skill name"; set_skill "$2"; shift ;;
    --skill=*) set_skill "${1#--skill=}" ;;
    --force) FORCE=1 ;;
    --agents-dir) AGENTS_DIR=1 ;;
    --no-agent-files) AGENT_FILES=0 ;;
    --uninstall) UNINSTALL=1 ;;
    --update) UPDATE=1 ;;
    --check) CHECK=1 ;;
    -h|--help) usage 0 ;;
    *) echo "install.sh: unknown option: $1" >&2; usage 1 ;;
  esac
  shift
done
if [ "$CHECK" = 1 ]; then
  [ -z "$SKILL_ARG" ] || die_skill "--check only reads the mk-specs release; run it without --skill"
  exec python3 "$ROOT/skills/$DEFAULT_SKILL/scripts/check-update.py"
fi
if [ "$UPDATE" = 1 ]; then
  [ "$UNINSTALL" = 0 ] || die "--update and --uninstall do not combine"
  [ "$GLOBAL" = 1 ] || [ ${#PROJECTS[@]} -gt 0 ] || GLOBAL=1
  if [ -z "${MK_LAB_UPDATED:-}" ]; then
    git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 ||
      die "--update needs a git checkout of mk-lab ($ROOT is not one); reinstall with the curl line in --help"
    before="$(git -C "$ROOT" rev-parse --short HEAD)"
    to_release "$ROOT" "install this checkout as it is: drop --update (e.g. install.sh --global --project .)"
    echo "mk-lab: $before → $(git -C "$ROOT" rev-parse --short HEAD) ($RELEASE)"
    MK_LAB_UPDATED=1 exec bash "$ROOT/install.sh" "${ARGS[@]}"  # the installer itself may have changed
  fi
fi
if [ -n "$SKILL_ARG" ] && [ ! -f "$ROOT/skills/$SKILL_ARG/SKILL.md" ]; then die_skill "no skill named '$SKILL_ARG'"; fi
[ "$GLOBAL" = 1 ] || [ ${#PROJECTS[@]} -gt 0 ] || usage 1

version_of() {
  [ -f "$1/SKILL.md" ] && grep -m1 -E '^[[:space:]]*version:' "$1/SKILL.md" | sed -E 's/.*version:[[:space:]]*"?([^"]*)"?.*/\1/' || echo none
}

# Checksum list of the installed files (manifest itself and caches excluded).
manifest_of() {
  (cd "$1" && find . -type f ! -name "$MANIFEST" ! -name "$SOURCE_FILE" ! -name '.DS_Store' ! -path '*/__pycache__/*' -print | LC_ALL=C sort |
    while IFS= read -r f; do printf '%s %s\n' "$(cksum < "$f" | tr -s ' ' | cut -d' ' -f1,2)" "$f"; done)
}

no_symlink() {
  if [ -L "$1" ]; then die "$1 is a symlink — replace it with a real folder (install.sh never writes or deletes through symlinks)"; fi
}

# A skill folder install.sh did not create (no manifest) is never replaced or removed, unless --force. Global mk-specs
# also accepts its own older copies (.mk-specs-source); a project mk-specs copy is guarded by has_local_edits instead,
# which also covers hand installs (UC-105). Every destination of one place is checked before any is written or removed.
refuse_foreign() {
  local scope="$1" d
  shift
  [ "$FORCE" != 1 ] || return 0
  [ "$SKILL" != "$DEFAULT_SKILL" ] || [ "$scope" = global ] || return 0
  for d in "$@"; do
    if [ -e "$d" ] && [ ! -f "$d/$MANIFEST" ] && { [ "$SKILL" != "$DEFAULT_SKILL" ] || [ ! -f "$d/$SOURCE_FILE" ]; }; then
      die "$d was not installed by install.sh (no $MANIFEST) — it may belong to another tool; move it away or re-run with --force"
    fi
  done
}

copy_skill() {
  local dest="$1" tmp
  no_symlink "$dest"
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
  local proj="$1" dest="$2" rel="${2#"$1"/}" changed
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
  if [ "$SKILL" = "$DEFAULT_SKILL" ]; then
    die "$1 has edits not made by install.sh (listed above); an update would overwrite them.
  Repo-specific rules belong in AGENTS.md outside the mk-specs block. Keep a copy if needed, then re-run with --force."
  fi
  die "$1 has edits not made by install.sh (listed above); an update would overwrite them.
  Keep a copy if needed, then re-run with --force."
}

use_skill() { SKILL="$1"; SRC="$ROOT/skills/$1"; VERSION="$(version_of "$SRC")"; }

# Skills to handle at one place, given its two skill folders minus the skill name ("$1/<skill>" "$2/<skill>"):
# --skill → that one; --update alone → mk-specs if present plus every other skill install.sh put there (manifest),
# or mk-specs when none is there yet; otherwise mk-specs. mk-specs first, then the others in C order.
skills_at() {
  local f s
  if [ -n "$SKILL_ARG" ]; then echo "$SKILL_ARG"; return; fi
  if [ "$UPDATE" != 1 ]; then echo "$DEFAULT_SKILL"; return; fi
  {
    if [ -e "$1/$DEFAULT_SKILL" ] || [ -e "$2/$DEFAULT_SKILL" ]; then echo "$DEFAULT_SKILL"; fi
    for f in "$ROOT"/skills/*/SKILL.md; do
      [ -f "$f" ] || continue
      s="$(basename "$(dirname "$f")")"
      [ "$s" != "$DEFAULT_SKILL" ] || continue
      if [ -f "$1/$s/$MANIFEST" ] || [ -f "$2/$s/$MANIFEST" ]; then echo "$s"; fi
    done | LC_ALL=C sort
  } | grep . || echo "$DEFAULT_SKILL"
}

do_global() {
  local base dest old
  for dest in "$HOME/.claude/skills/$SKILL" "$HOME/.agents/skills/$SKILL"; do no_symlink "$dest"; done
  refuse_foreign global "$HOME/.claude/skills/$SKILL" "$HOME/.agents/skills/$SKILL"
  for base in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
    dest="$base/$SKILL"
    if [ "$UNINSTALL" = 1 ]; then
      if [ -e "$dest" ]; then rm -rf "$dest" && echo "removed $dest"; else echo "not installed: $dest"; fi
    else
      old="$(version_of "$dest")"
      copy_skill "$dest"
      echo "$ROOT" > "$dest/$SOURCE_FILE"
      echo "global: $dest ($old → $VERSION)"
    fi
  done
}

do_project() {
  local proj="$1" dest="$1/.claude/skills/$SKILL" agents="$1/.agents/skills/$SKILL" p old cfg kept=""
  # Inside the project nothing on the path may be a symlink (a linked .claude/skills could point at the global copy).
  for p in "$proj/.claude" "$proj/.claude/skills" "$dest" "$proj/.agents" "$proj/.agents/skills" "$agents"; do no_symlink "$p"; done
  if [ "$SKILL" = "$DEFAULT_SKILL" ]; then
    for p in "$proj/specs" "$proj/specs/mk-specs.yml"; do no_symlink "$p"; done
    kept=" (kept specs/mk-specs.yml)"
  fi
  refuse_foreign project "$dest" "$agents"
  if [ "$UNINSTALL" = 1 ]; then
    if [ "$FORCE" != 1 ] && has_local_edits "$proj" "$dest"; then refuse_edits "$dest"; fi
    if [ "$FORCE" != 1 ] && has_local_edits "$proj" "$agents"; then refuse_edits "$agents"; fi
    if [ -e "$dest" ]; then rm -rf "$dest" && echo "removed $dest$kept"; else echo "not installed: $dest"; fi
    if [ -d "$agents" ]; then rm -rf "$agents" && echo "removed $agents"; fi
    if [ "$SKILL" = "$DEFAULT_SKILL" ] && [ "$AGENT_FILES" = 1 ]; then python3 "$SRC/scripts/agent-files.py" "$proj" --uninstall; fi
    return
  fi
  if [ "$FORCE" != 1 ] && has_local_edits "$proj" "$dest"; then refuse_edits "$dest"; fi
  if [ "$FORCE" != 1 ] && has_local_edits "$proj" "$agents"; then refuse_edits "$agents"; fi
  old="$(version_of "$dest")"
  copy_skill "$dest"
  echo "project: $dest ($old → $VERSION)"
  if [ "$SKILL" = "$DEFAULT_SKILL" ]; then
    cfg="$proj/specs/mk-specs.yml"
    if [ -f "$cfg" ]; then
      echo "config: $cfg (kept)"
    else
      mkdir -p "$proj/specs"
      cp "$SRC/assets/mk-specs.yml.template" "$cfg"
      echo "config: $cfg (created from template — edit contexts, ids, tests, metrics.since)"
    fi
  fi
  if [ "$AGENTS_DIR" = 1 ] || [ -d "$agents" ]; then
    copy_skill "$agents"
    echo "project: $agents ($VERSION)"
  fi
  if [ "$SKILL" = "$DEFAULT_SKILL" ] && [ "$AGENT_FILES" = 1 ]; then python3 "$SRC/scripts/agent-files.py" "$proj"; fi
}

# Plan every (place, skill) first, print each skill's version once, then act place by place.
PLACES=() PLAN_SKILLS=()
if [ "$GLOBAL" = 1 ]; then
  for s in $(skills_at "$HOME/.claude/skills" "$HOME/.agents/skills"); do PLACES+=(""); PLAN_SKILLS+=("$s"); done
fi
for proj in ${PROJECTS[@]+"${PROJECTS[@]}"}; do
  [ -d "$proj" ] || die "project directory not found: $proj"
  proj="$(cd "$proj" && pwd)"
  for s in $(skills_at "$proj/.claude/skills" "$proj/.agents/skills"); do PLACES+=("$proj"); PLAN_SKILLS+=("$s"); done
done

for s in $(printf '%s\n' "${PLAN_SKILLS[@]}" | awk '!seen[$0]++'); do
  use_skill "$s"
  echo "$SKILL $VERSION"
done

i=0
while [ "$i" -lt ${#PLACES[@]} ]; do
  use_skill "${PLAN_SKILLS[$i]}"
  if [ -z "${PLACES[$i]}" ]; then do_global; else do_project "${PLACES[$i]}"; fi
  i=$((i + 1))
done
}

main "$@"
