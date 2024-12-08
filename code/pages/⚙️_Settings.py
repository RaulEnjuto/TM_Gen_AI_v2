import os
import inspect
import traceback

import streamlit as st
import openai

from utilities import utils
from utilities.prompts import Prompts

gpt_model = os.getenv("OPENAI_MODEL_NAME")
cases_data = os.path.join(os.getenv("CASE_DATA_PATH", ""), os.getenv("PRE_NARRATIVE_FOLDER", ""))
temperature = os.getenv("OPENAI_MODEL_TEMPERATURE", 0.1)

variable_dict = {
    'gpt_model': 'GPT Model',
    'llm_temperature': 'Temperature',
    'cases_data': 'Cases Data',
}

def update_env_vars(
    openai_model=None,
    llm_temperature=None,
    cases_folder_path=None,
):
    params = locals()
    for param in inspect.signature(update_env_vars).parameters:
        if params[param] is not None and os.environ.get(param.upper()) != str(params[param]):
            os.environ[param.upper()] = str(params[param])
            st.success(f"Updated **{param.upper()}** to **{params[param]}**")

try:

    st.set_page_config(
        page_title="Settings - Transaction Monitoring",
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    utils.check_password_expiry()
    utils.show_logo()
    utils.show_selected_case()

    client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
    models = sorted([model.id for model in client.models.list()])
    default_model_idx = models.index(gpt_model) if gpt_model in models else 0


    st.subheader("General settings")
    gpt_model = st.selectbox(label=variable_dict['gpt_model'], options=models, index=default_model_idx, key='gpt_model')
    temperature = st.slider(label=variable_dict['llm_temperature'], min_value=0.0, max_value=1.0, value=float(temperature), step=0.1, key='llm_temperature')
    cases_data = st.text_input(label=variable_dict['cases_data'], value=cases_data, key='cases_data')

    # Prompts
    st.subheader("Prompts settings")
    if 'questions' not in st.session_state:
        st.session_state['questions'] = [
            Prompts.naturaleza_alerta(),
            Prompts.principal_implicado(),
            Prompts.contexto_historico(),
            Prompts.analisis_operativa(),
            Prompts.recomendacion_prenarrativa(),
        ]

    text_area_height = 500
    if 'selected_case' in st.session_state and st.session_state['selected_case']:
        if 'base_prompt' not in st.session_state:
            st.session_state['base_prompt'] = Prompts.base_prompt(
            st.session_state['alert_data'],
            st.session_state['customer_data'],
            st.session_state['transactions_df']
            )
        base_prompt = st.text_area("(0) Prompt base (contexto de la tarea y datos)", value=st.session_state['base_prompt'], height=text_area_height, key="base_prompt_field")
    question_1 = st.text_area("(1) ¿Cuál es la naturaleza de la alerta?", value=st.session_state['questions'][0], height=text_area_height, key="question_1")
    question_2 = st.text_area("(2) ¿Quién es el principal implicado?", value=st.session_state['questions'][1], height=text_area_height, key="question_2")
    question_3 = st.text_area("(3) ¿Cuál es el contexto histórico del cliente?", value=st.session_state['questions'][2], height=text_area_height, key="question_3")
    question_4 = st.text_area("(4) Análisis de la operativa del cliente", value=st.session_state['questions'][3], height=text_area_height, key="question_4")
    question_5 = st.text_area("(5) ¿Cuáles son los siguientes pasos aconsejados?", value=st.session_state['questions'][4], height=text_area_height, key="question_5")

    # Save settings if "save settings" button is clicked
    if st.button("Save settings"):
        update_env_vars(
            openai_model=gpt_model,
            llm_temperature=temperature,
            cases_folder_path=cases_data,
        )
        st.session_state['questions'] = [
            question_1,
            question_2,
            question_3,
            question_4,
            question_5,
        ]
        if 'base_prompt' in st.session_state:
            st.session_state['base_prompt'] = base_prompt
        st.toast("Settings saved successfully!", icon="✅")
    else:
        st.toast("Settings not saved. Click the 'Save settings' button at the bottom of the page to save your changes.", icon="⚠️")

except Exception:
    st.error(traceback.format_exc())
