import json

import encrypt
import decrypt
import destroy

def lambda_handler(event, context):
    cryptex_encrypt = encrypt.Encrypt()
    cryptex_decrypt = decrypt.Decrypt()
    cryptex_destroy = destroy.Destroy()
    
    if event['requestContext']['http']['method'] == 'POST':
        if event['requestContext']['http']['path'] == '/encrypt':
            return cryptex_encrypt.run(event, context)
        elif event['requestContext']['http']['path'] == '/decrypt':
            return cryptex_decrypt.run(event, context)
        elif event['requestContext']['http']['path'] == '/destroy':
            return cryptex_destroy.run(event, context)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Cryptex!')
    }
