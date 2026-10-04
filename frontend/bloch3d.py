"""A draggable, ink-style 3D Bloch sphere.

Runs entirely in the browser (plain SVG + JS inside ``components.html``), so
dragging is smooth and never waits on the server.

* ``dial`` mode: one sphere you can grab. Drag the arrow tip to set the state,
  drag anywhere else to orbit; probabilities and amplitudes update live.
* ``view`` mode: one or more read-only spheres (e.g. each qubit of a circuit)
  that orbit together.
"""

from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components

_TEMPLATE = r"""
<style>
@font-face { font-family: "Patrick Hand"; src: url("app/static/fonts/PatrickHand-latin.woff2") format("woff2"); }
@font-face { font-family: "Caveat"; font-weight: 400 700; src: url("app/static/fonts/Caveat-latin.woff2") format("woff2"); }
@font-face { font-family: "Atkinson Hyperlegible"; src: url("app/static/fonts/AtkinsonHyperlegible-Regular-latin.woff2") format("woff2"); }
body.readable, body.readable .title, body.readable .panel h4, body.readable .pct, body.readable .angles,
body.readable .snaps button { font-family: "Atkinson Hyperlegible", system-ui, sans-serif; }
body.readable .title, body.readable .panel h4 { font-size: 18px; }
body.readable .pct, body.readable .angles { font-size: 16px; }
html, body { margin: 0; background: transparent; color: #2b2a27; font-family: "Patrick Hand", "Comic Neue", cursive; }
.wrap { display: flex; gap: 22px; flex-wrap: wrap; align-items: flex-start; }
.sphere { display: flex; flex-direction: column; align-items: center; }
.sphere svg { touch-action: none; user-select: none; cursor: grab; }
.sphere svg.grabbing { cursor: grabbing; }
.sphere .title { font-family: "Caveat", cursive; font-size: 22px; font-weight: 700; color: #1d3a8a; height: 24px; }
.hint { font-size: 14px; color: #6f6a5e; text-align: center; max-width: 280px; }
.panel { flex: 1; min-width: 240px; max-width: 380px; }
.panel h4 { font-family: "Caveat", cursive; font-size: 24px; color: #1d3a8a; margin: 4px 0 6px; }
.row { display: grid; grid-template-columns: 42px 1fr 64px; gap: 10px; align-items: center; margin: 8px 0; }
.row b { font-family: "Courier Prime", "Courier New", monospace; color: #1d3a8a; }
.track { height: 18px; border-bottom: 1.5px solid #b9b19c; }
.fill { height: 100%; background: #ffe867; border-radius: 3px 9px 4px 10px / 8px 3px 9px 4px; transform: skewX(-8deg); }
.row:nth-child(3) .fill { background: #b8f0c8; }
.pct { font-family: "Caveat", cursive; font-size: 22px; color: #1d3a8a; text-align: right; }
.amp { font-family: "Courier Prime", "Courier New", monospace; font-size: 13px; background: #fffef9; border: 1px solid #ddd3b8; padding: 6px 8px; margin: 8px 0; }
.angles { font-family: "Caveat", cursive; font-size: 20px; color: #6f6a5e; }
label.slider { display: grid; grid-template-columns: 58px 1fr; align-items: center; gap: 8px; font-size: 15px; margin: 4px 0; }
input[type=range] { accent-color: #1d3a8a; width: 100%; }
.snaps { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 2px; }
.snaps button {
  font-family: "Patrick Hand", cursive; font-size: 15px; color: #1d3a8a; background: transparent; cursor: pointer;
  border: 1.5px solid #1d3a8a; border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px; padding: 2px 10px;
}
.snaps button:hover { background: rgba(255, 232, 103, .5); }
</style>
<div class="wrap" id="root"></div>
<script>
const CFG = __CONFIG__;
if (CFG.readable) document.body.classList.add("readable");
const INK = "#1d3a8a", RED = "#ab2e22", PENCIL = "#6f6a5e", LIGHT = "#a9a08a", GRAPHITE = "#2b2a27";
let az = 0.52, el = 0.32;
const SIZE = CFG.size || 250, R = SIZE * 0.34;
const root = document.getElementById("root");
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];

function camera() {
  const sa = Math.sin(az), ca = Math.cos(az), se = Math.sin(el), ce = Math.cos(el);
  return { r: [-sa, ca, 0], u: [-ca * se, -sa * se, ce], f: [ca * ce, sa * ce, se] };
}
function project(p, cam, cx, cy) { return [cx + R * dot(p, cam.r), cy - R * dot(p, cam.u), dot(p, cam.f)]; }

function circlePaths(pointAt, cam, cx, cy, color, width, dashBack) {
  // Split a closed curve into front (solid) and back (dashed) runs.
  let out = "", run = [], front = null;
  const flush = () => {
    if (run.length > 1) {
      out += '<polyline points="' + run.join(" ") + '" fill="none" stroke="' + color + '" stroke-width="' + width + '"'
        + (front ? "" : ' stroke-dasharray="' + dashBack + '" opacity="0.65"') + "/>";
    }
  };
  for (let i = 0; i <= 96; i++) {
    const [x, y, d] = project(pointAt(2 * Math.PI * i / 96), cam, cx, cy);
    const isFront = d >= 0;
    if (front !== null && isFront !== front) { run.push(x.toFixed(1) + "," + y.toFixed(1)); flush(); run = []; }
    front = isFront;
    run.push(x.toFixed(1) + "," + y.toFixed(1));
  }
  flush();
  return out;
}

function sphereSVG(vec, opts) {
  const cam = camera(), cx = SIZE / 2, cy = SIZE / 2;
  let lines = "", texts = "";
  lines += '<circle cx="' + cx + '" cy="' + cy + '" r="' + R + '" fill="rgba(255,255,255,.45)" stroke="' + GRAPHITE + '" stroke-width="1.7"/>';
  lines += circlePaths(t => [Math.cos(t), Math.sin(t), 0], cam, cx, cy, LIGHT, 1.2, "3 4");
  lines += circlePaths(t => [Math.cos(t), 0, Math.sin(t)], cam, cx, cy, LIGHT, 0.8, "2 5");
  lines += circlePaths(t => [0, Math.cos(t), Math.sin(t)], cam, cx, cy, LIGHT, 0.8, "2 5");
  const len = Math.hypot(vec[0], vec[1], vec[2]);
  if (opts.latitude && len > 0.98) {
    const z = vec[2], rho = Math.sqrt(Math.max(0, 1 - z * z));
    lines += circlePaths(t => [rho * Math.cos(t), rho * Math.sin(t), z], cam, cx, cy, RED, 1, "2 4");
  }
  const axes = [[[0, 0, 1], "|0⟩"], [[0, 0, -1], "|1⟩"], [[1, 0, 0], "|+⟩"], [[-1, 0, 0], "|−⟩"], [[0, 1, 0], "|+i⟩"], [[0, -1, 0], "|−i⟩"]];
  for (const [p, label] of axes) {
    const [x, y, d] = project(p, cam, cx, cy);
    lines += '<line x1="' + cx + '" y1="' + cy + '" x2="' + x.toFixed(1) + '" y2="' + y.toFixed(1) + '" stroke="' + LIGHT + '" stroke-width="1" opacity="' + (d >= 0 ? 0.9 : 0.4) + '"/>';
    const [lx, ly, ld] = project([p[0] * 1.24, p[1] * 1.24, p[2] * 1.2], cam, cx, cy);
    texts += '<text x="' + lx.toFixed(1) + '" y="' + (ly + 5).toFixed(1) + '" text-anchor="middle" font-size="15" fill="' + PENCIL + '" opacity="' + (ld >= -0.2 ? 1 : 0.45) + '">' + label + "</text>";
  }
  for (const t of opts.trail || []) {
    const [x, y] = project(t, cam, cx, cy);
    lines += '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="3" fill="' + INK + '" opacity="0.25"/>';
  }
  if (len > 1e-6) {
    const [tx, ty, td] = project(vec, cam, cx, cy);
    const [fx, fy] = project([vec[0], vec[1], 0], cam, cx, cy);
    lines += '<line x1="' + tx.toFixed(1) + '" y1="' + ty.toFixed(1) + '" x2="' + fx.toFixed(1) + '" y2="' + fy.toFixed(1) + '" stroke="' + INK + '" stroke-dasharray="2 3" opacity="0.55"/>';
    lines += '<line x1="' + cx + '" y1="' + cy + '" x2="' + fx.toFixed(1) + '" y2="' + fy.toFixed(1) + '" stroke="' + INK + '" stroke-dasharray="2 3" opacity="0.35"/>';
    lines += '<line x1="' + cx + '" y1="' + cy + '" x2="' + tx.toFixed(1) + '" y2="' + ty.toFixed(1) + '" stroke="' + INK + '" stroke-width="3.6" stroke-linecap="round" opacity="' + (td >= 0 ? 1 : 0.6) + '"/>';
    lines += '<circle cx="' + tx.toFixed(1) + '" cy="' + ty.toFixed(1) + '" r="' + (opts.handle ? 8 : 6) + '" fill="' + INK + '" stroke="#fff" stroke-width="2"/>';
    if (opts.handle) {
      texts += '<circle data-handle="1" cx="' + tx.toFixed(1) + '" cy="' + ty.toFixed(1) + '" r="20" fill="transparent" style="cursor:pointer"/>';
    }
  } else {
    lines += '<circle cx="' + cx + '" cy="' + cy + '" r="5" fill="' + RED + '"/>';
  }
  lines += '<circle cx="' + cx + '" cy="' + cy + '" r="2.5" fill="' + GRAPHITE + '"/>';
  if (len < 0.98) {
    texts += '<text x="' + cx + '" y="' + (SIZE - 4) + '" text-anchor="middle" font-size="14" fill="' + RED + '">arrow shrunk to ' + len.toFixed(2) + " (entangled or noisy)</text>";
  }
  const defs = '<defs><filter id="rough" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="2.2"/></filter></defs>';
  return defs + '<g filter="url(#rough)">' + lines + "</g>" + texts;
}

// ---------------------------------------------------------------- dial mode
let theta = (CFG.theta || 0) * Math.PI, phi = (CFG.phi || 0) * Math.PI;
const spheres = [];

function blochOf(t, p) { return [Math.sin(t) * Math.cos(p), Math.sin(t) * Math.sin(p), Math.cos(t)]; }
function fmt(re, im) {
  re = Math.abs(re) < 5e-4 ? 0 : re; im = Math.abs(im) < 5e-4 ? 0 : im;
  const s = v => (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(3);
  if (im === 0) return s(re);
  if (re === 0) return s(im) + "i";
  return s(re) + s(im) + "i";
}

function buildDial() {
  const box = document.createElement("div");
  box.className = "sphere";
  box.innerHTML = '<svg width="' + SIZE + '" height="' + SIZE + '" viewBox="0 0 ' + SIZE + " " + SIZE + '" role="img" aria-label="Bloch sphere: drag the arrow tip to change the state, drag elsewhere to rotate the view"></svg>'
    + '<div class="hint">drag the dot to move the state · drag anywhere else to turn the sphere</div>';
  root.appendChild(box);
  const panel = document.createElement("div");
  panel.className = "panel";
  panel.innerHTML = '<h4>If you measured now</h4>'
    + '<div class="row"><b>|0⟩</b><div class="track"><div class="fill" id="f0"></div></div><span class="pct" id="p0"></span></div>'
    + '<div class="row"><b>|1⟩</b><div class="track"><div class="fill" id="f1"></div></div><span class="pct" id="p1"></span></div>'
    + '<div class="amp" id="amp"></div><div class="angles" id="angles"></div>'
    + '<label class="slider">tilt θ <input type="range" id="th" min="0" max="1" step="0.01" aria-label="tilt theta in units of pi"></label>'
    + '<label class="slider">spin φ <input type="range" id="ph" min="0" max="2" step="0.01" aria-label="spin phi in units of pi"></label>'
    + '<div class="snaps">' + [["|0⟩", 0, 0], ["|1⟩", 1, 0], ["|+⟩", .5, 0], ["|−⟩", .5, 1], ["|+i⟩", .5, .5], ["|−i⟩", .5, 1.5]]
      .map(([l, t, p]) => '<button data-t="' + t + '" data-p="' + p + '">' + l + "</button>").join("") + "</div>"
    + (CFG.show_curve ? '<svg id="curve" width="300" height="130" viewBox="0 0 300 130"></svg>' : "");
  root.appendChild(panel);
  spheres.push({ svg: box.querySelector("svg"), dial: true });
  panel.querySelector("#th").addEventListener("input", e => { theta = +e.target.value * Math.PI; render(); });
  panel.querySelector("#ph").addEventListener("input", e => { phi = +e.target.value * Math.PI; render(); });
  panel.querySelectorAll(".snaps button").forEach(b => b.addEventListener("click", () => {
    theta = +b.dataset.t * Math.PI; phi = +b.dataset.p * Math.PI; render();
  }));
}

function updatePanel() {
  const p0 = Math.cos(theta / 2) ** 2, p1 = 1 - p0;
  document.getElementById("f0").style.width = (p0 * 100).toFixed(1) + "%";
  document.getElementById("f1").style.width = (p1 * 100).toFixed(1) + "%";
  document.getElementById("p0").textContent = (p0 * 100).toFixed(1) + "%";
  document.getElementById("p1").textContent = (p1 * 100).toFixed(1) + "%";
  const s = Math.sin(theta / 2);
  document.getElementById("amp").textContent = "|ψ⟩ = (" + fmt(Math.cos(theta / 2), 0) + ")|0⟩ + (" + fmt(s * Math.cos(phi), s * Math.sin(phi)) + ")|1⟩";
  document.getElementById("angles").textContent = "θ = " + (theta / Math.PI).toFixed(2) + "π   ·   φ = " + (phi / Math.PI).toFixed(2) + "π";
  document.getElementById("th").value = (theta / Math.PI).toFixed(2);
  document.getElementById("ph").value = (phi / Math.PI).toFixed(2);
  const curve = document.getElementById("curve");
  if (curve) {
    const L = 34, W = 256, T = 10, H = 90, sx = t => L + W * t / Math.PI, sy = v => T + H * (1 - v);
    let pts = "";
    for (let i = 0; i <= 80; i++) { const t = Math.PI * i / 80; pts += sx(t).toFixed(1) + "," + sy(Math.sin(t / 2) ** 2).toFixed(1) + " "; }
    curve.innerHTML = '<line x1="' + L + '" y1="' + (T + H) + '" x2="' + (L + W) + '" y2="' + (T + H) + '" stroke="' + LIGHT + '"/>'
      + '<line x1="' + L + '" y1="' + T + '" x2="' + L + '" y2="' + (T + H) + '" stroke="' + LIGHT + '"/>'
      + '<polyline points="' + pts + '" fill="none" stroke="#3b6fc4" stroke-width="2"/>'
      + '<circle cx="' + sx(theta).toFixed(1) + '" cy="' + sy(p1).toFixed(1) + '" r="6" fill="' + INK + '" stroke="#fff" stroke-width="2"/>'
      + '<text x="' + (L + 6) + '" y="' + (T + 10) + '" font-size="14" fill="' + PENCIL + '">P(1) = sin²(θ/2)</text>'
      + '<text x="' + L + '" y="' + (T + H + 18) + '" font-size="13" fill="' + PENCIL + '">0</text>'
      + '<text x="' + (L + W / 2) + '" y="' + (T + H + 18) + '" text-anchor="middle" font-size="13" fill="' + PENCIL + '">π/2</text>'
      + '<text x="' + (L + W) + '" y="' + (T + H + 18) + '" text-anchor="end" font-size="13" fill="' + PENCIL + '">π</text>';
  }
}

// ---------------------------------------------------------------- view mode
function buildView() {
  for (const q of CFG.qubits) {
    const box = document.createElement("div");
    box.className = "sphere";
    box.innerHTML = '<div class="title">' + (q.title || "") + "</div>"
      + '<svg width="' + SIZE + '" height="' + SIZE + '" viewBox="0 0 ' + SIZE + " " + SIZE + '" role="img" aria-label="Bloch sphere for ' + (q.title || "a qubit") + '"></svg>';
    root.appendChild(box);
    spheres.push({ svg: box.querySelector("svg"), vec: q.vector, trail: q.trail || [] });
  }
  const hint = document.createElement("div");
  hint.className = "hint";
  hint.style.alignSelf = "center";
  hint.textContent = "drag a sphere to turn them all";
  root.appendChild(hint);
}

function render() {
  for (const s of spheres) {
    s.svg.innerHTML = s.dial
      ? sphereSVG(blochOf(theta, phi), { handle: true, latitude: true })
      : sphereSVG(s.vec, { trail: s.trail });
  }
  if (CFG.mode === "dial") updatePanel();
}

// ---------------------------------------------------------------- dragging
let drag = null;
function attach(svg, dial) {
  svg.addEventListener("pointerdown", e => {
    const onHandle = dial && e.target.dataset && e.target.dataset.handle;
    drag = { kind: onHandle ? "state" : "orbit", x: e.clientX, y: e.clientY, svg };
    svg.setPointerCapture(e.pointerId);
    svg.classList.add("grabbing");
    e.preventDefault();
  });
  svg.addEventListener("pointermove", e => {
    if (!drag || drag.svg !== svg) return;
    if (drag.kind === "orbit") {
      az -= (e.clientX - drag.x) * 0.012;
      el = Math.max(-1.35, Math.min(1.35, el + (e.clientY - drag.y) * 0.012));
      drag.x = e.clientX; drag.y = e.clientY;
    } else {
      const rect = svg.getBoundingClientRect();
      let u = (e.clientX - rect.left - SIZE / 2) / R, v = (SIZE / 2 - (e.clientY - rect.top)) / R;
      const n = Math.hypot(u, v);
      if (n > 0.999) { u *= 0.999 / n; v *= 0.999 / n; }
      const w = Math.sqrt(Math.max(0, 1 - u * u - v * v)), cam = camera();
      const p = [0, 1, 2].map(i => u * cam.r[i] + v * cam.u[i] + w * cam.f[i]);
      theta = Math.acos(Math.max(-1, Math.min(1, p[2])));
      phi = Math.atan2(p[1], p[0]);
      if (phi < 0) phi += 2 * Math.PI;
    }
    render();
  });
  const end = () => { drag = null; svg.classList.remove("grabbing"); };
  svg.addEventListener("pointerup", end);
  svg.addEventListener("pointercancel", end);
}

if (CFG.mode === "dial") buildDial(); else buildView();
spheres.forEach(s => attach(s.svg, !!s.dial));
render();
</script>
"""


def _render(config: dict, height: int) -> None:
    config = {**config, "readable": st.session_state.get("reading_mode") == "plain"}
    # Escape "<" so no string in the config can close the <script> tag.
    payload = json.dumps(config).replace("<", "\\u003c")
    html = _TEMPLATE.replace("__CONFIG__", payload)
    if hasattr(st, "iframe"):  # Streamlit >= 1.5x; components.v1.html is deprecated
        st.iframe(html, height=height)
    else:
        components.html(html, height=height)


def bloch_dial_3d(theta_pi: float = 0.0, phi_pi: float = 0.0, show_curve: bool = False) -> None:
    """One sphere the learner can grab, with live measurement odds."""
    _render({"mode": "dial", "theta": theta_pi, "phi": phi_pi, "show_curve": show_curve, "size": 270}, 470 if show_curve else 340)


def bloch_view_3d(qubits: list[dict], size: int = 210) -> None:
    """Read-only spheres that orbit together. ``qubits``: [{"title", "vector", "trail"?}]."""
    clean = [
        {
            "title": str(q.get("title", "")),
            "vector": [float(v) for v in q["vector"]],
            "trail": [[float(v) for v in t] for t in q.get("trail", [])],
        }
        for q in qubits
    ]
    _render({"mode": "view", "qubits": clean, "size": size}, size + 40)
