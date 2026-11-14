"""Hien goi y theo huong: Advisor -> replay viewmodel / overlay video / panel trong tran."""

from __future__ import annotations

from types import SimpleNamespace as NS

from src.decision.advisor import Advisor
from src.game_state.models import GameState
from src.overlay.widgets.augment_panel import build_plan_rows, build_rows, render_text
from src.replay.overlay import plan_pills
from src.replay.viewmodel import build_plans, build_view

OFFER = ["DA_SlamminPlus", "DA_URF", "DA_GoldDestinyPlus"]


def advise(**state):
    return Advisor().advise(GameState(**{"stage": "3-2", "gold": 30, "hp": 80, **state}), OFFER)


def test_advisor_attaches_plan_lines_when_enabled():
    bundle = advise()
    assert bundle.plans is not None and bundle.plans.lines
    picked = {line.entry.api_name for line in bundle.plans.lines}
    assert picked <= set(OFFER)
    assert bundle.to_dict()["plans"]["lines"]


def test_advisor_skips_plans_when_disabled():
    advisor = Advisor()
    advisor.plan_settings = type(advisor.plan_settings)(enabled=False)
    bundle = advisor.advise(GameState(stage="3-2"), OFFER)
    assert bundle.plans is None and bundle.ranking is not None


def event_for(bundle):
    cards = tuple(NS(slot=i, title=f"Thẻ {i + 1}", api_names=(api,), confidence=1.0, reason="")
                  for i, api in enumerate(OFFER))
    return NS(bundle=bundle, cards=cards, state=GameState(stage="3-2", augments=["DA_URF"]),
              rerolls=None, never_seen=(), stale_fields=(), state_note="")


def test_replay_plan_lines_use_card_titles_and_slots():
    lines = build_plans(event_for(advise()))
    assert lines
    for line in lines:
        assert line.slot is not None and line.name == f"Thẻ {line.slot + 1}"
        assert line.kind in ("eco", "combat", "")


def test_replay_strip_shows_held_augments():
    strip, _, _ = build_view(event_for(advise()))
    assert strip.held == ["DA_URF"]


def test_video_pills_split_merged_lines_per_plan():
    lines = build_plans(event_for(advise()))
    pills = plan_pills(lines)
    assert sum(len(v) for v in pills.values()) == sum(len(line.plans) for line in lines)
    for slot, items in pills.items():
        assert all(isinstance(label, str) and key for label, key in items)


def test_low_hp_warning_reaches_every_surface():
    bundle = advise(hp=30)
    rows = build_plan_rows(bundle.plans)
    text = render_text(build_rows(bundle.ranking), bundle.reroll, rows)
    assert "30 máu" in text
    assert any("30 máu" in w for line in build_plans(event_for(bundle)) for w in line.warnings)


def test_panel_without_plans_renders_as_before():
    bundle = advise()
    rows = build_rows(bundle.ranking)
    assert render_text(rows, bundle.reroll) == render_text(rows, bundle.reroll, [])
