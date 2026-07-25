import threading,MySQLdb
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


path = "/home/ubuntu/info/balances.txt"
file = open(path,"r").readlines()
db = get_db()
cursor = db.cursor()

for line in file:
    username, balance = line.strip().split("|")
    cursor.execute("INSERT INTO balances (username, balance, read_notifications, accepted) values (%s, %s,0,1);", (username,balance,))
    db.commit()