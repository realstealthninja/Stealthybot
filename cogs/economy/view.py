import disnake
from disnake.ext import commands


class ProfileDropdown(disnake.ui.Select):
    def __init__(self, ctx:commands.Context, embeds):
        self.ctx = ctx
        self.embeds = embeds
        options = [
            disnake.SelectOption(
                label = "Home",
                description= "Return to main menu",
                emoji= "🏠"
            ),
            disnake.SelectOption(
                label = "Inventory",
                description= "Inventory of the player",
                emoji = "🎒"
            )
        ]
        super().__init__(
            placeholder= "Choose a catagory.",
            min_values = 1,
            max_values = 1,
            options= options
        )
    
    async def callback(self, interaction: disnake.MessageInteraction):
        label = interaction.values[0]

        match label:
            case "Home":
                return await interaction.response.edit_message(embed=self.embeds[0])
            case "Inventory":
                return await interaction.response.edit_message(embed=self.embeds[1])


class ProfileDropdownView(disnake.ui.View):
    def __init__(self,ctx, embeds):
        super().__init__(timeout=None)
        self.add_item(ProfileDropdown(ctx, embeds))