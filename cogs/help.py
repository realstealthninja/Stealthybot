import disnake
from disnake.ext import commands
import json


class MyHelp(commands.HelpCommand):
    # ?help
    async def send_bot_help(self, mapping):
        embed = disnake.Embed(
        title="**Main Help Menu **",
        description=" ```ini\n[ do sb?help <group name> for more info on the group ] ``` ",
        timestamp=self.context.message.created_at,
        ).set_thumbnail(
            url="https://i.postimg.cc/HxDCyhc8/New-Project.png"
        ).set_author(
            name="frustra etiam in morte!",
            icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300",
        ).set_footer(
            text=f"issued by {self.context.author.display_name}",
            icon_url=self.context.author.avatar,
        ).add_field(
            name="**links**:",
            value="<:github:940532132399444011>[github](https://github.com/realstealthninja/Stealthybot) | [offical server](https://discord.gg/HAbStFeVAj) | [invite me!](https://discord.com/api/oauth2/authorize?client_id=889922820317007928&permissions=440972733504&scope=bot)",
        )
        catagories = """
        ***Catagories: ***
        
        > **Economy**
        > **Misc**
        > **Fun**
        > **Help**
        > **Gaming**
        """
        embed.add_field(name="⠀", value=catagories, inline=False)
        await self.context.send(embed=embed)

    # ?help <command>
    async def send_command_help(self, command):
        command: commands.Command = self.bot.get_command(c)
        if not command.description:
            command.descritpion = "``"
        embed = disnake.Embed().set_author(
            name="Help",
            icon_url=self.context.author.avatar
        ).add_field(
            name="⦑ Name ⦒",
            value=f"`{command.qualified_name}`",
            inline=False
        )
        if command.aliases:
            command.aliases = ", ".join(command.aliases)
            embed.add_field(name="⦑ Aliases ⦒", value=f"`{command.aliases}`", inline=False)
            embed.add_field(
            name="⦑ usage ⦒",
            value=f"`?{command.name + command.signature}`"
            if command.signature
            else f"`?{command.name}`",
            inline=False,
        )
        embed.add_field(
            name="⦑ Description ⦒", value=f"{command.description}", inline=False
        )
        embed.set_footer(text="<> = needed │ [] = not needed")    
        await self.context.send(embed=embed)

    # ?help <group>
    # we are not using it cause we dont have any grouped commands
    # async def send_group_help(self, group):
    #   await self.context.send("This is help group")

    # ?help <cog>
    async def send_cog_help(self, cog):
        embed = disnake.Embed(
            title=cog.qualified_name.capitalize(),
            description=cog.description,
            timestamp=self.context.message.created_at,
        )
        embed.set_author(
            name="frustra etiam in morte!",
            icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300",
        )
        embed.set_footer(
            text=f"issued by {self.context.author.display_name}",
            icon_url=self.context.author.avatar,
        )
        embed.add_field(
            name="**links**:",
            value="<:github:940532132399444011> [github](https://github.com/realstealthninja/Stealthybot) | [offical server](https://discord.gg/HAbStFeVAj) | ",
        )
        commands = "*** Commands: *** \n \n"
        for c in cog.get_commands():
            if c.hidden:
                continue
            commands += f"> **{c.name}** \n"
        embed.add_field(name=f"⠀", value=commands, inline=False)
        return await self.context.send(embed=embed)


class Help(commands.Cog, name="help"):
    """
    Help cog,
    Contains help commands
    """
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelp()
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(Help(bot))
