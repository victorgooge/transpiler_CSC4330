# streamlit_app.py

import streamlit as st
from transpiler import PythonToJS, extract_comments
from streamlit_ace import st_ace
from misc import themes
import uuid

transpiler = PythonToJS()

st.set_page_config(page_title="Python to JS Transpiler", layout="wide")
st.title("Python ➜ JavaScript Transpiler")

# Set default theme in session state
if "editor_theme" not in st.session_state:
    st.session_state.editor_theme = "monokai"
if "js_output" not in st.session_state:
    st.session_state.js_output = ""
if "js_editor_key" not in st.session_state:
    st.session_state.js_editor_key = str(uuid.uuid4())

# Theme dropdown
st.selectbox(
    "🎨 Choose Editor Theme",
    themes.THEMES,
    index=themes.THEMES.index(st.session_state.editor_theme),
    key="editor_theme"
)

# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <img 
                src="https://imgs.search.brave.com/PQDtuQbh0uVAlmDH_P-yauEFX2WMUJrnew1WV_HNzTU/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly9jZG4z/Lmljb25maW5kZXIu/Y29tL2RhdGEvaWNv/bnMvbG9nb3MtYW5k/LWJyYW5kcy1hZG9i/ZS81MTIvMjY3X1B5/dGhvbi01MTIucG5n" 
                width="30" height="30"
            >
            <h3 style="margin: 0;">Python Code</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    python_code = st_ace(
        placeholder="write your python code here...",
        language="python",
        theme=st.session_state.editor_theme,
        key="python_editor",
        height=400,
        font_size=14,
        show_gutter=True,
        show_print_margin=False,
        wrap=True,
        auto_update=True
    )
    st.session_state.python_code = python_code

    if st.button("Transpile"):
        if python_code.strip():
            st.session_state.js_output = transpiler.transpile(python_code)
            st.session_state.js_editor_key = str(uuid.uuid4()) 
        else:
            st.session_state.js_output = "// Please write some Python code."
            st.session_state.js_editor_key = str(uuid.uuid4())  


with col2:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <img 
                src="https://cdn-icons-png.flaticon.com/512/5968/5968292.png"
                width="30" height="30"
            >
            <h3 style="margin: 0;">JavaScript Code</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    st_ace(
        value=st.session_state.js_output,
        language="javascript",
        theme=st.session_state.editor_theme,
        key=st.session_state.js_editor_key, 
        height=400,
        readonly=True,
        auto_update=True
    )