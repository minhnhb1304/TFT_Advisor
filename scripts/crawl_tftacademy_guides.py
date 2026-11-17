"""Luu comp TFT Academy GIU DO TUNG TUONG + bang bac do (docs/item-reading/core-items.md I3.1).

    .venv\\Scripts\\python scripts\\crawl_tftacademy_guides.py

Ghi hai file (commit ca hai - 18.6 la patch cuoi, chi crawl mot lan):
    data/tftacademy_guides.json  : moi comp: style, tier, mainChampion, finalComp/earlyComp
                                   (do tung tuong), altBuilds, carousel
    data/item_tiers.json         : bac S/A/B/C cua do ghep va an (chi do thuong: bo
                                   bang do anh sang / do Ornn - ngoai pham vi)

`crawl_tftacademy_comps.py` (-> MetaComp) bo mat do tung tuong; file nay khong
thay no, chi giu phan ma bang do core can.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import requests

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
HOST = "https://tftacademy.com/api/tierlist"
USER_AGENT = "TFT-Agent-Thesis/0.1 (research build)"
UNIT_KEYS = ("apiName", "items", "stars")
# Chi do thuong (chot 2026-11-17); TFT Academy con co "radiants", "ornns".
TIER_TYPES = ("craftables", "emblems")


def _get(url: str) -> dict:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    resp.raise_for_status()
    return resp.json()


def _units(rows) -> list[dict]:
    return [{k: r.get(k) for k in UNIT_KEYS} | {"items": list(r.get("items") or [])}
            for r in rows or [] if isinstance(r, dict) and r.get("apiName")]


def trim_guide(g: dict) -> dict:
    """Chi giu truong bang do core can; bo tips/augments (da co o meta_comps)."""
    return {
        "slug": g.get("compSlug"),
        "title": g.get("title"),
        "tier": g.get("tier"),
        "style": g.get("style"),
        "main": (g.get("mainChampion") or {}).get("apiName"),
        "final": _units(g.get("finalComp")),
        "early": _units(g.get("earlyComp")),
        "alt": _units(g.get("altBuilds")),
        "carousel": [c.get("apiName") for c in g.get("carousel") or [] if isinstance(c, dict)],
        "public": bool(g.get("isPublic", True)),
        "updated": g.get("updated"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--set", type=int, default=18)
    ap.add_argument("--patch", default="18.6")
    ap.add_argument("--guides-out", default=str(ROOT / "data/tftacademy_guides.json"))
    ap.add_argument("--tiers-out", default=str(ROOT / "data/item_tiers.json"))
    args = ap.parse_args(argv)

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # Giu ca comp da go khoi tier list (public=false, comp cua cac ban 18.x
    # truoc): do hop tuong khong doi theo ban nen van la bang chung cho bang
    # core; ung vien theo huong chi lay comp public (mau chuan hien tai).
    guides = [trim_guide(g) for g in _get(f"{HOST}/comps?set={args.set}")["guides"]
              if isinstance(g, dict)]
    guides.sort(key=lambda g: (g["style"] or "", g["slug"] or ""))
    Path(args.guides_out).write_text(json.dumps(
        {"meta": {"source": f"{HOST}/comps?set={args.set}", "patch": args.patch,
                  "fetched_at": now, "n": len(guides)}, "guides": guides},
        ensure_ascii=False, indent=1), encoding="utf-8")

    tiers = {}
    for block in _get(f"{HOST}/items?set={args.set}").get("items_tierlists") or []:
        if block.get("type") not in TIER_TYPES:
            continue
        tiers[block["type"]] = {
            t: list(v) for t, v in sorted((block.get("tier") or {}).items())}
    Path(args.tiers_out).write_text(json.dumps(
        {"meta": {"source": f"{HOST}/items?set={args.set}", "patch": args.patch,
                  "fetched_at": now}, "tiers": tiers},
        ensure_ascii=False, indent=1), encoding="utf-8")

    public = sum(g["public"] for g in guides)
    print(f"{len(guides)} comp ({public} public) -> {Path(args.guides_out).relative_to(ROOT)}")
    print("bậc đồ: " + ", ".join(f"{k} ({sum(map(len, v.values()))})" for k, v in tiers.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
