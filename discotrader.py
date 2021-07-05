from coggers import get_cogcision
import discord
from discord.ext import commands
from trader import Trader
from utils import TraderResponse, dprint
from user import User
from typing import Any, Dict, List
import configparser

config: configparser.ConfigParser = configparser.ConfigParser()
config.read('config.ini')
TOKEN: str = config['DISCORD']['TOKEN']
ADMIN: int = int(config['DISCORD']['ADMIN'])
AUTH_ERR: str = "Unauthorized Action!"
VERSION: int = 0

class DiscoTrader(commands.Cog):

    trader: Trader

    def __init__(self, bot):

        # does not spark joy        
        self.bot = bot
        bot.remove_command('help')
        self.bot.add_cog(self)
        self.bot.run(TOKEN)


    @commands.command(name='ping')
    async def ping(self, ctx):
        
        dprint("pong! ")
        await ctx.send("pong! ")

    @commands.command(name='echo')
    async def echo(self, ctx, *, msg:str):

        await ctx.send(f"message \"{msg}\" from {ctx.message.author.id}")


    @commands.command(name='init')
    async def trader_init(self, ctx, override=False):
        if ctx.message.author.id != ADMIN and not override:
            await ctx.send(AUTH_ERR)
        else:
            self.trader = Trader()
            self.trader.load()

            await ctx.send("Trader initialized and loaded")


    @commands.command(name='buy')
    async def buy(self, ctx, ticker: str, quantity: float):

        if self.trader is None:
            self.trader_init(ctx, override=True)

        self.trader.addUser(ctx.message.author.id)
        #await ctx.send(f"Saw BUY from {ctx.message.author.id} for {quantity} shares of {ticker.upper()}")
    
        resp = self.trader.buy(ctx.message.author.id,ticker.upper(),quantity)
        await ctx.send(resp.message)

    @commands.command(name='sell')
    async def sell(self, ctx, ticker: str, quantity: float):

        if self.trader is None:
            self.trader_init(ctx, override=True)
        #await ctx.send(f"Saw SELL from {ctx.message.author.id} for {quantity} shares of {ticker.upper()}")
    
        resp = self.trader.sell(ctx.message.author.id,ticker.upper(),quantity)
        await ctx.send(resp.message)

    @commands.command(name='bp')
    async def buyingPower(self, ctx):

        resp = self.trader.getBuyingPower(ctx.message.author.id)
        await ctx.send(resp.message)

    @commands.command(name='backup')
    async def backup(self, ctx):
        if ctx.message.author.id != ADMIN:
            await ctx.send(AUTH_ERR)
            return


        resp = self.trader.backup()
        await ctx.send(resp.message)

    @commands.command(name='clear')
    async def clear(self, ctx):
        if ctx.message.author.id != ADMIN:
            await ctx.send(AUTH_ERR)
            return


        self.trader.backup()
        self.trader.user_db = []
        await ctx.send("Destroyed database!")
    
    @commands.command(name='pf')
    async def pf(self, ctx):


        resp = self.trader.getPortfolio(ctx.message.author.id)
        await ctx.send(resp.message)

    @commands.command(name='stock')
    async def stock(self, ctx, ticker):

        resp = self.trader.getStockInfo(ticker)

        await ctx.send(resp.message)

    @commands.command(name='?', aliases=['help', 'h'])
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
        ?split TICKER R: manually split stocks by a ratio R 
    User Commands:
        ?buy TICKER X: purchase X shares of TICKER
        ?sell TICKER X: sell X shares of TICKER
        ?bp: get your buying power
        ?pf: get your full portfolio
        ?stock TICKER: get information about a stock
        ??: Display this message
        ?help and ?h: alias for ??""")         
    
    @commands.command(name='split')
    async def split(self, ctx, ticker, ratio):
        if ctx.message.author.id != ADMIN:
            await ctx.send(AUTH_ERR)
            return
        resp = self.trader.fixAfterSplit(ticker.upper(), ratio)

        await ctx.send(resp.message)
    
    @commands.command(name='coggers')
    async def cog(self, ctx):
        message = get_cogcision()

        await ctx.send(message)
dt = DiscoTrader(commands.Bot(command_prefix='?'))