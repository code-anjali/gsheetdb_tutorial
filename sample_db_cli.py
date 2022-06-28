import toml
import logging
from shillelagh.backends.apsw.db import connect


logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO)


class MyDB:
    def __init__(self, toml_path="secrets.toml"):
        logging.info(f"Establishing connection to Google sheet...")
        self.secrets = toml.load(toml_path)
        self.conn = connect(":memory:", adapter_kwargs={"gsheetsapi": {"service_account_file": ".streamlit/googlesheetdb-credentials.json"}})
        self.sheet_url = self.secrets["private_gsheets_url"]
        logging.info(f"Connection to {self.sheet_url} established? {'no' if self.conn.closed else 'yes'}")

    def run_query(self, query):
        return self.conn.execute(query)


if __name__ == '__main__':
        db = MyDB()
        query1 = f'SELECT * FROM "{db.sheet_url}" WHERE person = \'FFF\''
        query2 = f'INSERT INTO "{db.sheet_url}" (person, pet) VALUES (\'NAME1\',\'PET1\')'
        query3 = f'UPDATE  "{db.sheet_url}"  SET  pet=\'bird\'  WHERE pet=\'cow\''

        rows_dict = db.run_query(query=query3)
        print(f"{rows_dict.rowcount}")

        for row in rows_dict:
            print(f"{row}")
