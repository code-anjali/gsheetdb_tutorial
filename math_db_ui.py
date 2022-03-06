import json
import tempfile

import pandas as pd
import streamlit as st
from shillelagh.backends.apsw.db import connect, Cursor

import logging

logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO)


def fill_secrets_from_streamlit(credentials_empty_fp):
    logging.info(f"Filling secrets from streamlit...")
    credentials_filled_temp_fp = tempfile.NamedTemporaryFile(delete=False, suffix='.json').name
    with open(credentials_filled_temp_fp, 'w') as credentials_filled_temp:
        with open(credentials_empty_fp, 'r') as credentials_empty:
            credentials_empty_entries = json.load(credentials_empty)
            logging.info(f"before credentials were: {credentials_empty_entries}")
            for key_to_copy in ["private_key", "private_key_id", "client_id"]:
                credentials_empty_entries[key_to_copy] = st.secrets["gcp_service_account"][key_to_copy]
                assert not credentials_empty_entries[key_to_copy], f"toml from streamlit could not be read for: {key_to_copy}"
            json.dump(credentials_empty_entries, credentials_filled_temp)
            logging.info(f"after credentials are  : {credentials_empty_entries}")
            logging.info(f"saved credentials to   : {credentials_filled_temp}")
    return credentials_filled_temp_fp


def establish_connection(sheet_key,
                         in_localhost=False,
                         sheet_names_json_fp="sheet_names.json",
                         credentials_empty_fp="credentials_empty.json",
                         local_secret_fp=".streamlit/googlesheetdb-credentials.json"
                         ):
    if "conn" not in st.session_state or "sheet_url" not in st.session_state or st.session_state.conn.closed:
        with open(sheet_names_json_fp, 'r') as sheets:
            secrets = json.load(sheets)
        st.session_state.conn = connect(":memory:", adapter_kwargs={
            "gsheetsapi": {"service_account_file": local_secret_fp if in_localhost else fill_secrets_from_streamlit(credentials_empty_fp)}})
        st.session_state.sheet_url = secrets[sheet_key]
        logging.info(f"Connection to {st.session_state.sheet_url} established? {'no' if st.session_state.conn.closed else 'yes'}")


def search_submissions_query(email_arr_query):
    logging.info(f"Querying by email ids: {email_arr_query}")
    where_clause = " OR ".join([f"LOWER([Email Address])=\'{email.strip().lower()}\'" for email in email_arr_query])
    query = f'SELECT "Student first name",	"Student last name", "Math Challenge name", "Question 1", "Question 2", "Question 3", "Question 4", "Question 5", "Question 6", "Question 7", "Question 8", "Question 9", "Question 10", "Question 11", "Question 12", "Question 13", "Question 14", "Question 15", "Question 16", "Question 17", "Question 18" FROM "{st.session_state.sheet_url}" WHERE {where_clause}'
    logging.info(f"Querying DB: {query}")
    rows = st.session_state.conn.execute(query)
    return rows


def print_results(rows: Cursor, header):
    # ValueError: could not convert string to float: '6,931' => Goggle sheets- Format -> number -> plain text
    logging.info(f"Retrieved: {rows.rowcount if rows else '0'} submissions.")
    st.table(data=pd.DataFrame([row for row in rows], columns=header))


if __name__ == '__main__':
    establish_connection(sheet_key="math challenge", in_localhost=False)
    with st.form("form1"):
        st.title("Search")
        student_query = st.text_input("Search by parent email ids")
        user_clicked = st.form_submit_button(label="Search submissions")
        if user_clicked:
            header = ["Student first name", "Student last name", "Math Challenge name", "Question 1", "Question 2",
                      "Question 3", "Question 4", "Question 5", "Question 6", "Question 7", "Question 8", "Question 9",
                      "Question 10", "Question 11", "Question 12", "Question 13", "Question 14", "Question 15",
                      "Question 16", "Question 17", "Question 18"]
            result = search_submissions_query(email_arr_query=student_query.strip().lower().split(','))
            print_results(result, header=header)



