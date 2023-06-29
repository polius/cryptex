"""This lambda is executed with the POST API request /encrypt"""

import json
import time
import uuid
import boto3
import string
import random
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
    password = body.get('password')
    retention = body.get('retention', 60)
    if not validate_message(message) or not validate_retention(retention) or not validate_password(password):
        return {
            'statusCode': 400,
            'body': "The request could not be understood or was missing required parameters.\n"
        }

    # Parse retention
    expiration = parse_expiration(retention)

    # Calculate timestamp and expiration datetime
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Create an SQS client
    sqs = boto3.client('sqs')

    # Assign SQS tags
    tags = {"password": password, "timestamp": timestamp, "retention": str(retention), "uuid": str(uuid.uuid4())}

    # Create a new SQS queue
    while True:
        try:
            id = generate_uuid()
            response = sqs.create_queue(QueueName=f"cryptex-{id}", Attributes={"MaximumMessageSize": "1024", "VisibilityTimeout": "0", "MessageRetentionPeriod": str(retention)}, tags=tags)
            break
        except (sqs.exceptions.QueueNameExists, sqs.exceptions.QueueDeletedRecently):
            # QueueNameExists: If the queue name, attributes or tags don't match with an existing queue.
            # QueueDeletedRecently: The queue has been deleted with the last 60 seconds.
            pass

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

def generate_uuid():
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=8))

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