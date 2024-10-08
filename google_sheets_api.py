
from pprint import pprint
from dotenv import load_dotenv
import httplib2, os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()
CREDENTIAL_FILE = os.getenv("CREDENTIAL_FILE")
spreadsheet_id = os.getenv("SPREADSHEET_ID")

# Create service account credentials
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIAL_FILE,
    [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)
http_auth = credentials.authorize(httplib2.Http())
service = build("sheets", "v4", http=http_auth)

# Fetch values from the spreadsheet
values = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,  # Correct argument name
    range="A1:E10",  # Adjust the range as necessary
    majorDimension="ROWS"
).execute()

pprint(values)


values = service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        "valueInputOption": "USER_ENTERED",
        "data":
            {
                "range": "A15:B15",
                "majorDimension": "ROWS",
                "values": [["John", "Doe"]],
            }}
).execute()
