# objectif : dechiffrer le programme RML de moi
# encryption TLCG
import binascii
from fpylll import *

def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

def lire_message_RML(nom_file):
    with open(nom_file) as f:
        message = f.read()
    return message

def convert_message_to_int(message):
    message = message.replace("-----BEGIN ENCRYPTED RML PROGRAM -----\n","")
    message = message.replace("-----END ENCRYPTED RML PROGRAM -----\n","")
    message = message.replace("# Encryption: [TLCG]\n", "")
    message = message.replace("# hash: [SDBM] a4ff56faca3017f54b91ed6dc6ac2d7a\n", "")
    message = message.replace("# MAC: [tarMAC, 17893 bytes] a9e0f3da89d2d2d38ceaed813e54be2e\n", "")
    message = message.replace("\n","")
    return message



# 1. Retrive 40 bits of the file
plaintext = lire_message_RML("downloader_robot1.txt")
plaintext = plaintext.replace("-----BEGIN RML PROGRAM -----\n","")
print("Plain text  : \n\n",plaintext[0:1000])

# plaintext = "Les sanglots longs\nDes violons\nDe l'automne\nBlessent mon coeur\nD'une langueur\nMonotone."
plain = plaintext.encode('utf-8').hex()

plain = plain[0:1000]
print(plain)

message = lire_message_RML("downloader_me.txt")
message = convert_message_to_int(message)
message = message.lower()
print(message)

# message = "3d8a065b3ccba48c74c53c4b9d7dbbbcc1b3ba9c8ae689687a31517b3bd79814b133a3b6671124e8bae01efba766c3ebd9f6908e65000995a99a873cd085bfeada8db8e6565539b1ffb3f703f386b41c2d37f2bb5b351c"
# print(message)

mul = 2**120
def xor(a,b):
	return hex(int(a, 16) ^ int(b, 16))

p = [message[i:i+2] for i in range(0,len(message),2)]
c = [plain[i:i+2] for i in range(0,len(plain),2)]
z = []

def XORfunction(input_1, input_2):
    input_1 = (binascii.unhexlify(input_1))
    input_2 = (binascii.unhexlify(input_2))
    return binascii.hexlify(bytes(
        a ^ b for a, b in zip(input_1, input_2)))

z = [int(XORfunction(i,j),base=16)*mul for (i,j) in list(zip(p,c))]
# 2. Compute vector
n = 20 # nombre de bits qu'onutilise
a = 47026247687942121848144207491837523525
# 3. Créer la base de l'espace euclidien
mm = 2**128
M = IntegerMatrix(n,n)
M[0,0] = 1
for i in range(1,n):
	M[i,i] = mm
	M[0,i] = pow(a,i)

A = LLL.reduction(M)

x = CVP.closest_vector(A,z[:n])
Y = [hex(x[i]) for i in range(0,len(x))]
print(Y)
print("Seed = {}".format(Y[0][2:4]))
seed = Y[0]

import base64

def decode(cypher,root):
    plain = ""
    seed = root
    for i in range(0,len(cypher),2) : #len(cypher)
        seed = seed[2:]
        #print("seed = {}".format(seed))
        temp = xor(seed[0:2],cypher[i:i+2])
        #print("Xor results : {}|".format(temp))
        #print(chr(int(temp[2:], 16)))
        #print("encoded to ascii : ",temp.encode("ascii"))
        plain+=chr(int(temp[2:], 16))
        seed = (((int(seed,16))*a) % mm)
        seed = hex(seed)
        if(len(seed)<(128/4)+2):
            seed = seed[:2]+'0'+seed[2:]
            #print("new seed",seed)
        #print("result : ",plain)
    return plain

plain = decode(message,seed)

with open("downloader_me_decode.txt",'w') as f:
    f.write(plain)
