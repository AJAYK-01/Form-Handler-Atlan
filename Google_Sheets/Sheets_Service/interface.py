"""
    interface for the google sheets service
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


from .share_sheet import impl_share_spreadsheet
from .write_sheet import impl_create_sheet, impl_delete_default_sheet, impl_write_data

# Google Sheets API creds
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = './Sheets_Service/google-sheets-service-key.json'


class GoogleSheets:
    """ The Google Sheets service class """

    def __init__(self):
        self.credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        self.sheets_service = build(
            'sheets', 'v4', credentials=self.credentials)

    def create_sheet(self, title):
        """ Create a new Google Sheets under service account """
        return impl_create_sheet(sheets_service=self.sheets_service, title=title)

    def write_data(self, spreadsheet_id, sheet_name, data):
        """ Write data to the created Google Sheets as service account """
        return impl_write_data(sheets_service=self.sheets_service,
                               spreadsheet_id=spreadsheet_id, sheet_name=sheet_name, data=data)

    def share_spreadsheet(self, spreadsheet_id, email):
        """ Share spreadsheet from service account to requesting user's mail """
        return impl_share_spreadsheet(creds=self.credentials,
                                      spreadsheet_id=spreadsheet_id, email=email)

    def delete_default_sheet(self, spreadsheet_id):
        """ Delete default empty sheet in every spreadsheet """
        return impl_delete_default_sheet(sheets_service=self.sheets_service,
                                         spreadsheet_id=spreadsheet_id)
