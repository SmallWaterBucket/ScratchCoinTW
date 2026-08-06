import secrets

from flask import Flask, render_template
from primes.primes import is_prime, generate_prime
import random

import random

app = Flask(__name__)


@app.route("/<amount>,<length>")
def main(amount,length):
    primes = []
    for i in range(100):
        primes.append(str(generate_prime(int(length))))
    primes_text = str(','.join(primes))
    return render_template("main.html", primes = primes_text, amount = amount, length = length)