# BAKA meet in the middle + maléabilité de RSA
# use RFID tags 
# Every system has a RSA key Pair
# badges have ---OUI   --- containing serial number on 32 bits + secret key of a chip 
# locks  have ---MOUAIS--- containing public key + linked to server

# OUI + MOUAIS => chaine de K de 48 random bits
# => Encrypt(K,public_key) => OUI => RSA decrypt sends (n°serie,HMAC(K,n°serie)) => MOUAIS


##### We want to send and HMAC as if we were 000000 
##### Thus we want the MOUAIS to decrypt our message, and find that HMAC(K,0000000) is correct how?
##### well, K^d^e = 1 %N. Thus, HMAC(K,OOOOO)^d = ????
# RSA : m->int => m**e%N
# Exemple :  K = 0x554433221100.

# MOUAIS >>> OUI :

#       1ade43cb907946668eaddbbafc6cde1a0d7b651526c235041334fd9dee126afa
#       374a13aa53f97bb1d57cdff96d20c6588f439f4397d208e3ed73c205aa29a830
#       228c5965bfda8d122bd9e9c46abb9a98ae07bb8bfee66a25806df6756ba55871
#       9ab158202751a4b11694029939558f065c4481607e89138cc9e595937a999675

# OUI >>> MOUAIS :

#       00000000a90710ec6f1fea02e57ded332134305a777a93f43f34a7583a615ef0dda73094
#       ^^^^^^^^||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#        serial        HMAC-SHA256(0x554433221100, 0x00000000)

# MOUAIS >>> OUI :

#       OK



# clé = OUI
# serrure = MOUAIS
# tout le dispositifs à une paire de clé RSA
# Chaque OUI contient un numéro de série (32bits) + clef secrète
# MOUAIS contiennent la clef publique
# OUI contact avec MOUAIS => MOUAIS génère une chaine K de 48 bits aléatoire, puis la chiffre avec la clef publique et la transmet au OUI.
# OUI effectue le déchiffrement RSA, récupère K, puis renvoie la paire (numéro de série, HMAC(K, numéro de série)) au MOUAIS.
# Le MOUAIS vérifie si MAC est correct et interroge le serveur de permission pour déterminer si le OUI qui porte ce numéro de série est autorisé à ouvrir la porte

# OUI portant le numéro 0 (il a toujours le droit d'ouvrir toutes les portes).

# p et q => large primes 24 bits
# chiffrage de k : k**e % N
# Clé publique du système

# goal : récupérer K en déchiffrant c=k**e%N mais on a besoin de d pour dechiffrer k = c**d%N
# trouver diviseur de N => trouver p et q => calculer d
# p et q large primes
# n = p.q et phi(n)=(p-1)(q-1)
# 1<e<phi(n), gcd(e,phi(n))=1
# d est l'inverse modulaire de e dans phi(n). 1<d<phi(n) => e.d=1[phi(n)]

from string import ascii_letters
from random import SystemRandom
from doc.pkcs1 import *
from utils import *
import sys
from alive_progress import alive_bar
import pickle

import multiprocessing as mp
import hashlib
import hmac
from utils import *


def create_dictionnaire(e,N):
    D = {}
    with alive_bar(2**24) as bar:
        for i in range(1,2**24):
            x = pow(i,e,N)
            D[x] = i
            bar()
    with open('obj/dictionnaire_baka.pkl', 'wb') as f:
        pickle.dump(D, f, pickle.HIGHEST_PROTOCOL)
    return D

def read_dictionnaire(file_name):
    with open('obj/' + file_name + '.pkl', 'rb') as f:
        return pickle.load(f)

def format(K,serial):
    K = K.to_bytes(6,"big")
    serial = serial.to_bytes(4,"big")
    return K,serial



#D = create_dictionnaire(e,N)
D = read_dictionnaire("dictionnaire_baka")

e = 0x10001 #e=65537 prime, Fermat primes e = 2**16 + 1
N = 0x1ea982ba8f01d5e03163b0409a554484b8e145af768a8d3e66b84c9723d8604a33bd7c52033def81adfaf49beaa4f0f2b3b92370efb88f07665c5c35afdfd94752eacc4cf24ff3b96954ff391abaf39108df0cf11c26567ac2aa408143038ed11d53172667b95637a7cd3d6bc8972e6a4d7a503730db2af935d3baf8d5a5465d
D = create_dictionnaire(e,N)
D = read_dictionnaire("dictionnaire_baka")

def work_log(workload):
    idx , data = workload[0],workload[1]
    
    ciphertext,e,N,n_bit = data
    
    start = int(((2**int(n_bit))*idx)/mp.cpu_count())
    if(start==0):start=1
    end   =int(((2**int(n_bit))*(idx+1))/mp.cpu_count())
    with alive_bar(2*(end - start +1)) as bar:
        tab = []
        tab_x = {}
        prod = 1
        # calcul du porduit des 2^i à 2^i+1
        for k in range(start,end+1):
            x = pow(k,e,N)
            tab_x[k] = x
            prod = (prod *x) %N
            tab.append(prod)
            bar()
        X = modinv(prod,N)
        # X = inv(a0,a1,...,ap-1)
        # calcul de a0^-1, a1^-1,...,ap^-1 en utilisant 2^i+1 à 2^i
        cpt = len(tab)
        for j in range(end,start,-1):
            #xj = pow(j,e,N) 
            xj = tab_x[j]                 # d
            # inv_x = modinv(x,N)
            inv_xj = X*tab[cpt-2] %N    # X * abc
            cpt-=1
            X = (X*xj) %N  # X<-X*d
            y = ciphertext * inv_xj % N
            if(y in D):
                i = D[y]
                print("Value found!!!!!!")
                print(i,j)
                return (i,j)
            bar()
    return("Not found")

 


def get_result(result):
    global results
    results.append(result)




if __name__ == "__main__":
    if(len(sys.argv)>1):
        Kchiffre = int(sys.argv[1])
        print("Number of cpu : ", mp.cpu_count())
        nbits = 24
        work = [[i, [Kchiffre,e,N,(nbits)]] for i in range(mp.cpu_count())]
        results = []
        pool = mp.Pool(mp.cpu_count())
        for i in range(0, len(work)):
            pool.apply_async(work_log, args=(work[i],), callback=get_result)
        pool.close()
        pool.join()
        print("Multiple values were found : ")
        print(results)
        for a in results:
            if(a!="Not found"):
                i,j = a
                print("i = {} \nj = {} ".format(i,j))
                print("K trouvé       = {}".format(i*j%N))
                K2 = i*j
                K,serial = format(K2,0)
                print("K hex format   = {}".format(K.hex()))
                print("num série      = {}".format(serial.hex()))
                HM = hmac.new(
                key = K,
                msg = serial,
                digestmod = hashlib.sha256).hexdigest()

                answer = str(serial.hex()) + HM
                print("Possible key : {}".format(answer))
                break
        

        

		

