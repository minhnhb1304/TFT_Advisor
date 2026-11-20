"""Trang demo thuat toan cham diem loi tren MOT man chon loi da gan nhan.

    .venv\\Scripts\\python tools\\demo_scoring.py minh_06 4-2      # -> local_docs/demo/minh_06_4-2.html

Trang tu chua (anh, icon, du lieu nhung san), mo offline duoc. Moi con so lay tu
engine that (`rank()` + `rank_by_plan()`), khong tinh lai bang tay; trang chi
tinh lai tong khi keo thanh trong so - phep cong tuyen tinh, giong het engine.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plan_advice as E  # noqa: E402
from src.decision.advisor import Advisor  # noqa: E402
from src.decision.augment_advisor import AugmentChoice  # noqa: E402
from src.decision.scoring.core_fit import CoreFitSettings  # noqa: E402
from src.decision.scoring.plan_fit import PlanSettings  # noqa: E402
from src.utils.settings import Settings  # noqa: E402

PAGE = Path(__file__).with_suffix(".html")
OUT_DIR = ROOT / "local_docs/demo"
SPLIT = ROOT / "data/eval/split.json"


def data_uri(path: Path, mime: str) -> str | None:
    if not path.is_file():
        return None
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def icon(api: str) -> str | None:
    return data_uri(ROOT / "data/augment_icons" / f"{api}.png", "image/png")


def build(video: str, stage: str) -> dict:
    labels = E.load(ROOT / "data/eval/playtest" / f"{video}.json")
    advisor = Advisor(settings=Settings.load().for_patch(E.data_patch(SPLIT, video)))
    engine = advisor.augment_advisor
    held: list[str] = []
    for screen in labels.screens:
        if screen.stage == stage:
            break
        if screen.picked:
            held.append(screen.picked)
    else:
        raise SystemExit(f"{video}: không có màn {stage}")

    offer = screen.offers[-1]
    state = E.state_of(screen, held)
    choices = [AugmentChoice(list(s), slot=i) for i, s in enumerate(offer.cards) if s]
    base = engine.rank(choices, state)
    advice = engine.rank_by_plan(choices, state)
    plan_settings = PlanSettings.from_config(engine.config)
    core_settings = CoreFitSettings.from_config(engine.config)

    def name(api: str) -> str:
        f = engine.features.get(api)
        return (f.name if f else "") or api

    cards = []
    for e in base.entries:
        f = engine.features.get(e.api_name)
        plans = {}
        for p in plan_settings.plans:
            entry = next(x for x in advice.rankings[p.key].entries if x.api_name == e.api_name)
            fit = entry.components["plan_fit"]
            core = entry.components.get("core_fit")
            plans[p.key] = {
                "pf": fit.score,
                "reason": fit.reason,
                "combo": float(fit.detail.get("combo_delta") or 0.0),
                "warnings": list(fit.detail.get("warnings") or []),
                "core_bonus": float((core.detail or {}).get("bonus") or 0.0) if core else 0.0,
                "core_reason": core.reason if core else "",
                "off_damage": bool((core.detail or {}).get("off_damage")) if core else False,
                "engine_total": entry.total,
            }
        cards.append({
            "api": e.api_name,
            "name": e.name,
            "slot": e.choice_index + 1,
            "icon": icon(e.api_name),
            "tags": {
                "categories": f.categories if f else [],
                "econ_value": f.econ_value if f else 0,
                "econ_type": f.econ_type if f else [],
                "tempo": f.tempo if f else "",
            },
            "components": {n: {"score": c.score, "reason": c.reason} for n, c in e.components.items()},
            "engine_rank": e.total,
            "plans": plans,
        })

    hud = screen.hud or {}
    return {
        "video": video,
        "stage": stage,
        "frame": data_uri(ROOT / offer.snapshot, "image/jpeg") if offer.snapshot else None,
        "state": {
            "gold": state.gold, "level": state.level, "xp": state.xp, "xp_needed": state.xp_needed,
            "hp": state.hp, "hp_labeled": hud.get("hp") is not None, "streak": state.streak,
        },
        "held": [{"api": a, "name": name(a), "icon": icon(a)} for a in held],
        "picked": screen.picked,
        "route": (labels.plan or {}).get("route"),
        "weights": dict(engine.config.weights),
        "plan_weight": plan_settings.weight,
        "core": {"enabled": core_settings.enabled, "weight": core_settings.weight,
                 "off_factor": core_settings.off_damage_factor},
        "plans": [{"key": p.key, "label": p.label} for p in plan_settings.plans],
        "true_plan": (plan_settings.plan_for_route((labels.plan or {}).get("route")) or
                      type("x", (), {"key": None})).key,
        "cards": cards,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("video")
    ap.add_argument("stage")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    data = build(args.video, args.stage)
    out = Path(args.out) if args.out else OUT_DIR / f"{args.video}_{args.stage}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    html = PAGE.read_text(encoding="utf-8").replace("/*DATA*/null", json.dumps(data, ensure_ascii=False))
    out.write_text(html, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
