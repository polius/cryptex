import os
import json
import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

class Destroy:
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

        # Delete the cryptex
        if self.__dynamodb_delete_item({'id': id, 'password': password}):
            return {
                'statusCode': 200,
                'body': "The cryptex has been destroyed.\n"
            }
        else:
            return {
                'statusCode': 400,
                'body': "This cryptex does not exist or it doesn't open with the provided password.\n"
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

    def __dynamodb_delete_item(self, item):
        """
        Attempt to delete an item from DynamoDB using the specified key and password.
        """
        try:
            # Attempt to delete the item with a conditional expression
            self._dynamodb.delete_item(
                TableName=self._TABLE_NAME,
                Key={'id': {'S': item['id']}},
                ConditionExpression='#password = :password AND #ttl > :ttl',
                ExpressionAttributeNames={
                    '#password': 'password',
                    '#ttl': 'ttl'
                },
                ExpressionAttributeValues={
                    ':password': {
                        'S': item['password']
                    },
                    ':ttl': {
                        'N': str(int(datetime.utcnow().timestamp()))
                    }
                }
            )
            return True
        except ClientError as e:
            print(f"ERROR: {e}")
            return False
