import binascii
import sys
from fpylll import *
import codecs
import base64
from doc.aes import *
def lire_message_RML(nom_file):
    with open(nom_file) as f:
        message = f.read()
    return message

def recup_message(message):
    message = lire_message_RML(message)
    message = message.split("-----BEGIN RML PROGRAM -----\n")[1]
    message = message.split("-----END RML PROGRAM -----\n")[0]
    #message = message.replace("\n","")
    return message

def recup_h(message):
    message = lire_message_RML(message)
    message = message.split(' [SDBM] ')[1].split('\n')[0]
    return message

def SDBM(M,verbose=False):
    t = 0
    if(verbose):print("+----------------------------------+----+\n|                 X                | P  |\n+----------------------------------+----+")
    for i in range(len(M)):
        t = (65599 * t + ord(M[i])) % 2**128
        p = hex(t)[2:]
        if(verbose):print("| "+(len("0000000000000000000000000000004c")-len(p))*'0'+p+" | "+hex(ord(M[i]))[2:]+" |")
    hash=hex(t)
    return hash

def find_suffixe(h,verbose=False):
	a = 65599
	n = 25 
	G = IntegerMatrix(n+1,n+1)
	for i in range(0,n+1):
		if(i!=n):
			G[i,i] = 1
			G[i,n]=pow(a,n-(i+1))
		else:
			G[i,i] = pow(2,128)
	A = LLL.reduction(G)
	target = [64 for i in range(n)]
	target.append(h)
	if(verbose):print("target = {}".format(target))
	S = CVP.closest_vector(G,target)
	if(verbose):print("S      = {}".format(S))
	S = list(S)

	somme = sum([65599**(n-1-i) * S[i] for i in range(len(S)-1)]) + S[n] * pow(2,128)
	if(verbose):print("somme  = {}".format(somme%2**128))

	somme2 = sum([65599**(n-1-i) * S[i] for i in range(len(S)-2)]) % 2**128
	if(verbose):print("somme2 = {}".format(somme2%2**128))
	if(verbose):print(h-somme2)

	S[n-1]=h-somme2
	if(verbose):print("target = {}".format(target))
	if(verbose):print("new S  = {}".format(S))
	somme = sum([65599**(n-1-i) * S[i] for i in range(len(S)-1)]) % 2**128
	if(verbose):print("somme = {}".format(somme%2**128))
	if(verbose):print("h     = {}".format(h))

	suffixe = ""
	for i in S[:n]:
		suffixe = suffixe+chr(i)
	print(45*'_')
	print("Found suffixe : \""+suffixe+"\"")
	print(45*'_')
	return (suffixe)


if __name__ == "__main__":
    message = recup_message("doc/downloader_me_decode.txt")
    plaintext = message+"#"
    #plaintext = "Les sanglots longs\nDes violons\nDe l'automne\nBlessent mon coeur\nD'une langueur\nMonotone."
    #message = plaintext.encode('ascii')
    print(SDBM(plaintext))
    raw_h = SDBM(message)
    #raw_h = "5b2b3ae637b20f76e5dc5ad2933912c2"
    h  = int(raw_h,base=16)
    n = 25
    target = (int(raw_h,base=16) - (int(SDBM(plaintext),base=16) * 65599**(n))) % 2**128
    suffixe = find_suffixe(target)
    print(plaintext+suffixe)
    print("h                  : ", h)
    print("SBDM(m || suffixe) : ",int(SDBM(plaintext+suffixe),base=16))
