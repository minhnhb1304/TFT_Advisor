"""Do precision doc do tren tuong bang nhan da kiem, cheo theo video (docs/item-reading/evaluation.md).

    .venv\\Scripts\\python scripts\\eval_item_reading.py                  # nguong hien tai + quet nguong
    .venv\\Scripts\\python scripts\\eval_item_reading.py --errors         # in tung o doc sai

Cham PHAN LOAI tren cac o da gan nhan (vi tri o khong phu thuoc mau). Moi video V:
mau = icon CDragon + o da kiem cua cac video KHAC (giong `templates --exclude V`),
roi doc cac o cua V. So voi "chi icon CDragon" de thay mau tu game giup bao nhieu.

  o nhan la mon      : doc dung -> dung; doc mon khac -> sai; "chua ro" -> bo
  o "khong phai do" /
  "do dac biet"      : "chua ro" -> dung (khong tinh vao precision); doc ra mon -> sai
  precision = dung / so o doc ra mon; do phu = dung / so o nhan la mon
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

from src.vision.unit_items import MIN_MARGIN, MIN_SCORE, UnitItemReader, _features  # noqa: E402

LABELS = ROOT / "data/eval/items/unit_items.json"
SPECIAL = ("__not_item__", "__other__")


def labelled_cells(frames: list[dict]) -> list[dict]:
    """Moi o da kiem: video, anh cat, nhan."""
    out = []
    for f in frames:
        if not f.get("verified"):
            continue
        image = cv2.imread(str(ROOT / f["image"]))
        if image is None:
            print(f"thiếu ảnh {f['image']}, bỏ qua")
            continue
        for unit in f["units"]:
            for cell in unit["cells"]:
                if cell.get("label"):
                    x, y, s = cell["box"]
                    out.append({"video": f["video"], "frame": f["id"], "label": cell["label"],
                                "crop": image[y:y + s, x:x + s]})
    return out


def ranked(reader: UnitItemReader, crop) -> tuple[str, float, float]:
    """(mon dung dau, diem, khoang cach) khong ap nguong - de quet nguong sau."""
    _, score, margin, top3 = reader.classify(crop)
    return (top3[0][0] if top3 else ""), score, margin


def predictions(cells: list[dict], game_templates: bool) -> list[tuple[dict, str, float, float]]:
    base = UnitItemReader(ROOT / "data/item_icons", ROOT / "data/__none__", min_score=0, min_margin=0)
    out = []
    for video in sorted({c["video"] for c in cells}):
        reader = base
        if game_templates:
            reader = UnitItemReader(ROOT / "data/item_icons", ROOT / "data/__none__", min_score=0, min_margin=0)
            for c in cells:
                if c["video"] != video and c["label"] not in SPECIAL:
                    reader.templates.setdefault(c["label"], []).append(_features(c["crop"][1:-1, 1:-1]))
        out += [(c, *ranked(reader, c["crop"])) for c in cells if c["video"] == video]
    return out


def score(preds, min_score: float, min_margin: float) -> Counter:
    t = Counter()
    for cell, name, sc, mg in preds:
        named = name if sc >= min_score and mg >= min_margin else None
        is_item = cell["label"] not in SPECIAL
        t["items"] += is_item
        if named is None:
            continue
        t["named"] += 1
        t["correct"] += named == cell["label"]
    return t


def line(tag: str, t: Counter) -> str:
    p = t["correct"] / t["named"] if t["named"] else 0.0
    r = t["correct"] / t["items"] if t["items"] else 0.0
    return (f"{tag:34s} precision {p:.3f} ({t['correct']}/{t['named']}) · "
            f"độ phủ {r:.3f} ({t['correct']}/{t['items']})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--errors", action="store_true", help="in từng ô đọc sai ở ngưỡng hiện tại")
    args = ap.parse_args(argv)

    frames = json.loads(LABELS.read_text(encoding="utf-8"))["frames"]
    cells = labelled_cells(frames)
    kinds = Counter("món" if c["label"] not in SPECIAL else c["label"] for c in cells)
    print(f"{len(cells)} ô đã kiểm, {len({c['video'] for c in cells})} video: {dict(kinds)}\n")

    runs = {"chỉ icon CDragon": predictions(cells, False),
            "CDragon + mẫu game (chéo video)": predictions(cells, True)}
    print(f"Ngưỡng hiện tại MIN_SCORE={MIN_SCORE} MIN_MARGIN={MIN_MARGIN}:")
    for tag, preds in runs.items():
        print("  " + line(tag, score(preds, MIN_SCORE, MIN_MARGIN)))

    preds = runs["CDragon + mẫu game (chéo video)"]
    print("\nQuét ngưỡng (CDragon + mẫu game, chéo video):")
    for ms in (0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8):
        for mm in (0.0, 0.04, 0.08, 0.12):
            print("  " + line(f"score≥{ms:.2f} margin≥{mm:.2f}", score(preds, ms, mm)))

    if args.errors:
        print("\nÔ đọc sai (ngưỡng hiện tại, chéo video):")
        for cell, name, sc, mg in preds:
            if sc >= MIN_SCORE and mg >= MIN_MARGIN and name != cell["label"]:
                print(f"  {cell['frame']:22s} nhãn {cell['label']:34s} đọc {name:34s} {sc:.3f}/{mg:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
