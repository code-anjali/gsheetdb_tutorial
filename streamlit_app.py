# streamlit_app.py

import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import json

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
# @st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    return json.dumps({"rows": rows})


sheet_url = st.secrets["private_gsheets_url"]
rows_dict = json.loads(run_query(f'SELECT * FROM "{sheet_url}"'))

# Print results.
for row in rows_dict["rows"]:
    st.write(f"{row.name} has a :{row.pet}:")
