import alpaca_trade_api as ata
from typing import List, Dict, Any, NewType
from utils import *
from user import User
import pickle
from datetime import datetime
import configparser
NewType("User", User)
NewType("TraderResponse", TraderResponse)

DEBUG = True 

config = configparser.ConfigParser()

config.read('config.ini')
ALP_ERR = "Alpaca encountered an error: "
API_KEY_ID = config['ALPACA']['API_KEY_ID']
API_SECRET_KEY = config['ALPACA']['API_SECRET_KEY']
API_BASE_URL =  config['ALPACA']['API_BASE_URL'] if config['ALPACA']['API_BASE_URL'] else "https://paper-api.alpaca.markets" # be careful changing this!

def dprint(*args, **kwargs):
    if DEBUG:
        print("[debug] " + " ".join(map(str, args)), **kwargs)

class Trader(object):

    api = ata.REST(key_id=API_KEY_ID, secret_key=API_SECRET_KEY, base_url=API_BASE_URL)
    user_db: List[User] = []
    is_loaded = False

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
        #persist()

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
        for asset in u.portfolio:
        
            worth += self.api.get_last_trade(asset).price * u.portfolio[asset]
        worth += u.buying_power
        return TraderResponse(True, str(worth))


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
            price = self.api.get_last_trade(ticker).price
        except Exception as e:
            dprint(e)
            return TraderResponse(False,ALP_ERR + str(e))
    
        if purchaser.buying_power < price * quantity:
        
            dprint(f"Insufficient buying power! Have {purchaser.buying_power} but need {price * quantity}")
            return TraderResponse(False, f"Insufficient buying power! Have {purchaser.buying_power} but need {price * quantity}")
    
        ctime = self.api.get_clock()
        if not ctime.is_open:
            return TraderResponse(False, "Markets are closed!")

        try:

            self.api.submit_order(ticker, quantity, Side.buy, Type.market, TiF.day)
        except Exception as e:
            dprint(e)
            return TraderResponse(False, ALP_ERR + str(e))
    
        try:
            purchaser.portfolio[ticker] += quantity
        except KeyError:
            #dprint("key error!")
            purchaser.portfolio[ticker] = quantity
        purchaser.buying_power -= price * quantity
        
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
            price = self.api.get_last_trade(ticker).price
        except Exception as e:
            dprint(e)
            return TraderResponse(False, ALP_ERR + str(e))
    
        try:
            if quantity > seller.portfolio[ticker]:
        
                dprint(f"Insufficient holdings! Have {seller.portfolio[ticker]} but need {quantity}")
                return TraderResponse(False, f"Insufficient holdings! Have {seller.portfolio[ticker]} but need {quantity}")
        except KeyError as e:
            dprint(e)
            return TraderResponse(False, str(e) + f" are you sure you're holding {ticker}?")

        ctime = self.api.get_clock()
        if not ctime.is_open:
            return TraderResponse(False, "Markets are closed!")

        try:
            self.api.submit_order(ticker, quantity, Side.sell, Type.market, TiF.day)
        except Exception as e:
            dprint(e)
            return TraderResponse(False, ALP_ERR + str(e))
    
        seller.portfolio[ticker] -= quantity
        seller.buying_power += price * quantity
        self.persist()
        return TraderResponse(True, "Success!")
