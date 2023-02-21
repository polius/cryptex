"""This lambda is executed with the POST API request /encrypt"""

import json
import time
import uuid
import boto3
from datetime import datetime

# Global variable to store the token buckets
token_buckets = {}

def lambda_handler(event, context):
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
    message = body.get('message')
    retention = body.get('retention', 60)
    password = body.get('password')
    if not validate_message(message) or not validate_retention(retention) or not validate_password(password):
        return {
            'statusCode': 400,
            'body': "The request could not be understood or was missing required parameters.\n"
        }

    # Parse retention
    expiration = parse_expiration(retention)

    # Generate short uuid
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    id = ''.join(chars[x] for x in numberToBase(uuid.uuid4().int, len(chars)))

    # Calculate timestamp and expiration datetime
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Create an SQS client
    sqs = boto3.client('sqs')

    # Create a new SQS queue
    tags = {"password": password, "timestamp": timestamp, "retention": str(retention)}
    response = sqs.create_queue(QueueName=f"cryptex-{id}", Attributes={"MaximumMessageSize": "1024", "VisibilityTimeout": "0", "MessageRetentionPeriod": str(retention)}, tags=tags)

    # Create a message in the SQS queue
    sqs.send_message(QueueUrl=response['QueueUrl'], MessageBody=f"{password}|{message.strip()}")

    # Return generated code
    return {
        'statusCode': 200,
        'body': json.dumps({
            "id": id,
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

def numberToBase(n, b):
    # Function to convert a number to a specified base.
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]

def validate_body(value):
    try:
        json.loads(value)
        return True
    except Exception:
        return False

def validate_message(value):
    # Check if the value is None or is greater than 2000 encrypted characters
    if value is None or len(value.strip()) == 0 or len(value) > 2000:
        return False
    return True

def validate_retention(value):
    try:
        # Check if the integer value is in the desired range
        if 60 <= int(value) <= 86400:
            return True
        else:
            return False
    except ValueError:
        # Catch the error if the value cannot be cast to an integer
        return False

def validate_password(value):
    # Check if password is None or is greater than 128 encrypted characters (sha3-512)
    if value is None or len(value.strip()) == 0 or len(value) > 128:
        return False
    return True

def parse_expiration(seconds):
    # Convert the seconds to days, hours, minutes, and seconds
    minutes, sec = divmod(int(seconds), 60)
    hours, min = divmod(minutes, 60)
    days, hour = divmod(hours, 24)
    # Return the results as a dictionary
    return {"days": days, "hours": hour, "minutes": min, "seconds": sec}