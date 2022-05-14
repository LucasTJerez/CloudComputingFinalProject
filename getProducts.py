import json
import logging
import requests
import boto3
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    # TODO implement
    productName=event['productName']
    
    
    opensearch = boto3.client('opensearch',region_name='us-east-1')
    
    master = "COMSE6998"
    password = "Comse6998!"
    host_url = "https://search-rainforest-product-search-c7dshudmnvp2w4aolgkgxgrijm.us-east-1.es.amazonaws.com/amazon/_search"
    
    
    query = {
            'size': 15,
            'query': {
                'multi_match': {
                'query': productName,
                'fields': ['title']
                }
                  
            }
                
        }
            
    response = requests.get(host_url, auth=(master,password),json=query)
    result=response.json()
    
    amazonProductTable = dynamodb.Table('rainforest_product_data')
    
    resultlist= result["hits"]["hits"]
    returnList=[]
    for item in resultlist:
        asin=item["_id"]
        print(asin)
        resp = amazonProductTable.get_item(
            Key={
                'asin' : asin,
            }
        )
        
        
        item_origin_dic=resp.get('Item')
        item_dict={}
        item_dict['brand']=item_origin_dic.get('brand','')
        item_dict['productName']=item_origin_dic.get('title','')
        images=item_origin_dic.get('images',None)
        image_list=[]
        for image in images:
            image_list.append(image['link'])
        item_dict['image']=image_list
        buyingoption=item_origin_dic.get('more_buying_choices',None)#
        if buyingoption:
            item_dict['price']=buyingoption[0]['price']['raw']
        item_dict['storefront'] = "http://www.amazon.com/exec/obidos/ASIN/" + str(asin)
        returnList.append(item_dict)
        

    return returnList