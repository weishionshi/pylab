#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2022/5/13 17:00
# @file    : crypt.py
from Crypto.Cipher import AES
import base64

class AesCrypt(object):
    def __init__(self,key='sqsfywllahmyyc'):
        self.key = key
        self.mode = AES.MODE_CBC

    # cryptographic functions
    def encrypt(self,text):
        cryptor = AES.new(self.key,self.mode,self.key)
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0'*add)
        self.ciphertext = cryptor.encrypt(text)
        return base64.b64encode(self.ciphertext)


    def decrypt(self,text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(base64.b64decode(text))
        print plain_text
        print plain_text.rstrip('\0')
        return 'ok'

a = prpcrypt()
text = a.encrypt("hello world!")
print text
a.decrypt(text)