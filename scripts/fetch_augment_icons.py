"""Tai icon cua moi lo trong bang dac trung ve data/augment_icons/<apiName>.png.

    python scripts/fetch_augment_icons.py            # chi tai icon con thieu
    python scripts/fetch_augment_icons.py --force    # tai lai het

Icon dung de doc dai lo DA CHON o huong 10 gio tren man hinh
(src/vision/held_augments.py). Duong dan lay tu truong `icon` cua CDragon
(cache `data/cdragon_cache/en_us.json`), doi `.tex` -> `.png` bang
`CDragonClient.icon_url` - cung cach da resolve dung 36/36 trait.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import urllib.request

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.knowledge.cdragon_client import CDragonClient  # noqa: E402

USER_AGENT = "TFT_Agent/augment-icons"


def icon_fields(locale_path: Path, wanted: set[str]) -> dict[str, str]:
    """apiName -> truong `icon` (.tex) cho cac lo trong `wanted`."""
    data = json.loads(locale_path.read_text(encoding="utf-8"))
    return {
        str(it["apiName"]): str(it["icon"])
        for it in data.get("items") or []
        if it.get("apiName") in wanted and it.get("icon")
    }


def is_placeholder(icon: str) -> bool:
    """CDragon tro ~40 lo chua co icon vao `hexcore/missing-t1|t2|t3.tex` - mot
    hinh chu "T" dung chung. Tai ve thi moi lo do trong giong nhau va sai."""
    return Path(icon).stem.lower().startswith("missing")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--features", default=str(ROOT / "data/augment_features.json"))
    ap.add_argument("--locale", default=str(ROOT / "data/cdragon_cache/en_us.json"))
    ap.add_argument("--out", default=str(ROOT / "data/augment_icons"))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    rows = json.loads(Path(args.features).read_text(encoding="utf-8"))["augments"]
    wanted = {r["api_name"] for r in (rows.values() if isinstance(rows, dict) else rows)}
    fields = icon_fields(Path(args.locale), wanted)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    fetched = skipped = 0
    failed: list[str] = []
    placeholders = sorted(a for a, icon in fields.items() if is_placeholder(icon))
    for api_name in placeholders:
        (out / f"{api_name}.png").unlink(missing_ok=True)
    for api_name, icon in sorted(fields.items()):
        if api_name in placeholders:
            continue
        target = out / f"{api_name}.png"
        if target.exists() and not args.force:
            skipped += 1
            continue
        url = CDragonClient.icon_url(icon)
        try:
            # CDragon tra 403 cho User-Agent mac dinh cua urllib.
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as resp:
                target.write_bytes(resp.read())
            fetched += 1
        except OSError as exc:
            failed.append(f"{api_name}: {exc}")

    missing = sorted(wanted - set(fields))
    print(f"tải {fetched} · đã có {skipped} · lỗi {len(failed)} · không có icon trong CDragon"
          f" {len(missing)} · icon giữ chỗ 'missing' (bỏ) {len(placeholders)}")
    for line in failed[:10] + [f"{m}: không có trường icon" for m in missing]:
        print("  " + line)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
