"""Thanh phan PlanFit: do hop cua augment voi MOT huong di (directional augment).

Thiet ke: docs/directional-augment/plan-conditioned-advice.md (chot 2026-11-13).

He thong KHONG doan nguoi choi di huong nao - khong co bo doc ban co, va o 4-2
fast8 voi fast9 trong giong het nhau. Thay vao do, moi man chon augment cham
diem MOT LAN CHO MOI HUONG, roi nguoi choi tu chon dong cua minh. Day la
`Score(a | phi)` cua docs/directional-augment/architecture.md buoc 4, hien
tung phi thay vi gop bang belief.

Thanh phan nay KHONG nam trong `AugmentAdvisor.scorers`: `rank()` giu nguyen
tung byte, va do chinh la dong doi chung cua ablation. Chi `rank_by_plan()`
cong them no.

Hai luat cua nguoi choi (tung Thach Dau VN), deu la LUA CHON chua fit tren du
lieu:

  - Loai augment (combat / eco) TRUC GIAO voi huong. Eco khong bat buoc cho
    fast 9; no doi CACH di toi tran. 3 eco phai "full bai" (core 2 sao, reroll
    3 sao) moi manh; 3 combat chi can "full form" (du doi hinh 1 sao).
  - Vi vay moi augment eco DA CAM la mot khoan "no suc manh" ban co phai tra:
    augment combat o man sau duoc cong theo so no do (`debt_bonus`).
  - Combo / ki nhau / loi rui ro giua loi ung vien va loi da cam: bang
    data/augment_combos.json (augment_combos.py), muc manh `combo_strength`.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any, Sequence

from ...game_state.models import GameState
from ...knowledge.augment_features import ECON_TYPES, AugmentFeature
from .types import ComponentScore, ScoringConfig, clamp01, neutral

if TYPE_CHECKING:
    from .augment_combos import ComboTable

NAME = "plan_fit"

ECO_CATEGORIES = frozenset({"econ", "reroll"})
POWER_CATEGORIES = frozenset({"combat", "item", "trait"})
DEFAULT_WEIGHT = 0.15
DEFAULT_DEBT_BONUS = 0.05
# Cam tu chung nay loi combat tro len thi dong du kinh te uu tien them combat.
COMBAT_STACK = 2
# Don vi TONG DIEM (khong nhan weight): ~1/2, 1, 2 lan khoang cach top-1/top-2
# trung vi tren dev (0.039, do 2026-11-18).
DEFAULT_COMBO_STRENGTH = {"info": 0.0, "light": 0.02, "medium": 0.04, "strong": 0.08}


def is_eco(feature: AugmentFeature) -> bool:
    """Augment cho tai nguyen (vang/XP/roll)."""
    return feature.econ_value > 0 or bool(ECO_CATEGORIES & set(feature.categories))


def is_power(feature: AugmentFeature) -> bool:
    """Augment cho suc manh truc tiep (chi so, trang bi, toc he)."""
    return bool(POWER_CATEGORIES & set(feature.categories))


def eco_only(feature: AugmentFeature) -> bool:
    return is_eco(feature) and not is_power(feature)


def power_only(feature: AugmentFeature) -> bool:
    return is_power(feature) and not is_eco(feature)


@dataclass(frozen=True)
class PlanProfile:
    """Mot huong di va cach no dinh gia augment. Doc tu `tuning.plan_fit.plans`."""

    key: str
    label: str
    eco: float = 0.0
    power: float = 0.0
    econ_type: dict[str, float] = field(default_factory=dict)
    # Nhan `plan.route` trong file nhan playtest anh xa vao huong nay.
    routes: tuple[str, ...] = ()
    # Duoi muc mau nay thi dong cua huong nay kem canh bao (khong doi diem).
    min_hp: int | None = None
    # Dong "thieu tien": nguoi choi tu nhan la thieu kinh te (cach B, 2026-11-18).
    short_on_cash: bool = False
    # Tu stage nay tro di dung bo trong so khac. Vd reroll da roll xong 3 sao
    # o 4-2 thi loi eco het gia tri: "du eco, thieu combat" (minh_04 4-2).
    by_stage: tuple[tuple[int, "PlanProfile"], ...] = ()

    def at_stage(self, stage_number: int) -> "PlanProfile":
        """Bo trong so ap dung o stage nay (moc lon nhat <= stage)."""
        active = self
        for start, profile in sorted(self.by_stage, key=lambda x: x[0]):
            if stage_number >= start:
                active = profile
        return active

    @classmethod
    def from_config(cls, key: str, data: dict[str, Any]) -> "PlanProfile":
        econ_type = {str(k): float(v) for k, v in (data.get("econ_type") or {}).items()}
        unknown = set(econ_type) - set(ECON_TYPES)
        if unknown:
            raise ValueError(f"plan '{key}': econ_type không hợp lệ {sorted(unknown)}")
        min_hp = data.get("min_hp")
        base = cls(
            key=key,
            label=str(data.get("label") or key),
            eco=float(data.get("eco", 0.0)),
            power=float(data.get("power", 0.0)),
            econ_type=econ_type,
            routes=tuple(str(r) for r in data.get("routes") or ()),
            min_hp=int(min_hp) if min_hp is not None else None,
            short_on_cash=bool(data.get("short_on_cash", False)),
        )
        # Moc stage chi doi trong so; nhan, route, min_hp ke thua tu huong goc.
        stages = []
        for start, override in (data.get("by_stage") or {}).items():
            merged = {
                "label": base.label, "eco": base.eco, "power": base.power,
                "econ_type": dict(base.econ_type), "min_hp": min_hp,
                "short_on_cash": base.short_on_cash, **(override or {}),
            }
            stages.append((int(start), cls.from_config(key, merged)))
        return replace(base, by_stage=tuple(stages))


@dataclass(frozen=True)
class PlanSettings:
    """Khoi `tuning.plan_fit` trong scoring_weights.yaml."""

    enabled: bool = False
    weight: float = DEFAULT_WEIGHT
    debt_bonus: float = DEFAULT_DEBT_BONUS
    plans: tuple[PlanProfile, ...] = ()
    # Muc nhe/vua/manh cua luat combo; rong = gia tri mac dinh cua augment_combos.
    combo_strength: dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_config(cls, config: ScoringConfig) -> "PlanSettings":
        tune = config.tune(NAME)
        plans = tuple(
            PlanProfile.from_config(str(k), v or {}) for k, v in (tune.get("plans") or {}).items()
        )
        return cls(
            enabled=bool(tune.get("enabled", False)),
            weight=float(tune.get("weight", DEFAULT_WEIGHT)),
            debt_bonus=float(tune.get("debt_bonus", DEFAULT_DEBT_BONUS)),
            plans=plans,
            combo_strength={str(k): float(v) for k, v in (tune.get("combo_strength") or {}).items()},
        )

    def plan_for_route(self, route: str | None) -> PlanProfile | None:
        """Huong ung voi nhan `plan.route` (vd `standard` -> fast8)."""
        if route is None:
            return None
        return next((p for p in self.plans if route in p.routes or route == p.key), None)


class PlanFitScorer:
    """Cham mot augment duoi MOT huong. 0.5 = huong nay khong co y kien."""

    def __init__(self, settings: PlanSettings, combos: "ComboTable | None" = None) -> None:
        self.settings = settings
        self.combos = combos

    def __call__(
        self,
        api_name: str,
        feature: AugmentFeature | None,
        state: GameState,
        plan: PlanProfile,
        held: Sequence[AugmentFeature] = (),
    ) -> ComponentScore:
        if feature is None:
            return neutral(NAME, "Không có dữ liệu đặc trưng cho augment này", plan=plan.key)

        label = plan.label
        plan = plan.at_stage(state.stage_number)
        delta = 0.0
        parts: list[str] = []
        eco, power = is_eco(feature), is_power(feature)
        if eco:
            # Strength theo econ_value; loi eco khong ghi econ_value (vd chi co
            # nhan `reroll`) van tinh nhu muc thap nhat, khong phai bang 0.
            strength = max(feature.econ_value, 1) / 3.0
            delta += plan.eco * strength
            delta += sum(plan.econ_type.get(t, 0.0) for t in feature.econ_type) * strength
        if power:
            delta += plan.power

        # Can bang HAI chieu: cam eco -> thieu suc manh, loi combat dang gia;
        # cam combat lam ban dap -> can tien de len full bai, loi eco dang gia
        # (minh_06 4-2). `debt` > 0 = nghieng eco, < 0 = nghieng combat.
        # Rieng khi da cam >= 2 loi combat (nguoi choi, 2026-11-18): du kinh te ->
        # them combat; thieu kinh te -> eco. "Thieu" = dong `short_on_cash`
        # nguoi choi tu chon, KHONG doc tu HUD (cach A con can nghien cuu).
        combat_held = sum(1 for h in held if power_only(h))
        debt = sum(1 for h in held if eco_only(h)) - combat_held
        stack_combat = combat_held >= COMBAT_STACK and not plan.short_on_cash
        debt_delta = 0.0
        if debt > 0 and power_only(feature):
            debt_delta = self.settings.debt_bonus * debt
            parts.append(f"đã nặng kinh tế ({debt} lõi) — cần lõi combat bù sức mạnh")
        elif debt < 0 and stack_combat and power_only(feature):
            debt_delta = self.settings.debt_bonus * -debt
            parts.append(f"đã {combat_held} lõi combat, đủ kinh tế — thêm combat")
        elif debt < 0 and not stack_combat and eco_only(feature):
            debt_delta = self.settings.debt_bonus * -debt
            parts.append(f"đã có {-debt} lõi combat làm bàn đạp — cần tiền lên full bài")
        delta += debt_delta

        warnings: list[str] = []
        combo_delta = 0.0
        if self.combos is not None:
            effect = self.combos.effect(feature, held, plan.key,
                                        {**DEFAULT_COMBO_STRENGTH, **self.settings.combo_strength})
            # Khong vao `delta`: rank_by_plan() cong thang vao tong diem.
            combo_delta = effect.delta
            parts.extend(effect.reasons)
            warnings.extend(effect.warnings)

        if eco_only(feature):
            parts.append("lõi kinh tế: phải lên full bài mới mạnh")
        elif power_only(feature):
            parts.append("lõi combat: full form là đủ")

        if plan.min_hp is not None and state.hp < plan.min_hp:
            warnings.insert(0, f"còn {state.hp} máu — {label.lower()} rủi ro")
        warning = " · ".join(warnings)

        reason = f"{label}: " + (" · ".join(parts) if parts else "không có ý kiến riêng")
        return ComponentScore(
            NAME,
            clamp01(0.5 + delta),
            reason,
            {
                "plan": plan.key,
                "eco": eco,
                "power": power,
                "debt": debt,
                "debt_delta": round(debt_delta, 3),
                "combo_delta": round(combo_delta, 3),
                "warning": warning,
                "warnings": warnings,
            },
        )
