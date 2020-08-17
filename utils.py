import enum
import configparser
import alpaca_trade_api as ata

config = configparser.ConfigParser()
config.read('config.ini')
ALP_ERR = "Alpaca encountered an error: "
API_KEY_ID = config['ALPACA']['API_KEY_ID']
API_SECRET_KEY = config['ALPACA']['API_SECRET_KEY']
API_BASE_URL =  config['ALPACA']['API_BASE_URL'] if config['ALPACA']['API_BASE_URL'] else "https://paper-api.alpaca.markets" # be careful changing this!
api = ata.REST(key_id=API_KEY_ID, secret_key=API_SECRET_KEY, base_url=API_BASE_URL)

class Side(str, enum.Enum):
    
    buy = "buy"
    sell = "sell"

class Type(str, enum.Enum):

    market = "market"
    limit = "limit"
    stop = "stop"
    stop_limit = "stop_limit"

# https://alpaca.markets/docs/trading-on-alpaca/orders/#time-in-force
class TiF(str, enum.Enum):
    
    day = "day"
    till_cancelled = "gtc"
    on_open = "opg"
    on_close = "cls"
    imm_or_x = "ioc"
    fill_or_kill = "fok"

class TraderResponse(object):

    status: bool = False
    message: str = "Default response"

    def __init__(self, status, message):
        self.status = status
        self.message = message

class Position(object):

    ticker: str
    quantity: float = 0
    #avg_cost = 0
    owner: int = 0

    def __init__(self, ticker, init_quantity, init_cost, owner):

        self.ticker = ticker
        self.quantity = init_quantity
        #self.a = init_cost
        self.owner = owner


    def getValue(self) -> float:

        return self.quantity * api.get_last_trade(self.ticker).price

    def update(self, delta, price_per_share) -> None:

        self.quantity += delta
    
    def getQuantity(self) -> float:
        
        return self.quantity

    



