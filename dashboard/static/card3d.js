/* three.js card scenes: the full-screen viewer, the home showcase ring, and the
   3D gallery view. Card fronts are the bot's own renders (same origin). */
import * as THREE from "./vendor/three.module.min.js";

const CARD_W = 2, CARD_H = 3, RADIUS = 0.16, DEPTH = 0.05;
const DPR = Math.min(window.devicePixelRatio || 1, 2);
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const loader = new THREE.TextureLoader();

/* ------------------------------------------------------------------ geometry */
function roundedShape(w, h, r) {
  const s = new THREE.Shape();
  const x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  return s;
}
const SHAPE = roundedShape(CARD_W, CARD_H, RADIUS);
function faceGeometry() {
  const g = new THREE.ShapeGeometry(SHAPE, 12);
  const pos = g.attributes.position, uv = g.attributes.uv;
  for (let i = 0; i < pos.count; i++) uv.setXY(i, (pos.getX(i) + CARD_W / 2) / CARD_W, (pos.getY(i) + CARD_H / 2) / CARD_H);
  uv.needsUpdate = true;
  return g;
}
const FACE_GEO = faceGeometry();
const EDGE_GEO = (() => {
  const g = new THREE.ExtrudeGeometry(SHAPE, { depth: DEPTH, bevelEnabled: true, bevelThickness: 0.012, bevelSize: 0.012, bevelSegments: 2, curveSegments: 12 });
  g.translate(0, 0, -DEPTH / 2);
  return g;
})();

/* ------------------------------------------------------------------ textures */
function texFromCanvas(canvas) {
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}
function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.decoding = "async";
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}
async function cardTexture(src) {
  const t = await loader.loadAsync(src);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}
function placeholderTexture(name, glow) {
  const c = document.createElement("canvas");
  c.width = 256; c.height = 384;
  const g = c.getContext("2d");
  g.fillStyle = "#0d0d0d"; g.fillRect(0, 0, 256, 384);
  const pg = g.createRadialGradient(128, 160, 0, 128, 160, 220); pg.addColorStop(0, glow || "#77d4ff"); pg.addColorStop(1, "rgba(0,0,0,0)");
  g.globalAlpha = 0.35; g.fillStyle = pg; g.fillRect(0, 0, 256, 384); g.globalAlpha = 1;
  g.fillStyle = "#fafafa"; g.font = "600 20px Poppins, Inter, sans-serif"; g.textAlign = "center";
  g.fillText((name || "").slice(0, 16), 128, 200);
  return texFromCanvas(c);
}
// Back of every card: Anime VS+ crest in the card's type colour.
const backCache = new Map();
function backTexture(glow = "#77d4ff") {
  if (backCache.has(glow)) return backCache.get(glow);
  const c = document.createElement("canvas");
  c.width = 512; c.height = 768;
  const g = c.getContext("2d");
  g.fillStyle = "#050505"; g.fillRect(0, 0, 512, 768);
  const blob = (x, y, r, col, a) => { const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, col); gr.addColorStop(1, "rgba(0,0,0,0)"); g.globalAlpha = a; g.fillStyle = gr; g.fillRect(0, 0, 512, 768); g.globalAlpha = 1; };
  blob(150, 230, 380, glow, 0.85); blob(400, 600, 330, "#0069a4", 0.7); blob(380, 140, 200, "#ffffff", 0.18);
  const noise = g.getImageData(0, 0, 512, 768), d = noise.data;
  for (let i = 0; i < d.length; i += 4) { const n = (Math.random() - 0.5) * 38; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
  g.putImageData(noise, 0, 0);
  g.textAlign = "center"; g.textBaseline = "middle"; g.fillStyle = "#fafafa";
  g.font = "92px 'Instrument Serif', Georgia, serif"; g.fillText("Anime VS+", 256, 384);
  g.font = "18px 'Geist Mono', ui-monospace, monospace"; g.fillStyle = "rgba(255,255,255,.6)"; g.fillText("CARD BATTLE", 256, 452);
  const t = texFromCanvas(c);
  backCache.set(glow, t);
  return t;
}
// For records that are a picture (summons, universes...): cover-crop into a card face.
async function artCardTexture(src, name, glow) {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 768;
  const g = c.getContext("2d");
  g.fillStyle = "#0d0720"; g.fillRect(0, 0, 512, 768);
  try {
    const img = await loadImage(src);
    const s = Math.max(512 / img.width, 768 / img.height);
    g.drawImage(img, (512 - img.width * s) / 2, (768 - img.height * s) / 2 - 20, img.width * s, img.height * s);
  } catch (e) { /* leave the dark face */ }
  const fade = g.createLinearGradient(0, 520, 0, 768);
  fade.addColorStop(0, "rgba(7,3,15,0)"); fade.addColorStop(1, "rgba(7,3,15,.95)");
  g.fillStyle = fade; g.fillRect(0, 500, 512, 268);
  g.textAlign = "left"; g.font = "500 24px 'Geist Mono', ui-monospace, monospace";
  g.fillStyle = "rgba(250,250,250,.92)"; g.fillText((name || "").slice(0, 28), 32, 712);
  return texFromCanvas(c);
}

/* ------------------------------------------------------------------ foil shader */
function foilMaterial() {
  return new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uTime: { value: 0 }, uTilt: { value: 0 }, uStrength: { value: 0.55 } },
    vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
    fragmentShader: `varying vec2 vUv; uniform float uTime; uniform float uTilt; uniform float uStrength;
      void main(){
        float d = vUv.x * 1.3 + vUv.y * 0.8;
        float band = sin(d * 7.0 - uTilt * 4.0 - uTime * 0.6);
        float m = smoothstep(0.55, 1.0, band) * 0.85 + 0.08;
        vec3 rainbow = 0.55 + 0.45 * cos(6.2831 * (d * 0.6 + uTilt * 0.25 + vec3(0.0, 0.33, 0.67)));
        float edge = smoothstep(0.0, 0.05, vUv.x) * smoothstep(0.0, 0.05, 1.0 - vUv.x) * smoothstep(0.0, 0.035, vUv.y) * smoothstep(0.0, 0.035, 1.0 - vUv.y);
        gl_FragColor = vec4(rainbow * m * uStrength * edge, 1.0);
      }`,
  });
}

/* ------------------------------------------------------------------ card mesh */
function makeCard({ front, glow = "#77d4ff", foil = true }) {
  const group = new THREE.Group();
  const color = new THREE.Color(glow);
  const edge = new THREE.Mesh(EDGE_GEO, new THREE.MeshStandardMaterial({ color: 0x1a1a1a, metalness: 0.9, roughness: 0.3, emissive: color, emissiveIntensity: 0.12 }));
  const frontMat = new THREE.MeshStandardMaterial({ map: front, roughness: 0.38, metalness: 0.05, emissive: 0xffffff, emissiveMap: front, emissiveIntensity: 0.62 });
  const frontMesh = new THREE.Mesh(FACE_GEO, frontMat);
  frontMesh.position.z = DEPTH / 2 + 0.014;
  const back = backTexture(glow);
  const backMesh = new THREE.Mesh(FACE_GEO, new THREE.MeshStandardMaterial({ map: back, emissive: 0xffffff, emissiveMap: back, emissiveIntensity: 0.55, roughness: 0.4 }));
  backMesh.rotation.y = Math.PI;
  backMesh.position.z = -DEPTH / 2 - 0.014;
  group.add(edge, frontMesh, backMesh);
  let foilMesh = null;
  if (foil) {
    foilMesh = new THREE.Mesh(FACE_GEO, foilMaterial());
    foilMesh.position.z = DEPTH / 2 + 0.02;
    group.add(foilMesh);
  }
  group.userData = { frontMesh, foilMesh, glow };
  return group;
}
function setFront(card, texture) {
  const m = card.userData.frontMesh.material;
  m.map = texture; m.emissiveMap = texture; m.needsUpdate = true;
}

function sparkles(count, color, spread = 4) {
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const r = spread * (0.45 + Math.random() * 0.6), a = Math.random() * Math.PI * 2;
    pos[i * 3] = Math.cos(a) * r; pos[i * 3 + 1] = (Math.random() - 0.5) * spread * 1.4; pos[i * 3 + 2] = Math.sin(a) * r;
  }
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const c = document.createElement("canvas"); c.width = c.height = 64;
  const g = c.getContext("2d");
  const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grd.addColorStop(0, "rgba(255,255,255,1)"); grd.addColorStop(0.3, "rgba(255,255,255,.6)"); grd.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grd; g.fillRect(0, 0, 64, 64);
  const mat = new THREE.PointsMaterial({ size: 0.12, map: texFromCanvas(c), color: new THREE.Color(color), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending });
  return new THREE.Points(geo, mat);
}

function makeRenderer(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(DPR);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  return renderer;
}
function lights(scene, glow) {
  scene.add(new THREE.AmbientLight(0xffffff, 0.7));
  const key = new THREE.DirectionalLight(0xffffff, 1.6); key.position.set(3, 4, 6); scene.add(key);
  const rim = new THREE.PointLight(new THREE.Color(glow || "#77d4ff"), 30, 20); rim.position.set(-3, -1, 3); scene.add(rim);
  const rim2 = new THREE.PointLight(0x0069a4, 18, 20); rim2.position.set(3, -2, -3); scene.add(rim2);
  return { key, rim, rim2 };
}
function fit(renderer, camera, canvas) {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (!w || !h) return;
  if (canvas.width !== Math.round(w * DPR) || canvas.height !== Math.round(h * DPR)) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
}
function webglOk() {
  try { const c = document.createElement("canvas"); return !!(c.getContext("webgl2") || c.getContext("webgl")); } catch (e) { return false; }
}

/* ------------------------------------------------------------------ full-screen viewer */
const Viewer = (() => {
  const dialog = document.getElementById("viewer");
  if (!dialog || !webglOk()) return { open: (o) => window.open(o.src, "_blank") };
  const canvas = document.getElementById("viewer-canvas");
  let renderer, scene, camera, card, dust, light, raf = 0, clock = new THREE.Clock();
  let rotY = 0, rotX = 0, velY = 0, velX = 0, targetFlip = 0, flipOffset = 0, autoSpin = !reduceMotion, shine = true, zoom = 7.2;
  let dragging = false, lastX = 0, lastY = 0, pinch = null;
  const pointers = new Map();

  function setup() {
    renderer = makeRenderer(canvas);
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    camera.position.set(0, 0, zoom);
    light = lights(scene);
    canvas.addEventListener("pointerdown", (e) => {
      canvas.setPointerCapture(e.pointerId);
      pointers.set(e.pointerId, [e.clientX, e.clientY]);
      if (pointers.size === 2) { const [a, b] = [...pointers.values()]; pinch = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), z: zoom }; }
      dragging = true; lastX = e.clientX; lastY = e.clientY; velX = velY = 0;
    });
    canvas.addEventListener("pointermove", (e) => {
      if (!pointers.has(e.pointerId)) return;
      pointers.set(e.pointerId, [e.clientX, e.clientY]);
      if (pointers.size === 2 && pinch) {
        const [a, b] = [...pointers.values()];
        zoom = THREE.MathUtils.clamp(pinch.z * pinch.d / Math.max(20, Math.hypot(a[0] - b[0], a[1] - b[1])), 4.2, 12);
        return;
      }
      if (!dragging) return;
      const dx = e.clientX - lastX, dy = e.clientY - lastY;
      lastX = e.clientX; lastY = e.clientY;
      velY = dx * 0.012; velX = dy * 0.008;
      rotY += velY; rotX = THREE.MathUtils.clamp(rotX + velX, -0.7, 0.7);
    });
    const up = (e) => { pointers.delete(e.pointerId); if (pointers.size < 2) pinch = null; if (!pointers.size) dragging = false; };
    canvas.addEventListener("pointerup", up);
    canvas.addEventListener("pointercancel", up);
    canvas.addEventListener("dblclick", () => flip());
    canvas.addEventListener("wheel", (e) => { e.preventDefault(); zoom = THREE.MathUtils.clamp(zoom + e.deltaY * 0.004, 4.2, 12); }, { passive: false });
    dialog.addEventListener("close", stop);
    dialog.querySelectorAll("[data-viewer]").forEach((b) => b.addEventListener("click", () => {
      const a = b.dataset.viewer;
      if (a === "spin") { autoSpin = !autoSpin; velY = autoSpin ? 0.08 : 0; b.textContent = autoSpin ? "⏸ Pause" : "🌀 Spin"; }
      if (a === "flip") flip();
      if (a === "shine") { shine = !shine; b.textContent = shine ? "✨ Shine" : "▫️ Matte"; }
      if (a === "reset") { rotY = rotY - (rotY % (Math.PI * 2)); flipOffset = targetFlip = 0; rotX = 0; velX = velY = 0; zoom = defaultZoom(); }
    }));
  }
  function flip() { targetFlip += Math.PI; }
  function defaultZoom() {
    const half = Math.tan(THREE.MathUtils.degToRad(19));
    const aspect = (canvas.clientWidth || window.innerWidth) / Math.max(1, canvas.clientHeight || window.innerHeight);
    return THREE.MathUtils.clamp(Math.max(7.2, 1.45 / (half * aspect)), 4.2, 12);
  }
  function stop() { cancelAnimationFrame(raf); raf = 0; }
  function loop() {
    raf = requestAnimationFrame(loop);
    const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;
    fit(renderer, camera, canvas);
    if (!dragging) {
      velY *= 0.95; velX *= 0.9;
      rotY += velY + (autoSpin ? dt * 0.55 : 0);
      rotX += velX; rotX *= 0.96;
    }
    flipOffset += (targetFlip - flipOffset) * Math.min(1, dt * 7);
    camera.position.z += (zoom - camera.position.z) * Math.min(1, dt * 8);
    if (card) {
      card.rotation.y = rotY + flipOffset;
      card.rotation.x = rotX + Math.sin(t * 0.9) * 0.04;
      card.position.y = Math.sin(t * 1.3) * 0.08;
      const foil = card.userData.foilMesh;
      if (foil) { foil.material.uniforms.uTime.value = t; foil.material.uniforms.uTilt.value = card.rotation.y + card.rotation.x; foil.material.uniforms.uStrength.value += ((shine ? 0.55 : 0) - foil.material.uniforms.uStrength.value) * 0.1; }
    }
    if (dust) dust.rotation.y = t * 0.08;
    light.rim.position.set(Math.cos(t * 0.7) * 4, Math.sin(t * 0.5) * 2, 3);
    renderer.render(scene, camera);
  }
  async function open({ src, name, glow = "#77d4ff", shape = "card" }) {
    if (!renderer) setup();
    document.getElementById("viewer-title").textContent = name || "";
    if (card) { scene.remove(card); }
    if (dust) { scene.remove(dust); }
    card = makeCard({ front: placeholderTexture(name, glow), glow });
    card.scale.setScalar(0.01);
    scene.add(card);
    dust = sparkles(120, "#ffffff", 4.2);
    scene.add(dust);
    light.rim.color.set(glow);
    rotY = -0.6; rotX = 0; velY = reduceMotion ? 0 : 0.18; targetFlip = flipOffset = 0;
    if (!dialog.open) dialog.showModal();
    zoom = defaultZoom();
    clock.getDelta();
    if (!raf) loop();
    const target = card;
    const grow = () => { if (target.scale.x < 1) { target.scale.setScalar(Math.min(1, target.scale.x + 0.08)); requestAnimationFrame(grow); } };
    grow();
    try {
      const tex = shape === "card" ? await cardTexture(src) : await artCardTexture(src, name, glow);
      if (card === target) setFront(target, tex);
    } catch (e) { window.AVSToast && window.AVSToast("Couldn't load that picture.", "error"); }
  }
  return { open };
})();
window.AVS3D = Viewer;

/* ------------------------------------------------------------------ carousel ring (home + 3D gallery) */
function ring({ canvas, items, onOpen, onFocus, auto = true, cameraZ = 9.5, radiusScale = 1 }) {
  const renderer = makeRenderer(canvas);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  const l = lights(scene, "#77d4ff");
  const group = new THREE.Group();
  scene.add(group);
  const n = Math.max(items.length, 1);
  const radius = Math.max(3.2, (n * (CARD_W + 0.55)) / (Math.PI * 2)) * radiusScale;
  // Keep the front card (about 3.4 tall, 2.3 wide when enlarged) fully in view at any aspect.
  const placeCamera = () => {
    const half = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    const dist = Math.max(2.35 / half, 2.0 / (half * Math.max(camera.aspect, 0.3)));
    camera.position.set(0, 0.55, radius + dist);
    camera.lookAt(0, 0.1, 0);
  };
  let lastAspect = 0;
  const cards = items.map((item, i) => {
    const glow = (item.type && item.type.glow) || "#77d4ff";
    const card = makeCard({ front: placeholderTexture(item.name, glow), glow, foil: n <= 40 });
    const a = (i / n) * Math.PI * 2;
    card.position.set(Math.sin(a) * radius, 0, Math.cos(a) * radius);
    card.rotation.y = a;
    card.userData.index = i;
    card.userData.flip = 0;
    card.userData.flipTarget = 0;
    group.add(card);
    return card;
  });
  scene.add(Object.assign(sparkles(160, "#ffffff", radius + 2), { name: "dust" }));
  // load fronts nearest-first
  const order = items.map((_, i) => i).sort((a, b) => Math.min(a, n - a) - Math.min(b, n - b));
  (async () => {
    for (const i of order) {
      const it = items[i];
      try {
        const glow = (it.type && it.type.glow) || "#77d4ff";
        const tex = it.render ? await cardTexture(it.render) : it.image ? await artCardTexture(it.image, it.name, glow) : await itemTexture(it);
        setFront(cards[i], tex);
      } catch (e) { /* keep placeholder */ }
    }
  })();

  let angle = 0, target = 0, vel = 0, dragging = false, moved = 0, lastX = 0, focus = 0, lastTap = 0;
  const step = (Math.PI * 2) / n;
  const raycaster = new THREE.Raycaster(), ndc = new THREE.Vector2();
  function setFocus(i) {
    focus = ((i % n) + n) % n;
    target = -focus * step;
    // shortest path
    while (target - angle > Math.PI) target -= Math.PI * 2;
    while (target - angle < -Math.PI) target += Math.PI * 2;
    onFocus && onFocus(focus, items[focus]);
  }
  function pick(e) {
    const r = canvas.getBoundingClientRect();
    ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    raycaster.setFromCamera(ndc, camera);
    const hit = raycaster.intersectObjects(cards, true)[0];
    if (!hit) return -1;
    let o = hit.object; while (o && o.userData.index === undefined) o = o.parent;
    return o ? o.userData.index : -1;
  }
  canvas.addEventListener("pointerdown", (e) => { dragging = true; moved = 0; lastX = e.clientX; vel = 0; canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const dx = e.clientX - lastX; lastX = e.clientX; moved += Math.abs(dx);
    vel = dx * 0.006; angle += vel; target = angle;
  });
  const release = (e) => {
    if (!dragging) return;
    dragging = false;
    if (moved < 6) {
      const i = pick(e);
      if (i >= 0) {
        const now = performance.now();
        if (i === focus && now - lastTap < 320) { cards[i].userData.flipTarget += Math.PI; }
        else if (i === focus && onOpen) onOpen(i, items[i]);
        else setFocus(i);
        lastTap = now;
      }
    } else {
      const projected = angle + vel * 18;
      setFocus(Math.round(-projected / step));
    }
  };
  canvas.addEventListener("pointerup", release);
  canvas.addEventListener("pointercancel", () => { dragging = false; });

  let raf = 0, visible = true, idle = 0;
  const clock = new THREE.Clock();
  new IntersectionObserver(([en]) => { visible = en.isIntersecting; if (visible && !raf) loop(); }).observe(canvas);
  function loop() {
    if (!visible) { raf = 0; return; }
    raf = requestAnimationFrame(loop);
    const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;
    fit(renderer, camera, canvas);
    if (camera.aspect !== lastAspect) { lastAspect = camera.aspect; placeCamera(); }
    if (!dragging) {
      idle += dt;
      if (auto && !reduceMotion && idle > 3) { target -= dt * 0.25; focus = ((Math.round(-target / step) % n) + n) % n; }
      angle += (target - angle) * Math.min(1, dt * 5);
    } else idle = 0;
    group.rotation.y = angle;
    cards.forEach((c, i) => {
      const a = (i / n) * Math.PI * 2 + angle;
      const front = Math.cos(a);              // 1 at the front of the ring
      const s = 0.82 + Math.max(0, front) * 0.28;
      c.scale.setScalar(s);
      c.position.y = Math.sin(t * 1.2 + i) * 0.06 + (i === focus ? 0.12 : 0);
      c.userData.flip += (c.userData.flipTarget - c.userData.flip) * Math.min(1, dt * 7);
      c.rotation.y = (i / n) * Math.PI * 2 + c.userData.flip;
      const foil = c.userData.foilMesh;
      if (foil) { foil.material.uniforms.uTime.value = t; foil.material.uniforms.uTilt.value = a; foil.material.uniforms.uStrength.value = 0.15 + Math.max(0, front) * 0.4; }
    });
    const dust = scene.getObjectByName("dust");
    if (dust) dust.rotation.y = -t * 0.04;
    l.rim.position.set(Math.cos(t * 0.6) * 5, 1, Math.sin(t * 0.6) * 5);
    renderer.render(scene, camera);
  }
  loop();
  setFocus(0);
  return {
    next: () => { idle = -999; setFocus(focus + 1); },
    prev: () => { idle = -999; setFocus(focus - 1); },
    flip: () => { cards[focus].userData.flipTarget += Math.PI; },
    focus: () => focus,
  };
}

// Face for records without a picture (titles, arms): big emblem + abilities.
function itemTexture(it) {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 768;
  const g = c.getContext("2d");
  const glow = (it.type && it.type.glow) || "#77d4ff", col = (it.type && it.type.color) || "#0069a4";
  g.fillStyle = "#050505"; g.fillRect(0, 0, 512, 768);
  const blob = (x, y, r, c, a) => { const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, c); gr.addColorStop(1, "rgba(0,0,0,0)"); g.globalAlpha = a; g.fillStyle = gr; g.fillRect(0, 0, 512, 768); g.globalAlpha = 1; };
  blob(170, 220, 360, glow, 0.9); blob(400, 420, 300, col, 0.8);
  const nz = g.getImageData(0, 0, 512, 768), nd = nz.data;
  for (let i = 0; i < nd.length; i += 4) { const n = (Math.random() - 0.5) * 34; nd[i] += n; nd[i + 1] += n; nd[i + 2] += n; }
  g.putImageData(nz, 0, 0);
  g.textAlign = "center"; g.textBaseline = "middle";
  g.font = "170px 'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif";
  g.fillText((it.type && it.type.key && it.type.emoji) || "✨", 256, 250);
  const name = (it.name || "").slice(0, 22);
  g.font = "600 40px Poppins, Inter, sans-serif"; g.fillStyle = "#fafafa"; g.fillText(name, 256, 480);
  g.font = "500 22px 'Geist Mono', ui-monospace, monospace";
  (it.abilities || []).slice(0, 3).forEach(([e, text], i) => {
    g.fillStyle = "rgba(0,0,0,.45)"; g.fillRect(56, 530 + i * 58, 400, 46);
    g.fillStyle = "rgba(250,250,250,.9)"; g.fillText(`${e} ${text}`.slice(0, 28), 256, 554 + i * 58);
  });
  return Promise.resolve(texFromCanvas(c));
}

/* ------------------------------------------------------------------ page wiring */
const PAGE = window.AVS_PAGE || {};
if (webglOk()) {
  const hero = document.getElementById("hero-canvas");
  if (hero && PAGE.showcase && PAGE.showcase.length) {
    ring({ canvas: hero, items: PAGE.showcase, onOpen: (i, it) => { location.href = it.edit; }, radiusScale: 1 });
  }
  const stage = document.getElementById("stage-canvas");
  if (stage && PAGE.tiles && PAGE.tiles.length) {
    const caption = document.getElementById("stage-caption");
    const ctl = ring({
      canvas: stage, items: PAGE.tiles, auto: false,
      onOpen: (i, it) => { location.href = it.edit; },
      onFocus: (i, it) => { caption.innerHTML = ""; caption.append(it.name); const s = document.createElement("small"); s.textContent = [it.universe, ...(it.chips || []).slice(0, 2)].filter(Boolean).join(" · "); caption.append(s); },
    });
    document.querySelectorAll("[data-stage]").forEach((b) => b.addEventListener("click", () => {
      const a = b.dataset.stage;
      if (a === "next") ctl.next();
      if (a === "prev") ctl.prev();
      if (a === "flip") ctl.flip();
      if (a === "open") location.href = PAGE.tiles[ctl.focus()].edit;
    }));
    document.addEventListener("keydown", (e) => { if (e.key === "ArrowRight") ctl.next(); if (e.key === "ArrowLeft") ctl.prev(); });
  }
}
