import os
import json
import boto3
import string
import secrets
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

class Encrypt:
    def __init__(self):
        # Constants
        self._TABLE_NAME = os.environ.get('TABLE_NAME', 'cryptex')
        self._MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 5))
        self._MIN_RETENTION_SECONDS = int(os.environ.get('MIN_RETENTION_SECONDS', 60))
        self._MAX_RETENTION_SECONDS = int(os.environ.get('MAX_RETENTION_SECONDS', 86400))

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
        message = body.get('message')
        password = body.get('password')
        retention = int(body.get('retention', self._MIN_RETENTION_SECONDS))

        # Validate parameters
        if not self.__validate_message(message) or not self.__validate_retention(retention) or not self.__validate_password(password):
            return {
                'statusCode': 400,
                'body': "The request could not be understood or was missing required parameters.\n"
            }

        # Parse retention
        expiration = self.__parse_expiration(retention)

        # Calculate timestamp and expiration datetime
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Try to put the item into the table with a retry mechanism in case the condition is not met
        for retry in range(self._MAX_RETRIES):
            # Generate a new random identifier for each retry
            id = self.__generate_random_string()

            # Attempt to put the item into the DynamoDB table
            if self.__dynamodb_put_item({'id': id, 'message': message, 'password': password, 'retention': retention}):
                # Break the loop if the item is successfully added
                break
        else:
            # If all retries have been exhausted without success
            return {
                'statusCode': 400,
                'body': "An error occurred creating the cryptex. Please try again in a few minutes.\n"
            }

        # Return generated code
        return {
            'statusCode': 200,
            'body': json.dumps({
                "id": id,
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

    def __validate_message(self, value):
        """
        Validate the message parameter.
        """
        # Check if the value is None or is greater than 1000 encrypted characters
        if value is None or len(value.strip()) == 0 or len(value) > 1000:
            return False
        return True

    def __validate_retention(self, value):
        """
        Validate the retention parameter.
        """
        try:
            # Check if the integer value is in the desired range
            if self._MIN_RETENTION_SECONDS <= int(value) <= self._MAX_RETENTION_SECONDS:
                return True
            else:
                return False
        except ValueError:
            # Catch the error if the value cannot be cast to an integer
            return False

    def __validate_password(self, value):
        """
        Validate the password parameter.
        """
        # Check if password is None or is greater than 128 encrypted characters (sha3-512)
        if value is None or len(value.strip()) == 0 or len(value) > 128:
            return False
        return True

    def __parse_expiration(self, seconds):
        """
        Parse the expiration time in seconds into days, hours, minutes, and seconds.
        """
        minutes, sec = divmod(int(seconds), 60)
        hours, min = divmod(minutes, 60)
        days, hour = divmod(hours, 24)
        return {"days": days, "hours": hour, "minutes": min, "seconds": sec}

    def __dynamodb_put_item(self, item):
        """
        Attempt to create an item in DynamoDB.
        """
        try:
            self._dynamodb.put_item(
                TableName=self._TABLE_NAME,
                Item={
                    'id': {'S': item['id']},
                    'message': {'S': item['message'].strip()},
                    'password': {'S': item['password']},
                    'ttl': {'N': str(int((datetime.utcnow() + timedelta(seconds=item['retention'])).timestamp()))}
                },
                ConditionExpression='attribute_not_exists(id)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print("Item with the same id already exists. Did not add the item.")
            else:
                # Handle other errors
                print(f"Error: {e}")
            return False

    def __generate_random_string(self):
        """
        Generate a random string in the format XXX-XXXX-XXX.
        """
        parts = [
            ''.join(secrets.choice(string.ascii_lowercase) for _ in range(length))
            for length in [3, 4, 3]
        ]
        return '-'.join(parts)
