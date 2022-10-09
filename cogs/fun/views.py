"""This file contains all the views that are required by the cog."""
import aiosqlite
import disnake
from disnake.ext import commands
from disnake.ui import Button, View, button


class Truthordare(View):
    """The view of Truth or dare command."""

    def __init__(self, ctx, bot, timeout: float = 180):
        """Init of the view."""
        self.ctx: commands.Context = ctx
        self.bot: commands.bot = bot
        super().__init__(timeout=timeout)

    async def on_timeout(self) -> None:
        """To make sure the bot doesnt listen to unused views."""
        for child in self.children:
            self.remove_item(child)
        self.stop()

    async def interaction_check(self, interaction) -> bool:
        """To make sure the interactiee is the same as the author."""
        if interaction.author != self.ctx.author:
            return False
        return True

    async def get_question(self, type: str) -> disnake.Embed:
        """Get a question/dare from the fun.db file."""
        cur: aiosqlite.Cursor = await self.bot.fundb.cursor()
        cur = await cur.execute(
            "SELECT * FROM tord WHERE type = ? ORDER BY RANDOM();", (type,)
        )
        cur = await cur.fetchone()
        color = disnake.Color.gold()
        if type == "Truth":
            color = disnake.Color.greyple()
        return disnake.Embed(title=cur[1], color=color)

    @button(label="Truth", style=disnake.ButtonStyle.secondary, emoji="🤫")
    async def truth(
        self, button: Button, interaction: disnake.MessageInteraction
    ) -> None:
        """For the user to get a question."""
        return await interaction.response.edit_message(
            embed=await self.get_question("Truth")
        )

    @button(label="Dare", style=disnake.ButtonStyle.secondary, emoji="👟")
    async def dare(
        self, button: Button, interaction: disnake.MessageInteraction
    ) -> None:
        """For the user to get a dare command."""
        return await interaction.response.edit_message(
            embed=await self.get_question("Dare")
        )
