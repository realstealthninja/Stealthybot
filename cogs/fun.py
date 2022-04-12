import random
import csv
from disnake.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def truthordare(self, ctx: commands.Context, type="t"):
        if type == "t":
            with open("assets/datasets/truth.csv") as f:
                ereader = csv.reader(f, delimiter=";")
                chosen = random.choice(list(ereader))
                await ctx.send(chosen[1])
        elif type == "d":
            with open("assets/datasets/dare.csv") as f:
                ereader = csv.reader(f, delimiter=";")
                chosen = random.choice(list(ereader))
                await ctx.send(chosen[1])
        else:
            await ctx.send("sorry that isnt a type use either t or d as your argument")


def setup(bot):
    bot.add_cog(Fun(bot))
