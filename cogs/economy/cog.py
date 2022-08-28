import random
import disnake


from disnake.ext import commands

from stealthybot.bot import Stealthybot
from . import ProfileDropdownView

from .objects import Item, Player, Server
from .constants import PROSPERITY


class Economy(commands.Cog, name="economy"):
    """
    economy cog contains the economy commands
    """

    def __init__(self, bot):
        self.bot: Stealthybot = bot

    async def create_or_fetch_player(self, user_id: int) -> Player:
        """
        Creates or fetches player from
        the database.

        Parameters
        ----------
        user_id: :class:`int`
            The user id.

        Returns
        -------
        :class:`Player`
        """

        cur = await self.bot.eco_base.cursor()
        query = await cur.execute("SELECT * FROM profiles WHERE id = ?", (user_id,))
        query = await query.fetchone()

        if not query:
            await cur.execute(
                "INSERT INTO profiles VALUES(?, 0, 0, 100, 0, 0)", (user_id,)
            )
            await self.bot.eco_base.commit()
            query = (user_id, 0, "None", 100, 100, "None", 0)
        return Player(user_id, query[1], query[2], query[3], query[4], query[5], self.bot)

    async def create_or_fetch_server(self, guild_id: int) -> Server:
        """
        Creates or Fetchs the server from the data base.

        Parameters
        ----------
        guild_id: :class:`int`
            The server id.

        Returns
        -------
        :class:`Server`
        """
        cur = await self.bot.eco_base.cursor()
        result = await cur.execute("SELECT * FROM servers WHERE id = ?", (guild_id,))
        result = await result.fetchone()
        if not result:
            await cur.execute("INSERT INTO servers VALUES(?, 0, 0, 0)", (guild_id,))
            await self.bot.eco_base.commit()
            result = (guild_id, 0, 0, 0)
            returnserver = Server(guild_id, result[1], result[2], result[3], self.bot)
            mapid = await returnserver.gen_chunk()
            await returnserver.gen_lootpool(("I-NVWkULk8fzBx2UqjgJLdYp",), (20,))
            result = (guild_id, 0, 0, await returnserver.fetch_lootpool(), mapid)
            print(result[3])
        return Server(guild_id, result[1], result[2], result[3], self.bot)

    async def fetch_item(self, id: str) -> Item:
        """Fetches an item based on its id

        Parameters
        ----------
        id: :class:`int`
            The id of the item required.

        Returns
        -------
        :class:`Item`
        """
        cur = await self.bot.eco_base.cursor()
        result = await cur.execute("SELECT * FROM items WHERE id = ?", (id,))
        result = await result.fetchone()
        return Item(result[0], result[1], result[2], result[3], result[4], result[5])

    @commands.command()
    async def landinfo(self, ctx: commands.Context) -> None:
        """Shows the details about the server"""
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
            message = PROSPERITY["dire"]["message"]
        elif server.bank <= 200:
            message = PROSPERITY["poor"]["message"]
        elif server.bank <= 500:
            message = PROSPERITY["average"]["message"]
        elif server.bank <= 1000:
            message = PROSPERITY["good"]["message"]
        elif server.bank >= 1000:
            message = PROSPERITY["great"]["message"]
        embed.add_field(
            name="PROSPERITY",
            value=f"{message} \n the vault contains `{server.bank}`",
        )
        embed.add_field(
            name="The state of the region",
            value=f"place holder \n the land level index is `{server.level}`",
        )
        await ctx.send(embed=embed)

    # ? here is a fun concept use the items from the players inventory to level up the settlement as the server progress the whole server must give up items to improve the server

    @commands.command()
    async def scavenge(self, ctx: commands.Context) -> None:
        """Scavenges for items in the area"""
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
        ctx: commands.Context,
        *,
        items: list = ("I-NVWkULk8fzBx2UqjgJLdYp",),
        number: list = (20,),
    ) -> None:
        """generates loot pool for the server"""
        server = await self.create_or_fetch_server(ctx.guild.id)
        await server.gen_lootpool(items, number)
        await ctx.send("loot pool generated")

    @commands.command(hidden=True)
    async def dirlootpool(self, ctx: commands.Context) -> None:
        """Displays the loot pool of the server"""
        server = await self.create_or_fetch_server(ctx.guild.id)
        await ctx.send(await server.fetch_lootpool())

    async def dirinv(self, player: Player) -> None:
        """Generate display of the inventory"""
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
        """Shows your current inventory"""
        player = await self.create_or_fetch_player(ctx.author.id)
        embed = await self.dirinv(player)
        await ctx.send(embed=embed)

    @commands.command()
    async def shop(self, ctx: commands.Context, *, itemfilter: str = None):
        """Displays the shop menu"""
        server = await self.create_or_fetch_server(ctx.guild.id)

        shop = await server.fetch_shop_item_wise()

        main = disnake.Embed(
            title="Shop Menu",
            description="Welcome to the baazar of the land! \n here the people sell and buy supplies",
        )
        main_body = "\n"
        if not itemfilter:
            for count, items in enumerate(shop):

                key = list(items.keys())[0]

                item = await server.fetch_item(key)
                itemname = item.name + item.emoji
                user = ctx.guild.get_member(items[key]["user"])
                main_body += f"{count}) |**{itemname} | {items[key]['amount']} | {items[key]['cost']} <:stealthycoin:897331306013286440> |** {user.mention} \n"
        else:
            item = await server.fetch_item_by_name(itemfilter)
            item = item.id
            shop = await server.fetch_shop_item_wise(item)
            if not shop:
                main_body += "***Could not find items with your specific filters***"
            for count, items in enumerate(shop):
                key = list(items.keys())[0]

                item = await server.fetch_item(key)
                itemname = item.name + item.emoji
                user = ctx.guild.get_member(items[key]["user"])
                main_body += f"{count}) |**{itemname} | {items[key]['amount']} | {items[key]['cost']} <:stealthycoin:897331306013286440> |** {user.mention} \n"

        main.add_field(name="Items currently on the market", value=main_body)
        await ctx.send(embed=main)

    @commands.command()
    async def sell(self, ctx: commands.Context, amount: int, cost: int, *, item: str):
        """Sell an item on the server market"""
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
    async def profile(self, ctx: commands.Context, member: disnake.Member = None) -> None:
        """Displays the profile of you or the person mentioned"""
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
    async def share(
        self, ctx: commands.Context, user: disnake.Member, amount: int, *, item: str
    ) -> None:
        """Share an item with another user"""
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


def setup(bot: Stealthybot):
    """
    Sets up the economy cog.

    Parameters
    ----------
    bot: :class:`Stealthybot`
        The bot instance to add the
        cog to.
    """
    bot.add_cog(Economy(bot))
