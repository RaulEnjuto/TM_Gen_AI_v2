import json
import os
import traceback
import io

from typing import List, Optional, Dict

import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from utilities import utils
from utilities.enums import CaseTypes
from utilities.prompts import Prompts
from utilities.azureblobstorage import AzureBlobStorageClient


@st.cache_data
def read_additional_documentation(_blob_client: AzureBlobStorageClient, narrative_path: str, case: str) -> Dict[str, str]:
    files = _blob_client.get_container_files(folder_name=os.path.join(narrative_path, case))
    files_content = {}
    for file in files:
        if os.path.splitext(file)[1] == ".docx":
            with open("dummy_filename.docx", 'wb') as f:
                f.write(_blob_client.get_file(file))
                docx_file = utils.get_docx_text(f.name)
            files_content[file] = docx_file
    return files_content

@st.cache_data
def read_additional_json_files(_blob_client: AzureBlobStorageClient, narrative_path: str, case: str) -> Dict[str, dict]:
    json_files = _blob_client.get_container_files(folder_name=os.path.join(narrative_path, case))
    json_files_content = {}
    for file in json_files:
        if os.path.splitext(file)[1] == ".json":
            with open("dummy_filename.json", 'wb') as f:
                f.write(_blob_client.get_file(file))
            with open("dummy_filename.json", 'r') as f:
                json_content = json.load(f)
            json_files_content[file] = json_content
    return json_files_content


def reset_selected_case():
    if 'selected_case' in st.session_state:
        # Reset the selected case to None or a valid default value
        st.session_state['selected_case_idx'] = None
        st.session_state['case_selector'] = None
        st.session_state['selected_case'] = None
        st.session_state['alert_data'] = None
        st.session_state['customer_data'] = None
        st.session_state['transactions_df'] = None
        st.session_state['json_interviniente_cliente'] = None

def set_selected_case_idx(filtered_cases: List[str]):
    selected_case = st.session_state['case_selector']
    st.session_state['selected_case_idx'] = filtered_cases.index(selected_case)
    return


@st.cache_data
def read_json(case: str, json_file: str) -> Dict:
    with open(os.path.join(pre_narrative_path, case, json_file), 'r', encoding='utf-8') as file:
        return json.load(file)


def process_excel_tables(xls: pd.ExcelFile, sheet, skip_rows = None, preprocess = True) -> pd.DataFrame:
    if "cuenta" in sheet.title.lower():
        skip_rows = 3
    # df = pd.read_excel(xls, sheet.title, skiprows=skip_rows)
    df = utils.read_excel_with_dynamic_headers(filepath=xls, sheet=sheet.title)
    # Set all NaN values to empty string or 0, depending on the column type
    df = df.fillna({col: "" if df[col].dtype == 'O' else 0 for col in df.columns})
    if preprocess:
        # Standardize float values (remove thousands separator)
        for col in df.select_dtypes(include=['float64']).columns:
            # df[col] = df[col].apply(lambda x: str(x).replace(",", "") if x else x).astype(float)
            df[col] = df[col].abs()
            # If there are less than 3 decimals, round to 0
            # if df[col].apply(lambda x: len(str(x).split(".")[1]) if "." in str(x) else 0).max() < 3:
            #     df[col] = df[col].apply(lambda x: round(x) if x else x)
            # if the column is a percentage (0-1), multiply by 100, and add % symbol
            if df[col].max() <= 1:
                df[col] = df[col].apply(lambda x: f"{int(x*100)}%" if x else x)

    return df


@st.cache_data
def get_excel_tables(case_path: str) -> Dict[str, pd.DataFrame]:
    excel_file = [f for f in files if "Tabla Resumen" in f][0]
    # xls = pd.ExcelFile(os.path.join(case_path, excel_file))
    xls = pd.ExcelFile(io.BytesIO(blob_client.get_file(os.path.join(case_path, excel_file))))
    sheets = xls.book.worksheets

    sheets_data = {}
    for sheet in sheets:
        if sheet.sheet_state == "visible":
            sheet_metadata = {'content': pd.DataFrame, 'tokens': int}
            sheet_metadata['content'] = process_excel_tables(xls, sheet)
            sheet_metadata['tokens'] = utils.num_tokens_from_string(sheet_metadata['content'].to_markdown(index=False))
            sheets_data[sheet.title] = sheet_metadata
    # Sort excel data dataframes by number of tokens
    sheets_data = {k: v for k, v in sorted(sheets_data.items(), key=lambda item: item[1]['tokens'], reverse=False)}
    return sheets_data

@st.cache_data
def get_additional_excel_tables (case_path: str) -> Dict[str, pd.DataFrame]:
    additional_excel_files = [f for f in files if "Intervinientes Adicionales" in f]
    if not additional_excel_files:
        return {}
    additional_excel_file = additional_excel_files[0]
    # xls = pd.ExcelFile(os.path.join(case_path, excel_file))
    additional_xls = pd.ExcelFile(blob_client.get_file(os.path.join(case_path, additional_excel_file)))
    additional_sheets = additional_xls.book.worksheets

    additional_sheets_data = {}
    for additional_sheet in additional_sheets:
        if additional_sheet.sheet_state == "visible":
            additional_sheet_metadata = {'content': pd.DataFrame, 'tokens': int}
            additional_sheet_metadata['content'] = process_excel_tables(additional_xls, additional_sheet)
            additional_sheet_metadata['tokens'] = utils.num_tokens_from_string(additional_sheet_metadata['content'].to_markdown(index=False))
            additional_sheets_data[additional_sheet.title] = additional_sheet_metadata
    # Sort excel data dataframes by number of tokens
    additional_sheets_data = {k: v for k, v in sorted(additional_sheets_data.items(), key=lambda item: item[1]['tokens'], reverse=False)}
    return additional_sheets_data



try:

    st.set_page_config(
        page_title="Case selector - Transaction Monitoring",
        page_icon="📜",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    utils.show_logo()

    file_emojis = {
        ".xlsx": ":abacus:",
        ".json": ":scroll:",
    }

    # pre_narrative_path  = os.path.join(os.getenv("CASE_DATA_PATH", ""), os.getenv("PRE_NARRATIVE_FOLDER", ""))
    # narrative_path      = os.path.join(os.getenv("CASE_DATA_PATH", ""), os.getenv("NARRATIVE_FOLDER", ""))
    pre_narrative_path  = os.getenv("PRE_NARRATIVE_FOLDER", "")
    narrative_path      = os.getenv("NARRATIVE_FOLDER", "")

    blob_client = AzureBlobStorageClient()

    st.header("Case selector - Transaction Monitoring")
    col1, col2 = st.columns(2)

    if 'selected_case_idx' not in st.session_state:
        st.session_state['selected_case_idx'] = None

    with col1:
        case_type = st.radio("(1) Select case type", options=[t.value for t in CaseTypes], key="case_type_selector")
        # filtered_cases = utils.list_cases(pre_narrative_path, filter_by_word=CaseTypes.get(case_type), full_path=False)
        filtered_cases = blob_client.list_cases(pre_narrative_path, filter_by_word=CaseTypes.get(case_type), full_path=False)
        pass

    with col2:
        selected_case = st.radio("(2) Select case", options=filtered_cases, index=st.session_state['selected_case_idx'], key="case_selector", on_change=set_selected_case_idx, args=(filtered_cases,))
        st.session_state['selected_case'] = selected_case

    if st.session_state['selected_case']:
        print(f"Selected case: {st.session_state['selected_case']}, index: {st.session_state['selected_case_idx']}")
        st.subheader("Case data")

        with st.status("Retrieving data...", expanded=True) as status:
            # files = utils.get_files_in_folder(os.path.join(pre_narrative_path, st.session_state['selected_case']))
            files = blob_client.get_container_files(folder_name=os.path.join(pre_narrative_path, st.session_state['selected_case']), full_path=False)
            case_path = os.path.join(pre_narrative_path, st.session_state['selected_case'])

            for file in files:
                st.write(f"{file_emojis.get(os.path.splitext(file)[1], '')} {file}")

            status.update(label="Case data retrieved", state="complete", expanded=True)

        st.subheader("Quick overview")

        my_bar = st.progress(0, text="Loading Alert JSON data...")

        col1, col2 = st.columns(2)
        with col1:
            alert_data = utils.load_json(
                case=st.session_state['selected_case'],
                keywords=["Alerta", "alerta", "Alert", "alert"],
                files=files,
                folder=pre_narrative_path,
                _blob_client=blob_client
            )
            st.session_state['alert_data'] = alert_data
            if alert_data:
                st.session_state['numero_cuenta'] = alert_data[0].get("numero_cuenta", "")
            else:
                st.session_state['numero_cuenta'] = ""

        my_bar.progress(25, text="Loading Customer JSON data...")
        
        with col2:
            customer_data = utils.load_json(
                case=st.session_state['selected_case'],
                keywords=["Cliente", "cliente", "Customer", "customer"],
                files=files,
                folder=pre_narrative_path,
                _blob_client=blob_client
            )
            st.session_state['customer_data'] = customer_data

        my_bar.progress(50, text="Loading Excel data...")
    
        with st.container(border=True):
            st.session_state['excel_data'] = get_excel_tables(case_path)
            sheet_names = [sheet for sheet in st.session_state['excel_data'].keys()]
            with st.expander("Include/exclude tables for the narrative"):
                selected_sheet_names = st.multiselect("Selected:", options=sheet_names, default=sheet_names)
            total_num_tokens = 0
            for tab, sheet in zip(st.tabs(selected_sheet_names), selected_sheet_names):
                df = st.session_state['excel_data'][sheet]['content']
                sheet_tokens = st.session_state['excel_data'][sheet]['tokens']
                total_num_tokens += sheet_tokens
                tab.write(f"{sheet} contains: **{sheet_tokens:,} tokens**")
                tab.dataframe(df)
            st.write(f"Total selected tables contain: **{total_num_tokens:,} tokens**")

            # Set transactions data joining all selected tables into a Markdown string with the title of each table
            transactions_md = ""
            for sheet in selected_sheet_names:
                transactions_md += f"### {sheet}:\n\n"
                transactions_md += st.session_state['excel_data'][sheet]['content'].to_markdown(index=False, floatfmt=".0f") + "\n\n"
            st.session_state['transactions_df'] = transactions_md

        with st.container(border=True):
            st.session_state['additional_excel_data'] = get_additional_excel_tables(case_path)
            additional_sheet_names = [additional_sheet for additional_sheet in st.session_state['additional_excel_data'].keys()]
            with st.expander("Include/exclude tables for the narrative"):
                selected_additional_sheet_names = st.multiselect("Selected:", options=additional_sheet_names, default=additional_sheet_names)
            additional_total_num_tokens = 0
            if selected_additional_sheet_names:
            # Asegurarse de que todas las hojas seleccionadas sean cadenas
                selected_additional_sheet_names = [str(additional_sheet) for additional_sheet in selected_additional_sheet_names]
                for tab, additional_sheet in zip(st.tabs(selected_additional_sheet_names), selected_additional_sheet_names):
                    additional_df = st.session_state['additional_excel_data'][additional_sheet]['content']
                    additional_sheet_tokens = st.session_state['additional_excel_data'][additional_sheet]['tokens']
                    additional_total_num_tokens += additional_sheet_tokens
                    tab.write(f"{additional_sheet} contains: **{additional_sheet_tokens:,} tokens**")
                    tab.dataframe(additional_df)
                st.write(f"Total selected tables contain: **{additional_total_num_tokens:,} tokens**")
            else:
                st.write("No additional tables selected.")        


            # Set transactions data joining all selected tables into a Markdown string with the title of each table
            additional_transactions_md = ""
            for sheet in selected_additional_sheet_names:
                additional_transactions_md += f"### {sheet}:\n\n"
                additional_transactions_md += st.session_state['additional_excel_data'][sheet]['content'].to_markdown(index=False, floatfmt=".0f") + "\n\n"
            st.session_state['additional_transactions_df'] = additional_transactions_md            

        my_bar.progress(75, text="Loading additional documentation...")

        ## Automatically upload additional documentation:

        # additional_docu = utils.read_additional_documentation(narrative_path=narrative_path, case=st.session_state['selected_case'])
        additional_docu = read_additional_documentation(blob_client, narrative_path=narrative_path, case=st.session_state['selected_case'])
        # Remove os.path.join(narrative, case) from the keys
        case_path = os.path.join(narrative_path, st.session_state['selected_case']).replace("\\", "/") + "/"
        additional_docu = {k.replace(case_path, ""): v for k, v in additional_docu.items()}
        additional_docu_principal_implicado = {}

        for filename in list(additional_docu):
            folder, basename = os.path.split(filename)
            if "Correos" not in folder and "Docu Aportada" not in folder:
                print(folder)
                element = additional_docu.pop(filename)
                additional_docu_principal_implicado[filename] = element

        text_join_fn = lambda text, dic: "\n\n".join([f"### {text} \"{filename}\":\n\n{content}" for filename, content in dic.items()])

        additional_docu_text = text_join_fn("Documentación y explicación aportada", additional_docu)
        additional_docu_principal_implicado_text = text_join_fn("Documentación aportada relativa al principal implicado", additional_docu_principal_implicado)

        st.session_state['additional_documentation'] = additional_docu
        st.session_state['additional_documentation_text'] = additional_docu_text

        st.session_state['additional_documentation_principal_implicado'] = additional_docu_principal_implicado
        st.session_state['additional_documentation_principal_implicado_text'] = additional_docu_principal_implicado_text


        json_interviniente_cliente = read_additional_json_files(blob_client, narrative_path=narrative_path, case=st.session_state['selected_case'])
        case_path = os.path.join(narrative_path, st.session_state['selected_case']).replace("\\", "/") + "/"
        json_interviniente_cliente = {k.replace(case_path, ""): v for k, v in json_interviniente_cliente.items()}
        json_interviniente_cliente_text = text_join_fn("JSON de Intervinientes Adicionales", json_interviniente_cliente)

        st.session_state['json_interviniente_cliente'] = json_interviniente_cliente
        st.session_state['json_interviniente_cliente_text'] = json_interviniente_cliente_text

        ## Load Playbook (.docx) file from Azure Blob Storage to inject into the base prompt:
        
        playbook_filename = os.getenv("PLAYBOOK_FILENAME", "")
        playbook = utils.get_docx_text(blob_client.get_file(playbook_filename))

        with st.status(f"Playbook «{playbook_filename}» loaded successfully", expanded=False):
            st.write(playbook)

        ## Load alert_assessment files to inject into the base prompt:

        try:
            if case_type == CaseTypes.ALL.value:
                # Get case type from the selected case abbreviation and value from CaseTypes enum
                abbrev = st.session_state['selected_case'].split(" - ")[1]
                parsed_case_type = CaseTypes.get_value(abbrev)
            else:
                parsed_case_type = case_type
            
            alert_assessment_filename = str(parsed_case_type) + ".docx"
            alert_assessment = utils.get_docx_text(blob_client.get_file(alert_assessment_filename))
            with st.status(f"Alert assessment «{alert_assessment_filename}» loaded successfully", expanded=False):
                st.write(alert_assessment)
        except:
            alert_assessment = "No alert assessment found for this case type."
            st.warning(alert_assessment)
        

        ### Build BASE PROMPT

        st.session_state['base_prompt'] = Prompts.base_prompt(
            alert_data=st.session_state['alert_data'],
            customer_data=st.session_state['customer_data'],
            transactions_df=st.session_state['transactions_df'],
            playbook=playbook,
            alert_assessment=alert_assessment,
        )

        # Show number of tokens of the base prompt
        st.info(f"Base prompt contains: **{utils.num_tokens_from_string(st.session_state['base_prompt']):,} tokens**")

        col1, col2 = st.columns(2)
        with col1:
            st.button("Select a new case", type="secondary", use_container_width=True, on_click=reset_selected_case)
        with col2:
            if st.button("📄 Generate new pre-narrative", type="primary", use_container_width=True):
                st.session_state['auto_generate_answers'] = True
                switch_page("Pre-narrative")
        
        my_bar.progress(100, text="Case data loaded successfully ✅")
        st.toast("Case data loaded successfully!", icon="✅")

    utils.show_selected_case()


except Exception:
    st.error(traceback.format_exc())
