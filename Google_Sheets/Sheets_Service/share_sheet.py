from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def impl_share_spreadsheet(spreadsheet_id, email, creds):
    ''' share the spreadsheet to client after export'''

    try:
        # Build the Drive API client
        service = build('drive', 'v3', credentials=creds)

        # Set the permission body
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }

        # Share the spreadsheet with the given email address
        service.permissions().create(
            fileId=spreadsheet_id,
            body=permission,
            transferOwnership=False
        ).execute()

        return f'Spreadsheet created & shared with {email}, link: https://docs.google.com/spreadsheets/d/{spreadsheet_id}'

    except HttpError as error:
        print(f'An error occurred: {error}', flush=True)
        return "Error occurred: check logs for details"
