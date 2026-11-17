"""Nhan do tren tuong (I4, docs/item-reading/evaluation.md): chon khung, may dien truoc, ban sua.

    # 1. Chon khung tu video development, chay bo doc, ghi file nhan dien san
    .venv\\Scripts\\python scripts\\review_item_labels.py build --per-video 7
    # 2. Mo trang review (127.0.0.1) de sua va danh dau da kiem
    .venv\\Scripts\\python scripts\\review_item_labels.py serve
    # 3. Cat o da kiem lam mau trong game cho bo doc
    .venv\\Scripts\\python scripts\\review_item_labels.py templates

Chi lay video role=development trong split.json. Khung chon theo nhip `--step` giay,
giu khung co >= `--min-cells` o icon, roi lay deu theo thoi gian `--per-video` khung.
Anh khung luu o data/eval/items/frames/ (khong commit); file nhan thi commit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.vision.unit_items import UnitItemReader  # noqa: E402

LABELS = ROOT / "data/eval/items/unit_items.json"
FRAMES = ROOT / "data/eval/items/frames"
TEMPLATES = ROOT / "data/item_templates"
VIDEO_DIR = Path(r"D:\workspace\tft_record")
PAGE = Path(__file__).with_suffix(".html")
# Nhan dac biet ngoai apiName: o bat nham (khong phai icon) / do khong co trong bang.
NOT_ITEM, OTHER = "__not_item__", "__other__"


def item_options() -> list[dict]:
    """apiName + ten tieng Viet/Anh cho moi mon co icon."""
    names: dict[str, dict] = {}
    for loc in ("vi_vn", "en_us"):
        data = json.loads((ROOT / f"data/cdragon_cache/{loc}.json").read_text(encoding="utf-8"))
        for it in data.get("items") or []:
            names.setdefault(it["apiName"], {})[loc] = it.get("name") or ""
    out = []
    for icon in sorted((ROOT / "data/item_icons").glob("*.png")):
        n = names.get(icon.stem, {})
        out.append({"api": icon.stem, "vi": n.get("vi_vn", ""), "en": n.get("en_us", ""),
                    "icon": icon.relative_to(ROOT).as_posix()})
    return out


def dev_videos(split: Path) -> list[str]:
    data = json.loads(split.read_text(encoding="utf-8"))
    return [v["video_id"] for v in data["videos"] if v["role"] == "development"]


def unit_rows(units) -> list[dict]:
    return [{"bar": [u.bar.x, u.bar.y, u.bar.w, u.bar.h],
             "cells": [{"box": [c.x, c.y, c.size], "pred": c.api_name, "score": c.score,
                        "candidates": [list(x) for x in c.candidates], "label": c.api_name}
                       for c in u.cells]}
            for u in units]


def build(args) -> int:
    reader = UnitItemReader()
    FRAMES.mkdir(parents=True, exist_ok=True)
    old = json.loads(LABELS.read_text(encoding="utf-8")) if LABELS.is_file() else {"frames": []}
    kept = {f["id"]: f for f in old["frames"] if f.get("verified")}
    frames = list(kept.values())
    for vid in args.videos or dev_videos(ROOT / "data/eval/split.json"):
        cap = cv2.VideoCapture(str(VIDEO_DIR / f"{vid}.mp4"))
        if not cap.isOpened():
            print(f"{vid}: không mở được video, bỏ qua")
            continue
        duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / (cap.get(cv2.CAP_PROP_FPS) or 60)
        hits = []
        t = args.start
        while t < duration:
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, frame = cap.read()
            if not ok:
                break
            units = reader.read(frame)
            n = sum(len(u.cells) for u in units)
            if n >= args.min_cells:
                hits.append((t, frame, units))
            t += args.step
        cap.release()
        pick = [hits[round(i * (len(hits) - 1) / max(1, args.per_video - 1))]
                for i in range(min(args.per_video, len(hits)))] if hits else []
        for t, frame, units in pick:
            fid = f"{vid}@{t:.0f}"
            if fid in kept:
                continue
            image = FRAMES / f"{vid}_{t:.0f}.jpg"
            cv2.imwrite(str(image), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            frames.append({"id": fid, "video": vid, "t": round(t, 1),
                           "image": image.relative_to(ROOT).as_posix(),
                           "size": [frame.shape[1], frame.shape[0]],
                           "verified": False, "missed": 0, "note": "",
                           "units": unit_rows(units)})
        print(f"{vid}: {len(hits)} khung có đồ, lấy {len(pick)}")
    frames.sort(key=lambda f: (f["video"], f["t"]))
    LABELS.parent.mkdir(parents=True, exist_ok=True)
    LABELS.write_text(json.dumps({"version": 1, "frames": frames}, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    print(f"ghi {LABELS.relative_to(ROOT)}: {len(frames)} khung ({len(kept)} đã kiểm giữ nguyên)")
    return 0


def templates(args) -> int:
    data = json.loads(LABELS.read_text(encoding="utf-8"))
    count = 0
    for f in data["frames"]:
        if not f.get("verified") or (args.exclude and f["video"] in args.exclude):
            continue
        image = cv2.imread(str(ROOT / f["image"]))
        if image is None:
            print(f"thiếu ảnh {f['image']}, bỏ qua")
            continue
        for u, unit in enumerate(f["units"]):
            for k, cell in enumerate(unit["cells"]):
                label = cell.get("label")
                if not label or label in (NOT_ITEM, OTHER):
                    continue
                x, y, s = cell["box"]
                out = TEMPLATES / label / f"{f['id'].replace('@', '_')}_{u}_{k}.png"
                out.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(out), image[y:y + s, x:x + s])
                count += 1
    print(f"ghi {count} mẫu vào {TEMPLATES.relative_to(ROOT)}")
    return 0


def make_handler(options: list[dict]):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args) -> None:      # noqa: D102
            pass

        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, data) -> None:
            self._send(code, json.dumps(data, ensure_ascii=False).encode("utf-8"),
                       "application/json; charset=utf-8")

        def do_GET(self) -> None:                   # noqa: N802
            if self.path in ("/", "/index.html"):
                return self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            if self.path == "/api/state":
                data = json.loads(LABELS.read_text(encoding="utf-8"))
                return self._json(200, {"labels": data, "options": options,
                                        "special": {"not_item": NOT_ITEM, "other": OTHER},
                                        "path": LABELS.relative_to(ROOT).as_posix()})
            if self.path.startswith("/file/"):
                target = (ROOT / self.path[len("/file/"):]).resolve()
                if not target.is_file() or ROOT not in target.parents:
                    return self._send(404, b"not found", "text/plain")
                ctype = "image/png" if target.suffix == ".png" else "image/jpeg"
                return self._send(200, target.read_bytes(), ctype)
            self._send(404, b"not found", "text/plain")

        def do_POST(self) -> None:                  # noqa: N802
            if self.path != "/api/save":
                return self._json(404, {"error": "không có endpoint này"})
            payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            known = {o["api"] for o in options} | {NOT_ITEM, OTHER}
            errors = [f"{f['id']}: ô {u}.{k} chưa có nhãn hợp lệ"
                      for f in payload.get("frames", []) if f.get("verified")
                      for u, unit in enumerate(f["units"])
                      for k, cell in enumerate(unit["cells"]) if cell.get("label") not in known]
            if errors:
                return self._json(200, {"ok": False, "errors": errors[:20]})
            LABELS.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
            verified = sum(1 for f in payload["frames"] if f.get("verified"))
            print(f"đã lưu — {verified}/{len(payload['frames'])} khung đã kiểm", flush=True)
            return self._json(200, {"ok": True, "verified": verified})

    return Handler


def serve(args) -> int:
    if not LABELS.is_file():
        print("chưa có file nhãn — chạy `build` trước")
        return 1
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(item_options()))
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Mở {url} để sửa nhãn đồ. Ctrl+C để dừng.")
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nđã dừng.")
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Nhãn đồ trên tướng: chọn khung, review, cắt mẫu")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--videos", nargs="*", help="mặc định: mọi video development")
    b.add_argument("--per-video", type=int, default=7)
    b.add_argument("--step", type=float, default=15.0)
    b.add_argument("--start", type=float, default=60.0)
    b.add_argument("--min-cells", type=int, default=2)
    s = sub.add_parser("serve")
    s.add_argument("--port", type=int, default=8766)
    s.add_argument("--no-browser", action="store_true")
    t = sub.add_parser("templates")
    t.add_argument("--exclude", nargs="*", help="video không lấy mẫu (để đo chéo)")
    args = ap.parse_args(argv)
    return {"build": build, "serve": serve, "templates": templates}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
