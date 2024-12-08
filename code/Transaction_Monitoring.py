import os
import hmac
import shutil
import json
from pathlib import Path

import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit.source_util import _on_pages_changed, get_pages

from utilities import utils

DEFAULT_PAGE = "Transaction_Monitoring.py"
MEMORY_DB_PATH = "memory.db"
GRAPHS_DIR = "tmp/graphs/"

def get_all_pages():
    default_pages = get_pages(DEFAULT_PAGE)
    pages_path = Path("pages.json")
    if pages_path.exists():
        saved_default_pages = json.loads(pages_path.read_text())
    else:
        saved_default_pages = default_pages.copy()
        pages_path.write_text(json.dumps(default_pages, indent=4))

    # Sort by script_path
    saved_default_pages = {k: v for k, v in sorted(saved_default_pages.items(), key=lambda item: item[1]["script_path"])}
    return saved_default_pages

def clear_all_but_first_page():
    current_pages = get_pages(DEFAULT_PAGE)
    if len(current_pages.keys()) == 1:
        return
    get_all_pages()
    # Keep only the first page
    key, val = list(current_pages.items())[0]
    current_pages.clear()
    current_pages[key] = val
    _on_pages_changed.send()

def show_all_pages():
    current_pages = get_pages(DEFAULT_PAGE)
    saved_pages = get_all_pages()
    page_script_hashes = [page["page_script_hash"] for page in saved_pages.values()]
    missing_keys = set(saved_pages.keys()) - set(current_pages.keys())
    missing_keys = sorted(missing_keys, key=lambda x: page_script_hashes.index(saved_pages[x]["page_script_hash"]))

    for key in missing_keys:
        current_pages[key] = saved_pages[key]

    current_pages = {k: v for k, v in sorted(current_pages.items(), key=lambda item: item[1]["script_path"])}
    _on_pages_changed.send()

clear_all_but_first_page()

def check_password():
    """Check if the user's entered password matches the environment key."""
    # If password already known to be correct, just proceed
    if st.session_state.get("password_correct", False):
        return True

    st.write("You are accessing a restricted service.")

    # Password input field
    password_input = st.text_input("Please enter the credentials provided by your organization:", type="password")

    # A button to confirm password
    if st.button("Login"):
        if hmac.compare_digest(password_input, os.getenv("STREAMLIT_KEY", "")):
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False
            st.error("Wrong credential. Try again or contact your administrator.")

    # Return whether the user is authenticated
    return st.session_state.get("password_correct", False)


if not check_password():
    st.stop()

show_all_pages()

# Delete memory.db if exists
try:
    if os.path.exists(MEMORY_DB_PATH):
        os.remove(MEMORY_DB_PATH)
except Exception as e:
    st.error(f"An error occurred while deleting {MEMORY_DB_PATH}: {e}")
    st.stop()

# Delete tmp/graphs/ directory if exists
try:
    if os.path.exists(GRAPHS_DIR):
        shutil.rmtree(GRAPHS_DIR)
except Exception as e:
    st.error(f"An error occurred while deleting {GRAPHS_DIR} directory: {e}")
    st.stop()

utils.show_logo()
utils.show_selected_case()

switch_page("case selector")
