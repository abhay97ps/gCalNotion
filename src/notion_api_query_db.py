from pprint import pprint
import os
from notion_client import Client

from dotenv import load_dotenv
load_dotenv()

notion = Client(auth=os.environ["NOTION_TOKEN"])


list_users_response = notion.users.list()
pprint(list_users_response)
