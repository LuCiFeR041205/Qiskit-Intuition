import streamlit.components.v1 as components
import json
import math


def render_circuit_composer(gates: list, num_qubits: int) -> None:
    """
    Renders a holographic-style visual circuit timeline.
    Gates are displayed as colored chips on qubit wires.
    """
    gate_colors = {
        "H": "#65f4d4",
        "X": "#ff6f91",
        "Y": "#ff6f91",
        "Z": "#f6c85f",
        "S": "#f6c85f",
        "T": "#f6c85f",
        "RX": "#a7a2ff",
        "RY": "#a7a2ff",
        "RZ": "#a7a2ff",
        "CNOT": "#e9fff9",
    }

    max_steps = max(len(gates) + 3, 8)
    wire_y_start = 70
    wire_spacing = 60
    step_width = 72
    left_margin = 60
    chip_w = 52
    chip_h = 34

    canvas_w = left_margin + max_steps * step_width + 40
    canvas_h = wire_y_start + num_qubits * wire_spacing + 40
    component_h = max(canvas_h + 20, 180)

    # Build gate chip SVG elements
    gate_chips_svg = ""
    cnot_lines_svg = ""

    for step_idx, g in enumerate(gates):
        gate_name = g["gate"]
        target = g["target"]
        control = g.get("control")
        angle = g.get("angle")
        color = gate_colors.get(gate_name, "#e9fff9")

        cx = left_margin + step_idx * step_width + step_width // 2
        cy = wire_y_start + target * wire_spacing

        # Gate chip rectangle
        gate_chips_svg += f'''
        <rect x="{cx - chip_w//2}" y="{cy - chip_h//2}" width="{chip_w}" height="{chip_h}"
              rx="6" fill="rgba(10,26,25,0.9)" stroke="{color}" stroke-width="1.5"
              filter="url(#glow-{gate_name})"/>
        <text x="{cx}" y="{cy + 1}" text-anchor="middle" dominant-baseline="middle"
              fill="{color}" font-family="'JetBrains Mono',monospace" font-size="13" font-weight="700">
            {gate_name}
        </text>
        '''

        # Angle label for parameterized gates
        if gate_name in ("RX", "RY", "RZ") and angle is not None:
            angle_display = f"{float(angle)/math.pi:.2f}π"
            gate_chips_svg += f'''
            <text x="{cx}" y="{cy + chip_h//2 + 14}" text-anchor="middle"
                  fill="{color}" font-family="'JetBrains Mono',monospace" font-size="9" opacity="0.7">
                {angle_display}
            </text>
            '''

        # CNOT connecting line
        if gate_name == "CNOT" and control is not None:
            cy_ctrl = wire_y_start + control * wire_spacing
            cnot_lines_svg += f'''
            <line x1="{cx}" y1="{cy_ctrl}" x2="{cx}" y2="{cy}"
                  stroke="{color}" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.6"/>
            <circle cx="{cx}" cy="{cy_ctrl}" r="6" fill="{color}" opacity="0.9"/>
            <circle cx="{cx}" cy="{cy}" r="10" fill="none" stroke="{color}" stroke-width="1.5"/>
            <line x1="{cx - 6}" y1="{cy}" x2="{cx + 6}" y2="{cy}" stroke="{color}" stroke-width="1.5"/>
            <line x1="{cx}" y1="{cy - 6}" x2="{cx}" y2="{cy + 6}" stroke="{color}" stroke-width="1.5"/>
            '''

    # Build qubit wire lines
    wires_svg = ""
    for q in range(num_qubits):
        y = wire_y_start + q * wire_spacing
        wires_svg += f'''
        <line x1="{left_margin - 10}" y1="{y}" x2="{canvas_w - 20}" y2="{y}"
              stroke="rgba(101,244,212,0.2)" stroke-width="1"/>
        <text x="12" y="{y + 1}" fill="#65f4d4" font-family="'JetBrains Mono',monospace"
              font-size="12" font-weight="700" dominant-baseline="middle">q{q}</text>
        '''

    # Empty slot indicators
    empty_slots_svg = ""
    for step_idx in range(len(gates), max_steps):
        for q in range(num_qubits):
            cx = left_margin + step_idx * step_width + step_width // 2
            cy = wire_y_start + q * wire_spacing
            empty_slots_svg += f'''
            <circle cx="{cx}" cy="{cy}" r="4" fill="none"
                    stroke="rgba(101,244,212,0.12)" stroke-width="1" stroke-dasharray="2,2"/>
            '''

    # Time step labels
    time_labels_svg = ""
    for step_idx in range(max_steps):
        cx = left_margin + step_idx * step_width + step_width // 2
        time_labels_svg += f'''
        <text x="{cx}" y="20" text-anchor="middle" fill="rgba(141,184,176,0.5)"
              font-family="'JetBrains Mono',monospace" font-size="9">t{step_idx}</text>
        '''

    # Glow filters
    glow_filters = ""
    for name, color in gate_colors.items():
        glow_filters += f'''
        <filter id="glow-{name}" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feFlood flood-color="{color}" flood-opacity="0.3"/>
            <feComposite in2="blur" operator="in"/>
            <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        '''

    html = f'''<!DOCTYPE html>
<html><head>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  body {{ margin:0; padding:0; overflow:hidden; background:transparent; }}
  .composer-wrap {{
    position:relative;
    background: linear-gradient(145deg, rgba(10,26,25,0.95), rgba(17,21,34,0.85));
    border: 1px solid rgba(101,244,212,0.2);
    border-radius: 8px;
    padding: 8px;
    box-shadow: 0 18px 50px rgba(0,0,0,0.3);
  }}
  .hud-c {{ position:absolute; width:8px; height:8px; border-color:#65f4d4; border-style:solid; pointer-events:none; }}
  .tl {{ top:4px; left:4px; border-width:2px 0 0 2px; }}
  .tr {{ top:4px; right:4px; border-width:2px 2px 0 0; }}
  .bl {{ bottom:4px; left:4px; border-width:0 0 2px 2px; }}
  .br {{ bottom:4px; right:4px; border-width:0 2px 2px 0; }}
  .badge {{
    position:absolute; top:8px; right:14px;
    font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700;
    color:#65f4d4; letter-spacing:0.1em; text-transform:uppercase;
    border:1px solid rgba(101,244,212,0.3); padding:2px 8px; border-radius:3px;
    background:rgba(101,244,212,0.06);
  }}
</style>
</head><body>
<div class="composer-wrap">
  <div class="hud-c tl"></div><div class="hud-c tr"></div>
  <div class="hud-c bl"></div><div class="hud-c br"></div>
  <div class="badge">CIRCUIT</div>
  <svg width="{canvas_w}" height="{canvas_h}" xmlns="http://www.w3.org/2000/svg">
    <defs>{glow_filters}</defs>
    {time_labels_svg}
    {wires_svg}
    {empty_slots_svg}
    {cnot_lines_svg}
    {gate_chips_svg}
  </svg>
</div>
</body></html>'''

    components.html(html, height=component_h, scrolling=True)
