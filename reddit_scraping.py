import praw
import json
# set up the request parameters

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


reviewTable=dynamodb.Table('reddit_review_data')

reddit = praw.Reddit(client_id='5zCZemZGI-1yFGa7FVHbQA', \
                     client_secret='OF-sXwQ9ZDqO1gSd4Qcn4-Bgm0haOg', \
                     user_agent='doublecheck', \
                     username='doublecheckftw', \
                     password='Comse6998')


def scrap_reddit(brand,product_list):
    #brand='apple'
    for q_string in product_list:
        link_to_comment = {}
        count = 0
        """
        for submission in reddit.subreddit("Apple").search(q_string+):
        """

        for submission in reddit.subreddit(brand).search(' '.join(q_string.split(" ")[0:3])+" review"):
            

            if "WORTH" in submission.title.upper() or "REVIEW" in submission.title.upper():
                for comment in submission.comments.list():
                    try:
                        if submission.url in link_to_comment:
                            link_to_comment[submission.url] += [comment.body]
                        else:
                            link_to_comment[submission.url] = [comment.body]
                        count+=1
                    except:
                        pass
                


            # link_to_comment[submission.url] = submission.comments.list()
            if count == 5:

                break


        for submission in reddit.subreddit("Apple").search(' '.join(q_string.split(" ")[0:3])+" worth"):
            

            if "WORTH" in submission.title.upper() or "REVIEW" in submission.title.upper():
                for comment in submission.comments.list():
                    try:
                        if submission.url in link_to_comment:
                            link_to_comment[submission.url] += [comment.body]
                        else:
                            link_to_comment[submission.url] = [comment.body]
                        count+=1
                    except:
                        pass
                


            # link_to_comment[submission.url] = submission.comments.list()
            if count == 5:

                break
            

        print(link_to_comment)



        for key,val in link_to_comment.items():
            document = {
                            "link":key,
                            "title":q_string,
                        }

            # Send the request into opensearch.
            search.index(index='reddit', id=key, body=document, refresh=True)
            reviewTable.put_item(
                    Item={"link":key,
                        "title":q_string,
                        "review":val
                        }
                )

