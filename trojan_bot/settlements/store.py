from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .catalog import BUILDINGS
from .capitals import capital_for_nation
from .models import (
    CITADEL_UPGRADE_COSTS,
    RESOURCE_NAMES,
    QueuedAction,
    Settlement,
)
from .military import UNITS
from .nations import allowed_cultures, allowed_nations, canonical_culture, canonical_nation, culture_for_nation
from .religion import DEITIES, favor_capacity, favor_from_sacrifice
from .seeds import sparta, starting_settlement


class SettlementStore:
    def __init__(self, settlement_path: Path, queue_path: Path | None = None) -> None:
        self.settlement_path = settlement_path
        self.queue_path = queue_path or settlement_path.with_name("action_queue.json")

    def create_nation(self, owner_id: int, culture: str, nation: str) -> Settlement:
        settlements = self._load_settlements()

        if self.get_by_owner(owner_id) is not None:
            raise ValueError("You already have a nation.")

        chosen_culture = canonical_culture(culture)
        if chosen_culture is None:
            raise ValueError("Choose a culture from the Google Doc nations list.")

        canonical = canonical_nation(nation)
        if canonical is None:
            raise ValueError("Choose a nation from the Google Doc nations list.")

        actual_culture = culture_for_nation(canonical)
        if actual_culture is None:
            raise ValueError("That nation is missing a culture group in the catalog.")

        if actual_culture != chosen_culture:
            raise ValueError(f"`{canonical}` belongs to {actual_culture}, not {chosen_culture}.")

        nation_key = self._key(canonical)
        existing = settlements.get(nation_key)
        if existing is not None and existing.owner_id is None:
            existing.owner_id = owner_id
            settlements[nation_key] = existing
            self._save_settlements(settlements)
            return existing

        if existing is not None:
            raise ValueError(f"`{canonical}` is already claimed.")

        if nation_key == "sparta":
            settlement = sparta(owner_id)
        else:
            settlement = starting_settlement(canonical, actual_culture, owner_id, capital_for_nation(canonical))
        settlements[nation_key] = settlement
        self._save_settlements(settlements)
        return settlement

    def list_allowed_cultures(self) -> list[str]:
        return allowed_cultures()

    def list_allowed_nations(self) -> list[str]:
        return allowed_nations()

    def get(self, nation: str) -> Settlement | None:
        return self._load_settlements().get(self._key(nation))

    def get_by_owner(self, owner_id: int) -> Settlement | None:
        for settlement in self._load_settlements().values():
            if settlement.owner_id == owner_id:
                return settlement
        return None

    def get_for_user(self, owner_id: int, nation: str | None = None) -> Settlement | None:
        if nation:
            return self.get(nation)
        return self.get_by_owner(owner_id)

    def list_nations(self) -> list[str]:
        return sorted(settlement.nation for settlement in self._load_settlements().values())

    def list_queue(self, owner_id: int | None = None) -> list[QueuedAction]:
        actions = self._load_queue()
        if owner_id is None:
            return actions
        return [action for action in actions if action.owner_id == owner_id]

    def reset_claims(self) -> int:
        settlements = self._load_settlements()
        count = len(settlements)
        self._save_settlements({})
        self._save_queue([])
        return count

    def unclaim_nation(self, nation: str) -> Settlement:
        settlements = self._load_settlements()
        nation_key = self._key(nation)
        settlement = settlements.get(nation_key)

        if settlement is None:
            raise ValueError(f"`{nation}` is not claimed.")

        del settlements[nation_key]
        remaining_actions = [
            action
            for action in self._load_queue()
            if action.nation_key != nation_key
        ]
        self._save_settlements(settlements)
        self._save_queue(remaining_actions)
        return settlement

    def queue_building(self, owner_id: int, building_key: str) -> QueuedAction:
        settlements = self._load_settlements()
        settlement_key, settlement = self._settlement_for_owner(settlements, owner_id)
        key = self._key(building_key)

        if key == "citadel":
            return self._queue_citadel(settlements, settlement_key, settlement)

        definition = BUILDINGS.get(key)
        if definition is None:
            raise ValueError(f"Unknown building `{building_key}`.")

        pending_actions = self._load_queue()
        if self._has_pending_action(pending_actions, settlement_key, key):
            raise ValueError(f"`{key}` is already queued this turn.")

        current_level = self._effective_building_level(settlement, pending_actions, settlement_key, key)
        next_level = current_level + 1

        if next_level > definition.max_level:
            raise ValueError(f"{definition.name} is already at max tier.")

        if next_level > settlement.citadel_tier:
            raise ValueError("Upgrade your Citadel first. Building tier cannot exceed the Citadel tier.")

        used_slots = self._used_slots(settlement, pending_actions, settlement_key)
        if current_level == 0 and used_slots >= settlement.free_choice_slots():
            raise ValueError("No free building slots. Upgrade the Citadel before constructing another building.")

        tier = definition.tier(next_level)
        if tier is None:
            raise ValueError(f"{definition.name} has no tier {next_level}.")

        action = self._reserve_and_queue(
            settlements,
            settlement_key,
            settlement,
            action_type="BUILD",
            target=key,
            next_level=next_level,
            cost=tier.cost,
        )
        return action

    def queue_sacrifice(self, owner_id: int, deity_key: str, resource: str, amount: int) -> QueuedAction:
        settlements = self._load_settlements()
        settlement_key, settlement = self._settlement_for_owner(settlements, owner_id)
        deity = self._key(deity_key)
        resource_key = self._key(resource)

        if deity not in DEITIES:
            raise ValueError(f"Unknown deity `{deity_key}`.")

        if resource_key not in RESOURCE_NAMES:
            raise ValueError(f"Unknown resource `{resource}`.")

        if amount <= 0:
            raise ValueError("Sacrifice amount must be greater than zero.")

        if settlement.buildings.get("cult_center", 0) <= 0:
            raise ValueError("Build a Cult Center before making sacrifices.")

        return self._reserve_and_queue(
            settlements,
            settlement_key,
            settlement,
            action_type="SACRIFICE",
            target=deity,
            next_level=0,
            cost={resource_key: amount},
            quantity=amount,
            details={"resource": resource_key},
        )

    def queue_recruitment(self, owner_id: int, unit_key: str, quantity: int) -> QueuedAction:
        settlements = self._load_settlements()
        settlement_key, settlement = self._settlement_for_owner(settlements, owner_id)
        key = self._key(unit_key)
        unit = UNITS.get(key)

        if unit is None:
            raise ValueError(f"Unknown unit `{unit_key}`.")

        if quantity <= 0:
            raise ValueError("Recruitment quantity must be greater than zero.")

        if settlement.buildings.get(unit.building_key, 0) < unit.required_tier:
            raise ValueError(f"{unit.name} requires {unit.building_key} tier {unit.required_tier}.")

        cost = {
            resource: amount * quantity
            for resource, amount in unit.cost.items()
        }
        return self._reserve_and_queue(
            settlements,
            settlement_key,
            settlement,
            action_type="RECRUIT",
            target=key,
            next_level=0,
            cost=cost,
            quantity=quantity,
            details={"unit": unit.name},
        )

    def end_turn(self) -> dict[str, object]:
        settlements = self._load_settlements()
        actions = self._load_queue()
        generation = self._apply_passive_generation(settlements)
        processed: list[QueuedAction] = []

        for action in actions:
            settlement = settlements.get(action.nation_key)
            if settlement is None:
                continue

            for resource, amount in action.cost.items():
                settlement.resources[resource] = settlement.resources.get(resource, 0) - amount
                settlement.pending_resources[resource] = max(
                    0,
                    settlement.pending_resources.get(resource, 0) - amount,
                )

            if action.action_type == "SACRIFICE":
                self._process_sacrifice(settlement, action)
            elif action.action_type == "RECRUIT":
                settlement.army[action.target] = settlement.army.get(action.target, 0) + action.quantity
            elif action.action_type == "CITADEL":
                settlement.citadel_tier = action.next_level
            elif action.action_type == "BUILD":
                settlement.buildings[action.target] = action.next_level

            processed.append(action)

        self._save_settlements(settlements)
        self._save_queue([])
        return {
            "generated": generation,
            "processed": processed,
            "settlements": list(settlements.values()),
        }

    def _process_sacrifice(self, settlement: Settlement, action: QueuedAction) -> None:
        resource = str(action.details.get("resource", ""))
        amount = action.cost.get(resource, action.quantity)
        cult_level = settlement.buildings.get("cult_center", 0)
        gained = favor_from_sacrifice(action.target, resource, amount, cult_level)
        capacity = favor_capacity(cult_level)
        current = settlement.favor.get(action.target, 0)
        settlement.favor[action.target] = min(capacity, current + gained)
        settlement.favor_sacrificed += gained

        if settlement.patron_deity is None:
            settlement.patron_deity = action.target

    def _queue_citadel(
        self,
        settlements: dict[str, Settlement],
        settlement_key: str,
        settlement: Settlement,
    ) -> QueuedAction:
        next_level = settlement.citadel_tier + 1
        cost = CITADEL_UPGRADE_COSTS.get(next_level)

        if cost is None:
            raise ValueError("The Citadel is already at max tier.")

        if self._has_pending_action(self._load_queue(), settlement_key, "citadel"):
            raise ValueError("The Citadel is already queued this turn.")

        return self._reserve_and_queue(
            settlements,
            settlement_key,
            settlement,
            action_type="CITADEL",
            target="citadel",
            next_level=next_level,
            cost=cost,
        )

    def _reserve_and_queue(
        self,
        settlements: dict[str, Settlement],
        settlement_key: str,
        settlement: Settlement,
        *,
        action_type: str,
        target: str,
        next_level: int,
        cost: dict[str, int],
        quantity: int = 0,
        details: dict[str, str | int | float] | None = None,
    ) -> QueuedAction:
        missing = self._missing_resources(settlement, cost)
        if missing:
            readable = self._format_cost(missing)
            raise ValueError(f"Insufficient resources. Missing {readable}.")

        for resource, amount in cost.items():
            settlement.pending_resources[resource] = settlement.pending_resources.get(resource, 0) + amount

        actions = self._load_queue()
        action = QueuedAction(
            action_id=self._next_action_id(actions),
            owner_id=settlement.owner_id or 0,
            nation_key=settlement_key,
            action_type=action_type,
            target=target,
            next_level=next_level,
            cost=dict(cost),
            quantity=quantity,
            details=details or {},
        )
        actions.append(action)
        settlements[settlement_key] = settlement
        self._save_settlements(settlements)
        self._save_queue(actions)
        return action

    def _apply_passive_generation(self, settlements: dict[str, Settlement]) -> dict[str, dict[str, int]]:
        generated: dict[str, dict[str, int]] = {}

        for key, settlement in settlements.items():
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
                    settlement.resources[resource] = settlement.resources.get(resource, 0) + amount
                    totals[resource] = totals.get(resource, 0) + amount

            generated[key] = totals

        return generated

    def _settlement_for_owner(
        self,
        settlements: dict[str, Settlement],
        owner_id: int,
    ) -> tuple[str, Settlement]:
        for key, settlement in settlements.items():
            if settlement.owner_id == owner_id:
                return key, settlement
        raise ValueError("You do not have a nation yet. Use `/nation claim` first.")

    @staticmethod
    def _used_slots(
        settlement: Settlement,
        actions: list[QueuedAction] | None = None,
        settlement_key: str | None = None,
    ) -> int:
        occupied = {key for key, level in settlement.buildings.items() if level > 0}

        if actions is not None and settlement_key is not None:
            occupied.update(
                action.target
                for action in actions
                if action.nation_key == settlement_key
                and action.action_type == "BUILD"
                and action.target not in occupied
            )

        return len(occupied)

    @staticmethod
    def _effective_building_level(
        settlement: Settlement,
        actions: list[QueuedAction],
        settlement_key: str,
        building_key: str,
    ) -> int:
        levels = [settlement.buildings.get(building_key, 0)]
        levels.extend(
            action.next_level
            for action in actions
            if action.nation_key == settlement_key
            and action.action_type == "BUILD"
            and action.target == building_key
        )
        return max(levels)

    @staticmethod
    def _has_pending_action(actions: list[QueuedAction], settlement_key: str, target: str) -> bool:
        return any(action.nation_key == settlement_key and action.target == target for action in actions)

    @staticmethod
    def _missing_resources(settlement: Settlement, cost: dict[str, int]) -> dict[str, int]:
        available = settlement.available_resources()
        return {
            resource: amount - available.get(resource, 0)
            for resource, amount in cost.items()
            if available.get(resource, 0) < amount
        }

    def _load_settlements(self) -> dict[str, Settlement]:
        if not self.settlement_path.exists():
            return {}

        with self.settlement_path.open("r", encoding="utf-8") as file:
            raw = json.load(file)

        return {
            key: self._settlement_from_dict(value)
            for key, value in raw.items()
        }

    def _save_settlements(self, settlements: dict[str, Settlement]) -> None:
        self.settlement_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {key: asdict(settlement) for key, settlement in settlements.items()}

        with self.settlement_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, sort_keys=True)

    def _load_queue(self) -> list[QueuedAction]:
        if not self.queue_path.exists():
            return []

        with self.queue_path.open("r", encoding="utf-8") as file:
            raw = json.load(file)

        return [
            QueuedAction(
                action_id=value["action_id"],
                owner_id=value["owner_id"],
                nation_key=value["nation_key"],
                action_type=value["action_type"],
                target=value["target"],
                next_level=value.get("next_level", 0),
                cost=value.get("cost", {}),
                quantity=value.get("quantity", 0),
                details=value.get("details", {}),
            )
            for value in raw
        ]

    def _save_queue(self, actions: list[QueuedAction]) -> None:
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)

        with self.queue_path.open("w", encoding="utf-8") as file:
            json.dump([asdict(action) for action in actions], file, indent=2, sort_keys=True)

    @staticmethod
    def _settlement_from_dict(value: dict) -> Settlement:
        if "citadel_tier" not in value:
            return Settlement(
                nation=value["nation"],
                culture=value["culture"],
                capital=value.get("capital", capital_for_nation(value["nation"])),
                ruler_title=value["ruler_title"],
                owner_id=value.get("owner_id"),
                citadel_tier=value.get("tier", 1),
                population=value["population"],
                resources=value["resources"],
                buildings={
                    key: building["level"] if isinstance(building, dict) else int(building)
                    for key, building in value.get("buildings", {}).items()
                },
                pending_resources=value.get("pending_resources", {}),
                favor=value.get("favor", {}),
                patron_deity=value.get("patron_deity"),
                favor_sacrificed=value.get("favor_sacrificed", 0),
                army=value.get("army", {}),
            )

        if "capital" not in value:
            value["capital"] = capital_for_nation(value["nation"])
        value.setdefault("favor", {})
        value.setdefault("patron_deity", None)
        value.setdefault("favor_sacrificed", 0)
        value.setdefault("army", {})

        return Settlement(**value)

    @staticmethod
    def _next_action_id(actions: list[QueuedAction]) -> int:
        return max((action.action_id for action in actions), default=0) + 1

    @staticmethod
    def _key(value: str) -> str:
        return value.strip().lower().replace(" ", "_")

    @staticmethod
    def _format_cost(cost: dict[str, int]) -> str:
        return ", ".join(f"{amount} {resource.replace('_', ' ')}" for resource, amount in cost.items())
