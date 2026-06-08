from __future__ import annotations

from .models import Settlement


STARTING_RESOURCES = {
    "food": 750,
    "wood": 900,
    "stone": 600,
    "bronze": 175,
    "horses": 40,
    "luxury_goods": 50,
}


def starting_settlement(nation: str, culture: str, owner_id: int | None, capital: str | None = None) -> Settlement:
    return Settlement(
        nation=nation,
        culture=culture,
        capital=capital or nation,
        ruler_title="Wanax",
        owner_id=owner_id,
        citadel_tier=1,
        population=900,
        resources=dict(STARTING_RESOURCES),
        buildings={},
        pending_resources={},
        favor={},
        patron_deity=None,
        favor_sacrificed=0,
        army={},
    )


def sparta(owner_id: int | None = None) -> Settlement:
    return starting_settlement("Sparta", "Achaeans", owner_id, "Sparta")
