import json

import streamlit as st
import toml
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


def run_pet_query(pet_query):
    logging.info(f"Querying for pet: {pet_query}")
    query = f'SELECT * FROM "{st.session_state.sheet_url}" WHERE pet=\'{pet_query}\''
    logging.info(f"Querying DB: {query}")
    rows = st.session_state.conn.execute(query)
    return rows

def update_pet_query(pet_to_update, update_pet):
    logging.info(f"Updating pet: {update_pet}")
    query = f'UPDATE  "{st.session_state.sheet_url}"  SET  pet=\'{update_pet}\'  WHERE pet=\'{pet_to_update}\''
    logging.info(f"Querying DB: {query}")
    rows = st.session_state.conn.execute(query)
    logging.info(f"rows:  {rows}")
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

def print_results(rows, header=["person", "pet"]):
    logging.info(f"Retrieved: {'some' if rows else '0'} results.")
    for row_id, row in enumerate(rows):
        st.write(f"{row[0]} = :{row[1].lower()}:")  # prints emoji
        # for col_name, col in zip(header, row):
        #     st.write(f"{col_name} = :{col.lower()}:")  # prints emoji


def print_updated_rows(rows):
    logging.info(f"Updated: {'some' if rows else '0'} results.")
    cnt = 0
    for _ in rows:
        cnt += 1
    st.write(f"updated {cnt} items")


if __name__ == '__main__':
    establish_connection(sheet_key="sample_pets")
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


