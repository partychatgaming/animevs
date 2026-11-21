/* Anime VS+ in the browser: renders the bot's messages, sends clicks back,
   and adds the effects (hit shake, damage numbers, victory/defeat). */
(function () {
  "use strict";
  const AVS = window.AVS || {};
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const toast = (m, k) => (window.AVSToast ? window.AVSToast(m, k) : console.log(m));
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const store = { get: (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } },
                  set: (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) { /* private mode */ } } };

  const state = { player: null, session: null, version: -1, lastEvent: 0, clickable: new Set(), polling: false,
                  messages: new Map(), waitingClick: false, record: { win: 0, loss: 0 } };

  async function api(method, url, body) {
    const res = await fetch(url, { method, headers: { "Content-Type": "application/json", "X-CSRF": AVS.csrf }, body: body ? JSON.stringify(body) : undefined });
    let data = {};
    try { data = await res.json(); } catch (e) { /* empty */ }
    if (!res.ok || data.ok === false) { const err = new Error(data.error || `${res.status} ${res.statusText}`); err.status = res.status; throw err; }
    return data;
  }

  /* ================================================================ markdown (Discord flavour) */
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  function inline(t) {
    const codes = [];
    t = t.replace(/`([^`]+)`/g, (_, c) => { codes.push(c); return `\u0000${codes.length - 1}\u0000`; });
    t = t.replace(/&lt;(a?):(\w+):(\d+)&gt;/g, (_, a, n, id) => `<img class="emo" alt=":${n}:" src="https://cdn.discordapp.com/emojis/${id}.${a ? "gif" : "png"}">`);
    t = t.replace(/&lt;@!?(\d+)&gt;/g, (_, id) => `<span class="mention">@${esc(state.player && state.player.did === id ? state.player.name : "player")}</span>`);
    t = t.replace(/&lt;#(\d+)&gt;/g, '<span class="mention">#channel</span>');
    t = t.replace(/&lt;t:(\d+)(?::(\w))?&gt;/g, (_, ts, f) => { const d = new Date(Number(ts) * 1000); return `<span class="mention">${f === "R" ? rel(d) : d.toLocaleString()}</span>`; });
    t = t.replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    t = t.replace(/\*\*\*(.+?)\*\*\*/g, "<b><i>$1</i></b>").replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/__(.+?)__/g, "<u>$1</u>")
         .replace(/(^|[^*\w])\*(?!\s)(.+?)\*(?!\w)/g, "$1<i>$2</i>").replace(/(^|[^_\w])_(?!\s)(.+?)_(?!\w)/g, "$1<i>$2</i>")
         .replace(/~~(.+?)~~/g, "<s>$1</s>").replace(/\|\|(.+?)\|\|/g, '<span class="spoiler" tabindex="0">$1</span>');
    t = t.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${codes[i]}</code>`);
    return t;
  }
  function rel(d) {
    const s = Math.round((d - Date.now()) / 1000), a = Math.abs(s);
    const u = a < 60 ? [a, "second"] : a < 3600 ? [Math.round(a / 60), "minute"] : a < 86400 ? [Math.round(a / 3600), "hour"] : [Math.round(a / 86400), "day"];
    const txt = `${u[0]} ${u[1]}${u[0] === 1 ? "" : "s"}`;
    return s >= 0 ? `in ${txt}` : `${txt} ago`;
  }
  function md(src) {
    if (!src) return "";
    let text = esc(src);
    const blocks = [];
    text = text.replace(/```(?:\w+\n)?([\s\S]*?)```/g, (_, c) => { blocks.push(c); return `\u0001${blocks.length - 1}\u0001`; });
    const out = [];
    let list = null;
    for (const raw of text.split("\n")) {
      let line = raw, html;
      const m = line.match(/^(#{1,3}) (.*)$/);
      if (/^\s*[-*] /.test(line) && !/^-# /.test(line)) {
        if (!list) { list = []; }
        list.push(`<li>${inline(line.replace(/^\s*[-*] /, ""))}</li>`);
        continue;
      }
      if (list) { out.push(`<ul>${list.join("")}</ul>`); list = null; }
      if (m) html = `<div class="h${m[1].length}">${inline(m[2])}</div>`;
      else if (/^-# /.test(line)) html = `<div class="sub">${inline(line.slice(3))}</div>`;
      else if (/^&gt; /.test(line)) html = `<div class="quote">${inline(line.slice(5))}</div>`;
      else if (!line.trim()) html = '<div class="gap"></div>';
      else html = `<div>${inline(line)}</div>`;
      out.push(html);
    }
    if (list) out.push(`<ul>${list.join("")}</ul>`);
    return out.join("").replace(/\u0001(\d+)\u0001/g, (_, i) => `<pre>${blocks[i]}</pre>`);
  }

  /* ================================================================ rendering */
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  function emojiNode(e) {
    if (!e) return null;
    if (e.url) { const i = el("img", "emo"); i.src = e.url; i.alt = e.name || ""; return i; }
    return el("span", "emo-t", esc(e.name));
  }
  const STYLE = { 1: "primary", 2: "secondary", 3: "success", 4: "danger", 5: "link", 6: "primary" };

  function renderButton(b, msgId) {
    if (b.style === 5 && b.url) {
      const a = el("a", "dbtn link"); a.href = b.url; a.target = "_blank"; a.rel = "noopener";
      const em = emojiNode(b.emoji); if (em) a.append(em);
      if (b.label) a.append(document.createTextNode(b.label));
      return a;
    }
    const btn = el("button", `dbtn ${STYLE[b.style] || "secondary"}`);
    btn.type = "button";
    btn.dataset.id = b.id || "";
    btn.dataset.msg = msgId;
    const em = emojiNode(b.emoji); if (em) btn.append(em);
    if (b.label) btn.append(el("span", "lbl", esc(b.label)));
    btn.disabled = !!b.disabled;
    if (b.disabled) btn.dataset.gamedisabled = "1";
    return btn;
  }
  function renderSelect(s, msgId) {
    const wrap = el("label", "dselect");
    const sel = el("select");
    sel.dataset.id = s.id; sel.dataset.msg = msgId; sel.disabled = !!s.disabled;
    if (s.disabled) sel.dataset.gamedisabled = "1";
    sel.append(new Option(s.placeholder || "Choose…", "", true, true));
    sel.options[0].disabled = true;
    s.options.forEach((o) => { const op = new Option(`${o.emoji && !o.emoji.url ? o.emoji.name + " " : ""}${o.label}${o.description ? " — " + o.description : ""}`, o.value); sel.append(op); });
    wrap.append(sel);
    return wrap;
  }
  function renderComponent(c, msgId) {
    switch (c.t) {
      case "container": {
        const box = el("div", "dcontainer");
        if (c.accent) box.style.setProperty("--accent", c.accent);
        c.items.forEach((k) => box.append(renderComponent(k, msgId)));
        return box;
      }
      case "text": return el("div", "dtext", md(c.md));
      case "gallery": {
        const g = el("div", `dgallery n${Math.min(c.items.length, 4)}`);
        c.items.forEach((it) => { if (!it.url) return; const img = el("img", "dimg"); img.src = it.url; img.alt = it.desc || ""; img.loading = "eager"; g.append(img); });
        return g;
      }
      case "thumb": { const img = el("img", "dthumb"); img.src = c.url || ""; return img; }
      case "sep": return el("hr", c.divider ? "dsep" : "dsep space");
      case "section": {
        const s = el("div", "dsection");
        const body = el("div", "dsection-body");
        c.items.forEach((k) => body.append(renderComponent(k, msgId)));
        s.append(body);
        if (c.accessory) s.append(renderComponent(c.accessory, msgId));
        return s;
      }
      case "row": {
        const r = el("div", "drow");
        c.items.forEach((k) => r.append(renderComponent(k, msgId)));
        return r;
      }
      case "button": return renderButton(c, msgId);
      case "select": return renderSelect(c, msgId);
      default: return el("div", "dtext", md(c.md || ""));
    }
  }
  function renderEmbed(e) {
    const box = el("div", "dembed");
    if (e.color) box.style.setProperty("--accent", e.color);
    const main = el("div", "dembed-main");
    if (e.author && e.author.name) {
      const a = el("div", "dembed-author");
      if (e.author.icon) { const i = el("img"); i.src = e.author.icon; a.append(i); }
      a.append(el("span", null, inline(esc(e.author.name))));
      main.append(a);
    }
    if (e.title) main.append(el("div", "dembed-title", md(e.title)));
    if (e.description) main.append(el("div", "dtext", md(e.description)));
    if (e.fields && e.fields.length) {
      const f = el("div", "dfields");
      e.fields.forEach((x) => { const d = el("div", `dfield${x.inline ? " inline" : ""}`); d.append(el("div", "dfield-name", md(x.name)), el("div", "dtext", md(x.value))); f.append(d); });
      main.append(f);
    }
    if (e.image) { const i = el("img", "dimg"); i.src = e.image; main.append(i); }
    if (e.footer && e.footer.text) main.append(el("div", "dembed-footer", inline(esc(e.footer.text))));
    box.append(main);
    if (e.thumbnail) { const t = el("img", "dembed-thumb"); t.src = e.thumbnail; box.append(t); }
    return box;
  }
  function renderMessage(m) {
    const node = el("article", "dmsg");
    node.dataset.id = m.id;
    if (m.content) node.append(el("div", "dtext dcontent", md(m.content)));
    (m.embeds || []).forEach((e) => node.append(renderEmbed(e)));
    (m.components || []).forEach((c) => node.append(renderComponent(c, m.id)));
    (m.files || []).forEach((u) => { const i = el("img", "dimg"); i.src = u; node.append(i); });
    return node;
  }

  /* ---------------------------------------------------------------- effects */
  const fx = $("#fx"), stage = $("#stage");
  function shake(strength = 1) {
    if (reduce) return;
    stage.classList.remove("shake", "shake-big");
    void stage.offsetWidth;
    stage.classList.add(strength > 1 ? "shake-big" : "shake");
  }
  function floatNumber(text, kind, anchor) {
    const n = el("div", `float-num ${kind}`, esc(text));
    const r = (anchor || stage).getBoundingClientRect(), s = stage.getBoundingClientRect();
    n.style.left = `${r.left - s.left + r.width * (0.35 + Math.random() * 0.3)}px`;
    n.style.top = `${r.top - s.top + r.height * 0.35}px`;
    fx.append(n);
    setTimeout(() => n.remove(), 1600);
  }
  function flash(color) {
    if (reduce) return;
    const f = el("div", "flash-fx"); f.style.background = color; fx.append(f); setTimeout(() => f.remove(), 450);
  }
  function analyseTurn(node, json, prev) {
    // A battle message: container with a gallery (the scene) and a log text after it.
    const texts = [];
    const walk = (c) => { if (!c) return; if (c.t === "text") texts.push(c.md); (c.items || []).forEach(walk); };
    (json.components || []).forEach(walk);
    const prevTexts = [];
    if (prev) (prev.components || []).forEach(function w(c) { if (!c) return; if (c.t === "text") prevTexts.push(c.md); (c.items || []).forEach(w); });
    const fresh = texts.join("\n").split("\n").filter((l) => l.trim() && !prevTexts.join("\n").includes(l));
    const scene = node.querySelector(".dgallery img");
    const img = scene && scene.getBoundingClientRect().height > 60 ? scene : node;
    let hits = 0;
    fresh.slice(0, 4).forEach((line) => {
      const plain = line.replace(/[*_`~#>-]/g, "");
      const dmg = plain.match(/([\d,]{2,})\s*(?:damage|dmg)/i);
      const heal = plain.match(/(?:heal(?:ed|s)?|recover(?:ed|s)?|restor(?:ed|es))[^\d]*([\d,]{2,})/i) || plain.match(/([\d,]{2,})\s*(?:hp|health)\b/i);
      if (dmg) {
        const crit = /critical|crit\b|💥|ultimate/i.test(plain);
        floatNumber(`-${dmg[1]}${crit ? "!" : ""}`, crit ? "crit" : "dmg", img);
        hits = Math.max(hits, crit ? 2 : 1);
      } else if (heal) {
        floatNumber(`+${heal[1]}`, "heal", img);
      }
      if (/resolve/i.test(plain)) flash("radial-gradient(circle, rgba(255,230,120,.55), transparent 70%)");
      if (/focus/i.test(plain) && !dmg) flash("radial-gradient(circle, rgba(119,212,255,.4), transparent 70%)");
    });
    if (hits) { shake(hits); flash(hits > 1 ? "rgba(255,255,255,.35)" : "rgba(255,101,104,.18)"); }
  }

  // confetti / embers on a canvas
  const canvas = $("#fx-canvas");
  const ctx2d = canvas.getContext("2d");
  let parts = [], raf = 0;
  function burst(kind) {
    if (reduce) return;
    const r = stage.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = r.width * dpr; canvas.height = r.height * dpr;
    ctx2d.setTransform(dpr, 0, 0, dpr, 0, 0);
    const colors = kind === "win" ? ["#fafafa", "#77d4ff", "#fde68a", "#4ade80", "#c4b5fd"] : ["#ff6568", "#7f1d1d", "#262626"];
    for (let i = 0; i < (kind === "win" ? 180 : 70); i++) {
      parts.push({ x: r.width / 2 + (Math.random() - 0.5) * 120, y: r.height * 0.42, vx: (Math.random() - 0.5) * (kind === "win" ? 14 : 6),
                   vy: kind === "win" ? -Math.random() * 13 - 4 : Math.random() * 2, g: kind === "win" ? 0.32 : 0.05, s: 3 + Math.random() * 5,
                   c: colors[i % colors.length], rot: Math.random() * 6, vr: (Math.random() - 0.5) * 0.4, life: 1 });
    }
    if (!raf) tick();
  }
  function tick() {
    const r = stage.getBoundingClientRect();
    ctx2d.clearRect(0, 0, r.width, r.height);
    parts.forEach((p) => {
      p.vy += p.g; p.x += p.vx; p.y += p.vy; p.vx *= 0.99; p.rot += p.vr; p.life -= 0.006;
      ctx2d.save(); ctx2d.globalAlpha = Math.max(0, p.life); ctx2d.translate(p.x, p.y); ctx2d.rotate(p.rot);
      ctx2d.fillStyle = p.c; ctx2d.fillRect(-p.s / 2, -p.s / 4, p.s, p.s / 2); ctx2d.restore();
    });
    parts = parts.filter((p) => p.life > 0 && p.y < r.height + 40);
    raf = parts.length ? requestAnimationFrame(tick) : 0;
    if (!raf) ctx2d.clearRect(0, 0, r.width, r.height);
  }
  function banner(kind, detail) {
    const b = $("#banner-fx");
    const word = { win: "Victory", loss: "Defeat", timeout: "Timed out", error: "Something broke", end: "Match over" }[kind] || kind;
    const sub = detail && typeof detail === "object" ? `${detail.you || ""} vs ${detail.foe || ""}${detail.turns ? ` · ${detail.turns} turns` : ""}` : (detail || "");
    b.className = `banner-fx show ${kind}`;
    b.innerHTML = `<div class="word">${esc(word)}</div><div class="cap-sub">${esc(sub)}</div>`;
    clearTimeout(banner.t);
    banner.t = setTimeout(() => { b.className = "banner-fx"; }, kind === "error" ? 5000 : 2600);
  }

  /* ---------------------------------------------------------------- applying state */
  const feed = $("#feed");
  function apply(snap) {
    state.version = snap.version;
    state.clickable = new Set(snap.clickable || []);
    state.record = snap.record || state.record;
    $("#arena-record").textContent = `${state.record.win}W · ${state.record.loss}L`;
    const status = $("#arena-status");
    const yourMove = state.clickable.size > 0 || snap.waiting_text;
    status.className = `status-dot ${yourMove ? "you" : snap.busy ? "busy" : "idle"}`;
    status.title = yourMove ? "Your move" : snap.busy ? "The game is thinking…" : "Finished";
    $("#arena-sub").textContent = yourMove ? "Your move" : snap.busy ? "Working…" : "Done. Pick another mode from the lobby.";

    const seen = new Set();
    const normal = snap.messages.filter((m) => !m.ephemeral);
    const eph = snap.messages.filter((m) => m.ephemeral);
    let grew = false;
    normal.forEach((m) => {
      seen.add(String(m.id));
      const key = JSON.stringify(m);
      const old = state.messages.get(String(m.id));
      if (old && old.key === key) return;
      const node = renderMessage(m);
      if (old) {
        // keep the previous scene image visible until the new one has loaded, then punch in
        const newImg = node.querySelector(".dgallery img"), oldImg = old.node.querySelector(".dgallery img");
        if (newImg && oldImg && newImg.src !== oldImg.src) {
          newImg.classList.add("punch");
        }
        old.node.replaceWith(node);
        analyseTurn(node, m, old.json);
      } else {
        node.classList.add("enter");
        feed.append(node);
        grew = true;
        analyseTurn(node, m, null);
      }
      state.messages.set(String(m.id), { key, node, json: m });
    });
    for (const [id, item] of state.messages) {
      if (!seen.has(id) && !eph.some((m) => String(m.id) === id)) { item.node.classList.add("leave"); setTimeout(() => item.node.remove(), 250); state.messages.delete(id); }
    }
    // ephemeral panel (the "More" kit panel, confirmations…)
    const dlg = $("#ephemeral");
    const latestEph = eph[eph.length - 1];
    if (latestEph) {
      const body = $("#ephemeral-body");
      body.innerHTML = "";
      body.append(renderMessage(latestEph));
      if (!dlg.open) dlg.showModal();
    } else if (dlg.open) dlg.close();

    refreshButtons();
    // Only pop the reply bar open when typing is the one thing the game wants;
    // otherwise keep it behind the ⌨ button (some screens listen for chat in the background).
    const onlyText = snap.waiting_text && state.clickable.size === 0;
    $("#arena-type").hidden = !snap.waiting_text || onlyText;
    if (!snap.waiting_text) $("#typebar").hidden = true;
    else if (onlyText && $("#typebar").hidden) { $("#typebar").hidden = false; setTimeout(() => $("#type-input").focus(), 50); }

    (snap.events || []).forEach(([v, kind, detail]) => {
      if (v <= state.lastEvent) return;
      state.lastEvent = v;
      if (kind === "win") { banner("win", detail); burst("win"); }
      else if (kind === "loss") { banner("loss", detail); burst("loss"); shake(2); }
      else if (kind === "error") { banner("error", detail); }
      else if (kind === "timeout") { banner("timeout", "The game stopped waiting. Start again from the lobby."); }
    });
    if (grew) stage.scrollTo({ top: stage.scrollHeight, behavior: reduce ? "auto" : "smooth" });
  }
  function refreshButtons() {
    $$(".dbtn[data-id], .dselect select").forEach((b) => {
      const live = state.clickable.has(b.dataset.id) && !b.dataset.gamedisabled;
      b.disabled = !live || state.waitingClick;
      b.classList.toggle("dead", !live);
    });
  }

  /* ---------------------------------------------------------------- input */
  async function press(id, msg, values, btn) {
    if (!state.session || state.waitingClick) return;
    state.waitingClick = true;
    if (btn) { btn.classList.add("pressed"); }
    $$(".dbtn[data-id]").forEach((b) => (b.disabled = true));
    try {
      await api("POST", `/play/api/${state.session}/press`, { id, message: msg, values });
    } catch (err) {
      toast(err.message, "error");
    } finally {
      state.waitingClick = false;
      setTimeout(refreshButtons, 30);
    }
  }
  document.addEventListener("click", (e) => {
    const b = e.target.closest(".dbtn[data-id]");
    if (!b || b.disabled) return;
    ripple(b, e);
    press(b.dataset.id, b.dataset.msg, null, b);
  });
  document.addEventListener("change", (e) => {
    const s = e.target.closest(".dselect select");
    if (s && s.value) press(s.dataset.id, s.dataset.msg, [s.value], null);
  });
  function ripple(b, e) {
    if (reduce) return;
    const r = b.getBoundingClientRect(), d = el("span", "ripple");
    d.style.left = `${(e.clientX || r.left + r.width / 2) - r.left}px`;
    d.style.top = `${(e.clientY || r.top + r.height / 2) - r.top}px`;
    b.append(d); setTimeout(() => d.remove(), 600);
  }
  document.addEventListener("keydown", (e) => {
    // number keys 1–9 press the battle buttons in order, like a fighting game
    if (!state.session || $("#arena").hidden || e.target.closest("input, textarea, select") || e.metaKey || e.ctrlKey) return;
    if (/^[1-9]$/.test(e.key)) {
      const live = $$("#feed .dbtn[data-id]:not(:disabled)");
      const target = live[Number(e.key) - 1];
      if (target) { e.preventDefault(); target.click(); }
    }
  });
  $("#arena-type").addEventListener("click", () => { const t = $("#typebar"); t.hidden = !t.hidden; if (!t.hidden) $("#type-input").focus(); });
  $("#typebar").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = $("#type-input");
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    try { await api("POST", `/play/api/${state.session}/text`, { text }); } catch (err) { toast(err.message, "error"); }
  });

  /* ---------------------------------------------------------------- session lifecycle */
  async function poll() {
    if (state.polling) return;
    state.polling = true;
    let backoff = 500;
    while (state.session) {
      const sid = state.session;
      try {
        const res = await fetch(`/play/api/${sid}/state?v=${state.version}`);
        if (res.status === 404) { if (sid === state.session) { toast("That game has ended.", "error"); leave(false); } break; }
        const snap = await res.json();
        if (sid !== state.session) continue;
        apply(snap);
        backoff = 500;
      } catch (err) {
        await new Promise((r) => setTimeout(r, backoff));
        backoff = Math.min(backoff * 2, 8000);
      }
    }
    state.polling = false;
  }
  function enterArena(name, sub) {
    $("#lobby").hidden = true;
    $("#arena").hidden = false;
    $("#arena-name").textContent = name;
    $("#arena-sub").textContent = sub || "Starting…";
    feed.innerHTML = "";
    state.messages.clear();
    state.version = -1;
    state.lastEvent = 0;
    window.scrollTo({ top: 0 });
  }
  async function begin(command, args, label) {
    if (!state.player) { toast("Pick a player first.", "error"); $("#player-q").focus(); return; }
    enterArena(label, "Starting…");
    try {
      const data = await api("POST", "/play/api/start", { did: state.player.did, command, args });
      state.session = data.session;
      store.set("avs.play.session", data.session);
      store.set("avs.play.label", label);
      poll();
    } catch (err) {
      toast(err.message, "error");
      leave(false);
    }
  }
  async function leave(endIt = true) {
    const sid = state.session;
    state.session = null;
    store.set("avs.play.session", null);
    if (endIt && sid) { try { await api("POST", `/play/api/${sid}/end`); } catch (e) { /* already gone */ } }
    $("#arena").hidden = true;
    $("#lobby").hidden = false;
    if ($("#ephemeral").open) $("#ephemeral").close();
    if (state.player) loadPlayer(state.player.did);
  }
  $("#arena-leave").addEventListener("click", () => {
    if (state.clickable.size && !confirm("Leave this game? Any battle in progress stops here (like walking away in Discord).")) return;
    leave(true);
  });
  window.addEventListener("beforeunload", (e) => {
    if (state.session && state.clickable.size) { e.preventDefault(); e.returnValue = ""; }
  });

  /* ---------------------------------------------------------------- lobby */
  const results = $("#player-results");
  let searchTimer = 0;
  async function search(q) {
    const res = await fetch(`/play/api/players?q=${encodeURIComponent(q)}`);
    const list = await res.json();
    results.innerHTML = "";
    if (!list.length) { results.append(el("div", "muted pr-empty", "No players match.")); }
    list.forEach((p) => {
      const b = el("button", "pr-item");
      b.type = "button";
      b.innerHTML = `<span>${esc(p.name)}</span><span class="cap-sub">Lv ${esc(p.level)} · ${esc(p.card || "no card")}</span>`;
      b.addEventListener("click", () => { results.classList.remove("open"); $("#player-q").value = p.name; loadPlayer(p.did); });
      results.append(b);
    });
    results.classList.add("open");
  }
  $("#player-q").addEventListener("input", (e) => { clearTimeout(searchTimer); searchTimer = setTimeout(() => search(e.target.value.trim()), 180); });
  $("#player-q").addEventListener("focus", (e) => search(e.target.value.trim()));
  document.addEventListener("click", (e) => { if (!e.target.closest(".player-search")) results.classList.remove("open"); });

  async function loadPlayer(did) {
    const res = await fetch(`/play/api/player/${encodeURIComponent(did)}`);
    if (!res.ok) { store.set("avs.play.did", null); return; }
    const p = await res.json();
    state.player = p;
    store.set("avs.play.did", p.did);
    $("#player-q").placeholder = p.name;
    const card = $("#player-card");
    card.className = "player-card";
    card.style.setProperty("--glow", p.glow);
    const modes = p.modes.length
      ? p.modes.map((m) => `<div class="rec-row"><span>${esc(m.mode)}</span><span class="cap-sub">${m.clears}/${m.runs} cleared</span><i style="--w:${m.runs ? Math.round((m.clears / m.runs) * 100) : 0}%"></i></div>`).join("")
      : '<p class="muted" style="margin:0;font-size:13px">No battles recorded yet.</p>';
    card.innerHTML = `
      ${p.render ? `<div class="pc-art" data-tilt><img src="${esc(p.render)}" alt="${esc(p.card)}"></div>` : ""}
      <div class="pc-name">${esc(p.name)}</div>
      <div class="cap-sub">Lv ${esc(p.level)} · 🪙 ${esc(p.balance)} · ${esc(p.difficulty)}${p.prestige ? ` · Prestige ${esc(p.prestige)}` : ""}</div>
      ${p.available ? "" : '<div class="pill warn">In a battle elsewhere</div>'}
      <div class="chips" style="margin-top:12px">
        <span class="chip">🎴 ${esc(p.card || "—")}${p.card_level ? ` · Lv ${esc(p.card_level)}` : ""}</span>
        <span class="chip">🎗️ ${esc(p.title || "—")}</span><span class="chip">🦾 ${esc(p.arm || "—")}</span><span class="chip">🧬 ${esc(p.summon || "—")}</span>
      </div>
      <p class="section-label" style="margin-top:18px">Record</p>
      <div class="rec">${modes}</div>
      <div class="rec-totals cap-sub">PvP ${esc(p.pvp.wins)}W / ${esc(p.pvp.losses)}L · Bosses beaten ${esc(p.boss_wins)} · Tales done ${esc(p.tales_done)} · Dungeons done ${esc(p.dungeons_done)}</div>`;
  }

  $$(".mode-tile").forEach((t) => t.addEventListener("click", () => {
    const uni = t.dataset.uni === "1" ? $("#play-universe").value : "";
    const label = t.querySelector("strong").textContent + (uni ? ` · ${uni}` : "");
    if (t.dataset.command === "explore") begin("explore", uni ? { universe: uni } : {}, label);
    else begin("play", { mode: t.dataset.mode, universe: uni }, label);
  }));

  // tools that need an argument ask for it first
  let pendingTool = null;
  $$(".tool-chip").forEach((t) => t.addEventListener("click", () => {
    const args = JSON.parse(t.dataset.args || "[]");
    const label = t.textContent.trim();
    if (!args.length) return begin(t.dataset.command, {}, label);
    pendingTool = { command: t.dataset.command, label, args };
    $("#args-title").textContent = label;
    const body = $("#args-body"); body.innerHTML = "";
    args.forEach(([key, lab, kind]) => {
      const l = el("label", null, esc(lab));
      let input;
      if (kind.includes("|")) { input = el("select"); kind.split("|").forEach((o) => input.append(new Option(o, o))); }
      else { input = el("input"); input.type = kind === "number" ? "number" : "text"; if (kind === "number") { input.min = 1; input.max = 10; input.value = 1; } }
      input.name = key;
      l.append(input); body.append(l);
    });
    $("#args-dialog").showModal();
    setTimeout(() => body.querySelector("input, select")?.focus(), 50);
  }));
  $("#args-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const args = {};
    $$("#args-body [name]").forEach((i) => { if (i.value !== "") args[i.name] = i.value; });
    $("#args-dialog").close();
    if (pendingTool) begin(pendingTool.command, args, pendingTool.label);
  });

  /* ---------------------------------------------------------------- boot */
  (async () => {
    const did = store.get("avs.play.did");
    if (did) await loadPlayer(did);
    const sid = store.get("avs.play.session");
    if (sid) {
      const res = await fetch(`/play/api/${sid}/state?probe=1`).catch(() => null);
      // a quick probe: 404 means the game is gone
      if (res && res.ok) {
        enterArena(store.get("avs.play.label") || "Game", "Reconnected");
        state.session = sid;
        poll();
      } else store.set("avs.play.session", null);
    }
  })();
})();
