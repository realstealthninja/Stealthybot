import asyncio
import json, os
from twitchio.ext import commands as commands


class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.getenv("TwitchToken"),
            prefix="?",
            initial_channels=["asgytreal"],  # pyright: ignore[reportArgumentType]
            loop=asyncio.new_event_loop(),
        )

    async def event_message(self, message):
        if message.echo:
            return
        with open("Jsons/chatchannel.json", "r+") as f:
            datakek = json.load(f)
        for channel in datakek:
            await self.elmayo(
                message.content,
                int(channel),
                message.author.name,
                "https://cdn.slangit.com/img/sc/twitch/smile.png",
            )
            await self.handle_commands(message)
