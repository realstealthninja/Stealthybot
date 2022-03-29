import asyncio
import os
from dotenv import load_dotenv
from stealthybot import TwitchBot
from stealthybot import Stealthybot

load_dotenv("secrets.env")
token = os.getenv("Token")


twitchbot = TwitchBot()
stelbot = Stealthybot()

loop = asyncio.get_event_loop_policy().get_event_loop()
loop.create_task(twitchbot.connect())


@stelbot.check
async def precheck(ctx):
    if ctx.command.hidden and not await stelbot.is_owner(ctx.author):
        return False
    return True


if __name__ == "__main__":
    stelbot.run(token)
