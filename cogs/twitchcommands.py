import discord
import json
from discord.ext import commands
def Json(file1, data1):
         file1.truncate(0)
         file1.seek(0)
         file1.write(json.dumps(data1, indent=4))


class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(aliases=["ac"], description="adds twitch chat to a specified channel")
    async def addchat(self, ctx, channelid=None):
            with open("Jsons/chatchannel.json", "r+") as f:
                datakek = json.load(f)
                if (channelid == None):
           
                    datakek[str(ctx.channel.id)] = {
                    "channelid": f"{ctx.guild.id}"
                    }
                    Json(f, datakek)
                    await ctx.send("channel added")
                if(channelid != None):
                    datakek[str(channelid)] = {
                        "guild": f"{ctx.guild.id}"
                    }
                    Json(f, datakek)
                    await ctx.send("channel added")
    

def setup(bot):
    bot.add_cog(Twitch(bot))
