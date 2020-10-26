import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']


def get_creds():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(os.path.dirname(__file__), '..', 'config', 'google_sheet_auth.json')
        , SCOPE)
    return gspread.authorize(creds)


def write_output(data):
    client = get_creds()

    sheet = client.open("Infarm_Zoho_Results").worksheet("API_Create")

    rows = data

    sheet.insert_rows(rows, 2)


def get_sheet_data():
    client = get_creds()

    org_sheet = client.open("Infarm Sample").worksheet("Zoho Warehouses")
    source_of_truth = client.open("Infarm Sample").worksheet("Items Source of Truth")

    org_sheet_data = org_sheet.get_all_records()
    source_of_truth = source_of_truth.get_all_records()

    return org_sheet_data, source_of_truth


if __name__ == "__main__":
    pass
    # write_output()