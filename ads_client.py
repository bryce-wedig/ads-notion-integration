import math
from urllib.parse import urlencode

import requests


def get_config(token):
    return {
        'url': 'https://api.adsabs.harvard.edu/v1/biblib',
        'headers': {
            'Authorization': 'Bearer:{}'.format(token),
            'Content-Type': 'application/json',
        }
    }


def get_libraries(token):
    config = get_config(token)

    r = requests.get(
        '{}/libraries'.format(config['url']),
        headers=config['headers']
    )

    try:
        data = r.json()['libraries']
        return data
    except ValueError:
        raise ValueError(r.text)


def get_library(token, library_id, num_documents):
    config = get_config(token)

    start = 0
    rows = 25
    num_paginates = int(math.ceil(num_documents / (1.0*rows)))

    documents = []
    for i in range(num_paginates):
        # print('Pagination {} out of {}'.format(i+1, num_paginates))

        r = requests.get(
            '{}/libraries/{id}?start={start}&rows={rows}'.format(
                config['url'],
                id=library_id,
                start=start,
                rows=rows
            ),
            headers=config['headers']
        )

        # get all the documents that are inside the library
        try:
            data = r.json()['documents']
        except ValueError:
            raise ValueError(r.text)

        documents.extend(data)

        start += rows

    return documents


def get_document(token, bibcode):
    encoded_query = urlencode({"q": "bibcode:" + bibcode,
                               "fl": "title,abstract,date,bibcode"})
    results = requests.get("https://api.adsabs.harvard.edu/v1/search/query?{}".format(encoded_query),
                           headers={'Authorization': 'Bearer ' + token})

    response = results.json()

    return response['response']['docs'][0]
