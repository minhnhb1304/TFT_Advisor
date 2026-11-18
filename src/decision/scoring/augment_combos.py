"""Luat combo lo cua nguoi choi (data/augment_combos.json) cho PlanFit.

Giai thich: docs/directional-augment/augment-combos.md. Moi luat la LUA CHON
cua nguoi choi (tung Thach Dau VN), chua fit tren du lieu; muc manh nhe/vua/
manh doi ra so o `tuning.plan_fit.combo_strength`.

Nhom lo khai bao bang danh sach api (`apis`), nhan (`category`) hoac mon duoc
tang (`grant`). Ham o day khong biet trong so cua huong; chi tra delta + ly do.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from itertools import permutations
from pathlib import Path
from typing import Any, Mapping, Sequence

from ...knowledge.augment_features import AugmentFeature
from .plan_fit import DEFAULT_COMBO_STRENGTH, eco_only, is_eco

TRIAD_AXES = ("eco", "item", "combat")


def axes(feature: AugmentFeature) -> set[str]:
    """Truc ma lo phu trong bo 'eco - item - combat'."""
    cats = set(feature.categories)
    out = set()
    if is_eco(feature):
        out.add("eco")
    if "item" in cats:
        out.add("item")
    if cats & {"combat", "trait"}:
        out.add("combat")
    return out


@dataclass(frozen=True)
class ComboEffect:
    delta: float = 0.0
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ComboTable:
    def __init__(self, data: Mapping[str, Any]) -> None:
        self.groups: dict[str, dict] = dict(data.get("groups") or {})
        self.pairs: list[dict] = list(data.get("pairs") or [])
        self.conflicts: list[dict] = list(data.get("conflicts") or [])
        self.eco_pair: dict | None = data.get("eco_pair")
        self.triad: dict | None = data.get("triad")
        self.risky: dict[str, dict] = {r["api"]: r for r in data.get("risky") or []}
        for rule in self.pairs + self.conflicts:
            for side in ("a", "b"):
                if rule[side] not in self.groups:
                    raise ValueError(f"combo '{rule['id']}': không có nhóm '{rule[side]}'")

    @classmethod
    def load(cls, path: Path) -> "ComboTable | None":
        if not path.is_file():
            return None
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def member(self, group: str, feature: AugmentFeature) -> bool:
        g = self.groups[group]
        if "apis" in g:
            return feature.api_name in g["apis"]
        if "category" in g:
            return g["category"] in feature.categories
        if "grant" in g:
            return g["grant"] in feature.item_grants
        if "frontline" in g:
            return feature.frontline == g["frontline"]
        return False

    def _partner(self, rule: dict, cand: AugmentFeature,
                 held: Sequence[AugmentFeature]) -> AugmentFeature | None:
        """Lo da cam ghep voi ung vien theo luat, neu co.

        Mac dinh hai chieu; `one_way` = `a` phai cam TRUOC, ung vien la `b`.
        """
        for h in held:
            if h.api_name == cand.api_name:
                continue
            if ((self.member(rule["b"], cand) and self.member(rule["a"], h))
                    or (not rule.get("one_way")
                        and self.member(rule["a"], cand) and self.member(rule["b"], h))):
                return h
        return None

    def effect(self, cand: AugmentFeature, held: Sequence[AugmentFeature], plan_key: str,
               strength: Mapping[str, float] = DEFAULT_COMBO_STRENGTH) -> ComboEffect:
        delta, reasons, warnings = 0.0, [], []
        for rule in self.pairs:
            h = self._partner(rule, cand, held)
            if h is not None:
                delta += strength[rule["strength"]]
                reasons.append(f"combo với {h.name or h.api_name}: {rule['reason']}")
        for rule in self.conflicts:
            h = self._partner(rule, cand, held)
            if h is not None:
                delta -= strength[rule["strength"]]
                reasons.append(f"kị {h.name or h.api_name}: {rule['reason']}")

        rule = self.eco_pair
        if rule and plan_key in rule["avoid_plans"]:
            # "2 loi kinh te (tien - xp)": chi dem loi thuan eco co vang/XP.
            def money(f: AugmentFeature) -> bool:
                return eco_only(f) and bool(set(f.econ_type) & set(rule["econ_types"]))
            if sum(1 for h in held if money(h)) + money(cand) >= 2:
                warnings.append(rule["warning"])
                if money(cand):
                    delta -= strength[rule["strength"]]

        rule = self.triad
        if rule and len(held) == 2:
            # Lo chi tra thuong khi thang du (Warpath) khong dem vao truc nao.
            conditional = {c["api"] for c in rule.get("conditional") or ()}
            covers = [set() if f.api_name in conditional else axes(f)
                      for f in (held[0], held[1], cand)]
            if any(all(ax in c for ax, c in zip(order, covers))
                   for order in permutations(TRIAD_AXES)):
                delta += strength[rule["strength"]]
                reasons.append(rule["reason"])

        rule = self.risky.get(cand.api_name)
        if rule:
            warnings.append(rule["warning"])
            only = rule.get("only_plans")
            if only and plan_key not in only:
                delta -= strength[rule["strength"]]
        return ComboEffect(delta, reasons, warnings)
