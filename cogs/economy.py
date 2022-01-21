import aiosqlite
from disnake.ext import commands

class Player():
    def __init__(self, bank, wallet, items, user_id):
        self.bank = bank
        self.wallet = wallet
        self.items = items
        self.user_id = user_id

class Item():
    def __init__(self, name, type):
        self.name = name
        self.type = type
        
    async def setdefence(self, amount):
        self.defence = amount
    
    async def setattack(self, attack):
        self.attack = attack
    
    async def setid(self, id):
        self.id = id
    
        


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.bot.loop.create_task(self.connectdb())
    
    
    async def connectdb(self):
        self.db = await aiosqlite.connect("database\economy.db")
    
    async def register_status(self, user_Id):
        cur = await self.db.cursor()
        query = await cur.execute("select * from profile where id = ?", (user_Id,))
        query = await query.fetchone()
        
        if not query:
            await cur.execute(f"insert into profile values(?, 0,0, 'None')", (user_Id,))
            await self.db.commit()
    async def get_user (self, user_id):
        cur = await self.db.cursor()
        result = await cur.execute("select * from profile where id = ?", (user_id,))
        result.fetchone()
        return Player(result[1], result[2], result[3])
    
    async def add_money(self, id, money, place):
        cur = await self.db.cursor()
         
        await cur.execute(f"select {place} from profile where id = ?", (id,))
        acc = cur.fetchone()
        await cur.execute(f"update profile set {place} = ? where_id = ?",(acc[0]+ money, id,))
        await self.db.commit()
    
    async def remove_money(self, id, money, place):
        cur = await self.db.cursor()
         
        await cur.execute(f"select {place} from profile where id = ?", (id,))
        acc = cur.fetchone()
        await cur.execute(f"update profile set {place} = ? where_id = ?",(acc[0]- money, id,))
        await self.db.commit()
        
    async def add_item(self, id, item:Item):
        cur = await self.db.cursor()
        acc = await cur.execute(f"select items from profile where id= ?",(id,))
        
        await self.db.commit()
    
    
    
def setup(bot):
    bot.add_cog(Economy(bot))
