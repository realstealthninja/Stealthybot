import json
import discord
from discord.ext import commands



def Json(file1, data1):
    file1.truncate(0)
    file1.seek(0)
    file1.write(json.dumps(data1, indent=4))
    
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.profiles = "Jsons/economy/profiles.json"
        self.jobs = "Jsons/economy/jobs.json"
    
    
    async def add_or_find_account(self, userid:int, money:int = 100):
        with open (self.profiles, "r+") as f:
            datakek = json.load(f)
            if str(userid) in datakek:
                return None, datakek[userid]
            else:
                datakek[str(userid)] = {
                    "balance": 100,
                    "job_id": "0",
                    "inventory": []
                }   
                Json(f, datakek)
                return True
            
    
    @commands.command()
    async def start(self, ctx):
        
        acc = await self.add_or_find_account(ctx.author.id)
        if acc == True:
            embed=discord.Embed(title="Account made!", description="`you have been registered to stealthy economy, have fun!`",timestamp = ctx.message.created_at)
            embed.set_author(name=ctx.author.name,icon_url=ctx.author.avatar_url)
            embed.add_field(name="Balance", value="> 100", inline=False)
            embed.set_footer(text=f" issued by {ctx.author.name}")
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(timestamp = ctx.message.created_at)
            embed.add_field(name="You already have a acccount!", value="bal: in progress", inline=False)
            await ctx.send(embed=embed)       


   
def setup(bot):
    bot.add_cog(Economy(bot))
