# create a service to sync a notion task database to google calendar
from dotenv import load_dotenv
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from notion_client import Client
from datetime import datetime, timedelta

load_dotenv()

# Authenticate with the Notion API
notion = Client(auth=os.environ["NOTION_API_KEY"])

# Authenticate with the Google Calendar API
scopes = ['https://www.googleapis.com/auth/calendar']
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=scopes)
service = build("calendar", "v3", credentials=credentials)


# print top 10 notional database entries
def print_top_10_notion_tasks():
    results = notion.databases.query(
        **{
            "database_id": os.environ["NOTION_DATABASE_ID"],
            "filter": {
                "property": "Status",
                "select": {
                    "equals": "To Do"
                }
            }
        }
    )
    for result in results["results"][:10]:
        print(result["properties"]["Name"]["title"][0]["text"]["content"])

# print top 10 google calendar events
def print_top_10_google_calendar_events():
    results = service.events().list(
        calendarId='primary',
        timeMin=(datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z',
        timeMax=(datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    for result in results["items"][:10]:
        print(result["summary"])

print_top_10_notion_tasks()
print_top_10_google_calendar_events()
