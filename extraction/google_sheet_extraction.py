import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_sheet_data():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(os.path.dirname(__file__), '..', 'config', 'google_sheet_auth.json')
        , scope)
    client = gspread.authorize(creds)
    org_sheet = client.open("Infarm Sample").worksheet("Zoho Warehouses")
    source_of_truth = client.open("Infarm Sample").worksheet("Items Source of Truth")

    org_sheet_data = org_sheet.get_all_records()
    source_of_truth = source_of_truth.get_all_records()
    print(source_of_truth)
    return org_sheet_data, source_of_truth

if __name__ == "__main__":
    get_sheet_data()