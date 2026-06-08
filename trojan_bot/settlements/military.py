from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Unit:
    name: str
    category: str
    building_key: str
    required_tier: int
    cost: dict[str, int]
    food_upkeep: int
    notes: str


UNITS = {
    "dagger_militia": Unit(
        name="Dagger Militia",
        category="Melee Shock",
        building_key="sword_smithy",
        required_tier=1,
        cost={"food": 10, "bronze": 2},
        food_upkeep=1,
        notes="Entry sword unit unlocked by Copper Forge.",
    ),
    "bronze_swordsmen": Unit(
        name="Bronze Swordsmen",
        category="Melee Shock",
        building_key="sword_smithy",
        required_tier=2,
        cost={"food": 16, "bronze": 6},
        food_upkeep=2,
        notes="Mid-tier sword unit unlocked by Bladesmith's Guild.",
    ),
    "royal_anax_guards": Unit(
        name="Royal Anax Guards",
        category="Melee Shock",
        building_key="sword_smithy",
        required_tier=3,
        cost={"food": 26, "bronze": 12, "luxury_goods": 1},
        food_upkeep=3,
        notes="Elite sword guard unlocked by Royal Armory.",
    ),
    "levy_macemen": Unit(
        name="Levy Macemen",
        category="Melee Defense",
        building_key="spear_muster",
        required_tier=1,
        cost={"food": 8, "wood": 2},
        food_upkeep=1,
        notes="Entry defensive infantry unlocked by Training Yard.",
    ),
    "phalanx_spearmen": Unit(
        name="Phalanx Spearmen",
        category="Melee Defense",
        building_key="spear_muster",
        required_tier=2,
        cost={"food": 14, "wood": 3, "bronze": 4},
        food_upkeep=2,
        notes="Mid-tier spear unit unlocked by Phalanx Garrison.",
    ),
    "citadel_phalangites": Unit(
        name="Citadel Phalangites",
        category="Melee Defense",
        building_key="spear_muster",
        required_tier=3,
        cost={"food": 24, "wood": 5, "bronze": 10},
        food_upkeep=3,
        notes="Elite spear unit unlocked by Citadel Academy.",
    ),
    "copper_hatcheteers": Unit(
        name="Copper Hatcheteers",
        category="Shield-Breakers",
        building_key="axe_lodge",
        required_tier=1,
        cost={"food": 10, "wood": 4, "bronze": 1},
        food_upkeep=1,
        notes="Entry axe unit unlocked by Woodcutter's Muster.",
    ),
    "bronze_axemen": Unit(
        name="Bronze Axemen",
        category="Shield-Breakers",
        building_key="axe_lodge",
        required_tier=2,
        cost={"food": 16, "wood": 5, "bronze": 5},
        food_upkeep=2,
        notes="Mid-tier axe unit unlocked by Axe Foundry.",
    ),
    "labrys_shock_troops": Unit(
        name="Labrys Shock-Troops",
        category="Shield-Breakers",
        building_key="axe_lodge",
        required_tier=3,
        cost={"food": 26, "wood": 8, "bronze": 11},
        food_upkeep=3,
        notes="Elite axe unit unlocked by Labrys Sanctuary.",
    ),
    "tribal_clubmen": Unit(
        name="Tribal Clubmen",
        category="Armor-Crackers",
        building_key="club_foundry",
        required_tier=1,
        cost={"food": 8, "wood": 3},
        food_upkeep=1,
        notes="Zero-bronze club unit unlocked by Stone Quarry Pit.",
    ),
    "mace_infantry": Unit(
        name="Mace Infantry",
        category="Armor-Crackers",
        building_key="club_foundry",
        required_tier=2,
        cost={"food": 15, "wood": 4, "bronze": 3},
        food_upkeep=2,
        notes="Mid-tier mace unit unlocked by Mace Smithy.",
    ),
    "elite_armor_crackers": Unit(
        name="Elite Armor-Crackers",
        category="Armor-Crackers",
        building_key="club_foundry",
        required_tier=3,
        cost={"food": 24, "wood": 7, "bronze": 8},
        food_upkeep=3,
        notes="Elite club unit unlocked by Great Hammer Yard.",
    ),
}


def unlocked_units(buildings: dict[str, int]) -> list[Unit]:
    return [
        unit
        for unit in UNITS.values()
        if buildings.get(unit.building_key, 0) >= unit.required_tier
    ]
