import sqlite3
from position import Position
from user import User
import utils
from typing import List, Dict, Any, NewType
NewType("User", User)
NewType("Position", Position)

class DatabaseInterface(object):
    
    connection = None
    cursor = None
    filename = None
    
    def __init__(self, filename="disco.db"):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        self.filename = filename

        self.cursor.execute("""CREATE TABLE IF NOT exists positions(
                identity string PRIMARY KEY, ticker string, quantity int, sigma_cost float, owner int)""")
        self.cursor.execute("CREATE TABLE IF NOT exists users(ident int PRIMARY KEY, buying_power float)")
        self.connection.commit()


    def commitUsers(self, users: List[User])-> bool:
        for u in users:
            if not self.commitUser(u):
                return False
        
        return True

    def commitUser(self, u: User) -> bool:
        
        try:
            self.cursor.execute(f"""INSERT OR REPLACE INTO users VALUES({u.ident},{u.buying_power})""")
            self.connection.commit()

        except Exception as e:
            utils.utils.dprint(e)
            return False
        
        for p in u.portfolio:
            if not self.commitPosition(p):
                return False

        return True
    def commitPosition(self, p: Position) -> bool:
        try:
            self.cursor.execute(f"INSERT OR REPLACE INTO positions {p.package()}")
            self.connection.commit()
            return True
        except Exception as e:
            utils.dprint(e)
        
        return False
    def check(self):
        self.cursor.execute("SELECT * FROM users")
        rows = self.cursor.fetchall()
        for row in rows:
            utils.dprint(row)
        
        self.cursor.execute("SELECT * FROM positions")
        rows = self.cursor.fetchall()

        for row in rows:
            utils.dprint(rows)
    
    def retrieveUsers(self) -> List[User]:
        returnable = []
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        for user in users:
            
            t_user = User(user[0], buying_power=user[1])
            self.cursor.execute(f"SELECT * FROM positions WHERE owner={t_user.ident}")
            positions = self.cursor.fetchall()
            ratio = float(ratio)
            for position in positions:
                if position[2] == 0:
                    continue
                t_user.portfolio.append(Position(position[1], position[2], position[3]/position[2],t_user.ident))
            
            returnable.append(t_user)
        
        return returnable

    def backup(self) -> bool:
        bak = sqlite3.connect(self.filename +".bak")
        with bak:
            self.connection.backup(bak)
        bak.close()