from notion_2_gcal_connector import notion_page_2_gcal_event, construct_all_day_event, today_all_day_event


def test_notion_page_2_gcal_event_completed():
    page = {
        'properties': {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': 'Test Page'
                        }
                    }
                ]
            },
            'Status': {
                'select': {
                    'name': 'Backlog'
                }
            },
            'Due Date': {
                'date': {
                    'start': '2022-01-01'
                }
            }
        }
    }
    assert notion_page_2_gcal_event(page) is None


def test_notion_page_2_gcal_event_no_date():
    page = {
        'properties': {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': 'Test Page'
                        }
                    }
                ]
            },
            'Status': {
                'select': {
                    'name': 'In Progress'
                }
            },
            'Due Date': {
                'date': {}
            }
        }
    }
    expected_event = today_all_day_event('Test Page')
    assert notion_page_2_gcal_event(page) == expected_event


def test_notion_page_2_gcal_event_expired_date():
    page = {
        'properties': {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': 'Test Page'
                        }
                    }
                ]
            },
            'Status': {
                'select': {
                    'name': 'In Progress'
                }
            },
            'Due Date': {
                'date': {
                    'start': '2022-01-01',
                    'end': '2022-01-02'
                }
            }
        }
    }
    expected_event = today_all_day_event('Test Page')
    assert notion_page_2_gcal_event(page) == expected_event


def test_notion_page_2_gcal_event_all_day():
    page = {
        'properties': {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': 'Test Page'
                        }
                    }
                ]
            },
            'Status': {
                'select': {
                    'name': 'In Progress'
                }
            },
            'Due Date': {
                # today is 2023 oct 08
                'date': {
                    'start': '2023-10-09'
                }
            }
        }
    }
    expected_event = construct_all_day_event('Test Page', '2023-10-09')
    print('@@@@@@@@@@@@@@@')
    assert notion_page_2_gcal_event(page) == expected_event


def test_notion_page_2_gcal_event_timed():
    page = {
        'properties': {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': 'Test Page'
                        }
                    }
                ]
            },
            'Status': {
                'select': {
                    'name': 'In Progress'
                }
            },
            'Due Date': {
                # today is 2023 oct 08
                'date': {
                    'start': '2023-10-08T14:00:00+08:00',
                    'end': '2023-10-08T15:00:00+08:00'
                }
            }
        }
    }
    expected_event = {
        'summary': 'Test Page',
        'start': {
            'dateTime': '2023-10-08T14:00:00+08:00',
            'timeZone': 'America/New_York',
            'date': '2023-10-08'
        },
        'end': {
            'dateTime': '2023-10-08T15:00:00+08:00',
            'timeZone': 'America/New_York',
            'date': '2023-10-08'
        },
        'originalStartTime': {'date': '2023-10-08'},
    }
    assert notion_page_2_gcal_event(page) == expected_event
