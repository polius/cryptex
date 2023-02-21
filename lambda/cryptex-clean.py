"""This lambda is executed daily using EventBridge Scheduler"""

import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # Create an SQS client
    sqs = boto3.client('sqs')

    # Get existing queues with a prefix of "cryptex-"
    kwargs = {
        "QueueNamePrefix": "cryptex-",
        "MaxResults": 1000
    }
    # Continue the loop until all queues have been processed
    while True:
        # Get a batch of up to 1000 queues
        response = sqs.list_queues(**kwargs)

        # Check if there are no queues matching the prefix
        if 'QueueUrls' not in response:
            break

        # Loop through the returned queue URLs
        ndeleted = 0
        for queueUrl in response['QueueUrls']:
            # Get the tags associated with the queue
            try:
                tags = sqs.list_queue_tags(QueueUrl=queueUrl)['Tags']
            except Exception:
                # If there's an error, it might be because the queue has been deleted (race condition)
                # Continue to the next queue
                continue
            # Check if the queue has expired
            has_expired = check_expiration(tags['timestamp'], tags['retention'])
            if has_expired:
                # If the queue has expired, delete it
                try:
                    sqs.delete_queue(QueueUrl=queueUrl)
                    ndeleted += 1
                except Exception:
                    # If there's an error, it might be because the queue has been deleted (race condition)
                    # Continue to the next queue
                    pass

        # If there's no next token, all queues have been processed
        if 'NextToken' not in response:
            break
        # Save the token for the next iteration
        kwargs['NextToken'] = response['NextToken']

    # Return the number of cryptex deleted
    return {
        'statusCode': 200,
        'body': f"{ndeleted} cryptex deleted."
    }

def check_expiration(utc_datetime_str, seconds):
    # parse the input string as a UTC datetime
    utc_datetime = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S")
    # add the number of seconds to the input UTC datetime
    target_datetime = utc_datetime + timedelta(seconds=int(seconds))
    # check if cryptex has expired
    return datetime.utcnow() > target_datetime
