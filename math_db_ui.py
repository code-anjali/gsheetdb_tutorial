import json
import tempfile
from typing import Dict, List

import pandas as pd
import streamlit as st
from shillelagh.backends.apsw.db import connect, Cursor

import logging

from math_challenge_related.challenge_result_checker import ResultChecker
from math_challenge_related.student_info import StudentInfo

logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.DEBUG)


def fill_secrets_from_streamlit(credentials_empty_fp):
    logging.info(f"Filling secrets from streamlit...")
    credentials_filled_temp_fp = tempfile.NamedTemporaryFile(delete=False, suffix='.json').name
    with open(credentials_filled_temp_fp, 'w') as credentials_filled_temp:
        with open(credentials_empty_fp, 'r') as credentials_empty:
            credentials_empty_entries = json.load(credentials_empty)
            logging.debug(f"before credentials were: {credentials_empty_entries}")
            for key_to_copy in ["private_key", "private_key_id", "client_id"]:
                credentials_empty_entries[key_to_copy] = st.secrets["gcp_service_account"][key_to_copy]
                if not st.secrets["gcp_service_account"][key_to_copy]:
                    return ""
                assert len(credentials_empty_entries[key_to_copy]) > 0, f"toml from streamlit could not be read for: {key_to_copy} --> {st.secrets['gcp_service_account'][key_to_copy]}"
            json.dump(credentials_empty_entries, credentials_filled_temp)
            logging.debug(f"after credentials are  : {credentials_empty_entries}")
            logging.debug(f"saved credentials to   : {credentials_filled_temp}")
    return credentials_filled_temp_fp


def init_sheet_url(sheet_key, sheet_names_json_fp="sheet_names.json"):
    if sheet_key not in st.session_state:
        with open(sheet_names_json_fp, 'r') as sheets:
            secrets = json.load(sheets)
            st.session_state[sheet_key] = secrets[sheet_key]


def establish_connection(in_localhost=False,
                         credentials_empty_fp="credentials_empty.json",
                         local_secret_fp=".streamlit/googlesheetdb-credentials.json"
                         ):
    if "conn" not in st.session_state or st.session_state.conn.closed:
        service_account_file = local_secret_fp if in_localhost else fill_secrets_from_streamlit(credentials_empty_fp)
        if not service_account_file:
            return
        else:
            with open(service_account_file, 'r') as checkcheck:
                checks = json.load(checkcheck)
                if not in_localhost:
                    assert checks["private_key_id"] == st.secrets["gcp_service_account"]["private_key_id"], f"checks['private_key_id']={checks['private_key_id']} \nand\n st.secrets['gcp_service_account']['private_key_id'] = {st.secrets['gcp_service_account']['private_key_id']}"
                else:
                    assert len(checks["private_key_id"]) > 1
        st.session_state.conn = connect(":memory:", adapter_kwargs={
            "gsheetsapi": {"service_account_file": service_account_file}})
        logging.info(f"Connection established? {'no' if st.session_state.conn.closed else 'yes'}")


def load_gold(target_var, gold_sheet_key):
    if target_var not in st.session_state:
        golds: Dict[str, List[str]] = {}
        questions_csv = ", ".join([f'"Question {x}"' for x in range(1, 19)])  # Question 1, Question 2, ... Question 18
        query = f'SELECT "Math Challenge name", {questions_csv} FROM "{st.session_state[gold_sheet_key]}"'
        rows = st.session_state.conn.execute(query)
        for r in rows:
            golds[r[0]] = [x for x in r[1:]]
        st.session_state[target_var] = golds


def fetch_challenges_by_email(email_arr_query, sheet_key):
    logging.info(f"Querying by email ids: {email_arr_query}")
    where_clause = " OR ".join([f"LOWER([Email Address])=\'{email.strip().lower()}\'" for email in email_arr_query])
    questions_csv = ", ".join([f'"Question {x}"' for x in range(1, 19)])
    query = f'SELECT "Student first name",	"Student last name", "Grade", "Teacher\'s name", "Email Address", "Math Challenge name", {questions_csv} FROM "{st.session_state[sheet_key]}" WHERE {where_clause}'
    logging.info(f"Querying DB: {query}")
    rows = st.session_state.conn.execute(query)
    return rows


def prepare_results(rows: Cursor, header):
    # If        : this error is encountered --
    # ValueError: could not convert string to float: '6,931'
    # Then      : Google sheets- Format -> number -> plain text
    logging.info(f"Retrieved: {rows.rowcount if rows else '0'} submissions.")
    assert CHECKER_KEY in st.session_state and st.session_state[CHECKER_KEY] is not None, f"{CHECKER_KEY} for checking results is missing."
    final_rows = []
    short_header = [x.replace('"','').replace("Question ", "Q") for x in header]
    logging.info(f"About to check student answers ... ")
    for row in rows:  # one parent can have multiple kids.
        student = mk_student(row)
        final_rows.append(row)  # student name and answer.
        result = st.session_state[CHECKER_KEY].check_one_challenge(student=student,
                                                                   challenge_nm=row[5],
                                                                   answers_arr=row[6:])
        final_rows.append([f"GOLD:", "", "", "", "", ""] + result.gold_orig_ans)  # gold # "\N{grinning face}")
        final_rows.append([f"pass" if {result.passed} else "fail", "", "", "", "", ""] + ["\N{check mark}" if y=="1" else "\N{cross mark}" for y in result.diagnostics])   # is_ans_correct
        final_rows.append(["", "", "", "", "", ""] + ["" for _ in result.diagnostics])  # empty line
    st.table(data=pd.DataFrame([row for row in final_rows], columns=short_header))
    # st.table(data=[row for row in final_rows])


def load_result_checker(key):
    if key not in st.session_state:
        assert st.session_state[GOLD_DATA_KEY] is not None, f"Result checker requires gold answers which is not loaded."
        st.session_state[key] = ResultChecker(st.session_state[GOLD_DATA_KEY])


CHECKER_KEY="result_checker"
STUDENT_SHEET_KEY="math_challenge"
GOLD_SHEET_KEY="math_challenge_gold"
GOLD_DATA_KEY=f"values_{GOLD_SHEET_KEY}"


def mk_student(row) -> StudentInfo:
    return StudentInfo(f_name=row[0],l_name=row[1],grade=row[2],teacher=row[3],email=row[4])


if __name__ == '__main__':
    st.set_page_config(layout="wide")
    establish_connection(in_localhost=False)
    init_sheet_url(sheet_key=GOLD_SHEET_KEY)
    init_sheet_url(sheet_key=STUDENT_SHEET_KEY)
    load_gold(target_var=GOLD_DATA_KEY, gold_sheet_key=GOLD_SHEET_KEY)
    load_result_checker(key=CHECKER_KEY)
    ques_arr = [f'"Question {x}"' for x in range(1, 19)]

    with st.form("form1"):
        st.title("Report card")
        student_query = st.text_input("Looking by parent email ids (separate by comma if you used multiple email ids)")
        user_clicked = st.form_submit_button(label="Generate report")
        if user_clicked:
            header = ["Student first name", "Student last name", "Grade", "Teacher\s name", "Email Address", "Math Challenge name"] + ques_arr
            responses = fetch_challenges_by_email(email_arr_query=student_query.strip().lower().split(','),
                                                  sheet_key="math_challenge")
            if responses:
                prepare_results(responses, header=header)
