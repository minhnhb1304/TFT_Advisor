"""Goi y theo huong co khop lua chon cua nguoi choi khong? (directional augment)

    python scripts/eval_plan_advice.py                    # moi ban development
    python scripts/eval_plan_advice.py data/eval/playtest/minh_05.json ...

Moi man verified co `picked` va file co `plan.route`: lay offer CUOI (cai nguoi
choi chon tu do), cham hai cach roi so voi `picked`:

  - tat : top-1 cua `rank()`          - dong doi chung, hanh vi hien tai
  - bat : top-1 cua dong huong THAT    - `rank_by_plan()` voi huong cua nhan

Lo da cam o man truoc di vao state (`state.augments`), nen luat "no suc manh"
duoc do. Moi video cham bang du lieu patch CUA NO (split.json `data_patch`).

Gioi han phai noi khi bao cao: `picked` la lua chon cua MOT nguoi choi, khong
phai dap an dung - day la do khop voi chuyen gia, khong phai do chinh xac. Ban
development chi de chinh; so bao cao lay tu held-out.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.decision.advisor import Advisor  # noqa: E402
from src.decision.augment_advisor import AugmentChoice  # noqa: E402
from src.decision.scoring import PlanSettings  # noqa: E402
from src.eval.playtest_labels import PlaytestLabels, load  # noqa: E402
from src.game_state.models import GameState  # noqa: E402
from src.utils.settings import Settings  # noqa: E402


def state_of(screen, held: list[str]) -> GameState:
    hud = screen.hud or {}
    return GameState(
        gold=int(hud.get("gold") or 0),
        level=int(hud.get("level") or 1),
        hp=int(hud.get("hp") or 100),
        xp=int(hud.get("xp") or 0),
        xp_needed=hud.get("xp_needed"),
        stage=screen.stage,
        streak=int(hud.get("streak") or 0),
        active_traits=dict(screen.traits or {}),
        augments=list(held),
    )


def development_ids(split_path: Path) -> list[str]:
    split = json.loads(split_path.read_text(encoding="utf-8"))
    return [v["video_id"] for v in split["videos"] if v.get("role") == "development"]


def data_patch(split_path: Path, video_id: str) -> str | None:
    split = json.loads(split_path.read_text(encoding="utf-8"))
    for v in split["videos"]:
        if v["video_id"] == video_id:
            return v.get("data_patch")
    return None


def evaluate(labels: PlaytestLabels, advisor: Advisor) -> list[dict[str, object]]:
    engine = advisor.augment_advisor
    settings = PlanSettings.from_config(engine.config)
    route = (labels.plan or {}).get("route")
    plan = settings.plan_for_route(route)
    rows: list[dict[str, object]] = []
    held: list[str] = []
    for screen in labels.screens:
        if not (screen.verified and screen.picked and screen.offers):
            if screen.picked:
                held.append(screen.picked)
            continue
        choices = [AugmentChoice(list(slot), slot=i) for i, slot in enumerate(screen.offers[-1].cards) if slot]
        state = state_of(screen, held)
        off = engine.rank(choices, state).top
        advice = engine.rank_by_plan(choices, state)
        on = advice.top_for(plan.key) if plan else None
        rows.append({
            "stage": screen.stage,
            "picked": screen.picked,
            "off": off.api_name if off else None,
            "on": on,
            "lines": [(line.label, line.entry.api_name, line.warnings) for line in advice.lines],
        })
        held.append(screen.picked)
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("labels", nargs="*", help="file nhãn; bỏ trống = mọi bản development")
    ap.add_argument("--split", default=str(ROOT / "data/eval/split.json"))
    args = ap.parse_args(argv)

    split = Path(args.split)
    paths = [Path(p) for p in args.labels] or [
        ROOT / "data/eval/playtest" / f"{vid}.json" for vid in development_ids(split)
    ]
    base_settings = Settings.load()
    total = off_hits = on_hits = 0
    for path in paths:
        if not path.exists():
            print(f"bỏ qua {path.name}: chưa có nhãn")
            continue
        labels = load(path)
        route = (labels.plan or {}).get("route")
        if not route:
            print(f"bỏ qua {path.name}: chưa có plan.route")
            continue
        advisor = Advisor(settings=base_settings.for_patch(data_patch(split, path.stem)))
        print(f"\n{path.stem} — hướng thật: {route}")
        for row in evaluate(labels, advisor):
            total += 1
            off_hits += row["off"] == row["picked"]
            on_hits += row["on"] == row["picked"]
            mark = lambda x: "✓" if x == row["picked"] else "✗"  # noqa: E731
            print(f"  {row['stage']}  chọn {row['picked']}  |  tắt {mark(row['off'])} {row['off']}"
                  f"  |  bật {mark(row['on'])} {row['on']}")
            for label, api, warnings in row["lines"]:
                warn = f"  ⚠ {'; '.join(warnings)}" if warnings else ""
                print(f"      {label} → {api}{warn}")
    if total:
        print(f"\nTop-1 khớp lựa chọn người chơi ({total} màn): "
              f"tắt {off_hits}/{total} · bật {on_hits}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
