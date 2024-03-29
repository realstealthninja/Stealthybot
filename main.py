import asyncio
import os
from dotenv import load_dotenv
from stealthybot import TwitchBot
from stealthybot import Stealthybot

load_dotenv("secrets.env")
token = os.getenv("Token")


twitchbot = TwitchBot()
stealthybot = Stealthybot()

# removing twtich support until further notice
# loop = asyncio.get_event_loop_policy().get_event_loop()
# loop.create_task(twitchbot.connect())


@stealthybot.check
async def precheck(ctx):
    if ctx.command.hidden and not await stealthybot.is_owner(ctx.author):
        return False
    return True


if __name__ == "__main__":
    stealthybot.run(token)
