"""Tom tat do tre tu log live (data/live_logs/*.jsonl) thanh bang p50 / p95 / max.

run_live.py ghi moi su kien vao data/live_logs/<phien>.jsonl. Script nay gom lai de tra loi
"doc HUD khi game chay mat bao lau" bang so do that, khong phai uoc luong.

    .venv\\Scripts\\python tools\\live_latency_report.py                 # moi phien
    .venv\\Scripts\\python tools\\live_latency_report.py --game-only     # bo phien mo phong video
    .venv\\Scripts\\python tools\\live_latency_report.py data\\live_logs\\live-20261116-*.jsonl

Lan doc HUD dau moi phien gom ca thoi gian nap OCR nen tach rieng ("nap OCR"), khong tron
vao p50/p95. Phien ghi truoc khi co dong "Session" (truoc 2026-11-16) hien nguon "?".
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "data" / "live_logs"


def percentile(values: list[float], q: float) -> float:
    """Phan vi kieu nearest-rank: luon la mot gia tri da do, khong noi suy."""
    ordered = sorted(values)
    rank = max(1, math.ceil(q / 100.0 * len(ordered)))
    return ordered[rank - 1]


def read_session(path: Path) -> dict:
    """Doc mot file jsonl -> nguon, so man chon loi theo stage, cac mau do tre."""
    session = {"file": path.name, "source": "?", "stages": [], "hud_first": None,
               "samples": {"hud": [], "step (màn chọn lõi)": [], "cards": [], "gate": [],
                           "advise": []}}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("type") == "Session":
            session["source"] = record.get("source", "?")
            continue
        if "hud_ms" in record:
            if session["hud_first"] is None:
                session["hud_first"] = record["hud_ms"]
            else:
                session["samples"]["hud"].append(record["hud_ms"])
        if record.get("type") == "AdviceReady":
            session["stages"].append(record.get("stage"))
            session["samples"]["step (màn chọn lõi)"].append(record["step_ms"])
        for key, value in (record.get("latency_ms") or {}).items():
            session["samples"].setdefault(key, []).append(value)
    return session


def print_table(title: str, samples: dict[str, list[float]], hud_first: list[float]) -> None:
    print(f"\n{title}")
    print(f"  {'khâu':<22}{'n':>5}{'p50 ms':>10}{'p95 ms':>10}{'max ms':>10}")
    for name, values in samples.items():
        if not values:
            continue
        print(f"  {name:<22}{len(values):>5}{percentile(values, 50):>10.0f}"
              f"{percentile(values, 95):>10.0f}{max(values):>10.0f}")
    if hud_first:
        print(f"  {'hud (nạp OCR, lần 1)':<22}{len(hud_first):>5}"
              f"{percentile(hud_first, 50):>10.0f}{'':>10}{max(hud_first):>10.0f}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tóm tắt độ trễ từ log live")
    ap.add_argument("logs", nargs="*", help="file jsonl (mặc định: mọi file trong data/live_logs)")
    ap.add_argument("--game-only", action="store_true", help="chỉ phiên chạy trên game thật")
    args = ap.parse_args(argv)

    paths = [Path(p) for p in args.logs] or sorted(LOG_DIR.glob("*.jsonl"))
    sessions = [read_session(p) for p in paths]
    if args.game_only:
        sessions = [s for s in sessions if s["source"] == "game"]
    if not sessions:
        print("Không có phiên nào để tóm tắt.")
        return 1

    print(f"{'phiên':<34}{'nguồn':<22}{'màn chọn lõi'}")
    for s in sessions:
        stages = ", ".join(str(x) for x in s["stages"]) or "-"
        print(f"{s['file']:<34}{s['source']:<22}{len(s['stages'])} ({stages})")

    merged: dict[str, list[float]] = {}
    for s in sessions:
        for key, values in s["samples"].items():
            merged.setdefault(key, []).extend(values)
    hud_first = [s["hud_first"] for s in sessions if s["hud_first"] is not None]
    sources = {s["source"] for s in sessions}
    print_table(f"Gộp {len(sessions)} phiên (nguồn: {', '.join(sorted(sources))})", merged, hud_first)
    if "?" in sources or any(x.startswith("video:") for x in sources):
        print("\n  Lưu ý: có phiên mô phỏng hoặc không rõ nguồn; số game thật dùng --game-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
