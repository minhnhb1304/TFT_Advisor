"""Doc lo da chon tu dai icon (src/vision/held_augments.py) - anh tong hop."""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from src.vision.held_augments import HeldAugmentTracker, IconBank, classify, find_strip

H, W = 1080, 1920
CELL = 37


def pattern(seed: int) -> np.ndarray:
    """Icon gia: hinh ve vang ngau nhien tren nen den, 128 px nhu icon CDragon."""
    rng = np.random.default_rng(seed)
    icon = np.zeros((128, 128, 3), np.uint8)
    for _ in range(6):
        center = tuple(int(v) for v in rng.integers(25, 103, 2))
        cv2.circle(icon, center, int(rng.integers(8, 22)), (40, 190, 230), -1)
    return icon


@pytest.fixture
def bank(tmp_path):
    for i, name in enumerate(("A", "B", "C", "D")):
        cv2.imwrite(str(tmp_path / f"{name}.png"), pattern(i))
    return IconBank(tmp_path)


def frame(icons: list[str], center_x: int = 511, top: int = 228) -> np.ndarray:
    image = np.full((H, W, 3), (200, 150, 60), np.uint8)       # nen ban co xanh
    left = center_x - CELL * len(icons) // 2
    seeds = {"A": 0, "B": 1, "C": 2, "D": 3}
    for k, name in enumerate(icons):
        cell = cv2.resize(pattern(seeds[name]), (CELL, CELL), interpolation=cv2.INTER_AREA)
        image[top:top + CELL, left + k * CELL:left + (k + 1) * CELL] = cell
    return image


@pytest.mark.parametrize("n", [1, 2, 3])
def test_counts_icons(n):
    strip = find_strip(frame(["A", "B", "C"][:n]))
    assert strip is not None and strip.count == n


def test_no_strip_on_plain_board():
    assert find_strip(np.full((H, W, 3), (200, 150, 60), np.uint8)) is None


def test_classify_picks_the_matching_candidate(bank):
    strip = find_strip(frame(["A", "C"]))
    match = classify(strip.icons[-1], ["B", "C", "D"], bank)
    assert match.api_name == "C" and match.margin > 0


def test_classify_refuses_when_nothing_matches(bank):
    strip = find_strip(frame(["A"]))
    assert classify(strip.icons[-1], ["B", "D"], bank).api_name is None


def test_tracker_records_one_pick_per_offer(bank):
    tracker = HeldAugmentTracker(bank)
    tracker.offer_seen(["A", "B", "D"], "2-1", t=100)
    assert tracker.observe(frame([]), 105) is None              # chua chon
    assert tracker.observe(frame(["A"]), 110) == "A"
    tracker.offer_seen(["B", "C", "D"], "3-2", t=600)
    assert tracker.observe(frame(["A"]), 605) is None           # man dang an
    assert tracker.observe(frame(["A", "C"]), 612) == "C"
    assert tracker.known == ["A", "C"]


def test_other_players_strip_is_ignored(bank):
    """Dang xem ban nguoi khac: so icon tang nhung icon khong khop lo vua chao."""
    tracker = HeldAugmentTracker(bank)
    tracker.offer_seen(["A", "B"], "2-1", t=0)
    assert tracker.observe(frame(["D"]), 5) is None
    assert tracker.held == []


def test_window_expiry_records_unknown_not_a_guess(bank):
    tracker = HeldAugmentTracker(bank, window_s=60)
    tracker.offer_seen(["A", "B"], "2-1", t=0)
    tracker.observe(frame([]), 61)
    assert tracker.held == [None] and tracker.known == []


def test_offer_rounds_split_plus_variants(bank):
    """B va C cung icon (ban +/++); chi C ra o 4-2 -> chon C du icon khop B."""
    tracker = HeldAugmentTracker(bank, offer_rounds={"B": ["3-2"], "C": ["4-2"]})
    tracker.held = ["A", "D"]
    bank._cache["C"] = bank.get("B")
    tracker.offer_seen(["B", "C"], "4-2", t=0)
    assert tracker.observe(frame(["A", "D", "B"]), 5) == "C"


def test_missed_picks_are_padded_with_unknown(bank):
    """Mo app giua van: dai da co 2 icon, lo moi van ghi duoc, hai o truoc la None."""
    tracker = HeldAugmentTracker(bank)
    tracker.offer_seen(["B", "C", "D"], "4-2", t=0)
    assert tracker.observe(frame(["A", "D", "C"]), 5) == "C"
    assert tracker.held == [None, None, "C"]


def test_sixteen_by_ten_frame():
    """Ban record 16:10 (dat_01): dai lech trai so voi phep neo giua."""
    image = np.full((1080, 1728, 3), (60, 160, 60), np.uint8)
    for k, seed in enumerate((0, 1, 2)):
        cell = cv2.resize(pattern(seed), (CELL, CELL), interpolation=cv2.INTER_AREA)
        image[227:227 + CELL, 358 + k * CELL:358 + (k + 1) * CELL] = cell
    strip = find_strip(image)
    assert strip is not None and strip.count == 3
