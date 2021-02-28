from hashlib import sha256
import random as rdm

def rand_bin(n):
    b = ""
    for _ in range(n):
        b += str(rdm.randint(0,1))
    return b

def F(k, x, n):
    # k et x sont des str representant des binaires
    h = sha256( (k + x).encode() )
    return int(h.hexdigest()[:(n//2)//4], base=16) # on tronque a n//2 bits


def feistel(plain, key, n, nb_tr=4, verbose=False):

    # decoupage en quatre sous-clefs
    K = [key[0:16], key[16:32], key[32:48], key[48:64]]

    # decoupage du plain en deux
    L = plain[0:n//2]
    R = plain[n//2:n]

    # tours de feistel
    if nb_tr < 0 or nb_tr > 4:
        print("erreur, feistel de", nb_tr, "tours")
        return None

    for t in range(nb_tr):
        if verbose:
            print("| feistel tour", t+1)
        Kt = K[t]
        L, R = R, format( int(L, base=2) ^ F(Kt, R, n), 'b' ).zfill(n//2)

    return L + R


def antifeistel(cypher, key, n, nb_tr=4, verbose=False):

    # decoupage en quatre sous-clefs
    K = [key[0:16], key[16:32], key[32:48], key[48:64]]

    # decoupage du plain en deux
    L = cypher[0:n//2]
    R = cypher[n//2:n]

    # tours de feistel
    if nb_tr < 0 or nb_tr > 4:
        print("erreur, feistel de", nb_tr, "tours")
        return None

    for t in range(nb_tr):
        if verbose:
            print("| antifeistel tour", t+1)
        Kt = K[nb_tr-1 -t]
        R, L = L, format( int(R, base=2) ^ F(Kt, L, n), 'b' ).zfill(n//2)

    return L + R


# distingueurs
def distingueur_1tr(plain, cypher, n):
    return plain[n//2:n] == cypher[0:n//2]


def distingueur_2tr(plain1, plain2, cypher1, cypher2, n):
    if plain1[n//2:n] != plain2[n//2:n]:
        print("erreur, les deux messages clairs doivent avoir le meme R")
        return False
    else:
        return (int(cypher1[0:n//2], 2) ^ int(cypher2[0:n//2], 2)) \
             == (int(plain1[0:n//2], 2) ^ int(plain2[0:n//2], 2))


def distingueur_3tr(plain1, plain2, plain3, cypher1, cypher2, cypher3, n):
    if plain1[n//2:n] != plain2[n//2:n]:
        print("erreur, les deux messages clairs doivent avoir le meme R")
        return False
    elif cypher3[0:n//2] != cypher2[0:n//2] \
            and int(cypher3[n//2:n], 2) == int(cypher2[n//2:n], 2) \
                                         ^ int(plain1[0:n//2], 2) \
                                         ^ int(plain2[0:n//2], 2):
        print("erreur, le cypher 3 n'est pas de la bonne forme")
        return False
    else:
        return int(plain3[n//2:n], 2) == (int(cypher1[0:n//2], 2) \
                                        ^ int(cypher2[0:n//2], 2) \
                                        ^ int(plain1[n//2:n], 2) )



def find_key(truekey, n):

    L1 = rand_bin(n//2)
    L2 = rand_bin(n//2)
    R  = rand_bin(n//2)
    plain1 = L1 + R
    plain2 = L2 + R

    cypher1 = feistel(plain1, truekey, n, 4)
    cypher2 = feistel(plain2, truekey, n, 4)

    for i in range(2**16):
        k3 = format(i, "b").zfill(16)
        k3bis = k3

        # on annule un tour de feistel
        cypher1_prime = antifeistel(cypher1, k3bis, n, 1)
        cypher2_prime = antifeistel(cypher2, k3bis, n, 1)

        cypher3_prime = cypher2_prime[0:n//2] + format( int(cypher2_prime[n//2:n], 2) \
                                         ^ int(plain1[0:n//2], 2) \
                                         ^ int(plain2[0:n//2], 2), "b" ).zfill(n//2)

        cypher3 = feistel(cypher3_prime, k3bis, n, 1) # on ravance cypher3 d'un tour
        plain3 = antifeistel(cypher3, truekey, n, 4)

        #plain3 = feistel(plain3, k3bis, n, 1) # on annule aussi un tour
        #cypher3 = antifeistel(cypher3_prime, k3bis, n, 1)

        if distingueur_3tr(plain1, plain2, plain3, cypher1_prime, cypher2_prime, cypher3_prime, n):
            print(k3)
            print(k3bis)
            print(truekey[48:], "  (true)")
            print(truekey[:16], "  (debut true)")
            break


    for i in range(2**16):
        k2 = format(i, "b").zfill(16)
        k2bis = k2 + k3

        # on annule deux tours de feistel
        cypher1_prime = antifeistel(cypher1, k2bis, n, 2)
        cypher2_prime = antifeistel(cypher2, k2bis, n, 2)

        if distingueur_2tr(plain1, plain2, cypher1_prime, cypher2_prime, n):
            print(k2)
            break

    for i in range(2**16):
        k1 = format(i, "b").zfill(16)
        k1bis = k1 + k2 + k3

        # on annule trois tours
        cypher1_prime = antifeistel(cypher1, k1bis, n, 3)

        if distingueur_1tr(plain1, cypher1_prime, n):
            print(k1)
            break

    for i in range(2**16):
        k0 = format(i, "b").zfill(16)
        k0bis = k0 + k1 + k2 + k3

        # on annule les quatre tours
        cypher1_prime = antifeistel(cypher1, k0bis, n, 4)

        if plain1 == cypher1_prime:
            print(k0)
            break

    print(k0bis, "  (found)")
    print(truekey, "  (true)")
    print(k0bis == truekey)


if __name__=="__main__":
    #print(F("lala", "lolo", n))

    n = 128
    handle = rand_bin(n)
    key = rand_bin(64)
    """
    print("\ntest de feistel et antifeistel")
    print(handle, int(handle, 2), "  (plain)")

    f = feistel(handle, key, n)
    print(f, int(f, 2), "  (cypher)")

    ff = antifeistel(f, key, n)
    print(ff, int(ff, 2), "  (re-plain)")
    #"""

    """
    # test distingeurs
    print("\ntest des distingueurs")
    L1 = rand_bin(n//2)
    L2 = rand_bin(n//2)
    R  = rand_bin(n//2)

    # 1 tour
    plain = L1 + R
    cypher = feistel(plain, key, n, 1)
    print("-- 1tr", distingueur_1tr(plain, cypher, n))

    # 2 tours
    plain2 = L2 + R
    cypher1 = feistel(plain, key, n, 2)
    cypher2 = feistel(plain2, key, n, 2)
    print("-- 2tr", distingueur_2tr(plain, plain2, cypher1, cypher2, n))

    # 3 tours
    cypher1 = feistel(plain, key, n, 3)
    cypher2 = feistel(plain2, key, n, 3)
    cypher3 = cypher2[0:n//2] + format( int(cypher2[n//2:n], 2) \
                                         ^ int(plain[0:n//2], 2) \
                                         ^ int(plain2[0:n//2], 2), "b" ).zfill(n//2)
    plain3 = antifeistel(cypher3, key, n, 3)
    print("-- 3tr", distingueur_3tr(plain, plain2, plain3, cypher1, cypher2, cypher3, n))
    #"""

    find_key(key, n)
