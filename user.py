import alpaca_trade_api as ata
from typing import List, Dict, Any, NewType
from utils import Position

class User(object):
    
    portfolio: List[Position]
    buying_power: float
    ident: int
   
    def __init__(self, ident: int):

        print(f"Spawned an instance of User with ident={ident}")
        self.portfolio = {}
        self.buying_power = 10000
        self.ident = ident

    def __str__(self) -> str:
        return f"User object with ident={self.ident}"

    
    def getPortfolioValue(self) -> float:
        
        ret = 0
        for p in portfolio:
            
            ret += p.getValue()
        return ret
    
    def updatePosition(self, ticker: str, delta: float, price: float) -> None:

        for p in portfolio:
            if ticker == p.ticker:
                p.updatePosition(delta, price)
                return
        portfolio.append(Position(ticker, delta, price, self.ident))
        