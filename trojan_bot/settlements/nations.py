from __future__ import annotations


NATIONS_BY_CULTURE = {
    "Achaeans": (
        "Aetolians",
        "Mycenae",
        "Sparta",
        "Argos",
        "Phthia",
        "Ithaca",
        "Salamis",
        "Anemoessa",
        "Antheada",
        "Apteron",
        "Arcadians",
        "Asia",
        "Curetes",
        "Dionysias",
        "Elis",
        "Ephesos",
        "Epidayrus",
        "Knossos",
        "Miletus",
        "Noagria",
        "Phyllis",
        "Pylos",
        "Rhodes",
        "Tantalis",
        "Teleboans",
        "Tiryns",
        "Triopion",
        "Troizen",
    ),
    "Aeolians": (
        "Aethaleia",
        "Apaesos",
        "Boetians",
        "Chersonesos",
        "Dindyma",
        "Dolopia",
        "Esperia",
        "Graea",
        "Kyme",
        "Lapiths",
        "Lycomedes' Dolopians",
        "Magnetes",
        "Makaria",
        "Meliboea",
        "Minyes",
        "Narykos",
        "Ozolian Locris",
        "Perrhaebi",
        "Thessalians",
    ),
    "Dorians": (
        "Cassopaei",
        "Dorians",
        "Epirotes",
        "Macednon",
        "Phaiacians",
    ),
    "Ionians": (
        "Abantes",
        "Athina",
        "Corinthians",
        "Ellopians",
        "Ionia",
        "Peraia",
        "Phlegra",
    ),
    "Leleges": (
        "Carians",
        "Lelegia Minoa",
        "Tlawa",
    ),
    "Maeonians": (
        "Alazones",
        "Maeonians",
        "Maeonians of Tmolos",
        "Paphlagonians",
    ),
    "Pelasgians": (
        "Aegaan Pelasgians",
        "Aethria",
        "Agriophones",
        "Bottiaeans",
        "Ilion Hyrtacidae",
        "Ilion Imbrasos",
        "Methymna",
        "Pelasgiotes",
        "Tereia",
        "Troy",
        "Dardania",
        "Lycia",
    ),
    "Phrygians": (
        "Ascanian Phrygians",
        "Bithyni",
        "Manyan Phrygians",
        "Mysia",
    ),
    "Thracians": (
        "Aenos",
        "Apsynthioi",
        "Bisaltae",
        "Cicones",
        "Edonia",
        "Mygdonians",
        "Paeonians",
        "Thrakes",
        "Thyni",
    ),
}

NATION_TO_CULTURE = {
    nation.lower(): culture
    for culture, nations in NATIONS_BY_CULTURE.items()
    for nation in nations
}


def allowed_nations() -> list[str]:
    return sorted(
        nation
        for nations in NATIONS_BY_CULTURE.values()
        for nation in nations
    )


def allowed_cultures() -> list[str]:
    return sorted(NATIONS_BY_CULTURE)


def nations_for_culture(culture: str) -> list[str]:
    canonical = canonical_culture(culture)
    if canonical is None:
        return []
    return list(NATIONS_BY_CULTURE[canonical])


def canonical_culture(value: str) -> str | None:
    cleaned = value.strip().lower()
    for culture in NATIONS_BY_CULTURE:
        if culture.lower() == cleaned:
            return culture
    return None


def canonical_nation(value: str) -> str | None:
    cleaned = value.strip().lower()
    for nation in allowed_nations():
        if nation.lower() == cleaned:
            return nation
    return None


def culture_for_nation(nation: str) -> str | None:
    canonical = canonical_nation(nation)
    if canonical is None:
        return None
    return NATION_TO_CULTURE[canonical.lower()]
