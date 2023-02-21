"""This lambda is executed every time there is an API request to prevent users from accessing the API through the ApiGateway default endpoint, instead of going through Cloudfront"""

import os

def lambda_handler(event, context):
    # Get the headers from the request
    headers = event['headers']

    # Get environment variables
    x_origin_verify = os.environ['x_origin_verify']
    
    # Check if the "x-origin-verify" header is present and has the expected value
    if 'x-origin-verify' in headers and headers['x-origin-verify'] == x_origin_verify:
        # Return the policy document with an "Allow" effect
        return {'isAuthorized': True}
    else:
        # Return an unauthorized response
        return {'isAuthorized': False}
