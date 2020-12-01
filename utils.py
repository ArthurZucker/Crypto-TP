from random import randrange, getrandbits

def xgcd(a, b):
    """return (g, x, y) such that a*x + b*y = g = gcd(a, b)"""
    x0, x1, y0, y1 = 0, 1, 1, 0
    while a != 0:
        (q, a), b = divmod(b, a), a
        y0, y1 = y1, y0 - q * y1
        x0, x1 = x1, x0 - q * x1
    return b, x0, y0

def modinv(a, b):
    """return x such that (x * a) % b == 1"""
    g, x, _ = xgcd(a, b)
    if g != 1:
        raise Exception('gcd(a, b) != 1')
    return x % b



def PrimeFactorization(p):
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

def is_prime(n, k=5):
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    # find r and s
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2
    # do k tests
    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow(a, r, n)
        if x != 1 and x != n-1:
            j = 1
            while j < s and x != n-1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
        return True

def generate_prime_candidate2(a,b):
    i = a
    while not is_prime(i):
        i+=1
    return i

def generate_prime_candidate(length):
    # generate random bits
    p = getrandbits(length)
    # apply a mask to set MSB and LSB to 1
    p |= (1 << length - 1) | 1
    return p

def generate_prime_number(length=2048):
    p = 4
    # keep generating while the primality test fail
    while not is_prime(p, 128):
        p = generate_prime_candidate(length)
    return p