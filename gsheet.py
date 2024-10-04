import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class GSheet:
    def __init__(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token = None
        if "SHEET_TOKEN" in os.environ:
            token = os.environ["SHEET_TOKEN"]
        elif os.path.exists("token.json"):
            with open("token.json", "r") as f:
                token =  json.load(f)
#            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if token:
            creds = Credentials.from_authorized_user_info(token, SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if "GITHUB_ACTIONS" not in os.environ and (not creds or not creds.valid):
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        if not creds:
            print("Failed to google sheet credential")
            return

        self.sheet = build("sheets", "v4", credentials=creds).spreadsheets()

    def get(self, sheetId, range):
        result = (
            self.sheet.values()
                .get(spreadsheetId=sheetId, range=range)
                .execute()
        )

        return result.get("values", [])

    def update(self, sheetId, range, data):
        self.sheet.values().update(spreadsheetId=sheetId, range=range,
            valueInputOption="USER_ENTERED", body={"values": data}).execute()


