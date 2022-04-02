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
            await cur.execute(
                f"INSERT INTO profiles VALUES(?, 0, 0, 100, 0, 0)", (userid,)
            )
            await self.bot.ecoBase.commit()
            query = (userid, 0, "None", 100, 100, "None", 0)
        return Player(
            userid, query[1], query[2], query[3], query[4], query[5], self.bot
        )

    async def create_or_fetch_server(self, serverid) -> Server:
        cur = await self.bot.ecoBase.cursor()
        result = await cur.execute("SELECT * FROM servers WHERE id = ?", (serverid,))
        result = await result.fetchone()

        if not result:
            await cur.execute("INSERT INTO servers VALUES(?, 0, 0, 0)", (serverid,))
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
    async def landinfo(self, ctx) -> None:
        server = await self.create_or_fetch_server(ctx.guild.id)
        embed = disnake.Embed(
            title="You look around you",
            description=f"""
                a wonders land of opertunities lay before you
                    your eyes gaze over the lands you find
                        the land named `{ctx.guild.name}`
        """,
        )
        if server.bank <= 100:
            prosperitymessage = prosperity["dire"]["message"]
        elif server.bank <= 200:
            prosperitymessage = prosperity["poor"]["message"]
        elif server.bank <= 500:
            prosperitymessage = prosperity["average"]["message"]
        elif server.bank <= 1000:
            prosperitymessage = prosperity["good"]["message"]
        elif server.bank >= 1000:
            prosperitymessage = prosperity["great"]["message"]
        embed.add_field(
            name="Prosperity",
            value=f"{prosperitymessage} \n the vault contains `{server.bank}`",
        )
        embed.add_field(
            name="The state of the region",
            value=f"place holder \n the land level index is `{server.level}`",
        )
        await ctx.send(embed=embed)

    # ? here is a fun concept use the items from the players inventory to level up the settlement as the server progress the whole server must give up items to improve the server
    # @commands.command()
    # async def establishcontrol(self, ctx) -> None:
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
        rawpool = await server.fetch_raw_lootpool()
        if rawpool.count(item.id) == 1:
            num = [random.randint(0, 1)]
        else:
            pool = [
                0,
                random.randint(1, round(rawpool.count(item.id) / 2)),
                rawpool.count(item.id),
            ]
            num = random.choices(pool, weights=[1, 5, 0.5], k=1)
        if num[0] == 0:
            return await ctx.send(embed=disnake.Embed(title="you found nothing"))

        await server.removeitem(item.id, num[0])

        await player.add_item(item.id, num[0])
        embed = disnake.Embed(
            title="You scavenged around the land",
            description=f"You found **{num[0]} {item.name}** {item.emoji}",
        )
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def genlootpool(
        self,
        ctx,
        *,
        items: list() = ("I-NVWkULk8fzBx2UqjgJLdYp",),
        number: list() = (20,),
    ) -> None:
        server = await self.create_or_fetch_server(ctx.guild.id)
        await server.gen_lootpool(items, number)
        await ctx.send("loot pool generated")

    @commands.command(hidden=True)
    async def dirlootpool(self, ctx) -> None:
        server = await self.create_or_fetch_server(ctx.guild.id)
        await ctx.send(await server.fetch_lootpool())

    async def dirinv(self, player: Player) -> None:
        items: list = await player.fetch_inv()
        embed = disnake.Embed(
            title="Bag",
            description="This is your inventory. your items are stored here.\n good luck traveller",
        )
        itemval = ""
        rawpool = await player.fetch_raw_inv()
        for item in items:
            if item.name in itemval:
                continue
            itemval += f"**{item.name}** {item.emoji} ***{rawpool.count(item.id)}***\n"

        if itemval == "":
            itemval = "No items in inventory!"
        embed.add_field(
            name="Items:",
            value=f"""
            {itemval}            
            """,
        )
        return embed

    @commands.command(aliases=["inv", "bag"])
    async def inventory(self, ctx: commands.Context) -> None:
        player = await self.create_or_fetch_player(ctx.author.id)
        embed = await self.dirinv(player)
        await ctx.send(embed=embed)

    @commands.command()
    async def shop(self, ctx: commands.Context):
        server = await self.create_or_fetch_server(ctx.guild.id)

        shop = await server.fetch_shop_item_wise()

        main = disnake.Embed(
            title="Shop Menu",
            description="Welcome to the baazar of the land! \n here the people sell and buy supplies",
        )
        main_body = "\n"
        for items in shop:

            key = list(items.keys())[0]

            item = await server.fetch_item(key)
            itemname = item.name + item.emoji
            user = ctx.guild.get_member(items[key]["user"])
            main_body += f"**{itemname} | {items[key]['amount']} | {items[key]['cost']} <:stealthycoin:897331306013286440> |** {user.mention} \n"
        main.add_field(name="Items currently on the market", value=main_body)
        await ctx.send(embed=main)

    @commands.command()
    async def buy(self, ctx: commands.command):
        pass

    @commands.command()
    async def sell(self, ctx: commands.Context, amount: int, cost: int, *, item: str):
        server = await self.create_or_fetch_server(ctx.guild.id)
        player = await self.create_or_fetch_player(ctx.author.id)

        if amount == 0:
            return await ctx.send("you cant sell 0 items!!!")

        await player.fetch_inv()
        inv = await player.fetch_raw_inv()

        item = await player.fetch_item_by_name(item)
        if not item:
            return await ctx.send("could not find the item")

        if inv.count(item.id) < amount:
            return await ctx.send(f" Not enough {item.name} {item.emoji} to sell")

        await player.remove_item(item.id, amount)
        await server.set_item_for_sale(player.id, item.id, amount, cost)
        await ctx.send(
            f"You set {amount} of {item.name} {item.emoji} for {cost} its now in the market! wait for someone to buy it"
        )

    @commands.command()
    async def profile(
        self, ctx: commands.Context, member: disnake.Member = None
    ) -> None:
        if not member:
            member = ctx.author
        player = await self.create_or_fetch_player(member.id)
        differitems = 0
        totalitems = 0
        await player.fetch_inv()
        if player.items:
            seen = set()
            for item in player.items:
                if item.name in seen:
                    continue
                seen.add(item.name)
            differitems = len(seen)
            totalitems = len(player.items)

        embed = disnake.Embed(title=f"{member.display_name}'s profile").set_thumbnail(
            url=member.display_avatar.url
        )
        embed.add_field(
            name="Money",
            value=f"""
            Wallet: `{player.wallet}`
            Bank: `{player.bank}`
            """,
        )
        embed.add_field(
            name="Inventory",
            value=f"""
            `{differitems}` different items | total(`{totalitems}`)
            """,
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

    @commands.command()
    async def share(
        self, ctx: commands.Context, user: disnake.Member, amount: int, *, item: str
    ) -> None:
        giver = await self.create_or_fetch_player(ctx.author.id)
        reciver = await self.create_or_fetch_player(user.id)

        await giver.fetch_inv()
        await reciver.fetch_inv()

        shareitem = await giver.fetch_item_by_name(item)
        if not shareitem or not await giver.check_for_item(shareitem.id):
            return await ctx.send("could not find the Item")
        raw_inv = await giver.fetch_raw_inv()
        numofitems = raw_inv.count(shareitem.id)
        if numofitems < amount:
            return await ctx.send(
                f" You have `{raw_inv.count(shareitem.id)}` {shareitem.name}"
            )

        await giver.remove_item(shareitem.id, amount)
        await reciver.add_item(shareitem.id, amount)

        await ctx.send(f"you gave {user.mention} {amount} {shareitem.name}")


def setup(bot):
    bot.add_cog(Economy(bot))
