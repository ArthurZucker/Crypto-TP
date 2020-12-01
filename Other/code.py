from client import *
from openssl import *
from hashlib import sha256, md5
import random
import base64
import math
from subprocess import Popen, PIPE, check_output
import os
import base64
# ce script suppose qu'il a affaire à OpenSSL v1.1.1
# vérifier avec "openssl version" en cas de doute.
# attention à MacOS, qui fournit à la place LibreSSL.

# en cas de problème, cette exception est déclenchée
class OpensslError(Exception):
    pass


def genpkey(nb_bits = 1024):
    """
    openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:1024 > public_key
    openssl pkey -in public_key -pubout
    """
    key_file = "pub_key"

    args = ['openssl', 'genpkey','-algorithm','RSA', '-pkeyopt', 'rsa_keygen_bits:{}'.format(nb_bits)]
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    content  = pipeline.stdout.read()
    args2 = ['openssl', 'pkey','-pubout']
    pipeline2 = Popen(args2, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout1,stderr = pipeline2.communicate(content)

    args3 = ['openssl','pkey']
    pipeline3 = Popen(args3, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout2,stderr = pipeline3.communicate(content)
    # OK, openssl a envoyé le chiffré sur stdout, en base64.
    # On récupère des bytes, donc on en fait une chaine unicode
    return (stdout1.decode(),stdout2.decode())

# Il vaut mieux être conscient de la différence entre str() et bytes()
# cf /usr/doc/strings.txt

def gentempkey(bsize=16):
    """
    openssl rand -base64 bsize
    """
    args = ['openssl','rand','-base64',str(bsize)]
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return pipeline.stdout.read()


def pkencrypt(plaintext, passphrase,enc=1):
    """
    openssl pkeyutl -encrypt -pubin -inkey
    """
    key_file = "key_file.txt"
    # prépare les arguments à envoyer à openssl
    f = open(key_file, "a")
    f.write(passphrase)
    f.close()
    if (enc==1):
        args = ['openssl', 'pkeyutl','-encrypt', '-pubin', '-inkey' ,key_file]
    else:
        args = ['openssl', 'pkeyutl','-decrypt', '-inkey' ,key_file]
    # si le message clair est une chaine unicode, on est obligé de
    # l'encoder en bytes() pour pouvoir l'envoyer dans le pipeline vers
    # openssl
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')

    # ouvre le pipeline vers openssl. Redirige stdin, stdout et stderr
    #    affiche la commande invoquée
    print('debug : {0}'.format(' '.join(args)))
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    # envoie plaintext sur le stdin de openssl, récupère stdout et stderr
    stdout, stderr = pipeline.communicate(plaintext)

    # si un message d'erreur est présent sur stderr, on arrête tout
    # attention, sur stderr on récupère des bytes(), donc on convertit
    error_message = stderr.decode()
    if error_message != '':
        raise OpensslError(error_message)
    os.system("rm -rf "+key_file)
    # OK, openssl a envoyé le chiffré sur stdout, en base64.
    # On récupère des bytes, donc on en fait une chaine unicode
    return stdout


def encrypt(plaintext, passphrase, cipher='aes-128-cbc'):
    """invoke the OpenSSL library (though the openssl executable which must be
       present on your system) to encrypt content using a symmetric cipher.

       The passphrase is an str object (a unicode string)
       The plaintext is str() or bytes()
       The output is bytes()

       # encryption use
       >>> message = "texte avec caractères accentués"
       >>> c = encrypt(message, 'foobar')

    """
    # prépare les arguments à envoyer à openssl
    pass_arg = 'pass:{0}'.format(passphrase)
    args = ['openssl', 'enc', '-' + cipher, '-base64', '-pass', pass_arg, '-pbkdf2']

    # si le message clair est une chaine unicode, on est obligé de
    # l'encoder en bytes() pour pouvoir l'envoyer dans le pipeline vers
    # openssl
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')

    # ouvre le pipeline vers openssl. Redirige stdin, stdout et stderr
    #    affiche la commande invoquée
    #    print('debug : {0}'.format(' '.join(args)))
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    # envoie plaintext sur le stdin de openssl, récupère stdout et stderr
    stdout, stderr = pipeline.communicate(plaintext)

    # si un message d'erreur est présent sur stderr, on arrête tout
    # attention, sur stderr on récupère des bytes(), donc on convertit
    error_message = stderr.decode()
    if error_message != '':
        raise OpensslError(error_message)

    # OK, openssl a envoyé le chiffré sur stdout, en base64.
    # On récupère des bytes, donc on en fait une chaine unicode
    return stdout.decode()

def sign(plaintext,key):
    """
    openssl dgst -sha256 -sign secret_key
    """
    key_file = "key_file.txt"
    # prépare les arguments à envoyer à openssl
    f = open(key_file, "a")
    f.write(key)
    f.close()
    args = ['openssl', 'dgst', '-sha256', '-sign',key_file]

    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')

    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    # envoie plaintext sur le stdin de openssl, récupère stdout et stderr
    stdout, stderr = pipeline.communicate(plaintext)

    error_message = stderr.decode()
    if error_message != '':
        raise OpensslError(error_message)
    os.system("rm -rf "+key_file)
    return stdout

def print_certificate(certificat):
    args = ['openssl', 'x509', '-text', '-noout']
    if isinstance(certificat, str):
        certificat = certificat.encode('utf-8')
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipeline.communicate(certificat)
    return stdout.decode()
def get_pub_cert(certificat):
    args = ['openssl', 'x509', '-pubkey', '-noout']
    if isinstance(certificat, str):
        certificat = certificat.encode('utf-8')
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipeline.communicate(certificat)
    return stdout.decode()
def get_sub_cert(certificat):
    args = ['openssl', 'x509', '-subject', '-noout']
    if isinstance(certificat, str):
        certificat = certificat.encode('utf-8')
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipeline.communicate(certificat)
    return stdout.decode()
def verify_cert(certificat):
    args = ['openssl', 'verify']
    if isinstance(certificat, str):
        certificat = certificat.encode('utf-8')
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipeline.communicate(certificat)
    return stdout.decode()

def verify_certificate2(trusted, untrusted2):
    with open("trusted_certificate.pem","w") as f:
        f.write(trusted)
    args = ['openssl', 'verify','-trusted','trusted_certificate.pem']
    if isinstance(untrusted2, str):
        untrusted2 = untrusted2.encode('utf-8')
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipeline.communicate(untrusted2)
    #os.system("rm -rf trusted_certificate.pem")
    if stderr.decode() != '':
        print(stderr.decode())
        return False

    return True


def verify_certificate(trusted, untrusted1,untrusted2):
    with open("trusted_certificate.pem","w") as f:
        f.write(trusted)
    with open("untrusted.pem","w") as f:
        f.write(untrusted1)
    args = ['openssl', 'verify','-trusted','trusted_certificate.pem','-untrusted','untrusted.pem']
    if isinstance(untrusted2, str):
        untrusted2 = untrusted2.encode('utf-8')
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipeline.communicate(untrusted2)
    if stderr.decode() != '':
        return False
    os.system("rm -rf trusted_certificate.pem untrusted.pem")
    return True

def verify(bank_CA,sample):
    # bank_name,bank_certificate,card_certificate,challenge,signature,card_number
    bank_name = sample["bank-name"]
    bank_certificate = sample["bank-certificate"]
    card_certificate = sample["card-certificate"]
    challenge = sample["challenge"]
    signature = sample["signature"]
    card_number = sample["card-number"]
    verif = verify_certificate(bank_CA,bank_certificate,card_certificate)
    verif2 = (bank_name==get_bank_name(bank_certificate))
    verif3 = (card_number==get_card_nb(card_certificate))
    verif4 = verify_challenge(card_certificate,signature,challenge)
    #print("verify 1 = {}\nverify 2 = {}\nverify 3 = {}\nverify 4 = {}".format(verif,verif2,verif3,verif4))
    return (verif and verif2 and verif3 and verif4)

def verify_challenge(certificate,signature,challenge):
    with open("public_key.pem","w") as f:
        f.write(get_pub_cert(certificate))
    with open("signature.bin","wb") as f:
        f.write(base64.b64decode(signature))
    args = ['openssl', 'dgst','-sha256','-verify','public_key.pem','-signature','signature.bin']
    if isinstance(challenge, str):
        challenge = challenge.encode('utf-8')
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipeline.communicate(challenge)
    if stdout.decode().split(' ')[1].strip('\n')=='Failure':
        return False
    os.system("rm -rf public_key.pem signature.bin")
    return True

def verify_signature(certificate,signature,challenge):
    with open("public_key.pem","w") as f:
        f.write(get_pub_cert(certificate))
    with open("signature.bin","wb") as f:
        f.write(base64.b64decode(signature))
    args = ['openssl', 'dgst','-sha256','-verify','public_key.pem','-signature','signature.bin']
    if isinstance(challenge, str):
        challenge = challenge.encode('utf-8')
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipeline.communicate(challenge)
    os.system("rm -rf public_key.pem signature.bin")
    return stdout.decode()

def get_bank_name(certificat):
    return get_sub_cert(certificat).split('=')[2].split('OU')[0][1:-2].strip("\"")
def get_card_nb(certificat):
        return get_sub_cert(certificat).split('CN')[1].split('=')[1].strip(' ').strip('\n')

def decrypt(cyphertext, passphrase, cipher='aes-128-cbc'):
    pass_arg = 'pass:{0}'.format(passphrase)
    args = ['openssl', 'enc',  '-base64','-' + cipher,'-d','-pass', pass_arg,'-pbkdf2',]
    if isinstance(cyphertext, str):
        cyphertext = cyphertext.encode('utf-8')
    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipeline.communicate(cyphertext)
    error_message = stderr.decode()
    if error_message != '':
        raise OpensslError(error_message)
    return stdout.decode()

def decrypt_b64(cyphertext, passphrase, cipher='aes-128-cbc'):

    pass_arg = 'pass:{0}'.format(passphrase)
    args = ['openssl', 'enc','-' + cipher,'-d','-pass', pass_arg,'-pbkdf2',]

    if isinstance(cyphertext, str):
        cyphertext = cyphertext.encode('utf-8')

    pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipeline.communicate(cyphertext)

    # si un message d'erreur est présent sur stderr, on arrête tout
    # attention, sur stderr on récupère des bytes(), donc on convertit
    error_message = stderr.decode()
    if error_message != '':
        raise OpensslError(error_message)
    # OK, openssl a envoyé le chiffré sur stdout, en base64.
    # On récupère des bytes, donc on en fait une chaine unicode
    return stdout.decode()
