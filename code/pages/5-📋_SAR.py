import os
import traceback

from datetime import datetime
from typing import Dict

import streamlit as st

from utilities import utils
from utilities.enums import QuestionsTypesSAR, TemplateNameSAR
from utilities.llm import ReportGenerator
from utilities.prompts import Prompts
from utilities.azureblobstorage import AzureBlobStorageClient


@st.cache_data
def read_docx_template(name: TemplateNameSAR) -> str:
            # Get all .docx files in the folder
            for file in sar_templates:
                if name.value in file:
                    return utils.get_docx_text(blob_client.get_file(file))
            return ""
        

@st.cache_data
def get_default_questions() -> Dict[QuestionsTypesSAR, str]:
    return {
        QuestionsTypesSAR.RESUMEN_EJECUTIVO: Prompts.resumen_ejecutivo(
            template=read_docx_template(TemplateNameSAR.RESUMEN_EJECUTIVO)),
        QuestionsTypesSAR.IDENTIFICACION_INTERVINIENTE: Prompts.identificacion_interviniente(
            template=read_docx_template(TemplateNameSAR.IDENTIFICACION_INTERVINIENTE)),
        QuestionsTypesSAR.DESCRIPCION_OPERACIONES: Prompts.descripcion_operaciones(
            template=read_docx_template(TemplateNameSAR.DESCRIPCION_OPERACIONES)),
        QuestionsTypesSAR.INDICIO_BLANQUEO: Prompts.indicios_blanqueo(
            template=read_docx_template(TemplateNameSAR.INDICIO_BLANQUEO)),
        QuestionsTypesSAR.GESTIONES_COMPROBACIONES: Prompts.gestiones_comprobaciones(
            template=read_docx_template(TemplateNameSAR.GESTIONES_COMPROBACIONES)),
        QuestionsTypesSAR.DOCUMENTACION_REMITIDA: Prompts.documentacion_remitida(
            template=read_docx_template(TemplateNameSAR.DOCUMENTACION_REMITIDA)),
    }


try:

    st.set_page_config(
        page_title="SAR - Transaction Monitoring",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    utils.show_logo()

    file_emojis = {
        ".xlsx": ":abacus:",
        ".json": ":scroll:",
        ".docx": ":memo:"
    }

    sar_data_path = os.getenv("SAR_DATA_FOLDER", "")
    sar_templates_path = os.getenv("SAR_TEMPLATES_FOLDER", "")

    blob_client = AzureBlobStorageClient()

    if 'narrative_answers' not in st.session_state:
        st.session_state['narrative_answers'] = {}
    if 'sar_answers' not in st.session_state:
        st.session_state['sar_answers'] = {}
    if 'selected_case' not in st.session_state or st.session_state['selected_case'] is None:
        utils.alert_and_redirect()

    st.markdown(f'## SAR for case `{st.session_state["selected_case"]}`')

    if st.session_state['selected_case'] not in st.session_state['narrative_answers']:
        st.warning("There is no narrative generated for this case. Please go to the **Narrative** page to generate one.")
        st.stop()
    else:

        with st.status("There is a narrative ready to be used.", expanded=False):
            answers = st.session_state['narrative_answers'][st.session_state['selected_case']]
            full_response = "\n".join(answers)
            st.write(full_response)


    with st.status("Preparing data for SAR generation...", expanded=False):

        files = blob_client.get_container_files(folder_name=os.path.join(sar_data_path, st.session_state['selected_case']), full_path=False)

        col1, col2 = st.columns(2)

        with col1:
            alert_data = utils.load_json(
                    case=st.session_state['selected_case'],
                    keywords=["Alerta", "alerta", "Alert", "alert"],
                    files=files,
                    folder=sar_data_path,
                    _blob_client=blob_client
            )
            st.session_state['alert_data_SAR'] = alert_data

        with col2:
            customer_data = utils.load_json(
                    case=st.session_state['selected_case'],
                    keywords=["Cliente", "cliente", "Customer", "customer"],
                    files=files,
                    folder=sar_data_path,
                    _blob_client=blob_client
                )
            st.session_state['customer_data_SAR'] = customer_data
            if customer_data:
                tipo_documento = customer_data[0].get("identificacion", {}).get("tipo_documento", "")
            st.session_state['persona_fisica'] = False if tipo_documento in ["CIF"] else True

        sar_folder_type = "Persona Fisica" if st.session_state['persona_fisica'] else "Persona Juridica"
        sar_templates = blob_client.get_container_files(folder_name=os.path.join(sar_templates_path, sar_folder_type), full_path=True)

        default_questions: Dict[QuestionsTypesSAR, str] = get_default_questions()

        ## Base prompt SAR
        st.session_state['base_prompt_SAR'] = Prompts.base_prompt_SAR(
            alert_data=st.session_state['alert_data_SAR'],
            customer_data=st.session_state['customer_data_SAR'],
            transactions_df=st.session_state['transactions_df'],
            narrative_output=full_response,
        )

        st.header("Templates")
        col1, col2 = st.columns(2)
        if col1.checkbox("Show base prompt", key="show_base_prompt", value=False):
            st.subheader("Base prompt")
            with st.container(border=True):
                st.write(st.session_state['base_prompt_SAR'])
        if col2.checkbox("Show default questions", key="show_default_questions", value=True):
            for question_name, question in default_questions.items():
                with st.container(border=True):
                    st.subheader(question_name.value)
                    st.write(question)

    model = os.getenv("OPENAI_MODEL_NAME", ReportGenerator.DEFAULT_MODEL)
    temperature = float(os.getenv("OPENAI_MODEL_TEMPERATURE", 0.0))
    report_generator = ReportGenerator(prompt=st.session_state['base_prompt_SAR'], model=model, temperature=temperature, session_id=st.session_state['selected_case'])

    col1, col2, col3 = st.columns(3)
    placeholder_narrative = st.empty()

    if col3.button("📋 Generate new SAR", type="primary", use_container_width=True):
        
        st.session_state['sar_answers'][st.session_state['selected_case']] = []

        with placeholder_narrative.container(border=True):
            for question_type, question in default_questions.items():
                if question_type.value == QuestionsTypesSAR.INDICIO_BLANQUEO.value:
                    response = report_generator.ask_question(question)
                    st.write(response)
                else:
                    response = report_generator.ask_question_stream(question)
                    response = st.write_stream(response)
                st.session_state['sar_answers'][st.session_state['selected_case']].append(response)
                st.session_state['sar_timestamp'] = datetime.now()
        placeholder_narrative.empty()
        st.rerun()

    if st.session_state['selected_case'] in st.session_state['sar_answers']:

        answers = st.session_state['sar_answers'][st.session_state['selected_case']]
        st.session_state['full_SAR'] = "\n".join(answers)

        with placeholder_narrative.container(border=True):
            for answer in answers:
                st.write(answer)

        narrative_type = st.radio("Select narrative type", options=["Plain text (.txt)", "Markdown (.md)", "Microsoft Word (.docx)"], index=1)
        file_name = f"{st.session_state['narrative_timestamp'].strftime('%Y%m%d-%H%M')} SAR {st.session_state['selected_case']}"
        button_name = f"Download SAR"

        if narrative_type == "Plain text (.txt)":
            st.download_button(button_name, data=utils.md_to_text(st.session_state['full_SAR']), file_name=file_name + ".txt", mime="text/plain")
        elif narrative_type == "Markdown (.md)":
            st.download_button(button_name, data=st.session_state['full_SAR'], file_name=file_name + ".md", mime="text/markdown")
        elif narrative_type == "Microsoft Word (.docx)":
            st.download_button(button_name, data=utils.save_to_docx(st.session_state['full_SAR']).getvalue(), file_name=file_name + ".docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    utils.show_selected_case()


except Exception:
    st.error(traceback.format_exc())
