"""
    Module to create Spreadsheet and Write data to it
"""


def impl_write_data(sheets_service, spreadsheet_id, sheet_name, data):
    """Write data to a Google Sheet."""

    # Check if a sheet with the same name already exists and append copy number if necessary
    sheets_metadata = sheets_service.spreadsheets().get(
        spreadsheetId=spreadsheet_id).execute()
    sheets = sheets_metadata.get('sheets', '')
    sheet_names = [sheet.get("properties", {}).get("title", "")
                   for sheet in sheets]

    version_number = 2
    new_sheet_name = sheet_name

    while new_sheet_name in sheet_names:
        new_sheet_name = f'{sheet_name} {version_number}'
        version_number += 1

    body = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': new_sheet_name
                }
            }
        }]
    }
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body).execute()
    body = {
        'values': data
    }
    range_ = f'{new_sheet_name}!A1'
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_, valueInputOption='RAW', body=body).execute()


def impl_create_sheet(sheets_service, title):
    """Create a new Google Sheet and return its ID."""
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    spreadsheet = sheets_service.spreadsheets().create(
        body=spreadsheet, fields='spreadsheetId').execute()
    return spreadsheet.get('spreadsheetId')


def impl_delete_default_sheet(sheets_service, spreadsheet_id):
    """ Delete the default empty sheet """

    try:
        body = {
            'requests': [{
                'deleteSheet': {
                    'sheetId': 0
                }
            }]
        }
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body).execute()

        return True

    except Exception:
        return False
