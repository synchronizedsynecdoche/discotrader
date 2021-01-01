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

        self.cursor.execute("""CREATE TABLE IF NOT exists positions(
                identity string PRIMARY KEY, ticker string, quantity int, sigma_cost float, owner int)""")
        self.cursor.execute("CREATE TABLE IF NOT exists users(ident int PRIMARY KEY, buying_power float)")
        self.connection.commit()
    def commitUser(self, u: User) -> bool:
        
        try:
            self.cursor.execute(f"""INSERT OR REPLACE INTO users VALUES({u.ident},{u.buying_power})""")
            self.connection.commit()

        except Exception as e:
            dprint(e)
            return False
        
        for p in u.portfolio:
            if not self.commitPosition(p):
                return False

        return True
    def commitPosition(self, p: Position) -> bool:
        try:
            self.cursor.execute(f"INSERT OR REPLACE INTO positions {p.package()}")
            return True
        except Exception as e:
            dprint(e)
        
        return False
    def check(self):
        self.cursor.execute("SELECT * FROM users")
        rows = self.cursor.fetchall()
        for row in rows:
            dprint(row)
        
        self.cursor.execute("SELECT * FROM positions")
        rows = self.cursor.fetchall()

        for row in rows:
            dprint(rows)
    
    def retrieveUsers(self) -> List[User]:
        returnable = []
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        for user in users:
            
            t_user = User(user[0], buying_power=user[1])
            self.cursor.execute(f"SELECT * FROM positions WHERE owner={t_user.ident}")
            positions = self.cursor.fetchall()
            
            for position in positions:
                t_user.portfolio.append(Position(position[1], position[2], position[3]/position[2],t_user.ident))
            
            returnable.append(t_user)
        
        return returnable

    
    
dbi = DatabaseInterface("db.db")
user = User(1)
user.updatePosition("PLTR", 10, 100)
dbi.commitUser(user)
dbi.check()
dprint([p.package() for p in dbi.retrieveUsers()[0].portfolio])