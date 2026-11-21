/* Small SVG charts for the home and stats pages. No dependencies. */
(function () {
  "use strict";
  const P = window.AVS_PAGE || {};
  const B = (window.AVS || {}).builder || {};
  const NS = "http://www.w3.org/2000/svg";
  const POP = ["#77d4ff", "#00a5ef", "#0084cc", "#0069a4", "#005986", "#9be3ff", "#4cc3ff", "#0a7fbf", "#5fb6e8", "#2b92d4", "#1d6fa3", "#c4eeff"];
  const CLASS_COLORS = { FIGHTER: "#ff7a1a", SWORDSMAN: "#cfd8ff", RANGER: "#a6ff3c", TANK: "#6eb4ff", MAGE: "#c86bff", HEALER: "#2ee6a0", ASSASSIN: "#ff4d5e", SUMMONER: "#18e0ff", MONSTROSITY: "#ff2e88", TACTICIAN: "#ffd400" };
  const style = (k) => (B.styles || {})[String(k || "").toUpperCase()] || { emoji: "❔", color: "#8f82c4", glow: "#c4b8f2" };
  const title = (s) => String(s || "").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
  const fmt = (n) => Math.abs(n) >= 10000 ? (n / 1000).toFixed(1).replace(/\.0$/, "") + "K" : Math.round(n).toLocaleString();
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const el = (tag, attrs = {}, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    if (parent) parent.appendChild(e);
    return e;
  };
  const tip = document.getElementById("tip");
  function showTip(e, html) {
    if (!tip) return;
    tip.innerHTML = html;
    tip.style.opacity = 1;
    const x = Math.min(window.innerWidth - tip.offsetWidth - 8, e.clientX + 14);
    const y = Math.max(8, e.clientY - tip.offsetHeight - 12);
    tip.style.left = x + "px"; tip.style.top = y + "px";
  }
  const hideTip = () => tip && (tip.style.opacity = 0);
  function hover(node, html, onclick) {
    node.addEventListener("pointermove", (e) => showTip(e, html));
    node.addEventListener("pointerleave", hideTip);
    if (onclick) { node.style.cursor = "pointer"; node.addEventListener("click", onclick); }
  }
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  function grow(node, attr, to, delay = 0) {
    if (reduce) { node.setAttribute(attr, to); return; }
    node.animate([{ [attr === "height" ? "transform" : "transform"]: attr === "height" ? "scaleY(0)" : "scaleX(0)" }, { transform: "none" }], { duration: 600, delay, easing: "cubic-bezier(.3,1.4,.5,1)", fill: "backwards" });
  }

  /* vertical bars: data = [[label, value, color?, href?]] */
  function bars(host, data, { height = 220, colors = POP, labelFn = (l) => l, valueTip = (l, v) => `${esc(l)}: <b>${fmt(v)}</b>` } = {}) {
    if (!host) return;
    host.innerHTML = "";
    const W = Math.max(320, data.length * 34), H = height, pad = { l: 34, r: 8, t: 16, b: 38 };
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img" }, host);
    const max = Math.max(1, ...data.map((d) => d[1]));
    const ih = H - pad.t - pad.b, iw = W - pad.l - pad.r, bw = iw / data.length;
    [0, 0.5, 1].forEach((f) => {
      const y = pad.t + ih * (1 - f);
      el("line", { x1: pad.l, x2: W - pad.r, y1: y, y2: y, class: "grid-line" }, svg);
      el("text", { x: pad.l - 6, y: y + 4, "text-anchor": "end" }, svg).textContent = fmt(max * f);
    });
    data.forEach(([label, value, color, href], i) => {
      const h = (value / max) * ih, x = pad.l + i * bw + bw * 0.14, y = pad.t + ih - h;
      const c = color || colors[i % colors.length];
      const r = el("rect", { x, y, width: bw * 0.72, height: Math.max(h, 1), rx: 5, fill: c, class: "bar-rect", style: `transform-origin: ${x}px ${pad.t + ih}px; color:${c}` }, svg);
      grow(r, "height", h, i * 30);
      hover(r, valueTip(label, value), href ? () => (location.href = href) : null);
      if (value) el("text", { x: x + bw * 0.36, y: y - 4, "text-anchor": "middle", class: "v" }, svg).textContent = fmt(value);
      el("text", { x: x + bw * 0.36, y: H - pad.b + 16, "text-anchor": "middle" }, svg).textContent = labelFn(label);
    });
  }

  /* horizontal bars, good for long labels */
  function hbars(host, data, { colors = POP, max: limit = 14, emoji = () => "", href = null } = {}) {
    if (!host) return;
    host.innerHTML = "";
    data = data.slice(0, limit);
    const rowH = 26, W = 420, pad = { l: 128, r: 46 }, H = data.length * rowH + 6;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img" }, host);
    const max = Math.max(1, ...data.map((d) => d[1]));
    data.forEach(([label, value, color], i) => {
      const y = i * rowH + 3, w = ((W - pad.l - pad.r) * value) / max;
      const c = color || colors[i % colors.length];
      el("text", { x: pad.l - 8, y: y + 15, "text-anchor": "end" }, svg).textContent = (emoji(label) + " " + title(label)).trim().slice(0, 20);
      const r = el("rect", { x: pad.l, y, width: Math.max(w, 2), height: rowH - 7, rx: 4, fill: c, class: "bar-rect", style: `transform-origin:${pad.l}px 0; color:${c}` }, svg);
      grow(r, "width", w, i * 25);
      hover(r, `${esc(title(label))}: <b>${fmt(value)}</b>`, href ? () => (location.href = href(label)) : null);
      el("text", { x: pad.l + w + 6, y: y + 15, class: "v" }, svg).textContent = fmt(value);
    });
  }

  /* donut with emoji legend */
  function donut(host, data, { colorFn, emoji = () => "", href = null } = {}) {
    if (!host) return;
    host.innerHTML = "";
    const total = data.reduce((s, d) => s + d[1], 0) || 1;
    const W = 420, H = 230, cx = 115, cy = 115, R = 98, r = 58;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img" }, host);
    let a0 = -Math.PI / 2;
    const top = data.slice(0, 9), rest = data.slice(9).reduce((s, d) => s + d[1], 0);
    const rows = rest ? [...top, ["OTHER", rest]] : top;
    rows.forEach(([label, value], i) => {
      const a1 = a0 + (value / total) * Math.PI * 2;
      const large = a1 - a0 > Math.PI ? 1 : 0;
      const p = (ang, rad) => [cx + Math.cos(ang) * rad, cy + Math.sin(ang) * rad];
      const [x0, y0] = p(a0, R), [x1, y1] = p(a1 - 0.0001, R), [x2, y2] = p(a1 - 0.0001, r), [x3, y3] = p(a0, r);
      const c = label === "OTHER" ? "#262626" : colorFn ? colorFn(label, i) : POP[i % POP.length];
      const path = el("path", { d: `M${x0},${y0} A${R},${R} 0 ${large} 1 ${x1},${y1} L${x2},${y2} A${r},${r} 0 ${large} 0 ${x3},${y3} Z`, fill: c, stroke: "#141414", "stroke-width": 2, class: "bar-rect", style: `color:${c}` }, svg);
      if (!reduce) path.animate([{ opacity: 0, transform: "scale(.7)" }, { opacity: 1, transform: "none" }], { duration: 500, delay: i * 50, fill: "backwards", easing: "cubic-bezier(.3,1.4,.5,1)" }), (path.style.transformOrigin = `${cx}px ${cy}px`);
      hover(path, `${emoji(label)} ${esc(title(label))}: <b>${fmt(value)}</b> (${Math.round((value / total) * 100)}%)`, href && label !== "OTHER" ? () => (location.href = href(label)) : null);
      const ly = 18 + i * 21;
      el("rect", { x: 236, y: ly - 11, width: 13, height: 13, rx: 4, fill: c }, svg);
      el("text", { x: 256, y: ly }, svg).textContent = `${emoji(label)} ${title(label)}`.trim().slice(0, 16);
      el("text", { x: W - 4, y: ly, "text-anchor": "end", class: "v" }, svg).textContent = fmt(value);
      a0 = a1;
    });
    el("text", { x: cx, y: cy - 2, "text-anchor": "middle", class: "v", style: "font-size:22px; font-family: Poppins, Inter, sans-serif; font-weight: 600" }, svg).textContent = fmt(total);
    el("text", { x: cx, y: cy + 18, "text-anchor": "middle" }, svg).textContent = "total";
  }

  /* scatter: points = [{x,y,r,c,label,href,group}] */
  function scatter(host, points, { xLabel = "", yLabel = "", groups = [], groupColor = () => "#ff2e88", legendHost = null } = {}) {
    if (!host) return;
    const hidden = new Set();
    const draw = () => {
      host.innerHTML = "";
      const W = 820, H = 380, pad = { l: 46, r: 14, t: 12, b: 36 };
      const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img" }, host);
      const xs = points.map((p) => p.x), ys = points.map((p) => p.y), rs = points.map((p) => p.r);
      const xmax = Math.max(10, ...xs) * 1.05, ymax = Math.max(10, ...ys) * 1.05, rmax = Math.max(1, ...rs), rmin = Math.min(...rs);
      const X = (v) => pad.l + (v / xmax) * (W - pad.l - pad.r), Y = (v) => H - pad.b - (v / ymax) * (H - pad.t - pad.b);
      for (let f = 0; f <= 1.001; f += 0.25) {
        el("line", { x1: pad.l, x2: W - pad.r, y1: Y(ymax * f), y2: Y(ymax * f), class: "grid-line" }, svg);
        el("line", { y1: pad.t, y2: H - pad.b, x1: X(xmax * f), x2: X(xmax * f), class: "grid-line" }, svg);
        el("text", { x: pad.l - 6, y: Y(ymax * f) + 4, "text-anchor": "end" }, svg).textContent = fmt(ymax * f);
        el("text", { x: X(xmax * f), y: H - pad.b + 16, "text-anchor": "middle" }, svg).textContent = fmt(xmax * f);
      }
      el("text", { x: W - pad.r, y: H - 4, "text-anchor": "end" }, svg).textContent = xLabel;
      el("text", { x: pad.l + 6, y: pad.t + 12 }, svg).textContent = yLabel;
      el("line", { x1: X(0), y1: Y(0), x2: X(Math.min(xmax, ymax)), y2: Y(Math.min(xmax, ymax)), stroke: "rgba(255,255,255,.18)", "stroke-dasharray": "4 6" }, svg);
      points.forEach((p, i) => {
        if (hidden.has(p.group)) return;
        const rad = 3 + ((p.r - rmin) / Math.max(1, rmax - rmin)) * 6;
        const c = groupColor(p.group);
        const dot = el("circle", { cx: X(p.x), cy: Y(p.y), r: rad, fill: c, "fill-opacity": 0.85, stroke: "#000", "stroke-width": 1, class: "dot" }, svg);
        hover(dot, `<b>${esc(p.label)}</b><br>${esc(p.sub || "")}`, p.href ? () => (location.href = p.href) : null);
      });
    };
    draw();
    if (legendHost) {
      legendHost.innerHTML = "";
      groups.forEach((g) => {
        const b = document.createElement("button");
        b.type = "button";
        b.innerHTML = `<i style="background:${groupColor(g)}"></i>${esc(title(g))}`;
        b.addEventListener("click", () => { hidden.has(g) ? hidden.delete(g) : hidden.add(g); b.classList.toggle("off"); draw(); });
        legendHost.appendChild(b);
      });
    }
  }

  /* multi-line chart over tiers */
  function lines(host, rows, series, legendHost) {
    if (!host) return;
    const hidden = new Set(series.filter((s) => s.hidden).map((s) => s.key));
    const draw = () => {
      host.innerHTML = "";
      const W = 420, H = 230, pad = { l: 40, r: 10, t: 12, b: 28 };
      const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img" }, host);
      const shown = series.filter((s) => !hidden.has(s.key));
      const max = Math.max(1, ...rows.flatMap((r) => shown.map((s) => r[s.key])));
      const X = (i) => pad.l + (i / (rows.length - 1)) * (W - pad.l - pad.r), Y = (v) => H - pad.b - (v / max) * (H - pad.t - pad.b);
      [0, 0.5, 1].forEach((f) => { el("line", { x1: pad.l, x2: W - pad.r, y1: Y(max * f), y2: Y(max * f), class: "grid-line" }, svg); el("text", { x: pad.l - 5, y: Y(max * f) + 4, "text-anchor": "end" }, svg).textContent = fmt(max * f); });
      rows.forEach((r, i) => { el("text", { x: X(i), y: H - 8, "text-anchor": "middle" }, svg).textContent = `T${r.tier}`; });
      shown.forEach((s) => {
        const pts = rows.map((r, i) => [X(i), Y(r[s.key]), r]).filter((p) => p[2].count);
        if (!pts.length) return;
        const path = el("polyline", { points: pts.map((p) => p.slice(0, 2).join(",")).join(" "), fill: "none", stroke: s.color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
        if (!reduce) { const len = 2000; path.style.strokeDasharray = len; path.animate([{ strokeDashoffset: len }, { strokeDashoffset: 0 }], { duration: 1100, easing: "ease-out", fill: "backwards" }); }
        pts.forEach(([x, y, r]) => { const d = el("circle", { cx: x, cy: y, r: 3.5, fill: "#000", stroke: s.color, "stroke-width": 2, class: "dot" }, svg); hover(d, `Tier ${r.tier} · ${s.label}: <b>${fmt(r[s.key])}</b><br>${r.count} cards`); });
      });
    };
    draw();
    if (legendHost) {
      legendHost.innerHTML = "";
      series.forEach((s) => {
        const b = document.createElement("button"); b.type = "button";
        if (hidden.has(s.key)) b.classList.add("off");
        b.innerHTML = `<i style="background:${s.color}"></i>${s.label}`;
        b.addEventListener("click", () => { hidden.has(s.key) ? hidden.delete(s.key) : hidden.add(s.key); b.classList.toggle("off"); draw(); });
        legendHost.appendChild(b);
      });
    }
  }

  function histogram(host, values, buckets = 12) {
    if (!host || !values.length) { if (host) host.innerHTML = "<p class='muted'>No data</p>"; return; }
    const sorted = values.slice().sort((a, b) => a - b);
    const lo = sorted[0], hi = sorted[Math.floor(sorted.length * 0.99)] || sorted[sorted.length - 1];
    const w = Math.max(1, (hi - lo) / buckets);
    const counts = new Array(buckets).fill(0);
    values.forEach((v) => { counts[Math.min(buckets - 1, Math.max(0, Math.floor((v - lo) / w)))]++; });
    bars(host, counts.map((c, i) => [`${fmt(lo + i * w)}`, c]), {
      colors: counts.map((_, i) => `hsl(${200 - (i * 10) / buckets * 2} ${70 + i * 2}% ${78 - (i * 40) / buckets}%)`),
      valueTip: (l, v) => `Power ≈ ${l}–${fmt(Number(String(l).replace(/[K,]/g, "")) + w)}: <b>${v}</b> cards`,
    });
  }

  function heat(host, affinity) {
    if (!host) return;
    const kinds = [["WEAKNESS", "Weak"], ["RESISTANT", "Resist"], ["IMMUNE", "Immune"], ["REPEL", "Repel"], ["ABSORB", "Absorb"]];
    const els = Object.keys(affinity);
    const max = Math.max(1, ...els.flatMap((e) => kinds.map(([k]) => affinity[e][k])));
    host.style.gridTemplateColumns = `110px repeat(${els.length}, minmax(30px, 1fr))`;
    host.style.minWidth = `${110 + els.length * 32}px`;
    host.innerHTML = "<div></div>" + els.map((e) => `<div class="lab" style="justify-content:center" title="${title(e)}">${style(e).emoji}</div>`).join("");
    const tints = { WEAKNESS: "255,101,104", RESISTANT: "119,212,255", IMMUNE: "74,222,128", REPEL: "253,230,138", ABSORB: "196,181,253" };
    kinds.forEach(([k, label]) => {
      const lab = document.createElement("div"); lab.className = "lab"; lab.textContent = label; host.appendChild(lab);
      els.forEach((e) => {
        const v = affinity[e][k];
        const cell = document.createElement("div");
        cell.className = "cell";
        cell.style.background = `rgba(${tints[k]},${0.08 + (v / max) * 0.92})`;
        cell.style.color = v / max > 0.55 ? "#000" : "#fff";
        cell.textContent = v || "";
        hover(cell, `${style(e).emoji} ${title(e)} · ${label}: <b>${v}</b> cards`);
        host.appendChild(cell);
      });
    });
  }

  const cardsHref = (params) => `${P.cardsUrl}?${new URLSearchParams(Object.assign(P.universe ? { universe: P.universe } : {}, params))}`;
  const classEmoji = (k) => (P.classEmoji || {})[k] || "";

  /* ---------------------------------------------------------------- home */
  if (P.mini) {
    const m = P.mini;
    bars(document.getElementById("mini-tier"), m.by_tier.map(([t, c]) => [`★${t}`, c, null, `${P.cardsUrl}?tier=${t}`]), { height: 200 });
    donut(document.getElementById("mini-type"), m.by_type, { colorFn: (k) => style(k).glow, emoji: (k) => style(k).emoji, href: (k) => `${P.cardsUrl}?type=${k}` });
    hbars(document.getElementById("mini-uni"), m.by_universe.slice(0, 10), { href: (u) => `${P.cardsUrl}?universe=${encodeURIComponent(u)}` });
  }

  /* ---------------------------------------------------------------- stats */
  if (P.cards) {
    const c = P.cards, g = P.gear;
    const classes = [...new Set(c.scatter.map((p) => p.c))].sort();
    scatter(document.getElementById("c-scatter"), c.scatter.map((p) => ({
      x: p.a, y: p.d, r: p.h, group: p.c, label: p.n,
      sub: `${p.u} · ${title(p.c)} · Tier ${p.t} · HP ${fmt(p.h)} · ATK ${fmt(p.a)} · DEF ${fmt(p.d)}`,
      href: `${P.cardsUrl}/${p.id}`,
    })), { xLabel: "ATK →", yLabel: "↑ DEF", groups: classes, groupColor: (k) => CLASS_COLORS[k] || "#c4b8f2", legendHost: document.getElementById("c-scatter-legend") });
    lines(document.getElementById("c-tierline"), c.tiers, [
      { key: "hp", label: "HP", color: "#4ade80", hidden: true }, { key: "atk", label: "ATK", color: "#ff8a65" },
      { key: "def", label: "DEF", color: "#77d4ff" }, { key: "ult", label: "Ultimate", color: "#fafafa" },
    ], document.getElementById("c-tierline-legend"));
    bars(document.getElementById("c-tier"), c.by_tier.map(([t, n]) => [`★${t}`, n, null, cardsHref({ tier: t })]));
    donut(document.getElementById("c-type"), c.by_type, { colorFn: (k) => style(k).glow, emoji: (k) => style(k).emoji, href: (k) => cardsHref({ type: k }) });
    hbars(document.getElementById("c-class"), c.by_class, { colors: c.by_class.map(([k]) => CLASS_COLORS[k] || "#c4b8f2"), emoji: classEmoji, href: (k) => cardsHref({ cls: k }) });
    histogram(document.getElementById("c-ult"), c.ultimates);
    donut(document.getElementById("c-drop"), c.by_drop);
    heat(document.getElementById("c-heat"), c.affinity);
    hbars(document.getElementById("c-uni"), c.by_universe, { max: 30, href: (u) => `${P.cardsUrl}?universe=${encodeURIComponent(u)}` });
    hbars(document.getElementById("c-titles"), g.title_abilities);
    hbars(document.getElementById("c-arms"), g.arm_types, { emoji: (k) => (B.arm_emoji || {})[k] || "" });
    donut(document.getElementById("c-armel"), g.arm_elements, { colorFn: (k) => style(k).glow, emoji: (k) => style(k).emoji });
    hbars(document.getElementById("c-summons"), g.summon_types, { colors: g.summon_types.map(([k]) => style(k).glow), emoji: (k) => style(k).emoji });
  }
})();
