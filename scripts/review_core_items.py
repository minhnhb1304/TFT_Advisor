"""Trang duyet bang do core (docs/item-reading/core-items.md): xem, sua, luu thang vao overrides.

    .venv\\Scripts\\python scripts\\review_core_items.py            # mo http://127.0.0.1:8767

Moi tuong: bo core may sinh (kem so comp ung ho), loai sat thuong, va cac comp TFT
Academy lam bang chung. Ban sua bo / AD-AP / ghi chu, danh dau "da duyet" roi Luu:
chi truong KHAC may sinh (cung "da duyet" + ghi chu) duoc ghi vao
data/core_items.overrides.json, roi bang data/core_items.json duoc sinh lai.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_core_items  # noqa: E402
from review_item_labels import item_options  # noqa: E402

OVERRIDES = ROOT / "data/core_items.overrides.json"
TABLE = ROOT / "data/core_items.json"
PAGE = Path(__file__).with_suffix(".html")
ROLES = ("carry", "secondary")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def generated() -> dict:
    """Bang may sinh KHONG co dong da duyet - de trang so sanh."""
    recipes = {r["item"]: r["components"] for r in load(ROOT / "data/item_recipes.json")["recipes"]}
    return build_core_items.build(load(ROOT / "data/tftacademy_guides.json")["guides"], recipes,
                                  load(ROOT / "data/cdragon_cache/en_us.json"))


def champion_names() -> dict[str, str]:
    data = load(ROOT / "data/cdragon_cache/vi_vn.json")
    out: dict[str, str] = {}
    for s in data.get("setData") or []:
        if s.get("mutator") == "TFTSet18":
            for c in s.get("champions") or []:
                out[c["apiName"]] = c.get("name") or c["apiName"]
    return out


def state() -> dict:
    gen = generated()
    over = load(OVERRIDES) if OVERRIDES.is_file() else {"champions": {}}
    recipes = {r["item"] for r in load(ROOT / "data/item_recipes.json")["recipes"]}
    return {
        "generated": gen["champions"],
        "overrides": over.get("champions") or {},
        "comps": gen["comps"],
        "tank_items": gen["tank_items"],
        "names": champion_names(),
        "items": [o for o in item_options() if o["api"] in recipes],
        "path": OVERRIDES.relative_to(ROOT).as_posix(),
    }


def clean(payload: dict) -> tuple[dict, list[str]]:
    """Kiem tra du lieu trang gui ve; chi giu truong hop le."""
    known = {o["api"] for o in item_options()}
    out, errors = {}, []
    for api, row in (payload.get("champions") or {}).items():
        entry = {}
        for role in ROLES:
            if role in row:
                sets = [sorted(s["items"]) for s in row[role] if s.get("items")]
                bad = [i for s in sets for i in s if i not in known]
                if bad:
                    errors.append(f"{api}: món lạ {bad}")
                entry[role] = [{"items": s} for s in sets]
        if "damage" in row:
            if row["damage"] not in ("AD", "AP", None):
                errors.append(f"{api}: AD/AP sai ({row['damage']})")
            entry["damage"] = row["damage"]
        if row.get("note"):
            entry["note"] = str(row["note"])
        if row.get("verified"):
            entry["verified"] = True
        if entry:
            out[api] = entry
    return out, errors


def save(champions: dict) -> str:
    over = load(OVERRIDES) if OVERRIDES.is_file() else {}
    over["champions"] = champions
    over.setdefault("note", "Dòng người chơi (Challenger) đã duyệt, đè lên dòng build_core_items.py sinh.")
    OVERRIDES.write_text(json.dumps(over, ensure_ascii=False, indent=1), encoding="utf-8")
    build_core_items.main([])
    return f"đã lưu {len(champions)} tướng vào {OVERRIDES.relative_to(ROOT).as_posix()}, sinh lại {TABLE.name}"


def make_handler():
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
                return self._json(200, state())
            if self.path.startswith("/file/"):
                target = (ROOT / self.path[len("/file/"):]).resolve()
                if not target.is_file() or ROOT not in target.parents or target.suffix != ".png":
                    return self._send(404, b"not found", "text/plain")
                return self._send(200, target.read_bytes(), "image/png")
            self._send(404, b"not found", "text/plain")

        def do_POST(self) -> None:                  # noqa: N802
            if self.path != "/api/save":
                return self._json(404, {"error": "không có endpoint này"})
            payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            champions, errors = clean(payload)
            if errors:
                return self._json(200, {"ok": False, "errors": errors[:20]})
            msg = save(champions)
            print(msg, flush=True)
            return self._json(200, {"ok": True, "message": msg})

    return Handler


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8767)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args(argv)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler())
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Mở {url} để duyệt bảng core. Ctrl+C để dừng.")
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nđã dừng.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
