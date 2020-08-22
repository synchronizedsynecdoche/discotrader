from typing import List, Dict, Any, NewType
from utils import *
from user import User
import pickle
from datetime import datetime
import time
NewType("User", User)
NewType("TraderResponse", TraderResponse)
NewType("Trader", Trader)
from utils import api, dprint
import threading

#DEBUG = True 
FORCE_EXECUTION = False

class Trader(object):


    user_db: List[User] = []
    is_loaded: bool = False

    def __init__(self) -> Trader:
        
        self.load()

    def persist(self) -> TraderResponse:

        try:
        
            with open("user_db", "wb") as f:
                pickle.dump(self.user_db, f)
        
        except Exception as e:
            return TraderResponse(False, str(e))

        return TraderResponse(True, "Persisted!")
    
    def backup(self) -> TraderResponse:

        try:
            with open("user_db" + str(datetime.now()), "wb") as f:
                pickle.dump(self.user_db, f)
        except Exception as e:
            return TraderResponse(False, str(e))

        return TraderResponse(True, "Backed up a copy of the database!")   
     
    def load(self) -> TraderResponse:

        self.is_loaded = True #even if we fail, we're considered loaded with a blank db
        try:

            with open("user_db", "rb") as f:
            
                temp = pickle.load(f)
                self.user_db = temp
                return TraderResponse(True, "Loaded successfully!")

        except FileNotFoundError as e:
        
            return TraderResponse(False, str(e) + " Starting a new DB")
    
    def addUser(self, id: int) -> TraderResponse:

        if id not in [u.ident for u in self.user_db]:
            temp = User(id)
            self.user_db.append(temp)
            self.persist()
            TraderResponse(True, f"Added a new user: {temp}")

    def locateUser(self, id: int) -> User: #internal

        for u in self.user_db:
            if u.ident == id:
                return u
        return None


    def getBuyingPower(self, id: int) -> TraderResponse:

        worth: float = 0
        u: User = self.locateUser(id)

        if u is None:
            return TraderResponse(False, "User doesn't exist!")
        
        return TraderResponse(True, f"${u.buying_power}")


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

        print(type(purchaser.portfolio))
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
        except NoneType as e:
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

        answer: str = ""

        for u in self.user_db:

            if u.ident == id:
                
                for p in u.portfolio:

                    answer += f"\n{p.ticker}:\n\tShares: {p.getQuantity()}\n\tAverage Cost: ${p.getAverageCost()}\n\tChange: {p.getTotalPriceChange()}\n\tPercent Change: {p.getPercentChange()}%"
                
                return TraderResponse(True, answer)
        
        return TraderResponse(False, "No such user")
                