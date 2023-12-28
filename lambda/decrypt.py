import os
import json
import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

class Decrypt:
    def __init__(self):
        # Constants
        self._TABLE_NAME = os.environ.get('TABLE_NAME', 'cryptex')

        # DynamoDB client
        self._dynamodb = boto3.client('dynamodb')

    def run(self, event, context):
        # Validate body parameters
        body = event.get('body')
        if not self.__validate_body(body):
            return {
                'statusCode': 400,
                'body': "The request could not be understood or was missing required parameters.\n"
            }

        # Get parameters
        body = json.loads(body)
        id = body.get('id')
        password = body.get('password')

        # Validate parameters
        if not id or not password:
            return {
                'statusCode': 400,
                'body': "The request could not be understood or was missing required parameters.\n"
            }

        # Open cryptex and retrieve its data
        item = self.__dynamodb_get_item({'id': id})

        # Check if item exists
        if not item:
            return {
                'statusCode': 400,
                'body': "This cryptex does not exist or it doesn't open with the provided password.\n"
            }

        # Validate the provided password against the stored password
        if password != item['password']['S']:
            return {
                'statusCode': 400,
                'body':"This cryptex does not exist or it doesn't open with the provided password.\n"
            }

        # Calculate the remaining time until expiration
        expiration = self.__time_difference(item['ttl']['N'])

        # Return the message and the remaining time until expiration
        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": item['message']['S'],
                "expiration": f"{expiration['days']} days, {expiration['hours']} hours, {expiration['minutes']} minutes, {expiration['seconds']} seconds"
            }) + '\n'
        }

    def __validate_body(self, value):
        """
        Validate the request body by attempting to parse it as JSON.
        """
        try:
            json.loads(value)
            return True
        except Exception:
            return False

    def __time_difference(self, ttl):
        """
        Calculate the difference between the current UTC time and the target UTC time.
        """
        difference = datetime.utcfromtimestamp(int(ttl)) - datetime.utcnow()

        # Convert the difference to days, hours, minutes, and seconds.
        days, remainder = divmod(difference.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Return the results as a dictionary.
        return {"days": int(days), "hours": int(hours), "minutes": int(minutes), "seconds": int(seconds)}

    def __dynamodb_get_item(self, item):
        """
        Retrieve an item from DynamoDB using the specified id.
        """
        try:
            response = self._dynamodb.query(
                TableName=self._TABLE_NAME,
                KeyConditionExpression='#id = :id', 
                FilterExpression='#ttl > :ttl', 
                ExpressionAttributeNames={
                    '#id': 'id',
                    '#ttl': 'ttl'
                },
                ExpressionAttributeValues={
                    ':id': { 
                        'S': item['id']
                    },
                    ':ttl': { 
                        'N': str(int(datetime.utcnow().timestamp()))
                    }
                }
            )
            return response['Items'][0] if response['Count'] > 0 else None
        except ClientError as e:
            print(f"ERROR: {e}")
            return None
