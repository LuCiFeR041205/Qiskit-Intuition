"""Interactive "feel it first" widgets and small SVG visuals.

Every widget is pure Python + inline SVG so it renders instantly on Hugging
Face Spaces without extra JavaScript bundles. Single-qubit maths is done with
2x2 NumPy matrices; anything bigger uses the shared QuantumEngine.

Drawings are styled like a lab notebook: pencil outlines, blue and red ink,
handwritten labels, and a slight hand-drawn wobble from an SVG filter.
"""

from __future__ import annotations

import html
import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib import font_manager

from backend.core.qiskit_thread import on_qiskit_thread

INK = "#2b2a27"      # graphite (text)
MUTED = "#6f6a5e"    # pencil
GRID = "#a9a08a"     # light pencil
TEAL = "#1d3a8a"     # blue ink (state arrows, markers)
AMBER = "#ab2e22"    # red ink (highlights); meets WCAG AA on paper and sticky notes
BLUE = "#3b6fc4"     # lighter blue ink (curves)
PAPER = "#fbf7ec"
STICKY = "#fff1a1"

_ROUGH_DEFS = (
    '<defs><filter id="qi-rough" x="-5%" y="-5%" width="110%" height="110%">'
    '<feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="7"/>'
    '<feDisplacementMap in="SourceGraphic" scale="2.4"/></filter></defs>'
)
_TEXT_RE = re.compile(r"<text\b.*?</text>", re.S)
_SVG_RE = re.compile(r"(<svg\b[^>]*>)(.*)</svg>$", re.S)
_FONT_STYLE = "font-family:'Patrick Hand','Caveat',cursive"


def sketch(svg: str) -> str:
    """Give an SVG drawing a hand-drawn wobble and handwritten labels.

    Lines and shapes go through a displacement filter; text is kept crisp
    and drawn on top so it stays legible.
    """
    texts = "".join(_TEXT_RE.findall(svg))
    match = _SVG_RE.match(_TEXT_RE.sub("", svg))
    if not match:
        return svg
    open_tag, inner = match.groups()
    if 'style="' in open_tag:
        open_tag = open_tag.replace('style="', f'style="{_FONT_STYLE};', 1)
    else:
        open_tag = open_tag[:-1] + f' style="{_FONT_STYLE}">'
    return f'{open_tag}{_ROUGH_DEFS}<g filter="url(#qi-rough)">{inner}</g>{texts}</svg>'


_FONT_PATH = Path(__file__).resolve().parents[1] / "static" / "fonts" / "PatrickHand-Regular.ttf"


def _hand_font() -> str:
    try:
        font_manager.fontManager.addfont(str(_FONT_PATH))
        return font_manager.FontProperties(fname=str(_FONT_PATH)).get_name()
    except (OSError, RuntimeError, ValueError):
        return "DejaVu Sans"


HAND_FONT = _hand_font()


@on_qiskit_thread
def notebook_circuit_figure(engine, readable: bool = False):
    """Draw the engine's circuit as if sketched in the notebook: wobbly ink
    wires, sticky-note gates, handwritten labels. ``readable`` draws straight
    lines and plain labels instead."""
    gate_names = ["h", "x", "y", "z", "s", "sdg", "t", "tdg", "rx", "ry", "rz", "p", "u", "sx", "id", "measure", "reset"]
    display = {name: (STICKY, TEAL) for name in gate_names}
    display.update({name: (TEAL, PAPER) for name in ("cx", "cz", "swap")})
    style = {
        "backgroundcolor": "none",
        "textcolor": TEAL,
        "linecolor": INK,
        "gatetextcolor": TEAL,
        "gatefacecolor": STICKY,
        "barrierfacecolor": "#e8e2cf",
        "creglinecolor": MUTED,
        "fontsize": 16,
        "subfontsize": 11,
        "displaycolor": display,
    }
    if readable:
        figure = engine.build_circuit().draw("mpl", style=style)
    else:
        with plt.xkcd(scale=0.7, length=150, randomness=1.5):
            plt.rcParams.update({
                "path.effects": [],
                "font.family": HAND_FONT,
                "mathtext.fontset": "custom",
                "mathtext.it": HAND_FONT,
                "mathtext.rm": HAND_FONT,
            })
            figure = engine.build_circuit().draw("mpl", style=style)
    figure.patch.set_alpha(0)
    return figure


def render_circuit(engine) -> None:
    """Show the notebook-style circuit drawing at a size that suits its width."""
    import io

    figure = notebook_circuit_figure(engine, readable=st.session_state.get("reading_mode") == "plain")
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", dpi=160, bbox_inches="tight", transparent=True)
    width_px = int(figure.get_size_inches()[0] * 72)
    plt.close(figure)
    st.image(buffer.getvalue(), width=max(220, min(width_px, 900)))

# Camera for the Bloch sphere: x points toward the viewer (lower left), y right, z up.
_CAM_AZ = math.radians(30)
_CAM_EL = math.radians(18)


# --------------------------------------------------------------------------- basics


def show_html(markup: str) -> None:
    """Render raw HTML/SVG. Lines are stripped so Markdown never sees an indented code block."""
    st.markdown("".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def bloch_vector(state: np.ndarray) -> tuple[float, float, float]:
    """Bloch vector (x, y, z) of a normalized single-qubit state."""
    a, b = complex(state[0]), complex(state[1])
    return (
        float(2 * (a.conjugate() * b).real),
        float(2 * (a.conjugate() * b).imag),
        float(abs(a) ** 2 - abs(b) ** 2),
    )


def state_from_angles(theta: float, phi: float) -> np.ndarray:
    return np.array([math.cos(theta / 2), np.exp(1j * phi) * math.sin(theta / 2)])


def _project(x: float, y: float, z: float) -> tuple[float, float, float]:
    u = -x * math.sin(_CAM_AZ) + y * math.cos(_CAM_AZ)
    depth = x * math.cos(_CAM_AZ) + y * math.sin(_CAM_AZ)
    v = z * math.cos(_CAM_EL) - depth * math.sin(_CAM_EL)
    return u, v, depth


def bloch_svg(x: float, y: float, z: float, size: int = 240, title: str = "", trail: list | None = None,
              axis: tuple[float, float, float] | None = None, axis_labels: tuple[str, str] = ("", "")) -> str:
    """An inline SVG Bloch sphere with the state arrow at (x, y, z)."""
    r = size * 0.36
    cx, cy = size / 2, size / 2 + (8 if title else 0)

    def pt(px: float, py: float, pz: float) -> tuple[float, float, float]:
        u, v, d = _project(px, py, pz)
        return cx + r * u, cy - r * v, d

    parts = [f'<svg viewBox="0 0 {size} {size + (16 if title else 0)}" width="100%" style="max-width:{size}px" role="img" aria-label="Bloch sphere">']
    if title:
        parts.append(f'<text x="{cx}" y="14" text-anchor="middle" font-size="16" font-weight="700" fill="{INK}">{html.escape(title)}</text>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="rgba(255,255,255,.45)" stroke="{INK}" stroke-width="1.6"/>')

    # Equator: solid in front, dashed behind.
    front, back = [], []
    for i in range(73):
        t = 2 * math.pi * i / 72
        sx, sy, d = pt(math.cos(t), math.sin(t), 0)
        (front if d >= 0 else back).append(f"{sx:.1f},{sy:.1f}")
    parts.append(f'<polyline points="{" ".join(back)}" fill="none" stroke="{GRID}" stroke-dasharray="3 3"/>')
    parts.append(f'<polyline points="{" ".join(front)}" fill="none" stroke="{GRID}"/>')

    # Axes and labels.
    for (ax, ay, az), label in (((0, 0, 1), "|0⟩"), ((0, 0, -1), "|1⟩"), ((1, 0, 0), "|+⟩"), ((0, 1, 0), "|+i⟩")):
        ex, ey, _ = pt(ax, ay, az)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{GRID}" stroke-width="1"/>')
        lx, ly, _ = pt(ax * 1.22, ay * 1.22, az * 1.18)
        parts.append(f'<text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle" font-size="15" fill="{MUTED}">{label}</text>')

    if axis is not None:
        ax_, ay_, az_ = axis
        p1x, p1y, _ = pt(ax_ * 1.12, ay_ * 1.12, az_ * 1.12)
        p2x, p2y, _ = pt(-ax_ * 1.12, -ay_ * 1.12, -az_ * 1.12)
        parts.append(f'<line x1="{p1x:.1f}" y1="{p1y:.1f}" x2="{p2x:.1f}" y2="{p2y:.1f}" stroke="{AMBER}" stroke-width="2.2" stroke-dasharray="6 4"/>')
        parts.append(f'<circle cx="{p1x:.1f}" cy="{p1y:.1f}" r="4" fill="{AMBER}"/>')
        parts.append(f'<circle cx="{p2x:.1f}" cy="{p2y:.1f}" r="4" fill="none" stroke="{AMBER}" stroke-width="2"/>')
        q1x, q1y, _ = pt(ax_ * 1.32, ay_ * 1.32, az_ * 1.3)
        q2x, q2y, _ = pt(-ax_ * 1.32, -ay_ * 1.32, -az_ * 1.3)
        parts.append(f'<text x="{q1x:.1f}" y="{q1y + 4:.1f}" text-anchor="middle" font-size="14" font-weight="700" fill="{AMBER}">{html.escape(axis_labels[0])}</text>')
        parts.append(f'<text x="{q2x:.1f}" y="{q2y + 4:.1f}" text-anchor="middle" font-size="14" font-weight="700" fill="{AMBER}">{html.escape(axis_labels[1])}</text>')

    for tx, ty, tz in trail or []:
        px_, py_, _ = pt(tx, ty, tz)
        parts.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="3" fill="{TEAL}" opacity="0.25"/>')

    length = math.sqrt(x * x + y * y + z * z)
    if length > 1e-6:
        sx, sy, _ = pt(x, y, z)
        fx, fy, _ = pt(x, y, 0)
        parts.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{fx:.1f}" y2="{fy:.1f}" stroke="{TEAL}" stroke-dasharray="2 3" opacity="0.6"/>')
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{fx:.1f}" y2="{fy:.1f}" stroke="{TEAL}" stroke-dasharray="2 3" opacity="0.4"/>')
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{TEAL}" stroke-width="3.5" stroke-linecap="round"/>')
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="6" fill="{TEAL}" stroke="#fff" stroke-width="2"/>')
    else:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="{AMBER}"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="2.5" fill="{INK}"/>')
    if length < 0.98:
        parts.append(
            f'<text x="{cx}" y="{size + (16 if title else 0) - 4}" text-anchor="middle" font-size="13" fill="{AMBER}">'
            f"arrow shrunk to {length:.2f} (entangled or noisy)</text>"
        )
    parts.append("</svg>")
    return sketch("".join(parts))


def probability_bars(probabilities: dict[str, float], compare: dict[str, float] | None = None, compare_label: str = "") -> str:
    rows = []
    for label, p in probabilities.items():
        pct = max(0.0, min(100.0, p * 100))
        ghost = ""
        if compare is not None:
            cp = max(0.0, min(100.0, compare.get(label, 0.0) * 100))
            ghost = f'<div class="prob-ghost" style="left:{cp:.2f}%" title="{html.escape(compare_label)}"></div>'
        rows.append(
            f'<div class="prob-row"><div class="prob-label">|{html.escape(label)}⟩</div>'
            f'<div class="prob-track">{ghost}<div class="prob-fill" style="width:{pct:.2f}%"></div></div>'
            f'<div class="prob-value">{p:.1%}</div></div>'
        )
    return "".join(rows)


def render_probabilities(probabilities: dict[str, float], compare: dict[str, float] | None = None, compare_label: str = "") -> None:
    show_html(probability_bars(probabilities, compare, compare_label))
    if compare is not None and compare_label:
        st.caption(f"Bars: current result · thin marker: {compare_label}")


def curve_svg(fn, x_max: float, x_value: float, *, x_label: str, y_label: str, width: int = 320, height: int = 170,
              ticks: list[tuple[float, str]] | None = None, history: list[float] | None = None, y_max: float = 1.0) -> str:
    """Plot y = fn(x) on [0, x_max] with a marker at x_value."""
    left, right, top, bottom = 34, 10, 16, 28
    w, h = width - left - right, height - top - bottom

    def sx(xv: float) -> float:
        return left + w * xv / x_max

    def sy(yv: float) -> float:
        return top + h * (1 - yv / y_max)

    pts = " ".join(f"{sx(x_max * i / 120):.1f},{sy(fn(x_max * i / 120)):.1f}" for i in range(121))
    out = [f'<svg viewBox="0 0 {width} {height}" width="100%" style="max-width:{width}px">']
    out.append(f'<line x1="{left}" y1="{top + h}" x2="{left + w}" y2="{top + h}" stroke="{GRID}"/>')
    out.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + h}" stroke="{GRID}"/>')
    for yv in (0, y_max / 2, y_max):
        out.append(f'<text x="{left - 6}" y="{sy(yv) + 4:.1f}" text-anchor="end" font-size="13" fill="{MUTED}">{yv:g}</text>')
    for xv, label in ticks or []:
        out.append(f'<text x="{sx(xv):.1f}" y="{top + h + 14}" text-anchor="middle" font-size="13" fill="{MUTED}">{label}</text>')
    out.append(f'<text x="{left + w}" y="{height - 2}" text-anchor="end" font-size="13" fill="{MUTED}">{html.escape(x_label)}</text>')
    out.append(f'<text x="{left + 6}" y="{top - 5}" font-size="13" fill="{MUTED}">{html.escape(y_label)}</text>')
    out.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    for hx in history or []:
        out.append(f'<circle cx="{sx(hx):.1f}" cy="{sy(fn(hx)):.1f}" r="3" fill="{AMBER}" opacity="0.45"/>')
    out.append(f'<line x1="{sx(x_value):.1f}" y1="{top}" x2="{sx(x_value):.1f}" y2="{top + h}" stroke="{TEAL}" stroke-dasharray="3 3"/>')
    out.append(f'<circle cx="{sx(x_value):.1f}" cy="{sy(fn(x_value)):.1f}" r="6" fill="{TEAL}" stroke="#fff" stroke-width="2"/>')
    out.append("</svg>")
    return sketch("".join(out))


_PI_TICKS = [(0, "0"), (math.pi / 2, "π/2"), (math.pi, "π"), (3 * math.pi / 2, "3π/2"), (2 * math.pi, "2π")]


def _fmt_amp(a: complex) -> str:
    re, im = (0.0 if abs(a.real) < 5e-4 else a.real), (0.0 if abs(a.imag) < 5e-4 else a.imag)
    if im == 0:
        return f"{re:+.3f}"
    if re == 0:
        return f"{im:+.3f}i"
    return f"{re:+.3f}{im:+.3f}i"


def amplitude_line(state: np.ndarray) -> str:
    return f"|ψ⟩ = ({_fmt_amp(complex(state[0]))})|0⟩ + ({_fmt_amp(complex(state[1]))})|1⟩"


# --------------------------------------------------------------------------- widgets


def bloch_dial(widget: dict, key: str) -> None:
    from frontend.bloch3d import bloch_dial_3d

    bloch_dial_3d(float(widget.get("theta", 0.0)), float(widget.get("phi", 0.0)), bool(widget.get("show_curve")))


_SQ2 = 1 / math.sqrt(2)
SINGLE_QUBIT_GATES = {
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    "H": np.array([[_SQ2, _SQ2], [_SQ2, -_SQ2]], dtype=complex),
    "S": np.array([[1, 0], [0, 1j]], dtype=complex),
    "T": np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], dtype=complex),
}

GATE_BLURBS = {
    "X": "half-turn around x (NOT)",
    "Y": "half-turn around y",
    "Z": "half-turn around z (phase flip)",
    "H": "half-turn around the x+z diagonal",
    "S": "quarter-turn around z",
    "T": "eighth-turn around z",
}


def gate_play(widget: dict, key: str) -> None:
    gates = widget.get("gates", ["X", "H", "Z"])
    seq_key = f"{key}_seq"
    sequence: list[str] = st.session_state.setdefault(seq_key, [])

    cols = st.columns(len(gates) + 1)
    for col, gate in zip(cols, gates):
        with col:
            if st.button(f"Apply {gate}", key=f"{key}_{gate}", use_container_width=True, help=GATE_BLURBS.get(gate)):
                sequence.append(gate)
    with cols[-1]:
        if st.button("Reset to |0⟩", key=f"{key}_reset", use_container_width=True):
            sequence.clear()

    state = np.array([1, 0], dtype=complex)
    trail = [bloch_vector(state)]
    for gate in sequence:
        state = SINGLE_QUBIT_GATES[gate] @ state
        trail.append(bloch_vector(state))

    sphere, readout = st.columns([1, 1.3], gap="large")
    with sphere:
        from frontend.bloch3d import bloch_view_3d

        bloch_view_3d([{"title": "", "vector": trail[-1], "trail": trail[:-1][-8:]}], size=240)
    with readout:
        path = " → ".join(["|0⟩", *sequence]) if sequence else "|0⟩ (no gates yet)"
        st.markdown(f"**Sequence:** `{path}`")
        render_probabilities({"0": float(abs(state[0]) ** 2), "1": float(abs(state[1]) ** 2)})
        st.code(amplitude_line(state), language="text")
        legend = " · ".join(f"**{g}** {GATE_BLURBS[g]}" for g in gates if g in GATE_BLURBS)
        st.caption(legend + ". Faint dots show where the arrow has been.")


def shots(widget: dict, key: str) -> None:
    controls, result = st.columns([1, 1.4], gap="large")
    with controls:
        p1 = st.slider("True P(1)", 0.0, 1.0, float(widget.get("p1", 0.3)), 0.01, key=f"{key}_p1")
        n = st.select_slider("Shots", options=[1, 5, 10, 50, 100, 500, 1000, 10000], value=10, key=f"{key}_n")
        seed_key = f"{key}_seed"
        if st.button("🎲 Re-run the experiment", key=f"{key}_roll", use_container_width=True):
            st.session_state[seed_key] = st.session_state.get(seed_key, 0) + 1
    rng = np.random.default_rng(st.session_state.get(f"{key}_seed", 0) * 7919 + n)
    outcomes = rng.random(n) < p1
    ones = int(outcomes.sum())
    observed = ones / n
    with result:
        st.markdown(f"**{n} shot{'s' if n != 1 else ''}: {n - ones} × 0, {ones} × 1**")
        render_probabilities({"0": 1 - observed, "1": observed}, compare={"0": 1 - p1, "1": p1}, compare_label="true probability")
        typical = math.sqrt(max(p1 * (1 - p1), 1e-12) / n)
        st.caption(f"Observed P(1) = {observed:.3f}. Typical shot-noise error at this size ≈ ±{typical:.3f}.")
        if n <= 50:
            chips = "".join(f'<span class="shot-chip s{int(o)}">{int(o)}</span>' for o in outcomes)
            show_html(f'<div class="shot-strip">{chips}</div>')
        else:
            running = np.cumsum(outcomes) / np.arange(1, n + 1)
            idx = np.unique(np.geomspace(1, n, 120).astype(int)) - 1
            show_html(_running_svg(running[idx], idx + 1, p1, n))


def _running_svg(values: np.ndarray, xs: np.ndarray, target: float, n: int, width: int = 360, height: int = 150) -> str:
    left, right, top, bottom = 34, 10, 8, 26
    w, h = width - left - right, height - top - bottom

    def sx(xv: float) -> float:
        return left + w * math.log10(xv) / max(math.log10(n), 1e-9)

    def sy(yv: float) -> float:
        return top + h * (1 - yv)

    pts = " ".join(f"{sx(x):.1f},{sy(v):.1f}" for x, v in zip(xs, values))
    return sketch(
        f'<svg viewBox="0 0 {width} {height}" width="100%" style="max-width:{width}px">'
        f'<line x1="{left}" y1="{sy(target):.1f}" x2="{left + w}" y2="{sy(target):.1f}" stroke="{TEAL}" stroke-dasharray="4 3"/>'
        f'<line x1="{left}" y1="{top + h}" x2="{left + w}" y2="{top + h}" stroke="{GRID}"/>'
        f'<text x="{left - 6}" y="{sy(0) + 4:.1f}" text-anchor="end" font-size="13" fill="{MUTED}">0</text>'
        f'<text x="{left - 6}" y="{sy(1) + 4:.1f}" text-anchor="end" font-size="13" fill="{MUTED}">1</text>'
        f'<text x="{left + w}" y="{height - 4}" text-anchor="end" font-size="13" fill="{MUTED}">shots (log scale)</text>'
        f'<text x="{left + 4}" y="{top + 10}" font-size="13" fill="{MUTED}">running fraction of 1s</text>'
        f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="1.8"/></svg>'
    )


def _phasor_svg(phi: float, sign: int, label: str, size: int = 150) -> str:
    """Two half-amplitudes added head-to-tail: ½ + sign·½·e^{iφ}."""
    c = size / 2
    s = size * 0.36
    a = complex(0.5, 0)
    b = sign * 0.5 * complex(math.cos(phi), math.sin(phi))
    total = a + b

    def p(z: complex) -> tuple[float, float]:
        return c - s * 0.5 + s * z.real, c - s * z.imag

    ox, oy = p(0)
    ax, ay = p(a)
    tx, ty = p(a + b)
    prob = abs(total) ** 2
    return sketch(
        f'<svg viewBox="0 0 {size} {size + 18}" width="100%" style="max-width:{size}px">'
        f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="{s:.1f}" fill="none" stroke="{GRID}" stroke-dasharray="2 3"/>'
        f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{ax:.1f}" y2="{ay:.1f}" stroke="{BLUE}" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{AMBER}" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{TEAL}" stroke-width="2" stroke-dasharray="4 2"/>'
        f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="4" fill="{TEAL}"/>'
        f'<text x="{c}" y="{size + 12}" text-anchor="middle" font-size="15" fill="{INK}">{html.escape(label)}: P = {prob:.2f}</text>'
        "</svg>"
    )


def interference(widget: dict, key: str) -> None:
    phi_pi = st.slider("Phase shift φ between the two paths (× π)", 0.0, 2.0, float(widget.get("phi", 0.0)), 0.01, key=f"{key}_phi")
    phi = phi_pi * math.pi
    p0 = math.cos(phi / 2) ** 2
    curve, phasors, bars = st.columns([1.3, 1.2, 1], gap="medium")
    with curve:
        show_html(curve_svg(lambda t: math.cos(t / 2) ** 2, 2 * math.pi, phi, x_label="φ", y_label="P(0)", ticks=_PI_TICKS))
    with phasors:
        a, b = st.columns(2)
        with a:
            show_html(_phasor_svg(phi, +1, "|0⟩"))
        with b:
            show_html(_phasor_svg(phi, -1, "|1⟩"))
        st.caption("Blue: path through |0⟩. Amber: path through |1⟩ after the phase shift. Dashed: their sum.")
    with bars:
        render_probabilities({"0": p0, "1": 1 - p0})
        if p0 > 0.995:
            st.success("Paths in step: constructive on |0⟩.")
        elif p0 < 0.005:
            st.warning("Paths cancel on |0⟩: everything lands on |1⟩.")


def bit_order(widget: dict, key: str) -> None:
    n = int(widget.get("qubits", 3))
    cols = st.columns(n + 1)
    bits = []
    for i, col in enumerate(cols[:n]):
        q = n - 1 - i  # show q_{n-1} … q0 left to right, like the string
        with col:
            bits.append((q, st.toggle(f"X on q{q}", key=f"{key}_q{q}")))
    flipped = {q for q, on in bits if on}
    string = "".join("1" if q in flipped else "0" for q, _ in bits)
    digits = "".join(
        f'<div class="bit-cell {"on" if ch == "1" else ""}"><strong>{ch}</strong><small>q{q}</small></div>'
        for (q, _), ch in zip(bits, string)
    )
    show_html(f'<div class="bit-display">{digits}<div class="bit-arrow">← qubit 0 is on the right</div></div>')
    lines = "\n".join(f"qc.x({q})" for q in sorted(flipped)) or "# no gates"
    with cols[-1]:
        st.metric("As a number", int(string, 2))
    st.code(f"qc = QuantumCircuit({n})\n{lines}\n# Qiskit reports: '{string}'", language="python")


def entangle(widget: dict, key: str) -> None:
    seed_key = f"{key}_seed"
    if st.button("🎲 Run 10 more shots", key=f"{key}_roll"):
        st.session_state[seed_key] = st.session_state.get(seed_key, 0) + 1
    rng = np.random.default_rng(st.session_state.get(seed_key, 0) + 11)
    coins = rng.integers(0, 2, size=(10, 2))
    bell = np.repeat(rng.integers(0, 2, size=(10, 1)), 2, axis=1)

    def table(rows: np.ndarray) -> str:
        agree = int(sum(r[0] == r[1] for r in rows))
        cells = "".join(
            f'<div class="pair {"match" if r[0] == r[1] else "miss"}"><span>{r[1]}</span><span>{r[0]}</span></div>' for r in rows
        )
        return f'<div class="pair-grid">{cells}</div><p class="pair-note">q1 q0 agree in {agree}/10 shots</p>'

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("**Two independent coins** — H on each qubit")
        show_html(table(coins))
        st.caption("Each qubit is 50/50 and they agree only by chance.")
    with right:
        st.markdown("**Bell pair** — H on q0, then CNOT")
        show_html(table(bell))
        st.caption("Each qubit alone is still 50/50 — but the pair always agrees.")


def _grover_steps(n_items: int, marked: int, rounds: int) -> list[tuple[str, np.ndarray]]:
    amps = np.full(n_items, 1 / math.sqrt(n_items))
    steps = [("Uniform start (H on every qubit)", amps.copy())]
    for r in range(1, rounds + 1):
        amps[marked] *= -1
        steps.append((f"Round {r}: oracle flips the marked sign", amps.copy()))
        amps = 2 * amps.mean() - amps
        steps.append((f"Round {r}: diffuser reflects about the mean", amps.copy()))
    return steps


def _amplitude_svg(amps: np.ndarray, marked: int, width: int = 520, height: int = 200) -> str:
    n = len(amps)
    left, right, top, bottom = 10, 10, 10, 22
    w, h = width - left - right, height - top - bottom
    mid = top + h / 2
    bw = w / n
    out = [f'<svg viewBox="0 0 {width} {height}" width="100%" style="max-width:{width}px">']
    out.append(f'<line x1="{left}" y1="{mid}" x2="{left + w}" y2="{mid}" stroke="{GRID}"/>')
    for i, a in enumerate(amps):
        bh = (h / 2) * float(a)
        y = mid - max(bh, 0)
        color = AMBER if i == marked else BLUE
        out.append(f'<rect x="{left + i * bw + bw * 0.15:.1f}" y="{y:.1f}" width="{bw * 0.7:.1f}" height="{abs(bh):.1f}" fill="{color}" rx="2"/>')
    mean = float(amps.mean())
    my = mid - (h / 2) * mean
    out.append(f'<line x1="{left}" y1="{my:.1f}" x2="{left + w}" y2="{my:.1f}" stroke="{TEAL}" stroke-dasharray="5 3"/>')
    out.append(f'<text x="{left + w}" y="{my - 4:.1f}" text-anchor="end" font-size="13" fill="{TEAL}">mean</text>')
    out.append(f'<text x="{left}" y="{height - 4}" font-size="13" fill="{MUTED}">amplitude of each item (amber = marked); above line = +, below = −</text>')
    out.append("</svg>")
    return sketch("".join(out))


def grover(widget: dict, key: str) -> None:
    c1, c2 = st.columns([1, 1])
    with c1:
        n_items = st.select_slider("Items to search (N)", options=[4, 8, 16, 32, 64], value=8, key=f"{key}_n")
    with c2:
        marked = st.number_input("Marked item", 0, n_items - 1, min(5, n_items - 1), key=f"{key}_m")
    optimal = max(1, round(math.pi / 4 * math.sqrt(n_items) - 0.5))
    steps = _grover_steps(n_items, int(marked), optimal + 2)
    step = st.slider("Step through the algorithm", 0, len(steps) - 1, 0, key=f"{key}_step")
    label, amps = steps[step]
    p_marked = float(amps[int(marked)] ** 2)
    st.markdown(f"**{label}** — chance of measuring the marked item: **{p_marked:.0%}** (random guess: {1 / n_items:.0%})")
    show_html(_amplitude_svg(amps, int(marked)))
    st.caption(f"Best number of rounds for N = {n_items}: about π/4·√N ≈ {optimal}. Go past it and the probability starts to fall again.")


BASES = {
    "Z (the usual one)": ((0.0, 0.0, 1.0), ("0", "1"), "qc.measure_all()"),
    "X": ((1.0, 0.0, 0.0), ("+", "−"), "qc.h(0)\nqc.measure_all()"),
    "Y": ((0.0, 1.0, 0.0), ("+i", "−i"), "qc.sdg(0)\nqc.h(0)\nqc.measure_all()"),
}


def basis_measure(widget: dict, key: str) -> None:
    controls, sphere, readout = st.columns([1, 1.1, 1.2], gap="large")
    with controls:
        theta_pi = st.slider("Tilt θ (× π)", 0.0, 1.0, float(widget.get("theta", 0.5)), 0.01, key=f"{key}_theta")
        phi_pi = st.slider("Spin φ (× π)", 0.0, 2.0, float(widget.get("phi", 0.0)), 0.01, key=f"{key}_phi")
        basis = st.radio("Measure along", list(BASES), key=f"{key}_basis", horizontal=False)
    axis, labels, code = BASES[basis]
    vector = bloch_vector(state_from_angles(theta_pi * math.pi, phi_pi * math.pi))
    along = sum(a * b for a, b in zip(axis, vector))
    p_plus = (1 + along) / 2
    with sphere:
        show_html(bloch_svg(*vector, axis=axis, axis_labels=labels))
    with readout:
        st.markdown(f"**Measuring along {basis.split()[0]}**")
        render_probabilities({labels[0]: p_plus, labels[1]: 1 - p_plus})
        st.caption("The odds depend only on how close the arrow is to each end of the red axis.")
        st.code(f"# rotate the {basis.split()[0]} axis onto Z, then measure\n{code}", language="python")


def teleport(widget: dict, key: str) -> None:
    controls, alice, bob = st.columns([1.1, 1, 1], gap="medium")
    with controls:
        theta_pi = st.slider("Alice's state: tilt θ (× π)", 0.0, 1.0, 0.35, 0.01, key=f"{key}_theta")
        phi_pi = st.slider("Alice's state: spin φ (× π)", 0.0, 2.0, 0.5, 0.01, key=f"{key}_phi")
        outcome = st.radio(
            "Alice's two measurement results (each 25% likely)",
            ["00", "01", "10", "11"],
            horizontal=True,
            key=f"{key}_outcome",
        )
        fixed = st.toggle("Bob applies the corrections", value=False, key=f"{key}_fix")
    psi = state_from_angles(theta_pi * math.pi, phi_pi * math.pi)
    m_z, m_x = int(outcome[0]), int(outcome[1])  # q0 result -> Z fix, q1 result -> X fix
    received = psi.copy()
    if m_z:
        received = SINGLE_QUBIT_GATES["Z"] @ received
    if m_x:
        received = SINGLE_QUBIT_GATES["X"] @ received
    shown = psi if fixed else received
    with alice:
        show_html(bloch_svg(*bloch_vector(psi), size=210, title="Alice's qubit (to send)"))
    with bob:
        show_html(bloch_svg(*bloch_vector(shown), size=210, title="Bob's qubit"))
    fixes = [name for flag, name in ((m_x, "X"), (m_z, "Z")) if flag]
    if fixed:
        st.success(f"Bob applied {' then '.join(fixes) if fixes else 'nothing'} — his arrow now matches Alice's original exactly.")
    else:
        st.info(
            f"Alice phoned Bob: \"{outcome}\". Until he acts on it, his qubit is "
            + ("already right (lucky 00)." if not fixes else f"off by {' and '.join(fixes)}.")
        )
    st.caption("Alice's own qubit ends up measured and destroyed — the state moved, it wasn't copied.")


ORACLES = {
    "f(x) = 0  (constant)": (0, 0, ""),
    "f(x) = 1  (constant)": (1, 1, "qc.x(1)"),
    "f(x) = x  (balanced)": (0, 1, "qc.cx(0, 1)"),
    "f(x) = NOT x  (balanced)": (1, 0, "qc.cx(0, 1)\nqc.x(1)"),
}


def deutsch(widget: dict, key: str) -> None:
    choice = st.radio("Pick the hidden function inside the black box", list(ORACLES), horizontal=True, key=f"{key}_f")
    f0, f1, oracle_code = ORACLES[choice]
    kind = "constant" if f0 == f1 else "balanced"
    classical, quantum = st.columns(2, gap="large")
    with classical:
        st.markdown("**Classically** — you must ask twice")
        show_html(
            f'<div class="bit-display"><div class="bit-cell"><strong>{f0}</strong><small>f(0)</small></div>'
            f'<div class="bit-cell"><strong>{f1}</strong><small>f(1)</small></div>'
            f'<div class="bit-arrow">→ {kind}, after 2 queries</div></div>'
        )
    # q0 after the oracle acting on |+>|->: phase kickback puts (-1)^f(x) on each branch.
    sign0, sign1 = (-1) ** f0, (-1) ** f1
    after = np.array([sign0, sign1]) / math.sqrt(2)
    p1 = float(abs((after[0] - after[1]) / math.sqrt(2)) ** 2)
    with quantum:
        st.markdown("**Quantum** — one query, thanks to phase kickback")
        left, right = st.columns([1, 1.2])
        with left:
            show_html(bloch_svg(*bloch_vector(after), size=170, title="q0 after the oracle"))
        with right:
            render_probabilities({"0": 1 - p1, "1": p1})
            st.markdown(f"Measured **{int(round(p1))}** → **{kind}**, after 1 query")
    st.caption("The oracle's answer lands as a phase on q0 — |+⟩ for constant, |−⟩ for balanced — and the final H reads it out.")
    st.code(f"# oracle for {choice.split('(')[0].strip()}\n{oracle_code or '# (does nothing)'}", language="python")


ROUTING_CIRCUITS = {
    "Bell pair on neighbours (q0, q1)": [("h", 0), ("cx", 0, 1)],
    "CNOT between far-apart qubits (q0 → q3)": [("h", 0), ("cx", 0, 3)],
    "Star: q0 talks to everyone": [("h", 0), ("cx", 0, 1), ("cx", 0, 2), ("cx", 0, 3)],
}


@st.cache_data(show_spinner=False)
@on_qiskit_thread
def _route(circuit_name: str, topology: str) -> dict:
    from qiskit import QuantumCircuit, transpile
    from qiskit.transpiler import CouplingMap

    qc = QuantumCircuit(4)
    for op in ROUTING_CIRCUITS[circuit_name]:
        getattr(qc, op[0])(*op[1:])
    coupling = CouplingMap.from_line(4) if topology.startswith("Line") else CouplingMap.from_full(4)
    native = transpile(
        qc, coupling_map=coupling, basis_gates=["rz", "sx", "x", "cx"],
        initial_layout=[0, 1, 2, 3], optimization_level=1, seed_transpiler=7,
    )
    ops = dict(native.count_ops())
    return {
        "before": qc.draw(output="text", fold=-1).single_string(),
        "after": native.draw(output="text", fold=-1, idle_wires=False).single_string(),
        "cx_before": dict(qc.count_ops()).get("cx", 0),
        "cx_after": ops.get("cx", 0),
        "depth_before": qc.depth(),
        "depth_after": native.depth(),
    }


def routing(widget: dict, key: str) -> None:
    left, right = st.columns(2)
    with left:
        circuit_name = st.selectbox("Circuit", list(ROUTING_CIRCUITS), index=1, key=f"{key}_c")
    with right:
        topology = st.radio("Chip wiring", ["Line: q0–q1–q2–q3", "Every qubit connected"], key=f"{key}_t", horizontal=True)
    result = _route(circuit_name, topology)
    extra = result["cx_after"] - result["cx_before"]
    show_html(
        '<div class="metric-row">'
        f'<div><div class="metric-label">CNOTs you wrote</div><div class="metric-value">{result["cx_before"]}</div></div>'
        f'<div><div class="metric-label">CNOTs the chip runs</div><div class="metric-value">{result["cx_after"]}</div></div>'
        f'<div><div class="metric-label">Depth</div><div class="metric-value">{result["depth_before"]} → {result["depth_after"]}</div></div>'
        "</div>"
    )
    if extra > 0:
        st.warning(f"{extra} extra CNOTs were inserted to move qubits next to each other (SWAPs). Each one adds noise.")
    else:
        st.success("No extra CNOTs needed — the qubits that interact are already neighbours.")
    st.code("What you wrote:\n" + result["before"] + "\n\nWhat the chip runs:\n" + result["after"], language="text")


def noise(widget: dict, key: str) -> None:
    lam = st.slider("Depolarizing noise λ", 0.0, 0.6, 0.1, 0.01, key=f"{key}_lam",
                    help="Probability that the state is replaced by pure randomness")
    ideal = {"00": 0.5, "01": 0.0, "10": 0.0, "11": 0.5}
    noisy = {k: (1 - lam) * v + lam / 4 for k, v in ideal.items()}
    sphere, bars = st.columns([1, 1.4], gap="large")
    with sphere:
        show_html(bloch_svg(1 - lam, 0, 0, title="|+⟩ after noise"))
    with bars:
        st.markdown("**Bell experiment with noise**")
        render_probabilities(noisy, compare=ideal, compare_label="ideal simulation")
        st.caption(f"{noisy['01'] + noisy['10']:.0%} of shots land on outcomes the ideal circuit forbids.")


def variational(widget: dict, key: str) -> None:
    def p1(t: float) -> float:
        return math.sin(t / 2) ** 2

    target = st.slider("Target P(1)", 0.0, 1.0, 0.8, 0.01, key=f"{key}_target")
    theta_key, hist_key = f"{key}_theta_val", f"{key}_hist"
    theta = float(st.session_state.setdefault(theta_key, 0.3))
    history: list[float] = st.session_state.setdefault(hist_key, [])

    def cost(t: float) -> float:
        return (p1(t) - target) ** 2

    def step_once(t: float) -> float:
        dp = (p1(t + math.pi / 2) - p1(t - math.pi / 2)) / 2  # parameter-shift rule
        grad = 2 * (p1(t) - target) * dp
        return float(min(max(t - 2.0 * grad, 0.0), 2 * math.pi))

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Train 1 step", key=f"{key}_s1", use_container_width=True):
            history.append(theta)
            theta = step_once(theta)
    with b2:
        if st.button("Train 10 steps", key=f"{key}_s10", use_container_width=True):
            for _ in range(10):
                history.append(theta)
                theta = step_once(theta)
    with b3:
        if st.button("Reset", key=f"{key}_reset", use_container_width=True):
            theta, history[:] = 0.3, []
    st.session_state[theta_key] = theta

    landscape, sphere, bars = st.columns([1.4, 1, 1.1], gap="medium")
    with landscape:
        show_html(curve_svg(cost, 2 * math.pi, theta, x_label="θ", y_label="cost", ticks=_PI_TICKS,
                            history=history[-15:], y_max=max(target, 1 - target) ** 2 + 1e-9))
        st.caption(f"Steps taken: {len(history)} · cost {cost(theta):.4f}")
    with sphere:
        show_html(bloch_svg(*bloch_vector(state_from_angles(theta, 0.0)), size=200))
    with bars:
        render_probabilities({"0": 1 - p1(theta), "1": p1(theta)}, compare={"0": 1 - target, "1": target}, compare_label="target")
        st.caption(f"θ = {theta:.3f} rad")


WIDGETS = {
    "bloch_dial": bloch_dial,
    "gate_play": gate_play,
    "shots": shots,
    "interference": interference,
    "bit_order": bit_order,
    "entangle": entangle,
    "grover": grover,
    "noise": noise,
    "variational": variational,
    "basis_measure": basis_measure,
    "teleport": teleport,
    "deutsch": deutsch,
    "routing": routing,
}


def render_widget(widget: dict | None, key: str) -> None:
    if not widget or widget.get("type") not in WIDGETS:
        return
    WIDGETS[widget["type"]](widget, key)
    if widget.get("caption"):
        st.caption(widget["caption"])
