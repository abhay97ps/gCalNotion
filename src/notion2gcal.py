# notion to google calendar operations
# requirements
# should support atleast 1 year of data

# 1. notion2gcal: get all pages from database and create
# tasks was no certain time only day and
# for specific date and time make events in google calendar

# 2. gcal2notion: get all events from google calendar and create
# pages if it does not exist
# also update pages if it exists

'''
# notion2gcal
# get all pages from database
# parse pages with only date and no datetime as tasks
# parse pages with datetime as events
# create tasks in google calendar
# create events in google calendar

'''


from gcal_api_utils import create_gcal_event
import datetime
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()


def gcal_entry(page):
    '''Parse page info into Google Calendar event format.

    Args:
        page (dict): A dictionary containing information about a Notion page.

    Returns:
        dict: A dictionary representing a Google Calendar event.
    '''
    try:
        # Extract relevant properties from page dictionary
        name = page['properties']['Name']['title'][0]['text']['content']
        due_date = page['properties']['Due Date']['date']['start']
        status = page['properties']['Status']['select']['name']
        impact = page['properties']['Impact']['select']['name']
        loe = page['properties']['LOE']['select']['name']
        complexity = page['properties']['Complexity']['select']['name']

        # Check if due date has passed
        if datetime.datetime.now().date() > datetime.datetime.fromisoformat(due_date).date():
            # Set event start time to next Saturday at 9AM
            next_saturday = datetime.datetime.now() + datetime.timedelta(days=(5 -
                                                                               datetime.datetime.now().weekday()) % 7 + 1)
            event_start = datetime.datetime.combine(
                next_saturday, datetime.time(hour=9))

            # Construct event dictionary
            event = {
                'summary': name,
                'location': '',
                'description': f'Status: {status}\nImpact: {impact}\nLOE: {loe}\nComplexity: {complexity}',
                'start': {
                    'dateTime': event_start.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (event_start + datetime.timedelta(hours=1)).isoformat(),
                    'timeZone': 'UTC',
                },
                'recurrence': [],
                'attendees': [],
                'reminders': {
                    'useDefault': True,
                },
            }
        else:
            # Construct event dictionary with original due date
            event = {
                'summary': name,
                'location': '',
                'description': f'Status: {status}\nImpact: {impact}\nLOE: {loe}\nComplexity: {complexity}',
                'start': {
                    'dateTime': due_date,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (datetime.datetime.fromisoformat(due_date) + datetime.timedelta(hours=1)).isoformat(),
                    'timeZone': 'UTC',
                },
                'recurrence': [],
                'attendees': [],
                'reminders': {
                    'useDefault': True,
                },
            }

        return event
    except Exception as e:
        print(f"Error: {e}")
        return None


def notion2gcal():
    try:
        # get notion client
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        # get notion database pages
        database = notion.databases.query(
            database_id=os.environ["NOTION_TASK_DB_ID"])
        print(database)
        gCalEntries = list(map(gcal_entry, database["results"]))
        # create entries in google calendar
        # create events using calender api
        events = list(map(create_gcal_event, gCalEntries))
        # access events variable
        print(events)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    notion2gcal()
