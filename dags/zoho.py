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

class ApiRequest:
  _base_url_access = 'https://accounts.zoho.com/oauth/v2/token?refresh_token='
  _base_url = "https://inventory.zoho.com/api/v1/"

  def __init__(self, org_data):
    self.client_id, self.client_secret, self.refresh_token = self.get_creds()
    self.access_token = self.get_access_token()
    self.header = {
      'Authorization': f'Zoho-oauthtoken {self.access_token}',
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    self.org = org_data['org_id']
    self.org_data = org_data


  def get_creds(self):
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'credentials.yml')
    with open(config_path) as config_file:
      creds = _yaml.load(config_file, Loader=_yaml.FullLoader)

      zoho_client_id = creds['zoho']['client_id']
      zoho_client_secret = creds['zoho']['client_secret']
      zoho_refresh_token = creds['zoho']['refresh_token']

      return zoho_client_id, zoho_client_secret, zoho_refresh_token

  def get_access_token(self):
    url = f'{self._base_url_access}{self.refresh_token}&client_id={self.client_id}&client_secret={self.client_secret}&redirect_uri=http://www.zoho.com/books&grant_type=refresh_token'
    response = requests.request("POST", url, data = {})

    return response.json()['access_token']


  def set_org(self):
    response = requests.request("GET", f'{self._base_url}organizations?=', headers=self.header)
    org_list = [x.get('organization_id') for x in response.json()['organizations']]

    if str(self.org) not in org_list:
      self.create_org()

  def create_org(self):
    cons_url = f'{self._base_url}organizations?organization_id={self.org}'
    org_name = self.org_data['org_name']

    payload = {
      'JSONString': f'{"name": "{org_name}", "currency_code": "EUR", "time_zone": "PST"}'}

    print(payload)
    # response = requests.request("POST", cons_url, headers=self.header)

    # print(response.json())


  def create_item(self):
    url = f'https://inventory.zoho.com/api/v1/items?organization_id={self.org}'
    print(url)
    headers = {
      'Authorization': f'Zoho-oauthtoken {self.access_token}',
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }

    payload = {'JSONString': '{"name": "test_1"}'}

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())

  def update_zoho_item(self):
    url = f'https://inventory.zoho.com/api/v1/items?organization_id={self.org}'
    headers = {
      'Authorization': f'Zoho-oauthtoken {self.access_token}'
    }

    payload = {'JSONString': '{"name": ""}'}

    response = requests.request("POST", url, headers=headers, data = payload)
    print(response.json())


def main(org_data, source_data):
    api = ApiRequest(org_data)
    api.set_org()
    # api.update_zoho()


if __name__ == "__main__":
    main(
      org_data = '53793142878',
      source_data = {}
    )
    
# class DagFactory:
#   def __init__(self, dag_id, org_data, source_data, schedule):
#         self.dag_id = dag_id
#         self.org_data = org_data
#         self.source_data = source_data
#         self.schedule = schedule
#         self.default_args = {
#             'owner': 'Drew',
#             'start_date': days_ago(2)
#         }

#   @contextmanager
#   def _dag(self):
#       with DAG(self.dag_id, default_args=self.default_args, schedule_interval=self.schedule) as dag:
#           yield dag

#   def org_dag(self):
#     with self._dag() as dag:
#       task = PythonOperator(
#         task_id=self.dag_id,
#         python_callable=main,
#         op_kwargs={
#           'org_data': self.org_data,
#           'source_data': self.source_data
#         },
#         dag=dag
#       )
#     return dag



# organizations, source_of_truth = google_sheet_extraction.get_sheet_data()
# for orgs in organizations:
#   dag_factory = DagFactory(
#     dag_id = orgs['org_id'],
#     org_data = orgs,
#     source_data = source_of_truth,
#     schedule = '@daily'
#   )
#   dag_factory.org_dag()