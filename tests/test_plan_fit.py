"""Goi y theo huong (directional augment) - docs/directional-augment/plan-conditioned-advice.md."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.decision.augment_advisor import AugmentAdvisor
from src.decision.scoring import PlanFitScorer, PlanProfile, PlanSettings, ScoringConfig
from src.game_state.models import GameState
from src.knowledge.augment_features import AugmentFeature, FeatureTable

ROOT = Path(__file__).resolve().parent.parent

ECO = AugmentFeature(api_name="ECO", name="Eco", category="econ", categories=["econ"],
                     econ_value=3, econ_type=["gold"])
XP = AugmentFeature(api_name="XP", name="Xp", category="econ", categories=["econ"],
                    econ_value=3, econ_type=["xp"])
COMBAT = AugmentFeature(api_name="COMBAT", name="Combat", category="combat", categories=["combat"])

FAST9 = PlanProfile("fast9", "Muốn lên 9", eco=0.20, econ_type={"gold": 0.10, "xp": 0.10},
                    min_hp=40)
FAST8 = PlanProfile("fast8", "Mạnh ngay", eco=-0.10, power=0.20, routes=("fast8", "standard"))
REROLL = PlanProfile("reroll", "Reroll", econ_type={"xp": -0.20}, routes=("reroll1",))
SILENT = PlanProfile("silent", "Không ý kiến")


def advisor(*plans: PlanProfile, debt_bonus: float = 0.05) -> AugmentAdvisor:
    config = ScoringConfig.default()
    config.tuning["plan_fit"] = {
        "weight": 0.15,
        "debt_bonus": debt_bonus,
        "plans": {
            p.key: {"label": p.label, "eco": p.eco, "power": p.power, "econ_type": p.econ_type,
                    "routes": list(p.routes), "min_hp": p.min_hp}
            for p in plans
        },
    }
    table = FeatureTable({f.api_name: f for f in (ECO, XP, COMBAT)})
    return AugmentAdvisor(table, config=config)


def state(**kw) -> GameState:
    return GameState(**{"stage": "3-2", "gold": 30, "hp": 80, **kw})


def test_silent_plan_reproduces_rank_exactly():
    """plan_fit = 0.5 -> thu tu va diem dung bang rank(): dong doi chung cua ablation."""
    adv = advisor(SILENT)
    s = state()
    base = adv.rank(["ECO", "XP", "COMBAT"], s)
    by_plan = adv.rank_by_plan(["ECO", "XP", "COMBAT"], s).rankings["silent"]
    assert by_plan.order == base.order
    assert [e.total for e in by_plan] == pytest.approx([e.total for e in base])


def test_rank_is_untouched_by_plan_config():
    s = state()
    plain = AugmentAdvisor(FeatureTable({f.api_name: f for f in (ECO, XP, COMBAT)}))
    assert advisor(FAST9, FAST8).rank(["ECO", "COMBAT"], s).to_dict() == \
        plain.rank(["ECO", "COMBAT"], s).to_dict()


def test_fast9_prefers_eco_fast8_prefers_combat():
    advice = advisor(FAST9, FAST8).rank_by_plan(["ECO", "COMBAT"], state())
    fits = advice.plan_fits
    assert fits["fast9"]["ECO"].score > fits["fast9"]["COMBAT"].score
    assert fits["fast8"]["COMBAT"].score > fits["fast8"]["ECO"].score


def test_reroll_plan_dislikes_xp():
    fit = PlanFitScorer(PlanSettings())("XP", XP, state(), REROLL)
    assert fit.score < 0.5


def test_held_eco_is_power_debt_for_combat():
    """3 eco phai full bai moi manh -> lo eco da cam lam lo combat dang gia hon."""
    scorer = PlanFitScorer(PlanSettings(debt_bonus=0.05))
    none = scorer("COMBAT", COMBAT, state(), SILENT, held=[])
    two = scorer("COMBAT", COMBAT, state(), SILENT, held=[ECO, XP])
    assert two.score == pytest.approx(none.score + 0.10)
    assert two.detail["debt"] == 2
    # Lo eco khong duoc cong khi da nang eco.
    assert scorer("ECO", ECO, state(), SILENT, held=[ECO]).detail["debt_delta"] == 0


def test_held_combat_springboard_makes_eco_worth_more():
    """Co lo combat lam ban dap -> can tien len full bai (minh_06 4-2)."""
    scorer = PlanFitScorer(PlanSettings(debt_bonus=0.05))
    assert scorer("ECO", ECO, state(), SILENT, held=[COMBAT]).score == pytest.approx(0.55)
    assert scorer("COMBAT", COMBAT, state(), SILENT, held=[COMBAT]).detail["debt_delta"] == 0
    # Mot eco + mot combat: can bang, khong ai duoc cong.
    balanced = [ECO, COMBAT]
    assert scorer("ECO", ECO, state(), SILENT, held=balanced).detail["debt_delta"] == 0
    assert scorer("COMBAT", COMBAT, state(), SILENT, held=balanced).detail["debt_delta"] == 0


def test_stage_override_switches_weights_but_keeps_label():
    """Reroll da roll xong o stage 4: du eco, thieu combat (minh_04 4-2)."""
    plan = PlanProfile.from_config("reroll", {
        "label": "Reroll", "eco": 0.05, "econ_type": {"reroll": 0.2},
        "by_stage": {4: {"eco": -0.10, "power": 0.20, "econ_type": {}}},
    })
    scorer = PlanFitScorer(PlanSettings())
    early, late = state(stage="3-2"), state(stage="4-2")
    assert scorer("ECO", ECO, early, plan).score > 0.5
    assert scorer("ECO", ECO, late, plan).score < 0.5
    assert scorer("COMBAT", COMBAT, late, plan).score > scorer("COMBAT", COMBAT, early, plan).score
    assert scorer("ECO", ECO, late, plan).reason.startswith("Reroll:")


def test_cost_note_names_full_bai_vs_full_form():
    scorer = PlanFitScorer(PlanSettings())
    assert "full bài" in scorer("ECO", ECO, state(), FAST9).reason
    assert "full form" in scorer("COMBAT", COMBAT, state(), FAST9).reason


def test_low_hp_warns_without_changing_score():
    scorer = PlanFitScorer(PlanSettings())
    healthy = scorer("ECO", ECO, state(hp=80), FAST9)
    dying = scorer("ECO", ECO, state(hp=30), FAST9)
    assert dying.score == healthy.score
    assert "30 máu" in dying.detail["warning"] and not healthy.detail["warning"]


def test_plans_with_same_top_collapse_into_one_line():
    advice = advisor(FAST9, FAST8, REROLL).rank_by_plan(["ECO", "COMBAT"], state())
    tops = {p: advice.top_for(p) for p in ("fast9", "fast8", "reroll")}
    assert len(advice.lines) == len(set(tops.values()))
    for line in advice.lines:
        assert all(tops[p.key] == line.entry.api_name for p in line.plans)


def test_unknown_augment_is_neutral():
    fit = PlanFitScorer(PlanSettings())("NEW", None, state(), FAST9)
    assert fit.score == 0.5


def test_invalid_econ_type_in_config_fails_loudly():
    with pytest.raises(ValueError):
        PlanProfile.from_config("x", {"econ_type": {"gold": 0.1, "mana": 0.1}})


def test_committed_config_maps_every_label_route():
    """Moi huong co the gan nhan trong playtest deu co dong goi y tuong ung."""
    from src.eval.playtest_labels import PLANS

    settings = PlanSettings.from_config(ScoringConfig.load(ROOT / "config/scoring_weights.yaml"))
    for route in PLANS:
        assert settings.plan_for_route(route) is not None, route
    assert settings.plan_for_route("standard").key == "fast8"
