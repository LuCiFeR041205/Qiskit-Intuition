import streamlit as st

def inject_theme():
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

    @keyframes pulse-animation {
        0% { opacity: 0.4; }
        50% { opacity: 1; }
        100% { opacity: 0.4; }
    }
    .pulse-dot {
        animation: pulse-animation 2s infinite ease-in-out;
    }

    :root {
        --lab-bg: #07110f;
        --panel: rgba(12, 30, 28, 0.78);
        --panel-2: rgba(17, 37, 42, 0.72);
        --line: rgba(111, 225, 205, 0.26);
        --line-strong: rgba(111, 225, 205, 0.52);
        --text: #ffffff;
        --muted: #a6d0c6;
        --cyan: #65f4d4;
        --gold: #f6c85f;
        --rose: #ff6f91;
        --violet: #a7a2ff;
    }

    /* Accessibility improvements: clear focus indicators */
    *:focus-visible {
        outline: 2px solid var(--cyan) !important;
        outline-offset: 2px !important;
    }

    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at 50% 0%, rgba(101, 244, 212, 0.1) 0%, transparent 50%),
            repeating-linear-gradient(90deg, rgba(101, 244, 212, 0.035) 0 1px, transparent 1px 86px),
            repeating-linear-gradient(0deg, rgba(246, 200, 95, 0.028) 0 1px, transparent 1px 86px),
            linear-gradient(135deg, #050a0a 0%, #0a111a 45%, #100b1a 100%);
        font-family: 'Space Grotesk', Inter, ui-sans-serif, system-ui, sans-serif;
    }
    
    @keyframes hologram-glitch {
        0% { opacity: 0.8; transform: translateX(0); }
        5% { opacity: 1; transform: translateX(1px); filter: drop-shadow(0 0 5px var(--cyan)); }
        10% { opacity: 0.8; transform: translateX(-1px); filter: none; }
        100% { opacity: 0.8; transform: translateX(0); }
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1480px;
    }

    [data-testid="stHeader"] {
        background: transparent;
        padding: 0.5rem 1rem;
        border-bottom: none;}

    /* Hide Streamlit's top-right app chrome, including the theme menu. */
    [data-testid="stToolbar"],
    [data-testid="stHeaderActionElements"],
    [data-testid="stDeployButton"],
    [data-testid="stMainMenu"],
    [data-testid="stMainMenuButton"],
    [data-testid="stBaseButton-header"],
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
    

    [data-testid="stSidebar"] {
        background: rgba(6, 15, 15, 0.96);
        border-right: 1px solid var(--line);
    }

    h1, h2, h3 {
        color: var(--text) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.01em;
        text-shadow: 0 0 15px rgba(101, 244, 212, 0.2);
    }

    p, li, label, div, span {
        color: var(--text);
    }

    /* ── Physics cards ── */
    .lab-hero {
        border: 1px solid var(--line);
        background:
            linear-gradient(145deg, rgba(10, 27, 25, 0.94), rgba(28, 23, 48, 0.86)),
            repeating-linear-gradient(90deg, rgba(101, 244, 212, 0.08) 0 1px, transparent 1px 48px);
        border-radius: 8px;
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.25);
    }

    .physics-card, .gate-card, .timeline-row {
        border: 1px solid var(--line);
        border-radius: 8px;
        background:
            linear-gradient(145deg, rgba(18, 39, 37, 0.86), rgba(17, 21, 34, 0.78)),
            repeating-linear-gradient(135deg, rgba(255, 255, 255, 0.025) 0 1px, transparent 1px 12px);
        padding: 14px;
        box-shadow:
            0 18px 38px rgba(0, 0, 0, 0.26),
            inset 0 1px 0 rgba(255, 255, 255, 0.06);
        transition: border-color 200ms ease, transform 200ms ease, box-shadow 200ms ease;
    }

    .physics-card:hover, .gate-card:hover {
        border-color: var(--line-strong);
        transform: translateY(-2px);
        box-shadow:
            0 22px 44px rgba(0, 0, 0, 0.31),
            0 0 20px rgba(101, 244, 212, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }

    .physics-card strong, .gate-card strong { color: var(--cyan); }
    .physics-card span, .gate-card span { color: var(--muted); font-size: 0.9rem; }
    .gate-card { min-height: 120px; }
    .compact-card {
        padding: 10px 12px !important;
        margin-bottom: 10px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.2) !important;
    }

    /* ── Metric strip ── */
    .metric-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin: 14px 0 20px 0;
    }

    /* ── Timeline rows ── */
    .timeline-row {
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
    }

    .timeline-chip {
        border: 1px solid var(--line-strong);
        border-radius: 999px;
        padding: 4px 10px;
        color: var(--gold);
        white-space: nowrap;
        font-size: 0.82rem;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── Compact learning selector ── */
    .learning-console {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        border: 1px solid rgba(111, 225, 205, 0.34);
        border-radius: 8px;
        padding: 14px 16px;
        margin: 4px 0 10px 0;
        background:
            linear-gradient(145deg, rgba(12, 30, 28, 0.92), rgba(15, 18, 31, 0.82));
        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.24);
    }

    .learning-console h3 {
        margin: 2px 0 4px 0 !important;
        font-size: 1.18rem !important;
        line-height: 1.15 !important;
        text-shadow: none !important;
    }

    .learning-console p {
        margin: 0 !important;
        color: var(--muted) !important;
        font-size: 0.86rem;
        line-height: 1.35;
    }

    .console-eyebrow {
        display: block;
        color: var(--gold) !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        margin-bottom: 2px;
    }

    /* ── Roadmap ── */
    .roadmap {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: 14px 0 24px 0;
    }

    .roadmap-step {
        position: relative;
        min-height: 120px;
        border: 1px solid rgba(111, 225, 205, 0.4);
        border-radius: 8px;
        padding: 14px;
        background: linear-gradient(145deg, rgba(14, 33, 31, 0.8), rgba(23, 20, 39, 0.7));
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.3), 0 0 15px rgba(101, 244, 212, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: border-color 200ms ease, transform 200ms ease, box-shadow 200ms ease;
    }

    .roadmap-step:hover {
        border-color: var(--line-strong);
        transform: translateY(-2px);
    }

    .roadmap-step strong { color: var(--gold); display: block; font-size: 0.92rem; margin-bottom: 8px; }
    .roadmap-step span { color: var(--muted); font-size: 0.86rem; line-height: 1.45; }

    /* ── Clickable foundation boxes ── */
    [data-testid="stExpander"] {
        border: 1px solid rgba(111, 225, 205, 0.34) !important;
        border-radius: 8px !important;
        background: linear-gradient(145deg, rgba(14, 33, 31, 0.78), rgba(23, 20, 39, 0.72)) !important;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.22), 0 0 14px rgba(101, 244, 212, 0.08);
        overflow: hidden;
    }

    [data-testid="stExpander"] summary {
        color: var(--gold) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700;
    }

    [data-testid="stExpander"] summary:hover {
        color: var(--cyan) !important;
    }

    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        color: var(--text) !important;
    }

    /* ── Study materials ── */
    .study-access {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin: 14px 0 18px 0;
    }

    .study-access-item {
        border: 1px solid var(--line);
        border-left: 3px solid var(--cyan);
        border-radius: 8px;
        padding: 12px;
        background: rgba(10, 27, 25, 0.62);
        min-height: 92px;
    }

    .study-access-item strong {
        color: var(--cyan);
        display: block;
        font-size: 0.88rem;
        margin-bottom: 6px;
    }

    .study-access-item span {
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.4;
    }

    /* ── Buttons ── */
    .stButton > button,
    .stButton button,
    button[kind],
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-secondary"] {
        border-radius: 6px;
        border: 1px solid var(--line-strong) !important;
        background: #050a0a !important;
        color: var(--text) !important;
        min-height: 2.25rem;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 500;
        font-size: 0.88rem;
        transition: all 200ms ease;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
    }

    .stButton > button:hover,
    .stButton button:hover,
    button[kind]:hover,
    [data-testid="baseButton-primary"]:hover,
    [data-testid="baseButton-secondary"]:hover {
        border-color: var(--cyan) !important;
        background: rgba(101, 244, 212, 0.16) !important;
        color: #fff !important;
        box-shadow: 0 0 20px rgba(101, 244, 212, 0.28) !important;
        transform: scale(1.02);
    }

    .stButton > button:disabled,
    .stButton > button:disabled:hover,
    .stButton button:disabled,
    .stButton button:disabled:hover,
    button[kind]:disabled,
    button[kind]:disabled:hover {
        background: #080e14 !important;
        color: rgba(255, 255, 255, 0.48) !important;
        border-color: rgba(111, 225, 205, 0.18) !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* ── Streamlit/BaseWeb inputs ── */
    [data-baseweb="select"] > div,
    [data-baseweb="select"] input,
    [data-baseweb="select"] [role="combobox"] {
        background: #080e14 !important;
    }

    [data-baseweb="select"] > div {
        border-color: var(--line) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #080e14 !important;
        border-color: var(--line) !important;
    }

    [role="option"],
    [data-baseweb="menu"] li {
        background: #080e14 !important;
    }

    [role="option"]:hover,
    [data-baseweb="menu"] li:hover {
        background: rgba(101, 244, 212, 0.16) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid var(--line);
        margin-bottom: 0.6rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        color: var(--muted);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        letter-spacing: 0.02em;
        transition: color 200ms ease;
    }

    .stTabs [aria-selected="true"] {
        color: var(--cyan) !important;
        border-bottom: 2px solid var(--cyan);
    }

    /* ── Code blocks ── */
    .stCodeBlock, .stTextArea textarea {
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stCodeBlock,
    .stCodeBlock div,
    .stCodeBlock pre,
    .stCodeBlock code,
    [data-testid="stCode"],
    [data-testid="stCode"] *,
    [data-testid="stCodeBlock"],
    [data-testid="stCodeBlock"] *,
    [data-testid="stCodeBlock"] div,
    [data-testid="stCodeBlock"] pre,
    [data-testid="stCodeBlock"] code {
        background: var(--panel) !important;
    }

    .stTextArea textarea {
        background: #000000 !important;
        color: var(--text) !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
    }

    /* ── Chat messages ── */
    [data-testid="stChatMessage"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        background:
            linear-gradient(145deg, rgba(12, 28, 26, 0.9), rgba(17, 18, 30, 0.85)) !important;
        margin-bottom: 8px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }

    /* ── Custom progress bars ── */
    .neon-bar-wrap {
        background: rgba(10, 20, 18, 0.8);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 3px;
        margin: 4px 0;
    }

    .neon-bar {
        height: 22px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        padding: 0 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        color: #0a1a19;
        transition: width 400ms cubic-bezier(0.4, 0, 0.2, 1);
    }

    .neon-bar-cyan {
        background: linear-gradient(90deg, #65f4d4, #4db8a0);
        box-shadow: 0 0 12px rgba(101, 244, 212, 0.4);
    }

    /* ── Preset chips ── */
    .preset-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0 16px 0;
    }

    .preset-chip {
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 6px 16px;
        background: rgba(101, 244, 212, 0.06);
        color: var(--cyan);
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 200ms ease;
    }

    .preset-chip:hover {
        border-color: var(--cyan);
        background: rgba(101, 244, 212, 0.14);
        box-shadow: 0 0 14px rgba(101, 244, 212, 0.15);
    }

    /* ── Lab shell ── */
    .lab-shell {
        border: 1px solid rgba(111, 225, 205, 0.24);
        border-radius: 8px;
        padding: 16px;
        background:
            linear-gradient(160deg, rgba(9, 24, 23, 0.86), rgba(19, 18, 33, 0.72)),
            repeating-linear-gradient(90deg, rgba(111, 225, 205, 0.035) 0 1px, transparent 1px 36px);
        box-shadow: 0 28px 80px rgba(0, 0, 0, 0.34);
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: rgba(7, 17, 15, 0.5); }
    ::-webkit-scrollbar-thumb {
        background: rgba(101, 244, 212, 0.25);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(101, 244, 212, 0.4); }

    /* ── Responsive ── */
    @media (max-width: 900px) {
        .metric-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .roadmap { grid-template-columns: 1fr; }
        .learning-console { align-items: flex-start; flex-direction: column; }
    }
</style>
        """,
        unsafe_allow_html=True,
    )
