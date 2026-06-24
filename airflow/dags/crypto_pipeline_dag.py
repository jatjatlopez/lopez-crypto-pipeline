from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

DATABRICKS_CONN_ID = "databricks_default"

with DAG(
    dag_id="crypto_pipeline",
    description="Fetch crypto data, upload to S3, trigger Databricks lakehouse",
    default_args=default_args,
    start_date=datetime(2026, 6, 22),
    schedule_interval="0 */4 * * *",
    catchup=False,
    tags=["crypto", "ingestion", "databricks"],
) as dag:

    fetch_prices = BashOperator(
        task_id="fetch_prices",
        bash_command="cd /opt/airflow/ingestion && pip install -q -r /opt/airflow/ingestion/../requirements.txt && python fetch_prices.py",
    )

    fetch_sentiment = BashOperator(
        task_id="fetch_sentiment",
        bash_command="cd /opt/airflow/ingestion && python fetch_sentiment.py",
    )

    run_bronze = DatabricksSubmitRunOperator(
        task_id="run_bronze_notebook",
        databricks_conn_id=DATABRICKS_CONN_ID,
        json={
            "run_name": "airflow_bronze",
            "tasks": [
                {
                    "task_key": "bronze",
                    "notebook_task": {
                        "notebook_path": "/Workspace/Users/lopezjatjat10@gmail.com/lopez-crypto-pipeline/notebooks/01_bronze_layer",
                    },
                }
            ],
        },
    )

    run_silver = DatabricksSubmitRunOperator(
        task_id="run_silver_notebook",
        databricks_conn_id=DATABRICKS_CONN_ID,
        json={
            "run_name": "airflow_silver",
            "tasks": [
                {
                    "task_key": "silver",
                    "notebook_task": {
                        "notebook_path": "/Workspace/Users/lopezjatjat10@gmail.com/lopez-crypto-pipeline/notebooks/02_silver_layer",
                    },
                }
            ],
        },
    )

    run_gold = DatabricksSubmitRunOperator(
        task_id="run_gold_notebook",
        databricks_conn_id=DATABRICKS_CONN_ID,
        json={
            "run_name": "airflow_gold",
            "tasks": [
                {
                    "task_key": "gold",
                    "notebook_task": {
                        "notebook_path": "/Workspace/Users/lopezjatjat10@gmail.com/lopez-crypto-pipeline/notebooks/03_gold_layer",
                    },
                }
            ],
        },
    )

    fetch_prices >> fetch_sentiment >> run_bronze >> run_silver >> run_gold

