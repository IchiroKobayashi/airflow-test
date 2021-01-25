# coding: utf-8
import airflow
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
import re
import json
import requests
from datetime import timedelta

# webhook URLやチャンネル名などを指定
WEBHOOK_URL = "https://hooks.slack.com/services/XXXXXXXXXX"
WEBHOOK_NAME = "webhookName"
CHANNEL_NAME = "channelName"
webhook_url = WEBHOOK_URL
webhook_name = WEBHOOK_NAME
channel_name = WEBHOOK_URL

# タスク失敗を通知する関数
def failured(context):
    dag_name = re.findall(r'.*\:\s(.*)\>', str(context['dag']))[0]
    task_name = re.findall(r'.*\:\s(.*)\>', str(context['task']))[0]
    data = {
            'username': webhook_name,
            'channel': channel_name,
            'attachments': [{
                'title': 'Failed: {}.{}.{}'.format(context['dag'], context['task'], context['execution_date']),
                "color": 'danger',
                'text': dag_name+':'+task_name+' was failed!'
            }]
    }
    requests.post(webhook_url, json.dumps(data))

# タスク成功を通知する関数
def successed(context):
    dag_name = re.findall(r'.*\:\s(.*)\>', str(context['dag']))[0]
    data = {
            'username': webhook_name,
            'channel': channel_name,
            'attachments': [{
                'title': 'Failed: {}.{}.{}'.format(context['dag'], context['task'], context['execution_date']),
                "color": 'danger',
                'text': dag_name+' was succeeded!'
            }]
    }
    requests.post(webhook_url, json.dumps(data))

# 共通すべてのタスクに持たせる引数
default_args = {
        'owner': 'airflow',
        'email': ['xxxxxxxxx@ssss.com'],
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 0,
        # 'retry_delay': timedelta(minutes=5),
        'start_date': airflow.utils.dates.days_ago(1),
        # 'end_date': datetime(2016, 1, 1),
        'on_failure_callback': failured # すべてのタスクについて失敗時に通知する
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_success_callback': some_other_function,
        # 'on_retry_callback': another_function,
        # 'sla_miss_callback': yet_another_function,
        # 'trigger_rule': 'all_success'
        }

with DAG(
        dag_id='noti_test',
        default_args=default_args,
        schedule_interval="@once"
        ) as dag:

    def function1():
        print('function1')
    def function2():
        print('function2')
    def function3():
        1/0
        print('function3')

    op1 = PythonOperator(
            task_id='op1',
            python_callable=function1,
            dag=dag
            )
    op2 = PythonOperator(
            task_id='op2',
            python_callable=function2,
            dag=dag,
            #depends_on_past=False,
            )
    op3 = PythonOperator(
            task_id='op3',
            python_callable=function3,
            on_success_callback=successed, # 最後のタスクの成功を通知する
            dag=dag
            )

    op1 >> op2 >> op3

if __name__ == '__main__':
    dag.cli()