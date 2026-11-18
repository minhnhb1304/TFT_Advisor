"""Bang do core (scripts/build_core_items.py) va CoreFit theo huong (docs/item-reading/plan-item-fit.md).

Cac vi du cua nguoi choi la TEST cho thuat toan, khong go tay vao bang:
Tristana/Kayle -> Guinsoo, Ahri -> Gang + Shojin, Gargoyle/Warmog la do tank.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

from src.decision.augment_advisor import AugmentAdvisor
from src.decision.scoring.core_fit import CoreFit, CoreFitSettings
from src.decision.scoring.types import ScoringConfig
from src.game_state.models import GameState
from src.knowledge.augment_features import AugmentFeature, FeatureTable
from src.knowledge.core_items import Comp, CoreTable, short_name

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_core_items  # noqa: E402

GUINSOO, IE, KRAKEN = "DA_GuinsoosRageblade", "DA_InfinityEdge", "DA_KrakensFury"


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def built() -> dict:
    """Bang may sinh tu du lieu that, KHONG co dong nguoi choi da duyet."""
    recipes = {r["item"]: r["components"] for r in load("data/item_recipes.json")["recipes"]}
    return build_core_items.build(load("data/tftacademy_guides.json")["guides"], recipes,
                                  load("data/cdragon_cache/en_us.json"))


def first_set(built: dict, champ: str, role: str = "carry") -> list[str]:
    return built["champions"][champ][role][0]["items"]


@pytest.mark.parametrize("champ", ["DA_18_Tristana", "DA_18_Kayle"])
def test_guinsoo_carries_have_one_item_core(built, champ):
    assert first_set(built, champ) == [GUINSOO]


def test_ahri_core_is_gauntlet_plus_shojin(built):
    assert first_set(built, "DA_18_Ahri") == ["DA_JeweledGauntlet", "DA_SpearOfShojin"]


def test_meta_tank_items_are_never_carry_core(built):
    tank = set(built["tank_items"])
    assert {"DA_GargoyleStoneplate", "DA_WarmogsArmor"} <= tank
    for entry in built["champions"].values():
        for role in ("carry", "secondary"):
            for s in entry.get(role, []):
                assert not tank & set(s["items"])


def test_damage_type_from_ability_and_name(built):
    champs = built["champions"]
    assert champs["DA_18_Aphelios"]["damage"] == "AD"
    assert champs["DA_18_Ahri"]["damage"] == "AP"
    assert champs["DA_18_Sivir"]["damage"] == "AD"


def test_adaptor_damage_follows_items_per_comp(built):
    """He Thich Ung: AD hay AP theo chi so lon hon tu do -> moi comp mot kieu.
    Hau to `_AD`/`_AP` trong apiName chi la mac dinh cua CDragon."""
    champs = built["champions"]
    assert champs["DA_18_MasterYi_AD"]["damage"] == "adaptive"
    assert champs["DA_Nidalee18_AP"]["damage"] == "adaptive"
    nidalee = {tuple(s["items"]): s["damage"] for s in champs["DA_Nidalee18_AP"]["secondary"]}
    assert nidalee[("DA_SteraksGage",)] == "AD" and nidalee[("DA_GuinsoosRageblade",)] == "AP"
    comps = {c["title"]: c["damage"] for c in built["comps"]}
    assert comps["Invoker Nidalee"] == "AP"      # Gang + Guinsoo + Flail
    assert comps["Solar Melee"] == "AP"          # Akali: Gang + HoJ + EoN


def test_style_maps_to_plan(built):
    plans = {c["style"]: c["plan"] for c in built["comps"]}
    assert plans["4-Cost Fast 8"] == "fast8"
    assert plans["Fast 9"] == "fast9"
    assert plans["2-Cost Reroll"] == "reroll"


def reviewed_sets(row: dict, role: str) -> list[tuple[str, ...]]:
    return [tuple(sorted(x["items"])) for x in row[role]]


def test_reviewed_rows_override_generated(built):
    """Dong ban da duyet (trang review_core_items) thay han dong may sinh."""
    over = load("data/core_items.overrides.json")["champions"]
    table = {k: dict(v) for k, v in built["champions"].items()}
    build_core_items.apply_overrides(table, over)
    for api, row in over.items():
        for role in ("carry", "secondary"):
            if role in row:
                assert [tuple(x["items"]) for x in table[api][role]] == reviewed_sets(row, role), api
        if "damage" in row:
            assert table[api]["damage"] == row["damage"], api
        assert "verified" not in table[api]


def test_committed_table_has_reviewed_rows():
    over = load("data/core_items.overrides.json")["champions"]
    table = CoreTable.load(ROOT / "data/core_items.json", ROOT / "data/item_recipes.json")
    for api, row in over.items():
        if "carry" in row:
            assert [x.items for x in table.core_sets(api)] == reviewed_sets(row, "carry"), api
    assert all(KRAKEN in x.items for x in table.core_sets("DA_18_Aphelios"))


def test_short_name():
    assert [short_name(a) for a in ("DA_18_Aphelios", "DA_Draven18", "DA_Nidalee18_AP",
                                    "DA_18_MasterYi_AD")] == ["Aphelios", "Draven", "Nidalee", "MasterYi"]


# --- CoreFit tren bang tong hop -------------------------------------------

RECIPES = {GUINSOO: ("DA_Component_RecurveBow", "DA_Component_NeedlesslyLargeRod"),
           IE: ("DA_Component_BFSword", "DA_Component_SparringGloves"),
           KRAKEN: ("DA_Component_RecurveBow", "DA_Component_NegatronCloak"),
           "DA_RabadonsDeathcap": ("DA_Component_NeedlesslyLargeRod",) * 2}


def table(*comps: Comp, champions: dict | None = None) -> CoreTable:
    return CoreTable(champions or {}, list(comps), frozenset(), RECIPES,
                     {a: int(e["cost"]) for a, e in (champions or {}).items() if e.get("cost")})


def comp(slug, plan, carry, damage, items) -> Comp:
    return Comp(slug, slug, plan, True, carry, damage, {carry: ("carry", tuple(items))})


SETTINGS = CoreFitSettings(enabled=True, weight=0.1, anvil_extra=0.15, off_damage_factor=0.15,
                           plan_costs={"fast8": (4,), "reroll": (1, 2, 3)})
CHAMPS = {"X": {"carry": [{"items": [GUINSOO], "weight": 1.0}], "damage": "AD", "cost": 2},
          "Y": {"carry": [{"items": ["DA_RabadonsDeathcap"], "weight": 1.0}], "damage": "AP", "cost": 4}}


def feat(api, grants=(), carry_type="none") -> AugmentFeature:
    return AugmentFeature(api_name=api, name=api, category="item", item_grants=list(grants),
                          carry_type=carry_type)


def test_bonus_only_for_missing_core_component():
    fit = CoreFit(table(comp("a", "reroll", "X", "AD", [GUINSOO]), champions=CHAMPS), SETTINGS)
    state = GameState(stage="2-1", item_components=["DA_Component_RecurveBow"])
    rod = fit(feat("ROD", ["NeedlesslyLargeRod"]), state=state, plan_key="reroll", api_name="ROD") \
        if False else fit("ROD", feat("ROD", ["NeedlesslyLargeRod"]), state, "reroll")
    sword = fit("SW", feat("SW", ["BFSword"]), state, "reroll")
    anyc = fit("ANY", feat("ANY", ["AnyComponent"]), state, "reroll")
    anvil = fit("ANV", feat("ANV", ["Anvil"]), state, "reroll")
    done = fit("CI", feat("CI", ["CompletedItem"]), state, "reroll")
    assert rod.detail["bonus"] == 1.0 and "Guinsoo" in rod.reason
    assert sword.is_neutral and sword.detail["bonus"] == 0.0
    assert anyc.detail["bonus"] == rod.detail["bonus"]
    assert anvil.detail["bonus"] == 1.0  # da toi tran: lo ren khong vuot 1
    assert done.detail["bonus"] == 0.0


def test_completed_items_narrow_candidates_and_fallback():
    t = table(comp("ad", "fast8", "X", "AD", [GUINSOO, IE]), comp("ap", "fast8", "Y", "AP", [GUINSOO]),
              champions=CHAMPS)
    fit = CoreFit(t, SETTINGS)
    assert {c.slug for c in fit.candidates(GameState(), "fast8").comps} == {"ad", "ap"}
    one = fit.candidates(GameState(completed_items=[GUINSOO]), "fast8")
    assert {c.slug for c in one.comps} == {"ad", "ap"} and one.damage is None
    two = fit.candidates(GameState(completed_items=[GUINSOO, IE]), "fast8")
    assert [c.slug for c in two.comps] == ["ad"] and two.damage == "AD"
    lost = fit.candidates(GameState(completed_items=[KRAKEN]), "fast8")
    assert lost.fallback and [c.carry for c in lost.comps] == ["Y"]


def test_off_damage_augment_is_penalised_only_when_locked():
    t = table(comp("ad", "fast8", "X", "AD", [GUINSOO, IE]), comp("ap", "fast8", "Y", "AP", [GUINSOO]),
              champions=CHAMPS)
    fit = CoreFit(t, SETTINGS)
    wand = feat("WAND", ["NeedlesslyLargeRod"], carry_type="AP")
    locked = fit("WAND", wand, GameState(completed_items=[GUINSOO, IE]), "fast8")
    mixed = fit("WAND", wand, GameState(completed_items=[GUINSOO]), "fast8")
    assert locked.detail["off_damage"] and locked.score == 0.0 and "chấp lõi" in locked.reason
    assert not mixed.detail["off_damage"]


def test_no_items_read_is_neutral():
    fit = CoreFit(table(comp("a", "reroll", "X", "AD", [GUINSOO]), champions=CHAMPS), SETTINGS)
    out = fit("ROD", feat("ROD", ["NeedlesslyLargeRod"], carry_type="AP"), GameState(), "reroll")
    assert out.is_neutral and not out.detail.get("off_damage")


# --- rank_by_plan tren bang that ------------------------------------------

@pytest.fixture(scope="module")
def advisor() -> AugmentAdvisor:
    config = ScoringConfig.load(ROOT / "config/scoring_weights.yaml")
    return AugmentAdvisor(FeatureTable.load(ROOT / "data/augment_features.json"), config=config,
                          core_table=CoreTable.load(ROOT / "data/core_items.json",
                                                    ROOT / "data/item_recipes.json"))


NEUTRAL_AUGS = ["DA_BeltOverflow", "DA_SwordOverflow"]


def test_wand_overflow_on_aphelios_fast8_ranks_last(advisor):
    """Vi du cua nguoi choi: da di Aphelios (Guinsoo + IE) ma lay Wand Overflow = chap loi."""
    state = GameState(stage="3-2", completed_items=[GUINSOO, IE])
    advice = advisor.rank_by_plan(["DA_WandOverflow", *NEUTRAL_AUGS], state)
    assert advice.rankings["fast8"].entries[-1].api_name == "DA_WandOverflow"
    reroll = advisor.rank_by_plan(["DA_WandOverflow", *NEUTRAL_AUGS], GameState(stage="2-1"))
    assert not reroll.rankings["reroll"].entries[0].components["core_fit"].detail.get("off_damage")


def test_without_core_table_rank_by_plan_is_unchanged(advisor):
    plain = AugmentAdvisor(advisor.features, config=advisor.config)
    state = GameState(stage="3-2", completed_items=[GUINSOO, IE])
    for ranking in plain.rank_by_plan(["DA_WandOverflow", *NEUTRAL_AUGS], state).rankings.values():
        assert all("core_fit" not in e.components for e in ranking.entries)


def test_anvil_is_slightly_more_than_any_component():
    """Mot nua ung vien can Gay -> manh bat ky 0,5; lo ren nhinh hon mot chut."""
    t = table(comp("a", "reroll", "X", "AD", [GUINSOO]), comp("b", "reroll", "Z", "AP", [IE]))
    fit = CoreFit(t, SETTINGS)
    state = GameState(stage="2-1", item_components=["DA_Component_RecurveBow", "DA_Component_BFSword",
                                                    "DA_Component_SparringGloves"])
    anyc = fit("ANY", feat("ANY", ["AnyComponent"]), state, "reroll")
    anvil = fit("ANV", feat("ANV", ["Anvil"]), state, "reroll")
    assert anyc.detail["bonus"] == 0.5
    assert anvil.detail["bonus"] == pytest.approx(0.65)
