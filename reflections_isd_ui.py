from dataclasses import dataclass
from typing import List

import streamlit as st
import pandas as pd
import json

from shillelagh.backends.apsw.db import connect
import logging

from math_db_ui import establish_connection, init_sheet_url

st.set_page_config(layout="wide")  # page, layout setup


@dataclass
class ReflectionsRecord:
    email: str
    name: str
    school: str
    art_cat: str
    art_stm: str
    url: str

    def is_valid(self) -> bool:
        if self.email and self.name and self.school and self.art_cat and self.art_stm and self.url:
            return True
        return False

    @staticmethod
    def get_header() -> List[str]:
        return ["chair_email","name","school","art_category","artist_statement","google_drive_url"]

    def get_pd_row(self) -> List[str]:
        return [self.email,self.name,self.school,self.art_cat,self.art_stm,self.url]

    def get_db_row(self) -> str:
        return f"('{self.email}','{self.name}','{self.school}','{self.art_cat}','{self.art_stm}','{self.url}')"
        # ('1aaa@gmail.com',	'cc', 'discovery2',	'dvdfvvds',	'sdferr', 'url1')
        # return (self.email,self.name,self.school,self.art_cat,self.art_stm,self.url)


def run_search_query(search_query, sheet_key):
    logging.info(f"Check artwork submissions: {search_query}")
    query = f'SELECT * FROM "{st.session_state[sheet_key]}" WHERE school=\'{search_query}\''
    logging.info(f"Querying DB: {query}")
    rows = st.session_state.conn.execute(query)
    return rows


def insert_query(reflections_records, sheet_key):
    # The following is a sample query
    # f'INSERT INTO "{db.sheet_url}" (person, pet)  VALUES (\'NAME1\',\'PET1\')'
    logging.info(f"Saving records")
    query = f'INSERT INTO  "{st.session_state[sheet_key]}"  VALUES {reflections_records}'
    logging.info(f"Querying DB: {query}")
    rows = st.session_state.conn.execute(query)
    # logging.info(f"rows:  {rows}")
    return rows


def print_results(rows, header, column_handler=None):
    logging.info(f"Retrieved: {'some' if rows else '0'} results.")
    logging.info(f"Retrieved: {rows}")
    df = pd.DataFrame(rows, columns=header)
    if column_handler:
        column_handler.table(df)
    else:
        st.table(df)
    # for row_id, row in enumerate(df):
    #     st.write(f"{df}")
    # https://www.askpython.com/python-modules/pandas/add-rows-to-dataframe


def add_row_preserving_old_state(i):
    email = st.text_input(label=f"Chairs email {i}", key=f"TXT_EMAIL_{i}")
    nam = st.text_input(label=f"Student Name {i}", key=f"TXT_NM_{i}")
    sch = st.text_input(label=f"School", key=f"TXT_SC_{i}")
    cat = st.text_input(label=f"Art Category", key=f"TXT_AC_{i}")
    stm = st.text_input(label=f"Artist Statement", key=f"TXT_AS_{i}")
    url = st.text_input(label=f"Google drive URL", key=f"TXT_URL_{i}")
    # st.checkbox(label=f"Is student [{i}] selected?", key=f"CHK_{i}")

    record = ReflectionsRecord(
        email=email,
        name=nam,
        school=sch,
        art_cat=cat,
        art_stm=stm,
        url=url
    )
    if "RECORDS" not in st.session_state:
        # initialize records
        st.session_state["RECORDS"]: List[ReflectionsRecord] = []

    st.session_state["RECORDS"].append(record)
    st.markdown("""---""")  # hline


def save_as_df():
    df = pd.DataFrame([["A", "2", "Yes"], ["B", "1", "Yes"], ["C", "3", "No"]],
                      columns=["Artist name", "Artist Statement", "Student selected"])
    return df


def rank_condition(v):
    if v == "1":
        return "First"
    elif v == "2":
        return "Second"
    elif v == "3":
        return "Third"
    else:
        return v


def make_pretty(styler):
    # st.dataframe(df.style.highlight_max(axis=0))
    styler.highlight_max(axis=None)
    styler.set_caption("Submitted entries")
    styler.format(rank_condition)
    styler.background_gradient(axis=None, vmin=1, vmax=5, cmap="Pastel2")
    return styler


def spaces(n: int, column_handler=None):
    for i in range(n):
        if column_handler:
            column_handler.write("")
        else:
            st.write("")


if __name__ == '__main__':
    sheet_key = "reflections-submissions"
    establish_connection(in_localhost=False)
    init_sheet_url(sheet_key=sheet_key)

    left, right = st.columns(2)
    left.title("Submit entries.")
    spaces(2, left)
    right.title("Verify or lookup entries.")
    spaces(2, right)
    # right.image("image.png", width=300)

    with right.form("form1"):
        search_query = right.text_input("Search by school name")
        # search_query = search_query.lower().replace("school","").replace("elementary","").replace("high","").replace("middle","")
        user_clicked = st.form_submit_button(label="Search")
        if user_clicked:
            result = run_search_query(search_query=search_query.strip().lower(), sheet_key=sheet_key)
            print_results(result, header=ReflectionsRecord.get_header(), column_handler=right)

    if 'total_rows' not in st.session_state:  # maintain total_rows
        st.session_state.total_rows = 1

    if left.button(label="add a row"):  # if new row must be added.
        st.session_state.total_rows += 1

    with left.form("schoolForm"):
        for i in range(1, st.session_state.total_rows + 1):  # add new row and maintain old states on prior rows
            add_row_preserving_old_state(i)

        if st.form_submit_button(label="save"):
            pd_rows = [record.get_pd_row() for record in st.session_state["RECORDS"] if record.is_valid()]
            comma = ","
            db_rows_str = comma.join([record.get_db_row() for record in st.session_state["RECORDS"] if record.is_valid()])
            df = pd.DataFrame(data = pd_rows, columns=ReflectionsRecord.get_header())
            right.write(f"saving the following {len(pd_rows)} records")
            right.table(df)
            # st.table(df.style.pipe(make_pretty))  # TODO styler object on df.
            # st.write(f"db insert query looks like:\n{db_rows_str}")
            if db_rows_str:
                insert_query(reflections_records=db_rows_str, sheet_key=sheet_key)
                spaces(2, left)
                left.success(f"successfully submitted {st.session_state.total_rows} entries so far")
                left.balloons()
            else:
                left.error(f"No record to save. Try again after adding content.")
