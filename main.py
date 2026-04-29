import os
from dotenv import load_dotenv
from stealthybot import Stealthybot
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv("secrets.env")
token = os.getenv("Token")

# twitchbot = TwitchBot()
stealthybot = Stealthybot()


@stealthybot.check
async def precheck(ctx):
    if ctx.command.hidden and not await stealthybot.is_owner(ctx.author):
        return False
    return True


if __name__ == "__main__":
    stealthybot.run(token)
