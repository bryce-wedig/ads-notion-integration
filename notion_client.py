import json
import sys

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


def query_bibcodes(notion_header, research_papers_page_id):
    result = requests.post(
        "https://api.notion.com/v1/databases/" + research_papers_page_id + "/query",
        headers=notion_header
    )

    bibcodes = []

    if result.status_code == 200:
        json_response = json.loads(result.text)
        pages = json_response["results"]

        for page in pages:
            bibcode_list = page["properties"]["Bibcode"]["rich_text"]

            if len(bibcode_list) != 0:
                bibcodes.append(bibcode_list[0]["plain_text"])
            else:
                page_title = page["properties"]["Name"]["title"][0]["plain_text"]
                raise Exception('Page ' + page_title + ' is missing a Bibcode')
    else:
        sys.exit('ERROR: Notion query failed')

    return bibcodes
