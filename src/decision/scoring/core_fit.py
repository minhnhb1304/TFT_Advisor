"""Thanh phan CoreFit: thuong manh core + chap loi, THEO TUNG HUONG.

Thiet ke: docs/item-reading/plan-item-fit.md (I3.2, I3.3, chap loi - chot 2026-11-17).

Giong PlanFit, thanh phan nay KHONG nam trong `AugmentAdvisor.scorers`: `rank()`
(va ItemFit cu, co san 0,4) giu nguyen; chi `rank_by_plan()` cong them
`weight * bonus`. Chi cong THUONG nen khong tinh trung phan san cua ItemFit.

  ung_vien(huong) = comp TFT Academy co style khop huong, giu nhom co nhieu mon
                    DA GHEP dang cam nhat; chua ghep mon nao -> moi comp cua huong;
                    khong comp nao khop mon nao -> lui ve tuong theo gia (ghi `fallback`).
  thuong(manh m)  = trung binh tren ung vien: weight bo core neu m con thieu de ghep bo do.
  chap loi        = moi ung vien cung mot loai sat thuong (AD/AP) va lose co carry_type
                    nguoc lai -> diem huong nay con `off_damage_factor` (mac dinh 15%).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from ...game_state.models import GameState
from ...knowledge.augment_features import AugmentFeature
from ...knowledge.core_items import Comp, CoreSet, CoreTable, short_name
from .board_fit import component_key
from .types import ComponentScore, ScoringConfig, clamp01, neutral

NAME = "core_fit"
ANY_GRANTS = {"AnyComponent", "Anvil"}
DAMAGE_TYPES = ("AD", "AP")


@dataclass(frozen=True)
class CoreFitSettings:
    """Khoi `tuning.core_fit` trong scoring_weights.yaml."""

    enabled: bool = False
    weight: float = 0.10
    anvil_extra: float = 0.15
    off_damage_factor: float = 0.15
    public_only: bool = True
    # Gia carry chinh cua moi huong - dung khi lui (khong comp nao khop).
    plan_costs: dict[str, tuple[int, ...]] = field(default_factory=dict)

    @classmethod
    def from_config(cls, config: ScoringConfig) -> "CoreFitSettings":
        tune = config.tune(NAME)
        return cls(
            enabled=bool(tune.get("enabled", False)),
            weight=float(tune.get("weight", 0.10)),
            anvil_extra=float(tune.get("anvil_extra", 0.15)),
            off_damage_factor=float(tune.get("off_damage_factor", 0.15)),
            public_only=bool(tune.get("public_only", True)),
            plan_costs={str(k): tuple(int(c) for c in v)
                        for k, v in (tune.get("plan_costs") or {}).items()},
        )


@dataclass(frozen=True)
class Candidates:
    comps: tuple[Comp, ...]
    fallback: bool = False
    matched: int = 0

    @property
    def damage(self) -> str | None:
        """Loai sat thuong chung cua moi ung vien; lan hoac chua ro -> None."""
        types = {c.damage for c in self.comps}
        if len(types) == 1:
            only = next(iter(types))
            return only if only in DAMAGE_TYPES else None
        return None


class CoreFit:
    """Cham mot augment duoi MOT huong theo bang core.

    `detail["bonus"]` (0-1) la phan cong vao diem huong. `score` theo quy uoc
    chung cua cac thanh phan: 0,5 = khong y kien (khong thuong), 0,5 + bonus/2
    khi cho manh core, 0 khi chap loi - de `ScoredAugment.reasons` loc dung.
    """

    def __init__(self, table: CoreTable, settings: CoreFitSettings) -> None:
        self.table = table
        self.settings = settings
        self.all_components = sorted({component_key(c) for comps in table.recipes.values()
                                      for c in comps})

    # -- ung vien ----------------------------------------------------------

    def held_completed(self, state: GameState) -> list[str]:
        return [i for i in state.completed_items if self.table.is_completed(i)]

    def candidates(self, state: GameState, plan_key: str) -> Candidates:
        comps = [c for c in self.table.comps
                 if c.plan == plan_key and (c.public or not self.settings.public_only)]
        held = Counter(self.held_completed(state))
        if not comps or not held:
            return Candidates(tuple(comps))
        matched = {c.slug: sum((held & c.items).values()) for c in comps}
        best = max(matched.values())
        if best > 0:
            return Candidates(tuple(c for c in comps if matched[c.slug] == best), matched=best)
        costs = self.settings.plan_costs.get(plan_key, ())
        pseudo = tuple(
            Comp(f"core:{api}", short_name(api), plan_key, True, api, self.table.damage(api),
                 {api: ("carry", ())})
            for api, cost in sorted(self.table.costs.items())
            if cost in costs and self.table.core_sets(api))
        return Candidates(pseudo, fallback=True)

    # -- manh con thieu ----------------------------------------------------

    def missing(self, comp: Comp, state: GameState) -> tuple[CoreSet | None, Counter]:
        """Bo core cua carry chinh gan xong nhat va cac manh con thieu cua no.
        Carry khong co dong trong bang -> dung chinh do cua no trong comp mau."""
        sets = self.table.core_sets(comp.carry) if comp.carry else []
        if not sets and comp.carry in comp.units:
            items = tuple(i for i in comp.units[comp.carry][1] if i not in self.table.tank_items)
            sets = [CoreSet(items)] if items else []
        held_items = Counter(self.held_completed(state))
        held_parts = Counter(component_key(c) for c in state.item_components)
        best: tuple[CoreSet | None, Counter] = (None, Counter())
        best_key: tuple[int, float] | None = None
        for s in sets:
            todo = Counter(s.items) - held_items
            need = Counter({component_key(c): n for c, n in self.table.components_of(todo.elements()).items()})
            need -= held_parts
            key = (sum(need.values()), -s.weight)
            if best_key is None or key < best_key:
                best, best_key = (s, need), key
        return best

    def component_bonus(self, cands: Candidates, state: GameState) -> dict[str, tuple[float, list[str]]]:
        """manh -> (thuong, cac carry dang thieu manh do kem bo core)."""
        out: dict[str, tuple[float, list[str]]] = {}
        if not cands.comps:
            return out
        acc: dict[str, float] = Counter()
        who: dict[str, list[str]] = {}
        for comp in cands.comps:
            core, need = self.missing(comp, state)
            if core is None:
                continue
            for part in need:
                acc[part] += core.weight
                label = f"{'+'.join(short_name(i) for i in core.items)} cho {short_name(comp.carry or '')}"
                who.setdefault(part, [])
                if label not in who[part]:
                    who[part].append(label)
        for part, total in acc.items():
            out[part] = (total / len(cands.comps), who[part])
        return out

    # -- cham diem ---------------------------------------------------------

    def __call__(self, api_name: str, feature: AugmentFeature | None, state: GameState,
                 plan_key: str, label: str = "") -> ComponentScore:
        label = label or plan_key
        if feature is None:
            return neutral(NAME, "Không có dữ liệu đặc trưng", plan=plan_key, bonus=0.0)
        if not state.completed_items and not state.item_components:
            # Chua doc duoc do nao: khong biet carry thieu gi, khong phat.
            return neutral(NAME, "Chưa đọc được đồ", plan=plan_key, bonus=0.0)

        cands = self.candidates(state, plan_key)
        detail: dict[str, Any] = {
            "plan": plan_key, "bonus": 0.0, "off_damage": False, "fallback": cands.fallback,
            "candidates": [c.slug for c in cands.comps][:8], "n_candidates": len(cands.comps),
        }
        dmg = cands.damage
        if (dmg and self.held_completed(state) and feature.carry_type in DAMAGE_TYPES
                and feature.carry_type != dmg):
            carries = sorted({short_name(c.carry) for c in cands.comps if c.carry})
            detail.update(off_damage=True, damage=dmg)
            reason = (f"{label}: chấp lõi — lõi {feature.carry_type}, đội hình đang theo carry "
                      f"{dmg} ({'/'.join(carries[:3])})")
            return ComponentScore(NAME, 0.0, reason, detail)

        bonus_by_part = self.component_bonus(cands, state)
        best, best_reason = 0.0, ""
        for grant in feature.item_grants:
            if grant in ANY_GRANTS:
                part = max(bonus_by_part, key=lambda p: (bonus_by_part[p][0], p), default=None)
                value = bonus_by_part[part][0] if part else 0.0
                if grant == "Anvil":
                    value = min(1.0, value + self.settings.anvil_extra)
                why = f"tự chọn {part}" if part else ""
            else:
                part = component_key(grant)
                value = bonus_by_part.get(part, (0.0, []))[0]
                why = part
            if value > best:
                ghep = bonus_by_part.get(part, (0.0, []))[1] if part else []
                best = value
                best_reason = f"{label}: cho {why}" + (
                    f", đang thiếu để ghép {', '.join(ghep[:3])}" if ghep else "")
        detail["bonus"] = round(best, 3)
        if best <= 0:
            return neutral(NAME, f"{label}: không cho mảnh core đang thiếu", **detail)
        return ComponentScore(NAME, clamp01(0.5 + 0.5 * best), best_reason, detail)
