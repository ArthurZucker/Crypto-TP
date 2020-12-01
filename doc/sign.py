from hashlib import sha256, md5
import random
import base64
import sys
import math
from subprocess import Popen, PIPE, check_output
import os
import base64

def sign(plaintext,pk="../private-key"):
    """
    openssl dgst -sha256 -sign secret_key
    """
    key_file = pk+".pem"
    # prépare les arguments à envoyer à openssl
    # f = open(key_file, "a")
    # f.write(key)
    # f.close()
    args = ['openssl', 'dgst', '-sha256', '-sign',key_file]

    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')

    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    # envoie plaintext sur le stdin de openssl, récupère stdout et stderr
    stdout, stderr = pipeline.communicate(plaintext)
    print(stdout.hex())

    error_message = stderr.decode()
    if error_message != '':
        raise OpensslError(error_message)
    return stdout

if __name__ == "__main__":
    sign(sys.argv[1],"private-key")


