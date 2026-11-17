"""Doc do tren tuong cua minh: 3 icon duoi thanh mau xanh (docs/item-reading/unit-items.md).

Do tren minh_06 (1080p, 2026-11-17): icon ~23 px co vien den 1 px, hang icon
nam ngay duoi thanh mau (dinh icon ~ +10 px so voi dinh phan xanh), buoc 25 px.
Thanh mau xanh = tuong cua minh, ke ca tuong tren hang cho.

Bo doc KHONG suy o icon tu mep trai phan xanh: tuong mat mau hay bi hieu ung de
thi phan xanh ngan lai / bi cat, va do lech ca hai o (minh_06 giay 1085). Thay
vao do no quet hang ngay duoi thanh mau tim cac o vuong vien den.

Phan loai bang NCC voi mau. Mau lay tu GAME (`data/item_templates/<apiName>/`,
cat tu khung da gan nhan) la chinh; icon CDragon chi la du phong vi khac net
ve trong game va bi so cong don de len. Khong chac thi tra None.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np

# Nguong mau thanh mau xanh (BGR), do tren minh_06; giong TFT-Copilot / Agente-TFT.
GREEN_MIN = 110
GREEN_OVER_RED = 1.65
GREEN_OVER_BLUE = 1.5
# Kich thuoc o 1080p, nhan voi chieu cao khung / 1080.
BAR_H = (3, 6)
BAR_MIN_W = 6
# Do sang trung binh toi da cua khung toi quanh phan xanh.
FRAME_DARK_MAX = 70
CELL = 23
CELL_STEP = 25.5
# Goc o dau tien so voi goc tren trai phan xanh, va do xe dich cho phep.
SLOT_DX = -5
SLOT_DY_RANGE = (8, 13)
SLOT_JITTER = 3
# Vien icon den: do sang < DARK_MAX tren >= BORDER_MIN cua vien. Do tren minh_06:
# o co do 0,67-0,91 (o vien olive cua do dac biet thap nhat), o trong <= 0,53.
DARK_MAX = 45
BORDER_MIN = 0.6
# O co icon phai co noi dung (o vien den nhung ben trong phang = nen toi).
INNER_STD_MIN = 12.0
MAX_ITEMS = 3
MATCH_SIZE = 21
# Nguong tra loi; chinh tren bo nhan dev (docs/item-reading/evaluation.md).
MIN_SCORE = 0.55
MIN_MARGIN = 0.08
DEFAULT_ICON_DIR = Path("data/item_icons")
DEFAULT_TEMPLATE_DIR = Path("data/item_templates")


@dataclass(frozen=True)
class Bar:
    """Phan xanh cua thanh mau (pixel khung goc)."""

    x: int
    y: int
    w: int
    h: int


@dataclass(frozen=True)
class ItemCell:
    """Mot o icon duoi thanh mau. `api_name` None = khong chac."""

    x: int
    y: int
    size: int
    api_name: str | None = None
    score: float = 0.0
    margin: float = 0.0
    candidates: tuple[tuple[str, float], ...] = ()


@dataclass(frozen=True)
class UnitItems:
    bar: Bar
    cells: tuple[ItemCell, ...] = field(default_factory=tuple)

    @property
    def items(self) -> list[str]:
        """Cac mon doc chac duoc (bo o khong chac)."""
        return [c.api_name for c in self.cells if c.api_name]

    @property
    def uncertain(self) -> bool:
        return any(c.api_name is None for c in self.cells)


def scale_of(frame: np.ndarray) -> float:
    return frame.shape[0] / 1080.0


def find_health_bars(frame: np.ndarray) -> list[Bar]:
    """Phan xanh cua moi thanh mau tuong minh, tren -> duoi, trai -> phai."""
    s = scale_of(frame)
    b, g, r = (frame[..., i].astype(np.int32) for i in range(3))
    mask = ((g > GREEN_MIN) & (g * 100 > GREEN_OVER_RED * 100 * r)
            & (g * 100 > GREEN_OVER_BLUE * 100 * b)).astype(np.uint8)
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bars = [Bar(int(x), int(y), int(w), int(h)) for x, y, w, h, _ in stats[1:n]
            if BAR_H[0] * s <= h <= BAR_H[1] * s and w >= BAR_MIN_W * s and w > 3 * h
            and _framed(gray, int(x), int(y), int(w), int(h))]
    return sorted(bars, key=lambda bar: (bar.y, bar.x))


def _framed(gray: np.ndarray, x: int, y: int, w: int, h: int) -> bool:
    """Thanh mau that nam trong khung toi: hang ngay tren va ngay duoi phan xanh toi.
    Loai cac vet xanh le tren san dau / giao dien (minh_06 giay 105: vet 7x2 px)."""
    if y < 2 or y + h + 2 > gray.shape[0]:
        return False
    above = gray[y - 2:y, x:x + w]
    below = gray[y + h:y + h + 2, x:x + w]
    return float(above.mean()) < FRAME_DARK_MAX and float(below.mean()) < FRAME_DARK_MAX


def _border_dark(dark: np.ndarray, size: int) -> np.ndarray:
    """Ti le pixel toi tren vien o vuong `size` dat tai moi goc (y, x) hop le."""
    ii = np.pad(dark.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))

    def box(y0, x0, h, w):
        return ii[y0 + h, x0 + w] - ii[y0, x0 + w] - ii[y0 + h, x0] + ii[y0, x0]

    H, W = dark.shape
    ys, xs = np.mgrid[0:H - size + 1, 0:W - size + 1]
    outer = box(ys, xs, size, size)
    inner = box(ys + 1, xs + 1, size - 2, size - 2)
    return (outer - inner) / float(4 * size - 4)


def find_item_cells(frame: np.ndarray, bar: Bar) -> list[tuple[int, int, int]]:
    """Cac o co icon (x, y, size) duoi mot thanh mau, trai -> phai.

    Mau giam thi phan xanh ngan lai tu ben PHAI, mep trai dung yen, nen 3 o
    neo theo mep trai (do: o dau o +(-5, +10), buoc 25-26). Moi o duoc xe dich
    toi da SLOT_JITTER px ngang va SLOT_DY_RANGE doc de khop vien den. Do lap
    tu trai sang, nen gap o trong dau tien thi dung: vung toi o o 2 ma o 1
    trong la nen (vien khung thanh mau, than tuong), khong phai icon.
    """
    s = scale_of(frame)
    size = max(8, round(CELL * s))
    jit = max(1, round(SLOT_JITTER * s))
    cells: list[tuple[int, int, int]] = []
    for k in range(MAX_ITEMS):
        bx = bar.x + round((SLOT_DX + k * CELL_STEP) * s)
        x0, x1 = bx - jit, bx + jit + size
        y0 = bar.y + round(SLOT_DY_RANGE[0] * s)
        y1 = bar.y + round(SLOT_DY_RANGE[1] * s) + size
        if x0 < 0 or y0 < 0 or x1 > frame.shape[1] or y1 > frame.shape[0]:
            continue
        gray = cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
        score = _border_dark(gray < DARK_MAX, size)
        yy, xx = np.unravel_index(int(np.argmax(score)), score.shape)
        if (score[yy, xx] < BORDER_MIN
                or gray[yy + 2:yy + size - 2, xx + 2:xx + size - 2].std() < INNER_STD_MIN):
            break
        cells.append((int(x0 + xx), int(y0 + yy), size))
    return cells


def _unit(x: np.ndarray) -> np.ndarray:
    x = x - x.mean()
    n = float(np.linalg.norm(x))
    return x / n if n > 1e-6 else x


def _features(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(ca icon, 3/5 phia tren) da chuan hoa - so cong don chi de nua duoi."""
    x = cv2.resize(img, (MATCH_SIZE, MATCH_SIZE), interpolation=cv2.INTER_AREA).astype(np.float32)
    return _unit(x), _unit(x[: MATCH_SIZE * 3 // 5])


class UnitItemReader:
    """Tim thanh mau -> tim o icon -> phan loai tung o."""

    def __init__(self, icon_dir: Path | str = DEFAULT_ICON_DIR,
                 template_dir: Path | str = DEFAULT_TEMPLATE_DIR,
                 min_score: float = MIN_SCORE, min_margin: float = MIN_MARGIN,
                 names: Iterable[str] | None = None) -> None:
        self.min_score = min_score
        self.min_margin = min_margin
        allowed = set(names) if names is not None else None
        self.templates: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {}
        for path in sorted(Path(icon_dir).glob("*.png")):
            if allowed is None or path.stem in allowed:
                img = cv2.imread(str(path))
                if img is not None:
                    # Icon CDragon khong co vien; trong game vien 1 px nam ngoai net ve.
                    self.templates.setdefault(path.stem, []).append(_features(img))
        tdir = Path(template_dir)
        if tdir.is_dir():
            for path in sorted(tdir.glob("*/*.png")):
                name = path.parent.name
                if allowed is not None and name not in allowed:
                    continue
                img = cv2.imread(str(path))
                if img is not None:
                    self.templates.setdefault(name, []).append(_features(img[1:-1, 1:-1]))

    def classify(self, cell: np.ndarray) -> tuple[str | None, float, float, tuple[tuple[str, float], ...]]:
        """(apiName | None, diem, khoang cach voi ung vien thu hai, top-3)."""
        full, top = _features(cell[1:-1, 1:-1])
        ranked = []
        for name, temps in self.templates.items():
            best = max(max(float((full * tf).sum()), float((top * tt).sum())) for tf, tt in temps)
            ranked.append((best, name))
        ranked.sort(reverse=True)
        if not ranked:
            return None, 0.0, 0.0, ()
        score = ranked[0][0]
        margin = score - (ranked[1][0] if len(ranked) > 1 else 0.0)
        top3 = tuple((n, round(sc, 3)) for sc, n in ranked[:3])
        ok = score >= self.min_score and margin >= self.min_margin
        return (ranked[0][1] if ok else None), score, margin, top3

    def read(self, frame: np.ndarray) -> list[UnitItems]:
        units = []
        for bar in find_health_bars(frame):
            cells = []
            for x, y, size in find_item_cells(frame, bar):
                name, score, margin, top3 = self.classify(frame[y:y + size, x:x + size])
                cells.append(ItemCell(x, y, size, name, round(score, 3), round(margin, 3), top3))
            units.append(UnitItems(bar, tuple(cells)))
        return units
