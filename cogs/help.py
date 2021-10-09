import datetime
from operator import iconcat, imod
from os import name, read
import discord
from discord import colour
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands
import json



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
      cogs = []
      cmds = []
      
      if not command:
        
        for k in self.bot.cogs:
          cog = self.bot.get_cog(k)
          cogs.append(cog.qualified_name)
        embed = discord.Embed(title="**Main Help Menu **",description = " ```asciidoc \n = do ?help <group name> for more info on the group = ```")
        embed.set_thumbnail(url="https://i.postimg.cc/HxDCyhc8/New-Project.png")
        embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
        embed.set_footer(text=f"issued at : {datetime.datetime.now()} by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="**links**:", value="<:github:896250023313043477> [github](https://github.com/realstealthninja/Stealthybot) | [offical server(includes moonfight)](https://discord.gg/HAbStFeVAj) | ")
        betterstring =  f"  *** Catagories :*** \n \n"
        for string in cogs:
          betterstring = betterstring + f"> **{string}** \n"
        print(betterstring)
        embed.add_field(name="⠀",value=betterstring, inline=False)
        
        
        await ctx.send(embed=embed)
      

      cog = self.bot.get_cog(command)
      print(cog)
      if cog:
        
        #this means they sent %help cog
        # DONE:
        # figure out how to set descriptions for cogs
        #
        with open("Jsons/cogdescriptions.json") as f:
          datakek = json.load(f)
        if cog.qualified_name in datakek:
          bettername = datakek[cog.qualified_name]["betternames"]
          description = datakek[cog.qualified_name]["description"]
          embed = discord.Embed(title=bettername,description=description)
          embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
          embed.set_footer(text=f"issued at : {datetime.datetime.now()} by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
          embed.add_field(name="**links**:", value="<:github:896250023313043477> [github](https://github.com/realstealthninja/Stealthybot) | [offical server(includes moonfight)](https://discord.gg/HAbStFeVAj) | ")
          commands = cog.get_commands()
          betteastring = "*** Commands: *** \n \n"
          for c in commands:
            betteastring += f"> **{c.name}** \n"
          embed.add_field(name=f"⠀", value=betteastring, inline=False)
          await ctx.send(embed=embed)
        else:
          await ctx.send("better name was not found D:")
        
      # TODO:
      # do the command help
      #
      #newcommand = bot.get_command(command)
      #if not newcommand:
       #  this means that the command they sent wasnt actually a command, so you need to             #reply saying 'that isnt a command!' 
      #else:
          #this means the command that they have sent is a command, so you send information           #about the command they sent (the command.description, command.name,       command.signature, etc) 


def setup(bot):
    bot.add_cog(Help(bot))
