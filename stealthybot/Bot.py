import discord, os, coc, dotenv
from discord.ext import commands


dotenv.load_dotenv("secrets.env")
class Stealthybot(commands.Bot):
    coc_client = coc.login(
    
        email = os.getenv('cocemail'),
        password =os.getenv('cocpass'),
        key_names="test",
        client=coc.EventsClient,

    )

    def __init__(self):
        super().__init__(
            command_prefix="s?",
            description="worst bot ever lol",
            intents = discord.Intents.all(),
            case_insensitive= True,
            owner_ids=[521226389559443461]
        )
        self.coc_client = self.coc_client

    
        for filename in os.listdir("./cogs/"):
            if filename.endswith('.py') and not filename.startswith('dutils'):
                    self.load_extension(f'cogs.{filename[:-3]}')

    async def elmayo(self,message:str, channel:int, name:str ):
        """this sends a message to a specified channel

        Args:
            message (str): the message that needs to be send
            channel (int): the id of the channel
            name (str): the name of the embed
        """    
        embed = discord.Embed(title=message, description="")
        embed.set_author(name=name,icon_url="https://cdn.slangit.com/img/sc/twitch/smile.png")
        await self.get_channel(channel).send(embed = embed)
 

    async def on_ready(self):
        print(f"We have logged in as {self.user}")

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name =f"{self.command_prefix}help"))
        print(discord.__version__)


