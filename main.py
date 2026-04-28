import asyncio
import os
from dotenv import load_dotenv
from stealthybot import TwitchBot
from stealthybot import Stealthybot
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv("secrets.env")
token = os.getenv("Token")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

twitchbot = TwitchBot()
stealthybot = Stealthybot()

_ = loop.create_task(twitchbot.connect())


@stealthybot.check
async def precheck(ctx):
    if ctx.command.hidden and not await stealthybot.is_owner(ctx.author):
        return False
    return True


if __name__ == "__main__":
    stealthybot.run(token)
