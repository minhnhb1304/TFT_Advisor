"""ItemTracker: doc do luc chuan bi, giu lan doc gan nhat cho man chon loi."""

from __future__ import annotations

from src.live.item_tracker import ItemTracker, held_items
from src.vision.unit_items import Bar, ItemCell, UnitItems


class FakeReader:
    def __init__(self, *reads):
        self.reads = list(reads)
        self.calls = 0

    def read(self, image):
        self.calls += 1
        return self.reads.pop(0)


def unit(*names):
    return UnitItems(Bar(0, 0, 60, 4), tuple(ItemCell(0, 0, 23, n) for n in names))


def test_splits_components_and_completed_and_skips_uncertain():
    tracker = ItemTracker(FakeReader([unit("DA_GuinsoosRageblade", None), unit("DA_Component_BFSword")]))
    assert tracker.observe(None, 0.0)
    assert tracker.completed == ["DA_GuinsoosRageblade"]
    assert tracker.components == ["DA_Component_BFSword"]
    assert tracker.uncertain == 1


def test_reads_at_most_every_period_and_keeps_last():
    reader = FakeReader([unit("DA_InfinityEdge")], [unit("DA_KrakensFury")])
    tracker = ItemTracker(reader, every_s=5.0)
    tracker.observe(None, 0.0)
    assert not tracker.observe(None, 3.0)
    assert tracker.observe(None, 6.0) and tracker.completed == ["DA_KrakensFury"]
    assert reader.calls == 2


def test_combat_frames_do_not_overwrite():
    reader = FakeReader([unit("DA_InfinityEdge")])
    tracker = ItemTracker(reader, every_s=0.0, in_combat=lambda image: image == "combat")
    tracker.observe("planning", 0.0)
    assert not tracker.observe("combat", 1.0)
    assert tracker.completed == ["DA_InfinityEdge"] and reader.calls == 1


def test_apply_and_reset():
    class State:
        completed_items: list = []
        item_components: list = []

    tracker = ItemTracker(FakeReader([unit("DA_InfinityEdge", "DA_Component_TearOfTheGoddess")]))
    tracker.observe(None, 0.0)
    state = tracker.apply(State())
    assert state.completed_items == ["DA_InfinityEdge"]
    assert state.item_components == ["DA_Component_TearOfTheGoddess"]
    tracker.reset()
    assert tracker.completed == [] and tracker.observe is not None


def test_thiefs_gloves_random_items_are_not_held():
    """Gang Dao Tac chiem 3 o: 2 mon ngau nhien bi bo, IE that tren tuong khac van tinh."""
    units = [unit("DA_ThiefsGloves", "DA_InfinityEdge", "DA_KrakensFury"), unit("DA_InfinityEdge")]
    assert held_items(units) == (["DA_ThiefsGloves", "DA_InfinityEdge"], [])
    tracker = ItemTracker(FakeReader(units))
    tracker.observe(None, 0.0)
    assert tracker.completed == ["DA_ThiefsGloves", "DA_InfinityEdge"]
