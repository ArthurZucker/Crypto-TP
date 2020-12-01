#! /usr/bin/python

from utils import xgcd

def ChineseRemainder(pairs):
    '''Retourne a tel que a == pairs[0] mod pairs[1] pour tout les élements de pairs
    et m la multiplication des modulo '''

    (a, m)=pairs[0]
    for (b,p) in pairs[1:]:
        k = ((b-a)*xgcd(m,p)[1])
        a = (a+m*k) % (m*p)
        m *= p
    return (a,m)


def CountOccurences(primeFactors):
    """Count occurances of each prime factor"""
    return [[x, primeFactors.count(x)] for x in set(primeFactors)]


def factorMultiplicity(p):
    """Find all prime factors of the number p"""
    d, primeFactors = 2, []
    while d*d <= p:
        while (p % d) == 0:
            primeFactors.append(d)
            p //= d
        d += 1
    if p > 1:
       primeFactors.append(p)
    return primeFactors

def PohligHellmanModP(beta, alpha, p, verbose=True):
    ''' Solves discrete log problem alpha^x = beta mod p, and returns x,
     using Pohlig-Hellman reduction to prime factors of p-1. 
    '''
    congruenceList=[getXModP(beta, alpha, p, q, r)
                    for (q, r) in CountOccurences(factorMultiplicity(p-1))]
    (x,m)=ChineseRemainder(congruenceList)
    if verbose: print("Given", beta,"=", alpha,"^x mod",p, "\n","x=", x)
    assert pow(alpha, x, p) == beta % p
    return x

def discreteLogModP(a, b, p):  # brute force version
    '''Returns x so pow(a, x, p) is b mod p, or None if no solution.'''
    a_x = 1
    b %= p
    for x in range(p-1):
        if a_x == b: return x
        a_x = a_x * a % p
    return None

def getXModP(beta, alpha, p, q, r):
    ''' return (x, q**r) with (p-1)/q**r = k, 0 <= x < q**r, os
    beta^(x*k) = alpha^k mod p
    '''
    oDiv = (p-1)//q # first divided group order
    bCurrent=beta
    xFinal=0  # returns x=x0+x1q+x2q^2+...+xiq^i with 0<=xi<q-1
    alphaRaisedModp=pow(int(alpha), int(oDiv), p)
    qPow = 1
    alphaInv = xgcd(alpha, p)[1]
    for i in range(0,r):
        betaRaisedModp=pow(int(bCurrent), int(oDiv), p)
        xCurrent = discreteLogModP(alphaRaisedModp, betaRaisedModp, p)
        xFinal += xCurrent*qPow
        #now we calculate the next beta, power of q, order factor
        bCurrent = bCurrent*pow(alphaInv, xCurrent*qPow, p) % p
        qPow *= q
        oDiv //= q
    return (xFinal,qPow)

def PohligHellman(beta, alpha, order, verbose=True):
    ''' Solves discrete log problem alpha^x = beta in group of given order,
     and returns x, using Pohlig-Hellman reduction to prime factors of order. 
    '''
    print ('PohligHellman for group elements not written')

def discreteLog(a, b, bound):  # brute force version for group elements a, b
    '''Returns x so a**x = b for x < bound, or None if no solution.'''
    a_x = 1
    for x in range(bound):
        if a_x == b: return x
        a_x *= a
    return None

def getX(beta, alpha, order, q, r):
    ''' return (x, q**r) with order/q**r = k, 0 <= x < q**r, so
    beta**(x*k) = alpha**k, alpha and beta in group of given order.
    '''
    print ('getX for group elements not written')

def testGenModP(a, p):  # want generator base for discrete log (and Pohlig-Hellman)
    '''True if a generates Fp* for prime p.'''
    b = a
    for i in range(1, p-1):
        if b == 1:
            return False
        b = b*a % p
    assert b == 1
    return True

if __name__ == '__main__':
	PohligHellmanModP(27, 10001, (2**61-1))
##    PohligHellmanModP(95, 37, 2017)
##    PohligHellmanModP(19, 95, 3001)
##    PohligHellmanModP(7531, 6, 8101)