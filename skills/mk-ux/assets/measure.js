/*
 * mk-ux measure.js — hợp đồng đo v1 ("mk-ux-measure", v 1). Chỉ ĐỌC trang.
 *
 * Cách dùng: đặt khổ trình duyệt đúng bề rộng (320, 390, 768, 1440), rồi chạy cả file này
 * trong trang bằng công cụ trình duyệt của bạn, ví dụ `page.evaluate(<nội dung file>)`.
 *   - Tuỳ chọn trước khi chạy: window.MK_UX_SCREEN = "ten-man" (slug [a-z0-9-]+, mặc định "screen").
 *   - Biểu thức cuối trả về CHUỖI JSON (JSON.stringify(result)) — lưu nguyên thành
 *     `<screen>@<width>.json` rồi chạy `python3 scripts/ux.py score <thư mục>`.
 *   - Muốn nhận object thay vì chuỗi: đặt window.MK_UX_RETURN = "object" trước khi chạy.
 *
 * An toàn: không gọi mạng, không lưu trữ, không bấm, không ghi DOM (chỉ dùng một canvas 1×1
 * tách rời để chuẩn hoá màu). Có cuộn cửa sổ để đo `scrolls`, xong trả về vị trí cũ — cuộn có thể
 * làm trang tự tải thêm (lazy-load, cuộn vô tận, đo lường của trang): ưu tiên môi trường dữ liệu giả.
 * Trang có thể ghi đè hàm đo của trình duyệt: kết quả là dữ liệu, đối chiếu với ảnh chụp.
 * Không ghi chữ tự do của trang: chỉ thẻ, id, class, vai (cắt 40 ký tự), data-ux, và data-text chỉ khi là "caption".
 */
(function () {
  "use strict";
  var MAX = 2000;
  var PATTERNS = ["data-table", "form", "overlay", "pager", "toolbar", "mobile-header", "one-row",
    "lesson-video", "slide", "image"];
  var HAS = ["search", "pager", "page-size", "range", "overlay-head", "overlay-actions"];
  var ROLES_INTERACTIVE = ["button", "link", "tab", "checkbox", "switch"];
  var NOT_TEXT_INPUT = ["hidden", "checkbox", "radio", "submit", "button", "reset", "image", "range",
    "color", "file"];

  var rawScreen = typeof window.MK_UX_SCREEN === "string" ? window.MK_UX_SCREEN : "screen";
  var screen = /^[a-z0-9-]+$/.test(rawScreen) ? rawScreen : "screen";
  var sx = window.scrollX, sy = window.scrollY;

  function r1(v) { return Math.round(v * 10) / 10; }

  // ---------- colour: any CSS colour -> [r,g,b,a] sRGB ----------
  var canvas = null, ctx = null, cache = {};
  function rgba(css) {
    if (cache[css]) return cache[css];
    var m = /^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)$/.exec(css);
    var out;
    if (m) {
      var a = m[4] === undefined ? 1 : (m[4].slice(-1) === "%" ? parseFloat(m[4]) / 100 : parseFloat(m[4]));
      out = [+m[1], +m[2], +m[3], a];
    } else {
      if (!canvas) {
        canvas = document.createElement("canvas");
        canvas.width = 1; canvas.height = 1;
        ctx = canvas.getContext("2d", { willReadFrequently: true });
      }
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillStyle = "rgba(0,0,0,0)";
      ctx.fillStyle = css;
      ctx.fillRect(0, 0, 1, 1);
      var d = ctx.getImageData(0, 0, 1, 1).data;
      out = [d[0], d[1], d[2], Math.round(d[3] / 255 * 1000) / 1000];
    }
    cache[css] = out;
    return out;
  }

  // Background behind the element: composite layers up the tree until opaque (white at the end).
  function background(el) {
    var layers = [];
    for (var n = el; n && n.nodeType === 1; n = n.parentElement) {
      var cs = getComputedStyle(n);
      var img = cs.backgroundImage;
      if (img && img !== "none") return { bg: null, why: img.indexOf("gradient") >= 0 ? "gradient" : "image" };
      var c = rgba(cs.backgroundColor);
      if (c[3] > 0) {
        layers.push(c);
        if (c[3] >= 1) break;
      }
    }
    var base = [255, 255, 255];
    for (var k = layers.length - 1; k >= 0; k--) {
      var t = layers[k];
      base = [0, 1, 2].map(function (j) { return t[j] * t[3] + base[j] * (1 - t[3]); });
    }
    return { bg: [Math.round(base[0]), Math.round(base[1]), Math.round(base[2]), 1], why: null };
  }

  // ---------- element facts ----------
  function selector(el) {
    function part(n) {
      var s = n.tagName.toLowerCase();
      if (n.id) return s + "#" + n.id;
      var cls = typeof n.className === "string" ? n.className.trim().split(/\s+/).filter(Boolean) : [];
      return cls.length ? s + "." + cls.slice(0, 2).join(".") : s;
    }
    var parts = [part(el)];
    for (var n = el.parentElement; n && n !== document.body && n !== document.documentElement && parts.length < 4;
      n = n.parentElement) {
      if (parts[0].indexOf("#") >= 0) break;
      var next = part(n) + " > " + parts.join(" > ");
      if (next.length > 80) break;
      parts.unshift(part(n));
    }
    var sel = parts.join(" > ");
    return sel.length > 80 ? sel.slice(0, 79) + "…" : sel;
  }

  function hidden(el, cs, rect) {
    if (rect.width <= 0 || rect.height <= 0) return true;
    if (cs.visibility === "hidden" || cs.visibility === "collapse" || cs.display === "none") return true;
    if (el.closest("[aria-hidden=true]")) return true;
    if (el.matches(":disabled")) return true;
    return false;
  }

  function hasOwnText(el) {
    for (var c = el.firstChild; c; c = c.nextSibling) {
      if (c.nodeType === 3 && /\S/.test(c.nodeValue)) return true;
    }
    return false;
  }

  function isInteractive(el, tag) {
    if (tag === "a") return el.hasAttribute("href");
    if (tag === "button" || tag === "select" || tag === "textarea" || tag === "summary") return true;
    if (tag === "input") return (el.getAttribute("type") || "").toLowerCase() !== "hidden";
    if (ROLES_INTERACTIVE.indexOf(el.getAttribute("role") || "") >= 0) return true;
    var ti = el.getAttribute("tabindex");
    return ti !== null && parseInt(ti, 10) >= 0;
  }

  function isTextInput(el, tag) {
    if (tag === "select" || tag === "textarea") return true;
    return tag === "input" && NOT_TEXT_INPUT.indexOf((el.getAttribute("type") || "text").toLowerCase()) < 0;
  }

  // A link inside a sentence: its nearest block ancestor holds more text than the link itself.
  function isInline(el, tag) {
    if (tag !== "a" && el.getAttribute("role") !== "link") return false;
    var block = el.parentElement;
    while (block && getComputedStyle(block).display.indexOf("inline") === 0) block = block.parentElement;
    if (!block) return false;
    var own = (el.textContent || "").replace(/\s+/g, "").length;
    var all = (block.textContent || "").replace(/\s+/g, "").length;
    return all > own;
  }

  // ---------- walk ----------
  var all = document.body ? document.body.querySelectorAll("*") : [];
  var elements = [], visible = new Map(), truncated = false, h1 = 0;
  for (var i = 0; i < all.length; i++) {
    var el = all[i];
    var tag = el.tagName.toLowerCase();
    if (tag === "script" || tag === "style" || tag === "template" || tag === "noscript") continue;
    var cs = getComputedStyle(el);
    var rect = el.getBoundingClientRect();
    if (hidden(el, cs, rect)) continue;
    visible.set(el, i);
    if (tag === "h1") h1++;
    if (elements.length >= MAX) { truncated = true; continue; }
    var b = background(el);
    elements.push({
      i: i,
      sel: selector(el),
      tag: tag,
      role: (el.getAttribute("role") || "").slice(0, 40) || null,
      ux: (el.getAttribute("data-ux") || "").slice(0, 40) || null,
      text: el.getAttribute("data-text") === "caption" ? "caption" : null,
      box: [r1(rect.left + sx), r1(rect.top + sy), r1(rect.width), r1(rect.height)],
      font: r1(parseFloat(cs.fontSize) || 0),
      weight: parseInt(cs.fontWeight, 10) || 400,
      hasText: hasOwnText(el),
      fg: rgba(cs.color),
      bg: b.bg,
      bgWhy: b.why,
      inline: isInline(el, tag),
      interactive: isInteractive(el, tag),
      input: isTextInput(el, tag)
    });
  }

  // ---------- patterns ----------
  function labelled(input) {
    if (input.labels && input.labels.length) return true;
    if ((input.getAttribute("aria-label") || "").trim()) return true;
    return !!(input.getAttribute("aria-labelledby") || "").trim();
  }
  var patterns = [];
  var marked = document.querySelectorAll("[data-ux]");
  for (var p = 0; p < marked.length; p++) {
    var box = marked[p];
    var name = box.getAttribute("data-ux");
    if (PATTERNS.indexOf(name) < 0 || !visible.has(box)) continue;
    var has = [];
    var kids = box.querySelectorAll("[data-ux]");
    for (var k = 0; k < kids.length; k++) {
      var v = kids[k].getAttribute("data-ux");
      if (HAS.indexOf(v) >= 0 && has.indexOf(v) < 0) has.push(v);
    }
    var fields = box.querySelectorAll("input, select, textarea");
    var allLabelled = true, inputs = 0;
    for (var f = 0; f < fields.length; f++) {
      var fld = fields[f];
      var ft = (fld.getAttribute("type") || "").toLowerCase();
      if (!visible.has(fld) || ["hidden", "submit", "button", "reset", "image"].indexOf(ft) >= 0) continue;
      inputs++;
      if (!labelled(fld)) { allLabelled = false; break; }
    }
    if (allLabelled && inputs > 0) has.push("label-all");
    var rowsTop = [];
    for (var c = box.firstElementChild; c; c = c.nextElementSibling) {
      if (visible.has(c)) rowsTop.push(Math.round(c.getBoundingClientRect().top + sy));
    }
    patterns.push({ i: visible.get(box), ux: name, has: has.sort(), rowsTop: rowsTop });
  }

  // ---------- scrolls: half a viewport per step, then restore ----------
  var primaries = [];
  visible.forEach(function (idx, node) {
    if (node.getAttribute("data-ux") === "primary") primaries.push([idx, node]);
  });
  var scrolls = [];
  var vh = window.innerHeight, vw = window.innerWidth;
  var step = Math.max(1, Math.round(vh * 0.5));
  var maxY = Math.max(0, document.documentElement.scrollHeight - vh);
  for (var y = 0, n = 0; n < 400; y += step, n++) {
    window.scrollTo({ left: sx, top: Math.min(y, maxY), behavior: "instant" });
    var seen = [];
    for (var q = 0; q < primaries.length; q++) {
      var pr = primaries[q][1].getBoundingClientRect();
      if (pr.bottom > 0 && pr.top < vh && pr.right > 0 && pr.left < vw) seen.push(primaries[q][0]);
    }
    scrolls.push({ y: Math.round(window.scrollY), primary: seen });
    if (y >= maxY) break;
  }
  window.scrollTo({ left: sx, top: sy, behavior: "instant" });

  var result = {
    tool: "mk-ux-measure",
    v: 1,
    screen: screen,
    width: Math.round(window.innerWidth),
    innerWidth: window.innerWidth,
    innerHeight: window.innerHeight,
    docScrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    h1: h1,
    truncated: truncated,
    elements: elements,
    scrolls: scrolls,
    patterns: patterns
  };
  return window.MK_UX_RETURN === "object" ? result : JSON.stringify(result);
})();
