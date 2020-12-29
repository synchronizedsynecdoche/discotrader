

import sqlite3
from position import Position
from user import User
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
        self.connection = sqlite3.connect(":memory:")
        self.cursor = connection.cursor()
        self.cursor.execute("""CREATE TABLE positions(
            identity string PRIMARY KEY, ticker string, quantity int, sigma_cost float, owner int)""")
        self.cursor.execute("""CREATE TABLE users(identity int PRIMARY KEY)""")
        self.connection.commit()
    def commitUser(self, u: User) -> bool:
        

