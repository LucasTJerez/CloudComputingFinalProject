import json
import boto3
client = boto3.client('comprehend')
import boto3
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
import requests
import random

def truncate_unicode_to_byte_limit(src, byte_limit, encoding='utf-8'):
    return src.encode(encoding)[:byte_limit].decode(encoding, 'ignore')

def lambda_handler(event, context):
    # TODO implement
    productName=' '.join(event['productName'].split(' ')[0:3])
    #print(productName)
    opensearch = boto3.client('opensearch',region_name='us-east-1')
    
    master = "COMSE6998"
    password = "Comse6998!"
    
    #get amazon product asin
    host_url = "https://search-rainforest-product-search-c7dshudmnvp2w4aolgkgxgrijm.us-east-1.es.amazonaws.com/amazon/_search"
    
    query = {
            'size': 1,
            'query': {
                'multi_match': {
                'query': productName,
                'fields': ['title^2','description']
                }
                  
            }
                
        }
            
    response = requests.get(host_url, auth=(master,password),json=query)
    result=response.json()
    
    amazon_resultlist= result["hits"]["hits"]
    amazon_product_id=[]
    for item in amazon_resultlist:
        
        asin=item["_id"]
        #print(asin)
        amazon_product_id.append(asin)
        
        
        
        
    #get walmart item_id    
    host_url = "https://search-rainforest-product-search-c7dshudmnvp2w4aolgkgxgrijm.us-east-1.es.amazonaws.com/walmart/_search"
    
    
    query = {
            'size': 2,
            'query': {
                'multi_match': {
                'query': productName,
                'fields': ['title^2','description']
                }
                  
            }
                
        }
            
    response = requests.get(host_url, auth=(master,password),json=query)
    result=response.json()
    
    walmart_resultlist= result["hits"]["hits"]
    walmart_product_id=[]
    for item in walmart_resultlist:
        item_id=item["_id"]
        #print(item_id)
        walmart_product_id.append(item_id)
        
    
    #get reddit title
    host_url = "https://search-rainforest-product-search-c7dshudmnvp2w4aolgkgxgrijm.us-east-1.es.amazonaws.com/reddit/_search"
    
    
    query = {
            'size': 1,
            'query': {
                'multi_match': {
                'query': productName,
                'fields': ['title']
                }
                  
            }
                
        }
            
    response = requests.get(host_url, auth=(master,password),json=query)
    result=response.json()
    
    reddit_resultlist= result["hits"]["hits"]
    reddit_product_id=[]
    for item in reddit_resultlist:
        item_title=item["_source"]['title']
        print(item_title)
        reddit_product_id.append(item_title)
        
        
        
    
    reviews=[]
    sources=[]
    links=[]
    
    #get amazon review data from dynamodb
    amazonReviewTable = dynamodb.Table('rainforest_review_data')
    
    for productID in amazon_product_id:
        resp=amazonReviewTable.query(
            KeyConditionExpression=Key('asin').eq(productID)
        )
        for item in resp['Items']:
            if 'body' in item:
                reviews.append(item['body'])
                sources.append('amazon')
                links.append("https://www.amazon.com/product-reviews/"+productID)
    #print(reviews)
    
    #get reviews from walmart database
    walmartReviewTable = dynamodb.Table('bluecart_review_data')
    
    for productID in walmart_product_id:
        resp=walmartReviewTable.query(
            KeyConditionExpression=Key('item_id').eq(productID)
        )
        for item in resp['Items']:
            if 'body' in item:
                reviews.append(item['body'])
                sources.append('walmart')
                links.append("https://www.walmart.com/reviews/product/"+productID)
    #print(reviews)
    
    
    #get reviews from reddit database
    redditReviewTable = dynamodb.Table('reddit_review_data')
    
    for productID in reddit_product_id:
        resp=redditReviewTable.query(
            KeyConditionExpression=Key('title').eq(productID)
        )
        for item in resp['Items']:
            if 'review' in item:
                for i in item['review']:
                    reviews.append(i)
                    sources.append('reddit')
                    links.append(item['link'])
    # print(reviews)
    
    key_phrases = []
    
    #do sentimental analysis on review list
    sentiment_list=[]
    for i in range(0,len(reviews),25):
        batch_reviews=reviews[i:i+25]
        batch_reviews_alt=[]
        for r in batch_reviews:
            temp_review=truncate_unicode_to_byte_limit(r, 5000)
            batch_reviews_alt.append(temp_review)
        sentiment=client.batch_detect_sentiment(TextList=batch_reviews_alt,LanguageCode='en')
        sentiment_list+=sentiment['ResultList']
        res = client.batch_detect_key_phrases(TextList=batch_reviews_alt, LanguageCode='en')
        key_phrases += res['ResultList']

    
    positive=0
    negative=0
    neutral=0
    mixed=0
    pro_count=0
    con_count=0
    neutral_count=0
    mixed_count=0
    
    for s in sentiment_list:
        sentimentScoreDic=s['SentimentScore']
        positive+=sentimentScoreDic.get('Positive',0)
        negative+=sentimentScoreDic.get('Negative',0)
        neutral+=sentimentScoreDic.get('Neutral',0)
        mixed+=sentimentScoreDic.get('Mixed',0)
        sentiment=s['Sentiment']
        if sentiment=='POSITIVE':
            pro_count+=1
        if sentiment=='NEGATIVE':
            con_count+=1
        if sentiment=='NEUTRAL':
            neutral_count+=1
        if sentiment=='MIXED':
            mixed_count+=1
        
        
    review_contents = []
    
    for i in range(len(reviews)):
        
        source = sources[i]
        review = reviews[i]
        sentiment = sentiment_list[i]
        link=links[i]
        
        review_contents.append({
            'review':review,
            'source':source,
            'sentiment':sentiment,
            'link':link
        })
    storefront="http://www.amazon.com/exec/obidos/ASIN/" + str(asin)
    
    random.shuffle(review_contents)
    return {
        'statusCode': 200,
        'review_contents':review_contents,
        #'reviews':reviews,
        #'sources':sources,
        #'sentimentList':sentiment_list,
        'pro_count':pro_count,
        'con_count':con_count,
        'neutral_count':neutral_count,
        'mixed_count':mixed_count,
        # 'storefront': asin,
        'walmart_id':walmart_product_id
    }
    
    
    """
    amazonReviewTable = dynamodb.Table('rainforest_review_data')
    
    resp=amazonReviewTable.query(
            KeyConditionExpression=Key('asin').eq(productID)
        )
       
    reviews=[] 
    posts = get_reddit_reviews("")
    for url in posts:
        for comment in posts[url]:
            reviews.append(comment)
    amazon_reviews = get_amazon_product_reviews(productID)
    review += amazon_reviews
    for item in resp['Items']:
        # print(item)
        if 'body' in item:
            reviews.append(item['body'])
            

    return {
        'statusCode': 200,
        'reviewList':reviews,
        'sentimentList':sentiment_list,
        'sentimental':sentimental,
        'sentimentScore':sentimentScore
    }
    """
