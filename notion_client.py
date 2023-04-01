import json
import requests


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
