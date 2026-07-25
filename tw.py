import scratchattach as sa
import threading,MySQLdb
from time import strftime
from random import randint

balancespath = "/home/ubuntu/scratch/info/balances.txt"
chargespath = "/home/ubuntu/scratch/info/charges.txt"
blockedpath = "/home/ubuntu/scratch/info/blocked.txt"
reports = "/home/ubuntu/scratch/info/reports.txt"
remixes = "/home/ubuntu/scratch/info/remixes.txt"
notifications = "/home/ubuntu/scratch/info/notifications.txt"
logs = "/home/ubuntu/scratch/info/logs.txt"
allowsend = "/home/ubuntu/scratch/info/allowsend.txt"


#session = sa.login_by_id(str(open('sid','r').read()).replace('\n',''), username="SAMURAI228")
cloud = sa.get_tw_cloud("1319788189")
client = cloud.requests()
verificators = {
"a":"b"
}

@client.request
def ping(): #called when client receives request
    return "pong" #sends back 'pong' to the Scratch project

@client.request
def get_verificator_code(username):
   user = sa.get_user(username)
   verificator = user.verify_identity(verification_project_id = 1319788189) # The project id where the user has to comment can be specified as `verification_project_id` keyword argument 
   verificators[username] = verificator
   return verificator.code

@client.request
def verify(username):
   verificator = verificators[username]
   print (f"verificator;   {username}    ;   {verificator.check()}")
   return verificator.check()

@client.request
def get_balance(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT balance from balances where username = %s;",(username,))
    balance = cursor.fetchall()
    return balance

@client.event
def on_ready():
    print("Request handler is running")


def get_db():
    db = MySQLdb.connect(
        host="localhost",
        user="jidelna",
        database="scratch"
    )
    return db

client.start(thread=True) # thread=True is an optional argument. It makes the cloud requests handler run in a thread
