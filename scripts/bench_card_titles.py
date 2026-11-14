"""Do thuc nghiem cac backend OCR tren bai doc TEN THE LOI (augment) - 2026-11-15.

Moi backend chi tra ve CAC DONG CHU cua o `card_text_<slot>` (man augment_select).
Sau do MOI backend di qua CUNG mot ham khop danh muc (`resolve_name`, nguong 0,82
cua src/live/card_reader.py), nen chenh lech chi den tu buoc doc chu.

Mau: MOI offer cua moi man `verified` co snapshot, trong cac video role
"development" cua data/eval/split.json. Offer sau reroll lap lai hai o khong doi,
nen cung mot o co the dem nhieu lan; cot `is_last` danh dau offer cuoi cua man
de tinh rieng tap "moi man mot lan".

    # RapidOCR (duong san pham) - chay bang .venv cua du an
    .venv/Scripts/python.exe scripts/bench_card_titles.py --backend rapidocr

    # indra-ocr va chandra-ocr-2 - chay bang moi truong rieng .venv-bench
    .venv-bench/Scripts/python.exe scripts/bench_card_titles.py --backend indra
    # Chandra 2 qua endpoint vLLM (vd Modal); khong dat CHANDRA_URL thi chay CPU cuc bo - rat nang
    CHANDRA_URL=https://<app>.modal.run/v1 .venv-bench/Scripts/python.exe \
        scripts/bench_card_titles.py --backend chandra2 --sample 40 --seed 20261115

    # Bang tong tren GIAO cac mau da chay cua nhieu backend
    python scripts/bench_card_titles.py --report data/eval/runs/bench_card_titles_*.csv

Ket qua moi the: dung / sai (ra ten khac) / sot (khong khop, hoac mo ho ma nhan
khong mo ho). CSV ghi tung dong ngay khi xong va chay lai thi bo qua mau da co
(--resume mac dinh bat), nen backend cham co the dung giua chung.
"""

from __future__ import annotations

import argparse
import csv
import glob
import html
import json
import os
import random
import re
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from src.capture.regions import ScreenRegions  # noqa: E402
from src.knowledge.name_index import NameIndex  # noqa: E402
from src.live.card_reader import FUZZY_CUTOFF, SCREEN, resolve_name  # noqa: E402

RUNS = ROOT / "data" / "eval" / "runs"
FIELDS = ("key", "video", "stage", "offer", "is_last", "slot", "truth", "lines", "pred",
          "verdict", "ms")


@dataclass(frozen=True)
class Sample:
    key: str
    video: str
    stage: str
    offer: int
    is_last: bool
    slot: int
    truth: tuple[str, ...]
    snapshot: str


# --- mau --------------------------------------------------------------------


def development_ids(split_path: Path) -> dict[str, str]:
    """sha256 -> video_id cua cac video role development."""
    split = json.loads(split_path.read_text(encoding="utf-8"))
    return {v["video_sha256"]: v["video_id"] for v in split["videos"] if v["role"] == "development"}


def collect(labels_glob: str, split_path: Path) -> list[Sample]:
    dev = development_ids(split_path)
    out: list[Sample] = []
    for path in sorted(glob.glob(labels_glob)):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        vid = dev.get(data.get("video_sha256") or "")
        if vid is None:
            continue
        for screen in data.get("screens", []):
            if screen.get("status") != "verified":
                continue
            offers = screen.get("offers") or []
            for k, offer in enumerate(offers):
                snap = offer.get("snapshot")
                if not snap or not (ROOT / snap).is_file():
                    continue
                for slot, truth in enumerate(offer.get("cards") or []):
                    out.append(Sample(
                        key=f"{vid}|{screen['stage']}|{k}|{slot}",
                        video=vid, stage=screen["stage"], offer=k,
                        is_last=(k == len(offers) - 1), slot=slot,
                        truth=tuple(truth), snapshot=snap,
                    ))
    return out


def verdict(pred: list[str], truth: tuple[str, ...]) -> str:
    """dung / sai / sot. Mo ho (nhieu apiName) chi dung khi nhan cung la cap do."""
    if not pred:
        return "sot"
    p, t = set(pred), set(truth)
    if p == t or (len(p) == 1 and p <= t):
        return "dung"
    if not p & t:
        return "sai"
    return "sot"                                  # mo ho, co chua dap an nhung khong chot


# --- backend ----------------------------------------------------------------
# Moi backend: crop BGR uint8 -> danh sach dong chu theo thu tu doc.


def backend_rapidocr() -> Callable[[np.ndarray], list[str]]:
    from src.vision.ocr_engine import read_full
    from src.vision.preprocess import ocr_texts

    def read(crop: np.ndarray) -> list[str]:
        # Giong het OcrCardReader.read_slot: det + cls + rec tren ca o.
        return [t for t in ocr_texts(read_full(crop)) if t.strip()]

    return read


def backend_indra(threads: int) -> Callable[[np.ndarray], list[str]]:
    try:
        import cv2
        import indra_ocr
    except ImportError as exc:
        raise SystemExit(
            f"thiếu thư viện cho indra ({exc}). Cài vào môi trường riêng: "
            "uv pip install --python .venv-bench indra-ocr") from exc
    conv = indra_ocr.load(threads=threads, mode="ocr")

    def read(crop: np.ndarray) -> list[str]:
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        page = conv.ocr(gray)
        return [ln.text for ln in page.lines if ln.text and ln.text.strip()]

    return read


BLOCK_END = re.compile(r"</(p|div|h[1-6]|li|tr|td|th|caption)>|<br\s*/?>", re.I)
TAG = re.compile(r"<[^>]+>")


def html_lines(raw: str) -> list[str]:
    """HTML cua Chandra -> cac dong chu. Dong dau thuong la ten the."""
    text = html.unescape(TAG.sub("", BLOCK_END.sub("\n", raw)))
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def backend_chandra2(threads: int, max_tokens: int) -> Callable[[np.ndarray], list[str]]:
    """CHANDRA_URL dat -> goi endpoint OpenAI-compatible (vLLM, vd tren Modal) bang
    chinh client cua package chandra (prompt "ocr", temperature 0). Khong dat ->
    chay cuc bo bang transformers tren CPU (nang: ~10,6 GB trong so bf16)."""
    url = os.environ.get("CHANDRA_URL")
    if url:
        try:
            from PIL import Image
            from chandra.model.schema import BatchInputItem
            from chandra.model.vllm import generate_vllm
        except ImportError as exc:
            raise SystemExit(f"thiếu thư viện cho chandra2 qua URL ({exc}): "
                             "uv pip install --python .venv-bench chandra-ocr") from exc

        def read_remote(crop: np.ndarray) -> list[str]:
            img = Image.fromarray(crop[:, :, ::-1].copy())
            res = generate_vllm([BatchInputItem(image=img, prompt_type="ocr")],
                                max_output_tokens=max_tokens, vllm_api_base=url)[0]
            if res.error:
                raise RuntimeError(f"Chandra endpoint lỗi: {res.raw!r}")
            return html_lines(res.raw)

        print(f"chandra2: endpoint {url} (model {os.environ.get('VLLM_MODEL_NAME', 'chandra')})",
              flush=True)
        return read_remote

    os.environ.setdefault("TORCH_DEVICE", "cpu")
    try:
        import torch
        from PIL import Image
        from chandra.model.hf import generate_hf, load_model
        from chandra.model.schema import BatchInputItem
    except ImportError as exc:
        raise SystemExit(
            f"thiếu thư viện cho chandra2 ({exc}). Cài vào môi trường riêng: "
            "uv pip install --python .venv-bench \"chandra-ocr[hf]\" "
            "--index-url https://download.pytorch.org/whl/cpu "
            "--extra-index-url https://pypi.org/simple --index-strategy unsafe-best-match") from exc
    torch.set_num_threads(threads)
    model = load_model()                          # bf16, device_map {"": "cpu"}, prompt "ocr"
    print(f"chandra2: dtype={model.dtype} device={model.device}", flush=True)

    def read(crop: np.ndarray) -> list[str]:
        img = Image.fromarray(crop[:, :, ::-1].copy())
        with torch.inference_mode():
            res = generate_hf([BatchInputItem(image=img, prompt_type="ocr")], model,
                              max_output_tokens=max_tokens)[0]
        read.last_raw = res.raw
        return html_lines(res.raw)

    return read


# --- chay ---------------------------------------------------------------------


def done_keys(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    with path.open(encoding="utf-8", newline="") as fh:
        return {row["key"] for row in csv.DictReader(fh)}


def run(args: argparse.Namespace) -> int:
    import cv2

    samples = collect(args.labels, Path(args.split))
    if args.sample:
        samples = sorted(random.Random(args.seed).sample(samples, min(args.sample, len(samples))),
                         key=lambda s: s.key)
    regions = ScreenRegions.load(args.regions)
    index = NameIndex.load(args.name_index)

    out = Path(args.out or RUNS / f"bench_card_titles_{args.backend}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    skip = done_keys(out) if args.resume else set()
    todo = [s for s in samples if s.key not in skip]
    print(f"{args.backend}: {len(samples)} mẫu, đã có {len(samples) - len(todo)}, chạy {len(todo)}",
          flush=True)
    if not todo:
        return 0

    t0 = time.perf_counter()
    if args.backend == "rapidocr":
        read = backend_rapidocr()
    elif args.backend == "indra":
        read = backend_indra(args.threads)
    else:
        read = backend_chandra2(args.threads, args.max_tokens)
    print(f"nạp model {time.perf_counter() - t0:.1f} s", flush=True)

    frames: dict[str, np.ndarray] = {}

    def crop_of(s: Sample) -> np.ndarray:
        if s.snapshot not in frames:
            frames.clear()
            img = cv2.imread(str(ROOT / s.snapshot))
            if img is None:
                raise SystemExit(f"không đọc được {s.snapshot}")
            frames[s.snapshot] = img
        return regions.crop(frames[s.snapshot], SCREEN, f"card_text_{s.slot}")

    read(crop_of(todo[0]))                        # khoi dong, khong tinh gio
    new = not out.is_file() or not args.resume
    with out.open("w" if new else "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for i, s in enumerate(todo, 1):
            crop = crop_of(s)
            t = time.perf_counter()
            lines = read(crop)
            ms = (time.perf_counter() - t) * 1000.0
            pred = resolve_name(lines, index, "augments", FUZZY_CUTOFF)
            v = verdict(pred, s.truth)
            w.writerow({"key": s.key, "video": s.video, "stage": s.stage, "offer": s.offer,
                        "is_last": int(s.is_last), "slot": s.slot, "truth": "+".join(s.truth),
                        "lines": " | ".join(lines), "pred": "+".join(pred), "verdict": v,
                        "ms": f"{ms:.1f}"})
            fh.flush()
            if args.verbose or v != "dung" or i % 25 == 0:
                print(f"[{i}/{len(todo)}] {s.key} {v} {ms:.0f} ms  {lines[:2]} -> {pred}",
                      flush=True)
    report([str(out)])
    return 0


# --- bang tong ----------------------------------------------------------------


def _summ(rows: list[dict]) -> str:
    n = len(rows)
    if not n:
        return "0 mẫu"
    c = {k: sum(r["verdict"] == k for r in rows) for k in ("dung", "sai", "sot")}
    ms = sorted(float(r["ms"]) for r in rows)
    p95 = ms[min(n - 1, int(round(0.95 * (n - 1))))]
    return (f"n={n:4d}  đúng {c['dung']:4d} ({c['dung'] / n:6.1%})  sai {c['sai']:3d}  "
            f"sót {c['sot']:3d}  p50 {statistics.median(ms):9.1f} ms  p95 {p95:9.1f} ms")


def report(paths: list[str]) -> None:
    runs: dict[str, dict[str, dict]] = {}
    for p in paths:
        name = Path(p).stem.replace("bench_card_titles_", "")
        with open(p, encoding="utf-8", newline="") as fh:
            runs[name] = {r["key"]: r for r in csv.DictReader(fh)}
    common = set.intersection(*(set(r) for r in runs.values())) if runs else set()
    for name, rows in runs.items():
        allr = list(rows.values())
        print(f"\n== {name}")
        print(f"  mọi offer          {_summ(allr)}")
        print(f"  offer cuối         {_summ([r for r in allr if r['is_last'] == '1'])}")
        if len(runs) > 1 and len(common) < len(allr):
            print(f"  giao {len(common):3d} mẫu chung {_summ([rows[k] for k in sorted(common)])}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đo OCR tên thẻ lõi trên snapshot nhãn verified")
    ap.add_argument("--backend", choices=("rapidocr", "indra", "chandra2"))
    ap.add_argument("--report", nargs="+", metavar="CSV", help="chỉ in bảng tổng từ các CSV")
    ap.add_argument("--labels", default=str(ROOT / "data/eval/playtest/*.json"))
    ap.add_argument("--split", default=str(ROOT / "data/eval/split.json"))
    ap.add_argument("--regions", default=str(ROOT / "config/screen_regions.yaml"))
    ap.add_argument("--name-index", default=str(ROOT / "data/name_index.json"))
    ap.add_argument("--sample", type=int, default=0, help="chỉ chạy N mẫu chọn bằng --seed")
    ap.add_argument("--seed", type=int, default=20261115)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=256, help="chandra2: trần token sinh ra")
    ap.add_argument("--out", help="CSV kết quả (mặc định data/eval/runs/bench_card_titles_<backend>.csv)")
    ap.add_argument("--no-resume", dest="resume", action="store_false")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    if args.report:
        report([p for pat in args.report for p in sorted(glob.glob(pat))])
        return 0
    if not args.backend:
        ap.error("cần --backend hoặc --report")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
