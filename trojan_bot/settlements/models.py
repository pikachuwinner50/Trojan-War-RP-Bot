from __future__ import annotations

from dataclasses import dataclass, field


RESOURCE_NAMES = ("food", "wood", "stone", "bronze", "horses", "luxury_goods")
RESOURCE_LABELS = {
    "food": "Food",
    "wood": "Timber",
    "stone": "Stone",
    "bronze": "Bronze",
    "horses": "Horses",
    "luxury_goods": "Luxury Goods",
}

CITADEL_TIERS = {
    1: ("Village", 2),
    2: ("Town", 2),
    3: ("City", 4),
    4: ("Metropolis", 6),
}

CITADEL_UPGRADE_COSTS = {
    2: {"wood": 600, "stone": 400},
    3: {"wood": 1500, "stone": 1200},
    4: {"wood": 3500, "stone": 3000, "bronze": 500},
}


@dataclass(slots=True)
class BuildingTier:
    name: str
    cost: dict[str, int]
    production: dict[str, int] = field(default_factory=dict)
    effect: str = ""


@dataclass(slots=True)
class BuildingDefinition:
    key: str
    name: str
    branch: str
    tiers: dict[int, BuildingTier]
    unique: bool = False

    @property
    def max_level(self) -> int:
        return max(self.tiers)

    def tier(self, level: int) -> BuildingTier | None:
        return self.tiers.get(level)


@dataclass(slots=True)
class QueuedAction:
    action_id: int
    owner_id: int
    nation_key: str
    action_type: str
    target: str
    next_level: int
    cost: dict[str, int]
    quantity: int = 0
    details: dict[str, str | int | float] = field(default_factory=dict)


@dataclass(slots=True)
class Settlement:
    nation: str
    culture: str
    capital: str
    ruler_title: str
    owner_id: int | None
    citadel_tier: int
    population: int
    resources: dict[str, int]
    buildings: dict[str, int] = field(default_factory=dict)
    pending_resources: dict[str, int] = field(default_factory=dict)
    favor: dict[str, int] = field(default_factory=dict)
    patron_deity: str | None = None
    favor_sacrificed: int = 0
    army: dict[str, int] = field(default_factory=dict)

    def normalized_resources(self) -> dict[str, int]:
        return {name: self.resources.get(name, 0) for name in RESOURCE_NAMES}

    def normalized_pending_resources(self) -> dict[str, int]:
        return {name: self.pending_resources.get(name, 0) for name in RESOURCE_NAMES}

    def available_resources(self) -> dict[str, int]:
        return {
            name: self.resources.get(name, 0) - self.pending_resources.get(name, 0)
            for name in RESOURCE_NAMES
        }

    def citadel_name(self) -> str:
        return CITADEL_TIERS[self.citadel_tier][0]

    def free_choice_slots(self) -> int:
        return CITADEL_TIERS[self.citadel_tier][1]
