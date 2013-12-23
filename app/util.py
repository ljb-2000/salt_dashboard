#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/20 15:20
def AESencrypt(password, plaintext, base64=False):
    import hashlib, os
    from Crypto.Cipher import AES

    SALT_LENGTH = 32
    DERIVATION_ROUNDS = 1337
    BLOCK_SIZE = 16
    KEY_SIZE = 32
    MODE = AES.MODE_CBC

    salt = os.urandom(SALT_LENGTH)
    iv = os.urandom(BLOCK_SIZE)

    paddingLength = 16 - (len(plaintext) % 16)
    paddedPlaintext = plaintext + chr(paddingLength) * paddingLength
    derivedKey = password
    for i in range(0, DERIVATION_ROUNDS):
        derivedKey = hashlib.sha256(derivedKey + salt).digest()
    derivedKey = derivedKey[:KEY_SIZE]
    cipherSpec = AES.new(derivedKey, MODE, iv)
    ciphertext = cipherSpec.encrypt(paddedPlaintext)
    ciphertext = ciphertext + iv + salt
    if base64:
        import base64

        return base64.b64encode(ciphertext)
    else:
        return ciphertext.encode("hex")


def AESdecrypt(password, ciphertext, base64=False):
    import hashlib
    from Crypto.Cipher import AES

    SALT_LENGTH = 32
    DERIVATION_ROUNDS = 1337
    BLOCK_SIZE = 16
    KEY_SIZE = 32
    MODE = AES.MODE_CBC

    if base64:
        import base64

        decodedCiphertext = base64.b64decode(ciphertext)
    else:
        decodedCiphertext = ciphertext.decode("hex")
    startIv = len(decodedCiphertext) - BLOCK_SIZE - SALT_LENGTH
    startSalt = len(decodedCiphertext) - SALT_LENGTH
    data, iv, salt = decodedCiphertext[:startIv], decodedCiphertext[startIv:startSalt], decodedCiphertext[startSalt:]
    derivedKey = password
    for i in range(0, DERIVATION_ROUNDS):
        derivedKey = hashlib.sha256(derivedKey + salt).digest()
    derivedKey = derivedKey[:KEY_SIZE]
    cipherSpec = AES.new(derivedKey, MODE, iv)
    plaintextWithPadding = cipherSpec.decrypt(data)
    paddingLength = ord(plaintextWithPadding[-1])
    plaintext = plaintextWithPadding[:-paddingLength]
    return plaintext


from functools import wraps
from flask import request, redirect, current_app


def ssl_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        print "*" * 60
        print current_app.config
        if current_app.config.get("SSL"):
            print "*" * 60
            print "SSL"
            print "*" * 60
            if request.is_secure:
                return fn(*args, **kwargs)
            else:
                return redirect(request.url.replace("http://", "https://"))

        return fn(*args, **kwargs)

    return decorated_view