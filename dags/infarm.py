import os
import json
import requests
import yaml as _yaml
from airflow import DAG
# import dagfactory

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults

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

  def update_zoho_item(self):
    url = f'https://inventory.zoho.com/api/v1/items?organization_id={self.zoho_org}'
    print(url)
    response = requests.request("POST", url, data = {})
    print(response.json())


    # r = requests.put('https://httpbin.org/put', data = {'key':'value'})

if __name__ == "__main__":
    api = ApiRequest()
    api.update_zoho_item()



# dag_factory = dagfactory.DagFactory(os.path.join(os.path.dirname(os.path.realpath(__file__)), "dag_factory.yml"))

# dag_factory.clean_dags(globals())
# dag_factory.generate_dags(globals())