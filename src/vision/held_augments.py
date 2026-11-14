"""Doc dai lo DA CHON (huong 10 gio tu tam man hinh) - directional augment, viec A.

Sau moi man chon augment, client hien lo vua chon thanh mot icon ~37 px (o
1080p) tren nen den, xep trai -> phai theo thu tu chon, ca dai nam giua quanh
x~511, y~245 va no ra hai ben khi them icon. Do tren 15 man development
(2026-11-14): vi tri on dinh. Dai 10 gio LUON la lo CUA MINH, ke ca khi dang
xem nha khac hay dang giao tranh; lo cua doi thu hien o huong 2 GIO (nguoi choi
xac nhan 2026-11-14).

Bo doc nay KHONG nhan dien giua 250 lo. No:
  1. tim dai nen den, dem so icon (`find_strip`);
  2. so icon MOI NHAT voi icon cua dung cac lo vua duoc chao (`classify`) -
     bai toan chon 1 trong 3, khong phai 1 trong 250.

Mau so sanh lay tu CHINH THE LO tren man chon (`card_icon`), icon CDragon chi
la du phong. Do tren minh_06 3-2: icon CDragon cua Bonus Gift+ la chu "T",
con trong game la dong xu "?" - so voi CDragon khop 0,38 (sai), so voi the
khop 0,83 va cach lo ke tiep 0,52.

Khong chac thi tra None. Doan sai mot lo da cam lam lech luat can bang va
combo cho ca phan con lai cua van.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import cv2
import numpy as np

from ..capture.regions import anchor_x

# Vung tim dai, ti le khung 16:9 neo giua (x0, x1, y0, y1). Rong hon dai that
# nhieu: 16:10 dich ban co mot chut so voi phep neo giua (dat_01).
SEARCH_BOX = (0.14, 0.42, 0.16, 0.30)
# Nen icon: den gan tuyet doi. Ban co Set 18 khong co mang toi den muc nay
# trong vung tim (do tren 15 man, nen xanh/tim/la deu > 60).
DARK_MAX = 40
# Kich thuoc o icon theo chieu cao khung (37 px / 1080).
CELL_MIN, CELL_MAX = 0.026, 0.044
MAX_ICONS = 5
# Ti le nen den trong khoi sau khi dong. Icon bac (silver) ve day hon icon
# vang: do duoc 0,82-0,84 (minh_04, dat_01), icon vang ~0,9.
MIN_FILL = 0.70
DEFAULT_ICON_DIR = Path("data/augment_icons")
MATCH_SIZE = 32
# Icon lon tren the lo o man chon (ti le khung 16:9, neo giua): tam x cua ba
# o, khoang y, nua canh theo chieu cao. Do tren minh_06 3-2 (1080p) va kiem
# lai tren dat_01 (16:10) va the kim cuong minh_04 4-2.
CARD_ICON_X = (0.2865, 0.5, 0.7135)
CARD_ICON_Y = (0.324, 0.454)
CARD_ICON_HALF = 0.0648
# Do khop toi thieu va khoang cach toi thieu voi ung vien thu hai.
MIN_SCORE = 0.35
MIN_MARGIN = 0.08


@dataclass(frozen=True)
class Strip:
    """Dai icon tim duoc: so icon va anh tung o (BGR), trai -> phai."""

    icons: tuple[np.ndarray, ...]
    box: tuple[int, int, int, int]          # left, top, right, bottom tren khung

    @property
    def count(self) -> int:
        return len(self.icons)


def _search_area(image: np.ndarray) -> tuple[np.ndarray, int, int]:
    h, w = image.shape[:2]
    x0, x1, y0, y1 = SEARCH_BOX
    left = max(0, int(anchor_x(x0, w, h, "center")))
    right = min(w, int(anchor_x(x1, w, h, "center")))
    top, bottom = int(y0 * h), int(y1 * h)
    return image[top:bottom, left:right], left, top


def find_strip(image: np.ndarray) -> Strip | None:
    """Tim dai nen den chua icon lo. None = khong thay (dang o man khac, loading...)."""
    area, ox, oy = _search_area(image)
    if area.size == 0:
        return None
    h = image.shape[0]
    cell_min, cell_max = CELL_MIN * h, CELL_MAX * h
    dark = (area.max(axis=2) <= DARK_MAX).astype(np.uint8)
    # Hinh ve vang trong icon la lo thung tren nen den: dong lai de ca dai
    # thanh mot khoi.
    k = max(3, int(cell_min * 0.35)) | 1
    closed = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    n, _, stats, _ = cv2.connectedComponentsWithStats(closed, connectivity=4)

    best: tuple[float, tuple[int, int, int, int], int] | None = None
    for i in range(1, n):
        x, y, bw, bh, area_px = stats[i]
        if not cell_min <= bh <= cell_max:
            continue
        count = int(round(bw / bh))
        if not 1 <= count <= MAX_ICONS or abs(bw / bh - count) > 0.25:
            continue
        fill = area_px / float(bw * bh)
        if fill < MIN_FILL:
            continue
        # Uu tien khoi vuong van nhat (sai lech ti le nho nhat).
        err = abs(bw / bh - count)
        if best is None or err < best[0]:
            best = (err, (int(x), int(y), int(bw), int(bh)), count)
    if best is None:
        return None

    _, (x, y, bw, bh), count = best
    cell = bw / count
    icons = tuple(
        area[y:y + bh, int(round(x + i * cell)):int(round(x + (i + 1) * cell))].copy()
        for i in range(count)
    )
    return Strip(icons, (ox + x, oy + y, ox + x + bw, oy + y + bh))


def card_icon(image: np.ndarray, slot: int) -> np.ndarray:
    """Icon lon tren the lo o o `slot` (0-2) cua man chon lo."""
    h, w = image.shape[:2]
    cx = int(anchor_x(CARD_ICON_X[slot], w, h, "center"))
    half = int(CARD_ICON_HALF * h)
    return image[int(CARD_ICON_Y[0] * h):int(CARD_ICON_Y[1] * h), max(0, cx - half):cx + half].copy()


def _prep(image: np.ndarray) -> np.ndarray:
    """Chuan hoa de so: xam, cung kich thuoc, cat vien 10% (vien khung khac nhau)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    gray = cv2.resize(gray, (MATCH_SIZE, MATCH_SIZE), interpolation=cv2.INTER_AREA)
    m = MATCH_SIZE // 10
    core = gray[m:-m, m:-m].astype(np.float32)
    core -= core.mean()
    norm = float(np.linalg.norm(core))
    return core / norm if norm > 1e-6 else core


class IconBank:
    """Icon CDragon da nap, theo apiName. Nap luoi, mot lan moi lo."""

    def __init__(self, icon_dir: str | Path = DEFAULT_ICON_DIR) -> None:
        self.icon_dir = Path(icon_dir)
        self._cache: dict[str, np.ndarray | None] = {}

    def get(self, api_name: str) -> np.ndarray | None:
        if api_name not in self._cache:
            path = self.icon_dir / f"{api_name}.png"
            image = cv2.imread(str(path), cv2.IMREAD_COLOR) if path.exists() else None
            self._cache[api_name] = _prep(image) if image is not None else None
        return self._cache[api_name]


@dataclass(frozen=True)
class IconMatch:
    api_name: str | None                    # None = khong du chac
    score: float
    margin: float
    scores: dict[str, float]


def classify(
    icon: np.ndarray,
    candidates: Iterable[str],
    bank: IconBank,
    templates: dict[str, np.ndarray] | None = None,
) -> IconMatch:
    """Icon nay la lo nao trong `candidates`? Tuong quan chuan hoa tren anh xam.

    Moi ung vien lay diem CAO HON giua icon cat tu the (`templates`, da
    `_prep`) va icon CDragon: the co the bi cat luc dang lat, CDragon co the
    khac icon trong game - mot nguon dung la du.
    """
    probe = _prep(icon)
    templates = templates or {}
    scores: dict[str, float] = {}
    for api in dict.fromkeys(candidates):
        sources = [t for t in (templates.get(api), bank.get(api)) if t is not None]
        if sources:
            scores[api] = max(float((probe * t).sum()) for t in sources)
    if not scores:
        return IconMatch(None, 0.0, 0.0, scores)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top, score = ranked[0]
    margin = score - ranked[1][1] if len(ranked) > 1 else score
    ok = score >= MIN_SCORE and margin >= MIN_MARGIN
    return IconMatch(top if ok else None, score, margin, scores)


def read_newest(
    image: np.ndarray, candidates: Sequence[str], bank: IconBank
) -> tuple[Strip | None, IconMatch | None]:
    """Tien ich: tim dai va phan loai icon ngoai cung ben phai (lo moi nhat)."""
    strip = find_strip(image)
    if strip is None:
        return None, None
    return strip, classify(strip.icons[-1], candidates, bank)


class HeldAugmentTracker:
    """Nho lo da chon trong van, tu dai icon. Dung chung cho replay va live.

    Vong doi mot lan chon:
      1. `offer_seen()` - dang o man chon lo: nho cac lo DANG CHAO (lan cuoi
         cung la lan nguoi choi chon tu do) va stage.
      2. `observe()`    - ngoai man: khi dai co dung `len(held) + 1` icon thi
         phan loai icon moi nhat trong cac lo vua chao.

    Ba cach chong ghi sai:
      - Chi nhan khi so icon TANG va icon moi nhat khop mot lo vua chao. Man
        bi an (chua chon) thi so icon chua doi nen khong ghi. Icon khong khop
        lo nao vua chao (doc sai dai) cung bi bo qua - lop an toan.
      - Chi phan loai giua cac lo vua chao, loc them theo `offer_rounds` cua
        stage (ban +/++ ra o vong khac nhau).
      - Het `window_s` ma chua chac thi ghi None ("chua ro"), khong doan.
    """

    def __init__(
        self,
        bank: IconBank | None = None,
        offer_rounds: dict[str, Sequence[str]] | None = None,
        window_s: float = 120.0,
    ) -> None:
        self.bank = bank or IconBank()
        self.offer_rounds = offer_rounds or {}
        self.window_s = window_s
        self.held: list[str | None] = []
        self._pending: tuple[tuple[str, ...], str, float] | None = None
        self._templates: dict[str, np.ndarray] = {}
        self.last_match: IconMatch | None = None

    def reset(self) -> None:
        self.held.clear()
        self._pending = None
        self._templates = {}
        self.last_match = None

    @property
    def known(self) -> list[str]:
        """Lo da chon doc chac duoc - thu di vao `GameState.augments`."""
        return [a for a in self.held if a]

    def offer_seen(
        self,
        candidates: Iterable[str],
        stage: str,
        t: float,
        card_icons: dict[str, np.ndarray] | None = None,
    ) -> None:
        """Nho lan chao. `card_icons`: apiName -> icon cat tu the (`card_icon`)."""
        names = tuple(dict.fromkeys(str(c) for c in candidates if c))
        if names:
            self._pending = (names, stage, t)
            self._templates = {
                a: _prep(img) for a, img in (card_icons or {}).items() if img is not None and img.size
            }

    def _filter_round(self, candidates: tuple[str, ...], stage: str) -> tuple[str, ...]:
        kept = tuple(c for c in candidates if stage in (self.offer_rounds.get(c) or (stage,)))
        return kept or candidates

    def observe(self, image: np.ndarray, t: float) -> str | None:
        """Doc dai ngoai man chon lo. Tra ve lo vua ghi nhan (neu co)."""
        if self._pending is None:
            return None
        candidates, stage, seen_t = self._pending
        if t - seen_t > self.window_s:
            self.held.append(None)
            self._pending = None
            return None
        strip = find_strip(image)
        # count == len+1: lan chon vua roi. count > len+1: bo lo mot doan (mo
        # app giua van, tua video) - van nhan neu icon moi KHOP lo vua chao,
        # cac o bo lo ghi None. count <= len: chua chon, hoac dang xem ban khac.
        if strip is None or strip.count <= len(self.held):
            return None
        match = classify(
            strip.icons[-1], self._filter_round(candidates, stage), self.bank, self._templates
        )
        self.last_match = match
        if match.api_name is None:
            return None
        self.held.extend([None] * (strip.count - 1 - len(self.held)))
        self.held.append(match.api_name)
        self._pending = None
        return match.api_name
