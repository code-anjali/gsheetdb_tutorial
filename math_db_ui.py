import json

import pandas as pd
import streamlit as st
from shillelagh.backends.apsw.db import connect, Cursor

import logging

logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO)


def establish_connection(sheet_key, sheet_names_json=".streamlit/sheet_names.json"):
    if "conn" not in st.session_state or "sheet_url" not in st.session_state or st.session_state.conn.closed:
        with open(sheet_names_json, 'r') as sheets:
            secrets = json.load(sheets)
        st.session_state.conn = connect(":memory:", adapter_kwargs={
            "gsheetsapi": {"service_account_file": ".streamlit/googlesheetdb-credentials.json"}})
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
    establish_connection(sheet_key="math challenge")
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

        # st.title("Update")
        # pet_to_update = st.selectbox("Pet:" , ['dog', 'cat', 'mouse', 'bird'])
        # update_pet = st.text_input("Update the pet name")
        # user_clicked = st.form_submit_button(label="Update")
        # if user_clicked:
        #     logging.info(f"field_to_update (PET); item to update = {pet_to_update} , replace_with_value = {update_pet}")
        #     result = update_pet_query(pet_to_update.strip().lower(), update_pet=update_pet.strip().lower())
        #     print_updated_rows(result)
        #
        # st.title("Delete")


