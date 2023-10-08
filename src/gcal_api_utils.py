from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_gcal_events(creds=get_credentials()):
    """Gets the upcoming 10 events from the user's Google Calendar.

    Args:
        creds: Credentials, the user's valid credentials.

    Returns:
        List of dicts, the upcoming 10 events on the user's calendar.
    """
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=100, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return []

        return events

    except HttpError as error:
        print('An error occurred: %s' % error)
        return []


def create_gcal_event(event_body, creds=get_credentials()):
    """Creates an event on the user's Google Calendar.

    Args:
        event: Dict, the event to be created.
        creds: Credentials, the user's valid credentials.

    Returns:
        Dict, the created event.
    """
    try:
        service = build('calendar', 'v3', credentials=creds)
        print(f'Creating event...:{event_body}')
        # Call the Calendar API
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        return event

    except HttpError as error:
        print('An error occurred: %s' % error)
        return None


def get_nyt_now():
    """Gets the current time in New York.

    Returns:
        Dict, the current time in New York in the format {'dateTime': 'YYYY-MM-DDTHH:MM:SS-05:00', 'timeZone': 'America/New_York'}.
    """
    nyt_now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=-5)))
    nyt_now_str = nyt_now.strftime('%Y-%m-%dT%H:%M:%S-05:00')
    return {'dateTime': nyt_now_str, 'timeZone': 'America/New_York'}

def add_time_to_now(delta):
    """Adds a time delta to the current time in New York.

    Args:
        delta: datetime.timedelta, the time delta to add to the current time.

    Returns:
        Dict, the current time plus the delta in the format {'dateTime': 'YYYY-MM-DDTHH:MM:SS-05:00', 'timeZone': 'America/New_York'}.
    """
    nyt_now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=-5)))
    nyt_now_plus_delta = nyt_now + delta
    nyt_now_plus_delta_str = nyt_now_plus_delta.strftime('%Y-%m-%dT%H:%M:%S-05:00')
    return {'dateTime': nyt_now_plus_delta_str, 'timeZone': 'America/New_York'}


def get_calendar_list(creds=get_credentials(), calendar_id='primary'):
    """Calls the Google Calendar API to retrieve the specified calendar list.

    Args:
        creds: Credentials, the user's valid credentials.
        calendar_id: str, the ID of the calendar to retrieve. Defaults to 'primary'.

    Returns:
        Dict, the calendar list.
    """
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        calendar_list = service.calendarList().get(calendarId=calendar_id).execute()
        return calendar_list

    except HttpError as error:
        print('An error occurred: %s' % error)
        return None
