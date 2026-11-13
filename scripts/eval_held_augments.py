"""Doc lo da chon tu dai icon co khop `picked` trong nhan khong? (directional, viec A)

    python scripts/eval_held_augments.py                       # moi ban development
    python scripts/eval_held_augments.py data/eval/playtest/minh_06.json

Mo phong dung vong doi cua HeldAugmentTracker tren video: o moi man verified,
`offer_seen` voi offer CUOI cua nhan tai `close_s`, roi `observe` cac khung
moi `--step` giay trong `window_s`. Ung vien lay tu NHAN chu khong tu bo doc
the: o day chi do bo doc DAI ICON, loi doc the da co thuoc do rieng
(eval_playtest.py).
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

import cv2  # noqa: E402

from src.eval.playtest_labels import load  # noqa: E402
from src.knowledge.augment_features import FeatureTable  # noqa: E402
from src.vision.held_augments import HeldAugmentTracker, IconBank, card_icon  # noqa: E402

VIDEO_DIR = Path("D:/workspace/tft_record")


def development_ids(split_path: Path) -> list[str]:
    split = json.loads(split_path.read_text(encoding="utf-8"))
    return [v["video_id"] for v in split["videos"] if v.get("role") == "development"]


def frame_at(cap: cv2.VideoCapture, t: float):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
    ok, image = cap.read()
    return image if ok else None


def run(
    labels_path: Path, video: Path, tracker: HeldAugmentTracker, step: float, use_cards: bool = True
) -> list[dict]:
    labels = load(labels_path)
    cap = cv2.VideoCapture(str(video))
    tracker.reset()
    rows = []
    for screen in labels.screens:
        if not (screen.offers and screen.picked):
            continue
        last = screen.offers[-1]
        cards = [a for slot in last.cards for a in slot]
        icons = {}
        if use_cards:
            # Live cat icon o MOI khung trong man, nen lan cat cuoi la ngay truoc
            # khi man dong. `at_s` cua offer roi vao hieu ung lat the sau reroll.
            offer_image = frame_at(cap, screen.close_s - 1.0)
            if offer_image is not None:
                icons = {a: card_icon(offer_image, k) for k, slot in enumerate(last.cards) for a in slot}
        tracker.offer_seen(cards, screen.stage, screen.close_s, icons)
        got, at = None, None
        t = screen.close_s
        while t <= screen.close_s + tracker.window_s + step:
            image = frame_at(cap, t)
            if image is not None:
                got = tracker.observe(image, t)
                if got or len(tracker.held) > len(rows):
                    at = t - screen.close_s
                    break
            t += step
        if len(tracker.held) == len(rows):
            tracker.held.append(None)           # het video truoc khi het cua so
            tracker._pending = None
        m = tracker.last_match
        rows.append({
            "stage": screen.stage, "picked": screen.picked, "read": tracker.held[-1],
            "after_s": at, "score": round(m.score, 3) if m else None,
            "margin": round(m.margin, 3) if m else None,
        })
        tracker.last_match = None
    cap.release()
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("labels", nargs="*")
    ap.add_argument("--split", default=str(ROOT / "data/eval/split.json"))
    ap.add_argument("--videos", default=str(VIDEO_DIR))
    ap.add_argument("--step", type=float, default=2.0)
    ap.add_argument("--cdragon-only", action="store_true", help="bỏ icon cắt từ thẻ, chỉ dùng icon CDragon")
    args = ap.parse_args(argv)

    paths = [Path(p) for p in args.labels] or [
        ROOT / "data/eval/playtest" / f"{vid}.json" for vid in development_ids(Path(args.split))
    ]
    features = FeatureTable.load(ROOT / "data/augment_features.json")
    rounds = {a: f.offer_rounds for a, f in features.features.items()}
    tracker = HeldAugmentTracker(IconBank(ROOT / "data/augment_icons"), rounds)

    total = hits = unknown = 0
    for path in paths:
        video = Path(args.videos) / f"{path.stem}.mp4"
        if not path.exists() or not video.exists():
            print(f"bỏ qua {path.stem}: thiếu nhãn hoặc video")
            continue
        print(f"\n{path.stem}")
        for row in run(path, video, tracker, args.step, not args.cdragon_only):
            total += 1
            hits += row["read"] == row["picked"]
            unknown += row["read"] is None
            mark = "✓" if row["read"] == row["picked"] else ("?" if row["read"] is None else "✗")
            print(f"  {row['stage']} {mark} đọc {row['read']} · nhãn {row['picked']}"
                  f" · sau {row['after_s']} s · khớp {row['score']} cách {row['margin']}")
    if total:
        print(f"\nĐọc đúng {hits}/{total} · chưa rõ {unknown} · sai {total - hits - unknown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
