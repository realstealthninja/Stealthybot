import asyncio
import discord
from discord.ext import commands


class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(hidden=True, description="pulls the repo")
    async def pull(self, ctx):
        """this command will pull the code from github and put it in the hoster(my mobile)

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
        
    

def setup(bot):
    bot.add_cog(Staff(bot))
