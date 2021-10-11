import json
import re
from aiosqlite import cursor
from aiosqlite.context import Result
import discord
import aiosqlite
from discord import message

from discord.ext import commands
from discord.ext.commands.core import cooldown

from main import Json


    
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.bot.loop.create_task(self.connect())        
        
        
    #a function to connect to the database
    async def connect(self):
        self.db = await aiosqlite.connect("dbs/economy.db")
    
    #A find or make function for conveince
    async def Find_account_or_Make_account(self, User_Id: discord.Member.id):
        accountmade = None
        cursor = await self.db.cursor()
        await cursor.execute('select * from Balance where UserId = ? ', (User_Id,))
        result = await cursor.fetchone()
        await cursor.execute('select * from Profiles where userid = ? ', (User_Id))
        profileresult = await cursor.fetchone
        accountmade = False
        if result is None and profileresult is None:
            profileresult = (0,0, User_Id)
            result= (User_Id, 100)
            await cursor.execute('insert into Balance values(?,?)', (result))
            await cursor.execute('insert into Profiles values(?,?,?)', (profileresult))
            await self.db.commit()
            accountmade = True
            return result, accountmade , profileresult
        else:
            return result, accountmade , profileresult
    
    async def add_cash(self, amount:int, userid: discord.Member.id):
        cursor = await self.db.cursor()
        await cursor.execute('Update Balance set Cash =? where UserId=?', (amount ,userid) )
        await self.db.commit()

    async def update_job(self, jobid:int, userid: discord.Member.id):
        cursor = await self.db.cursor()
        await cursor.execute('updare Profiles set job_id =? where userid=?', (jobid, userid))
        await self.db.commit()
    
    @commands.command(aliases=["start adventure"])
    async def start(self, ctx):
        account = await  self.Find_account_or_Make_account(ctx.author.id)
        if account[1] == True:
            await ctx.send("account was made")
        else:   
            await ctx.send("account already exists")    
    
    @commands.command(aliases=["bal"])
    async def balance(self, ctx, member: discord.member=None):
        member = member or ctx.author
        user = await self.Find_account_or_Make_account(member.id)
        cash = user[0][1]
        await ctx.send(cash)
    @commands.command()
    async def work(self, ctx):
        user = await self.Find_account_or_Make_account(ctx.author.id)
        oldcash = user[0][1]
        print(user[2][0])
        if user[2][0] == 0:
            await ctx.send("you dont have a job!")
        else:
            await self.add_cash(oldcash+100,ctx.author.id)
            await ctx.send("you earned 100")
    @commands.command()
    async def job(self, ctx):
        with open("Jsons/jobs.json", "r+") as f:
            datakek = json.load(f)
        
        embed = discord.Embed(title="Job list")
        betterstring =  f"  ** Jobs :** \n \n"
        for job in datakek:
            pay = datakek[job]["Base_pay"]
            betterstring = betterstring + f"> **{job} || pay : {pay} ** \n"
        embed.add_field(name="⠀", value=betterstring)
        await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Economy(bot))
