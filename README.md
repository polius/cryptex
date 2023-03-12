# Cryptex.ninja

[https://cryptex.ninja](https://cryptex.ninja)

Cryptex.ninja is a web application that provides secure messaging with end-to-end encryption.

Our top priority is to ensure that your information remains secure and confidential. To achieve this, we employ strong encryption methods, such as AES-256 and SHA3-512, to protect your data from unauthorized access. Your information is encrypted on your device, meaning that only the intended recipient can access it with the correct password. This provides maximum security and privacy for your communication.

In addition, Cryptex.ninja generates a unique web address when you share a message, which requires a password to access. This feature adds an extra layer of security to ensure that only authorized users can read your communication.

Your messages will always remain private and confidential.

### How it works under the hood

All data stored in Cryptex, the message and password, is encrypted in the user's browser just before being sent to the Cryptex infrastructure. The message is encrypted using AES-256, and the password is encrypted using SHA3-512.

When a user attempts to open a cryptex, they provide their password. This password is then encrypted using SHA3-512 in the user's browser and after that is sent to the Cryptex infrastructure. Then the backend compares the stored SHA3-512 password to the one provided by the user (which is also encrypted in SHA3-512). If the passwords match, Cryptex sends back the message (which is encrypted with AES-256), and the decryption process begins in the user's browser.

All encryption and decryption occurs in the user's browser, and the server only receives already-encrypted data. Also, all data is transmitted in encrypted form.

The infrastructure is build using AWS and consists of the following components:

User's browser --> Cloudfront --> Api Gateway --> Lambda --> SQS
