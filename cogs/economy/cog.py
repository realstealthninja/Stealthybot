import json
import random
import disnake

from disnake.ext import commands
from . import ProfileDropdownView

from .objects import Item, Player, Server
from .constants import prosperity, landlevelindex


"""
basic player class with minimal functionalites := remove, add money | remove, add items | remove, add citzenship | equip, uneuip items
basic item class with minimal functionalites := item stats
basic server class with minimal functionalites := level up settlement | shop, quest, trade systems | (re)generate loot pool | (re)generate enemy pool


basic quest system :     quest -> quest controller(server wide) -> recive money or and loot
basic trading system : player 1 -> trade controller(server wide) -> player 2 
basic shop system : player -> shop controller(server wide) -> player 2
basic global shop system: server 1 -> global shop(global) -> server 2 #? we do not need this right now 


how the items `might` work:
> short uuids with a prefix of one of these {W, A, T} (https://github.com/skorokithakis/shortuuid)
> first check for prefix then check the required database for item
> making an item is self explanatory

how the server world building might work
> perlin noise to make map -> send to private channel // plain map -> send to private channel ✅
> storing data on a discord channel seems like a good plan ✅
        - save space
        
        - editable and easily accessable
        - reusablity and storing more main components
    > two options
        - save it on a private server [im leaning more towards this] ✅
        - save it on the server the bot is in 

>Rethinking server
        - instead of a single table consisting of all info on the server we could split it up into multiple tables
"""

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_or_fetch_player(self, userid) -> Player:
        cur = await self.bot.ecoBase.cursor()
        query = await cur.execute("SELECT * FROM profiles WHERE id = ?", (userid,))
        query = await query.fetchone()

        if not query:
            await cur.execute(f"INSERT INTO profiles VALUES(?, 0, 'None', 'None', 100, 0)", (userid,))
            await self.bot.ecoBase.commit()
            query = (userid,  0, "None",'None', 100, 'None', 0)
        return Player(userid, query[1], query[2], query[3], query[4], query[5], self.bot)
    
    async def create_or_fetch_server(self, serverid) -> Server:
        cur = await self.bot.ecoBase.cursor()
        result = await cur.execute("SELECT * FROM servers WHERE id = ?",(serverid,))
        result = await result.fetchone()
        
        if not result:
            await cur.execute("INSERT INTO servers VALUES(?, 0, 0, 0)",(serverid,))
            await self.bot.ecoBase.commit()
            result = (serverid, 0, 0, 0)
            returnserver = Server(serverid, result[1], result[2], result[3], self.bot)
            mapid = await returnserver.gen_chunk()
            await returnserver.gen_lootpool(("I-NVWkULk8fzBx2UqjgJLdYp",), (20,))
            result = (serverid, 0, 0, await returnserver.fetch_lootpool(), mapid)
            print(result[3])
        return Server(serverid, result[1], result[2], result[3], self.bot)

    async def fetch_item(self, id):
        cur = await self.bot.ecoBase.cursor()
        result = await cur.execute("SELECT * FROM items WHERE id = ?", (id,))
        result = await result.fetchone()
        return Item(result[0], result[1], result[2], result[3], result[4])
    
    
    @commands.command()
    async def landinfo(self,ctx) -> None:
        server = await self.create_or_fetch_server(ctx.guild.id)
        embed = disnake.Embed(
            title = "You look around you",
            description=
        f"""
                a wonders land of opertunities lay before you
                    your eyes gaze over the lands you find
                        the land named `{ctx.guild.name}`
        """
        )
        if server.bank >= 100: prosperitymessage = prosperity["dire"]["message"]
        elif server.bank >= 200: prosperitymessage = prosperity["poor"]["message"]
        elif server.bank >= 500: prosperitymessage = prosperity["average"]["message"]
        elif server.bank >= 1000: prosperitymessage = prosperity["good"]["message"]
        elif server.bank <= 1000:  prosperitymessage = prosperity["great"]["message"]
        embed.add_field(
            name = "Prosperity",
            value= f"{prosperitymessage} \n the vault contains `{server.bank}`"
        )
        embed.add_field(
            name="The state of the region",
            value = "place holder \n the land level index is `{server.level}`"
        )
        await ctx.send(embed=embed)

    #? here is a fun concept use the items from the players inventory to level up the settlement as the server progress the whole server must give up items to improve the server
    #@commands.command()
    #async def establishcontrol(self, ctx) -> None:
    #    server = await self.create_or_fetch_server(ctx.guild.id)
    #    embed = disnake.Embed(
    #        title=""
    #    )

    @commands.command()
    async def scavenge(self, ctx) -> None:
        
        server = await self.create_or_fetch_server(ctx.guild.id)
        player = await self.create_or_fetch_player(ctx.author.id)
        await server.fetch_lootpool()
        if server.lootpool == None or len(server.lootpool) == 0:
            return await ctx.send("The land is barren try again later")
        item = random.choice(server.lootpool)
        num = random.randint(0, server.lootpool.count(item))
        
        if num == 0:
            return await ctx.send(embed = disnake.Embed(title="you found nothing"))
        
        await player.add_item(item.id, num)
        embed = disnake.Embed(
            title = "You scavenged around the land",
            description= f"You found {num} {item.name}!"
        )
        
        await ctx.send(embed = embed)

    @commands.command(hidden=True)
    async def genlootpool(self,ctx ,*, items:list() = ("I-NVWkULk8fzBx2UqjgJLdYp",), number:list() = (20,)) -> None: 
        server = await self.create_or_fetch_server(ctx.guild.id)
        await server.gen_lootpool(items, number)
        await ctx.send("loot pool generated")
    
    @commands.command(hidden=True)
    async def dirlootpool(self, ctx )-> None:
        server = await self.create_or_fetch_server(ctx.guild.id)
        await ctx.send(await server.fetch_lootpool())

    async def dirinv(self, player) -> None:
        items = await player.fetch_inv()
        embed = disnake.Embed(
            title= "Bag",
            description="this bag contains the following"
        )
        itemval = ""
        for item in items:
            if item.name in itemval: continue
            itemval += f"**{item.name}** : `{items.count(item)}`\n"
            
        embed.add_field(
            name= "items",
            value= 
            f"""
            {itemval}            
            """
        )
        return embed

    @commands.command()
    async def profile(self, ctx) -> None:
        player = await self.create_or_fetch_player(ctx.author.id)
        differitems = 0
        totalitems = 0
        await player.fetch_inv()
        if player.items:
            seen = set()
            for item in player.items:
                if item in seen:
                    continue
                seen.add(item)
            differitems = len(seen)
            totalitems = len(player.items)
            
        
        embed = disnake.Embed(
            title = f"{ctx.author.display_name}'s profile"
        ).set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_field(
            name="Money",
            value=
            f"""
            Wallet: `{player.wallet}`
            Bank: `{player.bank}`
            """
        )
        embed.add_field(
            name="Inventory",
            value= 
            f"""
            `{differitems}` different items | total(`{totalitems}`)
            """ 
        )
        playerinv = await self.dirinv(player)
        await ctx.send(embed=embed, view=ProfileDropdownView(ctx, [embed, playerinv]))

    @commands.command()
    async def inventory(self, ctx) -> None:
        player: Player = await self.create_or_fetch_player(ctx.author.id)
        items = await player.fetch_inv()
        if len(items) == 0:
            return await ctx.send(disnake.Embed(title="No items in bag"))
        embed = await self.dirinv(player)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Economy(bot))
