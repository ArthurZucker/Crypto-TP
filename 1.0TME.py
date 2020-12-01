
from random import randrange, getrandbits
from utils import PrimeFactorization
from utils import modinv
from utils import xgcd
from utils import is_prime
from utils import generate_prime_candidate2
import sys
import re
from alive_progress import alive_bar

def findOrder(p,g):
    L1  = PrimeFactorization(p-1)
    q = p-1
    for i in L1:
        if(pow(g,(q//i),p) == 1):
            q = q//i
    return q

def ChineseRemainder(pairs):
    '''Retourne a tel que a == pairs[0] mod pairs[1] pour tout les élements de pairs
    et m la multiplication des modulo '''

    (a, m)=pairs[0]
    for (b,p) in pairs[1:]:
        k = ((b-a)*xgcd(m,p)[1])
        a = (a+m*k) % (m*p)
        m *= p
    return (a,m)

def groupe_cyclique2(a,b,q):
    ''' trouver g et p tels que
          - p est premier et a <= p < b,
          - le groupe cyclique engendré par g est d'ordre q modulo p (q est premier) '''
    lima = (a-1)//q
    limb = (b-1)//q
    print("Calcul de p ... ")
    #x = generate_prime_candidate2(lima,limb)
    x = randrange(lima, limb, 2)
    while(not is_prime(q*x + 1)):
        x = randrange(lima, limb,2)
        #x = generate_prime_candidate2(lima,limb)
    p = x*q + 1
    y = randrange(2,2000000000)
    temp = (p-1)//q
    print("Calcul de g ... ")
    while(pow(y,temp,p)==1):
        y = randrange(2,2000000000)
    p = x*q + 1
    g = pow(y,temp,p)
    return g,p

def TME1():
	a = int(input("a = "))
	b = int(input("b = "))
	n = int(input("n = "))
	ia = modinv(a,n)
	print(-b*ia)
	return

def TME2():
	a = int(input("a = "))
	b = int(input("b = "))
	q = int(input("q = "))
	g,p = groupe_cyclique2(a,b,q)
	print(g)
	print(p)
	return

def TME3():
    with open("pairs.txt",'r') as f:
        text = f.read()
    text = text.split('\n')
    pairs = []
    with alive_bar(len(text),"Reading file") as bar:
        for line in text:
            line = re.sub('\s+',' ',line)
            line = line.split(' ')
            ele = int(line[2]),int(line[4])
            pairs.append(ele)
            bar()
    print(ChineseRemainder(pairs)[0])

def TME4():
    p = int(input("p = "))
    g = int(input("g = "))
    print(findOrder(p,g))
    return

if __name__ == "__main__":
	if(len(sys.argv)>1):
		if(int(sys.argv[1])==1):
			TME1()
		elif(int(sys.argv[1])==2):
			TME2()
		elif(int(sys.argv[1])==3):
			TME3()
		elif(int(sys.argv[1])==4):
			TME4()
	else:
		print("Error not enought argument. Usage :python <TME=={1,2,3,4}>")


