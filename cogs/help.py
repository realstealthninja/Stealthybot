
from os import name, read
import discord
from discord import colour
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["h"])
    async def help(self, ctx, command = None):
      """this command will bring up help 

      Args:
          ctx ([ctx]): [the ctx that dpy provides]
          command ([string], optional): [command is optional cause the user can get the full list]. Defaults to None.
      """          
      if not command:
        cogs = []
        cmds = []
        for k in self.bot.cogs:
          cog = self.bot.get_cog(k)
          cogs.append(cog.qualified_name)
        embed = discord.Embed(title="temp help",description = " ll the groups :D")
        for cog2 in cogs:
            embed.add_field(name=cog2,value="032")
        await ctx.send(embed=embed)
      if cog:
        #this means they sent %help cog
        # TODO:
        # figure out how to set descriptions for cogs
        #
        embed = discord.Embed(title=f"{cog.qualified_name}",description="figuring out the descriotions ", colour = discord.Color.red())
        commands = cog.get_commands()
        for c in commands:
          embed.add_field(title="> c.name", value="temp desc")
          
        
      #newcommand = bot.get_command(command)
      #if not newcommand:
       #  this means that the command they sent wasnt actually a command, so you need to             #reply saying 'that isnt a command!' 
      #else:
          #this means the command that they have sent is a command, so you send information           #about the command they sent (the command.description, command.name,       command.signature, etc) 


def setup(bot):
    bot.add_cog(Help(bot))
