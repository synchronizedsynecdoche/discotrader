import logging
import os
import random

import asyncio

import asyncpraw

from utils import api, REDDIT_SECRET, REDDIT_ID

async def get_cogcision() -> str:
    reddit = asyncpraw.Reddit(
        client_id=REDDIT_ID,
        client_secret=REDDIT_SECRET,
        user_agent="prawddit",
    )

    subreddit = await reddit.subreddit("wallstreetbets")

    symbol_list = []

    async for comment in subreddit.comments(limit=10000000):
        words = comment.body.split()
        for word in words:
            if len(word) in range(1,5) or (word[0] == "$"):
                symbol = True
                for c in word:
                    if c.islower() or not c.isalpha():
                        symbol = False

                if symbol:
                    symbol_list.append(word)
    
    async for comment in subreddit.new(limit=10000000):
        words = comment.title.split()
        for word in words:
            if len(word) in range(1,5) or (word[0] == "$"):
                symbol = True
                for c in word:
                    if c.islower() or not c.isalpha():
                        symbol = False

                if symbol:
                    symbol_list.append(word)
    
    counter = 0
    while True:
        # randomly pick a stock
        symbol = random.choice(symbol_list)
        try:
            print(f"trying {symbol}")
            stock = api.get_last_trade(symbol)
            break
        except:
            counter += 1
            if counter == 100:
                return "SORRY IM TOO WEAK. THESE FOOLS ARE SPEWING BULLSHIT."
                break
            pass
        
    # # randomly pick buy/sell
    action = random.choice(["BUY", "SELL"])

    # # randomly pick amount
    amount = random.randint(1, 100)

    # # return sentence
    return (f"I WILL {action} {amount} SHARE{'S' if amount >= 1 else ''} OF {symbol}. THIS LITTLE MANEUVER IS GONNA COST US $" + str(stock.price * amount))



async def main():
    await get_cogcision()

if __name__ == "__main__":
    asyncio.run(main())