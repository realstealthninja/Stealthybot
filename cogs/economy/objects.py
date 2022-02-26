import random
from .constants import storageServerId, mapStorageChannelId

def genbasicmap(width, height):
    builtmap = [[r for r in range(width)] for i in range(height)]

    for i in range(0, height):
        for j in range(0, width):
            builtmap[i][j] = 0

    return builtmap


class Item(object):
    def __init__(self, id: str, name: str, easyid: str, cost: int, value: int) -> None:
        self.id = id
        self.name = name
        self.easyid = easyid
        self.cost = cost
        self.value = value

class Server(object):
    def __init__(self, id, level, bank, mapdata, bot) -> None:
        self.bot = bot
        self.id = id
        self.level = level
        self.bank = bank
        self.mapdata = mapdata
        self.lootpool = None

    # TODO: find a way to parse the map then be able to update it

    async def gen_chunk(self):
        noise = genbasicmap(50, 12)
        string = "```"
        for i in noise:
            string += "\n"
            for o in i:
                string += "-"
        string += "\n```"
        message = await self.bot.get_guild(storageServerId).get_channel(mapStorageChannelId).send(string)

        cur = await self.bot.ecoBase.cursor()
        await cur.execute("UPDATE servers SET mapdata = ? WHERE id = ?", (message.id, self.id,))
        await self.bot.ecoBase.commit()
        self.mapdata = message.id
        return message.id

    async def gen_enemypool(self, leveldist: list, enemypool: list = None):
        cur = await self.bot.ecoBase.cursor()
        if enemypool:
            for enemy in enemypool:
                await cur.execute("INSERT INTO enemypool VALUES(?,?,?)", (self.id, enemy, random.randrange(leveldist[0], leveldist[1])))
                return

        for num in range(5):
            await cur.execute("INSERT INTO enemypool VALUES(?,?,?)", (self.id, "2XuyDTUXJHqKtvNH7NJJho", num))

    async def gen_lootpool(self, lootpool: list(), numofitems: list()) -> None:
        cur = await self.bot.ecoBase.cursor()
        if len(lootpool) != len(numofitems):
            raise ValueError
        for (item, number) in zip(lootpool, numofitems):
            await cur.execute("INSERT INTO lootpool VALUES(?,?,?)", (self.id, item, number))
        await self.fetch_lootpool()
        

    async def removeitem(self, itemid, amount):
        cur = await self.bot.ecoBase.cursor()
        result = await cur.execute("SELECT amount FROM lootpool WHERE serverid = ? AND itemid = ?", (self.id, itemid))
        result = result.fetchone()
        if not result:
            return
        if result > amount:
            await cur.execute("DELETE FROM lootpool WHERE serverid = ? AND itemid = ?", (self.id, itemid))
        else:
            await cur.execute("UPDATE lootpool SET amount = ?  WHERE itemid = ? AND serverid = ?", (amount, itemid, self.id))
        await self.fetch_lootpool()

    async def fetch_item(self, id: int) -> Item:
        cur = await self.bot.ecoBase.cursor()
        result = await cur.execute("SELECT * FROM items WHERE id = ?", (id,))
        result = await result.fetchone()
        return Item(result[0], result[1], result[2], result[3], result[4])
    
    async def fetch_lootpool(self) -> list():
        items: list() = []
        async with self.bot.ecoBase.execute("SELECT * FROM lootpool WHERE serverid = ?", (self.id,)) as cur:
            async for row in cur:
                for amount in range(row[2]):
                    items.append(await self.fetch_item(row[1]))
                    
        self.lootpool = items
        return items
    
    async def imp_map(self):
        pass  # TODO:





class Player(object):
    def __init__(self, id, bank, wallet, health, armor, serverid, bot) -> None:
        self.id: int = id
        self.bank: int = bank
        self.wallet: int = wallet
        self.serverid: int  = serverid
        self.health: int = health
        self.armor: str  = armor
        self.bot = bot
        self.items: list() = None

    async def add_money(self, money: int, place):
        cur = await self.bot.db.cursor()
        if place == "wallet":
            self.wallet += money
            await cur.execute(f"UPDATE profiles SET {place} = ? WHERE id = ?", (self.wallet, self.id,))
        if place == "bank":
            self.bank += money
            await cur.execute(f"UPDATE profiles SET {place} = ? WHERE id = ?", (self.bank, self.id,))
        await self.bot.db.commit()

    async def remove_money(self, money: int, place):
        cur = await self.bot.db.cursor()
        if place == "wallet":
            self.wallet -= money
            await cur.execute(f"UPDATE profiles SET {place} = ? WHERE id = ?", (self.wallet, self.id,))
        if place == "bank":
            self.bank -= money
            await cur.execute(f"UPDATE profiles SET {place} = ? WHERE id = ?", (self.bank, self.id,))
        await self.bot.db.commit()

    async def add_citzen(self, serverid: int):
        cur = await self.bot.db.cursor()
        self.serverid = serverid
        await cur.execute("UPDATE profiles SET serverid = ? WHERE id = ?", (self.serverid, self.id))
        await self.bot.db.commit()

    async def remove_citzen(self):
        cur = await self.bot.db.cursor()
        self.serverid = 0
        await cur.execute("UPDATE profiles SET serverid = ? WHERE id = ?", (self.serverid, self.id))

    async def add_health(self, value: int):
        cur = await self.bot.db.cursor()
        self.health += value
        await cur.execute("UPDATE profiles SET health = ? WHERE id = ? ", (self.health, self.id))

    async def decrease_health(self, value: int):
        cur = await self.bot.db.cursor()
        self.health -= value
        await cur.execute("UPDATE profiles SET health = ? WHERE id = ? ", (self.health, self.id))

    async def fetch_inv(self) -> list():
        items:list() = []
        async with self.bot.ecoBase.execute("SELECT * FROM inventory WHERE playerid = ?", (self.id,)) as cur:
            async for row in cur:
                for amount in range(row[2]):
                    items.append(await self.fetch_item(row[1]))
        self.items = items
        return items

    async def fetch_item(self, id: int) -> Item:
        cur = await self.bot.ecoBase.cursor()
        result = await cur.execute("SELECT * FROM items WHERE id = ?", (id,))
        result = await result.fetchone()
        return Item(result[0], result[1], result[2], result[3], result[4])

    async def add_item(self, itemid, amount: int) -> None:
        cur = await self.bot.ecoBase.cursor()
        result = await cur.execute("SELECT amount FROM inventory WHERE playerid = ? AND itemid = ?", (self.id, itemid))
        result = await result.fetchone()

        if not result:
            await cur.execute("INSERT INTO inventory VALUES(?,?,?)", (self.id, itemid, amount))
        else:
            await cur.execute("UPDATE inventory SET amount = ? WHERE itemid = ? AND playerid = ?", (amount + result[0], itemid, self.id))
        await self.fetch_inv()
    
    async def remove_item(self, itemid, amount: int):
        cur = await self.bot.ecoBase.cursor()
        result = await cur.execute("SELECT amount FROM inventory WHERE playerid = ? AND itemid = ?", (self.id, itemid))
        result = result.fetchone()
        if not result:
            return
        if result > amount:
            await cur.execute("DELETE FROM inventory WHERE playerid = ? AND itemid = ?", (self.id, itemid))
        else:
            await cur.execute("UPDATE inventory SET amount = ?  WHERE itemid = ? AND playerid = ?", (amount - result[0], itemid, self.id))
        await self.fetch_inv()

class enemy(object):
    def __init__(self, easyid, health, basedmg, weapon, description, drops, level, bot) -> None:
        self.id = id
        self.easyid = easyid
        self.level = level
        self.health = health
        self.basedmg = basedmg
        self.weapon = weapon
        self.description = description
        self.drops = drops
        self.bot = bot

    async def attack(self, player: Player):
        await player.decrease_health(self.basedmg)


class weapon(object):
    def __init__(self) -> None:
        # TODO:
        pass


class armor(object):
    def __init__(self) -> None:
        # TODO:
        pass


class tools(object):
    def __init__(self) -> None:
        # TODO:
        pass
