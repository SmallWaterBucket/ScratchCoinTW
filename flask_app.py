from flask import Flask, render_template
import random

import random

app = Flask(__name__)

def is_prime(n, k=20):
    if n < 2:
        return False

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # write n-1 as d*2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 2)
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
        # force exactly n digits and odd
        n = random.randint(10**(digits-1), 10**digits - 1)
        n |= 1

        if is_prime(n):
            return n


@app.route("/<amount>,<length>")
def main(amount,length):
    primes = []
    for i in range(100):
        primes.append(str(generate_prime(int(length))))
    primes_text = str(','.join(primes))
    return render_template("main.html", primes = primes_text, amount = amount, length = length)