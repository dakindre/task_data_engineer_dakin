import os
import time
import requests
import json
import yaml as _yaml
from airflow import DAG
from contextlib import contextmanager
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
import extraction.google_sheet_extraction as google_sheet_extraction



item_args = {
    'name': 'test_2',
    'start_date': days_ago(2)
}

dag = DAG(
    dag_id='zoho',
    default_args=item_args,
    description='A dag to interact with zoho API',
    schedule_interval=None
)


class ApiRequest:
  _base_url = "https://inventory.zoho.com/api/v1/organizations?="

  def __init__(self):
    self.zoho_client_id, self.zoho_client_secret, self.zoho_refresh_token = self.get_creds()
    self.zoho_access_token = self.get_access_token()
    self.zoho_org = self.get_zoho_org()


  def get_creds(self):
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'credentials.yml')
    with open(config_path) as config_file:
      creds = _yaml.load(config_file, Loader=_yaml.FullLoader)

      zoho_client_id = creds['zoho']['client_id']
      zoho_client_secret = creds['zoho']['client_secret']
      zoho_refresh_token = creds['zoho']['refresh_token']

      return zoho_client_id, zoho_client_secret, zoho_refresh_token

  def get_access_token(self):
    url = f'https://accounts.zoho.com/oauth/v2/token?refresh_token={self.zoho_refresh_token}&client_id={self.zoho_client_id}&client_secret={self.zoho_client_secret}&redirect_uri=http://www.zoho.com/books&grant_type=refresh_token'
    response = requests.request("POST", url, data = {})

    return response.json()['access_token']


  def get_zoho_org(self):
    url = "https://inventory.zoho.com/api/v1/organizations?="
    headers = {
      'Authorization': f'Zoho-oauthtoken {self.zoho_access_token}'
    }

    response = requests.request("GET", url, headers=headers, data = {})
    return response.json()['organizations'][0]['organization_id']

  def create_zoho_org(self):
    url = "https://inventory.zoho.com/api/v1/organizations?="
    headers = {
      'Authorization': f'Zoho-oauthtoken {self.zoho_access_token}'
    }


  def create_item(self):
    url = f'https://inventory.zoho.com/api/v1/items?organization_id={self.zoho_org}'
    print(url)
    headers = {
      'Authorization': f'Zoho-oauthtoken {self.zoho_access_token}',
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }

    payload = {'JSONString': '{"name": "test_1"}'}

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())

  def update_zoho_item(self):
    url = f'https://inventory.zoho.com/api/v1/items?organization_id={self.zoho_org}'
    headers = {
      'Authorization': f'Zoho-oauthtoken {self.zoho_access_token}'
    }

    payload = {'JSONString': '{"name": ""}'}

    response = requests.request("POST", url, headers=headers, data = payload)
    print(response.json())

def api_call():
    api = ApiRequest()
    api.create_item()

class DagFactory:
  def __init__(self, dag_id, dag_data, schedule):
        self.dag_id = dag_id
        self.dag_data = dag_data
        self.schedule = schedule
        self.default_args = {
            'owner': 'Drew',
            'start_date': days_ago(2)
        }

  @contextmanager
  def _dag(self):
      with DAG(self.dag_id, default_args=self.default_args, schedule_interval=self.schedule) as dag:
          yield dag

  def org_dag(self):
    with self._dag() as dag:
      task = PythonOperator(
        task_id=self.dag_data['item_name'],
        python_callable=api_call,
        op_kwargs={'random_base': },
        dag=dag
      )
    return dag



organizations, source_of_truth = google_sheet_extraction.get_sheet_data()
for orgs in organizations:
  dag_factory = DagFactory(
    dag_id = orgs['org_id'],
    dag_data = source_of_truth,
    schedule = '@daily'
  )
  dag_factory.org_dag()