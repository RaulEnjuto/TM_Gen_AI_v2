import os
import traceback
import re
import time

from typing import Dict
from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from utilities import utils
from utilities.enums import QuestionsTypes
from utilities.llm import ReportGenerator
from utilities.prompts import Prompts


def add_currency_symbol(df: pd.DataFrame, keyword_column: str = "importe", symbol: str = "€") -> pd.DataFrame:
    """
    Add currency symbol to a DataFrame column
    """
    # Find the column with the keyword
    df_copy = df.copy()
    currency_columns = [col for col in df_copy.columns if keyword_column in col.lower()]
    if currency_columns:
        for col in currency_columns:
            df_copy[col] = df_copy[col].apply(lambda x: f"{x:,.2f} {symbol}")
    return df_copy


def get_specific_table(keyword: str, format_table: bool = True) -> pd.DataFrame:
    sheets = st.session_state['excel_data'].keys()
    numero_cuenta = st.session_state['numero_cuenta']
    tables = [t for t in sheets if keyword in t.lower()]
    selected_table = None
    
    # If more than one table matches, try to find a match with 'numero_cuenta'
    if len(tables) > 1:
        for table in tables:
            nums = re.findall(r'\d+', table)  # Extract numbers from table name
            for num in nums:
                if num in numero_cuenta:
                    selected_table = table
                    break  # Stop after finding the first match
    
    # If no table was selected by 'numero_cuenta' match or only one table matches
    if not selected_table and tables:
        selected_table = tables[0]
    
    # If a table has been selected, format it if required, and return
    if selected_table:
        table_content = st.session_state['excel_data'][selected_table]['content']
        return add_currency_symbol(table_content) if format_table else table_content
    
    # Return an empty DataFrame if no tables match
    return pd.DataFrame()


def display_narrative():
    if st.session_state['selected_case'] in st.session_state['prenarrative_answers']:
        # Build the full response, by adding the name of the case and joining all the responses
        header = utils.get_narrative_header(
            case=st.session_state['selected_case'],
            timestamp=st.session_state['prenarrative_timestamp'],
            model=os.getenv("OPENAI_MODEL_NAME", ReportGenerator.DEFAULT_MODEL),
            temperature=float(os.getenv("OPENAI_MODEL_TEMPERATURE", 0.0))
        )
        answers = [q["answer"] for q in st.session_state['prenarrative_answers'][st.session_state['selected_case']].values()]
        st.session_state['full_prenarrative'] = header + "\n\n".join(answers)

        with placeholder_narrative.container(border=True):
            for answer in answers:
                if utils.render_graph(answer, case=st.session_state['selected_case']):
                    pass
                else:
                    st.write(answer)
        
        narrative_type = st.radio("Select narrative type", options=["Plain text (.txt)", "Markdown (.md)", "Microsoft Word (.docx)"], index=1)
        if st.session_state.get('prenarrative_timestamp') is None:
            st.session_state['prenarrative_timestamp'] = datetime.now()
        file_name = f"{st.session_state['prenarrative_timestamp'].strftime('%Y%m%d-%H%M')} Pre-narrativa {st.session_state['selected_case']}"
        button_name = f"Download narrative"

        if narrative_type == "Plain text (.txt)":
            st.download_button(button_name, data=utils.md_to_text(st.session_state['full_prenarrative']), file_name=file_name + ".txt", mime="text/plain")
        elif narrative_type == "Markdown (.md)":
            st.download_button(button_name, data=st.session_state['full_prenarrative'], file_name=file_name + ".md", mime="text/markdown")
        elif narrative_type == "Microsoft Word (.docx)":
            st.download_button(button_name, data=utils.save_to_docx(st.session_state['full_prenarrative']).getvalue(), file_name=file_name + ".docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        st.warning('There is no pre-narrative generated for this case. Click "Generate new narrative" to create one.')

def update_progress_bar(progress_bar, progress, total, question, idx):
    progress_bar.progress(
        progress / total,
        text=f'Asking AI about "{question}"... ({idx}/{total})'
    )

def generate_narrative():
    st.session_state['auto_generate_answers'] = False
    st.session_state['prenarrative_answers'][st.session_state['selected_case']] = {}
    st.session_state['full_prenarrative'] = ""

    with col2:
        if st.button("⏹️ Stop generation", type="secondary", use_container_width=True):
            return

    st.toast("Generating narrative with AI...", icon="🤖")

    model = os.getenv("OPENAI_MODEL_NAME", ReportGenerator.DEFAULT_MODEL)
    temperature = float(os.getenv("OPENAI_MODEL_TEMPERATURE", 0.0))
    report_generator = ReportGenerator(prompt=st.session_state['base_prompt'], model=model, temperature=temperature, session_id=st.session_state['selected_case'])
    report_generator.clear_session(st.session_state['selected_case'])

    questions_dict = st.session_state['questions_dict']
    filtered_question_dict = {k: v for k, v in questions_dict.items() if k in st.session_state['questions_to_ask']}

    with placeholder_progress_bar.container(border=False):
        progress_bar = st.progress(0)
        total_questions = len(filtered_question_dict.keys())
    
    # Generate the narrative
    with placeholder_narrative.container(border=True):
        for idx, question in enumerate(filtered_question_dict.keys(), start=1):
            update_progress_bar(
                progress_bar,
                progress=idx - 1,
                total=total_questions,
                question=list(filtered_question_dict.keys())[idx - 1].value,
                idx=idx
            )
            prompt = filtered_question_dict[question]["prompt"]
            
            if question == QuestionsTypes.GRAFO_INTERVINIENTES:
                response = report_generator.ask_question(prompt)
                _ = utils.render_graph(response, case=st.session_state['selected_case'])
            else:
                response = report_generator.ask_question_stream(prompt)
                response = st.write_stream(response)

            # Save answer to the session state, and update pre-narrative answers to questions_dict
            st.session_state['questions_dict'][question]["answer"] = response
            st.session_state['prenarrative_answers'][st.session_state['selected_case']] = st.session_state['questions_dict']
            st.session_state['prenarrative_timestamp'] = datetime.now()

        progress_bar.progress(1.0, text="Narrative generated successfully! ✅")

    placeholder_narrative.empty()
    st.toast("Pre-Narrative generated successfully!", icon="✅")
    st.session_state['auto_generate_answers'] = False
    st.rerun()



try:

    st.set_page_config(
        page_title="Pre-Narrative - Transaction Monitoring",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    utils.show_logo()
    utils.show_selected_case()

    # Ensure a case has been selected
    if 'selected_case' not in st.session_state or st.session_state['selected_case'] is None:
        utils.alert_and_redirect()
    if 'auto_generate_answers' not in st.session_state:
        st.session_state['auto_generate_answers'] = False
    if 'prenarrative_answers' not in st.session_state:
        st.session_state['prenarrative_answers'] = {}
    if 'full_prenarrative' not in st.session_state:
        st.session_state['full_prenarrative'] = ""
    if 'prenarrative_timestamp' not in st.session_state:
        st.session_state['prenarrative_timestamp'] = None

    st.markdown(f'## Pre-narrative for case `{st.session_state["selected_case"]}`')

    st.session_state['tabla_abonos'] = get_specific_table(keyword="abono").to_markdown(index=False, floatfmt=",.2f")
    st.session_state['tabla_cargos'] = get_specific_table(keyword="cargos").to_markdown(index=False, floatfmt=",.2f")

    default_questions = {
        QuestionsTypes.NATURALEZA_ALERTA: Prompts.naturaleza_alerta(),
        QuestionsTypes.PRINCIPAL_IMPLICADO: Prompts.principal_implicado(),
        QuestionsTypes.CONTEXTO_HISTORICO: Prompts.contexto_historico(),
        QuestionsTypes.ANALISIS_OPERATIVA: Prompts.analisis_operativa(st.session_state['tabla_abonos'], st.session_state['tabla_cargos']),
        QuestionsTypes.GRAFO_INTERVINIENTES: Prompts.grafo_intervinientes(),
        QuestionsTypes.RECOMENDACION_INICIAL: Prompts.recomendacion_prenarrativa(),
    }

    with st.expander("Select parts of the pre-narrative to generate"):
        # questions_options = [k.value for k in default_questions.keys()]
        questions = st.multiselect("Selected:", options=default_questions, default=default_questions, format_func=lambda x: x.value, key="questions_to_ask")
        
        # Build questions as a dictionary with "prompt" and "answer" keys for each question
        # if 'questions_dict' not in st.session_state:
        if st.session_state['selected_case'] not in st.session_state['prenarrative_answers']:
            st.session_state['questions_dict'] = {q: {"prompt": default_questions[q], "answer": ""} for q in default_questions}


    col1, col2, col3 = st.columns(3)

    placeholder_progress_bar = st.empty()
    placeholder_narrative = st.empty()

    if col3.button("📄 Generate new pre-narrative", type="primary", use_container_width=True) or st.session_state['auto_generate_answers']:
        generate_narrative()
    display_narrative()

except Exception:
    st.error(traceback.format_exc())
