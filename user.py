import alpaca_trade_api as ata
from typing import List, Dict, Any, NewType
from utils import *

class User(object):
    
    portfolio: Dict[str, float]
    buying_power: float
    ident: int
   
    def __init__(self, ident: int):

        print(f"Spawned an instance of User with ident={ident}")
        self.portfolio = {}
        self.buying_power = 10000
        self.ident = ident

    def __str__(self):
        return f"User object with ident={self.ident}"
