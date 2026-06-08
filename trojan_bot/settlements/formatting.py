from __future__ import annotations

import discord

from .catalog import BUILDINGS
from .military import unlocked_units
from .models import CITADEL_TIERS, CITADEL_UPGRADE_COSTS, RESOURCE_LABELS, RESOURCE_NAMES, QueuedAction, Settlement
from .religion import DEITIES, HUBRIS_MODIFIERS, favor_bonus, favor_capacity


def settlement_embed(settlement: Settlement) -> discord.Embed:
    used = used_slots(settlement)
    free = max(0, settlement.free_choice_slots() - used)
    embed = discord.Embed(
        title=f"{settlement.nation}",
        description=(
            f"{settlement.culture} realm under the {settlement.ruler_title}.\n"
            f"Tier {settlement.citadel_tier} {settlement.citadel_name()} | "
            f"{free} of {settlement.free_choice_slots()} building slots open"
        ),
        color=discord.Color.dark_red(),
    )
    embed.set_author(name="Settlement Dashboard")

    embed.add_field(name="Capital", value=f"**{settlement.capital}**", inline=True)
    embed.add_field(name="Population", value=f"**{settlement.population:,}**", inline=True)
    embed.add_field(name="Build Slots", value=slot_bar(used, settlement.free_choice_slots()), inline=True)

    embed.add_field(name="Treasury", value=format_resource_table(settlement.normalized_resources()), inline=True)
    embed.add_field(name="Available", value=format_resource_table(settlement.available_resources()), inline=True)

    pending = {key: value for key, value in settlement.normalized_pending_resources().items() if value}
    embed.add_field(
        name="Reserved",
        value=format_resource_table(pending) if pending else "None",
        inline=True,
    )

    embed.add_field(name="Passive Income", value=format_production(settlement), inline=False)
    embed.add_field(name="Military", value=format_military_snapshot(settlement), inline=True)
    embed.add_field(name="Religion", value=format_religion_snapshot(settlement), inline=True)
    embed.set_footer(text="Queued builds resolve when a moderator runs /turn end.")
    return embed


def settlements_embed(settlement: Settlement) -> discord.Embed:
    embed = discord.Embed(
        title=f"{settlement.nation} Settlements",
        description="Your realm currently begins with a single capital settlement.",
        color=discord.Color.dark_red(),
    )
    embed.set_author(name="Settlements")
    embed.add_field(name=settlement.capital, value=format_capital_details(settlement), inline=False)
    embed.set_footer(text="More settlements can be added later through expansion or conquest systems.")
    return embed


def resources_embed(settlement: Settlement) -> discord.Embed:
    embed = discord.Embed(
        title=f"{settlement.nation} Resources",
        description="Treasury totals, available funds, and current turn reservations.",
        color=discord.Color.green(),
    )
    embed.set_author(name="Resources")
    embed.add_field(name="Treasury", value=format_resource_table(settlement.normalized_resources()), inline=True)
    embed.add_field(name="Available", value=format_resource_table(settlement.available_resources()), inline=True)
    pending = {key: value for key, value in settlement.normalized_pending_resources().items() if value}
    embed.add_field(name="Reserved", value=format_resource_table(pending) if pending else "None", inline=True)
    embed.add_field(name="Passive Income", value=format_production(settlement), inline=False)
    return embed


def military_embed(settlement: Settlement) -> discord.Embed:
    embed = discord.Embed(
        title=f"{settlement.nation} Military",
        description="Recruitment will depend on military buildings in your capital.",
        color=discord.Color.dark_red(),
    )
    embed.set_author(name="Military")
    rows = [
        format_military_building(settlement, key)
        for key in ("sword_smithy", "spear_muster", "axe_lodge", "club_foundry")
    ]
    embed.add_field(name="Recruitment Infrastructure", value="\n".join(rows), inline=False)
    units = unlocked_units(settlement.buildings)
    embed.add_field(
        name="Unlocked Units",
        value=format_unlocked_units(units) if units else "No units unlocked yet.",
        inline=False,
    )
    embed.add_field(name="Army Ledger", value="Recruitment quantities are not active yet.", inline=False)
    return embed


def religion_embed(settlement: Settlement) -> discord.Embed:
    embed = discord.Embed(
        title=f"{settlement.nation} Religion",
        description="Worship unlocks through the Cult Center building.",
        color=discord.Color.purple(),
    )
    embed.set_author(name="Religion")
    cult_level = settlement.buildings.get("cult_center", 0)
    definition = BUILDINGS["cult_center"]
    tier = definition.tier(cult_level)
    current = tier.name if tier else "No cult center"
    embed.add_field(name="Cult Center", value=f"Current: **{current}**", inline=False)
    embed.add_field(
        name="Favor Storage",
        value=f"Capacity: **{favor_capacity(cult_level):,}**\n{favor_bonus(cult_level)}",
        inline=True,
    )
    embed.add_field(name="Patron", value="No patron god chosen yet.", inline=True)
    deity_lines = format_deity_lines()
    embed.add_field(name="Olympians I", value="\n".join(deity_lines[:6]), inline=False)
    embed.add_field(name="Olympians II", value="\n".join(deity_lines[6:]), inline=False)
    embed.add_field(name="Hubris", value=format_hubris(), inline=False)
    return embed


def buildings_embed(settlement: Settlement) -> discord.Embed:
    embed = discord.Embed(
        title=f"{settlement.nation} Building Planner",
        description=(
            f"Citadel cap: tier {settlement.citadel_tier}. "
            f"Slots used: {used_slots(settlement)}/{settlement.free_choice_slots()}."
        ),
        color=discord.Color.gold(),
    )
    embed.set_author(name="Construction")
    embed.add_field(name="Citadel Upgrade", value=format_citadel(settlement), inline=False)

    for branch in ("Economic", "Administrative", "Religious", "Military"):
        rows = [
            format_building_plan(settlement, definition)
            for definition in BUILDINGS.values()
            if definition.branch == branch
        ]
        embed.add_field(name=branch, value="\n".join(rows), inline=False)

    embed.set_footer(text="Use /build queue building:<key> to reserve resources for this turn.")
    return embed


def queue_embed(actions: list[QueuedAction]) -> discord.Embed:
    embed = discord.Embed(
        title="Turn Queue",
        description="Orders waiting for the next turn resolution.",
        color=discord.Color.blue(),
    )

    if not actions:
        embed.add_field(name="Queued Orders", value="None yet.", inline=False)
        embed.set_footer(text="Use /build queue to add construction.")
        return embed

    for action in actions[:25]:
        embed.add_field(
            name=f"Order #{action.action_id}",
            value=(
                f"Nation: **{action.nation_key.title()}**\n"
                f"Action: **{action_label(action)}**\n"
                f"Cost: {format_cost(action.cost)}"
            ),
            inline=True,
        )

    if len(actions) > 25:
        embed.set_footer(text=f"Showing 25 of {len(actions)} queued orders.")
    else:
        embed.set_footer(text="Orders resolve after passive generation.")
    return embed


def end_turn_embed(result: dict[str, object]) -> discord.Embed:
    processed = result["processed"]
    generated = result["generated"]
    embed = discord.Embed(
        title="Turn Resolved",
        description="Passive generation completed, then queued orders were processed.",
        color=discord.Color.green(),
    )

    generation_lines = []
    for nation_key, resources in generated.items():
        if resources:
            generation_lines.append(f"**{nation_key.title()}**: {format_cost(resources)}")

    action_lines = [f"#{action.action_id} {action_label(action)}" for action in processed[:15]]

    embed.add_field(
        name="Generated",
        value="\n".join(generation_lines) if generation_lines else "No settlements generated resources.",
        inline=False,
    )
    embed.add_field(
        name="Completed Orders",
        value="\n".join(action_lines) if action_lines else "No queued orders.",
        inline=False,
    )
    embed.set_footer(text=f"{len(processed)} order(s) processed.")
    return embed


def format_citadel_short(settlement: Settlement) -> str:
    next_level = settlement.citadel_tier + 1
    cost = CITADEL_UPGRADE_COSTS.get(next_level)

    if cost is None:
        return "**Max tier**"

    return f"Next: tier {next_level}\n{format_cost(cost)}"


def format_capital_details(settlement: Settlement) -> str:
    return (
        f"Citadel: **Tier {settlement.citadel_tier} {settlement.citadel_name()}**\n"
        f"Population: **{settlement.population:,}**\n"
        f"Slots: {slot_bar(used_slots(settlement), settlement.free_choice_slots())}\n"
        f"Buildings:\n{format_building_summary(settlement)}"
    )


def format_citadel(settlement: Settlement) -> str:
    next_level = settlement.citadel_tier + 1
    current_name, slots = CITADEL_TIERS[settlement.citadel_tier]
    cost = CITADEL_UPGRADE_COSTS.get(next_level)

    if cost is None:
        return f"Current: **Tier {settlement.citadel_tier} {current_name}**\nMax tier reached. Slots: {slots}."

    next_name, next_slots = CITADEL_TIERS[next_level]
    return (
        f"Current: **Tier {settlement.citadel_tier} {current_name}** ({slots} slots)\n"
        f"Next: **Tier {next_level} {next_name}** ({next_slots} slots)\n"
        f"Cost: {format_cost(cost)}\n"
        "Key: `citadel`"
    )


def format_resource_table(resources: dict[str, int]) -> str:
    lines = []
    for resource in RESOURCE_NAMES:
        amount = resources.get(resource, 0)
        lines.append(f"{RESOURCE_LABELS[resource]}: **{amount:,}**")
    return "\n".join(lines)


def format_cost(cost: dict[str, int]) -> str:
    if not cost:
        return "No cost"

    return ", ".join(
        f"{amount:,} {RESOURCE_LABELS.get(resource, resource.replace('_', ' ').title())}"
        for resource, amount in cost.items()
    )


def format_production(settlement: Settlement) -> str:
    totals: dict[str, int] = {}
    treasury_level = settlement.buildings.get("treasury", 0)
    yield_bonus = 0.2 if treasury_level >= 3 else 0.1 if treasury_level == 2 else 0.0

    for building_key, level in settlement.buildings.items():
        definition = BUILDINGS.get(building_key)
        tier = definition.tier(level) if definition else None
        if tier is None:
            continue

        for resource, amount in tier.production.items():
            if building_key != "treasury":
                amount = int(amount * (1 + yield_bonus))
            totals[resource] = totals.get(resource, 0) + amount

    return format_cost(totals) if totals else "None yet. Build farms, forestry, quarries, or mines to start producing."


def format_building_summary(settlement: Settlement) -> str:
    if not settlement.buildings:
        return "No buildings yet. Your first two Village slots are open."

    lines = []
    for key, level in settlement.buildings.items():
        definition = BUILDINGS.get(key)
        tier = definition.tier(level) if definition else None
        if definition is None or tier is None:
            lines.append(f"**{key}**: tier {level}")
            continue

        output = f" | +{format_cost(tier.production)} per turn" if tier.production else ""
        effect = f" | {tier.effect}" if tier.effect else ""
        lines.append(f"**{definition.name}**: {tier.name} (tier {level}){output}{effect}")
    return "\n".join(lines)


def format_military_snapshot(settlement: Settlement) -> str:
    units = unlocked_units(settlement.buildings)
    if units:
        return f"{len(units)} unit type(s) unlocked"

    built = [
        BUILDINGS[key].name
        for key in ("sword_smithy", "spear_muster", "axe_lodge", "club_foundry")
        if settlement.buildings.get(key, 0) > 0
    ]
    return "\n".join(built) if built else "No recruitment buildings"


def format_religion_snapshot(settlement: Settlement) -> str:
    level = settlement.buildings.get("cult_center", 0)
    if level == 0:
        return "No cult center"
    tier = BUILDINGS["cult_center"].tier(level)
    return tier.name if tier else f"Tier {level}"


def format_military_building(settlement: Settlement, key: str) -> str:
    definition = BUILDINGS[key]
    level = settlement.buildings.get(key, 0)
    tier = definition.tier(level)
    current = tier.name if tier else "Not built"
    next_tier = definition.tier(level + 1)
    if next_tier is None:
        next_text = "Max tier reached"
    elif level + 1 > settlement.citadel_tier:
        next_text = f"Locked until Citadel tier {level + 1}"
    else:
        next_text = f"Next: {next_tier.name} ({format_cost(next_tier.cost)})"
    return f"**{definition.name}** `{key}` - {current}; {next_text}"


def format_unlocked_units(units) -> str:
    return "\n".join(
        f"**{unit.name}** - {unit.category}"
        for unit in units
    )


def format_deity_lines() -> list[str]:
    return [
        format_deity_line(deity)
        for deity in DEITIES.values()
    ]


def format_deity_line(deity) -> str:
    resource = RESOURCE_LABELS.get(deity.preferred_resource, deity.preferred_resource.title())
    return f"**{deity.name}**: {resource}; {deity.blessing}"


def format_hubris() -> str:
    return "\n".join(
        f"Week {week}: **{modifier}** - {text}"
        for week, (modifier, text) in HUBRIS_MODIFIERS.items()
    )


def format_building_plan(settlement: Settlement, definition) -> str:
    current_level = settlement.buildings.get(definition.key, 0)
    next_level = current_level + 1
    active = definition.tier(current_level)
    next_tier = definition.tier(next_level)

    current_text = active.name if active else "Open"
    if next_tier is None:
        return f"**{definition.name}** `{definition.key}` - {current_text}; [Max]"

    if next_level > settlement.citadel_tier:
        status = f"[Locked] requires Citadel tier {next_level}"
    elif current_level == 0 and used_slots(settlement) >= settlement.free_choice_slots():
        status = "[Full] needs an open slot"
    else:
        missing = missing_resources(settlement, next_tier.cost)
        if missing:
            status = f"[Short] missing {format_cost(missing)}"
        else:
            status = "[Ready]"

    reward = ""
    if next_tier.production:
        reward = f"; yields +{format_cost(next_tier.production)}/turn"
    elif next_tier.effect:
        reward = f"; {next_tier.effect}"

    return (
        f"**{definition.name}** `{definition.key}` - {current_text}; {status}\n"
        f"Next: {next_tier.name}; Cost: {format_cost(next_tier.cost)}{reward}"
    )


def slot_bar(used: int, total: int) -> str:
    filled = "#" * used
    empty = "-" * max(0, total - used)
    return f"{filled}{empty} **{used}/{total}**"


def action_label(action: QueuedAction) -> str:
    if action.target == "citadel":
        return f"Citadel to tier {action.next_level}"

    definition = BUILDINGS.get(action.target)
    name = definition.name if definition else action.target
    return f"{name} to tier {action.next_level}"


def missing_resources(settlement: Settlement, cost: dict[str, int]) -> dict[str, int]:
    available = settlement.available_resources()
    return {
        resource: amount - available.get(resource, 0)
        for resource, amount in cost.items()
        if available.get(resource, 0) < amount
    }


def used_slots(settlement: Settlement) -> int:
    return len([level for level in settlement.buildings.values() if level > 0])
