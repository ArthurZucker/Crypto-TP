from hashlib import sha256, md5
import hashlib
import random
import base64
import sys
import math
from subprocess import Popen, PIPE, check_output
import os
import base64
import os
from alive_progress import alive_bar
import binascii
from binascii import hexlify, unhexlify
# has to be in hexadecimal 
# has to start with the name of the operator 

# sha256 finger print with the starting 56 bits

# y1 = 

from random import randint 

import time
def f(x):
	m = sha256(x)
	y = m.hexdigest()
	return (y.encode())

def F(x0,x,nbit):
	m = sha256(x0+x+u0)
	y = m.hexdigest()
	return (y.encode()[:int(nbit/4)])


def collide(username,nbits):
	x0 = username.encode()
	h1 = f(x0)
	h2 = f(x0+f(x0))
	t=0
	x = h1
	y = h2
	tmax = pow(2,round(nbits/2)+1)
	with alive_bar(tmax) as bar:   # default setting
		while(h1[:int(nbits/4)] != h2[:int(nbits/4)] and t < tmax):
			t+=1
			x = h1
			y = h2
			h1 = f(x0+h1)
			h2 = f(x0+f(x0+h2))
			bar()
		return x0+x,x0+f(x0+y)

def brent2(x0,nbits):
	x0 = x0.encode()
	tmax = pow(2,round(nbits/2))
	t=0
	with alive_bar(tmax) as bar:
		# main phase: search successive powers of two
		power = lam = 1
		tortoise = x0
		hare = F(x0,x0,nbits)  # f(x0) is the element/node next to x0.
		while (hare[:int(nbits/4)] != tortoise[:int(nbits/4)] and t < tmax):
			if power == lam:  # time to start a new power of two?
				tortoise = hare
				power *= 2
				lam = 0
			t+=1
			hare =  F(x0,hare,nbits)
			lam += 1
			bar()
		if( t<tmax) : print("Cycle found")
		else : 
			print("Not found")
			exit(0)
		# Find the position of the first repetition of length λ
	t=0
	with alive_bar(tmax) as bar:
		tortoise = hare = x0
		for i in range(lam):
		# range(lam) produces a list with the values 0, 1, ... , lam-1
			hare = F(x0,hare,nbits)
		# The distance between the hare and tortoise is now λ.

		# Next, the hare and tortoise move at same speed until they agree
		mu = 0
		while (hare[:int(nbits/4)] != tortoise[:int(nbits/4)] and t < tmax):
			h2 = hare
			h1 = tortoise
			tortoise = F(x0,tortoise,nbits)
			hare = F(x0,hare,nbits)
			mu += 1
			t+=1
			bar()
 
	return lam, mu,x0+h1,x0+h2
u0 = b"hqlidsuhvbipsud"
if __name__ == "__main__":
	if(len(sys.argv)>2):
		user = sys.argv[1]
		nb   = int(sys.argv[2])
		_,_,key1,key2 = brent2(user,nb)
		print("Key 1 :"+str(key1.decode()))
		print("Key 2 :"+str(key2.decode()))
		
		print("sha(K1)      = "+str(f(key1+u0).decode()))
		print("sha(K2)      = "+str(f(key2+u0).decode()))
		print("Hexa1 : "+str((key1+u0).hex()))
		print("Hexa2 : "+str((key2+u0).hex()))
		print(len(key1))
		
