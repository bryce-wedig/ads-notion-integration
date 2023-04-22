import json
import requests
import sys


def create_page(notion_header, research_papers_page_id, document):
    result = requests.post(
        "https://api.notion.com/v1/pages",
        headers=notion_header,
        data=json.dumps({
            "parent": {
                "database_id": research_papers_page_id
            },
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": document['title'][0]
                            }
                        }
                    ]
                },
                "Abstract": {
                    "rich_text": [
                        {
                            "text": {
                                "content": document['abstract']
                            }
                        }
                    ]
                },
                "URL": {
                    "url": document['url']
                },
                "Bibcode": {
                    "rich_text": [
                        {
                            "text": {
                                "content": document['bibcode']
                            }
                        }
                    ]
                }
            }
        })
    )

    return result


def query_bibcodes(notion_header, research_papers_page_id):
    result = requests.post(
        "https://api.notion.com/v1/databases/" + research_papers_page_id + "/query",
        headers=notion_header
    )

    bibcodes = []

    if result.status_code == 200:
        text_response = result.text.replace('[', '').replace(']', '')
        json_response = json.loads(text_response)
        print(json_response)
    else:
        sys.exit('ERROR: Notion query failed')

    return bibcodes
