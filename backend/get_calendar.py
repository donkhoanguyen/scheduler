from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import base64
import os.path
import pickle
import json

def build_calendar_service():
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    creds = None

    # Load existing token if present
    if os.path.exists('credentials/token.pickle'):
        with open('credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Refresh token if expired or create new if none exists
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/gg_credentials.json', SCOPES)
            creds = flow.run_local_server(port=8081)
            
        # Save credentials for next run
        with open('credentials/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f'Failed to build service: {str(e)}')
        return None


service = build_calendar_service()

now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
print("Getting the upcoming 10 events")

# Example: List the next 10 events from the primary calendar
events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
events = events_result.get("items", [])

if not events:
    print('No upcoming events found.')
for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(start, event['summary'])
