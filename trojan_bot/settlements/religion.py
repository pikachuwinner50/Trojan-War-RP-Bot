from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Deity:
    name: str
    preferred_resource: str
    blessing: str


DEITIES = {
    "zeus": Deity(
        name="Zeus",
        preferred_resource="stone",
        blessing="Increases maximum civilian population capacity by 10%.",
    ),
    "hera": Deity(
        name="Hera",
        preferred_resource="stone",
        blessing="Boosts baseline civilian tax revenue by 15%.",
    ),
    "poseidon": Deity(
        name="Poseidon",
        preferred_resource="wood",
        blessing="Reduces an enemy coastal settlement's defensive wall tier by 1.",
    ),
    "athena": Deity(
        name="Athena",
        preferred_resource="bronze",
        blessing="Reduces heavy infantry casualties in resolved combat by 10%.",
    ),
    "ares": Deity(
        name="Ares",
        preferred_resource="bronze",
        blessing="Queued troops deploy instantly this turn.",
    ),
    "hephaestus": Deity(
        name="Hephaestus",
        preferred_resource="wood",
        blessing="Reduces raw bronze weapon and armor costs by 10%.",
    ),
    "apollo": Deity(
        name="Apollo",
        preferred_resource="luxury_goods",
        blessing="Cures plague or freezes an enemy city's population growth.",
    ),
    "artemis": Deity(
        name="Artemis",
        preferred_resource="wood",
        blessing="Grants a defense bonus in forest or mountain combat nodes.",
    ),
    "aphrodite": Deity(
        name="Aphrodite",
        preferred_resource="luxury_goods",
        blessing="Increases luxury goods generation by 15%.",
    ),
    "demeter": Deity(
        name="Demeter",
        preferred_resource="food",
        blessing="Boosts food production across active farming slots by 20%.",
    ),
    "dionysus": Deity(
        name="Dionysus",
        preferred_resource="food",
        blessing="Boosts population happiness and prevents riot production stalls.",
    ),
    "hermes": Deity(
        name="Hermes",
        preferred_resource="stone",
        blessing="Protects resource trades from raids or interception.",
    ),
}

SACRIFICE_VALUES = {
    "food": 1,
    "wood": 1,
    "stone": 1,
    "bronze": 3,
    "horses": 4,
    "luxury_goods": 5,
}

HUBRIS_MODIFIERS = {
    1: ("1.0x", "The gods look favorably upon your righteous rule."),
    2: ("0.9x", "The smoke of your altars smells faintly of earthly vanity."),
    3: ("0.75x", "Zeus demands greater proof; ordinary offerings no longer satisfy."),
    4: ("0.5x", "Absolute Hubris. Offerings are viewed as arrogant demands."),
}


def favor_capacity(cult_center_level: int) -> int:
    if cult_center_level >= 3:
        return 10000
    if cult_center_level == 2:
        return 3000
    if cult_center_level == 1:
        return 1000
    return 0


def favor_bonus(cult_center_level: int) -> str:
    if cult_center_level >= 2:
        return "+10% conversion bonus"
    if cult_center_level == 1:
        return "Basic worship unlocked"
    return "Worship locked"


def favor_from_sacrifice(deity_key: str, resource: str, amount: int, cult_center_level: int) -> int:
    deity = DEITIES[deity_key]
    value = SACRIFICE_VALUES[resource] * amount

    if deity.preferred_resource == resource:
        value = int(value * 1.5)

    if cult_center_level >= 2:
        value = int(value * 1.1)

    return value
