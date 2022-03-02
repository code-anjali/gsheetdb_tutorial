import streamlit as st
from google.oauth2 import service_account
from shillelagh.backends.apsw.db import connect


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

def update_pet_query(pet_to_update, update_pet):
    logging.info(f"Updating pet: {update_pet}")
    query = f'UPDATE  "{st.session_state.sheet_url}"  SET  pet=\'{update_pet}\'  WHERE pet=\'{pet_to_update}\''
    logging.info(f"Querying DB: {query}")
    rows = st.session_state.conn.execute(query)
    logging.info(f"rows:  {rows}" )
    return rows


def insert_query(columns, values_arr):
    """
    INSERT INTO table1 (column1,column2 ,..)
    VALUES
   (value1,value2 ,...),
   (value1,value2 ,...),
    ...
   (value1,value2 ,...);
    :param arr:
    :return:
    """
    logging.info(f"Updating pet: {update_pet}")
    query = f'INSERT INTO  "{st.session_state.sheet_url}"  VALUES \'{pet_to_update}\''
    logging.info(f"Querying DB: {query}")
    rows = st.session_state.conn.execute(query)
    logging.info(f"rows:  {rows}" )
    return rows

def print_results(rows):
    logging.info(f"Retrieved: {'some' if rows else '0'} results.")
    for row_id, row in enumerate(rows):
        st.write(f"{row.name} has a :{row.pet}:") # prints emoji


def print_updated_rows(rows):
    logging.info(f"Updated: {'some' if rows else '0'} results.")
    st.write( f" {rows} updated.")


if __name__ == '__main__':
    establish_connection()
    with st.form("form1"):
        st.title("Search")
        pet_query = st.text_input("Search by pet name")
        user_clicked = st.form_submit_button(label="Search")
        if user_clicked:
            result = run_pet_query(pet_query=pet_query.strip().lower())
            print_results(result)

        st.title("Update")
        pet_to_update = st.selectbox("Pet:" , ['dog', 'cat', 'mouse', 'bird'])
        update_pet = st.text_input("Update the pet name")
        user_clicked = st.form_submit_button(label="Update")
        if user_clicked:
            logging.info(f"field_to_update (PET); item to update = {pet_to_update} , replace_with_value = {update_pet}")
            result = update_pet_query(pet_to_update.strip().lower(), update_pet=update_pet.strip().lower())
            print_updated_rows(result)

        st.title("Delete")


