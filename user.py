import alpaca_trade_api as ata
from typing import List, Any, NewType
from position import Position
from threading import Lock
class User(object):
    
    portfolio: List[Position]
    buying_power: float
    ident: int
    #mutex: Lock
    
    def __init__(self, ident: int, buying_power=10000):

        print(f"Spawned an instance of User with ident={ident}")
        self.portfolio = list()
        self.buying_power = buying_power
        self.ident = ident

        #self.mutex = Lock()

    def __str__(self) -> str:
        return f"User object with ident={self.ident}"

    
    def getPortfolioValue(self) -> float:
        
        ret = 0
        for p in self.portfolio:
            
            ret += p.getValue()
        return ret
    
    def updatePosition(self, ticker: str, delta: float, price: float) -> None:

        #self.mutex.acquire(blocking=False)

        for p in self.portfolio:
            if ticker == p.ticker:
                p.update(delta, price)
                return

        self.portfolio.append(Position(ticker, delta, price, self.ident))
        self.buying_power -= price * delta

        #self.mutex.release()
    
    def findPosition(self, ticker) -> Position:

        # TODO: make this error resistant
        for p in self.portfolio:
            if p.ticker == ticker:

                return p
        return None