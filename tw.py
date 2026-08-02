import scratchattach as sa
import threading,MySQLdb,time
from datetime import datetime
from time import strftime
from random import randint
from dataclasses import dataclass
from functools import wraps

path = "/home/ubuntu/password.txt"


#session = sa.login_by_id(str(open('sid','r').read()).replace('\n',''), username="SAMURAI228")
cloud = sa.get_tw_cloud("1365548096")
client = cloud.requests()
verificators = {}
project = sa.get_project("1365548096")

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
    for loop_comment in comments:
        if loop_comment.author_name.lower() == username.lower():
            comment = loop_comment
            break

    if comment:
        comment = comment.content
        prime1 = int(prime1)
        prime2 = int(prime2)
        product = prime1 * prime2
        if int(product) == int(comment):
            expires_at = int(time.time()) + 10 * 60 #adds ten minures
            verificators[username] = Verificator(int(next_product), expires_at)
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
    current_product = prime1 * prime2

    if verificator.expires_at < int(time.time()):
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

@client.request
@verified_request
def test(username, text): #username, prime1, prime2, next_product should always be present to be able to authenticate
    return str(text) + str(username)


def get_time():
    return str(datetime.now().strftime("%B %d, %Y  %H:%M:%S"))
    


@client.request
def get_balance(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT balance from balances where username = %s;",(username,))
    balance = cursor.fetchall()
    if not balance or len(balance) == 0:
        create_user(username)
    return balance



def create_user(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO balances (username, balance, read_notifications, accepted) values (%s, 100,0,1);", (username,))
    db.commit()

@client.event
def on_ready():
    print("Request handler is running")


def get_db():
    password = open(path,"r").read().strip()
    db = MySQLdb.connect(
        host="localhost",
        user="scratch",
        passwd=password,
        database="scratch"
    )
    return db

client.start(thread=True) # thread=True is an optional argument. It makes the cloud requests handler run in a thread
