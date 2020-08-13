import enum
from marshmallow import Schema, fields

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

    status = False
    message = ""

    def __init__(self, status, message):
        self.status = status
        self.message = message