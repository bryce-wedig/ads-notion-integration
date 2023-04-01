import requests  # to make API calls
import json  # create JSON objects
import datetime


def get_notion_header(notion_api_token, notion_api_version):
    return {
            "Authorization": "Bearer " + notion_api_token,
            "Content-Type": "application/json",
            "Notion-Version": notion_api_version
        }


def get_todoist_header(todoist_api_token):
    return {"Authorization": "Bearer " + todoist_api_token}


def is_active_in_notion(notion_header, integration_page_id):
    query_active = requests.get(
        "https://api.notion.com/v1/pages/" + integration_page_id + "/properties/" + "ia%3Dl",
        headers=notion_header
    )

    return json.loads(query_active.text)["checkbox"]


def post_status_to_notion(notion_header, integration_page_id, is_success):
    if is_success:
        message = "Ran successfully at " + str(datetime.datetime.today())
    else:
        message = "Failed to run at " + str(datetime.datetime.today())

    requests.patch(
        'https://api.notion.com/v1/pages/' + integration_page_id,
        headers=notion_header,
        data=json.dumps({
            "properties": {
                "Status": {
                    "id": "_F=k",
                    "type": "rich_text",
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": message
                            },
                            "plain_text": message
                        }
                    ]
                }
            }
        })
    )
