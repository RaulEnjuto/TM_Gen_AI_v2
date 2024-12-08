import json
import os
import traceback

from typing import List, Optional, Dict

import docx
import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from utilities import utils
from utilities.enums import CaseTypes
from utilities.prompts import Prompts


try:

    st.set_page_config(
        page_title="Documentation - Transaction Monitoring",
        page_icon="📂",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    utils.show_logo()

    file_emojis = {
        ".xlsx": ":abacus:",
        ".json": ":scroll:",
        ".docx": ":memo:"
    }

    if 'additional_documentation' not in st.session_state:
        st.session_state['additional_documentation'] = ""
    if 'json_interviniente_cliente' not in st.session_state:
        st.session_state['json_interviniente_cliente'] = ""    
    if 'selected_case' not in st.session_state or st.session_state['selected_case'] is None:
        utils.alert_and_redirect()

    narrative_path = os.path.join(os.getenv("CASE_DATA_PATH", ""), os.getenv("NARRATIVE_FOLDER", ""))

    st.markdown(f'## Documentation for case `{st.session_state["selected_case"]}`')

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1.status("Retrieving data...", expanded=True) as status:
        for file in st.session_state['additional_documentation'].keys():
            st.write(f"{file_emojis.get(os.path.splitext(file)[1], '')} {file}")
        status.update(label="Documentación y explicación aportada", state="complete", expanded=True)

    with col2.status("Retrieving data...", expanded=True) as status:
        for file in st.session_state['additional_documentation_principal_implicado'].keys():
            st.write(f"{file_emojis.get(os.path.splitext(file)[1], '')} {file}")
        status.update(label="Documentación aportada relativa al principal implicado", state="complete", expanded=True)

    with col3.status("Retrieving data...", expanded=True) as status:
        for file in st.session_state['json_interviniente_cliente'].keys():
            st.write(f"{file_emojis.get(os.path.splitext(file)[1], '')} {file}")
        status.update(label="Intervinientes Adicionales", state="complete", expanded=True)


    st.subheader("Quick overview")

    tab1, tab2, tab3 = st.tabs(["Documentación y explicación aportada", "Documentación aportada relativa al principal implicado", "Intervinientes Adicionales"])

    with tab1.container(border=False):
        for filename, content in st.session_state['additional_documentation'].items():
            st.markdown(f"##### {filename}")
            with st.container(border=True, height=400):
                st.text(content)

    with tab2.container(border=False):
        for filename, content in st.session_state['additional_documentation_principal_implicado'].items():
            st.markdown(f"##### {filename}")
            with st.container(border=True, height=400):
                st.text(content)

    with tab3.container(border=False):
        for filename, content in st.session_state['json_interviniente_cliente'].items():
            st.markdown(f"##### {filename}")
            with st.container(border=True, height=400):
                st.text(content)


    utils.show_selected_case()


except Exception:
    st.error(traceback.format_exc())
