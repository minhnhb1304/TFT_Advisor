"""Sinh bang do core theo (tuong, vai) tu comp TFT Academy (docs/item-reading/core-items.md I3.1).

    .venv\\Scripts\\python scripts\\build_core_items.py            # ghi data/core_items.json
    .venv\\Scripts\\python scripts\\build_core_items.py --report   # in bang de duyet

Vao: data/tftacademy_guides.json (crawl_tftacademy_guides.py), data/item_recipes.json,
data/cdragon_cache/en_us.json. Khong go tay tuong nao: cac vi du cua nguoi choi
(Tristana/Kayle Guinsoo, Ahri Gang + Shojin, Aphelios phu LW + Red Buff) la test.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

DEFENSIVE = {"DA_Component_ChainVest", "DA_Component_NegatronCloak", "DA_Component_GiantsBelt"}
DEFENSE_STATS = {"Armor", "MagicResist", "Health", "BonusPercentHP", "FrontlineResists"}
OFFENSE_STATS = {"AD", "AP", "AS", "CritChance"}
# style TFT Academy -> huong (`plan_fit.plans`). "Lose Streak" ~ "Thieu tien" de sau.
STYLE_PLAN = {"1-Cost Reroll": "reroll", "2-Cost Reroll": "reroll", "3-Cost Reroll": "reroll",
              "4-Cost Fast 8": "fast8", "Fast 9": "fast9"}
# Mot mon la do tank khi >= nua so lan no nam tren tuong cam >= 2 mon ma da
# so la do tank (diem bat dong cua vong lap). Xuat phat: do ghep tu 2 manh thu,
# va do chi co chi so thu (giap/khang/mau) ma khong co chi so cong (CDragon).
TANK_SHARE = 0.5
MIN_HOLDS = 3
# Mon b di kem mon neo a thanh mot bo khi hai mon "di cung nhau" ca hai chieu:
# P(b|a) va P(a|b) >= PAIR (Ahri: Shojin 5/6 lan cung Gang), va cung xuat hien
# >= PAIR_MIN_CO comp: 2 lan chua tach duoc "luon di cung" khoi "tinh co"
# (Kayle: Rabadon 2/3 comp Guinsoo -> core van chi la Guinsoo).
PAIR = 0.6
PAIR_MIN_CO = 3
# Bo chi phu 1 comp la nhieu (core-items.md buoc 4).
MIN_SUPPORT = 2


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dedupe(guides: list[dict]) -> list[dict]:
    """Bo comp trung y het (ban '-copy' khong sua gi) de khong dem hai lan."""
    seen, out = set(), []
    for g in guides:
        key = tuple(sorted((u["apiName"], tuple(sorted(u["items"]))) for u in g["final"]))
        if key not in seen:
            seen.add(key)
            out.append(g)
    return out


def tank_items(units: list[list[str]], recipes: dict[str, list[str]],
               stats: dict[str, dict] | None = None) -> set[str]:
    """Do tank suy tu cach TFT Academy chia do, khong liet ke tay."""
    stats = stats or {}
    seed = {i for i, comps in recipes.items() if all(c in DEFENSIVE for c in comps)}
    seed |= {i for i in recipes if DEFENSE_STATS & set(stats.get(i, {}))
             and not OFFENSE_STATS & set(stats.get(i, {}))}
    tank = set(seed)
    multi = [u for u in units if len(u) >= 2]
    while True:
        holders = [u for u in multi if 2 * sum(i in tank for i in u) >= len(u)]
        hold = Counter(i for u in multi for i in u)
        on = Counter(i for u in holders for i in u)
        new = seed | {i for i, n in hold.items() if n >= MIN_HOLDS and on[i] >= TANK_SHARE * n}
        if new == tank:
            return tank
        tank = new


def is_tank_unit(items: list[str], tank: set[str]) -> bool:
    return bool(items) and 2 * sum(i in tank for i in items) >= len(items)


def damage_items(items: list[str], tank: set[str]) -> list[str]:
    return [i for i in items if i not in tank and "Emblem" not in i]


def assign_roles(guide: dict, recipes: dict, tank: set[str]) -> dict[str, tuple[str, list[str]]]:
    """apiName -> (vai, do). Carry chinh = mainChampion neu no cam >= 2 do sat
    thuong, khong thi tuong cam nhieu do sat thuong nhat. Ai cam do sat thuong
    con lai la carry phu. `mainChampion` mot minh khong du (5/74 la tank)."""
    roles: dict[str, tuple[str, list[str]]] = {}
    holders = []
    for u in guide["final"]:
        items = [i for i in u["items"] if i in recipes]
        if not items:
            continue
        if is_tank_unit(items, tank):
            roles[u["apiName"]] = ("tank", items)
        elif damage_items(items, tank):
            holders.append((u["apiName"], items))
    holders.sort(key=lambda h: (h[0] != guide["main"] or len(damage_items(h[1], tank)) < 2,
                                -len(damage_items(h[1], tank))))
    for k, (api, items) in enumerate(holders):
        roles[api] = ("carry" if k == 0 else "secondary", items)
    return roles


def core_sets(rows: list[list[str]], popularity: Counter) -> list[dict]:
    """Phu cac comp bang it bo nhat. Neo = mon co mat nhieu nhat trong comp chua
    phu; ghep them mon di cung hai chieu neu co. Lap voi comp chua phu."""
    left = [set(r) for r in rows if r]
    out = []
    while left:
        sup = Counter(i for r in left for i in r)
        anchor = max(sup, key=lambda i: (sup[i], popularity[i], i))
        if sup[anchor] < MIN_SUPPORT:
            break
        with_a = [r for r in left if anchor in r]
        items = (anchor,)
        co = Counter(i for r in with_a for i in r if i != anchor)
        for b in sorted(co, key=lambda i: (-co[i], -popularity[i], i)):
            if co[b] >= PAIR_MIN_CO and co[b] >= PAIR * len(with_a) and co[b] >= PAIR * sup[b]:
                items = (anchor, b)
                break
        covered = [r for r in left if set(items) <= r]
        out.append({"items": sorted(items), "comps": len(covered)})
        left = [r for r in left if not set(items) <= r]
    top = max((s["comps"] for s in out), default=1)
    for s in out:
        s["weight"] = round(s["comps"] / top, 2)
    return out


def ability_damage(champions: dict[str, dict]) -> dict[str, str]:
    """AD/AP cua tuong: hau to ten (`_AD`/`_AP`), roi bieu tuong scale trong mo ta ky nang."""
    out = {}
    for api, c in champions.items():
        m = re.search(r"_(AD|AP)$", api)
        if m:
            out[api] = m.group(1)
            continue
        votes = Counter(re.findall(r"%i:scale(AD|AP)%", (c.get("ability") or {}).get("desc") or ""))
        if votes["AD"] != votes["AP"]:
            out[api] = "AD" if votes["AD"] > votes["AP"] else "AP"
    return out


def item_stats(items: dict[str, dict]) -> dict[str, dict]:
    """Chi so cua mon DA_: lay tu ban TFT_Item_ cung ten (ban DA_ khong co effects)."""
    by_name: dict[str, dict] = {}
    for it in items.values():
        if not it["apiName"].startswith("DA_") and it.get("effects") and it.get("name"):
            by_name.setdefault(it["name"], it["effects"])
    return {api: by_name.get(it.get("name")) or {} for api, it in items.items()}


def item_damage(stats: dict[str, dict]) -> dict[str, str]:
    """AD/AP cua mon ghep theo chi so; co ca hai hoac khong co thi bo."""
    out = {}
    for api, eff in stats.items():
        ad, ap = "AD" in eff, "AP" in eff
        if ad != ap:
            out[api] = "AD" if ad else "AP"
    return out


def apply_overrides(table: dict[str, dict], overrides: dict[str, dict]) -> None:
    """Dong nguoi choi da duyet thay han dong may sinh (theo tung truong cua tuong)."""
    for api, fields in overrides.items():
        entry = table.setdefault(api, {})
        for key, value in fields.items():
            if key in ("note", "verified"):
                continue
            if key in ("carry", "secondary"):
                value = [{"items": sorted(s["items"]), "comps": s.get("comps"),
                          "weight": s.get("weight", 1.0), "source": "override"} for s in value]
            entry[key] = value


def build(guides: list[dict], recipes: dict[str, list[str]], cdragon: dict,
          overrides: dict[str, dict] | None = None) -> dict:
    guides = dedupe(guides)
    stats = item_stats({i["apiName"]: i for i in cdragon.get("items") or []})
    units = [[i for i in u["items"] if i in recipes] for g in guides for u in g["final"]]
    tank = tank_items([u for u in units if u], recipes, stats)

    rows: dict[tuple[str, str], list[list[str]]] = defaultdict(list)
    comps = []
    for g in guides:
        roles = assign_roles(g, recipes, tank)
        for api, (role, items) in roles.items():
            rows[(api, role)].append(damage_items(items, tank) if role != "tank" else items)
        comps.append({"slug": g["slug"], "title": g["title"], "style": g["style"],
                      "plan": STYLE_PLAN.get(g["style"] or ""), "public": g["public"],
                      "tier": g["tier"],
                      "units": {api: {"role": r, "items": items} for api, (r, items) in roles.items()}})

    popularity = Counter(i for (api, role), rs in rows.items() if role == "carry" for r in rs for i in r)
    champs = {c["apiName"]: c for b in cdragon.get("setData") or [] if b.get("mutator") == "TFTSet18"
              for c in b.get("champions") or []}
    by_ability = ability_damage(champs)
    by_item = item_damage(stats)

    table: dict[str, dict] = {}
    for (api, role), rs in sorted(rows.items()):
        if role == "tank":
            continue
        sets = core_sets(rs, popularity)
        if sets:
            table.setdefault(api, {})[role] = sets
    for api, entry in table.items():
        dmg = by_ability.get(api)
        if dmg is None:
            votes = Counter(by_item.get(i) for r in rows.get((api, "carry"), []) + rows.get((api, "secondary"), [])
                            for i in r)
            if votes["AD"] != votes["AP"]:
                dmg = "AD" if votes["AD"] > votes["AP"] else "AP"
        entry["damage"] = dmg
        entry["cost"] = champs.get(api, {}).get("cost")
    apply_overrides(table, overrides or {})

    for comp in comps:
        carry = next((a for a, u in comp["units"].items() if u["role"] == "carry"), None)
        comp["carry"] = carry
        comp["damage"] = table.get(carry, {}).get("damage") if carry else None

    return {"tank_items": sorted(tank), "champions": table, "comps": comps}


def report(data: dict) -> None:
    short = lambda i: i.replace("DA_", "")  # noqa: E731
    print("Đồ tank (suy từ cách chia đồ):", ", ".join(map(short, data["tank_items"])))
    for api, e in data["champions"].items():
        for role in ("carry", "secondary"):
            if role in e:
                sets = " / ".join("+".join(map(short, s["items"])) + f" ({s['comps']})" for s in e[role])
                print(f"{short(api):22s} {e.get('damage') or '?':3s} {role:10s} {sets}")
    n = len(data["comps"])
    miss = sum(1 for c in data["comps"] if not c["damage"])
    print(f"{n} comp, {miss} comp không rõ AD/AP của carry chính")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--guides", default=str(ROOT / "data/tftacademy_guides.json"))
    ap.add_argument("--out", default=str(ROOT / "data/core_items.json"))
    ap.add_argument("--overrides", default=str(ROOT / "data/core_items.overrides.json"),
                    help="dòng bạn đã duyệt, đè lên dòng máy sinh")
    ap.add_argument("--report", action="store_true", help="chỉ in bảng, không ghi file")
    args = ap.parse_args(argv)

    src = load_json(Path(args.guides))
    recipes = {r["item"]: r["components"] for r in load_json(ROOT / "data/item_recipes.json")["recipes"]}
    over = Path(args.overrides)
    overrides = load_json(over)["champions"] if over.is_file() else {}
    data = build(src["guides"], recipes, load_json(ROOT / "data/cdragon_cache/en_us.json"), overrides)
    if args.report:
        report(data)
        return 0
    data = {"meta": {"source": "tftacademy (data/tftacademy_guides.json) + cdragon en_us",
                     "patch": src["meta"].get("patch"), "guides_fetched_at": src["meta"].get("fetched_at"),
                     "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "pair": PAIR, "min_support": MIN_SUPPORT}, **data}
    Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ghi {Path(args.out).relative_to(ROOT)}: {len(data['champions'])} tướng có core, "
          f"{len(data['comps'])} comp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
