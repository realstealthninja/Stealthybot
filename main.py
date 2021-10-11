import asyncio
import os
from datetime import datetime

import discord
import discord.ext
from dotenv import load_dotenv
from discord.ext import commands as dio
from twitchio.ext import commands as tio
from twitchio.ext.commands import bot

from SendWebHookMessage import *

load_dotenv(dotenv_path="secrets.env")
token = os.getenv('Token')

def Json(file1, data1):
    file1.truncate(0)
    file1.seek(0)
    file1.write(json.dumps(data1, indent=4))

bot = dio.Bot(['s?'], intents=discord.Intents.all())


for filename in os.listdir("./cogs/"):
    if filename.endswith('.py'):
        if not filename.startswith('dutils'):
            bot.load_extension(f'cogs.{filename[:-3]}')

@bot.check
async def precheck(ctx):
    if ctx.command.hidden and not await bot.is_owner(ctx.author):
        return False
    return True

@bot.command(hidden=True)
async def load(ctx, extension):
        embed = discord.Embed()
        bot.load_extension(f'cogs.{extension}')
        embed.add_field(name="Load Extension", value=f"Loaded cog: ``{extension}`` successfully")
        await ctx.send(embed=embed)

@bot.command(hidden=True)
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    embed = discord.Embed()
    embed.add_field(name="Unload Extension", value=f"Unloaded cog: ``{extension}`` successfully")
    await ctx.send(embed=embed)

#reload
@bot.command(aliases=['r'], hidden=True)
async def reload(ctx, extension=""):
    if not extension:
    
        for cog in tuple(bot.extensions):
    
            bot.reload_extension(cog)
        embed = discord.Embed()
        embed.add_field(name="Reload Extension", value=f"Reloaded cogs successfully")
        await ctx.send(embed=embed)
    else:

        bot.reload_extension(f'cogs.{extension}')
        embed = discord.Embed()
        embed.add_field(name="Reload Extension", value=f"Reloaded cog: ``{extension}`` successfully")
        await ctx.send(embed=embed)


async def elmayo(message:str, channel:int, name:str ):
    """this sends a message to a specified channel

    Args:
        message (str): the message that needs to be send
        channel (int): the id of the channel
        name (str): the name of the embed
    """    
    embed = discord.Embed(title=message, description="")
    embed.set_author(name=name,icon_url="https://cdn.slangit.com/img/sc/twitch/smile.png")
    await bot.get_channel(channel).send(embed = embed)


#on ready
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name =f"{bot.command_prefix}help"))
    print(discord.__version__)




#twitchio
class TwitchBot(tio.Bot):

    def __init__(self):
        super().__init__(token=os.getenv('TwitchToken'), prefix='?', initial_channels=['asgytreal'])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        now = datetime.now()
        #
        # SendMessage("bot starting......", f"Twitchio bot has been started | logged in as {self.nick}")

    async def event_message(self, message):
        if message.echo:
            return
        with open("Jsons/chatchannel.json", "r+") as f:
           datakek = json.load(f)
        for channel in datakek:
          await elmayo(message.content, int(channel),message.author.name)
        await self.handle_commands(message)

twitchbot = TwitchBot()

loop = asyncio.get_event_loop()
loop.create_task(twitchbot.connect())
bot.run(token)

