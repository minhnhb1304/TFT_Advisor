"""HybridCardReader: OCR truoc, Gemini chi cho o OCR khong chac, Gemini loi thi giu OCR."""

from __future__ import annotations

from typing import Any

import numpy as np

from src.live.card_reader import GeminiCardReader, HybridCardReader
from src.vision.augment_reader import AugmentReading, CardRead

FRAME = np.zeros((4, 4, 3), dtype=np.uint8)


class StubReader:
    def __init__(self, cards: dict[int, CardRead], traits: dict[str, int] | None = None,
                 error: Exception | None = None) -> None:
        self.cards = cards
        self.traits = traits or {}
        self.error = error
        self.calls: list[int] = []

    def read_slot(self, frame: np.ndarray, slot: int) -> CardRead:
        self.calls.append(slot)
        if self.error is not None:
            raise self.error
        return self.cards[slot]

    def read_traits(self, frame: np.ndarray) -> dict[str, int]:
        return dict(self.traits)

    def cached_traits(self, frame: np.ndarray) -> dict[str, int] | None:
        return dict(self.traits) if self.calls else None


def _card(slot: int, *names: str, reason: str = "") -> CardRead:
    return CardRead(slot, names[0] if names else "", "", tuple(names), 1.0 if names else 0.0, reason)


def _hybrid(ocr: Any, gemini: Any) -> HybridCardReader:
    return HybridCardReader(ocr, gemini)


def test_unambiguous_ocr_never_calls_gemini() -> None:
    ocr = StubReader({0: _card(0, "A")}, traits={"T": 2})
    gemini = StubReader({0: _card(0, "B")}, traits={"G": 3})
    reader = _hybrid(ocr, gemini)

    assert reader.read_slot(FRAME, 0).api_names == ("A",)
    assert gemini.calls == []
    assert reader.read_traits(FRAME) == {"T": 2}


def test_empty_ocr_falls_back_to_gemini_and_its_traits() -> None:
    ocr = StubReader({1: _card(1, reason="không khớp")}, traits={"T": 2})
    gemini = StubReader({1: _card(1, "B")}, traits={"G": 3})
    reader = _hybrid(ocr, gemini)

    assert reader.read_slot(FRAME, 1).api_names == ("B",)
    assert reader.read_traits(FRAME) == {"G": 3}


def test_ambiguous_ocr_asks_gemini() -> None:
    ocr = StubReader({0: _card(0, "A1", "A2")})
    gemini = StubReader({0: _card(0, "A2")})

    assert _hybrid(ocr, gemini).read_slot(FRAME, 0).api_names == ("A2",)


def test_gemini_error_keeps_ocr_result() -> None:
    ocr = StubReader({0: _card(0, "A1", "A2", reason="cặp trùng tên")}, traits={"T": 2})
    gemini = StubReader({}, error=RuntimeError("503 UNAVAILABLE"))
    reader = _hybrid(ocr, gemini)

    card = reader.read_slot(FRAME, 0)
    assert card.api_names == ("A1", "A2")
    assert "503" in card.reason
    assert reader.read_traits(FRAME) == {"T": 2}


def test_gemini_refusal_keeps_ocr_reason() -> None:
    ocr = StubReader({2: _card(2, reason="OCR không đọc được chữ nào trên thẻ")})
    gemini = StubReader({2: _card(2, reason="Lỗi gọi Gemini: 429")})

    card = _hybrid(ocr, gemini).read_slot(FRAME, 2)
    assert card.api_names == ()
    assert "OCR không đọc được" in card.reason and "429" in card.reason


def test_gemini_calls_count_network_reads_only() -> None:
    class Reader:
        def __init__(self, sources: list[str]) -> None:
            self.sources = sources

        def read(self, frame: np.ndarray) -> AugmentReading:
            return AugmentReading((_card(0, "A"),), {}, self.sources.pop(0), 0.0)

    gemini = GeminiCardReader(Reader(["gemini:flash", "cache"]))  # type: ignore[arg-type]
    gemini.read_slot(FRAME, 0)
    gemini.read_slot(FRAME, 0)              # cung khung: khong goi lai reader
    gemini.read_slot(FRAME + 1, 0)          # khung moi nhung trung cache aHash
    assert gemini.calls == 1
