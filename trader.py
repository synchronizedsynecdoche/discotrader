from typing import List, Dict, Any, NewType
from utils import *
from position import Position
from user import User
import pickle
from datetime import datetime
import time
import threading
import configparser
from databaseInterface import DatabaseInterface

DB_NAME = "disco.db"

NewType("User", User)
NewType("TraderResponse", TraderResponse)

DEBUG: bool = True 
FORCE_EXECUTION: bool = True
LEGACY_INTERFACE: bool = False

class Trader(object):

    user_db: List[User] = []
    is_loaded: bool = False
    dbi = None
    def __init__(self):
        
        self.dbi = DatabaseInterface(filename=DB_NAME)
        self.mutex = threading.Lock()
        
        self.mutex.acquire(blocking=False)
        self.mutex.acquire(blocking=False)

    def persist(self) -> TraderResponse:

        if not self.is_loaded:
            return TraderResponse(False, "not loaded!")
        if LEGACY_INTERFACE:
            try:
        
                with open("user_db", "wb") as f:

                    self.mutex.acquire(blocking=False)
                    pickle.dump(self.user_db, f)
                    self.mutex.release()

            except Exception as e:
                return TraderResponse(False, str(e))

            return TraderResponse(True, "persisted!")
        else:
            self.dbi.commitUsers(self.user_db)
            return TraderResponse(True, "persisted!")
    
    def backup(self) -> TraderResponse:

        if not self.is_loaded:
            return TraderResponse(False, "not loaded!")
        if LEGACY_INTERFACE:
            try:
                with open("user_db" + str(datetime.now()), "wb") as f:
                
                    self.mutex.acquire(blocking=False)
                    pickle.dump(self.user_db, f)
                    self.mutex.release()
        
            except Exception as e:
                return TraderResponse(False, str(e))

            return TraderResponse(True, "Backed up a copy of the database!")   
        
        else:
            self.dbi.backup()
            return TraderResponse(True, "Backed up the database!")   
    def load(self) -> TraderResponse:

        self.is_loaded = True #even if we fail, we're considered loaded with a blank db

        if LEGACY_INTERFACE:
            try:

                with open("user_db", "rb") as f:
            
                    temp = pickle.load(f)
                
                    self.mutex.acquire(blocking=False)
                    self.user_db = temp
                    self.mutex.release()

            except FileNotFoundError as e:
        
                return TraderResponse(False, str(e) + " Starting a new DB")
        else:
            self.user_db = self.dbi.retrieveUsers()


        return TraderResponse(True, "loaded successfully!")
    
    def addUser(self, id: int) -> TraderResponse:

        if id not in [u.ident for u in self.user_db]:

            temp = User(id)
            
            self.mutex.acquire(blocking=False)
            self.user_db.append(temp)
            self.mutex.release()
            
            self.persist()
            TraderResponse(True, f"Added a new user: {temp}")

    def locateUser(self, id: int) -> User: #internal

        for u in self.user_db:
            if u.ident == id:
                return u
        return None


    def getBuyingPower(self, id: int) -> TraderResponse:

        u = self.locateUser(id)
        if u is None:
            return TraderResponse(False, "User doesn't exist!")
        
        return TraderResponse(True, f"${stringify(u.buying_power)}")


    def buy(self, id: int, ticker: str, quantity: float) -> TraderResponse:


        if ticker is None or quantity <= 0:
            return TraderResponse(False, "Bad ticker or quantity!")
    
        purchaser = self.locateUser(id)
        if purchaser is None:

            return TraderResponse(False, f"purchaser {id} doesn't exist!")
        #turn this into a switch statement for excepts...
        try:
            price = api.get_last_trade(ticker).price
        except Exception as e:
            return TraderResponse(False,ALP_ERR + str(e))
    
        if purchaser.buying_power < price * quantity:
        
            return TraderResponse(False, f"Insufficient buying power! Have {purchaser.buying_power} but need {price * quantity}")
    
        ctime = api.get_clock()
        if not ctime.is_open and not FORCE_EXECUTION:

            buy_thread = threading.Thread(target=self.pendingBuy, args=(id, ticker, quantity))
            buy_thread.start()
            return TraderResponse(True, "Markets are closed, queueing order")

        try:

            api.submit_order(ticker, quantity, Side.buy, Type.market, TiF.day)
        except Exception as e:
            return TraderResponse(False, ALP_ERR + str(e))
    
        purchaser.updatePosition(ticker, quantity, price)

        self.persist()
        return TraderResponse(True, "Success!")

    def sell(self, id: int, ticker: str, quantity: float) -> TraderResponse:

        if ticker is None or quantity <= 0:

            return TraderResponse(False, "Bad ticker or quantity!")
    
        seller = self.locateUser(id)
        if seller is None:

            return TraderResponse(False, f"seller {id} doesn't exist!")
            
        #turn this into a switch statement for excepts...
        try:
            price = api.get_last_trade(ticker).price
        except Exception as e:

            return TraderResponse(False, ALP_ERR + str(e))
    
        try:
            if quantity > seller.findPosition(ticker).quantity:
        
                return TraderResponse(False, f"Insufficient holdings! Have {seller.findPosition(ticker).quantity} but need {quantity}")
        except Exception as e:
            return TraderResponse(False, str(e) + f" are you sure you're holding {ticker}?")

        ctime = api.get_clock()
        if not ctime.is_open and not FORCE_EXECUTION:

            sell_thread = threading.Thread(target=self.pendingSell, args=(id, ticker, quantity))
            sell_thread.start()
            return TraderResponse(True, "Markets are closed, queueing order")

        try:
            api.submit_order(ticker, quantity, Side.sell, Type.market, TiF.day)
        except Exception as e:
            return TraderResponse(False, ALP_ERR + str(e))


        seller.updatePosition(ticker, -quantity, price)

        self.persist()
        return TraderResponse(True, "Success!")


    def pendingBuy(self, id: int, ticker: str, quantity: float) -> TraderResponse:
        while not api.get_clock().is_open:

            time.sleep(600)
            dprint(f"{id} has a pending order to buy {quantity} shares of {ticker}")
        
        return self.buy(id, ticker, quantity)

    def pendingSell(self, id: int, ticker: str, quantity: float) -> TraderResponse:
        while not api.get_clock().is_open:

            time.sleep(600)
            dprint(f"{id} has a pending order to sell {quantity} shares of {ticker}")
        return self.buy(id, ticker, quantity)

    def getStockInfo(self, ticker: str)-> TraderResponse:

        return TraderResponse(True, f"https://stockcharts.com/c-sc/sc?s={ticker.upper()}&p=D&b=5&g=0&i=0&r=1597681545347")

    def getPortfolio(self, id: int) -> TraderResponse:

        answer = ""

        for u in self.user_db:

            if u.ident == id:
                
                for p in u.portfolio:

                    answer += f"\n{p.ticker}:\n\tShares: {p.getQuantity()}\n\tAverage Cost: ${stringify(p.getAverageCost())}\n\tChange: ${stringify(p.getTotalPriceChange())}\n\tPercent Change: {stringify(p.getPercentChange())}%"
                
                return TraderResponse(True, answer)
        
        return TraderResponse(False, "No such user")

    def fixAfterSplit(self, ticker: str, ratio: int) -> TraderResponse:

        if not ratio.isnumeric():
            return TraderResponse(False, "Bad ratio")

        ratio = int(ratio)
        self.mutex.acquire(blocking=False)
        for u in self.user_db:
            for p in u.portfolio:
                if p.ticker == ticker:
                    p.split(ratio)
        self.mutex.release()

        return TraderResponse(True, "Stock successfully split!")


