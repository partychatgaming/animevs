/* Anime VS+ dashboard: dialogs, quick edit, inline table edits, live card preview,
   ability builders. Plain JS, no build step. */
(function () {
  "use strict";
  const AVS = window.AVS || {};
  const B = AVS.builder || {};
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v === undefined || v === null || v === false) continue;
      if (k === "class") el.className = v;
      else if (k === "style") el.style.cssText = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else if (k === "checked" || k === "selected" || k === "value") el[k] = v;
      else el.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat()) if (kid !== null && kid !== undefined && kid !== false) el.append(kid.nodeType ? kid : document.createTextNode(kid));
    return el;
  };
  const style = (key) => (B.styles || {})[String(key || "").toUpperCase()] || { emoji: "✨", color: "#c48c28", glow: "#ffd678" };
  const title = (s) => String(s || "").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());

  /* ---------------------------------------------------------------- toasts */
  function toast(message, kind = "ok") {
    const box = $("#toasts");
    if (!box) return;
    const t = h("div", { class: `toast ${kind}` }, message);
    box.append(t);
    setTimeout(() => { t.style.transition = "opacity .3s"; t.style.opacity = "0"; }, 2600);
    setTimeout(() => t.remove(), 3000);
  }
  window.AVSToast = toast;

  async function api(method, url, body) {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json", "X-CSRF": AVS.csrf },
      body: body ? JSON.stringify(body) : undefined,
    });
    let data = {};
    try { data = await res.json(); } catch (e) { /* not json */ }
    if (!res.ok || data.ok === false) throw new Error((data.errors || [res.statusText || "Request failed"]).join(" "));
    return data;
  }

  /* ---------------------------------------------------------------- dialogs */
  document.addEventListener("click", (e) => {
    const opener = e.target.closest("[data-open]");
    if (opener) { const d = document.getElementById(opener.dataset.open); if (d) d.showModal(); }
    const closer = e.target.closest("[data-close]");
    if (closer) closer.closest("dialog")?.close();
  });
  $$("dialog").forEach((d) => d.addEventListener("click", (e) => { if (e.target === d && !d.classList.contains("viewer")) d.close(); }));

  // create dialog
  const createDialog = $("#create-dialog");
  function openCreate(kind, universe) {
    if (!createDialog) return;
    const kindSel = $("#create-kind");
    kindSel.value = kind || "cards";
    syncCreate();
    if (universe) { const u = $("select[name=universe]", createDialog); if ([...u.options].some((o) => o.value === universe)) u.value = universe; }
    createDialog.showModal();
    setTimeout(() => $("input[name=name]", createDialog).focus(), 60);
  }
  function syncCreate() {
    const kind = $("#create-kind").value;
    $("#create-form").action = `/new/${kind}`;
    $("#create-universe-wrap").style.display = kind === "universes" ? "none" : "";
  }
  if (createDialog) $("#create-kind").addEventListener("change", syncCreate);
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-create]");
    if (b) openCreate(b.dataset.create, b.dataset.universe);
  });

  // duplicate asks for a name
  $$("form[data-duplicate]").forEach((form) => form.addEventListener("submit", (e) => {
    const current = $("h1")?.textContent.trim() || "";
    const name = window.prompt("Name for the copy:", `${current} Copy`);
    if (name === null) { e.preventDefault(); return; }
    form.querySelector("input[name=name]").value = name;
  }));

  // filters
  $$("[data-autosubmit]").forEach((s) => s.addEventListener("change", () => s.form.submit()));
  const toggleFilters = $("[data-toggle-filters]");
  if (toggleFilters) toggleFilters.addEventListener("click", () => $("#toolbar").classList.toggle("expanded"));

  /* ---------------------------------------------------------------- holo tilt */
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  function bindTilt(el) {
    if (!finePointer || el.dataset.tiltBound) return;
    el.dataset.tiltBound = "1";
    const face = el.querySelector(".face") || el;
    el.addEventListener("pointermove", (e) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      el.style.transform = `rotateY(${(x - 0.5) * 16}deg) rotateX(${(0.5 - y) * 14}deg) translateZ(10px)`;
      face.style.setProperty("--sx", `${x * 100}%`);
      face.style.setProperty("--sy", `${y * 100}%`);
    });
    el.addEventListener("pointerleave", () => { el.style.transform = ""; });
  }
  $$("[data-tilt]").forEach(bindTilt);

  /* ---------------------------------------------------------------- ability builders */
  // kind: "title" | "arm" | "summon". read()/write() move JSON in and out of a textarea.
  function abilityBuilder(container, kind, textarea, onChange) {
    let items = [];
    const parse = () => {
      try {
        const v = JSON.parse(textarea.value || "[]");
        items = Array.isArray(v) ? v : [v];
        container.classList.remove("bad");
        return true;
      } catch (e) {
        container.innerHTML = "";
        container.append(h("p", { class: "flash error" }, "The raw JSON below has a typo, so the builder is paused. Fix it there."));
        return false;
      }
    };
    const write = () => {
      textarea.value = JSON.stringify(items, null, 2);
      textarea.dispatchEvent(new Event("input", { bubbles: true }));
      onChange && onChange(items);
    };
    const select = (opts, value, onchange, blank) => {
      const s = h("select", { onchange: (e) => onchange(e.target.value) });
      if (blank) s.append(h("option", { value: "" }, "—"));
      const all = opts.includes(value) || value === "" || value === undefined ? opts : [value, ...opts];
      all.forEach((o) => s.append(h("option", { value: o, selected: o === value }, `${(B.arm_emoji || {})[o] || (style(o).emoji !== "✨" ? style(o).emoji : "")} ${title(o)}`.trim())));
      return s;
    };
    const num = (value, onchange) => h("input", { type: "number", inputmode: "numeric", value: value ?? 0, oninput: (e) => onchange(Number(e.target.value || 0)) });
    const removeBtn = (i) => h("button", { type: "button", class: "small ghost rm", title: "Remove", "aria-label": "Remove ability", onclick: () => { items.splice(i, 1); write(); render(); } }, "✕");

    function nameKey(obj, skip) { return Object.keys(obj).find((k) => !skip.includes(k)); }

    function render() {
      container.innerHTML = "";
      items.forEach((item, i) => {
        if (typeof item !== "object" || item === null) return;
        let row;
        if (kind === "title") {
          row = h("div", { class: "ability-row" },
            h("label", {}, "Ability", select(B.title_abilities || [], item.ABILITY || "", (v) => { item.ABILITY = v; write(); })),
            h("label", {}, "Power", num(item.POWER, (v) => { item.POWER = v; write(); })),
            h("label", {}, "Element", select(B.elements || [], item.ELEMENT || "", (v) => { item.ELEMENT = v; write(); }, true)),
            h("label", {}, "Turns", num(item.DURATION, (v) => { item.DURATION = v; write(); })),
            removeBtn(i));
        } else if (kind === "arm") {
          const key = Object.keys(item)[0] || "BASIC";
          row = h("div", { class: "ability-row arm" },
            h("label", {}, "Ability", select(B.arm_types || [], key, (v) => { const val = item[key]; delete item[key]; item[v] = val; write(); render(); })),
            h("label", {}, "Value", num(item[key], (v) => { item[key] = v; write(); })),
            removeBtn(i));
        } else {
          const key = nameKey(item, ["TYPE"]) || "Move";
          row = h("div", { class: "ability-row summon" },
            h("label", {}, "Move name", h("input", { value: key, onchange: (e) => {
              const nv = e.target.value.trim() || key; const val = item[key]; const type = item.TYPE;
              const rebuilt = { [nv]: val, TYPE: type }; Object.keys(item).forEach((k) => delete item[k]); Object.assign(item, rebuilt); write(); render();
            } })),
            h("label", {}, "Power", num(item[key], (v) => { item[key] = v; write(); })),
            h("label", {}, "Type", select(B.summon_types || [], item.TYPE || "", (v) => { item.TYPE = v; write(); })),
            removeBtn(i));
        }
        container.append(row);
      });
      if (!items.length) container.append(h("p", { class: "hint", style: "margin:0" }, "No abilities yet."));
    }
    function add() {
      if (!parse()) return;
      if (kind === "title") items.push({ ABILITY: "ATK", POWER: 10, ELEMENT: "", DURATION: 0 });
      else if (kind === "arm") items.push({ BASIC: 20 });
      else items.push({ "New Move": 20, TYPE: "PHYSICAL" });
      write(); render();
    }
    textarea.addEventListener("change", () => { if (parse()) { render(); onChange && onChange(items); } });
    if (parse()) render();
    return { add, items: () => items };
  }

  function abilityPreview(kind, items) {
    const box = $("#ability-preview");
    if (!box) return;
    box.innerHTML = "";
    (items || []).slice(0, 3).forEach((a) => {
      if (typeof a !== "object" || !a) return;
      let emoji = "✨", text = "";
      if (kind === "title") { text = `${a.ABILITY || ""} ${a.POWER ?? ""}${a.ELEMENT ? " · " + title(a.ELEMENT) : ""}${a.DURATION ? ` · ${a.DURATION} turns` : ""}`; }
      else if (kind === "arm") { const k = Object.keys(a)[0]; emoji = (B.arm_emoji || {})[k] || style(k).emoji; text = `${k} ${a[k]}`; }
      else { const k = Object.keys(a).find((x) => x !== "TYPE"); emoji = style(a.TYPE).emoji; text = `${k} ${a[k]} · ${a.TYPE || ""}`; }
      box.append(h("div", { class: "ability" }, h("span", {}, emoji), h("span", {}, text)));
    });
  }

  /* ---------------------------------------------------------------- editor page */
  const editor = $("#editor-form");
  if (editor) {
    const kindByBuilder = { title: "title", arm: "arm", summon: "summon" };
    // range <-> number
    $$("input[data-sync]", editor).forEach((range) => {
      const number = editor.querySelector(`input[type=number][name="${range.dataset.sync}"]`);
      const paint = () => {
        const p = ((range.value - range.min) / (range.max - range.min)) * 100;
        range.style.setProperty("--p", `${Math.max(0, Math.min(100, p))}%`);
      };
      range.addEventListener("input", () => { number.value = range.value; paint(); number.dispatchEvent(new Event("input", { bubbles: true })); });
      number.addEventListener("input", () => { if (Number(number.value) > Number(range.max)) range.max = number.value; range.value = number.value; paint(); });
      paint();
    });
    // moves: emoji + colour follow the element
    $$("[data-move]", editor).forEach((card) => {
      const sel = $("[data-move-value]", card);
      const tag = $("select[name^=m_tag_]", card);
      const paint = () => {
        const st = style(sel.value);
        card.style.setProperty("--ec", st.glow);
        $("[data-move-emoji]", card).textContent = tag.value === "TYPE" ? "🦠" : st.emoji;
      };
      sel.addEventListener("change", paint);
      tag.addEventListener("change", paint);
    });
    // ability builders
    $$("[data-builder]", editor).forEach((box) => {
      const ta = $(`#raw-${box.dataset.target}`);
      const kind = kindByBuilder[box.dataset.builder];
      const b = abilityBuilder(box, kind, ta, (items) => abilityPreview(kind, items));
      const add = $(`[data-add-ability="${box.dataset.target}"]`, editor);
      if (add) add.addEventListener("click", b.add);
    });

    // dirty tracking
    const savebar = $("#savebar");
    let dirty = false, submitting = false;
    const markDirty = () => { dirty = true; savebar && savebar.classList.add("is-dirty"); };
    editor.addEventListener("input", markDirty);
    editor.addEventListener("change", markDirty);
    editor.addEventListener("submit", () => { submitting = true; });
    window.addEventListener("beforeunload", (e) => { if (dirty && !submitting) { e.preventDefault(); e.returnValue = ""; } });
    document.addEventListener("keydown", (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") { e.preventDefault(); editor.requestSubmit(); }
    });

    // live Discord preview for cards
    const previewUrl = editor.dataset.preview;
    const img = $("#preview-img");
    if (previewUrl && img) {
      let timer = null, seq = 0, lastUrl = null;
      const holder = $("#preview-card");
      const refresh = async () => {
        const mine = ++seq;
        holder.classList.add("loading");
        try {
          const res = await fetch(previewUrl, { method: "POST", body: new FormData(editor), headers: { "X-CSRF": AVS.csrf } });
          if (!res.ok) throw new Error(await res.text());
          const blob = await res.blob();
          if (mine !== seq) return;
          const url = URL.createObjectURL(blob);
          img.src = url;
          $("#preview-open") && ($("#preview-open").href = url);
          if (lastUrl) setTimeout(((u) => () => URL.revokeObjectURL(u))(lastUrl), 4000);
          lastUrl = url;
        } catch (err) {
          if (mine === seq) toast("Preview failed: " + String(err.message || err).slice(0, 140), "error");
        } finally {
          if (mine === seq) holder.classList.remove("loading");
        }
      };
      const schedule = (e) => {
        if (e && e.target && e.target.name === "host_art") return;
        clearTimeout(timer);
        timer = setTimeout(refresh, 550);
      };
      editor.addEventListener("input", schedule);
      editor.addEventListener("change", schedule);
    }
  }

  /* ---------------------------------------------------------------- quick edit sheet */
  const quick = $("#quick-dialog");
  let quickTarget = null;
  function quickField(f) {
    const wrap = h("div", { class: "field" + (f.type === "json" ? " wide" : "") });
    if (f.type === "bool") {
      wrap.append(h("label", { class: "toggle" }, h("input", { type: "checkbox", name: f.key, checked: !!f.value }), h("span", { class: "sw" }), f.label));
      return wrap;
    }
    wrap.append(h("span", { class: "field-name" }, f.label));
    if (f.type === "select") {
      const s = h("select", { name: f.key });
      (f.choices || []).forEach((c) => s.append(h("option", { value: c, selected: String(c) === String(f.value) }, c === "" ? "—" : c)));
      wrap.append(s);
    } else if (f.type === "json" && f.builder) {
      const ta = h("textarea", { name: f.key, rows: 4, style: "display:none" });
      ta.value = f.value;
      const box = h("div", { class: "ability-builder" });
      const kind = { title: "title", arm: "arm", summon: "summon" }[f.builder];
      const b = abilityBuilder(box, kind, ta);
      wrap.append(box, h("button", { type: "button", class: "small lime", style: "justify-self:start", onclick: b.add }, "+ Add ability"), ta);
    } else if (f.type === "json" || f.type === "list") {
      const ta = h("textarea", { name: f.key, rows: 5 }); ta.value = f.value; wrap.append(ta);
    } else {
      const isNum = f.type === "int" || f.type === "float";
      const input = h("input", { name: f.key, type: isNum ? "number" : "text", step: f.type === "float" ? "any" : null, inputmode: isNum ? "decimal" : null, value: f.value ?? "" });
      if (isNum && f.max !== undefined) {
        const range = h("input", { type: "range", min: f.min, max: Math.max(f.max, Number(f.value) || 0), step: f.step || 1, value: f.value || 0,
          style: `--c:${f.key === "HLT" ? "var(--hp)" : f.key.includes("ATK") ? "var(--atk)" : f.key.includes("DEF") ? "var(--def)" : "#fafafa"}` });
        const paint = () => range.style.setProperty("--p", `${((range.value - range.min) / (range.max - range.min)) * 100}%`);
        range.addEventListener("input", () => { input.value = range.value; paint(); });
        input.addEventListener("input", () => { range.value = input.value; paint(); });
        paint();
        wrap.append(h("div", { class: "num-wrap" }, range, input));
      } else wrap.append(input);
    }
    return wrap;
  }

  async function openQuick(path) {
    if (!quick) { location.href = "/" + path; return; }
    quickTarget = path;
    $("#quick-body").innerHTML = "<p class='muted'>Loading…</p>";
    $("#quick-title").textContent = "Quick edit";
    quick.showModal();
    try {
      const res = await fetch(`/api/${path}`);
      const data = await res.json();
      $("#quick-title").textContent = data.tile.name;
      $("#quick-full").href = data.tile.edit;
      const body = $("#quick-body");
      body.innerHTML = "";
      const grid = h("div", { class: "fields" });
      data.fields.forEach((f) => { if (f.builder === undefined && f.key === "ABILITIES") f.builder = data.builder ? data.builder.replace(/s$/, "") : null; grid.append(quickField(f)); });
      body.append(grid);
    } catch (err) {
      $("#quick-body").innerHTML = "";
      $("#quick-body").append(h("p", { class: "flash error" }, "Couldn't load this record."));
    }
  }

  function collectQuick(form) {
    const out = {};
    $$("input[name], select[name], textarea[name]", form).forEach((el) => {
      if (el.type === "checkbox") out[el.name] = el.checked;
      else if (el.tagName === "TEXTAREA") {
        try { out[el.name] = JSON.parse(el.value); } catch (e) { out[el.name] = el.value; }
      } else out[el.name] = el.value;
    });
    return out;
  }

  function refreshTile(tile) {
    const card = document.querySelector(`.tile[data-id="${tile.id}"]`);
    if (card) {
      const img = card.querySelector(".face img");
      if (img && tile.render) img.src = tile.render;
      card.classList.toggle("off", !tile.available);
      card.style.setProperty("--glow", tile.type.glow);
      const small = card.querySelector(".meta small");
      if (small) small.textContent = `${tile.chips[1]} · ${tile.chips[2]}`;
      const spin = card.querySelector("[data-spin]");
      if (spin) { spin.dataset.spin = tile.render_full; spin.dataset.glow = tile.type.glow; }
      card.animate([{ transform: "scale(1.06) rotate(-1deg)" }, { transform: "none" }], { duration: 380, easing: "cubic-bezier(.3,1.6,.5,1)" });
    }
    const item = document.querySelector(`.item[data-id="${tile.id}"]`);
    if (item) {
      item.classList.toggle("off", !tile.available);
      item.style.setProperty("--c", tile.type.color);
      item.style.setProperty("--g", tile.type.glow);
      const body = item.querySelector(".body");
      $$(".ability", body).forEach((a) => a.remove());
      const anchor = body.querySelector(".uni") || body.querySelector(".name");
      tile.abilities.slice().reverse().forEach(([emoji, text]) => anchor.after(h("div", { class: "ability" }, h("span", {}, emoji), h("span", {}, text))));
      const chips = body.querySelectorAll(".chips");
      const last = chips[chips.length - 1];
      if (last) { last.innerHTML = ""; tile.chips.forEach((c) => last.append(h("span", { class: "chip" }, c))); }
      const banner = item.querySelector(".banner"), pill = banner && banner.querySelector(".pill");
      if (banner && !tile.available && !pill) banner.append(h("span", { class: "pill" }, "Hidden"));
      if (pill && tile.available) pill.remove();
      item.animate([{ transform: "scale(1.04)" }, { transform: "none" }], { duration: 320 });
    }
    const row = document.querySelector(`tr[data-id="${tile.id}"]`);
    if (row) row.classList.toggle("off", !tile.available);
  }

  if (quick) {
    $("#quick-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = e.submitter || $("#quick-form button[type=submit]");
      btn.disabled = true;
      try {
        const data = await api("PATCH", `/api/${quickTarget}`, collectQuick($("#quick-body")));
        refreshTile(data.tile);
        quick.close();
        toast(`Saved ${data.tile.name}`);
      } catch (err) {
        toast(err.message, "error");
      } finally { btn.disabled = false; }
    });
  }
  document.addEventListener("click", (e) => {
    const q = e.target.closest("[data-quick]");
    if (q) { e.preventDefault(); openQuick(q.dataset.quick); }
  });

  /* ---------------------------------------------------------------- table inline edits */
  const table = $("table.grid[data-catalog]");
  if (table) {
    const catalog = table.dataset.catalog;
    const save = async (row, payload, cell) => {
      try {
        const data = await api("PATCH", `/api/${catalog}/${row.dataset.id}`, payload);
        if (cell) { cell.classList.remove("saved"); void cell.offsetWidth; cell.classList.add("saved"); }
        row.classList.toggle("off", !data.tile.available);
        toast(`Saved ${data.tile.name}`);
      } catch (err) { toast(err.message, "error"); }
    };
    table.addEventListener("focusin", (e) => { const c = e.target.closest("td[contenteditable]"); if (c) c.dataset.before = c.textContent.trim(); });
    table.addEventListener("keydown", (e) => {
      const c = e.target.closest("td[contenteditable]");
      if (!c) return;
      if (e.key === "Enter") { e.preventDefault(); c.blur(); }
      if (e.key === "Escape") { c.textContent = c.dataset.before; c.blur(); }
    });
    table.addEventListener("focusout", (e) => {
      const c = e.target.closest("td[contenteditable]");
      if (!c) return;
      const v = c.textContent.trim().replace(/,/g, "");
      if (v === (c.dataset.before || "").replace(/,/g, "")) return;
      save(c.closest("tr"), { [c.dataset.key]: v }, c);
    });
    table.addEventListener("change", (e) => {
      const t = e.target.closest("input[data-avail]");
      if (t) save(t.closest("tr"), { AVAILABLE: t.checked });
    });
  }

  /* ---------------------------------------------------------------- tale / dungeon order */
  $$("[data-roster]").forEach((root) => {
    const list = $(".roster-list", root);
    const empty = $(".roster-empty", root);
    const search = $("input[type=search]", root);
    const results = $(".roster-results", root);
    const field = root.dataset.name;
    const universe = root.dataset.universe || "";
    let timer = 0;
    let drag = null;

    function sync() {
      $$(".roster-row", list).forEach((row, index) => { $(".ord", row).textContent = String(index + 1); });
      if (empty) empty.hidden = !!list.children.length;
      list.dispatchEvent(new Event("input", { bubbles: true }));
    }

    function rowFor(name) {
      const row = h("li", { class: "roster-row" },
        h("button", { type: "button", class: "grip", draggable: "true", "aria-label": `Drag ${name} to a new place` }, "⋮⋮"),
        h("span", { class: "ord" }, "0"),
        h("span", { class: "who" }, name),
        h("button", { type: "button", class: "rm ghost", "aria-label": `Remove ${name}` }, "✕"),
        h("input", { type: "hidden", name: field, value: name }));
      return row;
    }

    list.addEventListener("click", (e) => {
      const rm = e.target.closest(".rm");
      if (!rm || !list.contains(rm)) return;
      rm.closest(".roster-row").remove();
      sync();
    });

    list.addEventListener("pointerdown", (e) => {
      const grip = e.target.closest(".grip");
      if (!grip || !list.contains(grip)) return;
      const row = grip.closest(".roster-row");
      drag = { row, pointer: e.pointerId };
      row.classList.add("dragging");
      row.setPointerCapture(e.pointerId);
    });
    list.addEventListener("pointermove", (e) => {
      if (!drag || e.pointerId !== drag.pointer) return;
      e.preventDefault();
      drag.row.style.pointerEvents = "none";
      const hit = document.elementFromPoint(e.clientX, e.clientY);
      const target = hit && hit.closest(".roster-row");
      if (!target || target === drag.row || target.parentElement !== list) return;
      const box = target.getBoundingClientRect();
      list.insertBefore(drag.row, e.clientY > box.top + box.height / 2 ? target.nextSibling : target);
    });
    function finishDrag(e) {
      if (!drag || e.pointerId !== drag.pointer) return;
      drag.row.classList.remove("dragging");
      drag.row.style.pointerEvents = "";
      drag = null;
      sync();
    }
    list.addEventListener("pointerup", finishDrag);
    list.addEventListener("pointercancel", finishDrag);
    $$(".grip", list).forEach((grip) => { grip.draggable = true; });
    list.addEventListener("dragstart", (e) => {
      const grip = e.target.closest(".grip");
      if (!grip || !list.contains(grip)) { e.preventDefault(); return; }
      grip.closest(".roster-row").classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", "move");
    });
    list.addEventListener("dragover", (e) => {
      const row = $(".roster-row.dragging", list);
      if (!row) return;
      e.preventDefault();
      const hit = document.elementFromPoint(e.clientX, e.clientY);
      const target = hit && hit.closest(".roster-row");
      if (!target || target === row || target.parentElement !== list) return;
      const box = target.getBoundingClientRect();
      list.insertBefore(row, e.clientY > box.top + box.height / 2 ? target.nextSibling : target);
    });
    list.addEventListener("dragend", () => {
      const row = $(".roster-row.dragging", list);
      if (!row) return;
      row.classList.remove("dragging");
      row.style.pointerEvents = "";
      sync();
    });

    async function searchCards() {
      const q = search.value.trim();
      const params = new URLSearchParams({ universe, q });
      const res = await fetch(`/lookup/cards?${params}`);
      const cards = await res.json();
      results.hidden = false;
      results.replaceChildren();
      if (!cards.length) {
        results.append(h("p", { class: "hint", style: "margin:0" }, q ? "No cards match that search." : "This universe has no cards yet."));
        return;
      }
      cards.forEach((card) => {
        const button = h("button", { type: "button", class: "roster-hit ghost" },
          h("span", {}, card.name),
          h("small", {}, card.class ? title(card.class) : card.universe));
        button.addEventListener("click", () => {
          list.append(rowFor(card.name));
          sync();
        });
        results.append(button);
      });
    }
    search.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(searchCards, 180); });
    search.addEventListener("focus", () => { if (results.hidden) searchCards(); });
  });

  /* ---------------------------------------------------------------- 3D hooks */
  document.addEventListener("click", (e) => {
    const s = e.target.closest("[data-spin]");
    if (s) { e.preventDefault(); window.AVS3D ? window.AVS3D.open({ src: s.dataset.spin, name: s.dataset.name, glow: s.dataset.glow, shape: s.dataset.shape || "card" }) : toast("3D viewer is still loading…"); }
    const p = e.target.closest("[data-spin-preview]");
    if (p) { const img = $("#preview-img"); window.AVS3D && window.AVS3D.open({ src: img.src, name: p.dataset.name, glow: p.dataset.glow, shape: "card" }); }
  });
})();
