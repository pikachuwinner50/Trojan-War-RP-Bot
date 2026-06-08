from trojan_bot.settlements.catalog import BUILDINGS
from trojan_bot.settlements.capitals import CAPITALS, UNKNOWN_CAPITAL_NATIONS
from trojan_bot.settlements.military import UNITS
from trojan_bot.settlements.models import RESOURCE_NAMES
from trojan_bot.settlements.nations import allowed_nations
from trojan_bot.settlements.religion import DEITIES


def test_all_nations_have_capital_status() -> None:
    covered = set(CAPITALS) | set(UNKNOWN_CAPITAL_NATIONS)

    assert set(allowed_nations()) <= covered


def test_all_deities_use_valid_resources() -> None:
    for deity in DEITIES.values():
        assert deity.preferred_resource in RESOURCE_NAMES


def test_all_units_unlock_from_real_building_tiers() -> None:
    for unit in UNITS.values():
        building = BUILDINGS[unit.building_key]

        assert building.branch == "Military"
        assert building.tier(unit.required_tier) is not None
