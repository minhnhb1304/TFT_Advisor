"""Doc do duoi thanh mau (src/vision/unit_items.py) - anh tong hop + vung cat that tu minh_06."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from src.vision.unit_items import UnitItemReader, find_health_bars, find_item_cells

H, W = 1080, 1920
FIXTURES = Path(__file__).parent / "fixtures" / "unit_items"
BG = (200, 150, 60)


def pattern(seed: int) -> np.ndarray:
    """Icon gia 128 px nhu icon CDragon."""
    rng = np.random.default_rng(seed)
    icon = np.full((128, 128, 3), 90, np.uint8)
    for _ in range(6):
        center = tuple(int(v) for v in rng.integers(25, 103, 2))
        color = tuple(int(v) for v in rng.integers(60, 255, 3))
        cv2.circle(icon, center, int(rng.integers(10, 26)), color, -1)
    return icon


def draw_unit(image: np.ndarray, x: int, y: int, icons: list[int], hp: float = 1.0) -> None:
    """Thanh mau xanh (khung toi) + icon 23 px vien den theo so do minh_06."""
    cv2.rectangle(image, (x - 12, y - 3), (x + 66, y + 8), (30, 20, 10), -1)
    cv2.rectangle(image, (x, y), (x + int(63 * hp) - 1, y + 3), (20, 200, 30), -1)
    for k, seed in enumerate(icons):
        cx, cy = x - 5 + round(k * 25.5), y + 10
        cv2.rectangle(image, (cx, cy), (cx + 22, cy + 22), (5, 5, 5), -1)
        image[cy + 1:cy + 22, cx + 1:cx + 22] = cv2.resize(pattern(seed), (21, 21),
                                                           interpolation=cv2.INTER_AREA)


@pytest.fixture
def icon_dir(tmp_path):
    for seed in range(4):
        cv2.imwrite(str(tmp_path / f"DA_Item{seed}.png"), pattern(seed))
    return tmp_path


def blank() -> np.ndarray:
    return np.full((H, W, 3), BG, np.uint8)


def test_finds_one_bar_per_unit():
    image = blank()
    draw_unit(image, 500, 400, [])
    draw_unit(image, 900, 600, [0], hp=0.3)
    bars = find_health_bars(image)
    assert [(b.x, b.y) for b in bars] == [(500, 400), (900, 600)]


@pytest.mark.parametrize("n", [0, 1, 2, 3])
def test_counts_items(n):
    image = blank()
    draw_unit(image, 700, 500, list(range(n)))
    (bar,) = find_health_bars(image)
    assert len(find_item_cells(image, bar)) == n


def test_low_hp_keeps_left_anchor():
    """Mat mau thi phan xanh ngan tu ben phai - o icon khong duoc lech."""
    image = blank()
    draw_unit(image, 700, 500, [0, 1, 2], hp=0.25)
    (bar,) = find_health_bars(image)
    assert [c[0] for c in find_item_cells(image, bar)] == [695, 721, 746]


def test_classifies_each_slot(icon_dir):
    image = blank()
    draw_unit(image, 700, 500, [2, 0, 3])
    (unit,) = UnitItemReader(icon_dir, icon_dir / "none").read(image)
    assert unit.items == ["DA_Item2", "DA_Item0", "DA_Item3"]


def test_unknown_icon_is_uncertain_not_guessed(icon_dir):
    image = blank()
    draw_unit(image, 700, 500, [0, 99])
    (unit,) = UnitItemReader(icon_dir, icon_dir / "none").read(image)
    assert unit.items == ["DA_Item0"] and unit.uncertain


def test_game_templates_extend_cdragon(icon_dir, tmp_path):
    """Mau cat tu game duoc dung ngang icon CDragon cho cung apiName."""
    templates = tmp_path / "templates"
    (templates / "DA_ItemX").mkdir(parents=True)
    image = blank()
    draw_unit(image, 700, 500, [42])
    cv2.imwrite(str(templates / "DA_ItemX" / "a.png"), image[510:533, 695:718])
    (unit,) = UnitItemReader(icon_dir, templates).read(image)
    assert unit.items == ["DA_ItemX"]


def on_canvas(name: str, x: int, y: int) -> np.ndarray:
    crop = cv2.imread(str(FIXTURES / name))
    image = np.zeros((H, W, 3), np.uint8)
    image[y:y + crop.shape[0], x:x + crop.shape[1]] = crop
    return image


def test_real_frame_minh_06_combat():
    """4-1 giao tranh: Archangel / Void Staff / Archangel (so cong don de len) va
    tuong it mau: Sunfire / mon vien olive (khong co trong bang -> chua ro) / Gargoyle."""
    units = UnitItemReader().read(on_canvas("minh_06_1085.png", 840, 290))
    read = {(u.bar.x, u.bar.y): [c.api_name for c in u.cells] for u in units}
    assert read[(1332, 566)] == ["DA_ArchangelsStaff", "DA_VoidStaff", "DA_ArchangelsStaff"]
    assert read[(876, 317)] == ["DA_SunfireCape", None, "DA_GargoyleStoneplate"]
    assert all(cells == [] for key, cells in read.items() if key not in {(1332, 566), (876, 317)})


def test_real_frame_minh_06_planning_empty_unit():
    """Tuong khong cam do: vung toi cua khung thanh mau / than tuong khong thanh icon."""
    units = UnitItemReader().read(on_canvas("minh_06_400.png", 340, 660))
    read = {(u.bar.x, u.bar.y): u.items for u in units}
    assert read[(496, 683)] == ["DA_GargoyleStoneplate"]
    assert read[(376, 705)] == []


def test_red_bars_mark_combat():
    """Thanh do (dich) chi bat khi own=False; thanh xanh khong lan sang."""
    image = blank()
    draw_unit(image, 700, 500, [])
    cv2.rectangle(image, (1000, 300), (1062, 303), (30, 20, 200), -1)
    cv2.rectangle(image, (988, 297), (1066, 308), (30, 20, 10), -1)
    cv2.rectangle(image, (1000, 300), (1062, 303), (30, 20, 200), -1)
    assert [(b.x, b.y) for b in find_health_bars(image, own=False)] == [(1000, 300)]
    assert [(b.x, b.y) for b in find_health_bars(image)] == [(700, 500)]


def test_cell_under_another_units_bar_is_skipped(icon_dir):
    """Hai tuong dung sat: o cua tuong tren de len thanh mau tuong duoi -> bo."""
    image = blank()
    draw_unit(image, 700, 500, [0, 1, 2])
    draw_unit(image, 740, 520, [])
    units = UnitItemReader(icon_dir, icon_dir / "none").read(image)
    top = next(u for u in units if u.bar.y == 500)
    assert len(top.cells) < 3
