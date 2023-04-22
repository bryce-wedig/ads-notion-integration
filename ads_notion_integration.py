import ads_client
import notion_client
import utils
from bw_integration_utils import *
import sys


# read json file and put values into variables
json = utils.read_json('constants_ads_notion_integration.json')
ads_token = json['ads_token']
research_papers_page_id = json['research_papers_page_id']
notion_api_token = json['notion_api_token']
notion_api_version = json['notion_api_version']
integration_page_id = json['integration_page_id']

# check if integration is active in Notion
notion_header = get_notion_header(notion_api_token, notion_api_version)
if not is_active_in_notion(notion_header, integration_page_id):
    sys.exit('Integration is not active. Exiting...')

# read last successful runtime
last_successful_runtime = utils.read_last_successful_runtime()

# collect libraries
libraries = ads_client.get_libraries(ads_token)

# check if Unfiled library exists
unfiled_library = None
for library in libraries:
    if library['name'] == 'Unfiled':
        unfiled_library = library
        break
if unfiled_library is None:
    sys.exit('ERROR: Unfiled library not found')

# check if Unfiled library has been modified since code last ran - if not, then exit
library_last_modified = datetime.datetime.fromisoformat(unfiled_library['date_last_modified'])
if not library_last_modified > last_successful_runtime:
    sys.exit('No changes since last successful runtime')

# go get bibcodes for all documents in Unfiled
bibcodes = ads_client.get_library(ads_token, unfiled_library['id'], unfiled_library['num_documents'])

# get all bibcodes already in Notion
# notion_client.query_bibcodes(notion_header, research_papers_page_id)

# get deltas
# todo get deltas

# add those deltas to Notion
for bibcode in bibcodes:
    # query ADS for document
    document = ads_client.get_document(ads_token, bibcode)

    # construct url
    document['url'] = 'https://ui.adsabs.harvard.edu/abs/' + bibcodes[0] + '/abstract'

    # create page in Notion
    notion_page = notion_client.create_page(notion_header, research_papers_page_id, document)

# log result in Notion
if notion_page.status_code == 200:
    post_status_to_notion(notion_header, integration_page_id, True)
else:
    post_status_to_notion(notion_header, integration_page_id, False)

utils.write_last_successful_runtime()
