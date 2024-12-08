import json
import os
import traceback
import openai
import time

from datetime import datetime
from typing import List, Optional, Dict

import pandas as pd
import streamlit as st

from utilities import utils
from utilities.enums import QuestionsTypes
from utilities.llm import ReportGenerator
from utilities.prompts import Prompts


def display_narrative():
    if st.session_state['selected_case'] in st.session_state['narrative_answers']:

        answers = st.session_state['narrative_answers'][st.session_state['selected_case']]
        st.session_state['full_narrative'] = "\n".join([str(answer) if answer is not None else "" for answer in answers])

        with placeholder_narrative.container(border=True):
            for answer in answers:
                if utils.render_graph(answer, case=st.session_state['selected_case']):
                    pass
                else:
                    st.write(answer, unsafe_allow_html=True)
        
        narrative_type = st.radio("Select narrative type", options=["Plain text (.txt)", "Markdown (.md)", "Microsoft Word (.docx)"], index=1)
        file_name = f"{st.session_state['narrative_timestamp'].strftime('%Y%m%d-%H%M')} Narrativa {st.session_state['selected_case']}"
        button_name = f"Download narrative"

        if narrative_type == "Plain text (.txt)":
            st.download_button(button_name, data=utils.md_to_text(st.session_state['full_narrative']), file_name=file_name + ".txt", mime="text/plain")
        elif narrative_type == "Markdown (.md)":
            st.download_button(button_name, data=st.session_state['full_narrative'], file_name=file_name + ".md", mime="text/markdown")
        elif narrative_type == "Microsoft Word (.docx)":
            st.download_button(button_name, data=utils.save_to_docx(st.session_state['full_narrative']).getvalue(), file_name=file_name + ".docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        st.warning('There is no narrative generated for this case. Click "Generate new narrative" to create one.')

def generate_conclusion_final(report_generator, prompt, max_retries=10):
    try:
        if not prompt:
            st.error("Error: El prompt para la Conclusión Final es nulo o inválido.")
            return "Prompt inválido para Conclusión Final."

        response_content = ""
        retries = 0

        while retries < max_retries:
            try:
                for r in report_generator.ask_question_stream(prompt):
                    response_content += r
                # Si obtenemos una respuesta válida, salimos del ciclo
                if response_content:
                    break
            except openai.error.OpenAIError as e:
                st.error(f"OpenAI API error: {e}")
                retries += 1
                st.write(f"Retrying... Attempt {retries}/{max_retries}")
                time.sleep(2)  # Esperamos 2 segundos antes de reintentar
            except Exception as e:
                st.error(f"Error during streaming response: {e}")
                retries += 1
                st.write(f"Retrying... Attempt {retries}/{max_retries}")
                time.sleep(2)

        # Si después de los reintentos no hay respuesta, mostramos un error
        if not response_content:
            return "No response generated from the API after multiple attempts."

        return response_content

    except Exception as e:
        st.error(f"Critical error generating conclusion final: {e}")
        return "Critical error generating the conclusion final."

try:

    st.set_page_config(
        page_title="Narrative - Transaction Monitoring",
        page_icon="📝",
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
    if 'narrative_answers' not in st.session_state:
        st.session_state['narrative_answers'] = {}
    if 'selected_case' not in st.session_state or st.session_state['selected_case'] is None:
        utils.alert_and_redirect()

    st.markdown(f'## Narrative for case `{st.session_state["selected_case"]}`')

    if st.session_state['selected_case'] not in st.session_state['prenarrative_answers']:
        st.warning("There is no pre-narrative generated for this case. Please go to the **Pre-narrative** page to generate one.")
        st.stop()
    if st.session_state['additional_documentation'] == "":
        st.warning("There is no additional documentation available for this case. Please go to the **Additional documentation** page to load it.")
        st.stop()

    with st.status("There is a pre-narrative ready to be used.", expanded=False):
        answers = [q["answer"] for q in st.session_state['prenarrative_answers'][st.session_state['selected_case']].values()]
        full_response = "\n\n".join(answers)
        st.write(full_response)
        # st.write("\n".join(st.session_state['prenarrative_answers'][st.session_state['selected_case']]))
    with st.status("There is additional documentation available.", expanded=False):
        st.text(st.session_state['additional_documentation_text'])

    col1, col2, col3 = st.columns(3)
    placeholder_narrative = st.empty()

    default_questions = {
        QuestionsTypes.NATURALEZA_ALERTA: None,
        QuestionsTypes.PRINCIPAL_IMPLICADO: Prompts.principal_implicado(
            informacion_externa=st.session_state['additional_documentation_principal_implicado']),
        QuestionsTypes.CONTEXTO_HISTORICO: None,
        QuestionsTypes.ANALISIS_OPERATIVA: None,
        QuestionsTypes.GRAFO_INTERVINIENTES: None,
        QuestionsTypes.DOCUMENTACION_ADICIONAL: Prompts.documentacion_adicional(
            documentacion_adicional=st.session_state['additional_documentation']
        ),
        QuestionsTypes.INTERVINIENTES_ADICIONALES: Prompts.intervinientes_adicionales(
            json_interviniente_cliente=st.session_state['json_interviniente_cliente'],
            transactions_interviniente_df=st.session_state['additional_transactions_df']
        ),
        QuestionsTypes.CONCLUSION_FINAL: Prompts.conclusion_final(),
    }
    questions_dict = st.session_state['questions_dict']
    new_questions_dict = {}
    for question in default_questions.keys():
        if question == QuestionsTypes.CONCLUSION_FINAL or question not in questions_dict or default_questions[question] is not None:
            new_questions_dict[question] = {"prompt": default_questions[question], "answer": ""}
        else:
            new_questions_dict[question] = questions_dict[question]
    st.session_state['narrative_questions_dict'] = new_questions_dict

    model = os.getenv("OPENAI_MODEL_NAME", ReportGenerator.DEFAULT_MODEL)
    temperature = float(os.getenv("OPENAI_MODEL_TEMPERATURE", 0.0))
    report_generator = ReportGenerator(prompt=st.session_state['base_prompt'], model=model, temperature=temperature, session_id=st.session_state['selected_case'])

    if col3.button("📄 Generate new narrative", type="primary", use_container_width=True):

        st.session_state['narrative_answers'][st.session_state['selected_case']] = []

        new_questions_dict = st.session_state['narrative_questions_dict']

        with placeholder_narrative.container(border=True):
            for question, details in new_questions_dict.items():
                prompt = details["prompt"]
                if prompt is not None and not details["answer"]:
                    if question == QuestionsTypes.CONCLUSION_FINAL:
                        response = generate_conclusion_final(report_generator, prompt)
                    else:
                        response = ""
                        for fragment in report_generator.ask_question_stream(prompt):
                            response += fragment 
                    st.write(response) 
                    st.session_state['narrative_answers'][st.session_state['selected_case']].append(response)
                else:
                    response = details["answer"]
                    st.session_state['narrative_answers'][st.session_state['selected_case']].append(response)
            st.session_state['narrative_timestamp'] = datetime.now()
            st.write("Narrative Answers:", st.session_state['narrative_answers'])

        placeholder_narrative.empty()
        st.rerun()

    display_narrative()

    utils.show_selected_case()


except Exception:
    st.error(traceback.format_exc())
