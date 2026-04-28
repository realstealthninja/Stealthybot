import logging
import os
from typing import Any
from apexpy.exceptions import ApiKeyNotProvidedError
from disnake import ApplicationCommandInteraction, Embed
from disnake.ext.commands import Cog, Param, slash_command


class Sports(Cog, name="sports"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.rapid_key: str | None = os.getenv("rapidapikey")

    async def _football_get(self, path: str) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        base = "https://free-api-live-football-data.p.rapidapi.com/"
        if not self.rapid_key:
            logging.getLogger("disnake").warning(
                "No rapid api key found unloading sports cog"
            )
            raise ApiKeyNotProvidedError

        async with self.bot.client.get(
            base + path,
            headers={
                "x-rapidapi-key": self.rapid_key,
                "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com",
                "Content-Type": "application/json",
            },
        ) as resp:
            x = await resp.json()
            return x["response"]

    @slash_command(description="Gets the standings of a given league")
    async def standings(
        self,
        interaction: ApplicationCommandInteraction,
        league: int = Param(choices={"Champions League": 42, "Premiere League": 47}),
    ) -> None:
        await interaction.response.defer()
        _leauge = await self._football_get(
            f"football-get-league-detail?leagueid={league}"
        )
        logo = await self._football_get(f"football-get-league-logo?leagueid={league}")
        table = await self._football_get(f"football-get-standing-all?leagueid={league}")

        embed = Embed(title=_leauge["leagues"]["name"])
        embed.set_thumbnail(logo["url"])

        team_standing_str = f"```\n{'Team':^28} : Points\n"
        for team in table["standing"]:
            team_standing_str += f"{team['name']:<28} : {team['pts']}\n"
        team_standing_str += "```"

        embed.description = team_standing_str

        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(Sports(bot))
