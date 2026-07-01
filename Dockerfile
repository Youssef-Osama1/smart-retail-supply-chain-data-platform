FROM apache/airflow:2.10.4-python3.11

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.11.txt" -r /requirements.txt
RUN pip install --no-cache-dir "dbt-core==1.9.*" "dbt-postgres==1.9.*"
