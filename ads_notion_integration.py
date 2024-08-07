'''
Parts are adapted from https://github.com/adsabs/ads-examples/blob/master/library_csv/lib_2_csv.py
'''

import sys
import traceback

import ads_client
import notion_client
import utils
from notion_helper import *

# set to true for IDE execution
local_execution = False

if local_execution:
    textfile = 'last_successful_runtime.txt'
    json = utils.read_json('constants_ads_notion_integration.json')
else:
    textfile = '/home/ubuntu/ads-notion-integration/last_successful_runtime.txt'
    json = utils.read_json('/home/ubuntu/ads-notion-integration/constants_ads_notion_integration.json')

ads_token = json['ads_token']
ads_library_name = json['ads_library_name']
research_papers_page_id = json['research_papers_page_id']
notion_api_token = json['notion_api_token']
notion_api_version = json['notion_api_version']
integration_page_id = json['integration_page_id']

notion_header = get_notion_header(notion_api_token, notion_api_version)

try:
    # check if integration is active in Notion
    if not is_active_in_notion(notion_header, integration_page_id):
        sys.exit('Integration is not active. Exiting...')

    # read last successful runtime
    last_successful_runtime = utils.read_last_successful_runtime(textfile)

    # collect libraries
    libraries = ads_client.get_libraries(ads_token)

    # check if the ADS library exists
    ads_library = None
    for library in libraries:
        if library['name'] == ads_library_name:
            ads_library = library
            break
    if ads_library is None:
        post_status_to_notion(notion_header, integration_page_id, True)
        utils.write_last_successful_runtime(textfile)
        sys.exit('ERROR: ADS library \'' + ads_library_name + '\' not found')

    # check if ADS library has been modified since code last ran - if not, then exit
    library_last_modified = datetime.datetime.fromisoformat(ads_library['date_last_modified'])
    if last_successful_runtime > library_last_modified:
        post_status_to_notion(notion_header, integration_page_id, True)
        utils.write_last_successful_runtime(textfile)
        sys.exit('No changes since last successful runtime')

    # go get bibcodes for all documents in Unfiled
    bibcodes = ads_client.get_library(ads_token, ads_library['id'], ads_library['num_documents'])

    # get all bibcodes already in Notion
    existing_bibcodes = notion_client.query_bibcodes(notion_header, research_papers_page_id)

    # get deltas
    bibcodes_to_add = []
    for bibcode in bibcodes:
        if existing_bibcodes.count(bibcode) == 0:
            bibcodes_to_add.append(bibcode)

    if len(bibcodes_to_add) == 0:
        post_status_to_notion(notion_header, integration_page_id, True)
        utils.write_last_successful_runtime(textfile)
        print('No deltas')
        sys.exit()

    print("Identified " + str(len(bibcodes_to_add)) + " document(s) to add")

    failure_count = 0

    # add those deltas to Notion
    for bibcode in bibcodes_to_add:
        print("Creating page " + str(bibcodes_to_add.index(bibcode) + 1) + ' of ' + str(len(bibcodes_to_add)))

        # query ADS for document
        document = ads_client.get_document(ads_token, bibcode)

        # construct url
        document['url'] = 'https://ui.adsabs.harvard.edu/abs/' + bibcode + '/abstract'

        # truncate abstract to 2000 characters
        if 'abstract' in document:
            document['abstract'] = document['abstract'][:2000]
        else:
            document['abstract'] = ''

        # create page in Notion
        notion_page = notion_client.create_page(notion_header, research_papers_page_id, document)
        if notion_page.status_code != 200:
            failure_count += 1
            print("\t" + "Failure: " + document["bibcode"])
            print(notion_page.text)
        else:
            print("\t" + "Success: " + document["bibcode"])

    # log result in Notion
    if failure_count == 0:
        post_status_to_notion(notion_header, integration_page_id, True)
    else:
        post_status_to_notion(notion_header, integration_page_id, False)

    utils.write_last_successful_runtime(textfile)
except Exception:
    traceback.print_exc()
    post_status_to_notion(notion_header, integration_page_id, False)
