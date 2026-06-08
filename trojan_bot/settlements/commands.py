from __future__ import annotations

import discord
from discord import app_commands

from .catalog import BUILDINGS
from .capitals import UNKNOWN_CAPITAL_NATIONS
from .formatting import buildings_embed, end_turn_embed, queue_embed, settlement_embed
from .military import UNITS
from .models import RESOURCE_LABELS, RESOURCE_NAMES
from .nations import nations_for_culture
from .religion import DEITIES
from .store import SettlementStore
from .views import NationView


def _store(interaction: discord.Interaction) -> SettlementStore:
    return interaction.client.settlement_store


def _is_moderator(interaction: discord.Interaction) -> bool:
    permissions = interaction.user.guild_permissions
    return permissions.manage_guild or permissions.manage_messages or permissions.administrator


async def nation_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    current_key = current.lower()
    culture = getattr(interaction.namespace, "culture", None)
    nations = nations_for_culture(culture) if culture else _store(interaction).list_allowed_nations()
    return [
        app_commands.Choice(name=nation, value=nation)
        for nation in nations
        if current_key in nation.lower()
    ][:25]


async def culture_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    current_key = current.lower()
    return [
        app_commands.Choice(name=culture, value=culture)
        for culture in _store(interaction).list_allowed_cultures()
        if current_key in culture.lower()
    ][:25]


async def building_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    current_key = current.lower()
    choices = [app_commands.Choice(name="Citadel", value="citadel")]

    choices.extend(
        app_commands.Choice(name=f"{definition.name} ({definition.key})", value=definition.key)
        for definition in BUILDINGS.values()
        if current_key in definition.key.lower() or current_key in definition.name.lower()
    )
    return choices[:25]


async def deity_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    current_key = current.lower()
    return [
        app_commands.Choice(name=deity.name, value=key)
        for key, deity in DEITIES.items()
        if current_key in key or current_key in deity.name.lower()
    ][:25]


async def resource_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    current_key = current.lower()
    return [
        app_commands.Choice(name=RESOURCE_LABELS[key], value=key)
        for key in RESOURCE_NAMES
        if current_key in key or current_key in RESOURCE_LABELS[key].lower()
    ][:25]


async def unit_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    current_key = current.lower()
    return [
        app_commands.Choice(name=unit.name, value=key)
        for key, unit in UNITS.items()
        if current_key in key or current_key in unit.name.lower()
    ][:25]


class NationCommands(app_commands.Group):
    def __init__(self, store: SettlementStore) -> None:
        super().__init__(name="nation", description="Create and inspect player nations.")
        self.store = store

    @app_commands.command(name="claim", description="Claim one nation as your faction.")
    @app_commands.describe(
        culture="Choose your culture group first.",
        nation="Choose one nation from that culture.",
    )
    @app_commands.autocomplete(culture=culture_autocomplete, nation=nation_autocomplete)
    async def claim(self, interaction: discord.Interaction, culture: str, nation: str) -> None:
        try:
            settlement = self.store.create_nation(interaction.user.id, culture, nation)
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        await interaction.response.send_message(
            f"{interaction.user.mention} claimed **{settlement.nation}**.",
            embed=settlement_embed(settlement),
            view=NationView(settlement),
            ephemeral=True,
        )

    @app_commands.command(name="mine", description="View your nation.")
    async def mine(self, interaction: discord.Interaction) -> None:
        settlement = self.store.get_by_owner(interaction.user.id)

        if settlement is None:
            await interaction.response.send_message("You do not have a nation yet. Use `/nation claim`.", ephemeral=True)
            return

        await interaction.response.send_message(embed=settlement_embed(settlement), view=NationView(settlement), ephemeral=True)

    @app_commands.command(name="list", description="List founded player nations.")
    async def list(self, interaction: discord.Interaction) -> None:
        nations = self.store.list_nations()
        text = "\n".join(f"- {nation}" for nation in nations) if nations else "No nations have been founded yet."
        await interaction.response.send_message(text, ephemeral=True)


class SettlementCommands(app_commands.Group):
    def __init__(self, store: SettlementStore) -> None:
        super().__init__(name="settlement", description="Manage your Trojan War RP settlement.")
        self.store = store

    @app_commands.command(name="view", description="View your settlement or another known nation.")
    @app_commands.describe(nation="Optional nation to inspect. Leave blank for your nation.")
    @app_commands.autocomplete(nation=nation_autocomplete)
    async def view(self, interaction: discord.Interaction, nation: str | None = None) -> None:
        settlement = self.store.get_for_user(interaction.user.id, nation)

        if settlement is None:
            await interaction.response.send_message("No settlement found. Use `/nation claim` first.", ephemeral=True)
            return

        await interaction.response.send_message(embed=settlement_embed(settlement), view=NationView(settlement), ephemeral=True)

    @app_commands.command(name="buildings", description="List your building catalog and current tiers.")
    async def buildings(self, interaction: discord.Interaction) -> None:
        settlement = self.store.get_by_owner(interaction.user.id)

        if settlement is None:
            await interaction.response.send_message("You do not have a nation yet. Use `/nation claim`.", ephemeral=True)
            return

        await interaction.response.send_message(embed=buildings_embed(settlement), ephemeral=True)


class BuildCommands(app_commands.Group):
    def __init__(self, store: SettlementStore) -> None:
        super().__init__(name="build", description="Queue settlement construction for the turn.")
        self.store = store

    @app_commands.command(name="queue", description="Queue a building or Citadel upgrade.")
    @app_commands.describe(building="Building to construct or upgrade.")
    @app_commands.autocomplete(building=building_autocomplete)
    async def queue(self, interaction: discord.Interaction, building: str) -> None:
        try:
            action = self.store.queue_building(interaction.user.id, building)
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        await interaction.response.send_message(
            f"Queued **{action.target}** to tier **{action.next_level}** for the next `/turn end`.",
            ephemeral=True,
        )


class ReligionCommands(app_commands.Group):
    def __init__(self, store: SettlementStore) -> None:
        super().__init__(name="religion", description="Queue sacrifices and inspect divine favor.")
        self.store = store

    @app_commands.command(name="sacrifice", description="Queue an offering to an Olympian deity.")
    @app_commands.describe(
        deity="Olympian deity receiving the offering.",
        resource="Resource to sacrifice.",
        amount="Amount of that resource to sacrifice.",
    )
    @app_commands.autocomplete(deity=deity_autocomplete, resource=resource_autocomplete)
    async def sacrifice(self, interaction: discord.Interaction, deity: str, resource: str, amount: int) -> None:
        try:
            action = self.store.queue_sacrifice(interaction.user.id, deity, resource, amount)
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        await interaction.response.send_message(
            f"Queued sacrifice to **{DEITIES[action.target].name}**: {amount:,} {RESOURCE_LABELS[resource]}.",
            ephemeral=True,
        )


class MilitaryCommands(app_commands.Group):
    def __init__(self, store: SettlementStore) -> None:
        super().__init__(name="military", description="Queue recruitment and inspect army status.")
        self.store = store

    @app_commands.command(name="recruit", description="Queue unit recruitment for the turn.")
    @app_commands.describe(unit="Unit type to recruit.", quantity="Number of units to recruit.")
    @app_commands.autocomplete(unit=unit_autocomplete)
    async def recruit(self, interaction: discord.Interaction, unit: str, quantity: int) -> None:
        try:
            action = self.store.queue_recruitment(interaction.user.id, unit, quantity)
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        await interaction.response.send_message(
            f"Queued **{quantity:,} {UNITS[action.target].name}** for recruitment.",
            ephemeral=True,
        )


class TurnCommands(app_commands.Group):
    def __init__(self, store: SettlementStore) -> None:
        super().__init__(name="turn", description="Inspect or resolve the turn queue.")
        self.store = store

    @app_commands.command(name="queue", description="View queued actions.")
    async def queue(self, interaction: discord.Interaction) -> None:
        actions = self.store.list_queue()
        await interaction.response.send_message(embed=queue_embed(actions), ephemeral=True)

    @app_commands.command(name="end", description="GM: resolve passive generation and queued actions.")
    async def end(self, interaction: discord.Interaction) -> None:
        if not _is_moderator(interaction):
            await interaction.response.send_message("Only moderators can end the turn.", ephemeral=True)
            return

        result = self.store.end_turn()
        await interaction.response.send_message(embed=end_turn_embed(result))


class AdminCommands(app_commands.Group):
    def __init__(self, store: SettlementStore) -> None:
        super().__init__(name="admin", description="Moderator controls for campaign setup.")
        self.store = store

    @app_commands.command(name="reset_claims", description="Mods: clear all claimed factions and queued actions.")
    async def reset_claims(self, interaction: discord.Interaction) -> None:
        if not _is_moderator(interaction):
            await interaction.response.send_message("Only moderators can reset claims.", ephemeral=True)
            return

        count = self.store.reset_claims()
        await interaction.response.send_message(f"Cleared **{count}** claimed faction(s) and the turn queue.", ephemeral=True)

    @app_commands.command(name="unclaim", description="Mods: clear one claimed faction.")
    @app_commands.describe(nation="Claimed nation to clear.")
    @app_commands.autocomplete(nation=nation_autocomplete)
    async def unclaim(self, interaction: discord.Interaction, nation: str) -> None:
        if not _is_moderator(interaction):
            await interaction.response.send_message("Only moderators can unclaim factions.", ephemeral=True)
            return

        try:
            settlement = self.store.unclaim_nation(nation)
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        await interaction.response.send_message(f"Cleared the claim on **{settlement.nation}**.", ephemeral=True)

    @app_commands.command(name="missing_capitals", description="Mods: list factions that still need assigned capitals.")
    async def missing_capitals(self, interaction: discord.Interaction) -> None:
        if not _is_moderator(interaction):
            await interaction.response.send_message("Only moderators can view missing capital assignments.", ephemeral=True)
            return

        text = "\n".join(f"- {nation}" for nation in UNKNOWN_CAPITAL_NATIONS)
        await interaction.response.send_message(
            f"Factions with no confirmed capital yet:\n{text}",
            ephemeral=True,
        )
