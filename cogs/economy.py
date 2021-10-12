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
        self.items = "Jsons/economy/items.json" 
    
    
    async def add_or_find_account(self, userid:int, money:int = 100):
        with open (self.profiles, "r+") as f:
            datakek = json.load(f)
            if str(userid) in datakek:
                return None, datakek[userid]
            else:
                datakek[str(userid)] = {
                    "balance": 100,
                    "bank": 0,
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

    
    @commands.command()
    async def profile(self, ctx, member:discord.Member=""):
        with open (self.profiles, "r+") as f:
            datakek = json.load(f)
            if member=="":

                if str(ctx.author.id) in datakek:
                    embed = discord.Embed(title=ctx.author.name)
                    embed.set_thumbnail(url= ctx.author.avatar_url)
                    bal = datakek[str(ctx.author.id)]["balance"]
                    bank = datakek[str(ctx.author.id)]["bank"]
                    embed.add_field(name="Balance and bank",value=f"> {bal} || {bank}", inline=False)
                    with open(self.jobs, "r+") as jobjson:
                        jobkek = json.load(jobjson)
                    jobid = datakek[str(ctx.author.id)]["job_id"]
                    if jobid != "0":
                        jobname = jobkek[jobid]["name"]
                        embed.add_field(name="job", value=f"> {jobname}", inline=False)
                    else:
                        embed.add_field(name="Job",value="> this user has no job", inline=False)
                    listofitems = datakek[str(ctx.author.id)]["inventory"]
                    if bool(listofitems):
                        with open(self.items, "r+") as k:
                                itemkek = json.load(k)
                        betterstring=""
                        for item in listofitems:
                            itemname = itemkek[item]["name"]
                            emojiname = itemkek[item]["emoji"]
                            betterstring+= f"> {itemname} :: {emojiname}\n"
                        embed.add_field(name="Inventory", value=betterstring,inline=False)
                    else:
                        embed.add_field(name="Inventory", value="> No items in inventory")    
                    
                    await ctx.send(embed=embed)
                    
                else:
                    embed= discord.Embed(name="account not found!",description="you dont have an account!")
                    await ctx.send(embed=embed)
            else:
                if str(member.id) in datakek:
                    embed = discord.Embed(title=member.name)
                    embed.set_thumbnail(url= member.avatar_url)
                    bal = datakek[str(member.id)]["balance"]
                    bank = datakek[str(member.id)]["bank"]
                    embed.add_field(name="Balance and bank",value=f"> <:stealthycoin:897331306013286440>  {bal} || <:stealthycoin:897331306013286440>  {bank}", inline=False)
                    with open(self.jobs, "r+") as jobjson:
                        jobkek = json.load(jobjson)
                    jobid = datakek[str(member.id)]["job_id"]
                    if jobid != "0":
                        jobname = jobkek[jobid]["name"]
                        embed.add_field(name="job", value=f"> {jobname}", inline=False)
                        
                    else:
                        embed.add_field(name="Job",value="> this user has no job", inline=False)
                    listofitems = datakek[str(ctx.author.id)]["inventory"]
                    listofitems = datakek[str(member.id)]["inventory"]
                    if bool(listofitems):
                        with open(self.items, "r+") as k:
                                itemkek = json.load(k)
                        betterstring=""
                        for item in listofitems:
                            itemname = itemkek[item]["name"]
                            emojiname = itemkek[item]["emoji"]
                            betterstring+= f"> {itemname} :: {emojiname}\n"
                        embed.add_field(name="Inventory", value=betterstring,inline=False)
                    else:
                        embed.add_field(name="Inventory", value="> No items in inventory")
                    await ctx.send(embed=embed)
                else:
                    embed= discord.Embed(name="account not found!",description="the peron who you mentioned dont have an account!")
                    await ctx.send(embed=embed)
            
    @commands.command()
    async def iteminfo(self, ctx, *,item = None):
        print(item)
        with open(self.items, "r+") as f:
            datakek = json.load(f)
        if item ==None:
            embed = discord.Embed(title="Itemlist",timestamp=ctx.message.created_at)
            betterstring = "**Items currently in the bot**:\n"
            for k in datakek:
                itemname = datakek[k]["name"]
                betterstring += f"> {itemname}\n"
            embed.add_field(name="⠀",value=betterstring)
            await ctx.send(embed=embed)
        else:
            
            #https://ibb.co/9c6r496
            for k in datakek:
                if item == datakek[k]["name"]:
                    embed = discord.Embed(title="Item info",timestamp=ctx.message.created_at)
                    embed.set_footer(text=f"command issued by: {ctx.author.name}",icon_url=ctx.author.avatar_url)
                    embed.add_field(name=datakek[k]["name"],value=datakek[k]["item_desc"], inline=True)
                    value=datakek[k]["value"]
                    embed.add_field(name="value:", value=f"<:stealthycoin:897331306013286440> {value}")
                    image = datakek[k]["thumbnail"]
                    embed.set_thumbnail(url=image)
                    if datakek[k]["item_type"] == 1:
                        embed.add_field(name="type:", value="> amour <:armour:897329092444192768>",inline=False)
                        defence = datakek[k]["stats"]["defence"]
                        sharpres = datakek[k]["stats"]["s_res"]
                        bluntres = datakek[k]["stats"]["b_res"]
                        health_increasse = datakek[k]["stats"]["health_inc"]
                        stats = f"> defence = {defence},\n > sharp resistance ={sharpres},\n > blunt resistance = {bluntres},\n > health increase = {health_increasse} "
                        embed.add_field(name="stats", value=stats,inline=False)
                    if datakek[k]["item_type"] == 2:
                        embed.add_field(name="type:", value="> weapon <:attack:897321966640439296>",inline=False)
                        attack = datakek[k]["stats"]["attack"]
                        sharpdam = datakek[k]["stats"]["s_dam"]
                        bluntdam = datakek[k]["stats"]["b_dam"]
                        stats = f"> defence = {attack},\n > sharp damage ={sharpdam},\n > blunt damage = {bluntdam}"
                        embed.add_field(name="stats", value=stats)
                    await ctx.send(embed=embed)
                    break
                

def setup(bot):
    bot.add_cog(Economy(bot))
