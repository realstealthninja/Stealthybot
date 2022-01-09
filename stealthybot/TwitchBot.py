import json, os
from twitchio.ext import commands as commands



# making the channels accessable 

class TwitchBot(commands.Bot):
        def __init__(self):
            super().__init__(token=os.getenv('TwitchToken'), prefix='?', initial_channels=['asgytreal'])

        async def event_ready(self):
            print(f'Logged in as | {self.nick}')
        
        async def event_message(self, message):
            if message.echo:
                return
            with open("Jsons/chatchannel.json", "r+") as f:
                datakek = json.load(f)
            for channel in datakek:
                await self.elmayo(message.content, int(channel),message.author.name, "https://cdn.slangit.com/img/sc/twitch/smile.png")
                await self.handle_commands(message)