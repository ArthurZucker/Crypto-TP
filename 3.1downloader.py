# objectif : dechiffrer le programme RML de moi
# encryption TLCG
import binascii
import sys
from fpylll import *
import codecs
import base64

mul = 2**120
a = 47026247687942121848144207491837523525
mm = 2**128

def recup_message(message):
    message = lire_message_RML(message)
    message = message.split("-----BEGIN RML PROGRAM -----\n")[1]
    message = message.split("-----END RML PROGRAM -----\n")[0]
    print(message)
    return message.encode('utf-8')

def recup_message_e(message):
    message = lire_message_RML(message)
    message = message.split("-----BEGIN ENCRYPTED RML PROGRAM -----\n")[1]
    message = message.split("-----END ENCRYPTED RML PROGRAM -----\n")[0]
    print(message)
    message = message.replace("\n","")
    return message.encode('utf-8')


def lire_message_RML(nom_file):
    with open(nom_file) as f:
        message = f.read()
    return message

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def decode(cypher,root):
    plain = ""
    p2 = b""
    seed = root

    for i in range(0,len(cypher),2) : 
        temp = int(seed[2:4],base=16)^int(cypher[i:i+2],base=16)
        print(chr(temp)    )   
        p2+=int_to_bytes(temp)
        plain+=hex(temp)[2:]
        seed = (((int(seed,base=16))*a) % mm)
        seed = hex(seed)
        while(len((seed))<(128/4)+2):
            seed = str(seed[:2])+'0'+str(seed[2:])
    print(p2.decode())  
    return p2.decode()


def find_seed(message,plain):
    p = [message[i:i+2] for i in range(0,len(message),2)]
    c = [plain[i:i+2] for i in range(0,len(plain),2)]
    z = []
    z = [(int(i,base=16)^int(j,base=16))*mul for (i,j) in list(zip(p,c))]
    # 2. Compute vector
    n = 25 # nombre de bits qu'on utilise
    # 3. Créer la base de l'espace euclidien
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
    return Y[0]

if __name__ == "__main__":
    if(len(sys.argv)>1):
        file  = (sys.argv[1])
    else:
        file = "doc/downloader_robot.txt"
    plain = recup_message(file)
    plain = plain[0:1000].hex()
    message = recup_message_e("doc/downloader_me.txt")
    message = message.decode().replace('\n',"")
    seed = find_seed(message,plain)
    plain = decode(message,seed)
    with open("doc/downloader_me_decode.txt",'w') as f:
        f.write("-----BEGIN RML PROGRAM -----\n")
        f.write(plain)
        f.write("\n-----END RML PROGRAM -----\n")