"""This lambda is executed with the POST API request /destroy"""

import os
import json
import time
import boto3
from datetime import datetime, timedelta

# Global variable to store the token buckets
token_buckets = {}

def lambda_handler(event, context):
    # Get environment variables
    sqs_url = os.environ['sqs_url']

    # Check ratelimits
    if not check_ratelimits(event):
        return {
            "statusCode": 429,
            "body": "Rate limit exceeded. Try again in a few seconds.\n"
        }

    # Validate body parameters
    body = event.get('body')
    if not validate_body(body):
        return {
            'statusCode': 400,
            'body': "The request could not be understood or was missing required parameters.\n"
        }

     # Get and validate the parameters from the request data
    body = json.loads(body)
    identifier = body.get('id')
    password = body.get('password')

    # Check if parameters are present
    if not identifier or not password:
        return {
            'statusCode': 400,
            'body': "The request could not be understood or was missing required parameters.\n"
        }

    # Create an SQS client
    sqs = boto3.client('sqs')

    # Open cryptex and retrieve its data
    try:
        message = sqs.receive_message(QueueUrl=f"{sqs_url}{identifier}", MaxNumberOfMessages=1, VisibilityTimeout=0, WaitTimeSeconds=1)['Messages'][0]['Body']    
        message_split = message.split('|', 1)
    except Exception:
        return {
            'statusCode': 400,
            'body': "This cryptex does not exist or it doesn't open with the provided password.\n"
        }

    # Validate the provided password against the encrypted password
    if password != message_split[0]:
        return {
            'statusCode': 400,
            'body': "This cryptex does not exist or it doesn't open with the provided password.\n"
        }

    # Delete the cryptex
    try:
        sqs.delete_queue(QueueUrl=f"{sqs_url}{identifier}")
    except Exception:
        return {
            'statusCode': 400,
            'body': "This cryptex does not exist or it doesn't open with the provided password.\n"
        }

    # Return the message and the remaining time until expiration
    return {
        'statusCode': 200,
        'body': json.dumps("The cryptex has been destroyed.\n")
    }

def check_ratelimits(event):
    # Limit api requests (1 request per second per IP)
    sourceIp = event['requestContext']['http']['sourceIp']
    if sourceIp not in token_buckets:
        token_buckets[sourceIp] = time.time()
    elif time.time() - token_buckets[sourceIp] < 1:
        return False
    else:
        token_buckets[sourceIp] = time.time()
    return True

def validate_body(value):
    try:
        json.loads(value)
        return True
    except Exception:
        return False

