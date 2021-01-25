import airflow
import requests
import json
from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

WEBHOOK_URL = "https://hooks.slack.com/services/XXXXXXXXXXXXXXXX"

def slack_noti(context):
    url= WEBHOOK_URL
    print('aaaaaaaaaatest')
    requests.post(url, data = json.dumps({
        'username': 'username',
        'channel': 'channel',
        'icon_url': 'https://xxx.jpeg',
        'attachments': [{
            'title': 'Failed: {}.{}.{}'.format(context['dag'], context['task'], context['execution_date']),
            "color": 'danger'
            }]
        }))

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": airflow.utils.dates.days_ago(1),
    "retries": 1,
    "on_failure_callback": slack_noti,
    "retry_delay": timedelta(minutes=1)
}

dag = DAG("slack_dag", default_args=default_args, catchup=False, schedule_interval="@once")

def success_py():
    # 1/0
    # raise Exception('test fail')
    return 'success'

def fail_py():
    1/0
    return 'fail'

sp = PythonOperator(
    task_id='success_py',
    python_callable=success_py,
    dag=dag,
)

fp = PythonOperator(
    task_id='fail_py',
    python_callable=fail_py,
    dag=dag,
)

sp >> fp