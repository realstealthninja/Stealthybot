import disnake, os, coc, dotenv
from disnake.ext import commands


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
            command_prefix= "s?",
            description="worst bot ever lol",
            intents = disnake.Intents.all(),
            case_insensitive= True,
            owner_ids=[521226389559443461]
        )
        
        for filename in os.listdir("./cogs/"):
            if filename.endswith('.py') and not filename.startswith('dutils'):
                    self.load_extension(f'cogs.{filename[:-3]}')
 
    async def on_ready(self):
        print(f"We have logged in as {self.user}")

        await self.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name =f"{self.command_prefix}help"))
        print(disnake.__version__)


