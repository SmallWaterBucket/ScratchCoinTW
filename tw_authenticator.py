import scratchattach as sa
import threading ,time
from datetime import datetime
from time import strftime
from random import randint
from dataclasses import dataclass
from functools import wraps
from primes.primes import is_prime, generate_prime

cloud = sa.get_tw_cloud("1365548096") # main project that sends all the requests
client = cloud.requests()
verificators = {}
project = sa.get_project("1366081158") # project to post verification codes in

@dataclass
class Verificator:
    next_product: int
    expires_at: int

@client.request
def ping(): #called when client receives request
    return "pong" #sends back 'pong' to the Scratch project

@client.request
def authenticate(username, prime1, prime2, next_product):
    comments = project.comments(limit=100)
    comment = ""
    for loop_comment in comments: # finds the laters comment from a user
        if loop_comment.author_name.lower() == username.lower():
            comment = loop_comment
            break
    if comment:
        comment = comment.content
        prime1 = int(prime1)
        prime2 = int(prime2)
        if not is_prime(prime1) or not is_prime(prime2): # checks if the primes sent by the user are actually prime
            print(f"[{get_time()}] User \"{username}\" tried bypassing securty measures in function \"authenticate\".")
            return "Good try, but it is already fixed."
        product = prime1 * prime2 # multiplies primes sent by the user
        if int(product) == int(comment): # checks the product
            expires_at = int(time.time()) + 10 * 60 #adds ten minures
            verificators[username] = Verificator(int(next_product), expires_at) # adds a verificator item
            print(f"[{get_time()}] Authenticated user {username}")
            return "Authenticated"
    print(f"[{get_time()}] Failed to authenticate user {username}")
    return "Failed"

def verified_request(func):
    @wraps(func)
    def wrapper(username, prime1, prime2, next_product, *args, **kwargs):
        function_name = func.__name__
        status = verify_user(username, prime1, prime2, next_product,function_name)
        if status != "Verified":
            return status
        return func(username, *args, **kwargs)
    return wrapper
    
def verify_user(username,prime1,prime2,next_product, function_name):
    verificator = verificators.get(username)

    if verificator is None:
        print(f"User \"{username}\" tried executing \"{function_name}\" without authentication")
        return "Not authenticated"

    prime1 = int(prime1)
    prime2 = int(prime2)
    if not is_prime(prime1) or not is_prime(prime2):
        print(f"[{get_time()}] User \"{username}\" tried bypassing securty measures in function \"{function_name}\".")
        return "Good try, but it is already fixed."
    current_product = prime1 * prime2

    if verificator.expires_at < int(time.time()): # checks whether the verificator had expired
        verificators.pop(username)
        print(f"[{get_time()}] Verificator for user {username} expired in function: \"{function_name}\"")
        return "Expired"
    if int(current_product) == int(verificator.next_product):
        expires_at = int(time.time()) + 10 * 60 #adds ten minures
        verificators[username] = Verificator(int(next_product), expires_at)
        print(f"[{get_time()}] Verified user \"{username}\" for function: \"{function_name}\"")
        return "Verified"
    else:
        print(f"[{get_time()}] Failed to verify user: \"{username}\" for function: \"{function_name}\"")
        return "Failed"


def get_time():
    return str(datetime.now().strftime("%B %d, %Y  %H:%M:%S"))



# Your requests
@client.request
@verified_request # include this if you want to check for the legitimacy of the sender of the request
def test(username, text):  # very simple example for how to use the verified requests
    return f"{str(username)} : {str(text)}"






@client.event
def on_ready():
    print("Request handler is running")

client.start(thread=True) # thread=True is an optional argument. It makes the cloud requests handler run in a thread
