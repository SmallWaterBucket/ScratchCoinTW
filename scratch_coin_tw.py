import scratchattach as sa
import threading ,time
from datetime import datetime
from time import strftime
from random import randint
from dataclasses import dataclass
from functools import wraps
from primes.primes import is_prime, generate_prime
import MySQLdb

cloud = sa.get_tw_cloud("1385838253") # main project that sends all the requests
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
        #print(f"DEBUG:\nprime1: {prime1},\nprime2: {prime2},\ncurrent_product: {product},\nverificator.next_product: {comment},\nnext_product: {next_product}")
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

    #print(f"DEBUG:\nprime1: {prime1},\nprime2: {prime2},\ncurrent_product: {current_product},\nverificator.next_product: {verificator.next_product},\nnext_product: {next_product}")

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
        return f"Failed|Failed to verify user: \"{username}\" for function: \"{function_name}\".|Something went wrong, please report it in the comments.|After that restart the project."


def get_time():
    return str(datetime.now().strftime("%B %d, %Y  %H:%M:%S"))

#==========================================================================================================================

password_path = "/home/ubuntu/password.txt"


def get_db():
    password = open(password_path,"r").read().strip()
    db = MySQLdb.connect(
        host="localhost",
        user="scratch",
        passwd=password,
        database="scratch"
    )
    return db

def add_notification(username, notification):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO notifications (username, message) values (%s, %s);",(username,notification,)) # DB format: (id, username, balance, read_notifications, accepted)
    db.commit()

def set_balance(username, amount):
    add_new_user_if_non_existant(username)

    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE balances set balance = %s where username = %s;",(amount,username)) # DB format: (id, username, balance, read_notifications, accepted)
    db.commit()

def add_balance(username, amount):
    amount = int(amount)
    set_balance(username, get_balance(username) + amount)

def is_number(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def add_new_user_if_non_existant(username):
    username = username.lower()
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * from balances where username = %s", (username,))
    response = cursor.fetchone()
    if not response:
        cursor.execute("INSERT INTO balances (username, balance, read_notifications, accepted) values (%s, 100,0,0);", (username,))
        db.commit()

def get_notifications(username,date):
    username = username.lower()
    return "Not implemented yet."

def give(username, recepient, amount):
    if int(get_balance(username)) < amount:
        return f"Failed"

    if amount < 0:
        return f"Failed"

    add_balance(username, 0 - amount)

    add_balance(recepient, amount)

    return "Success"


def agreed_to_terms(username):
    add_new_user_if_non_existant(username)

    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT accepted FROM balances WHERE username = %s;",(username,)) # DB format: (id, username, balance, read_notifications, accepted)
    response = cursor.fetchone()
    return str(response[0])
    

# Your requests
@client.request
@verified_request # include this if you want to check for the legitimacy of the sender of the request
def test(username, text):  # very simple example for how to use the verified requests
    return f"{str(username)} : {str(text)}"

@client.request
@verified_request # include this if you want to check for the legitimacy of the sender of the request
def test2(username, text):  # very simple example for how to use the verified requests
    return f"test: {str(username)} : {str(text)}"

@client.request
def get_balance_request(username):
    print(f"[{get_time()}] Get balance was requested for user \"{username}\"")
    return str(get_balance(username))

def get_balance(username):
    add_new_user_if_non_existant(username)

    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT balance FROM balances WHERE username = %s;",(username,)) # DB format: (id, username, balance, read_notifications, accepted)
    response = cursor.fetchone()

    if not response:
        return -1

    return int(response[0])

@client.request
@verified_request
def give_request(username, recepient, amount, message):
    if not is_number(amount):
        return "Please enter only numbers"

    if agreed_to_terms(username) == "0":
        return "You must first agree to the Terms of Use until doing anything else."

    amount = int(amount)

    if int(get_balance(username)) < amount:
        return f"You can't give {amount} SC to {recepient} as you don't have them."

    if amount < 0:
        return "Cannot give someone negative SC, that's called stealing."

    status = give(username, recepient, amount)

    if status == "Failed":
        return f"Something went wrong :(|Failed to give \"{username}\" {amount} SC."

    add_notification(recepient, f"{username} has given you {amount} SC with the message: \"{message}\"")

    return f"Server:|Successfully gave {recepient} {amount} SC."

@client.request
def other_user_balance_request(username):
    return f"Get balance:|{username} has {get_balance(username)} SC."

@client.request
def agreed_to_terms_request(username):
    return agreed_to_terms(username)

@client.request
@verified_request
def accept_terms(username, apple):
    add_new_user_if_non_existant(username)
    
    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("update balances set accepted = 1 WHERE username = %s;",(username,)) # DB format: (id, username, balance, read_notifications, accepted)
    db.commit()

    cursor.execute("SELECT accepted FROM balances WHERE username = %s;",(username,)) # DB format: (id, username, balance, read_notifications, accepted)
    response = cursor.fetchone()[0]
    return str(response)

@client.request
def leaderboard(username):
    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username, balance FROM balances ORDER BY balance DESC LIMIT 10;") # DB format: (id, username, balance, read_notifications, accepted)
    ppl = cursor.fetchall()
    cursor.execute("SELECT COUNT(username) AS usernames from balances;")
    total = cursor.fetchone()[0]
    cursor.execute("""
    SELECT position
    FROM (
        SELECT username,
               ROW_NUMBER() OVER (ORDER BY balance DESC) AS position
        FROM balances
    ) AS leaderboard
    WHERE username = %s;
    """, (username.lower(),))

    position = cursor.fetchone()[0]

    return_str = f"Leaderboard:|You are {position} out of {total}|That is {str(((total - position + 1)/total * 100))}%|"

    i = 1
    for person, balance in ppl:
        return_str += f"{i})  {balance}{" " * (7 - len(str(balance)) - len(str(i)))}{person}|"
        i+=1

    return return_str

@client.request
def get_notifications(username):
    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT message FROM notifications WHERE username = %s;", (username,)) # DB format: (id, username, balance, read_notifications, accepted)
    notifications = cursor.fetchall()
    return_str = "Notifications:|"
    i = 1
    for notification in notifications:
        return_str+=f"{i}) {notification[0]}|"
        i+=1
    return return_str

@client.request
def read_notifications_question(username):
    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT read_notifications FROM balances WHERE username = %s;", (username,)) # DB format: (id, username, balance, read_notifications, accepted)
    read_notifications = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(message) AS messages FROM notifications WHERE username = %s;", (username,)) # DB format: (id, username, balance, read_notifications, accepted)
    count = cursor.fetchone()[0]
    return f"{read_notifications}|{count}"


@client.request
@verified_request
def read_notifications_announcment(username, number):
    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE balances SET read_notifications = %s where username = %s;", (number, username)) # DB format: (id, username, balance, read_notifications, accepted)
    db.commit()
    return "IGNORE"

@client.request
@verified_request
def add_charge(username, charge_who, amount, message):

    add_new_user_if_non_existant(username)
    add_new_user_if_non_existant(charge_who)

    if not is_number(amount):
        return "Error:|Please enter only numbers"
    
    if agreed_to_terms(username) == "0":
        return "Error:|You must first agree to the Terms of Use until doing anything else."
        
    username = username.lower()
    charge_who = charge_who.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO charges (sent_by, sent_to, amount,message) VALUES (%s,%s,%s,%s)",(username, charge_who, amount, message)) # DB format: (id, sent_by, sent_to, amount, message)
    db.commit()

    add_notification(charge_who,f"\"{username}\" charged you {amount}SC for {message}")

    return f"Success|Charged \"{username}\" {amount}SC"

@client.request
def get_charges(username):
    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, sent_by, amount, message from charges WHERE sent_to = %s",(username,)) # DB format: (id, sent_by, sent_to, amount, message)
    charges = cursor.fetchall()
    return_str = f"Press \"a\" to do any action:|"
    for id, sent_by, amount, message in charges:
        return_str+=f"ID: {id}; {sent_by} charged you {amount}SC for \"{message}\"|"
    if len(charges) == 0:
        return_str+="You haven't been charged yet.|After you are charged by a shop or another user, the charge will appear here."
    return return_str


def get_charge(charge_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, sent_by, amount, message from charges WHERE id = %s",(charge_id,)) # DB format: (id, sent_by, sent_to, amount, message)
    charge = cursor.fetchall()
    id, sent_by, amount, message = charge
    return_str = f"Pay this charge?|ID: {id},|Send SC to: {sent_by},|Amount: {amount},|Message: {message}"
    return return_str



@client.request
@verified_request
def accept_charge(username, charge_id):
    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT sent_by, amount, message from charges WHERE id = %s",(charge_id,)) # DB format: (id, sent_by, sent_to, amount, message)
    charge = cursor.fetchall()
    sent_by, amount, message = charge
    status = give(username,sent_by, amount)
    if status == "Success":
        add_notification(sent_by, f"\"{username}\" payed you {amount}SC for the charge \"{message}\".")
        cursor.execute("DELETE FROM charges WHERE id = %s",(charge_id,)) # DB format: (id, sent_by, sent_to, amount, message)
        return f"Success|Successfully payed the charge {charge_id}."
    else:
        return f"Failed|Failed to pay the charge {charge_id}.|If this continues hapenning and you are unsure why, ask me in the comments."


@client.request
@verified_request
def cancel_charge(username, charge_id):
    username = username.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT sent_by, amount, message from charges WHERE id = %s",(charge_id,)) # DB format: (id, sent_by, sent_to, amount, message)
    charge = cursor.fetchall()
    sent_by, amount, message = charge
    cursor.execute("DELETE FROM charges WHERE id = %s",(charge_id,)) # DB format: (id, sent_by, sent_to, amount, message)
    return f"Success|Successfully canceled the charge {charge_id}."


@client.event
def on_ready():
    print("Request handler is running")

client.start(thread=True) # thread=True is an optional argument. It makes the cloud requests handler run in a thread