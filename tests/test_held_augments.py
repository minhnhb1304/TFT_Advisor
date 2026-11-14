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
    """So icon tang nhung icon khong khop lo vua chao (doc sai dai): khong ghi."""
    tracker = HeldAugmentTracker(bank)
    tracker.offer_seen(["A", "B"], "2-1", t=0)
    assert tracker.observe(frame(["D"]), 5) is None
    assert tracker.held == []


def test_stage_moving_on_without_a_new_icon_records_unknown_not_a_guess(bank):
    """Het han theo VONG, khong theo giay: an man bao lau cung khong bi ghi."""
    tracker = HeldAugmentTracker(bank)
    tracker.offer_seen(["A", "B"], "2-1", t=0)
    tracker.observe(frame([]), 500, stage="2-1")       # an man rat lau, cung vong
    assert tracker.held == [] and not tracker.closed
    tracker.observe(frame([]), 600, stage="2-3")       # qua 2 vong ma khong co icon
    assert tracker.picks == [None] and tracker.known == [] and tracker.closed


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


def test_destiny_adds_two_icons_and_counts_as_one_pick(bank):
    """Van Menh: chon MOT lo, dai them HAI icon (no + lo cung bac duoc tang)."""
    tracker = HeldAugmentTracker(bank, tiers={"DA_GoldDestiny": 2, "B": 2, "C": 2, "D": 1})
    bank._cache["DA_GoldDestiny"] = bank.get("A")      # icon cua lo Van Menh = mau A
    tracker.offer_seen(["DA_GoldDestiny", "D"], "2-1", t=0)
    assert tracker.observe(frame(["A", "C"]), 5) == "DA_GoldDestiny"
    assert tracker.picks == ["DA_GoldDestiny"]
    assert tracker.held == ["DA_GoldDestiny", "C"]     # lo tang nhan dien trong bac vang
    assert tracker.closed
    # Vong sau: dai dem tiep tu 2 icon, khong lech.
    tracker.offer_seen(["B", "D"], "3-2", t=600)
    assert tracker.observe(frame(["A", "C", "B"]), 605) == "B"
    assert tracker.picks == ["DA_GoldDestiny", "B"]


def test_unrecognised_destiny_bonus_is_unknown_not_a_guess(bank):
    tracker = HeldAugmentTracker(bank, tiers={"DA_SilverDestiny": 1, "D": 1})
    bank._cache["DA_SilverDestiny"] = bank.get("A")
    tracker.offer_seen(["DA_SilverDestiny", "B"], "2-1", t=0)
    assert tracker.observe(frame(["A", "C"]), 5) == "DA_SilverDestiny"
    assert tracker.held == ["DA_SilverDestiny", None]  # C khong o bac bac -> chua ro
