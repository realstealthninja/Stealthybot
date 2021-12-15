import asyncio, io, contextlib
from traceback import format_exception
import textwrap
from logging import exception
import aiosqlite
import discord
from discord.ext import commands
from discord.ext import buttons

def clean_code(content:str) -> str:
    if content.startswith("```py"):
        content = content[5:-3]
    content = content.strip("`")
    content = content.replace("‘", "'").replace('“', '"').replace("”", "\"").replace("’", "'")
    return content

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.bot.loop.create_task(self.connecttodb())
        
    async def connecttodb(self):
        self.db = await aiosqlite.connect("./database/activity.db")    
    
    
    @commands.command(hidden=True)
    async def sqlcommand(self, ctx ,*, sqlcode,data=None, ):
        emebed = discord.Embed(title="Sql injector")
        try:
            cursor = await self.db.cursor()
            if data:
                await cursor.execute(sqlcode, (int(data),))
            await cursor.execute(sqlcode)
            result = None
            if "select" in sqlcode:
                result = await cursor.fetchone()
            await self.db.commit()
            bettastring = ""
            for thingy in result:
                bettastring += f"{thingy} | "
            emebed.add_field(name="result", value=f"{bettastring}")
        except Exception as ex:
            emebed.add_field(name="error occured", value=f"{ex}")
        await ctx.send(embed = emebed)
        
    
    
    @commands.command(hidden=True, description="pulls the repo")
    async def pull(self, ctx):
        """this command will pull the code from the current repo

        Args:
            ctx ctx: ctx that dpy provides

        Returns:
            null: it doesnt return shit?
        """
        embed = discord.Embed(title="Git pull.", description="")
        git_commands = [
            ["git", "stash"],
            ["git", "pull", "--ff-only"]
        ]
        for git_command in git_commands:
            process = await asyncio.create_subprocess_exec(
                git_command[0],
                *git_command[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            output, error = await process.communicate()
            embed.description += f'[{" ".join(git_command)!r} exited with return code {process.returncode}\n'
            if output:
                embed.description += f"**[stdout]**\n{output.decode()}\n"
            if error:   
                embed.description += f"**[stderr]**\n{error.decode()}\n"
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def load(self, ctx, extension):
            embed = discord.Embed()
            self.bot.load_extension(f'cogs.{extension}')
            embed.add_field(name="Load Extension", value=f"Loaded cog: ``{extension}`` successfully")
            await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def unload(self, ctx, extension):
        self.bot.unload_extension(f'cogs.{extension}')
        embed = discord.Embed()
        embed.add_field(name="Unload Extension", value=f"Unloaded cog: ``{extension}`` successfully")
        await ctx.send(embed=embed)

    
    
    
    #reload
    @commands.command(aliases=['r'], hidden=True)
    async def reload(self, ctx, extension=""):
        if not extension:
    
            for cog in tuple(self.bot.extensions):
    
                self.bot.reload_extension(cog)
            embed = discord.Embed()
            embed.add_field(name="Reload Extension", value=f"Reloaded cogs successfully")
            await ctx.send(embed=embed)
        else:

            self.bot.reload_extension(f'cogs.{extension}')
            embed = discord.Embed()
            embed.add_field(name="Reload Extension", value=f"Reloaded cog: ``{extension}`` successfully")
            await ctx.send(embed=embed)   

    @commands.command(aliases=['e'], hidden=True)
    async def eval(self, ctx, *, code:str) -> None:
        local_variables = {
            "discord": discord,
            "commands": commands, 
            "bot": ctx.bot, 
            "client": ctx.bot,
            "ctx": ctx, 
            "channel": ctx.channel, 
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message
        }

        code = clean_code(code)
        stdout = io.StringIO()

        pref = await ctx.bot.get_prefix(ctx.message)
        message = clean_code(ctx.message.content[len(pref) -1:])
            
        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}",  local_variables, 
                )
                obj = await local_variables["func"]()
            
                result = f"{stdout.getvalue()}{obj}\n"
        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__))
            pass
    
        result = result.replace('`', '')
        message = message.replace('`', '')
        if result.replace('\n', '').endswith('None') and result != "None":
            result = result[:-5]
            
        if len(result) < 2000:
            return await ctx.send(f"```py\nIn[0]: {message}\nOut[0]: {result}\n```")

        pager = buttons.Paginator(
            timeout=100,
            entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
            length=1,
            prefix="```py\n",
            suffix="```"
        )
        await pager.start(ctx)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            return await ctx.send('You are not a bot staff')
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            await ctx.send(error)

def setup(bot):
    bot.add_cog(Staff(bot))
