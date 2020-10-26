import os
import time
import requests
import json
import random
import yaml as _yaml
from airflow import DAG
from contextlib import contextmanager
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from google.google_sheets import(
  get_sheet_data,
  write_output
)


class ApiRequest:
  _base_url_access = 'https://accounts.zoho.com/oauth/v2/token?refresh_token='
  _base_url = "https://inventory.zoho.com/api/v1/"

  def __init__(self, org_name, item_data):
    self.client_id, self.client_secret, self.refresh_token = self.get_creds()
    self.access_token = self.get_access_token()
    self.header = {
      'Authorization': f'Zoho-oauthtoken {self.access_token}',
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    self.org = self.set_org(org_name)
    self.item_data = item_data


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


  def set_org(self, org_name):
    response = requests.request("GET", f'{self._base_url}organizations?=', headers=self.header)
    org_list = [{'org_id': x.get('organization_id'), 'org_name': x.get('name')} for x in response.json()['organizations']]

    if org_name not in [x.get('org_name') for x in org_list]:
      return self.create_org(org_name)
    else:
      return [str(x.get('org_id')) for x in org_list if x.get('org_name') == org_name][0]

  def create_org(self, org_name):
    cons_url = f'{self._base_url}organizations?='

    org_struct = {
      "name": f"{org_name}",
      "currency_code": "EUR",
      "time_zone": "CET",
      "language_code": "en",
      "industry_type": "Services",
      "portal_name": f"org{random.randrange(1000000, 9000000)}",
      "address": 
        {
            "country": "Germany"
        }
    }

    payload = {'JSONString': json.dumps(org_struct)}

    response = requests.request("POST", cons_url, headers=self.header, data=payload)
    response_json = response.json()

    create_org = [cons_url, json.dumps(org_struct), json.dumps(response_json)]

    write_output(data=[create_org])

    return response_json.get('organization').get('organization_id')

  def sync_items(self):
    # get current list of items
    items_list = self.get_items_list()
    write_array = []

    for item in self.item_data:
      # item exists but doesn't match entirely so an update is needed
      item_id = [x.get('item_id') for x in items_list if x.get('item_name')== item.get('item_name')][0]
      if item_id:
        write_array.append(self.update_item(item, item_id))
      else:
        # item doesn't exist so item creation is needed
        write_array.append(self.create_item(item))
    
    write_output(data=write_array)

  def get_items_list(self):
    cons_url = f'{self._base_url}items?organization_id={self.org}'
    response = requests.request("GET", cons_url, headers=self.header)

    items_list = [{'item_name': x.get('name'), 'item_id': x.get('item_id')} for x in response.json()['items']]
    return items_list
    

  def update_item(self, item, item_id):
    cons_url = f'{self._base_url}items/{item_id}?organization_id={self.org}'

    item_struct = {
      "name": f"{item.get('item_name')}",
      "group_name": f"{item.get('category')}",
      "vendor_name": f"{item.get('Supplier_Name')}"
    }

    payload = {'JSONString': json.dumps(item_struct)}

    response = requests.request("PUT", cons_url, headers=self.header, data=payload)
    response_json = response.json()
    
    update_item = [cons_url, 'update_item', json.dumps(item_struct), json.dumps(response_json)]

    return update_item


  def create_item(self, item):
    cons_url = f'{self._base_url}items?organization_id={self.org}'

    item_struct = {
      "name": f"{item.get('item_name')}",
      "group_name": f"{item.get('category')}",
      "vendor_name": f"{item.get('Supplier_Name')}"
    }

    payload = {'JSONString': json.dumps(item_struct)}

    response = requests.request("POST", cons_url, headers=self.header, data=payload)
    response_json = response.json()
    
    create_item = [cons_url, 'create_item', json.dumps(item_struct), json.dumps(response_json)]
    
    return create_item



def main(org_name, item_data):
    api = ApiRequest(org_name, item_data)
    api.sync_items()



if __name__ == "__main__":
  organizations, source_of_truth = get_sheet_data()
  print(organizations, source_of_truth)
    # main(
    #   org_name = 'Infarm_Hamburg',
    #   item_data = [{
    #     'item_name': 'DE_PRICETAG_PFEFFERMINZE_NEW_1_35',
    #     'category': 'Marketing',
    #     'Supplier_Name': 'PRINTSTAR GmbH'
    #   }]
    # )
    
class DagFactory:
  def __init__(self, dag_id, org_data, source_data, schedule):
        self.dag_id = dag_id
        self.org_data = org_data
        self.source_data = source_data
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
        task_id=self.dag_id,
        python_callable=main,
        op_kwargs={
          'org_data': self.org_data,
          'source_data': self.source_data
        },
        dag=dag
      )
    return dag


# organizations, source_of_truth = get_sheet_data()
# for orgs in organizations:
#   dag_factory = DagFactory(
#     dag_id = orgs['org_id'],
#     org_data = orgs,
#     source_data = source_of_truth,
#     schedule = '@daily'
#   )
#   dag_factory.org_dag()