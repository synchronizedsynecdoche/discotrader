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

DEBUG=True
def dprint(*args, **kwargs):
    if DEBUG:
        print("[debug] " + " ".join(map(str, args)), **kwargs)

def stringify(x):

    return "{0:.2f}".format(x)

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
        dprint(f"Saw TraderResponse({self.status}, {self.message})")
