#!/usr/bin/env python3
"""mk-ux: score page measurements, check an audit report, compute a contrast ratio. Read-only.

Usage:
  python3 <skill>/scripts/ux.py score <dir> [--design DESIGN.md] [--widths 320,390,768,1440] [--baseline <dir>]
  python3 <skill>/scripts/ux.py check <report.md>
  python3 <skill>/scripts/ux.py contrast <colour> <background>      (hex, 3 or 6 digits, with or without '#')

score reads <screen>@<width>[-suffix].json files written by assets/measure.js (measurement contract v1) and judges
them against the default thresholds or the `## Luật đo` table of DESIGN.md. JS only records raw facts; this script
decides. A rule that cannot apply prints CHƯA KIỂM (never counted as pass); a missing width prints THIẾU (fail).
check validates the `### UX-n` findings of an audit report.

Exit: score 0 all passes · 1 a pass failed or is missing · 2 bad call / bad file.
      check 0 report valid · 1 errors (one `LỖI:` line each) · 2 unreadable.
      contrast 0 computed · 2 bad colour.
Standard library only; output is deterministic (sorted, no time, no randomness).
"""
import argparse
import json
import math
import os
import re
import sys
import unicodedata

sys.dont_write_bytecode = True

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = "mk-ux-measure"
MAX_BYTES = 5 * 1024 * 1024
MAX_ELEMENTS = 2000
SEL_MAX = 80
DETAIL_MAX = 5
EPS = 0.05
DEFAULT_WIDTHS = (320, 390, 768, 1440)

# code -> (kind, default). kind: num (one number), pair (W×H), flag (on/off only).
RULES = {
    "overflow-x": ("num", 0.0),
    "text-min": ("num", 12.0),
    "body-text-mobile": ("num", 16.0),
    "input-size": ("num", 16.0),
    "tap-target": ("pair", (44.0, 44.0)),
    "tap-target-desktop": ("pair", (24.0, 24.0)),
    "contrast": ("num", 4.5),
    "contrast-large": ("num", 3.0),
    "primary-cta": ("num", 1.0),
    "h1": ("num", 1.0),
    "main-task-first-view": ("flag", True),
    "one-row": ("num", 4.0),
    "pattern-data-table": ("flag", True),
    "pattern-form": ("flag", True),
    "pattern-overlay": ("flag", True),
}
MOBILE_MAX = 768      # body-text-mobile, main-task-first-view apply below this width
TOUCH_MAX = 1024      # tap-target below, tap-target-desktop from this width
BODY_TAGS = {"p", "li", "td", "dd", "a", "button"}
BODY_EXEMPT_TAGS = {"label", "th"}
ONE_ROW_PATTERNS = {"pager", "toolbar", "mobile-header", "one-row"}
PATTERN_NEEDS = {
    "data-table": ("pattern-data-table", ("page-size", "pager", "range", "search")),
    "form": ("pattern-form", ("label-all",)),
    "overlay": ("pattern-overlay", ("overlay-actions", "overlay-head")),
}
KNOWN_UNMEASURED = {"lesson-video", "slide", "image", "video"}
FILE_RE = re.compile(r"^(?P<screen>[a-z0-9-]+)@(?P<width>\d+)(?:-[^/]*)?\.json$")
SCREEN_RE = re.compile(r"^[a-z0-9-]+$")
OFF = {"tắt", "tat", "off", "không", "khong"}
ON = {"có", "co", "bật", "bat", "on", "-", "—", ""}


class Fail(Exception):
    """Expected error: print `Lỗi: …` and exit 2."""


# ---------- text helpers ----------

def nfc(s):
    return unicodedata.normalize("NFC", s)


def clean(s, limit=SEL_MAX):
    s = "".join(" " if unicodedata.category(ch).startswith("C") else ch for ch in str(s))
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= limit else s[: limit - 1] + "…"


def num(v):
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.1f}".replace(".", ",")


def cut2(v):
    return f"{math.floor(v * 100 + 1e-9) / 100:.2f}".replace(".", ",")


def read_text(path):
    if not os.path.isfile(path):
        raise Fail(f"không đọc được {clean(path)}: không phải tệp thường")
    try:
        with open(path, "rb") as f:
            raw = f.read(MAX_BYTES + 1)
    except OSError as e:
        raise Fail(f"không đọc được {clean(path)}: {e.strerror or e}")
    if len(raw) > MAX_BYTES:
        raise Fail(f"{clean(path)} quá lớn")
    text = raw.decode("utf-8", errors="replace")
    if text.startswith("\ufeff"):
        text = text[1:]
    return nfc(text.replace("\r\n", "\n").replace("\r", "\n"))


def without_fences(lines):
    out, fenced = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        out.append("" if fenced else line)
    return out


# ---------- colour ----------

def lum(rgb):
    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(fg, bg):
    a, b = lum(fg), lum(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def over(top, under):
    """Composite an RGBA colour over an opaque colour."""
    a = top[3] if len(top) > 3 else 1
    return [top[k] * a + under[k] * (1 - a) for k in range(3)]


def parse_hex(s):
    m = re.fullmatch(r"#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", s.strip())
    if not m:
        raise Fail(f"màu không hợp lệ: {clean(s, 20)}")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return [int(h[k:k + 2], 16) for k in (0, 2, 4)]


def verdict(r):
    if r >= 4.5:
        return "đạt chữ thường"
    if r >= 3:
        return "đạt chữ lớn"
    return "không đạt"


# ---------- DESIGN.md thresholds ----------

def parse_threshold(code, value):
    kind, default = RULES[code]
    v = nfc(value).strip().strip("`").strip().lower()
    if len(v) > 40:
        raise Fail(f"ngưỡng không hợp lệ ở {code}: {clean(value, 30)}")
    if v in OFF:
        return None
    if kind == "flag":
        if v in ON:
            return True
        raise Fail(f"ngưỡng không hợp lệ ở {code}: {clean(value, 30)}")
    if kind == "pair":
        m = re.fullmatch(r"(\d+(?:[.,]\d+)?)\s*(?:px)?\s*(?:[x×]\s*(\d+(?:[.,]\d+)?)\s*(?:px)?)?", v)
        if not m:
            raise Fail(f"ngưỡng không hợp lệ ở {code}: {clean(value, 30)}")
        w = float(m.group(1).replace(",", "."))
        h = float(m.group(2).replace(",", ".")) if m.group(2) else w
        return (w, h)
    m = re.fullmatch(r"(?:[≥≤=<>]\s*)?(\d+(?:[.,]\d+)?)\s*(?:px|:1)?", v)
    if not m:
        raise Fail(f"ngưỡng không hợp lệ ở {code}: {clean(value, 30)}")
    return float(m.group(1).replace(",", "."))


def load_design(path, warnings):
    if not os.path.isfile(path):
        raise Fail(f"không có tệp DESIGN.md: {clean(path)}")
    lines = without_fences(read_text(path).split("\n"))
    rules = {code: default for code, (_kind, default) in RULES.items()}
    inside = False
    for line in lines:
        if re.match(r"^#{1,2}\s", line):
            inside = bool(re.match(r"^##\s+(\d+\.\s*)?Luật đo\s*$", line.strip()[:200]))
            continue
        if not inside or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        code = cells[0].strip("`").strip().lower()
        if not code or code == "mã" or set(code) <= set("-: "):
            continue
        if code not in RULES:
            warnings.add(f"Cảnh báo: mã luật lạ {clean(code, 40)}")
            continue
        rules[code] = parse_threshold(code, cells[-1])
    off = sorted(code for code, v in rules.items() if v is None)
    if off:
        warnings.add("Cảnh báo: tắt theo DESIGN.md: " + ", ".join(off))
    return rules


# ---------- measurement files ----------

def load_dir(path, widths, warnings):
    if not os.path.isdir(path):
        raise Fail(f"không phải thư mục: {path}")
    names = sorted(n for n in os.listdir(path) if n.endswith(".json"))
    if not names:
        raise Fail("không có file đo")
    pages = {}
    for name in names:
        full = os.path.join(path, name)
        if os.path.islink(full) or not os.path.isfile(full):
            raise Fail(f"{clean(name)} không phải tệp thường")
        try:
            with open(full, "rb") as f:
                raw = f.read(MAX_BYTES + 1)
        except OSError:
            raise Fail(f"{clean(name)} sai hợp đồng đo: json")
        if len(raw) > MAX_BYTES:
            raise Fail(f"{clean(name)} quá lớn")
        try:
            doc = json.loads(raw.decode("utf-8"))
        except (ValueError, RecursionError):
            raise Fail(f"{clean(name)} sai hợp đồng đo: json")
        check_contract(name, doc)
        key = (doc["screen"], int(doc["width"]))
        if key in pages:
            raise Fail(f"trùng lượt đo {key[0]}@{key[1]}")
        if key[1] not in widths:
            warnings.add(f"Cảnh báo: bỏ qua {clean(name)} — khổ {key[1]} ngoài --widths")
            continue
        if doc.get("truncated"):
            warnings.add(f"Cảnh báo: {key[0]}@{key[1]} đã cắt ở 2.000 phần tử")
        pages[key] = doc
    return pages


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def is_rgba(c):
    return c is None or (isinstance(c, list) and 3 <= len(c) <= 4 and all(is_num(x) for x in c))


def check_contract(name, doc):
    def bad(field):
        raise Fail(f"{clean(name)} sai hợp đồng đo: {field}")
    if not isinstance(doc, dict):
        bad("json")
    if doc.get("tool") != TOOL:
        bad("tool")
    if doc.get("v") != 1:
        bad("v")
    screen = doc.get("screen")
    if not isinstance(screen, str) or not SCREEN_RE.match(screen):
        bad("screen")
    for field in ("width", "innerWidth", "innerHeight", "docScrollWidth", "clientWidth", "h1"):
        if not is_num(doc.get(field)):
            bad(field)
    m = FILE_RE.match(name)
    if not m or m.group("screen") != screen:
        bad("screen")
    if int(m.group("width")) != int(doc["width"]):
        bad("width")
    for field in ("elements", "scrolls", "patterns"):
        if not isinstance(doc.get(field), list):
            bad(field)
    if len(doc["elements"]) > MAX_ELEMENTS:
        raise Fail(f"{clean(name)} quá lớn")
    if abs(doc["innerWidth"] - doc["width"]) > 1:
        raise Fail(f"{clean(name)} đo ở {num(doc['innerWidth'])}px, không phải {num(doc['width'])}px")
    for e in doc["elements"]:
        if not isinstance(e, dict) or not isinstance(e.get("i"), int) or isinstance(e.get("i"), bool):
            bad("elements")
        box = e.get("box")
        if not (isinstance(box, list) and len(box) == 4 and all(is_num(x) for x in box)):
            bad("elements.box")
        if not is_num(e.get("font", 0)) or not is_num(e.get("weight", 400)):
            bad("elements")
        if not is_rgba(e.get("fg")) or not is_rgba(e.get("bg")):
            bad("elements")
    for s in doc["scrolls"]:
        if not (isinstance(s, dict) and is_num(s.get("y", 0)) and isinstance(s.get("primary"), list)
                and all(isinstance(i, int) and not isinstance(i, bool) for i in s["primary"])):
            bad("scrolls")
    for p in doc["patterns"]:
        if not (isinstance(p, dict) and isinstance(p.get("ux"), str) and isinstance(p.get("i", 0), int)
                and isinstance(p.get("has", []), list) and all(isinstance(h, str) for h in p.get("has", []))
                and isinstance(p.get("rowsTop", []), list) and all(is_num(t) for t in p.get("rowsTop", []))):
            bad("patterns")


# ---------- judging one page ----------

def detail(items):
    """items: list of (i, sel, value) -> '<n> phần tử: a (v); b (v)…'."""
    items = sorted(items, key=lambda t: t[0])
    shown = "; ".join(f"{clean(sel)} ({val})" for _i, sel, val in items[:DETAIL_MAX])
    more = "; …" if len(items) > DETAIL_MAX else ""
    return f"{len(items)} phần tử: {shown}{more}"


def judge(doc, rules):
    """Return (fails: {code: text}, unchecked: {code: reason})."""
    width = doc["width"]
    els = doc["elements"]
    fails, unchecked = {}, {}

    def on(code):
        return rules.get(code) is not None

    over_px = doc["docScrollWidth"] - doc["clientWidth"]
    if on("overflow-x") and over_px > rules["overflow-x"] + EPS:
        fails["overflow-x"] = f"{num(over_px)}px"

    texty = [e for e in els if e.get("hasText") and isinstance(e.get("font"), (int, float))]
    if on("text-min"):
        bad = [(e["i"], e.get("sel", ""), f"{num(e['font'])}px") for e in texty if e["font"] < rules["text-min"] - EPS]
        if bad:
            fails["text-min"] = detail(bad)
    if on("body-text-mobile") and width < MOBILE_MAX:
        bad = [(e["i"], e.get("sel", ""), f"{num(e['font'])}px") for e in texty
               if str(e.get("tag", "")).lower() in BODY_TAGS and e.get("text") != "caption"
               and str(e.get("tag", "")).lower() not in BODY_EXEMPT_TAGS and e["font"] < rules["body-text-mobile"] - EPS]
        if bad:
            fails["body-text-mobile"] = detail(bad)
    if on("input-size"):
        bad = [(e["i"], e.get("sel", ""), f"{num(e.get('font', 0))}px") for e in els
               if e.get("input") and isinstance(e.get("font"), (int, float)) and e["font"] < rules["input-size"] - EPS]
        if bad:
            fails["input-size"] = detail(bad)

    tap_code = "tap-target" if width < TOUCH_MAX else "tap-target-desktop"
    if on(tap_code):
        tw, th = rules[tap_code]
        bad = [(e["i"], e.get("sel", ""), f"{num(e['box'][2])}×{num(e['box'][3])}") for e in els
               if e.get("interactive") and not e.get("inline")
               and (e["box"][2] < tw - EPS or e["box"][3] < th - EPS)]
        if bad:
            fails["tap-target"] = detail(bad)

    for code, large in (("contrast", False), ("contrast-large", True)):
        if not on(code):
            continue
        group = [e for e in texty if is_large(e) == large]
        hard = [e for e in group if not valid_rgba(e.get("bg")) or not valid_rgba(e.get("fg"))]
        bad = []
        for e in group:
            if e in hard:
                continue
            bg = over(e["bg"], [255, 255, 255])
            r = ratio(over(e["fg"], bg), bg)
            if r < rules[code]:
                bad.append((e["i"], e.get("sel", ""), f"{cut2(r)}:1"))
        if bad:
            fails[code] = detail(bad)
        if hard:
            unchecked[code] = f"khó đo {len(hard)} phần tử"

    if on("primary-cta"):
        primaries = {e["i"] for e in els if e.get("ux") == "primary"}
        if not primaries:
            unchecked["primary-cta"] = 'chưa đánh dấu data-ux="primary"'
        else:
            worst = []
            for s in doc["scrolls"]:
                seen = [i for i in s.get("primary", []) if i in primaries] if isinstance(s, dict) else []
                if len(seen) > len(worst):
                    worst = seen
            if len(worst) > rules["primary-cta"] + EPS:
                by_i = {e["i"]: e for e in els}
                fails["primary-cta"] = detail([(i, by_i[i].get("sel", ""), "nút chính") for i in worst])

    if on("h1") and abs(doc["h1"] - rules["h1"]) > EPS:
        fails["h1"] = f"{num(doc['h1'])} h1"

    if on("main-task-first-view") and width < MOBILE_MAX:
        tasks = [e for e in els if e.get("ux") == "main-task"]
        if not tasks:
            unchecked["main-task-first-view"] = 'chưa đánh dấu data-ux="main-task"'
        else:
            top = min(tasks, key=lambda e: (e["box"][1], e["i"]))
            if top["box"][1] >= doc["innerHeight"]:
                fails["main-task-first-view"] = detail([(top["i"], top.get("sel", ""), f"y={num(top['box'][1])}")])

    rows = []
    for p in sorted(doc["patterns"], key=lambda p: (p.get("i", 0), p["ux"])):
        name = p["ux"]
        if name in ONE_ROW_PATTERNS:
            tops = [t for t in p.get("rowsTop", []) if isinstance(t, (int, float))]
            if on("one-row") and tops and max(tops) - min(tops) > rules["one-row"] + EPS:
                rows.append(f"{clean(name, 30)} lệch {num(max(tops) - min(tops))}px")
            continue
        if name in PATTERN_NEEDS:
            code, needs = PATTERN_NEEDS[name]
            if not on(code):
                continue
            has = {h for h in p.get("has", []) if isinstance(h, str)}
            missing = sorted(set(needs) - has)
            if missing:
                fails[code] = "thiếu: " + ", ".join(missing)
            continue
        code = "pattern-" + clean(name, 30)
        unchecked[code] = "mẫu chưa có phép đo" if name in KNOWN_UNMEASURED else f"data-ux lạ {clean(name, 30)}"
    if rows:
        fails["one-row"] = "; ".join(rows)
    return fails, unchecked


def is_large(e):
    f, w = e.get("font", 0), e.get("weight", 400) or 400
    return f >= 24 - EPS or (f >= 18.66 - EPS and w >= 700)


def valid_rgba(c):
    return isinstance(c, list) and len(c) >= 3 and all(isinstance(x, (int, float)) for x in c)


# ---------- score ----------

def evaluate(path, widths, rules, warnings):
    pages = load_dir(path, widths, warnings)
    screens = sorted({s for s, _w in pages}, key=nfc)
    rows, fail_keys = [], set()
    passed = total = unchecked_n = 0
    for s in screens:
        for w in sorted(widths):
            total += 1
            key = f"{s}@{w}"
            doc = pages.get((s, w))
            if doc is None:
                rows.append(f"THIẾU: {key}")
                fail_keys.add(f"{key} thiếu")
                continue
            fails, unchecked = judge(doc, rules)
            if fails:
                for code in sorted(fails):
                    rows.append(f"TRƯỢT: {key} {code} — {fails[code]}")
                    fail_keys.add(f"{key} {code}")
            else:
                passed += 1
                rows.append(f"ĐẠT: {key}")
            for code in sorted(unchecked):
                rows.append(f"CHƯA KIỂM: {key} {code} — {unchecked[code]}")
                unchecked_n += 1
    return rows, fail_keys, passed, total, unchecked_n


def cmd_score(args):
    try:
        widths = sorted({int(x) for x in args.widths.split(",") if x.strip()})
    except ValueError:
        raise Fail(f"--widths không hợp lệ: {clean(args.widths, 40)}")
    if not widths or any(w <= 0 for w in widths):
        raise Fail(f"--widths không hợp lệ: {clean(args.widths, 40)}")
    warnings = set()
    rules = load_design(args.design, warnings) if args.design else {c: d for c, (_k, d) in RULES.items()}
    rows, fails, passed, total, unchecked = evaluate(args.dir, widths, rules, warnings)
    base = None
    if args.baseline:
        base = evaluate(args.baseline, widths, rules, set())
    out = sorted(warnings) + rows + [f"Kết quả: {passed}/{total} lượt đạt · chưa kiểm {unchecked} luật"]
    if base:
        _rows, bfails, bpassed, btotal, _u = base
        out.append(f"Đo trước: {bpassed}/{btotal} · Đo sau: {passed}/{total}")
        out += [f"SỬA ĐƯỢC: {k}" for k in sorted(bfails - fails)]
        out += [f"MỚI HỎNG: {k}" for k in sorted(fails - bfails)]
    print("\n".join(out))
    return 0 if passed == total else 1


# ---------- check ----------

REQUIRED = ("Người dùng", "Họ cảm thấy", "Hạng", "Phẩm chất", "Nguyên lý", "Điểm A", "Điểm B", "Khoảng cách",
            "Tác động", "Loại sửa", "Trạng thái")
ENUMS = {
    "Người dùng": ("người dùng", {"khách", "trong nhà"}),
    "Hạng": ("hạng", {"hỏng", "lệch hệ", "gu"}),
    "Tác động": ("tác động", {"rất cao", "cao", "trung bình", "thấp"}),
    "Loại sửa": ("loại sửa", {"trình bày", "hành vi"}),
}
QUALITIES = {"hợp lý", "dễ dùng", "tiện", "gọn", "hợp gu", "đẹp"}
FIELD_RE = re.compile(r"^\s*[-*]\s+([^:\n]{1,200}?)\s*:\s*(.*)$")
HEAD_RE = re.compile(r"^###\s+UX-(\d+)\b")
NOTE_RE = re.compile(r"\s*(?:\(.*|—.*|–.*)$")


def value(v):
    """Enum value without a trailing note: 'cao (3 màn)' / 'cao — 3 màn' -> 'cao'."""
    return NOTE_RE.sub("", v).strip().lower()


MEASURE_RE = re.compile(r"Đo trước:\s*(\d+)\s*/\s*(\d+)\s*·\s*Đo sau:\s*(\d+)\s*/\s*(\d+)")


def ids_in(rel, prefix):
    path = os.path.join(SKILL, "references", rel)
    try:
        text = read_text(path)
    except Fail:
        return set()
    return {f"{prefix}-{n}" for n in re.findall(rf"(?m)^###\s+{prefix}-(\d+)\b", text)}


def cmd_check(args):
    lines = without_fences(read_text(args.report).split("\n"))
    principles, mistakes = ids_in("principles.md", "NL"), ids_in("ai-mistakes.md", "AI")
    findings, errors, order = {}, [], []
    current = None
    for line in lines:
        m = HEAD_RE.match(line)
        if m:
            n = int(m.group(1))
            if n in findings:
                errors.append((n, f"LỖI: UX-{n} trùng mã"))
                current = None
                continue
            findings[n] = {}
            order.append(n)
            current = findings[n]
            continue
        if re.match(r"^#{1,3}\s", line):
            current = None
            continue
        if current is not None:
            f = FIELD_RE.match(line) if len(line) <= 4000 else None
            if f and f.group(1).strip() not in current:
                current[f.group(1).strip()] = f.group(2).strip()
    counts = {"mở": 0, "duyệt": 0, "đã sửa": 0, "bỏ": 0}
    for n in order:
        fields = findings[n]
        for key in REQUIRED:
            if not fields.get(key):
                errors.append((n, f"LỖI: UX-{n} thiếu {key}"))
        for key, (label, allowed) in ENUMS.items():
            raw_v = fields.get(key, "")
            parts = re.split(r"[,;]", raw_v) if key == "Người dùng" else [raw_v]
            for v in (value(p) for p in parts):
                if v and v not in allowed:
                    errors.append((n, f"LỖI: UX-{n} {label} không hợp lệ: {clean(v, 40)}"))
        q = [value(x) for x in re.split(r"[,;]", fields.get("Phẩm chất", "")) if value(x)]
        for x in q:
            if x not in QUALITIES:
                errors.append((n, f"LỖI: UX-{n} phẩm chất không hợp lệ: {clean(x, 40)}"))
        for token in re.findall(r"[A-Za-z]+-\d+|[^\s,;]+", fields.get("Nguyên lý", "")):
            if token.upper() not in principles:
                errors.append((n, f"LỖI: UX-{n} nguyên lý không có: {clean(token, 40)}"))
        for token in re.findall(r"[^\s,;]+", fields.get("Mã", "")):
            ok = token.upper() in mistakes if re.fullmatch(r"(?i)AI-\d+", token) else token.lower() in RULES
            if not ok:
                errors.append((n, f"LỖI: UX-{n} mã không có: {clean(token, 40)}"))
        status = value(fields.get("Trạng thái", ""))
        if status:
            if status in ("mở", "duyệt", "bỏ"):
                counts[status] += 1
            elif status.startswith("đã sửa"):
                if re.fullmatch(r"đã sửa\s+[0-9a-f]{7,40}", status):
                    counts["đã sửa"] += 1
                else:
                    errors.append((n, f"LỖI: UX-{n} đã sửa thiếu commit"))
            else:
                errors.append((n, f"LỖI: UX-{n} trạng thái không hợp lệ: {clean(status, 40)}"))
    if order and not any(re.match(r"^##\s+3 việc nên sửa trước\s*$", ln.strip()[:100]) for ln in lines):
        errors.append((-1, "LỖI: thiếu mục ## 3 việc nên sửa trước"))
    if counts["đã sửa"]:
        m = MEASURE_RE.search("\n".join(lines))
        if not m:
            errors.append((10 ** 9, "LỖI: thiếu số đo trước/sau"))
        elif m.group(2) != m.group(4):
            errors.append((10 ** 9, "LỖI: số lượt đo trước/sau khác nhau"))
    if errors:
        seen = []
        for _n, msg in sorted(errors, key=lambda t: (t[0], t[1])):
            if msg not in seen:
                seen.append(msg)
        print("\n".join(seen))
        return 1
    print(f"OK: {len(order)} phát hiện · mở {counts['mở']} · duyệt {counts['duyệt']} · "
          f"đã sửa {counts['đã sửa']} · bỏ {counts['bỏ']}")
    return 0


# ---------- contrast ----------

def cmd_contrast(args):
    r = ratio(parse_hex(args.colour), parse_hex(args.background))
    print(f"{cut2(r)}:1 — {verdict(r)}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="ux.py", description="mk-ux: score, check, contrast")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("dir")
    s.add_argument("--design")
    s.add_argument("--widths", default=",".join(str(w) for w in DEFAULT_WIDTHS))
    s.add_argument("--baseline")
    c = sub.add_parser("check")
    c.add_argument("report")
    k = sub.add_parser("contrast")
    k.add_argument("colour")
    k.add_argument("background")
    args = p.parse_args(argv)
    try:
        return {"score": cmd_score, "check": cmd_check, "contrast": cmd_contrast}[args.cmd](args)
    except Fail as e:
        print(f"Lỗi: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
