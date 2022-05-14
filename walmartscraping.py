import requests
import json
# set up the request parameters
import time

import boto3
from decimal import Decimal

from opensearchpy import OpenSearch,RequestsHttpConnection
master_name="COMSE6998"
master_password="Comse6998!"
host="https://search-rainforest-product-search-c7dshudmnvp2w4aolgkgxgrijm.us-east-1.es.amazonaws.com"
port=9200

search=OpenSearch(
    hosts=host,
    http_auth=(master_name,master_password),
    use_ssl = True,
    verify_certs = True,
    http_compress = True,
    connection_class = RequestsHttpConnection
)



dynamodb=boto3.resource('dynamodb')

productTable = dynamodb.Table('bluecart_product_data')

reviewTable=dynamodb.Table('bluecart_review_data')






def get_bluecart_product_info_from_idlist(api_search_result):
    item_ids=[]
    l=len(api_search_result)
    print(l)
    for i in range(l):
        item=api_search_result[i]
        item_id=item['product']['item_id']
        print(item_id)
        item_ids.append(item_id)
        params = {
            'api_key': 'A03FF5EF9CEE424A9DFD2E0DC2CD1E71',
            'type': 'product',
            'item_id': item_id
            }

        # make the http GET request to Rainforest API
        itemid_result = requests.get('https://api.bluecartapi.com/request', params)

        # print the JSON response from Rainforest API
        itemid_result=itemid_result.json()
        product_info=json.loads(json.dumps(itemid_result['product']),parse_float=Decimal)
        #print(product_info)
        productTable.put_item(
                Item=product_info
            )

        title=product_info.get('title','')
        description=product_info.get('description','')
        document = {
                    "item_id":product_info['item_id'],
                    "title":title,
                    "description":description
                }

        # Send the request into opensearch.
        search.index(index='walmart', id=product_info['item_id'], body=document, refresh=True)
        time.sleep(5)
    return item_ids


def scrap_walmart(amazon_title_list):
    #walmart_item_ids=[]
    for item in amazon_title_list:
        print(item)

        params = {
        'api_key': 'A03FF5EF9CEE424A9DFD2E0DC2CD1E71',
        'type': 'search',
        'search_term': item
        }

        # make the http GET request to Rainforest API
        api_result = requests.get('https://api.bluecartapi.com/request', params)

        # print the JSON response from Rainforest API
        api_result=api_result.json()

        api_search_result=api_result["search_results"][0:2]

        walmart_item_ids=get_bluecart_product_info_from_idlist(api_search_result)

        l=len(walmart_item_ids)
        for i in range(l):
            itemid=walmart_item_ids[i]
            
            params = {
                'api_key': 'A03FF5EF9CEE424A9DFD2E0DC2CD1E71',
                'type': 'reviews',
                'item_id': itemid,
                'sort_by': 'most_helpful'
                }

            # make the http GET request to BlueCart API
            itemid_result = requests.get('https://api.bluecartapi.com/request', params)

            # print the JSON response from Rainforest API
            itemid_result=itemid_result.json()
            #print(asin_result)
            print(itemid_result)
            if 'reviews' in itemid_result:
                for review in itemid_result['reviews']:
                    product_info=json.loads(json.dumps(review),parse_float=Decimal)
                    #print(product_info)
                    product_info['item_id']=itemid
                    
                    reviewTable.put_item(
                            Item=product_info
                        )
                    time.sleep(5)




