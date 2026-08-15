"""Visual system for the public educational app."""

import streamlit as st


def inject_education_theme() -> None:
    st.markdown(
        """
<style>
:root {
  --navy: #17212b;
  --navy-2: #243342;
  --teal: #087f8c;
  --teal-soft: #e4f2f3;
  --blue: #3169a8;
  --amber: #ad6500;
  --paper: #ffffff;
  --canvas: #f4f6f8;
  --line: #dce2e7;
  --muted: #5d6a75;
  --shadow-sm: 0 1px 2px rgba(23, 33, 43, 0.06), 0 6px 18px rgba(23, 33, 43, 0.035);
  --shadow-md: 0 10px 28px rgba(23, 33, 43, 0.10), 0 2px 6px rgba(23, 33, 43, 0.06);
}

html, body, [class*="css"] {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--navy);
}

.stApp {
  background:
    radial-gradient(circle at 82% -12%, rgba(8, 127, 140, 0.08), transparent 30rem),
    var(--canvas);
}

[data-testid="stHeader"] {
  background: rgba(244, 246, 248, 0.92);
  border-bottom: 1px solid rgba(220, 226, 231, 0.8);
}

[data-testid="stAppViewContainer"] > .main .block-container {
  max-width: 1180px;
  padding-top: 2rem;
  padding-bottom: 5rem;
}

[data-testid="stSidebar"] {
  background: var(--navy);
  border-right: 0;
}

[data-testid="stSidebar"] * {
  color: #eef4f6;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label p {
  color: #c9d3da !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
  min-height: 2.75rem;
  border-radius: 10px;
  padding: 0.5rem 0.65rem;
  transition: background 150ms ease, transform 150ms ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: rgba(255,255,255,0.08);
  transform: translateX(2px);
}

[data-testid="stSidebar"] hr {
  border-color: rgba(255,255,255,0.13);
}

h1, h2, h3 {
  color: var(--navy) !important;
  letter-spacing: -0.025em;
}

h1 { font-size: clamp(2rem, 4vw, 3.1rem) !important; line-height: 1.06 !important; }
h2 { font-size: 1.65rem !important; margin-top: 2rem !important; }
h3 { font-size: 1.12rem !important; }

p, li {
  line-height: 1.65;
}

.brand {
  padding: 0.4rem 0 1.2rem;
}

.brand-mark {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(145deg, #18a5b2, var(--teal));
  color: white;
  font-weight: 800;
  margin-bottom: 0.75rem;
  box-shadow: 0 8px 22px rgba(8, 127, 140, 0.32), inset 0 1px rgba(255,255,255,0.25);
}

.brand-name {
  color: white;
  font-size: 1.05rem;
  font-weight: 750;
  letter-spacing: -0.01em;
}

.brand-subtitle {
  color: #aebdc6;
  font-size: 0.78rem;
  margin-top: 0.15rem;
}

.eyebrow {
  color: var(--teal);
  font-weight: 750;
  font-size: 0.76rem;
  letter-spacing: 0.095em;
  text-transform: uppercase;
  margin-bottom: 0.55rem;
}

.page-intro {
  max-width: 760px;
  color: var(--muted);
  font-size: 1.08rem;
  line-height: 1.65;
  margin: -0.25rem 0 1.4rem;
}

.lesson-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin: 1rem 0 1.8rem;
}

.meta-pill {
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--muted);
  border-radius: 999px;
  padding: 0.32rem 0.68rem;
  font-size: 0.78rem;
  font-weight: 650;
}

.content-card, .callout, .lab-panel {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.3rem 1.4rem;
  box-shadow: var(--shadow-sm);
}

.content-card strong, .callout strong {
  display: block;
  margin-bottom: 0.35rem;
}

.content-card p:last-child, .callout p:last-child { margin-bottom: 0; }

.objective-list {
  margin: 0;
  padding-left: 1.15rem;
}

.objective-list li {
  margin: 0.28rem 0;
}

div[data-testid="stLatex"],
div[data-testid="stMarkdownContainer"]:has(> .katex-display) {
  margin: 1.15rem 0 0.4rem;
  padding: 1.15rem 1.25rem;
  overflow-x: auto;
  border: 1px solid #d7e4e7;
  border-radius: 13px;
  background: linear-gradient(135deg, #f7fbfb, #edf4f5);
  box-shadow: inset 4px 0 var(--teal), var(--shadow-sm);
}

div[data-testid="stLatex"] > div,
div[data-testid="stMarkdownContainer"]:has(> .katex-display) > .katex-display {
  font-size: clamp(1rem, 2vw, 1.18rem);
}

.callout {
  border-left: 4px solid var(--teal);
}

.callout.warning {
  border-left-color: var(--amber);
  background: #fffaf1;
}

.step-row {
  display: grid;
  grid-template-columns: 34px 1fr;
  gap: 0.75rem;
  align-items: start;
  margin: 0.75rem 0;
}

.step-number {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--teal-soft);
  color: var(--teal);
  font-size: 0.8rem;
  font-weight: 800;
}

.metric-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
  margin: 0.8rem 0 1.4rem;
}

.metric-box {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 13px;
  padding: 0.9rem 1rem;
  box-shadow: var(--shadow-sm);
}

.metric-label {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.metric-value {
  color: var(--navy);
  font-size: 1.25rem;
  font-weight: 760;
  margin-top: 0.18rem;
}

.prob-row {
  display: grid;
  grid-template-columns: 54px 1fr 64px;
  gap: 0.7rem;
  align-items: center;
  margin: 0.58rem 0;
  font-size: 0.85rem;
}

.prob-label {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-weight: 700;
}

.prob-track {
  height: 11px;
  background: #e8edf0;
  border-radius: 99px;
  overflow: hidden;
}

.prob-fill {
  height: 100%;
  background: var(--teal);
  border-radius: 99px;
}

.prob-value {
  text-align: right;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

.status-note {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.78rem;
  color: var(--muted);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2c9b66;
}

.stButton > button, [data-testid="baseButton-primary"], [data-testid="baseButton-secondary"] {
  min-height: 2.8rem;
  padding-inline: 1rem !important;
  border: 1px solid #ccd6dc !important;
  border-radius: 11px !important;
  font-weight: 720 !important;
  letter-spacing: -0.01em;
  box-shadow: 0 1px 2px rgba(23,33,43,0.06), 0 5px 14px rgba(23,33,43,0.045) !important;
  transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease, background 150ms ease !important;
}

.stButton > button:hover:not(:disabled),
[data-testid="baseButton-primary"]:hover:not(:disabled),
[data-testid="baseButton-secondary"]:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(23,33,43,0.10), 0 2px 5px rgba(23,33,43,0.06) !important;
}

.stButton > button:active:not(:disabled),
[data-testid="baseButton-primary"]:active:not(:disabled),
[data-testid="baseButton-secondary"]:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 3px rgba(23,33,43,0.10) !important;
}

.stButton > button:focus-visible,
[data-testid="baseButton-primary"]:focus-visible,
[data-testid="baseButton-secondary"]:focus-visible {
  outline: 3px solid rgba(8,127,140,0.22) !important;
  outline-offset: 2px !important;
}

[data-testid="baseButton-primary"] {
  background: linear-gradient(135deg, #10939f, #076e79) !important;
  border-color: #087682 !important;
  color: white !important;
  box-shadow: 0 8px 18px rgba(8,127,140,0.20), inset 0 1px rgba(255,255,255,0.22) !important;
}

[data-testid="baseButton-primary"]:hover {
  background: linear-gradient(135deg, #0d8792, #065f69) !important;
  border-color: #065f69 !important;
}

[data-testid="baseButton-secondary"] {
  background: linear-gradient(#ffffff, #fbfcfd) !important;
  color: var(--navy) !important;
}

[data-testid="baseButton-secondary"]:hover {
  border-color: #79adb3 !important;
  color: #066e78 !important;
  background: #f7fbfb !important;
}

.stButton > button:disabled,
[data-testid="baseButton-primary"]:disabled,
[data-testid="baseButton-secondary"]:disabled {
  opacity: 0.48;
  box-shadow: none !important;
}

[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div,
[data-testid="stNumberInput"] input {
  background: white !important;
  border-color: #cfd8de !important;
  border-radius: 10px !important;
  box-shadow: 0 1px 2px rgba(23,33,43,0.035) !important;
}

[data-testid="stTextArea"] textarea {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  line-height: 1.55;
}

[data-testid="stChatMessage"] {
  background: white;
  border: 1px solid var(--line);
  border-radius: 12px;
  margin-bottom: 0.65rem;
}

[data-testid="stExpander"] {
  background: white;
  border-color: var(--line) !important;
  border-radius: 10px !important;
}

code, pre { font-size: 0.82rem !important; }

@media (max-width: 760px) {
  [data-testid="stAppViewContainer"] > .main .block-container {
    padding-top: 1rem;
  }
  .metric-row { grid-template-columns: 1fr; }
  .prob-row { grid-template-columns: 44px 1fr 52px; }
}
</style>
        """,
        unsafe_allow_html=True,
    )
