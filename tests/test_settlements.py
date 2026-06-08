from trojan_bot.settlements.seeds import sparta, starting_settlement
from trojan_bot.settlements.store import SettlementStore


def test_starting_settlement_is_player_owned() -> None:
    settlement = starting_settlement("Argos", "Achaeans", 123)

    assert settlement.nation == "Argos"
    assert settlement.owner_id == 123
    assert settlement.capital == "Argos"
    assert settlement.citadel_tier == 1
    assert settlement.free_choice_slots() == 2


def test_sparta_template_has_test_buildings() -> None:
    settlement = sparta(123)

    assert settlement.nation == "Sparta"
    assert settlement.culture == "Achaeans"
    assert settlement.capital == "Sparta"
    assert settlement.buildings == {}


def test_create_nation_and_queue_building(tmp_path) -> None:
    store = SettlementStore(tmp_path / "settlements.json", tmp_path / "action_queue.json")
    store.create_nation(123, "Achaeans", "Argos")

    action = store.queue_building(123, "farms")
    settlement = store.get_by_owner(123)

    assert action.action_type == "BUILD"
    assert action.target == "farms"
    assert action.next_level == 1
    assert settlement is not None
    assert settlement.pending_resources["wood"] == 150


def test_end_turn_generates_before_processing_queue(tmp_path) -> None:
    store = SettlementStore(tmp_path / "settlements.json", tmp_path / "action_queue.json")
    store.create_nation(123, "Achaeans", "Argos")
    store.queue_building(123, "farms")
    result = store.end_turn()

    settlement = store.get_by_owner(123)

    assert len(result["processed"]) == 1
    assert settlement is not None
    assert settlement.buildings["farms"] == 1
    assert settlement.pending_resources.get("wood", 0) == 0


def test_slot_limit_rejects_third_village_building(tmp_path) -> None:
    store = SettlementStore(tmp_path / "settlements.json", tmp_path / "action_queue.json")
    store.create_nation(123, "Achaeans", "Argos")
    store.queue_building(123, "farms")
    store.queue_building(123, "forestry_camp")
    store.end_turn()

    try:
        store.queue_building(123, "masonry_quarry")
    except ValueError as error:
        assert "No free building slots" in str(error)
    else:
        raise AssertionError("Expected slot limit to reject the third building")


def test_queued_building_counts_against_slots_before_turn_end(tmp_path) -> None:
    store = SettlementStore(tmp_path / "settlements.json", tmp_path / "action_queue.json")
    store.create_nation(123, "Achaeans", "Argos")
    store.queue_building(123, "farms")
    store.queue_building(123, "forestry_camp")

    try:
        store.queue_building(123, "masonry_quarry")
    except ValueError as error:
        assert "No free building slots" in str(error)
    else:
        raise AssertionError("Expected pending slot limit to reject the third building")


def test_create_nation_rejects_non_doc_nation(tmp_path) -> None:
    store = SettlementStore(tmp_path / "settlements.json", tmp_path / "action_queue.json")

    try:
        store.create_nation(123, "Achaeans", "Atlantis")
    except ValueError as error:
        assert "Google Doc nations list" in str(error)
    else:
        raise AssertionError("Expected non-doc nation to fail")


def test_create_nation_assigns_doc_culture(tmp_path) -> None:
    store = SettlementStore(tmp_path / "settlements.json", tmp_path / "action_queue.json")

    settlement = store.create_nation(123, "Achaeans", "Sparta")

    assert settlement.culture == "Achaeans"


def test_create_nation_rejects_wrong_culture(tmp_path) -> None:
    store = SettlementStore(tmp_path / "settlements.json", tmp_path / "action_queue.json")

    try:
        store.create_nation(123, "Dorians", "Sparta")
    except ValueError as error:
        assert "belongs to Achaeans" in str(error)
    else:
        raise AssertionError("Expected wrong culture to fail")

