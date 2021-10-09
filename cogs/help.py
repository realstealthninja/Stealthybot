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
        embed = discord.Embed(title="**Main Help Menu **",description = " ```ini\n[ do ?help <group name> for more info on the group ] ``` ", timestamp=ctx.message.created_at)
        embed.set_thumbnail(url="https://i.postimg.cc/HxDCyhc8/New-Project.png")
        embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
        embed.set_footer(text=f"issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="**links**:", value="<:github:896250023313043477> [github](https://github.com/realstealthninja/Stealthybot) | [offical server(includes moonfight)](https://discord.gg/HAbStFeVAj) | ")
        betterstring =  f"  *** Catagories :*** \n \n"
        for string in cogs:
          betterstring = betterstring + f"> **{string}** \n"
        embed.add_field(name="⠀",value=betterstring, inline=False)
        
        
        await ctx.send(embed=embed)
      
      cog = self.bot.get_cog(command)
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
          embed = discord.Embed(title=bettername,description=description,timestamp=ctx.message.created_at)
          embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
          embed.set_footer(text=f"issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
          embed.add_field(name="**links**:", value="<:github:896250023313043477> [github](https://github.com/realstealthninja/Stealthybot) | [offical server(includes moonfight)](https://discord.gg/HAbStFeVAj) | ")
          commands = cog.get_commands()
          betteastring = "*** Commands: *** \n \n"
          for c in commands:
            betteastring += f"> **{c.name}** \n"
          embed.add_field(name=f"⠀", value=betteastring, inline=False)
          await ctx.send(embed=embed)
        else:
          await ctx.send("better name was not found D:")
        
     
      newcommand = self.bot.get_command(command)
      if not newcommand:
       #  this means that the command they sent wasnt actually a command, so you need to             
       # #reply saying 'that isnt a command!'
       embed = discord.Embed(title="Couldn't find Command/Catogory",description=" ```ini\n[ The command or catagory you specified doesnt exist! check the spelling ] ``` ",timestamp=ctx.message.created_at)
       embed.set_author(name="Error!", icon_url="https://img1.pnghut.com/21/4/5/NqXfU4QNEg/black-and-white-error-message-triangle-point.jpg")
       embed.set_thumbnail(url="https://icon2.cleanpng.com/20180716/ufq/kisspng-computer-icons-symbol-error-error-icon-5b4c4c02302596.3605614915317268501972.jpg")
       embed.set_footer(text=f"issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
       await ctx.send(embed=embed)
        
      else:
        #this means the command that they have sent is a command, so you send information           
        #about the command they sent (the command.description, command.name,command.signature, etc) 
        embed = discord.Embed(title="⠀")
        alieses = newcommand.aliases
        betteralieses = "⠀"
        for k in alieses:
          betteralieses += f", k"
        embed.add_field(name="⮚ Name ⮘", value=f"`{newcommand.qualified_name}`",inline=False )
        embed.add_field(name-"⮚ Aliases ⮘", value=f"` {betteralieses} `", inline=False)
        embed.add_field(name="⮚ usage ⮘", value=f"`?{newcommand.name + newcommand.signature}`" if newcommand.signature else f"`?{newcommand.name}`", inline=False)
        embed.add_field(name="⮚ Description ⮘", value=f"`{newcommand.description}`", inline=False)
        embed.set_footer(text="<> = needed │ [] = not needed")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
