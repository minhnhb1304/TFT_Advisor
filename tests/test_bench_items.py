"""Thanh do chua lap o mep trai (docs/item-reading/bench-components.md I2)."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from src.vision.bench_items import SLOTS, bench_items, read_bench, slot_boxes
from src.vision.unit_items import UnitItemReader

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "data/item_icons"


@pytest.fixture(scope="module")
def reader() -> UnitItemReader:
    return UnitItemReader(ICONS, ROOT / "data/__none__")


def board(height: int, width: int, slots: dict[int, str]) -> np.ndarray:
    """Khung gia: nen toi, ve icon CDragon vao cac o thanh do."""
    frame = np.full((height, width, 3), 20, np.uint8)
    for i, (x, y, size) in enumerate(slot_boxes(frame)):
        frame[y:y + size, x:x + size] = 0
        if i in slots:
            icon = cv2.imread(str(ICONS / f"{slots[i]}.png"))
            frame[y + 1:y + size - 1, x + 1:x + size - 1] = cv2.resize(icon, (size - 2, size - 2))
    return frame


@pytest.mark.parametrize("height,width", [(1080, 1920), (1080, 1728), (720, 1280)])
def test_reads_components_and_skips_empty(reader, height, width):
    frame = board(height, width, {1: "DA_Component_RecurveBow", 4: "DA_Crownguard"})
    slots = read_bench(frame, reader)
    assert len(slots) == SLOTS
    assert [s.index for s in slots if not s.empty] == [1, 4]
    assert bench_items(frame, reader) == ["DA_Component_RecurveBow", "DA_Crownguard"]


def test_empty_bench(reader):
    assert bench_items(board(1080, 1920, {}), reader) == []
