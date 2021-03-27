import os
import random

import asyncio

import asyncpraw

async def get_cogcision() -> str:
    reddit = asyncpraw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
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

    # randomly pick a stock
    stock = random.choice(symbol_list)

    # # randomly pick buy/sell
    action = random.choice(["BUY", "SELL"])

    # # randomly pick amount
    amount = random.randint(1, 100)

    # # return sentence
    print(f"I WILL {action} {amount} share{'s' if amount >= 1 else ''} of {stock}.")
    return f"I WILL {action} {amount} share{'s' if amount >= 1 else ''} of {stock}."



async def main():
    await get_cogcision()

if __name__ == "__main__":
    asyncio.run(main())