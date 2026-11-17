"""Tai icon cua moi mon trong bang cong thuc ve data/item_icons/<apiName>.png.

    python scripts/fetch_item_icons.py            # chi tai icon con thieu
    python scripts/fetch_item_icons.py --force    # tai lai het

Icon dung de doc do duoi thanh mau tuong (docs/item-reading/unit-items.md).
Danh sach mon = moi mon ghep + manh trong `data/item_recipes.json` (gom ca an),
cung cach resolve duong dan voi `fetch_augment_icons.py`.
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
sys.path.insert(0, str(ROOT / "scripts"))

from fetch_augment_icons import USER_AGENT, icon_fields, is_placeholder  # noqa: E402
from src.knowledge.cdragon_client import CDragonClient  # noqa: E402


def recipe_items(path: Path) -> set[str]:
    """Moi apiName xuat hien trong bang cong thuc: mon ghep va manh."""
    recipes = json.loads(path.read_text(encoding="utf-8"))["recipes"]
    return {r["item"] for r in recipes} | {c for r in recipes for c in r["components"]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--recipes", default=str(ROOT / "data/item_recipes.json"))
    ap.add_argument("--locale", default=str(ROOT / "data/cdragon_cache/en_us.json"))
    ap.add_argument("--out", default=str(ROOT / "data/item_icons"))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    wanted = recipe_items(Path(args.recipes))
    fields = icon_fields(Path(args.locale), wanted)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    fetched = skipped = 0
    failed: list[str] = []
    placeholders = sorted(a for a, icon in fields.items() if is_placeholder(icon))
    for api_name, icon in sorted(fields.items()):
        if api_name in placeholders:
            continue
        target = out / f"{api_name}.png"
        if target.exists() and not args.force:
            skipped += 1
            continue
        try:
            req = urllib.request.Request(CDragonClient.icon_url(icon),
                                         headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as resp:
                target.write_bytes(resp.read())
            fetched += 1
        except OSError as exc:
            failed.append(f"{api_name}: {exc}")

    missing = sorted(wanted - set(fields))
    print(f"tải {fetched} · đã có {skipped} · lỗi {len(failed)} · không có icon {len(missing)}"
          f" · icon giữ chỗ (bỏ) {len(placeholders)}")
    for line in failed[:10] + [f"{m}: không có trường icon" for m in missing] + placeholders:
        print("  " + line)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
