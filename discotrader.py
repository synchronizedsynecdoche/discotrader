import discord
from discord.ext import commands
from trader import Trader
from utils import TraderResponse
from user import User
from typing import Any, Dict, List
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
TOKEN: str = config['DISCORD']['TOKEN']
ADMIN: int = int(config['DISCORD']['ADMIN'])
AUTH_ERR: str = "Unauthorized Action!"
VERSION = 0

class DiscoTrader(commands.Cog):

    trader: Trader = None

    def __init__(self, bot):

        # does not spark joy        
        self.bot = bot
        self.bot.add_cog(self)
        self.bot.run(TOKEN)

    def ensureTraderExists(self) -> TraderResponse:

        if self.trader is None:
            self.trader = Trader()

        if not self.trader.is_loaded:
            
            resp = self.trader.load()
            return resp

        return None
    @commands.command(name='ping')
    async def ping(self, ctx):

        await ctx.send("pong! ")

    @commands.command(name='echo')
    async def echo(self, ctx, *, msg:str):

        await ctx.send(f"message \"{msg}\" from {ctx.message.author.id}")


    @commands.command(name='init')
    async def init(self, ctx):
        if ctx.message.author.id != ADMIN:
            await ctx.send(AUTH_ERR)
        else:
            self.trader = Trader()
            await ctx.send("Initialized trader, don't forget to load!")

    @commands.command(name='load')
    async def load(self, ctx):

        if ctx.message.author.id != ADMIN:
            await ctx.send(AUTH_ERR)
            return

        if self.trader is None or not self.trader.is_loaded:
            resp = self.ensureTraderExists()
            await ctx.send(resp.message)

    @commands.command(name='buy')
    async def buy(self, ctx, ticker: str, quantity: float):

        if self.trader is None or not self.trader.is_loaded:
            resp = self.ensureTraderExists()
            await ctx.send(resp.message)

        self.trader.add_user(ctx.message.author.id)
        await ctx.send(f"Saw BUY from {ctx.message.author.id} for {quantity} shares of {ticker.upper()}")
    
        resp = self.trader.buy(ctx.message.author.id,ticker.upper(),quantity)
        await ctx.send(resp.message)

    @commands.command(name='sell')
    async def sell(self, ctx, ticker: str, quantity: float):

        if self.trader is None or not self.trader.is_loaded:
            resp = self.ensureTraderExists()
            await ctx.send(resp.message)
        
        await ctx.send(f"Saw SELL from {ctx.message.author.id} for {quantity} shares of {ticker.upper()}")
    
        resp = self.trader.sell(ctx.message.author.id,ticker.upper(),quantity)
        await ctx.send(resp.message)

    @commands.command(name='val')
    async def val(self, ctx):
    
        if self.trader is None or not self.trader.is_loaded:
            resp = self.ensureTraderExists()
            await ctx.send(resp.message)


        resp = self.trader.get_user_value(ctx.message.author.id)
        await ctx.send(resp.message)

    @commands.command(name='backup')
    async def backup(self, ctx):
        if ctx.message.author.id != ADMIN:
            await ctx.send(AUTH_ERR)
            return

        if self.trader is None or not self.trader.is_loaded:
            resp = self.ensureTraderExists()
            await ctx.send(resp.message)

        self.trader.backup()
        await ctx.send("OK!")

    @commands.command(name='clear')
    async def clear(self, ctx):
        if ctx.message.author.id != ADMIN:
            await ctx.send(AUTH_ERR)
            return

        if self.trader is None or not self.trader.is_loaded:
            resp = self.ensureTraderExists()
            await ctx.send(resp.message)


        self.trader.backup()
        self.trader.user_db = []
        await ctx.send("Destroyed database!")
    
    @commands.command(name='pf')
    async def pf(self, ctx):

        if self.trader is None or not self.trader.is_loaded:
            resp = self.ensureTraderExists()
            await ctx.send(resp.message)

        for u in self.trader.user_db:
            if u.ident == ctx.message.author.id:
                for p in u.portfolio:
                    await ctx.send(f"{p.ticker} : {p.getValue()}")

    @commands.command(name='?')
    async def qmark(self, ctx):

        await ctx.send(f"""DiscoTrader v{VERSION}
    Testing Commands:
        ?ping: pongs you
        ?echo: echos you
    Administrator Commands:
        ?init: initialize the trader
        ?load: initialize the trader and load the database
        ?backup: make a copy of the database object
        ?clear: clear the database
    User Commands:
        ?buy TICKER X: purchase X shares of TICKER
        ?sell TICKER X: sell X shares of TICKER
        ?val: get your current net worth
        ?pf: get your full portfolio
        ??: Display this message""")         
        
dt = DiscoTrader(commands.Bot(command_prefix='?'))