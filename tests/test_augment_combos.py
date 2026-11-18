"""Luat combo lo cua nguoi choi - docs/directional-augment/augment-combos.md."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from src.decision.augment_advisor import AugmentChoice
from src.decision.scoring.augment_combos import ComboTable
from src.knowledge.augment_features import AugmentFeature, FeatureTable

ROOT = Path(__file__).resolve().parent.parent
COMBOS = ROOT / "data/augment_combos.json"
STRENGTH = {"info": 0.0, "light": 0.02, "medium": 0.04, "strong": 0.08}


@pytest.fixture(scope="module")
def table() -> ComboTable:
    return ComboTable.load(COMBOS)


@pytest.fixture(scope="module")
def features() -> FeatureTable:
    return FeatureTable.load(ROOT / "data/augment_features.json")


def effect(table, features, cand, held, plan="fast8"):
    return table.effect(features.get(cand), [features.get(h) for h in held], plan, STRENGTH)


def test_every_listed_augment_exists(features):
    data = json.loads(COMBOS.read_text(encoding="utf-8"))
    apis = [a for g in data["groups"].values() for a in g.get("apis", [])]
    apis += [r["api"] for r in data["risky"]]
    assert [a for a in apis if features.get(a) is None] == []


def test_every_rule_keeps_the_players_words():
    data = json.loads(COMBOS.read_text(encoding="utf-8"))
    rules = data["pairs"] + data["conflicts"] + data["risky"] + [data["eco_pair"], data["triad"]]
    assert all(r.get("source") for r in rules)


def test_unknown_group_fails_loudly():
    with pytest.raises(ValueError):
        ComboTable({"groups": {}, "pairs": [{"id": "x", "a": "nope", "b": "nope", "strength": "light"}]})


@pytest.mark.parametrize("cand, held", [
    ("DA_BoosterPackPlusPlus", ["DA_BonusGiftPlus"]),   # orb sau Bonus Gifts
    ("DA_BonusGift", ["DA_MissedConnections"]),         # chieu nguoc lai
])
def test_bonus_gift_and_orb_payers_combo_both_ways(table, features, cand, held):
    e = effect(table, features, cand, held)
    assert e.delta == STRENGTH["strong"]
    assert "combo với" in e.reasons[0]


def test_base_booster_pack_is_not_an_orb_payer(table, features):
    assert effect(table, features, "DA_BoosterPack", ["DA_BonusGift"]).delta == 0


def test_item_augments_feed_sweet_treats(table, features):
    assert effect(table, features, "DA_SweetTreats", ["DA_PandorasItemsI"]).delta == STRENGTH["medium"]


def test_two_high_verticality(table, features):
    assert effect(table, features, "DA_VerticalityIII", ["DA_VerticalityII"]).delta == STRENGTH["medium"]
    assert effect(table, features, "DA_VerticalityI", ["DA_VerticalityII"]).delta == 0


def test_lotus_with_thieves_gloves(table, features):
    assert effect(table, features, "DA_JeweledLotus_II", ["DA_BandOfThievesIIPlus"]).delta == STRENGTH["strong"]


@pytest.mark.parametrize("cand, held", [
    ("DA_PandorasItemsI", ["DA_MakeshiftArmorI"]),
    ("DA_PandorasItemsIIPlus", ["DA_Slammin"]),
])
def test_conflicts_cost_score(table, features, cand, held):
    e = effect(table, features, cand, held)
    assert e.delta < 0 and e.reasons[0].startswith("kị")


def test_second_gold_xp_augment_warns_reroll_only(table, features):
    reroll = effect(table, features, "DA_BoosterPackPlusPlus", ["DA_SlamminPlus"], plan="reroll")
    assert reroll.delta == -STRENGTH["medium"] and reroll.warnings
    assert effect(table, features, "DA_BoosterPackPlusPlus", ["DA_SlamminPlus"], plan="fast9").warnings == []


def test_eco_without_gold_or_xp_does_not_count(table, features):
    # minh_04 3-2: reroll, cam Expected Unexpectedness (khong tien/XP) roi chon Missed Connections.
    assert effect(table, features, "DA_MissedConnections", ["DA_ExpectedUnexpectedness"],
                  plan="reroll").warnings == []


def test_birthday_reunion_only_fits_fast9(table, features):
    fast9 = effect(table, features, "DA_BirthdayReunion", [], plan="fast9")
    fast8 = effect(table, features, "DA_BirthdayReunion", [], plan="fast8")
    assert fast9.delta == 0 and fast9.warnings
    assert fast8.delta == -STRENGTH["medium"]


def test_risky_augment_only_warns(table, features):
    e = effect(table, features, "DA_Warpath", [])
    assert e.delta == 0 and "Warpath" in e.warnings[0]


def test_easy_triad_is_explained_not_scored(table, features):
    e = effect(table, features, "DA_TwinGuardians", ["DA_PandorasItemsI", "DA_SlamminPlus"])
    assert e.delta == 0 and any("1 eco – 1 item – 1 combat" in r for r in e.reasons)


def test_combo_lifts_booster_pack_for_minh_06():
    """minh_06 4-2 (fast8): cam Bonus Gifts+ -> Booster Pack++ (lua chon cua nguoi choi)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import eval_plan_advice as E
    from src.decision.advisor import Advisor
    from src.utils.settings import Settings

    split = ROOT / "data/eval/split.json"
    labels = E.load(ROOT / "data/eval/playtest/minh_06.json")
    engine = Advisor(settings=Settings.load().for_patch(E.data_patch(split, "minh_06"))).augment_advisor
    held: list[str] = []
    for screen in labels.screens:
        if screen.stage == "4-2":
            choices = [AugmentChoice(list(s), slot=i) for i, s in enumerate(screen.offers[-1].cards) if s]
            advice = engine.rank_by_plan(choices, E.state_of(screen, held))
            assert advice.top_for("fast8") == "DA_BoosterPackPlusPlus"
            return
        held.append(screen.picked)
    pytest.fail("không thấy màn 4-2")
