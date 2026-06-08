from __future__ import annotations

import discord

from .formatting import military_embed, religion_embed, resources_embed, settlement_embed, settlements_embed
from .models import Settlement


class NationView(discord.ui.View):
    def __init__(self, settlement: Settlement) -> None:
        super().__init__(timeout=180)
        self.settlement = settlement

    @discord.ui.button(label="Overview", style=discord.ButtonStyle.primary)
    async def overview(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(embed=settlement_embed(self.settlement), view=self)

    @discord.ui.button(label="Settlements", style=discord.ButtonStyle.secondary)
    async def settlements(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(embed=settlements_embed(self.settlement), view=self)

    @discord.ui.button(label="Military", style=discord.ButtonStyle.secondary)
    async def military(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(embed=military_embed(self.settlement), view=self)

    @discord.ui.button(label="Resources", style=discord.ButtonStyle.secondary)
    async def resources(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(embed=resources_embed(self.settlement), view=self)

    @discord.ui.button(label="Religion", style=discord.ButtonStyle.secondary)
    async def religion(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(embed=religion_embed(self.settlement), view=self)
