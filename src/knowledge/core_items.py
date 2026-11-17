"""Bang do core theo (tuong, vai) + comp TFT Academy (docs/item-reading/core-items.md).

Sinh boi scripts/build_core_items.py -> data/core_items.json. File nay chi doc.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Iterable

DEFAULT_PATH = Path("data/core_items.json")
DEFAULT_RECIPES = Path("data/item_recipes.json")


def short_name(api: str) -> str:
    """DA_18_Aphelios / DA_Draven18 / DA_Nidalee18_AP -> Aphelios / Draven / Nidalee."""
    name = re.sub(r"^(DA_|TFT\d*_)(18_)?", "", api)
    return re.sub(r"18(_\w+)?$|_(AD|AP|Base)$", "", name)


@dataclass(frozen=True)
class CoreSet:
    items: tuple[str, ...]
    weight: float = 1.0


@dataclass(frozen=True)
class Comp:
    """Mot comp mau. `units`: apiName -> (vai, do)."""

    slug: str
    title: str
    plan: str | None
    public: bool
    carry: str | None
    damage: str | None
    units: dict[str, tuple[str, tuple[str, ...]]] = field(default_factory=dict)

    @property
    def items(self) -> Counter:
        return Counter(i for _, items in self.units.values() for i in items)


@dataclass
class CoreTable:
    champions: dict[str, dict] = field(default_factory=dict)
    comps: list[Comp] = field(default_factory=list)
    tank_items: frozenset[str] = frozenset()
    recipes: dict[str, tuple[str, ...]] = field(default_factory=dict)
    costs: dict[str, int] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path = DEFAULT_PATH,
             recipes: str | Path = DEFAULT_RECIPES) -> "CoreTable | None":
        """None khi chua sinh bang - CoreFit khi do tat, khong raise."""
        p = Path(path)
        if not p.is_file():
            return None
        data = json.loads(p.read_text(encoding="utf-8"))
        rec = json.loads(Path(recipes).read_text(encoding="utf-8"))["recipes"]
        comps = [Comp(c["slug"], c["title"], c.get("plan"), bool(c.get("public")), c.get("carry"),
                      c.get("damage"),
                      {a: (u["role"], tuple(u["items"])) for a, u in c["units"].items()})
                 for c in data["comps"]]
        champs = data["champions"]
        return cls(champs, comps, frozenset(data.get("tank_items") or ()),
                   {r["item"]: tuple(r["components"]) for r in rec},
                   {a: int(e["cost"]) for a, e in champs.items() if e.get("cost")})

    def core_sets(self, champion: str, role: str = "carry") -> list[CoreSet]:
        return [CoreSet(tuple(s["items"]), float(s.get("weight") or 1.0))
                for s in (self.champions.get(champion) or {}).get(role) or []]

    def damage(self, champion: str | None) -> str | None:
        return (self.champions.get(champion) or {}).get("damage") if champion else None

    def components_of(self, items: Iterable[str]) -> Counter:
        """Manh cua cac mon ghep (mon khong co cong thuc thi bo)."""
        return Counter(c for i in items for c in self.recipes.get(i, ()))

    def is_completed(self, item: str) -> bool:
        return item in self.recipes
