

import sqlite3
from position import Position
from user import User
from utils import *
from typing import List, Dict, Any, NewType
NewType("User", User)
NewType("Position", Position)
'''
p = Position("PLTR", 10, 100, 1)
con = sqlite3.connect(":memory:")
cursorObj = con.cursor()

cursorObj.execute("CREATE TABLE positions(identity string PRIMARY KEY, ticker string, quantity int, sigma_cost float, owner int)")
con.commit()
try:
    cursorObj.execute(f"INSERT INTO positions {p.package()}")
except sqlite3.IntegrityError:
    pass
con.commit()

cursorObj.execute('SELECT * from positions WHERE owner IS 1')
rows = cursorObj.fetchall()

for row in rows:
    print(row)
'''
class DatabaseInterface(object):
    
    connection = None
    cursor = None
    
    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute("""CREATE TABLE positions(
                identity string PRIMARY KEY, ticker string, quantity int, sigma_cost float, owner int)""")
            self.cursor.execute("CREATE TABLE users(identity int PRIMARY KEY, buying_power float)")
            self.connection.commit()
        except sqlite3.OperationalError as e:
            dprint(f"Operatitonal error caught: {e}, db already exists?")
    def commitUser(self, u: User):
        
        try:
            self.cursor.execute(f"INSERT INTO users VALUES({u.ident},{u.buying_power})")
            self.connection.commit()

        except sqlite3.IntegrityError as e:

            self.cursor.execute(f"SELECT * FROM users WHERE identity IS {u.ident}")
            if len(self.cursor.fetchall()) == 1:
            
                dprint("Caught IntegrityError, but was from existing user")
            
            else: # ouch
                return False
        
        return True

    def check(self):
        self.cursor.execute("SELECT * FROM users")
        rows = self.cursor.fetchall()
        for row in rows:
            dprint(row)

dbi = DatabaseInterface("test.db")
user = User(1)
dbi.commitUser(user)
dbi.check()