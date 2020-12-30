# se servir des paires (messages ,tag) qu'on a dejà qui sont valides pour tarMAC avec la clef K
# on sait que SDBM(message) == h et que AES(K, h) == tag
from fpylll import *

def lire_message_RML(nom_file):
    with open(nom_file) as f:
        message = f.read()
    return message

def recup_message(message,source=0):
    if(source == 0):
        message = message.replace("-----BEGIN ENCRYPTED RML PROGRAM -----\n","")
        message = message.replace("-----END ENCRYPTED RML PROGRAM -----\n","")
    else:
        message = message.replace("-----BEGIN RML PROGRAM -----\n","")
        message = message.replace("-----END RML PROGRAM -----\n","")
    message = message.replace("# Encryption: [TLCG]\n", "")
    message = message.replace("# hash: [SDBM] a4ff56faca3017f54b91ed6dc6ac2d7a\n", "")
    message = message.replace("# MAC: [tarMAC, 17893 bytes] a9e0f3da89d2d2d38ceaed813e54be2e\n", "")
    message = message.replace("\n","")
    return message

def recup_h(texte,message,source=0):
    if(source == 0):
        temp = texte.replace("-----BEGIN ENCRYPTED RML PROGRAM -----\n","")
        temp = temp.replace("-----END ENCRYPTED RML PROGRAM -----\n","")
    else:
        temp = texte.replace("-----BEGIN RML PROGRAM -----\n","")
        temp = temp.replace("-----END RML PROGRAM -----\n","")
    temp = temp.replace("# Encryption: [TLCG]\n", "")
    temp = temp.replace("# MAC: [tarMAC, 17893 bytes] a9e0f3da89d2d2d38ceaed813e54be2e\n", "")
    temp = temp.replace("\n","")
    temp = temp.replace(message,"")
    temp = temp.replace("# hash: [SDBM] ","")
    return temp

def SDBM(M):
    hash = 0
    for i in range(1):
        hash = (65599 * hash + M[i]) % 2**128

texte = lire_message_RML("downloader_me.txt")
message = recup_message(texte,1)
print(message)
h = recup_h(texte,message,1)
print(h)
h = int(h,base=16)
print("h={}".format(h))

# h = "3920e5ec628cf585f4fca26cdd67b308"
# h = int(h,base=16)
# print("h={}".format(h))

a = 65599

n = 25 # doit être >=16

G = IntegerMatrix(n+1,n+1)
for i in range(0,n+1):
    if(i!=n):
        G[i,i] = 1
        G[i,n]=pow(a,n-(i+1))
    else:
        G[i,i] = pow(2,128)

print(G)
A = LLL.reduction(G)

target = [64 for i in range(n)]
target.append(h)
print("target={}".format(target))
S = CVP.closest_vector(G,target)
print("S={}".format(S))
S = list(S)

somme = sum([65599**(n-1-i) * S[i] for i in range(len(S)-1)]) + S[n] * pow(2,128)
print("somme={}".format(somme%2**128))

somme2 = sum([65599**(n-1-i) * S[i] for i in range(len(S)-2)]) % 2**128
print("somme2={}".format(somme2%2**128))
print(h-somme2)

S[n-1]=h-somme2
print("target={}".format(target))
print("S={}".format(S))
somme = sum([65599**(n-1-i) * S[i] for i in range(len(S)-1)]) % 2**128
print("somme={}".format(somme%2**128))
print("h={}".format(h))

suffixe = ""
for i in S[:n-1]:
    suffixe = suffixe+chr(i)
print(suffixe)
# on a trouvé un suffixe mtn il faut concatener avec notre message et voir si ils ont le meme hashé h
