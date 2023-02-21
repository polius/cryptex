"""This lambda is executed with the POST API request /decrypt"""

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

    # Get queue tags
    try:
        tags = sqs.list_queue_tags(QueueUrl=f"{sqs_url}{identifier}")['Tags']
    except Exception:
        return {
            'statusCode': 400,
            'body': "This cryptex does not exist or it doesn't open with the provided password.\n"
        }

    # Check the expiration status of the cryptex
    has_expired = check_expiration(tags['timestamp'], tags['retention'])

    # Delete the queue if the cryptex has expired
    if has_expired:
        try:
            sqs.delete_queue(QueueUrl=f"{sqs_url}{identifier}")
        except Exception:
            pass
        finally:
            return {
                'statusCode': 400,
                'body': "This cryptex does not exist or it doesn't open with the provided password.\n"
            }

    # Open cryptex and retrieve its data
    else:
        try:
            message = sqs.receive_message(QueueUrl=f"{sqs_url}{identifier}", MaxNumberOfMessages=1, VisibilityTimeout=0, WaitTimeSeconds=1)['Messages'][0]['Body']    
            message_split = message.split('|', 1)
        except Exception:
            return {
                'statusCode': 400,
                'body': "An error occurred retriving the cryptex message. Please try again.\n"
            }

        # Validate the provided password against the stored password
        if password != message_split[0]:
            return {
                'statusCode': 400,
                'body': "This cryptex does not exist or it doesn't open with the provided password.\n"
            }
    
    # Calculate the remaining time until expiration
    expiration = time_difference(tags['timestamp'], tags['retention'])

    # Return the message and the remaining time until expiration
    return {
        'statusCode': 200,
        'body': json.dumps({
            "message": message_split[1],
            "expiration": f"{expiration['days']} days, {expiration['hours']} hours, {expiration['minutes']} minutes, {expiration['seconds']} seconds"
        }) + '\n'
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

def check_expiration(utc_datetime_str, seconds):
    # Parse the input string as a UTC datetime object.
    utc_datetime = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S")

    # Add the number of seconds to the input UTC datetime.
    target_datetime = utc_datetime + timedelta(seconds=int(seconds))

    # Check if the current UTC datetime is greater than the target datetime.
    return datetime.utcnow() > target_datetime

def time_difference(utc_datetime_str, seconds):
    # Parse the input string as a UTC datetime object.
    utc_datetime = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S")

    # Add the number of seconds to the input UTC datetime.
    target_datetime = utc_datetime + timedelta(seconds=int(seconds))

    # Calculate the difference between the current UTC time and the target UTC time.
    difference = target_datetime - datetime.utcnow()

    # Convert the difference to days, hours, minutes, and seconds.
    days, remainder = divmod(difference.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Return the results as a dictionary.
    return {"days": int(days), "hours": int(hours), "minutes": int(minutes), "seconds": int(seconds)}
