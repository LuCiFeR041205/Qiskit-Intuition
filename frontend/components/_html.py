# components/_html.py
# Compatibility shim for Streamlit's html rendering.
# Uses st.html() when available (Streamlit >= 1.46),
# falls back to the deprecated streamlit.components.v1.html().

import streamlit as st


def render_html(html_content: str, height: int = 400, scrolling: bool = False):
    """Render raw HTML in a Streamlit app, using the non-deprecated API when available."""
    try:
        # st.html() was added in Streamlit 1.46 (2025).
        # It does not accept height/scrolling — the iframe auto-sizes.
        st.html(html_content)
    except AttributeError:
        import streamlit.components.v1 as components
        components.html(html_content, height=height, scrolling=scrolling)
