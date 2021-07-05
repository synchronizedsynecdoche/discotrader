import utils
class Position(object):

    owner: int = 0
    ticker: str
    quantity: float = 0
    sigma_cost: float = 0
    identity: str 

    def __init__(self, ticker, init_quantity, init_price_per_share, owner):

        self.owner = owner
        self.ticker = ticker
        self.quantity = init_quantity
        self.sigma_cost = init_quantity * init_price_per_share
        self.identity = f"{owner}:{ticker}"


    def getValue(self) -> float:

        return self.quantity * utils.api.get_last_trade(self.ticker).price

    def update(self, delta, price_per_share) -> None:

        self.quantity += delta
        self.sigma_cost += delta * price_per_share # if this goes negative, it signifies a gain
    
    def getQuantity(self) -> float:
        
        return self.quantity

    def getAverageCost(self) -> float:

        if self.quantity <= 0 or self.sigma_cost < 0:
            return 0
        
        return self.sigma_cost / self.quantity

    def getTotalPriceChange(self) -> float:

        return self.getValue() - self.sigma_cost 


    def getPercentChange(self) -> float:

        if self.getValue() == 0: # rip
            return 0
        
        return 100 * (self.getValue() - self.sigma_cost) / self.sigma_cost 

    def split(self, ratio) -> None:

        if ratio <= 0:
            return 
            
        self.quantity *= ratio
    
    def package(self) -> str:

        return f"VALUES('{self.identity}','{self.ticker}', '{self.quantity}', '{self.sigma_cost}', '{self.owner}')"
        