import sqlite3

con=sqlite3.connect("db",check_same_thread=False)


def init():
    cursor=con.cursor()

    cursor.execute("CREATE TABLE IF NOT EXIST actions(ID int AUTOINCREMENT,Type int,Time TIMESTAMP,PRIMARY KEY(id))")

    cursor.close()

def add_event(type,message):
    cursor=con.cursor()

    cursor.execute("INSERT INTO events(type,description) VALUES(?,?)",(type,message))
    con.commit()

def add_login_attempt(func):
    add_event("LOGIN","Login attempt")
    return func


def add_exec_attempt(func):
    add_event("EXEC","Executin_attempt")
    return func

def add_move_attempt(func):
    add_event("MOVEMENT","Some actions were detected")
    return func



def add_wifi_start(func):
    add_event("WIFI","wifi started")
    return func

def add_wifi_stop(func):
    add_event("WIFI","wifi stoped")
    return func


def add_webgui_start(func=None):
    add_event("WEBGUI","Webgui stoped")
    if func: func()

def add_webgui_stop(func=None):
    add_event("WEBGUI","Webgui stoped")
    if func: func()


def on_led_cleanup():
    add_event("LED","LED connect cleaned")

def on_led_inited():
    add_event("LED","LED inited")


