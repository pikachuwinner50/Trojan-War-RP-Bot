from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from .settlements.commands import (
    AdminCommands,
    BuildCommands,
    MilitaryCommands,
    NationCommands,
    ReligionCommands,
    SettlementCommands,
    TurnCommands,
)
from .settlements.store import SettlementStore


class TrojanWarBot(commands.Bot):
    def __init__(self, *, data_path: Path, guild_id: int | None) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.data_path = data_path
        self.guild_id = guild_id
        self.settlement_store = SettlementStore(
            data_path / "settlements.json",
            data_path / "action_queue.json",
        )

    async def setup_hook(self) -> None:
        self.tree.add_command(NationCommands(self.settlement_store))
        self.tree.add_command(SettlementCommands(self.settlement_store))
        self.tree.add_command(BuildCommands(self.settlement_store))
        self.tree.add_command(ReligionCommands(self.settlement_store))
        self.tree.add_command(MilitaryCommands(self.settlement_store))
        self.tree.add_command(TurnCommands(self.settlement_store))
        self.tree.add_command(AdminCommands(self.settlement_store))

        if self.guild_id is not None:
            guild = discord.Object(id=self.guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logging.info("Synced %s guild slash commands.", len(synced))
            return

        synced = await self.tree.sync()
        logging.info("Synced %s global slash commands.", len(synced))

    async def on_ready(self) -> None:
        logging.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "unknown")


def build_bot() -> TrojanWarBot:
    load_dotenv()

    guild_id_raw = os.getenv("DISCORD_GUILD_ID", "").strip()
    guild_id = int(guild_id_raw) if guild_id_raw else None

    data_path = Path(os.getenv("DATA_DIR", "data"))
    return TrojanWarBot(data_path=data_path, guild_id=guild_id)


async def run_bot() -> None:
    bot = build_bot()
    token = os.getenv("DISCORD_TOKEN", "").strip()

    if not token:
        raise RuntimeError("DISCORD_TOKEN is missing. Add it to your .env file.")

    async with bot:
        await bot.start(token)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    asyncio.run(run_bot())
