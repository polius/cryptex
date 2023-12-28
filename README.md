# Cryptex.ninja

[https://cryptex.ninja](https://cryptex.ninja)

Cryptex.ninja is a web application that provides secure messaging with end-to-end encryption.

Ensuring the security and confidentiality of your information is a top priority. Cryptex.ninja employs robust encryption methods, including AES-256 and SHA3-512, to protect your data from unauthorized access.

The encryption and decryption process takes place directly on your device, allowing only the intended recipient to access and decrypt the data using the provided password. This approach ensures maximum security and privacy for your communication.

Furthermore, Cryptex.ninja generates a unique web address when a message is shared. To access the message, a password is required, adding an extra layer of security and ensuring that only authorized users can read your communication.

Your messages will always remain private and confidential. Cryptex.ninja prioritizes stringent security measures to safeguard your information and respect your privacy.

### How it works under the hood

All data stored in Cryptex, the message and password, is encrypted in the user's browser just before being sent to the Cryptex infrastructure. The message is encrypted using AES-256, and the password is encrypted using SHA3-512.

When a user attempts to open a cryptex, they provide their password. This password is then encrypted using SHA3-512 in the user's browser and after that is sent to the Cryptex infrastructure. Then the backend compares the stored SHA3-512 password to the one provided by the user (which is also encrypted in SHA3-512). If the passwords match, Cryptex sends back the message (which is encrypted with AES-256), and the decryption process begins in the user's browser.

All encryption and decryption occurs in the user's browser, and the server only receives already-encrypted data. Also, all data is transmitted in encrypted form.

### Infrastructure

The infrastructure is build using AWS and consists of the following components:

**Website (cryptex.ninja)**

```
User's browser → Cloudflare (DDOS Protection + CDN) → Cloudfront → S3
```

**API (api.cryptex.ninja)**

```
User's browser → Cloudflare (DDOS Protection + Rate Limits) → Api Gateway → Lambda → DynamoDB
```

### API Reference

These are the different API calls that Cryptex supports:

**Encrypt**

```
curl -X POST https://api.cryptex.ninja/encrypt -H "Content-Type: application/json" -d '{"message": "Hello World!", "password": "super_secret"}'
```

**Decrypt**

```
curl -X POST https://api.cryptex.ninja/decrypt -H "Content-Type: application/json" -d '{"id": "xxx-xxxx-xxx", "password": "super_secret"}'
```

**Destroy**

```
curl -X POST https://api.cryptex.ninja/destroy -H "Content-Type: application/json" -d '{"id": "xxx-xxxx-xxx", "password": "super_secret"}'
```

Released under the MIT License.