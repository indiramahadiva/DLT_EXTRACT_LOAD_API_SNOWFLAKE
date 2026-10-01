import os
from pathlib import Path
from dotenv import load_dotenv
import snowflake.connector
import pandas as pd

# .env is in the same folder as this file (dashboard_streamlit/)
ENV_PATH = Path(__file__).resolve().parent / ".env"


def query_job_listings(query="SELECT * FROM mart_technical_jobs"):

    load_dotenv(ENV_PATH, override=True)

    with snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        # private_key_file=os.getenv("SNOWFLAKE_RSA_KEY"), # for key-pair authentication
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    ) as conn:

        # Execute the query
        df = pd.read_sql(query, conn)

        return df
