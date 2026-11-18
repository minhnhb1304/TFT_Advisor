"""Doc do chua lap tren thanh do doc o sat mep trai man hinh (docs/item-reading/bench-components.md I2).

Thanh nay la UI phang (khong phai vat 3D tren san): 10 o doc, ben trai khung toc he,
vi tri co dinh theo chieu cao man hinh va neo mep trai (do tren 1920x1080 va 1728x1080).
O trong = ben trong den phang. Phan loai bang cung `UnitItemReader.classify`; vat dac
biet (o dau co so dem, bua ren, do co dong ho...) khong co mau nen ra "chua ro" va bi bo.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .unit_items import INNER_STD_MIN, UnitItemReader

SLOTS = 10
# Toa do o 1080p: o i nam o (X, Y0 + PITCH*i), canh SIZE (gom vien 1 px).
X, Y0, PITCH, SIZE = 11, 263, 54, 42
INSET = 6


@dataclass(frozen=True)
class BenchSlot:
    index: int
    box: tuple[int, int, int]
    api_name: str | None = None
    score: float = 0.0
    margin: float = 0.0
    empty: bool = True


def slot_boxes(frame: np.ndarray) -> list[tuple[int, int, int]]:
    s = frame.shape[0] / 1080.0
    return [(round(X * s), round((Y0 + PITCH * i) * s), round(SIZE * s)) for i in range(SLOTS)]


def read_bench(frame: np.ndarray, reader: UnitItemReader) -> list[BenchSlot]:
    out = []
    for i, (x, y, size) in enumerate(slot_boxes(frame)):
        cell = frame[y:y + size, x:x + size]
        inner = cell[INSET:-INSET, INSET:-INSET]
        if inner.size == 0 or float(inner.std()) < INNER_STD_MIN:
            out.append(BenchSlot(i, (x, y, size)))
            continue
        name, score, margin, _ = reader.classify(cell)
        out.append(BenchSlot(i, (x, y, size), name, round(score, 3), round(margin, 3), empty=False))
    return out


def bench_items(frame: np.ndarray, reader: UnitItemReader) -> list[str]:
    """Cac mon doc chac duoc tren thanh do (bo o trong va o khong chac)."""
    return [s.api_name for s in read_bench(frame, reader) if s.api_name]
