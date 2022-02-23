import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect

import logging

logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO)


def establish_connection():
    if "conn" not in st.session_state or "sheet_url" not in st.session_state or st.session_state.conn.closed:
        logging.info(f"Establishing connection to Google sheet...")
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
            ],
        )
        st.session_state.conn = connect(credentials=credentials)
        st.session_state.sheet_url = st.secrets["private_gsheets_url"]
        logging.info(f"Connection to {st.session_state.sheet_url} established? {'no' if st.session_state.conn.closed else 'yes'}")


def run_pet_query(pet_query):
    logging.info(f"Querying for pet: {pet_query}")
    query = f'SELECT * FROM "{st.session_state.sheet_url}" WHERE pet=\'{pet_query}\''
    logging.info(f"Querying DB: {query}")
    rows = st.session_state.conn.execute(query, headers=1)
    return rows


def print_results(rows):
    logging.info(f"Retrieved: {'some' if rows else '0'} results.")
    for row_id, row in enumerate(rows):
        st.write(f"{row.name} has a :{row.pet}:") # prints emoji


if __name__ == '__main__':
    establish_connection()
    with st.form("form1"):
        st.title("search func")
        pet_query = st.text_input("search by pet")
        user_clicked = st.form_submit_button(label="search now")
        if user_clicked:
            result = run_pet_query(pet_query=pet_query.strip().lower())
            print_results(result)


