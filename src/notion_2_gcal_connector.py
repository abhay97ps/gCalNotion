# notion to google calendar operations
# requirements
# should support atleast 1 year of data

# 1. notion2gcal: get all pages from database and create
# tasks was no certain time only day and
# for specific date and time make events in google calendar

# 2. gcal2notion: get all events from google calendar and create
# pages if it does not exist
# also update pages if it exists

from gcal_api_utils import create_gcal_event
import datetime
import pytz
import fire
from dotenv import load_dotenv

from notion_api_utils import get_tasks_database

load_dotenv()

IGNORED_STATUS = frozenset(['Completed', 'Backlog'])


def today_all_day_event(name, timezone='America/New_York', start=None):
    '''Construct an all-day Google Calendar event dictionary for today or a specified date.

    Args:
        name (str): The name of the event.
        timezone (str): The timezone for the event. Defaults to 'America/New_York'.
        start (str): The start date of the event in the format 'yyyy-mm-dd'. Defaults to None.

    Returns:
        dict: A dictionary containing the event details.
    '''
    try:
        if start is not None:
            # Parse start date to datetime
            start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
            # Set event start time to start_date at t timestep in the specified timezone
            event_start = pytz.timezone(timezone).localize(
                datetime.datetime.combine(start_date, datetime.time(16, 0)))
        else:
            # Set event start time to today at 9AM in the specified timezone
            event_start = datetime.datetime.now(pytz.timezone(timezone)).replace(
                hour=16, minute=0, second=0, microsecond=0)

        # Construct event dictionary
        event = {
            'summary': name,
            'start': {
                'dateTime': event_start.isoformat(),
                'date': event_start.date().isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': (event_start + datetime.timedelta(hours=1)).isoformat(),
                'date': event_start.date().isoformat(),
                'timeZone': timezone,
            },
            'originalStartTime': {
                'date': event_start.date().isoformat(),  # date, in the format "yyyy-mm-dd",
                # datetime, in the format "yyyy-mm-ddThh:mm:ssZ
                'dateTime': event_start.isoformat(),
                'timeZone': timezone,
            },
        }
        return event
    except Exception as e:
        print(f"Error from today all-day : {e}")
        return None


def construct_timed_event(name, start, end, timezone='America/New_York'):
    '''Construct a timed Google Calendar event dictionary.

    Args:
        name (str): The name of the event.
        start (str): The start date of the event in the format 'yyyy-mm-dd'.
        end (str): The end date of the event in the format 'yyyy-mm-dd'.

    Returns:
        dict: A dictionary containing the event details.
    '''
    try:
        event_start = datetime.datetime.fromisoformat(start)
        # if start date is expired set to today
        if datetime.datetime.now().date() > event_start.date():
            event_start = datetime.datetime.now()
        event_end = datetime.datetime.fromisoformat(end)
        # Construct event dictionary
        return {
            'summary': name,
            'start': {
                'dateTime': event_start.isoformat(),
                'date': event_start.date().isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': event_end.isoformat(),
                'date': event_end.date().isoformat(),
                'timeZone': timezone,
            },
            'originalStartTime': {
                'date': event_start.date().isoformat(),  # date, in the format "yyyy-mm-dd",
                # datetime, in the format "yyyy-mm-ddThh:mm:ssZ
                'dateTime': event_start.isoformat(),
                'timeZone': timezone,
            },
        }
    except Exception as e:
        print(f"Error: {e}")
        return None


def construct_gcal_event(name, start, end=None):
    '''Construct a Google Calendar event dictionary.

    Args:
        name (str): The name of the event.
        end (str): The end date of the event in the format 'yyyy-mm-dd'.
        start (str): The start date of the event in the format 'yyyy-mm-dd'. Defaults to None.

    Returns:
        dict: A dictionary containing the event details.
    '''
    try:
        if start and end:
            # if end date is expired, contruct all day event for today
            if datetime.datetime.now().date() > datetime.datetime.fromisoformat(end).date():
                return today_all_day_event(name=name)
            else:
                return construct_timed_event(name=name, start=start, end=end)
        else:
            return today_all_day_event(name=name, start=start)
    except Exception as e:
        print(f"Error: {e}")
        return None


def notion_page_2_gcal_event(page):
    '''Parse page info into Google Calendar event format.

    Args:
        page (dict): A dictionary containing information about a Notion page.

    Returns:
        dict: A dictionary representing a Google Calendar event.
    '''

    try:
        # Extract relevant properties from page dictionary
        name = page['properties']['Name']['title'][0]['text']['content']
        status = page['properties']['Status']['select']['name']
        date = page['properties']['Due Date']['date']

        # Ignore page if status is 'completed'
        if status in IGNORED_STATUS:
            print(f"Ignoring page '{name}' with status '{status}'")
            return None

        # Check if date exists else set start end to today (all day event)
        if len(date) != 0:
            print(f"Creating event for page '{name}' with date '{date}'")
            start = date['start']
            end = date.get('end', None)
            return construct_gcal_event(name=name, start=start, end=end)
        else:
            print(f"Creating event for page '{name}' with no date")
            return today_all_day_event(name=name)
    except KeyError as e:
        print(f"KeyError: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def notion2gcal():
    try:
        database = get_tasks_database()
        # create entries for google calendar
        gCalEntries = list(map(notion_page_2_gcal_event, database["results"]))
        # remove None values
        gCalEntries = list(filter(None, gCalEntries))
        # create events using calender api
        events = list(map(create_gcal_event, gCalEntries))
        # access events variable
        print(events)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    fire.Fire(notion2gcal)
