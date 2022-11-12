import json
import boto3
import os
import sys
import uuid
import time
from botocore.vendored import requests
from requests.auth import HTTPBasicAuth
basic = HTTPBasicAuth('user','Ttntest@Cated86')

ES_HOST = 'https://search-photos-sjzfxctg6nxjwr2eadpkmuz7lq.us-east-1.es.amazonaws.com'
REGION = 'us-east-1'

def get_url(es_index, es_type, keyword):
    url = ES_HOST + '/' + es_index + '/' + es_type + '/_search?q=' + keyword.lower()
    return url

def lambda_handler(event, context):
 # recieve from API Gateway
 print("EVENT --- {}".format(json.dumps(event)))
 
 headers = { "Content-Type":"application/json"}
	
 lex = boto3.client('lex-runtime')

 query = event["queryStringParameters"]["q"]
 

 lex_response = lex.post_text(
  botName='searchPhoto',
  botAlias='searchPhoto',
  userId='test',
  inputText=query
  )
 
 print("LEX RESPONSE --- {}".format(json.dumps(lex_response)))

 slots = lex_response['slots']

 img_list = []
 for i, tag in slots.items():
  if tag:
   url = get_url('photos', 'Photo', tag)
   print("ES URL --- {}".format(url))

   es_response = requests.get(url, headers=headers, auth = basic).json()
   print("ES RESPONSE --- {}".format(json.dumps(es_response)))

   es_src = es_response['hits']['hits']
   print("ES HITS --- {}".format(json.dumps(es_src)))

   for photo in es_src:
    labels = [word.lower() for word in photo['_source']['labels']]
    if tag in labels:
     objectKey = photo['_source']['objectKey']
     img_url = 'https://nyu-22fall-csgy9223-assignment2-yp2212-b2.s3.amazonaws.com/' + objectKey
     img_list.append(img_url)

 if img_list:
  return {
   'statusCode': 200,
   'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            "Access-Control-Allow-Methods": "OPTIONS, GET"
   },
   'body': json.dumps(img_list)
  }
 else:
  return {
   'statusCode': 200,
   'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            "Access-Control-Allow-Methods": "OPTIONS, GET"
   },
   'body': json.dumps("No such photos.")
  }