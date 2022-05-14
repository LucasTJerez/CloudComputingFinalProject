import requests
import json
# set up the request parameters
import time

import boto3
from decimal import Decimal
from reddit_scraping import scrap_reddit
from walmartscraping import scrap_walmart
dynamodb=boto3.resource('dynamodb')

productTable = dynamodb.Table('rainforest_product_data')

reviewTable=dynamodb.Table('rainforest_review_data')

params = {
  'api_key': 'BDCD9EFBD1914C6E9EE515D4C392B64D',
  'type': 'search',
  'amazon_domain': 'amazon.com',
  'search_term': 'ipad',
  'sort_by': 'featured'
}
brand='apple'

# make the http GET request to Rainforest API
api_result = requests.get('https://api.rainforestapi.com/request', params)

# print the JSON response from Rainforest API
api_result=api_result.json()

api_search_result=api_result["search_results"]


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

asins=[]
l=len(api_search_result)
print(l)


amazon_title_list=[]
for i in range(16):
    item=api_search_result[i]
    print(i)

    asin=item['asin']
    asins.append(asin)
    params = {
        'api_key': 'BDCD9EFBD1914C6E9EE515D4C392B64D',
        'type': 'product',
        'amazon_domain': 'amazon.com',
        'asin': asin
        }

    # make the http GET request to Rainforest API
    asin_result = requests.get('https://api.rainforestapi.com/request', params)

    # print the JSON response from Rainforest API
    asin_result=asin_result.json()
    product_info=json.loads(json.dumps(asin_result['product']),parse_float=Decimal)

    productTable.put_item(
            Item=product_info
        )

    title=product_info.get('title','')
    amazon_title_list.append(title)
    description=product_info.get('description','')
    document = {
                "asin":product_info['asin'],
                "title":title,
                "description":description
            }

    # Send the request into opensearch.
    search.index(index='amazon', id=product_info['asin'], body=document, refresh=True)


    time.sleep(5)


asins=[]
l=len(api_search_result)
print(l)
for i in range(16):
    print(i)
    item=api_search_result[i]

    asin=item['asin']
    asins.append(asin)
    params = {
        'api_key': 'BDCD9EFBD1914C6E9EE515D4C392B64D',
        'type': 'reviews',
        'amazon_domain': 'amazon.com',
        'asin': asin,
        'sort_by': 'most_helpful',
        'reviewer_type': 'all'
        }

    # make the http GET request to Rainforest API
    asin_result = requests.get('https://api.rainforestapi.com/request', params)

    # print the JSON response from Rainforest API
    asin_result=asin_result.json()
    #print(asin_result)
    for review in asin_result['reviews']:
        product_info=json.loads(json.dumps(review),parse_float=Decimal)
        #print(product_info)
        product_info['asin_sub']=product_info.get('asin',None)
        product_info['asin']=asin
        
        reviewTable.put_item(
                Item=product_info
            )
        time.sleep(1)

print(amazon_title_list)

scrap_reddit(brand,amazon_title_list)

scrap_walmart(amazon_title_list)