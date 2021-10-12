import asyncio
import os
import coc
import discord
import discord.ext
from dotenv import load_dotenv
from discord.ext import commands as dio
from twitchio.ext import commands as tio
from twitchio.ext.commands import bot

from SendWebHookMessage import *

load_dotenv(dotenv_path="secrets.env")
token = os.getenv('Token')
coc_client = coc.login(

    email = os.getenv('cocemail'),

    password =os.getenv('cocpass'),

    key_names="test",

    client=coc.EventsClient,

)
  
def Json(file1, data1):
    file1.truncate(0)
    file1.seek(0)
    file1.write(json.dumps(data1, indent=4))

class Stealthybot(dio.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="s?",
            description="worst bot ever lol",
            intents = discord.Intents.all(),
            case_insensitive= True,
            owner_id=[521226389559443461]
            
        )
        self.coc_client = coc_client
  

        for filename in os.listdir("./cogs/"):
            if filename.endswith('.py'):
                if not filename.startswith('dutils'):
                    self.load_extension(f'cogs.{filename[:-3]}')


    async def precheck(self, ctx):
        if ctx.command.hidden and not await self.is_owner(ctx.author):
            return False
        return True




    async def elmayo(message:str, channel:int, name:str ):
        """this sends a message to a specified channel

        Args:
            message (str): the message that needs to be send
            channel (int): the id of the channel
            name (str): the name of the embed
        """    
        embed = discord.Embed(title=message, description="")
        embed.set_author(name=name,icon_url="https://cdn.slangit.com/img/sc/twitch/smile.png")
        await self.get_channel(channel).send(embed = embed)


    #on ready
    async def on_ready(self):
        print(f"We have logged in as {self.user}")

    
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name =f"{self.command_prefix}help"))
        print(discord.__version__)




    #twitchio
class TwitchBot(tio.Bot):

        def __init__(self):
            super().__init__(token=os.getenv('TwitchToken'), prefix='?', initial_channels=['asgytreal'])

        async def event_ready(self):
            print(f'Logged in as | {self.nick}')
        
            #
            # SendMessage("bot starting......", f"Twitchio bot has been started | logged in as {self.nick}")

        async def event_message(self, message):
            if message.echo:
                return
            with open("Jsons/chatchannel.json", "r+") as f:
                datakek = json.load(f)
            for channel in datakek:
                await self.elmayo(message.content, int(channel),message.author.name)
                await self.handle_commands(message)

twitchbot = TwitchBot()

loop = asyncio.get_event_loop()
loop.create_task(twitchbot.connect())
if __name__ == "__main__":
    stelbot = Stealthybot()
    stelbot.run(token)
    

