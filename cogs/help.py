import disnake
from disnake.ext import commands
import json

class MyHelp(commands.HelpCommand):
      # ?help
      async def send_bot_help(self, mapping):
        cogs = []
        for cog , command in mapping.items():
        
          cogs.append(getattr(cog, "qualified_name", "⠀"))
        embed = disnake.Embed(title="**Main Help Menu **",description = " ```ini\n[ do s?help <group name> for more info on the group ] ``` ", timestamp=self.context.message.created_at)
        embed.set_thumbnail(url="https://i.postimg.cc/HxDCyhc8/New-Project.png")
        embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
        embed.set_footer(text=f"issued by {self.context.author.display_name}", icon_url=self.context.author.avatar)
        embed.add_field(name="**links**:", value="<:github:896250023313043477> [github](https://github.com/realstealthninja/Stealthybot) | [offical server](https://discord.gg/HAbStFeVAj) | [invite me!](https://discord.com/api/oauth2/authorize?client_id=889922820317007928&permissions=534659984470&scope=bot) ")
        betterstring =  f"  *** Catagories :*** \n \n"
        for string in cogs:
          betterstring = betterstring + f"> **{string}** \n"
        embed.add_field(name="⠀",value=betterstring, inline=False)
        await self.context.send(embed=embed)
        

      # ?help <command>
      async def send_command_help(self, command):
        newcommand = command
        embed = disnake.Embed()
        embed.set_author(name="Help", icon_url=self.context.author.avatar)
        embed.add_field(name="⦑ Name ⦒", value=f"`{newcommand.qualified_name}`",inline=False )
        alias = command.aliases
        if alias:
            alias2 = ', '.join(alias)
            embed.add_field(name="⦑ Aliases ⦒", value=f"`{alias2}`", inline=False)
        embed.add_field(name="⦑ usage ⦒", value=f"`?{newcommand.name + newcommand.signature}`" if newcommand.signature else f"`?{newcommand.name}`", inline=False)
        embed.add_field(name="⦑ Description ⦒", value=f"`{newcommand.description}`", inline=False)
        embed.set_footer(text="<> = needed │ [] = not needed")
        await self.context.send(embed = embed)
        

      # ?help <group>
      #we are not using it cause we dont have any grouped commands
      #async def send_group_help(self, group):
      #   await self.context.send("This is help group")
    


      # ?help <cog>
      async def send_cog_help(self, cog):
        with open("Jsons/cogdescriptions.json") as f:
          datakek = json.load(f)
        if cog.qualified_name in datakek:
          bettername = datakek[cog.qualified_name]["betternames"]
          description = datakek[cog.qualified_name]["description"]
          embed = disnake.Embed(title=bettername,description=description,timestamp=self.context.message.created_at)
          embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
          embed.set_footer(text=f"issued by {self.context.author.display_name}", icon_url=self.context.author.avatar)
          embed.add_field(name="**links**:", value="<:github:896250023313043477> [github](https://github.com/realstealthninja/Stealthybot) | [offical server(includes moonfight)](https://discord.gg/HAbStFeVAj) | ")
          commands = cog.get_commands()
          betteastring = "*** Commands: *** \n \n"
          for c in commands:
            betteastring += f"> **{c.name}** \n"
          embed.add_field(name=f"⠀", value=betteastring, inline=False)
          await self.context.send(embed=embed)
        else:
          await self.context.send("better name was not found D:")
        
    

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelp()
        bot.help_command.cog = self

        

def setup(bot):
    bot.add_cog(Help(bot))
