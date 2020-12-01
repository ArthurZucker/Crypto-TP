""" RSA KEYGEN """
from utils import generate_prime_number
from utils import modinv
from doc.pkcs1 import key_length
from doc.pkcs1 import *
from decimal import *
import sys


def lrack(n, k=3):
    """Racine kième entière d'un nb entier n de taille quelconque
       Génère une exception "ValueError" si n est négatif et k paire.
    """
    # initialisation du signe et traitement des  cas particuliers
    signe = +1
    if n < 2:
        if n < 0:
            if k % 2 == 0:
                raise ValueError("Erreur: racine paire d'un nombre négatif")
            else:
                # le calcul sera fait avec n>0 et on corrigera à la fin
                signe, n = -1, abs(n)
        else:
            return n  # ici n = 0 ou 1
    # trouve une valeur approchée de la racine (important pour les grds nb)
    rac1, i = n, 0  # i = compteur du nb de positions binaires utilisées
    while rac1 != 0:
        rac1 >>= 1
        i += 1
    rac1 = 1 << (i // k)
    # calcul de la racine en partant de la racine approchée rac1
    km1 = k - 1  # précalcul pour gagner du temps
    delta = n
    while True:
        rac2 = (km1 * rac1 + n // (rac1 ** km1)) // k
        if delta <= 1 and rac2 >= rac1:
            if signe > 0:
                return rac1
            return -rac1
        delta = abs(rac2 - rac1)  # on garde pour la prochaine boucle
        rac1 = rac2


def fake_sign(time="2020-11-05 10:59 UTC"):
    m = "PPTI SERVER ACCESS ON {}".format(time)
    MODULU = '00:ed:6b:8f:06:d5:b0:30:d2:47:e9:79:94:dd:1d:04:f3:01:69:81:db:de:88:e5:b8:f7:99:a3:08:17:ce:8f:70:97:c6:e8:a0:ba:5f:75:79:eb:a7:46:e7:7d:1b:d3:62:7d:01:ca:b7:93:d1:18:57:10:a9:c4:d8:82:23:10:47:1b:b6:01:26:f9:5b:fc:0d:ac:38:ee:26:c4:fb:67:42:d3:9a:c4:9f:0e:82:8e:4c:da:f4:2f:49:1b:10:cc:8e:dd:84:74:af:88:e6:ed:31:a5:f7:de:20:b7:84:26:0a:8a:70:af:6e:02:06:60:64:91:a3:2b:2b:a3:d6:cc:50:65:c3:18:35:a9:0b:b9:f3:37:79:62:2c:84:00:b4:a4:6c:4a:24:7d:6a:eb:f0:22:35:86:13:53:cb:9c:ed:94:80:27:70:66:33:94:43:62:bf:6f:82:37:30:dc:7d:9f:6e:5c:2b:52:a8:83:59:fc:fd:18:2d:bd:1d:75:30:09:03:0a:64:88:aa:16:0d:02:1c:71:5e:35:06:5d:54:2c:0f:6f:62:ef:5f:d1:fd:02:d4:f8:0e:ce:f6:af:2a:bf:69:5c:bf:df:ae:2f:e7:69:03:4e:f2:84:9c:9a:92:d0:10:97:0a:37:39:c0:f3:7e:fb:71:af:df:16:ab:da:4d'
    n = int(MODULU.replace(':', ''), base=16)
    k = key_length(n)
    # openssl rsa -pubin -inform PEM -text -noout < ppti-key.pem
    # objective : sign message such that when verifying with public-key
    # the signature is certified
    e = 3
    # here the modified version is used
    EM = emsa_pkcs1_encode(m, k)
    # the encoding is made such that when verifying, we will find the hash of our chain at the good spot!
    # compute the 3rd root of the encoded message
    Sign = lrack(os2ip(EM))
    print("Signature of your message   : {}".format(Sign))
    # in order to check, H(root^3) has to be = H(time)
    signed_chaine = i2osp(pow(Sign, e), k)
    print("Created sign hash           : {}".format(emsa_pkcs1_decode(signed_chaine, k).hex()))
    print("Message hash                : {}".format(sha256(m.encode()).digest().hex()))


if __name__ == "__main__":
    if(len(sys.argv) > 1):
        fake_sign(sys.argv[1])
    else:
        fake_sign()

# Extract n using openssl
# Compute square root of the message

# in order to sign, you need the private key? n = private key, d will be small, mod d won't change anything
