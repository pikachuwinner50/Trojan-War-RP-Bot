from __future__ import annotations

from .models import BuildingDefinition, BuildingTier


BUILDINGS = {
    "farms": BuildingDefinition(
        key="farms",
        name="Agricultural Estates",
        branch="Economic",
        tiers={
            1: BuildingTier("Grain Fields", {"wood": 150, "stone": 50}, {"food": 100}),
            2: BuildingTier("Olive Orchards", {"wood": 400, "stone": 200}, {"food": 250}),
            3: BuildingTier("Royal Vineyards", {"wood": 1000, "stone": 600}, {"food": 500}),
        },
    ),
    "forestry_camp": BuildingDefinition(
        key="forestry_camp",
        name="Forestry Camp",
        branch="Economic",
        tiers={
            1: BuildingTier("Timber Clearing", {"wood": 100, "stone": 50}, {"wood": 100}),
            2: BuildingTier("Carpenter's Yard", {"wood": 300, "stone": 250}, {"wood": 250}),
            3: BuildingTier("Shipbuilding Grove", {"wood": 800, "stone": 700}, {"wood": 500}),
        },
    ),
    "masonry_quarry": BuildingDefinition(
        key="masonry_quarry",
        name="Masonry Quarry",
        branch="Economic",
        tiers={
            1: BuildingTier("Stone Pit", {"wood": 200}, {"stone": 100}),
            2: BuildingTier("Stonemason's Guild", {"wood": 500, "stone": 150}, {"stone": 250}),
            3: BuildingTier("Monumental Quarry", {"wood": 1200, "stone": 400}, {"stone": 500}),
        },
    ),
    "mineral_mine": BuildingDefinition(
        key="mineral_mine",
        name="Mineral Mine",
        branch="Economic",
        tiers={
            1: BuildingTier("Copper Diggings", {"wood": 250, "stone": 100}, {"bronze": 50}),
            2: BuildingTier("Smelting Furnace", {"wood": 600, "stone": 350}, {"bronze": 150}),
            3: BuildingTier("Deep Bronze Mine", {"wood": 1500, "stone": 900}, {"bronze": 350}),
        },
    ),
    "treasury": BuildingDefinition(
        key="treasury",
        name="Treasury Complex",
        branch="Administrative",
        tiers={
            1: BuildingTier("Clay Tablet Archive", {"wood": 150, "stone": 150}, effect="Protects 10% of stored resources from raids."),
            2: BuildingTier("Tax Office", {"wood": 400, "stone": 500}, {"luxury_goods": 25}, "Protects 20% of resources and adds +10% city yields."),
            3: BuildingTier("Palace Vaults", {"wood": 900, "stone": 1400, "luxury_goods": 100}, {"luxury_goods": 75}, "Protects 30% of resources and adds +20% city yields."),
        },
    ),
    "cult_center": BuildingDefinition(
        key="cult_center",
        name="Cult Center",
        branch="Religious",
        unique=True,
        tiers={
            1: BuildingTier("Sacred Shrine", {"wood": 100, "stone": 200}, effect="Unlocks basic worship. Favor cap: 1,000."),
            2: BuildingTier("Grand Altar", {"wood": 350, "stone": 600, "luxury_goods": 50}, effect="Adds +10% favor conversion. Favor cap: 3,000."),
            3: BuildingTier("Monumental Temple", {"wood": 800, "stone": 1500, "luxury_goods": 200}, effect="Unlocks tier 3 blessings. Favor cap: 10,000."),
        },
    ),
    "sword_smithy": BuildingDefinition(
        key="sword_smithy",
        name="Sword Smithy",
        branch="Military",
        tiers={
            1: BuildingTier("Copper Forge", {"wood": 200, "stone": 150}, effect="Unlocks Dagger Militia."),
            2: BuildingTier("Bladesmith's Guild", {"wood": 550, "stone": 450, "bronze": 100}, effect="Unlocks Bronze Swordsmen."),
            3: BuildingTier("Royal Armory", {"wood": 1300, "stone": 1100, "bronze": 300}, effect="Unlocks Royal Anax Guards."),
        },
    ),
    "spear_muster": BuildingDefinition(
        key="spear_muster",
        name="Spear Muster",
        branch="Military",
        tiers={
            1: BuildingTier("Training Yard", {"wood": 150, "stone": 100}, effect="Unlocks Levy Macemen."),
            2: BuildingTier("Phalanx Garrison", {"wood": 500, "stone": 400, "bronze": 50}, effect="Unlocks Phalanx Spearmen."),
            3: BuildingTier("Citadel Academy", {"wood": 1200, "stone": 1000, "bronze": 200}, effect="Unlocks Citadel Phalangites."),
        },
    ),
    "axe_lodge": BuildingDefinition(
        key="axe_lodge",
        name="Axe Lodge",
        branch="Military",
        tiers={
            1: BuildingTier("Woodcutter's Muster", {"wood": 180, "stone": 120}, effect="Unlocks Copper Hatcheteers."),
            2: BuildingTier("Axe Foundry", {"wood": 520, "stone": 420, "bronze": 75}, effect="Unlocks Bronze Axemen."),
            3: BuildingTier("Labrys Sanctuary", {"wood": 1250, "stone": 1050, "bronze": 250}, effect="Unlocks Labrys Shock-Troops."),
        },
    ),
    "club_foundry": BuildingDefinition(
        key="club_foundry",
        name="Club Foundry",
        branch="Military",
        tiers={
            1: BuildingTier("Stone Quarry Pit", {"wood": 100, "stone": 150}, effect="Unlocks Tribal Clubmen."),
            2: BuildingTier("Mace Smithy", {"wood": 480, "stone": 480, "bronze": 50}, effect="Unlocks Mace infantry."),
            3: BuildingTier("Great Hammer Yard", {"wood": 1150, "stone": 1000, "bronze": 200}, effect="Unlocks elite armor-crackers."),
        },
    ),
}
