"""CoreFit tren video dev: doc do that truoc moi man chon loi, so dong huong bat/tat CoreFit.

    .venv\\Scripts\\python scripts\\eval_core_fit.py                 # moi ban development co nhan
    .venv\\Scripts\\python scripts\\eval_core_fit.py minh_06 --verbose

Moi man verified (co `picked`): lui tu `open_s` ve truoc, lay khung CHUAN BI gan
nhat (khong co thanh mau do) ma bo doc thay it nhat mot mon -> do dang cam. Roi
xep hang theo huong THAT (`plan.route`) hai lan: khong / co bang core.

Bao (docs/item-reading/evaluation.md):
  - ty le lui: man co do da ghep nhung khong comp TFT Academy nao khop (do phu)
  - so lan CoreFit doi top-1 cua huong, va khop `picked` truoc/sau
  - chap loi: man nao bi phat, loi nao
Do doc bang bo doc that nen gom ca loi doc; so nay la dev, khong bao cao.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import cv2

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from eval_plan_advice import data_patch, development_ids, state_of  # noqa: E402
from src.decision.advisor import Advisor  # noqa: E402
from src.decision.augment_advisor import AugmentAdvisor, AugmentChoice  # noqa: E402
from src.decision.scoring import PlanSettings  # noqa: E402
from src.decision.scoring.core_fit import CoreFit, CoreFitSettings  # noqa: E402
from src.eval.playtest_labels import load  # noqa: E402
from src.live.item_tracker import held_items  # noqa: E402
from src.utils.settings import Settings  # noqa: E402
from src.vision.bench_items import bench_items  # noqa: E402
from src.vision.unit_items import UnitItemReader, find_health_bars  # noqa: E402

VIDEO_DIR = Path(r"D:\workspace\tft_record")


def items_before(cap, reader: UnitItemReader, t_open: float, lookback: float, step: float):
    """(t, da ghep, manh) o khung chuan bi gan nhat truoc t_open co it nhat mot mon
    (tren tuong + thanh do chua lap)."""
    t = t_open - 1.0
    while t >= max(0.0, t_open - lookback):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if ok and not find_health_bars(frame, own=False):
            units = reader.read(frame)
            completed, parts = held_items(units, bench_items(frame, reader))
            if units and (completed or parts):
                return t, completed, parts
        t -= step
    return None, [], []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("videos", nargs="*", help="video_id; bỏ trống = mọi bản development")
    ap.add_argument("--split", default=str(ROOT / "data/eval/split.json"))
    ap.add_argument("--lookback", type=float, default=60.0)
    ap.add_argument("--step", type=float, default=2.0)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    split = Path(args.split)
    reader = UnitItemReader(ROOT / "data/item_icons", ROOT / "data/item_templates")
    base = Settings.load()
    tally = Counter()
    for vid in args.videos or development_ids(split):
        path = ROOT / "data/eval/playtest" / f"{vid}.json"
        if not path.exists():
            continue
        labels = load(path)
        route = (labels.plan or {}).get("route")
        advisor = Advisor(settings=base.for_patch(data_patch(split, vid)))
        on_engine = advisor.augment_advisor
        off_engine = AugmentAdvisor(on_engine.features, on_engine.stats, on_engine.config)
        settings = PlanSettings.from_config(on_engine.config)
        plan = settings.plan_for_route(route)
        core = CoreFit(on_engine.core_table, CoreFitSettings.from_config(on_engine.config)) \
            if on_engine.core_table else None
        cap = cv2.VideoCapture(str(VIDEO_DIR / f"{vid}.mp4"))
        if not cap.isOpened() or plan is None or core is None:
            print(f"{vid}: bỏ qua (video/hướng/bảng core thiếu)")
            continue
        print(f"\n{vid} — hướng thật: {plan.key}")
        held: list[str] = []
        for screen in labels.screens:
            if not (screen.verified and screen.picked and screen.offers):
                if screen.picked:
                    held.append(screen.picked)
                continue
            t, completed, parts = items_before(cap, reader, screen.open_s, args.lookback, args.step)
            state = state_of(screen, held)
            state.completed_items, state.item_components = completed, parts
            choices = [AugmentChoice(list(s), slot=i) for i, s in enumerate(screen.offers[-1].cards) if s]
            off = off_engine.rank_by_plan(choices, state).top_for(plan.key)
            ranking = on_engine.rank_by_plan(choices, state).rankings[plan.key]
            on = ranking.top.api_name if ranking.top else None
            cands = core.candidates(state, plan.key)
            offd = [e.api_name for e in ranking.entries
                    if (e.components.get("core_fit") and e.components["core_fit"].detail.get("off_damage"))]
            tally["screens"] += 1
            tally["with_items"] += bool(completed or parts)
            tally["with_completed"] += bool(completed)
            tally["fallback"] += cands.fallback
            tally["changed"] += on != off
            tally["off_hit"] += off == screen.picked
            tally["on_hit"] += on == screen.picked
            tally["off_damage"] += bool(offd)
            mark = lambda x: "✓" if x == screen.picked else "✗"  # noqa: E731
            when = f"@{t:.0f}s" if t is not None else "không đọc được"
            print(f"  {screen.stage} {when}: {len(completed)} đồ + {len(parts)} mảnh · "
                  f"{len(cands.comps)} ứng viên{' (lùi)' if cands.fallback else ''}"
                  f"{' · ' + cands.damage if cands.damage else ''} | chọn {screen.picked} | "
                  f"tắt {mark(off)} {off} | bật {mark(on)} {on}" + (f" | chấp lõi: {offd}" if offd else ""))
            if args.verbose:
                print(f"      đồ: {completed} {parts}")
                print(f"      comp: {[c.slug for c in cands.comps][:6]}")
                for e in ranking.entries:
                    cf = e.components.get("core_fit")
                    print(f"      {e.api_name:32s} {e.total:.3f}  {cf.reason if cf else ''}")
            held.append(screen.picked)
        cap.release()
    if tally["screens"]:
        n = tally["screens"]
        wc = tally["with_completed"] or 1
        print(f"\n{n} màn · đọc được đồ {tally['with_items']} · có đồ đã ghép {tally['with_completed']}"
              f" · lùi {tally['fallback']}/{wc} ({tally['fallback'] / wc:.0%})")
        print(f"CoreFit đổi top-1 của hướng thật: {tally['changed']}/{n} · chấp lõi {tally['off_damage']} màn")
        print(f"Top-1 khớp lựa chọn người chơi: tắt {tally['off_hit']}/{n} · bật {tally['on_hit']}/{n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
