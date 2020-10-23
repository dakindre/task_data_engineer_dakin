import os
import time
import requests
import json
import yaml as _yaml
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator

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


  def create_item(self):
    url = f'https://inventory.zoho.com/api/v1/items?organization_id={self.zoho_org}'
    print(url)
    headers = {
      'Authorization': f'Zoho-oauthtoken {self.zoho_access_token}',
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }

    payload = {'JSONString': '{"name": "test_ohhhh_yeah"}'}

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


def main():
    api = ApiRequest()
    api.create_item()

task = PythonOperator(
    task_id='zoho_item_insert',
    python_callable=main,
    dag=dag,
)

