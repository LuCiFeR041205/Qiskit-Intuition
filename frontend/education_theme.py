"""Visual system: a physicist's paper lab notebook.

Ruled cream paper with a red margin and punched holes sits on a desk; the
sidebar is the cloth notebook cover. Headings are handwritten (Caveat), body
text is neat handwriting (Patrick Hand), code is typewritten (Courier Prime).
Cards are sticky notes and index cards held on with tape; buttons look
hand-drawn; probability bars are highlighter strokes.
"""

import streamlit as st

NOTEBOOK_CSS = """
<style>
/* Fonts are self-hosted from ./static/fonts (SIL Open Font License) so the
   notebook look survives networks that block Google Fonts. */
@font-face { font-family: "Caveat"; font-weight: 400 700; font-display: swap; src: url("app/static/fonts/Caveat-latin.woff2") format("woff2"); }
@font-face { font-family: "Patrick Hand"; font-weight: 400; font-display: swap; src: url("app/static/fonts/PatrickHand-latin.woff2") format("woff2"); }
@font-face { font-family: "Courier Prime"; font-weight: 400; font-display: swap; src: url("app/static/fonts/CourierPrime-Regular-latin.woff2") format("woff2"); }
@font-face { font-family: "Courier Prime"; font-weight: 700; font-display: swap; src: url("app/static/fonts/CourierPrime-Bold-latin.woff2") format("woff2"); }

:root {
  --desk: #d9cfb8;
  --paper: #fbf7ec;
  --paper-2: #f4eedc;
  --rule: rgba(73, 128, 196, 0.16);
  --margin: rgba(214, 72, 72, 0.42);
  --ink: #1d3a8a;
  --graphite: #2b2a27;
  --pencil: #6f6a5e;
  --pencil-light: #b9b19c;
  --red-ink: #ab2e22;  /* 5.2:1 on pink sticky notes, 6.2:1 on paper (WCAG AA) */
  --marker: #ffe867;
  --marker-green: #b8f0c8;
  --marker-pink: #ffc8d6;
  --sticky: #fff1a1;
  --sticky-pink: #ffdbe4;
  --sticky-blue: #dbecff;
  --sticky-green: #ddf5dc;
  --tape: rgba(236, 224, 176, 0.78);
  --cover: #23365c;
  --hand-radius: 255px 15px 225px 15px / 15px 225px 15px 255px;
  --hand-radius-2: 15px 225px 15px 255px / 255px 15px 225px 15px;
  --hand: "Patrick Hand", "Comic Neue", "Segoe Print", cursive;
  --script: "Caveat", "Patrick Hand", cursive;
  --type: "Courier Prime", "Courier New", ui-monospace, monospace;
}

/* ---------- desk, page and binding ---------- */
.stApp {
  background:
    radial-gradient(circle at 20% 10%, rgba(255,255,255,.35), transparent 40rem),
    repeating-linear-gradient(115deg, rgba(120,95,60,.035) 0 2px, transparent 2px 9px),
    var(--desk);
}

.stApp :not([data-testid="stIconMaterial"]):not(.katex):not(.katex *):not(code):not(code *):not(pre):not(pre *):not(textarea):not(svg *) {
  font-family: var(--hand);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"] { display: none; }

[data-testid="stMainBlockContainer"] {
  position: relative;
  max-width: 1160px;
  margin: 1.4rem auto 3rem;
  padding: 2.6rem 3rem 4rem 6.2rem !important;
  color: var(--graphite);
  background-color: var(--paper);
  background-image:
    linear-gradient(90deg, transparent 4.6rem, var(--margin) 4.6rem, var(--margin) calc(4.6rem + 2px), transparent calc(4.6rem + 2px)),
    repeating-linear-gradient(180deg, transparent 0, transparent 31px, var(--rule) 31px, var(--rule) 32px);
  background-position: 0 0, 0 3.2rem;
  border-radius: 3px 8px 8px 3px;
  box-shadow:
    0 1px 1px rgba(0,0,0,.08),
    6px 6px 0 -1px var(--paper-2), 6px 6px 1px 0 rgba(0,0,0,.10),
    12px 12px 0 -2px #efe8d3, 12px 12px 2px -1px rgba(0,0,0,.10),
    0 22px 40px rgba(60, 45, 20, .22);
}

/* punched holes along the binding edge */
[data-testid="stMainBlockContainer"]::before {
  content: "";
  position: absolute;
  top: 1.2rem; bottom: 1.2rem; left: 1.3rem;
  width: 22px;
  background-image: radial-gradient(circle at 11px 11px, var(--desk) 0 7px, rgba(0,0,0,.18) 7.5px, transparent 9px);
  background-size: 22px 58px;
  background-repeat: repeat-y;
  pointer-events: none;
}

/* ---------- type ---------- */
.stApp p, .stApp li, .stApp label, .stApp [data-testid="stMarkdownContainer"] {
  color: var(--graphite);
  font-size: 1.12rem;
  line-height: 1.6;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
  font-family: var(--script) !important;
  color: var(--ink) !important;
  letter-spacing: 0;
  font-weight: 700 !important;
}
.stApp h1 {
  font-size: 3.3rem !important;
  line-height: 1.05 !important;
  display: inline;
  padding: 0 .2em !important;
  background: linear-gradient(transparent 62%, var(--marker) 62%, var(--marker) 90%, transparent 90%);
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}
.stApp h2 { font-size: 2.2rem !important; }
.stApp h3 { font-size: 1.85rem !important; }
.stApp h4 { font-size: 1.5rem !important; }
[data-testid="stHeaderActionElements"] { display: none; }
.stApp strong { color: #15213f; }
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] p {
  color: var(--pencil) !important;
  font-size: 1rem;
}

/* Code output keeps a system monospace: Qiskit's text circuit drawings need
   box-drawing glyphs (┤ ├ ─) that Courier Prime lacks, or columns misalign. */
code, pre, [data-testid="stCode"] * { font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, "DejaVu Sans Mono", "Liberation Mono", monospace !important; }
textarea { font-family: var(--type) !important; }
[data-testid="stCode"] pre, [data-testid="stCode"] code { line-height: 1.2 !important; }
.stApp [data-testid="stMarkdownContainer"] :not(pre) > code {
  background: rgba(255, 232, 103, .45);
  color: var(--ink);
  padding: .05em .3em;
  border-radius: 3px;
  font-size: .92em;
}

.eyebrow {
  font-family: var(--type) !important;
  color: var(--red-ink);
  font-size: .78rem;
  letter-spacing: .14em;
  text-transform: uppercase;
  margin-bottom: .3rem;
}
.page-intro {
  font-family: var(--script) !important;
  color: var(--pencil);
  font-size: 1.6rem;
  line-height: 1.3;
  max-width: 50rem;
  margin: .9rem 0 .4rem;
}

/* ---------- notebook cover (sidebar) ---------- */
[data-testid="stSidebar"] {
  background:
    repeating-linear-gradient(45deg, rgba(255,255,255,.035) 0 2px, transparent 2px 6px),
    repeating-linear-gradient(-45deg, rgba(0,0,0,.06) 0 2px, transparent 2px 6px),
    var(--cover);
  border-right: 10px solid #182641;
  box-shadow: inset -6px 0 12px rgba(0,0,0,.25);
}
[data-testid="stSidebar"] * { color: #f1ead6; }
[data-testid="stSidebar"] hr { border-color: rgba(241,234,214,.18); }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #cfc6ad !important; }

.brand {
  position: relative;
  margin: .2rem .2rem 1.4rem;
  padding: 1rem 1rem .9rem;
  background: var(--paper);
  border: 2px solid #2b2a27;
  outline: 1px solid #2b2a27;
  outline-offset: 3px;
  border-radius: 6px;
  transform: rotate(-1.2deg);
  box-shadow: 0 6px 14px rgba(0,0,0,.35);
}
.brand * { color: var(--graphite) !important; }
.brand-mark {
  font-family: var(--type) !important;
  font-size: .68rem;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--red-ink) !important;
}
.brand-name {
  font-family: var(--script) !important;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.05;
  color: var(--ink) !important;
}
.brand-subtitle {
  font-size: .95rem;
  border-top: 1px dashed var(--pencil-light);
  margin-top: .35rem;
  padding-top: .3rem;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
  margin: .25rem 0;
  padding: .45rem .8rem;
  border-radius: 0 10px 10px 0;
  background: rgba(241,234,214,.08);
  border-left: 6px solid #e8b04b;
  transition: transform 150ms ease, background 150ms ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2) { border-left-color: #7fc3a3; }
[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3) { border-left-color: #8fb7e8; }
[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(4) { border-left-color: #e88b9a; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { transform: translateX(4px); background: rgba(241,234,214,.16); }
[data-testid="stSidebar"] [role="radiogroup"] label p { font-family: var(--script) !important; font-size: 1.55rem !important; color: #f8f2df !important; }
[data-testid="stSidebar"] [data-testid="stProgressBarTrack"] { background: rgba(241,234,214,.2); }
.stApp [data-testid="stSidebar"] [data-baseweb="select"] > div, .stApp [data-testid="stSidebar"] [data-testid="stSelectbox"] div:has(> input) { background: rgba(241,234,214,.1) !important; border: 1.5px dashed rgba(241,234,214,.5) !important; }
.stApp [data-testid="stSidebar"] [data-baseweb="select"] *, .stApp [data-testid="stSidebar"] [data-testid="stSelectbox"] div:has(> input) * { color: #f8f2df !important; font-size: 1.05rem; }
[data-testid="stSidebar"] [data-testid="stExpander"] details { background: transparent !important; border-color: rgba(241,234,214,.35) !important; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary p { color: #f1ead6 !important; font-size: 1.3rem !important; }

.status-note { font-size: .95rem; display: flex; gap: .45rem; align-items: center; }
.status-dot { width: 9px; height: 9px; border-radius: 50%; background: #7fc3a3; display: inline-block; }

/* ---------- hand-drawn controls ---------- */
.stApp [data-testid^="stBaseButton"] {
  font-family: var(--hand) !important;
  border-radius: var(--hand-radius) !important;
  border: 2px solid var(--ink) !important;
  background: transparent !important;
  color: var(--ink) !important;
  box-shadow: 2px 3px 0 rgba(29, 58, 138, .18) !important;
  transition: transform 120ms ease, background 120ms ease, box-shadow 120ms ease;
}
.stApp [data-testid^="stBaseButton"] p { font-size: 1.15rem !important; color: inherit !important; }
.stApp [data-testid^="stBaseButton"]:hover {
  transform: rotate(-.6deg) translateY(-1px);
  background: rgba(255, 232, 103, .45) !important;
}
.stApp [data-testid="stBaseButton-primary"] {
  background: var(--marker) !important;
  border-radius: var(--hand-radius-2) !important;
  box-shadow: 3px 4px 0 rgba(29, 58, 138, .28) !important;
}
.stApp [data-testid="stBaseButton-primary"] p { font-weight: 700; }
.stApp [data-testid^="stBaseButton"]:disabled { opacity: .45; }
[data-testid="stSidebar"] [data-testid^="stBaseButton"] { border-color: #f1ead6 !important; color: #f1ead6 !important; box-shadow: none !important; }
[data-testid="stHeader"] [data-testid^="stBaseButton"],
[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"] { border: 0 !important; box-shadow: none !important; }

.stApp [data-testid="stTextAreaRootElement"], .stApp [data-baseweb="select"] > div, .stApp [data-testid="stSelectbox"] div:has(> input), .stApp [data-testid="stNumberInputContainer"] {
  background: #fffdf5 !important;
  border: 1.5px solid var(--pencil) !important;
  border-radius: 4px;
}
.stApp textarea {
  background:
    repeating-linear-gradient(180deg, transparent 0, transparent 23px, rgba(73,128,196,.10) 23px, rgba(73,128,196,.10) 24px),
    #fffdf5 !important;
  color: #1e1e1e !important;
  font-size: .95rem !important;
  line-height: 24px !important;
}

[data-testid="stCode"] pre, .stApp pre {
  background: #fffef9 !important;
  border: 1px solid #ddd3b8;
  border-radius: 2px;
  box-shadow: 2px 3px 0 rgba(0,0,0,.06);
}
[data-testid="stCode"] { position: relative; }
[data-testid="stCode"]::before {
  content: ""; position: absolute; top: -9px; left: 18px; width: 70px; height: 18px;
  background: var(--tape); transform: rotate(-3deg); z-index: 2; box-shadow: 0 1px 1px rgba(0,0,0,.06);
}

[data-testid="stAlertContainer"] {
  border-radius: 2px !important;
  border: 0 !important;
  box-shadow: 2px 4px 8px rgba(70, 55, 20, .16);
  transform: rotate(-.35deg);
}
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) [data-testid="stAlertContainer"] { background: var(--sticky-green) !important; }
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) [data-testid="stAlertContainer"] { background: var(--sticky) !important; }
[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) [data-testid="stAlertContainer"] { background: var(--sticky-pink) !important; }
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) [data-testid="stAlertContainer"] { background: var(--sticky-blue) !important; }
[data-testid="stAlertContainer"] p { color: var(--graphite) !important; }

[data-testid="stExpander"] details {
  border: 1.5px dashed var(--pencil-light) !important;
  border-radius: 4px !important;
  background: rgba(255,255,255,.35);
}
[data-testid="stExpander"] summary p { font-family: var(--script) !important; font-size: 1.45rem !important; color: var(--ink) !important; }

.stApp [data-testid="stSlider"] [role="slider"] { background: var(--ink) !important; box-shadow: none !important; }
.stApp [data-testid="stSliderThumbValue"], .stApp [data-testid="stSliderTickBarMin"], .stApp [data-testid="stSliderTickBarMax"] { color: var(--ink) !important; }
.stApp [data-testid="stRadio"] label p { font-size: 1.2rem !important; }
.stApp [data-testid="stMetricValue"] { font-family: var(--script) !important; color: var(--ink); }

[data-testid="stPopoverBody"] { background: var(--sticky) !important; border-radius: 2px !important; }

/* ---------- containers drawn as taped cards ---------- */
[class*="st-key-nb-card"] {
  position: relative;
  background: rgba(255, 255, 255, .55);
  border: 1.5px solid var(--pencil) !important;
  border-radius: var(--hand-radius-2) !important;
  padding: 1.1rem 1.2rem 1rem !important;
  box-shadow: 3px 4px 0 rgba(0,0,0,.05);
}
[class*="st-key-nb-card"]::before {
  content: ""; position: absolute; top: -11px; left: 42%; width: 96px; height: 22px;
  background: var(--tape); transform: rotate(2deg); box-shadow: 0 1px 1px rgba(0,0,0,.06);
}

/* ---------- course map ---------- */
.cover-label {
  position: relative;
  width: min(36rem, 100%);
  margin: .2rem auto 1.4rem;
  padding: 1.3rem 1.6rem 1.1rem;
  background: #fffef8;
  border: 2px solid var(--graphite);
  outline: 1px solid var(--graphite);
  outline-offset: 4px;
  border-radius: 10px;
  text-align: center;
  transform: rotate(-.8deg);
  box-shadow: 0 10px 24px rgba(70,55,20,.16);
}
.cover-label .label-kicker { font-family: var(--type) !important; letter-spacing: .2em; font-size: .78rem; color: var(--red-ink); text-transform: uppercase; }
.cover-label .label-title { font-family: var(--script) !important; font-size: 3.3rem; font-weight: 700; color: var(--ink); line-height: 1; margin: .3rem 0 .6rem; }
.cover-label .label-line { display: flex; gap: .6rem; align-items: baseline; text-align: left; font-size: 1.05rem; color: var(--pencil); margin: .35rem 0; }
.cover-label .label-line span { flex: 0 0 auto; font-family: var(--type) !important; font-size: .8rem; letter-spacing: .1em; text-transform: uppercase; }
.cover-label .label-line b { flex: 1; border-bottom: 1px solid var(--pencil); font-family: var(--script) !important; font-size: 1.5rem; color: var(--ink); font-weight: 500; line-height: 1.1; }
.intro-note { font-family: var(--script) !important; font-size: 1.65rem; line-height: 1.35; color: var(--graphite); max-width: 52rem; margin: .4rem 0 .8rem; }
.intro-note u { text-decoration: none; background: linear-gradient(transparent 60%, var(--marker-green) 60%); }

.loop-row { display: flex; flex-wrap: wrap; align-items: center; gap: .3rem .5rem; margin: .4rem 0 1.4rem; }
.loop-step { font-family: var(--script) !important; font-size: 1.55rem; color: var(--ink); white-space: nowrap; }
.loop-step span {
  display: inline-grid; place-items: center; width: 1.6rem; height: 1.6rem; margin-right: .15rem;
  border: 2px solid var(--red-ink); border-radius: 50% 45% 55% 48%; color: var(--red-ink); font-size: 1.1rem; line-height: 1;
}
.loop-step small { display: none; }
.loop-arrow { color: var(--pencil); font-size: 1.4rem; }

.unit-head { display: flex; align-items: baseline; gap: .6rem; flex-wrap: wrap; }
.unit-head span { font-family: var(--type) !important; color: var(--red-ink); font-size: .78rem; letter-spacing: .14em; text-transform: uppercase; }
.unit-head strong { font-family: var(--script) !important; font-size: 2rem; color: var(--ink); }
.unit-head small { margin-left: auto; font-family: var(--script) !important; font-size: 1.3rem; color: var(--pencil); }
.unit-blurb { color: var(--pencil) !important; margin: 0 0 .4rem !important; }
.lesson-row { display: flex; gap: .7rem; align-items: center; padding: .15rem 0; }
.lesson-row > span {
  flex: 0 0 auto; width: 1.4rem; height: 1.4rem; display: inline-grid; place-items: center;
  border: 1.5px solid var(--pencil); border-radius: 3px; color: transparent; font-weight: 700;
}
.lesson-row.done > span { color: var(--red-ink); font-family: var(--script) !important; font-size: 1.5rem; border-color: var(--pencil); }
.lesson-row strong { display: block; font-size: 1.15rem; color: var(--graphite); font-weight: 400; }
.lesson-row.done strong { text-decoration: line-through; text-decoration-color: rgba(192, 57, 43, .55); }
.lesson-row small { color: var(--pencil); font-size: .95rem; }

table.glossary { width: 100%; border-collapse: collapse; }
table.glossary th { text-align: left; font-family: var(--script) !important; font-size: 1.4rem; color: var(--ink); border-bottom: 2px solid var(--ink); padding: .3rem .5rem; }
table.glossary td { border-bottom: 1px solid var(--rule); padding: .4rem .5rem; vertical-align: top; font-size: 1.05rem; }
table.glossary td:first-child strong { background: linear-gradient(transparent 55%, var(--marker) 55%); font-weight: 400; color: var(--graphite); }

/* ---------- lesson chrome ---------- */
.path-context { display: flex; flex-wrap: wrap; gap: .6rem; margin-bottom: 1rem; }
.path-context span {
  font-family: var(--type) !important; font-size: .74rem; letter-spacing: .14em; text-transform: uppercase;
  color: var(--red-ink); border: 2px solid var(--red-ink); border-radius: 4px; padding: .15rem .5rem;
  transform: rotate(-1.5deg); opacity: .85;
}
.path-context span:nth-child(2) { transform: rotate(1deg); color: var(--ink); border-color: var(--ink); }

.journey-stepper { display: flex; flex-wrap: wrap; gap: .4rem 1.4rem; margin: 1.6rem 0 1.8rem; padding: .7rem 0; border-top: 1px dashed var(--pencil-light); border-bottom: 1px dashed var(--pencil-light); }
.journey-step { display: flex; align-items: center; gap: .45rem; color: var(--pencil); }
.journey-step strong { font-family: var(--script) !important; font-size: 1.5rem; font-weight: 500; }
.journey-step small { display: none; }
.journey-marker {
  width: 1.35rem; height: 1.35rem; display: inline-grid; place-items: center;
  border: 1.5px solid var(--pencil); border-radius: 3px; font-size: 0; color: transparent;
}
.journey-step.complete .journey-marker { font-family: var(--script) !important; font-size: 1.5rem; color: var(--red-ink); }
.journey-step.complete strong { text-decoration: line-through; text-decoration-color: rgba(192,57,43,.55); }
.journey-step.current { color: var(--ink); }
.journey-step.current strong {
  font-weight: 700; padding: 0 .45rem; border: 2px solid var(--ink); border-radius: 50% 45% 52% 48% / 60% 55% 45% 50%;
}

.stage-kicker {
  font-family: var(--script) !important; color: var(--red-ink); font-size: 1.5rem; font-weight: 700;
  transform: rotate(-1deg); display: inline-block; margin-bottom: .2rem;
}

/* sticky notes */
.content-card, .prediction-recap, .try-card {
  position: relative;
  padding: 1.1rem 1.2rem .9rem;
  background: var(--sticky);
  border-radius: 2px 2px 18px 2px;
  box-shadow: 2px 6px 12px rgba(70,55,20,.16);
  transform: rotate(.8deg);
  margin: .8rem .2rem 1rem;
}
.content-card::before, .prediction-recap::before, .try-card::before, .task-card::before, .prediction-prompt::before, .explanation-brief::before {
  content: ""; position: absolute; top: -10px; left: calc(50% - 45px); width: 90px; height: 22px;
  background: var(--tape); transform: rotate(-2deg); box-shadow: 0 1px 1px rgba(0,0,0,.06);
}
.content-card > strong, .try-card > strong, .prediction-recap > span {
  display: block; font-family: var(--script) !important; font-size: 1.5rem; color: var(--ink); margin-bottom: .2rem; font-weight: 700;
}
.prediction-recap { background: var(--sticky-blue); transform: rotate(-1deg); }
.prediction-recap p { margin: 0; font-size: 1.2rem; }
.try-card { background: var(--sticky-green); transform: rotate(-.6deg); }
.try-card ol { margin: .2rem 0 0 1.2rem; padding: 0; }
.try-card li { margin: .2rem 0; }
.objective-list { margin: .3rem 0 0 1.1rem; padding: 0; }
.objective-list li { margin: .25rem 0; }

.callout {
  position: relative; padding: .8rem 1rem .8rem 1.1rem; margin: 1rem 0;
  border-left: 3px solid var(--ink); background: rgba(219, 236, 255, .45); border-radius: 0 6px 6px 0;
}
.callout strong { font-family: var(--script) !important; font-size: 1.45rem; color: var(--ink); }
.callout.warning { background: var(--sticky-pink); border-left: 0; border-radius: 2px 2px 16px 2px; transform: rotate(-.8deg); box-shadow: 2px 6px 12px rgba(70,55,20,.16); }
.callout.warning strong { color: var(--red-ink); }
.callout.warning strong::before { content: "⚠ "; }
.callout p { margin: .2rem 0 0; }

/* index cards */
.prediction-prompt, .explanation-brief, .task-card {
  position: relative; margin: 1rem 0 1.1rem; padding: 1.4rem 1.4rem 1rem;
  background:
    linear-gradient(180deg, transparent 2.6rem, rgba(214,72,72,.55) 2.6rem, rgba(214,72,72,.55) calc(2.6rem + 2px), transparent calc(2.6rem + 2px)),
    repeating-linear-gradient(180deg, transparent 0, transparent 27px, rgba(73,128,196,.18) 27px, rgba(73,128,196,.18) 28px),
    #fffef9;
  background-position: 0 0, 0 2.7rem;
  border-radius: 2px;
  box-shadow: 2px 5px 12px rgba(70,55,20,.14);
}
.prediction-prompt > span, .task-card > span, .explanation-brief > strong {
  display: block; font-family: var(--type) !important; font-size: .76rem; letter-spacing: .16em; text-transform: uppercase; color: var(--red-ink); margin-bottom: .55rem;
}
.prediction-prompt > strong { display: block; font-family: var(--script) !important; font-size: 1.9rem; line-height: 1.2; color: var(--ink); }
.prediction-prompt p, .explanation-brief p, .task-card p { margin: .45rem 0 0; }
.explanation-brief blockquote { margin: .6rem 0 0; padding: 0; border: 0; font-family: var(--script) !important; font-size: 1.75rem; line-height: 1.25; color: var(--ink); }
.task-card { transform: rotate(-.4deg); }
.task-card.solved::after {
  content: "SOLVED"; position: absolute; top: .9rem; right: 1.2rem; font-family: var(--type); font-weight: 700; letter-spacing: .2em;
  color: var(--red-ink); border: 3px solid var(--red-ink); padding: .1rem .45rem; border-radius: 4px; transform: rotate(-8deg); opacity: .8;
}

.feel-it { display: flex; align-items: center; gap: .7rem; margin: 1.6rem 0 .7rem; }
.feel-it span {
  font-family: var(--script) !important; font-size: 1.9rem; font-weight: 700; color: var(--red-ink);
  transform: rotate(-4deg); display: inline-block;
}
.feel-it span::after { content: " ⤵"; }
.feel-it strong { font-family: var(--script) !important; font-size: 1.5rem; font-weight: 500; color: var(--pencil); }

.coach-feedback span { font-family: var(--script) !important; font-size: 1.6rem; color: var(--red-ink); }

/* circuit builder */
.guided-sequence { display: flex; flex-wrap: wrap; gap: .5rem; padding: .7rem .2rem; min-height: 3.2rem; align-items: center; }
.gate-chip {
  display: inline-flex; align-items: baseline; gap: .35rem; padding: .25rem .7rem;
  background: var(--sticky); border: 1.5px solid var(--ink); border-radius: var(--hand-radius);
  color: var(--ink); box-shadow: 1px 2px 0 rgba(0,0,0,.08);
}
.gate-chip:nth-child(even) { transform: rotate(1.2deg); }
.gate-chip:nth-child(odd) { transform: rotate(-1deg); }
.gate-chip small { font-family: var(--script) !important; color: var(--red-ink); font-size: 1.1rem; }
.gate-chip strong { font-weight: 400; color: var(--ink); }
.empty-sequence { font-family: var(--script) !important; font-size: 1.4rem; color: var(--pencil); }

.metric-row { display: flex; flex-wrap: wrap; gap: 1.6rem; margin: .4rem 0 1rem; }
.metric-label { font-family: var(--type) !important; font-size: .74rem; letter-spacing: .12em; text-transform: uppercase; color: var(--pencil); }
.metric-value { font-family: var(--script) !important; font-size: 1.9rem; color: var(--ink); }

.challenge-banner { position: relative; padding: 1rem 1.2rem; margin: .5rem 0 1rem; background: var(--sticky-pink); transform: rotate(-.5deg); box-shadow: 2px 6px 12px rgba(70,55,20,.16); }
.challenge-banner span { font-family: var(--type) !important; font-size: .74rem; letter-spacing: .14em; text-transform: uppercase; color: var(--red-ink); display: block; }
.challenge-banner strong { font-family: var(--script) !important; font-size: 1.7rem; color: var(--ink); }

/* highlighter probability bars */
.prob-row { display: grid; grid-template-columns: 4.2rem 1fr 4.6rem; gap: .7rem; align-items: center; margin: .5rem 0; }
.prob-label { font-family: var(--type) !important; font-weight: 700; color: var(--ink); }
.prob-track { position: relative; height: 18px; border-bottom: 1.5px solid var(--pencil-light); }
.prob-fill {
  height: 100%;
  background: var(--marker);
  opacity: .9;
  border-radius: 3px 9px 4px 10px / 8px 3px 9px 4px;
  transform: skewX(-8deg);
  mix-blend-mode: multiply;
}
.prob-row:nth-child(even) .prob-fill { background: var(--marker-green); }
.prob-value { text-align: right; white-space: nowrap; font-family: var(--script) !important; font-size: 1.35rem; color: var(--ink); }
.prob-ghost { position: absolute; top: -5px; bottom: -5px; width: 3px; margin-left: -1.5px; background: var(--red-ink); border-radius: 2px; z-index: 2; transform: rotate(6deg); }

.shot-strip { display: flex; flex-wrap: wrap; gap: 5px; margin: .5rem 0; }
.shot-chip {
  width: 1.7rem; height: 1.7rem; display: grid; place-items: center;
  border: 1.5px solid var(--pencil); border-radius: var(--hand-radius);
  font-family: var(--script) !important; font-size: 1.35rem; color: var(--graphite);
}
.shot-chip.s1 { background: var(--marker); border-color: var(--ink); color: var(--ink); }

.bit-display { display: flex; align-items: center; gap: .6rem; margin: .6rem 0 1rem; flex-wrap: wrap; }
.bit-cell { width: 4.2rem; text-align: center; padding: .3rem 0 .2rem; border: 2px solid var(--ink); border-radius: var(--hand-radius); background: #fffef8; }
.bit-cell:nth-child(even) { transform: rotate(1.5deg); }
.bit-cell strong { display: block; font-family: var(--script) !important; font-size: 2.6rem; line-height: 1; color: var(--ink); }
.bit-cell small { font-family: var(--type) !important; color: var(--pencil); }
.bit-cell.on { background: var(--marker); }
.bit-arrow { font-family: var(--script) !important; font-size: 1.5rem; color: var(--red-ink); margin-left: .4rem; }

.pair-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: .45rem; }
.pair {
  display: flex; justify-content: center; gap: 2px; padding: .15rem 0;
  border: 1.5px solid var(--pencil); border-radius: var(--hand-radius);
  font-family: var(--script) !important; font-size: 1.6rem; color: var(--graphite);
}
.pair.match { background: var(--marker-green); }
.pair.miss { background: var(--marker-pink); }
.pair-note { font-family: var(--script) !important; font-size: 1.4rem !important; color: var(--ink) !important; margin: .4rem 0 0; }

/* ---------- the learner's own writing ---------- */
[class*="st-key-nb-margin-notes"] {
  position: relative;
  margin-top: 1.6rem;
  padding: 1rem 1.1rem .7rem !important;
  background: var(--sticky);
  border-radius: 2px 2px 20px 2px;
  box-shadow: 2px 6px 12px rgba(70,55,20,.16);
  transform: rotate(-.5deg);
  max-width: 44rem;
}
[class*="st-key-nb-margin-notes"]::before {
  content: ""; position: absolute; top: -10px; left: calc(50% - 45px); width: 90px; height: 22px;
  background: var(--tape); transform: rotate(2deg);
}
.margin-title { font-family: var(--script) !important; font-size: 1.6rem; font-weight: 700; color: var(--red-ink); }
[class*="st-key-nb-margin-notes"] [data-testid="stTextAreaRootElement"] { background: transparent !important; border: 0 !important; }
[class*="st-key-nb-margin-notes"] textarea {
  font-family: var(--script) !important;
  font-size: 1.45rem !important;
  line-height: 30px !important;
  color: var(--ink) !important;
  background: repeating-linear-gradient(180deg, transparent 0, transparent 29px, rgba(29,58,138,.18) 29px, rgba(29,58,138,.18) 30px) !important;
}
[class*="st-key-nb-storage"] { height: 0; overflow: hidden; margin: 0 !important; }
[class*="st-key-nb-storage"] iframe { height: 0 !important; border: 0; }

.entry-head { display: flex; align-items: baseline; gap: .7rem; flex-wrap: wrap; margin-bottom: .3rem; }
.entry-head span { font-family: var(--type) !important; font-size: .76rem; letter-spacing: .14em; text-transform: uppercase; color: var(--red-ink); }
.entry-head strong { font-family: var(--script) !important; font-size: 2rem; color: var(--ink); }
.entry-head em { margin-left: auto; font-family: var(--script) !important; font-style: normal; font-size: 1.3rem; color: var(--pencil); }
.entry-line { margin: .35rem 0 .1rem !important; }
.entry-line span { font-family: var(--type) !important; font-size: .76rem; letter-spacing: .12em; text-transform: uppercase; color: var(--pencil); margin-right: .4rem; }
.entry-hand { font-family: var(--script) !important; font-size: 1.55rem !important; line-height: 1.35 !important; color: var(--ink) !important; white-space: pre-wrap; margin: 0 0 .4rem !important; }
.entry-note {
  display: inline-block; max-width: 36rem; margin: .5rem 0 .6rem; padding: .7rem .9rem;
  background: var(--sticky); transform: rotate(1deg); box-shadow: 2px 5px 10px rgba(70,55,20,.15);
  font-family: var(--script) !important; font-size: 1.4rem; line-height: 1.3; color: var(--ink); white-space: pre-wrap;
}

/* ---------- small screens ---------- */
@media (max-width: 760px) {
  [data-testid="stMainBlockContainer"] {
    margin: .4rem .3rem 2rem;
    padding: 1.6rem 1rem 3rem 2.6rem !important;
    background-image:
      linear-gradient(90deg, transparent 1.8rem, var(--margin) 1.8rem, var(--margin) calc(1.8rem + 2px), transparent calc(1.8rem + 2px)),
      repeating-linear-gradient(180deg, transparent 0, transparent 31px, var(--rule) 31px, var(--rule) 32px);
  }
  [data-testid="stMainBlockContainer"]::before { display: none; }
  .stApp h1 { font-size: 2.4rem !important; }
  .cover-label .label-title { font-size: 2.5rem; }
  .prob-row { grid-template-columns: 3.4rem 1fr 3.4rem; }
}
</style>
"""


def inject_education_theme() -> None:
    st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
