from typing import List, Dict, Any, NewType
from utils import *
from user import User
import pickle
from datetime import datetime
import time
NewType("User", User)
NewType("TraderResponse", TraderResponse)
from utils import api
import threading

DEBUG = True 
FORCE_EXECUTION = False

def dprint(*args, **kwargs):
    if DEBUG:
        print("[debug] " + " ".join(map(str, args)), **kwargs)

class Trader(object):


    user_db: List[User] = []
    is_loaded: bool = False

    def persist(self) -> None:

        with open("user_db", "wb") as f:
            pickle.dump(self.user_db, f)
    
    
    def backup(self) -> None:

        with open("user_db" + str(datetime.now()), "wb") as f:
            pickle.dump(self.user_db, f)
        
    
    def load(self) -> TraderResponse:

        self.is_loaded = True #even if we fail, we're considered loaded with a blank db
        try:

            with open("user_db", "rb") as f:
            
                temp = pickle.load(f)
                self.user_db = temp
                return TraderResponse(True, "Loaded successfully!")
        

        except FileNotFoundError as e:
        
            dprint(e)
            return TraderResponse(False, str(e) + " Starting a new DB")
    
    def add_user(self, id: int) -> None:

        if id not in [u.ident for u in self.user_db]:
            temp = User(id)
            self.user_db.append(temp)
            self.persist()

    def locate_user(self, id: int) -> User:

        for u in self.user_db:
            if u.ident == id:
                return u
        return None


    def get_user_value(self, id: int) -> TraderResponse:

        worth: float = 0
        u: User = self.locate_user(id)

        if u is None:
            return TraderResponse(False, "User doesn't exist!")
        
        return TraderResponse(True, str(u.getPortfolioValue()+ u.buying_power))


    def buy(self, id: int, ticker: str, quantity: float) -> TraderResponse:


        if ticker is None or quantity <= 0:
            dprint("Garbage in the args...")
            return TraderResponse(False, "Bad ticker or quantity!")
    
        purchaser = self.locate_user(id)
        if purchaser is None:

            dprint(f"purchaser {id} doesn't exist!")
            return TraderResponse(False, f"purchaser {id} doesn't exist!")
        #turn this into a switch statement for excepts...
        try:
            price = api.get_last_trade(ticker).price
        except Exception as e:
            dprint(e)
            return TraderResponse(False,ALP_ERR + str(e))
    
        if purchaser.buying_power < price * quantity:
        
            dprint(f"Insufficient buying power! Have {purchaser.buying_power} but need {price * quantity}")
            return TraderResponse(False, f"Insufficient buying power! Have {purchaser.buying_power} but need {price * quantity}")
    
        ctime = api.get_clock()
        if not ctime.is_open and not FORCE_EXECUTION:

            buy_thread = threading.Thread(target=self.pendingBuy, args=(id, ticker, quantity))
            buy_thread.start()
            return TraderResponse(True, "Markets are closed, queueing order")

        try:

            api.submit_order(ticker, quantity, Side.buy, Type.market, TiF.day)
        except Exception as e:
            dprint(e)
            return TraderResponse(False, ALP_ERR + str(e))

        print(type(purchaser.portfolio))
        purchaser.updatePosition(ticker, quantity, price)

        self.persist()
        return TraderResponse(True, "Success!")

    def sell(self, id: int, ticker: str, quantity: float) -> TraderResponse:

        if ticker is None or quantity <= 0:

            dprint("Garbage in the args...")
            return TraderResponse(False, "Bad ticker or quantity!")
    
        seller = self.locate_user(id)
        if seller is None:

            dprint(f"seller {id} doesn't exist!")
            return TraderResponse(False, f"seller {id} doesn't exist!")
            
        #turn this into a switch statement for excepts...
        try:
            price = api.get_last_trade(ticker).price
        except Exception as e:
            dprint(e)
            return TraderResponse(False, ALP_ERR + str(e))
    
        try:
            if quantity > seller.findPosition(ticker).quantity:
        
                dprint(f"Insufficient holdings! Have {seller.findPosition(ticker).quantity} but need {quantity}")
                return TraderResponse(False, f"Insufficient holdings! Have {seller.findPosition(ticker).quantity} but need {quantity}")
        except KeyError as e:
            dprint(e)
            return TraderResponse(False, str(e) + f" are you sure you're holding {ticker}?")

        ctime = api.get_clock()
        if not ctime.is_open and not FORCE_EXECUTION:

            buy_thread = threading.Thread(target=self.pendingSell, args=(id, ticker, quantity))
            buy_thread.start()
            return TraderResponse(True, "Markets are closed, queueing order")

        try:
            api.submit_order(ticker, quantity, Side.sell, Type.market, TiF.day)
        except Exception as e:
            dprint(e)
            return TraderResponse(False, ALP_ERR + str(e))


        seller.updatePosition(ticker, -quantity, price)
        self.persist()
        return TraderResponse(True, "Success!")


    def pendingBuy(self, id: int, ticker: str, quantity: float) -> TraderResponse:
        while not api.get_clock().is_open:

            time.sleep(600)
            dprint(f"{id} has a pending order to buy {quantity} shares of {ticker}")
        self.buy(id, ticker, quantity)

def pendingSell(self, id: int, ticker: str, quantity: float) -> TraderResponse:
        while not api.get_clock().is_open:

            time.sleep(600)
            dprint(f"{id} has a pending order to sell {quantity} shares of {ticker}")
        self.buy(id, ticker, quantity)