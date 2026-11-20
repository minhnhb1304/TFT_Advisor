"""Nho do tren tuong minh giua cac lan doc (docs/item-reading/unit-items.md I1.5).

Doc trong luc CHUAN BI (ngoai man chon loi, khong co thanh mau do), toi da mot
lan moi `every_s` giay, giu lan doc gan nhat. Man chon loi che mot phan ban co
nen luc do dung lai lan doc truoc. Moi vong deu co the tra do (augment, su kien),
nen doc lai lien tuc chu khong chot mot lan.

Chi do THUONG: o khong chac (do anh sang, do tao tac, icon mo) bi bo, khong doan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any, Callable

COMPONENT_PREFIX = "DA_Component_"
# Tuong cam Gang Dao Tac khong lap them duoc do: 2 mon con lai tren tuong do la
# do ngau nhien doi moi vong, khong phai do dang cam.
THIEFS_GLOVES = "DA_ThiefsGloves"


def held_items(units: Any, bench: Any = ()) -> tuple[list[str], list[str]]:
    """(do da ghep, manh) dang cam: tren cac tuong + tren thanh do chua lap.
    Bo do ngau nhien cua Gang Dao Tac."""
    items = [i for u in units
             for i in ([THIEFS_GLOVES] if THIEFS_GLOVES in u.items else u.items)] + list(bench)
    return ([i for i in items if not i.startswith(COMPONENT_PREFIX)],
            [i for i in items if i.startswith(COMPONENT_PREFIX)])


@dataclass
class ItemTracker:
    reader: Any                                    # UnitItemReader-like: .read(image) -> [UnitItems]
    every_s: float = 5.0
    # Co thanh mau do -> giao tranh / dang xem nha khac: khong phai do cua minh luc chuan bi.
    in_combat: Callable[[Any], bool] | None = None
    # Thanh do chua lap o mep trai: image -> [apiName].
    bench: Callable[[Any], list[str]] | None = None
    completed: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    uncertain: int = 0
    last_ms: float | None = None
    _last_t: float = float("-inf")

    def reset(self) -> None:
        self.completed, self.components, self.uncertain = [], [], 0
        self._last_t = float("-inf")

    def observe(self, image: Any, t: float) -> bool:
        """Doc neu da toi luot. True khi vua cap nhat."""
        if t - self._last_t < self.every_s:
            return False
        self._last_t = t
        t0 = time.perf_counter()
        try:
            if self.in_combat is not None and self.in_combat(image):
                return False
            units = self.reader.read(image)
            if not units:
                # Khong thay tuong minh (chuyen canh...): thanh do van hien nen
                # doc rieng no se de mat do tren tuong cua lan doc truoc.
                return False
            bench = self.bench(image) if self.bench is not None else []
        except Exception:                              # noqa: BLE001 - do la phu, khong lam hong vong lap
            return False
        finally:
            self.last_ms = (time.perf_counter() - t0) * 1000.0
        self.completed, self.components = held_items(units, bench)
        self.uncertain = sum(1 for u in units for c in u.cells if c.api_name is None)
        return True

    def apply(self, state: Any) -> Any:
        """Ghi do da doc vao GameState (state tracker khong biet gi ve do)."""
        state.completed_items = list(self.completed)
        state.item_components = list(self.components)
        return state


def default_item_tracker(root: Any = ".") -> ItemTracker:
    """Bo doc that: icon CDragon + mau cat tu game (neu da co)."""
    from pathlib import Path  # noqa: PLC0415

    from ..vision.bench_items import bench_items  # noqa: PLC0415
    from ..vision.unit_items import UnitItemReader, find_health_bars  # noqa: PLC0415

    base = Path(root)
    reader = UnitItemReader(base / "data/item_icons", base / "data/item_templates")
    return ItemTracker(reader, in_combat=lambda image: bool(find_health_bars(image, own=False)),
                       bench=lambda image: bench_items(image, reader))
