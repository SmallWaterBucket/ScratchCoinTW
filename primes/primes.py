import secrets

def is_prime(n, k=20):
    if not isinstance(n, int):
        return False
    
    if n < 2:
        return False

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(k):
        a = secrets.randbelow(n - 4) + 2
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def generate_prime(digits):
    while True:
        n = secrets.randbelow(10**digits - 10**(digits - 1)) + 10**(digits - 1)
        n |= 1
        if is_prime(n):
            return n