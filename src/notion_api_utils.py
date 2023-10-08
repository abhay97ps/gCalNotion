from pprint import pprint
import os
from notion_client import Client

from dotenv import load_dotenv
load_dotenv()


def get_notion_client():
    """Gets the Notion client."""
    return Client(auth=os.environ["NOTION_TOKEN"])


def get_tasks_database():
    """Gets the tasks database from Notion."""
    notion = get_notion_client()
    # get notion database pages
    database = notion.databases.query(
        database_id=os.environ["NOTION_TASK_DB_ID"])
    return database
