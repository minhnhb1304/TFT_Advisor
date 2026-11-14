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


# Lo "Van Menh" (Silver/Gold/Prismatic Destiny, ca ban +/++): chon MOT lo nhung
# dai co them HAI icon - chinh no va mot lo ngau nhien CUNG BAC no tang (mo ta
# CDragon: "Nhan 1 Nang Cap <bac> ngau nhien va vang"). Nguoi choi chi ra 2026-11-14.
GRANTS_SAME_TIER = ("DA_SilverDestiny", "DA_GoldDestiny", "DA_PrismaticDestiny")
# Vong chon lo cua van dau (moi vong dung MOT lan chon; lo tang khong tinh).
PICK_ROUNDS = ("2-1", "3-2", "4-2")
# Stage da qua vong chon nay tu chung nay vong tro len ma dai chua co icon moi
# -> coi la bo lo, ghi "chua ro". Dem theo VONG, khong theo giay.
EXPIRE_AFTER_ROUNDS = 2


def grants_same_tier(api_name: str | None) -> bool:
    return bool(api_name) and str(api_name).startswith(GRANTS_SAME_TIER)


def rounds_between(a: str, b: str) -> int:
    """So vong tu stage `a` toi `b` ("2-1" -> "2-3" = 2). Doc khong duoc -> 0."""
    try:
        sa, ra = (int(x) for x in a.split("-"))
        sb, rb = (int(x) for x in b.split("-"))
    except (ValueError, AttributeError):
        return 0
    return (sb - sa) * 7 + (rb - ra)


class HeldAugmentTracker:
    """Nho lo da chon trong van, tu dai icon huong 10 gio. Dung chung replay va live.

    Dai 10 gio LUON la lo cua minh (lo doi thu o huong 2 gio). Vong doi mot lan chon:
      1. `offer_seen()` - trong man chon lo: nho cac lo DANG CHAO (lan cuoi cung
         la lan nguoi choi chon tu do), stage va icon cat tu the.
      2. `observe()`    - ngoai man (ke ca khi man chi bi AN de di xem nha khac):
         khi dai co THEM icon thi phan loai trong cac lo vua chao. Ghi duoc ->
         `closed` = True: man chon lo nay da xong (LiveSession dong man theo co
         nay, khong theo nguong thoi gian).

    Truong hop dac biet: lo Van Menh them HAI icon (chinh no + lo tang cung bac).
    Lo tang nhan dien giua cac lo cung bac bang icon CDragon; khong chac -> None.

    Chong ghi sai: chi nhan khi so icon TANG va icon khop mot lo vua chao (loc
    them theo `offer_rounds` de tach ban +/++); stage qua `EXPIRE_AFTER_ROUNDS`
    vong ma chua thay icon moi thi ghi None ("chua ro"), khong doan.
    """

    def __init__(
        self,
        bank: IconBank | None = None,
        offer_rounds: dict[str, Sequence[str]] | None = None,
        tiers: dict[str, int] | None = None,
    ) -> None:
        self.bank = bank or IconBank()
        self.offer_rounds = offer_rounds or {}
        self.tiers = tiers or {}
        self.held: list[str | None] = []          # moi icon tren dai, ke ca lo tang
        self.picks: list[str | None] = []         # moi VONG chon mot phan tu
        self._pending: tuple[tuple[str, ...], str, float] | None = None
        self._templates: dict[str, np.ndarray] = {}
        self.last_match: IconMatch | None = None
        self.closed = False

    def reset(self) -> None:
        self.held.clear()
        self.picks.clear()
        self._pending = None
        self._templates = {}
        self.last_match = None
        self.closed = False

    @property
    def known(self) -> list[str]:
        """Lo dang cam doc chac duoc (ke ca lo tang) - thu di vao `GameState.augments`."""
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
            self.closed = False

    def _filter_round(self, candidates: tuple[str, ...], stage: str) -> tuple[str, ...]:
        kept = tuple(c for c in candidates if stage in (self.offer_rounds.get(c) or (stage,)))
        return kept or candidates

    def _close(self, pick: str | None, icons: list[str | None], strip_count: int) -> None:
        # Bo lo mot doan (mo app giua van, tua video): cac o truoc ghi None.
        missing = max(0, strip_count - len(icons) - len(self.held))
        self.held.extend([None] * missing)
        self.held.extend(icons)
        self.picks.append(pick)
        self._pending = None
        self.closed = True

    def _bonus(self, icon: np.ndarray, destiny: str) -> str | None:
        tier = self.tiers.get(destiny)
        pool = [a for a, t in self.tiers.items() if t == tier and not grants_same_tier(a)]
        match = classify(icon, pool, self.bank) if pool else None
        return match.api_name if match else None

    def observe(self, image: np.ndarray, t: float, stage: str | None = None) -> str | None:
        """Doc dai ngoai man chon lo. Tra ve lo vua chon (neu ghi duoc)."""
        if self._pending is None:
            return None
        candidates, offer_stage, _ = self._pending
        if stage and rounds_between(offer_stage, stage) >= EXPIRE_AFTER_ROUNDS:
            self._close(None, [None], len(self.held) + 1)
            return None
        strip = find_strip(image)
        if strip is None or strip.count <= len(self.held):
            return None                     # chua chon (man dang an), hoac khong thay dai
        cands = self._filter_round(candidates, offer_stage)

        match = classify(strip.icons[-1], cands, self.bank, self._templates)
        self.last_match = match
        if match.api_name is not None:
            self._close(match.api_name, [match.api_name], strip.count)
            return match.api_name

        # Van Menh: dai them HAI icon - lo da chon roi lo tang cung bac.
        destinies = tuple(c for c in cands if grants_same_tier(c))
        if destinies and strip.count >= len(self.held) + 2:
            match = classify(strip.icons[-2], destinies, self.bank, self._templates)
            self.last_match = match
            if match.api_name is not None:
                bonus = self._bonus(strip.icons[-1], match.api_name)
                self._close(match.api_name, [match.api_name, bonus], strip.count)
                return match.api_name
        return None
