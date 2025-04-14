

# streamlit_app.py

import streamlit as st
from transpiler import PythonToJS, extract_comments
from streamlit_code_editor import code_editor

st.set_page_config(page_title="Python to JS Transpiler", layout="wide")
st.title("🌀 Python ➜ JavaScript Transpiler")

# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Python Code")

    editor_content = code_editor(
        language="python",
        height=400,
        theme="material",  
        key="code_input",
        placeholder="Type your Python code here..."
    )

    python_code = editor_content["text"]

with col2:
    st.subheader("⚙️ Transpiled JavaScript")

    # Custom CSS for scrollable st.code()
    st.markdown(
        """
        <style>
        div[data-testid="stCode"] {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #30363d;
            border-radius: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    js_output_placeholder = st.empty()

    if st.button("🚀 Transpile"):
        if python_code.strip():
            comments = extract_comments(python_code)
            transpiler = PythonToJS(comments)
            js_code = transpiler.transpile(python_code)

            # still uses syntax highlighting
            js_output_placeholder.code(js_code, language="javascript")
        else:
            js_output_placeholder.info("Please enter some Python code to transpile.")
