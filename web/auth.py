import sqlite3
import hashlib
import base64


db=sqlite3.connect('users.sqlite',check_same_thread=False)


def init():
    cursor=db.cursor()
    cursor.execute('CREATE TABLE Users(Name TEXT , Password TEXT,CONSTRAINT User_key PRIMARY KEY (Name ))')
    return True

def all_users():
    cursor = db.cursor()
    cursor.execute('SELECT Name FROM Users')
    user_names=cursor.fetchall()
    return [r[0] for r in user_names]

def add_user(name,password):
    password=password.encode()
    #digest=hashlib.sha256(password).hexdigest()
    digest=password
    cursor=db.cursor()
    cursor.execute('INSERT INTO Users VALUES(?,?)',(name,digest))
    db.commit()
    return True


def get_passwd(name):
    if name in all_users():
        cursor=db.cursor()
        cursor.execute('SELECT Password FROM Users WHERE Name=?',(name,))
        pwd=cursor.fetchone()[0]
        if isinstance(pwd,bytes):
            return pwd.decode()
        return pwd

    return None

def update_user(name,password):
    if not name in all_users():
        return False

    password = password.encode()
    digest=password
    #digest=hashlib.sha256(password).hexdigest()
    cursor=db.cursor()
    cursor.execute('UPDATE Users SET Password=? WHERE Name=?',(digest,name))
    db.commit()
    return True

if __name__ == '__main__':
    #init()
    print(add_user('123','hash'))
    print(all_users())
    print(update_user('123','hello'))
    print(all_users())
    print(get_passwd('123'))