from airflow import DAG
from airflow.models import Variable
from airflow.operators.slack_operator import SlackAPIPostOperator
from airflow.operators.python_operator import PythonOperator
import datetime

def send_slack(context):
    ''' 処理失敗時のcallback
    '''
    op = SlackAPIPostOperator(
          task_id='task_failure',
          token=Variable.get("slack_access_token"),
          text=str(context['exception']),
          channel='#room-name',
          username='user-name')
    return op.execute(context=context)

# 必ず例外が発生する関数
def hello():
    raise Exception('テスト')

args = {
    'owner': 'masato watanabe',
    'start_date': datetime.datetime(2018, 12, 15)
}

dag = DAG('slack_example', default_args=args, schedule_interval='0 0 * * *')

# on_failure_callbackに上で定義したsend_slackを入れる
PythonOperator(
    task_id='hello',
    python_callable=hello,
    on_failure_callback=send_slack,
    dag=dag
)