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
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Sequence

from ...game_state.models import GameState
from ...knowledge.augment_features import ECON_TYPES, AugmentFeature
from .types import ComponentScore, ScoringConfig, clamp01, neutral

NAME = "plan_fit"

ECO_CATEGORIES = frozenset({"econ", "reroll"})
POWER_CATEGORIES = frozenset({"combat", "item", "trait"})
DEFAULT_WEIGHT = 0.15
DEFAULT_DEBT_BONUS = 0.05


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
    # Tu stage nay tro di dung bo trong so khac. Vd reroll da roll xong 3 sao
    # o 4-2 thi lo eco het gia tri: "du eco, thieu combat" (minh_04 4-2).
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
        )
        # Moc stage chi doi trong so; nhan, route, min_hp ke thua tu huong goc.
        stages = []
        for start, override in (data.get("by_stage") or {}).items():
            merged = {
                "label": base.label, "eco": base.eco, "power": base.power,
                "econ_type": dict(base.econ_type), "min_hp": min_hp, **(override or {}),
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
        )

    def plan_for_route(self, route: str | None) -> PlanProfile | None:
        """Huong ung voi nhan `plan.route` (vd `standard` -> fast8)."""
        if route is None:
            return None
        return next((p for p in self.plans if route in p.routes or route == p.key), None)


class PlanFitScorer:
    """Cham mot augment duoi MOT huong. 0.5 = huong nay khong co y kien."""

    def __init__(self, settings: PlanSettings) -> None:
        self.settings = settings

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
            # Strength theo econ_value; lo eco khong ghi econ_value (vd chi co
            # nhan `reroll`) van tinh nhu muc thap nhat, khong phai bang 0.
            strength = max(feature.econ_value, 1) / 3.0
            delta += plan.eco * strength
            delta += sum(plan.econ_type.get(t, 0.0) for t in feature.econ_type) * strength
        if power:
            delta += plan.power

        # Can bang HAI chieu: cam eco -> thieu suc manh, lo combat dang gia;
        # cam combat lam ban dap -> can tien de len full bai, lo eco dang gia
        # (minh_06 4-2). `debt` > 0 = nghieng eco, < 0 = nghieng combat.
        debt = sum(1 for h in held if eco_only(h)) - sum(1 for h in held if power_only(h))
        debt_delta = 0.0
        if debt > 0 and power_only(feature):
            debt_delta = self.settings.debt_bonus * debt
            parts.append(f"đã nặng kinh tế ({debt} lõi) — cần lõi combat bù sức mạnh")
        elif debt < 0 and eco_only(feature):
            debt_delta = self.settings.debt_bonus * -debt
            parts.append(f"đã có {-debt} lõi combat làm bàn đạp — cần tiền lên full bài")
        delta += debt_delta

        if eco_only(feature):
            parts.append("lõi kinh tế: phải lên full bài mới mạnh")
        elif power_only(feature):
            parts.append("lõi combat: full form là đủ")

        warning = ""
        if plan.min_hp is not None and state.hp < plan.min_hp:
            warning = f"còn {state.hp} máu — {label.lower()} rủi ro"

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
                "warning": warning,
            },
        )
