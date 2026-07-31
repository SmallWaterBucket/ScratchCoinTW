import scratchattach as sa
import threading,MySQLdb,time
from time import strftime
from random import randint
from dataclasses import dataclass

balancespath = "/home/ubuntu/scratch/info/balances.txt"
chargespath = "/home/ubuntu/scratch/info/charges.txt"
blockedpath = "/home/ubuntu/scratch/info/blocked.txt"
reports = "/home/ubuntu/scratch/info/reports.txt"
remixes = "/home/ubuntu/scratch/info/remixes.txt"
notifications = "/home/ubuntu/scratch/info/notifications.txt"
logs = "/home/ubuntu/scratch/info/logs.txt"
allowsend = "/home/ubuntu/scratch/info/allowsend.txt"

path = "/home/ubuntu/password.txt"


#session = sa.login_by_id(str(open('sid','r').read()).replace('\n',''), username="SAMURAI228")
cloud = sa.get_tw_cloud("1365548096")
client = cloud.requests()
verificators = {
"a":"b"
}
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
        print(prime1)
        print(prime2)
        prime1 = int(prime1)
        prime2 = int(prime2)
        product = prime1 * prime2
        if product == comment:
            expires_at = int(time.time()) + 10 * 60 #adds ten minures
            verificators[username] = Verificator(next_product, expires_at)
            return "Authenticated"

    return "Failed"

@client.request
def test(username, prime1, prime2, next_product):
    verify_user(username, prime1, prime2, next_product)

def verify_user(username,prime1,prime2,next_product):
    verificator = verificators[username]
    prime1 = int(prime1)
    prime2 = int(prime2)
    current_product = prime1 * prime2
    if verificator.expires_at > time.time():
        verificators.remove()
        return "Expired"
    if current_product == verificator.next_product:
        expires_at = int(time.time()) + 10 * 60 #adds ten minures
        verificators[username] = Verificator(next_product, expires_at)
        return "Authenticated"
    else:
        return "Failed"

    
    


@client.request
def get_balance(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT balance from balances where username = %s;",(username,))
    balance = cursor.fetchall()
    if not cursor.fetchall() or len(cursor.fetchall()) == 0:
        create_user(username)
    return balance



def create_user(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO balances (username, balance, read_notifications, accepted) values (%s, 100,0,1);", (username,))

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
