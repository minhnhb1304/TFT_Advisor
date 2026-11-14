"""Overlay trong tran: cua so trong suot, click xuyen qua, phu dung vung client game.

Ve CUNG bo ve voi overlay tren video cua replay (`src/replay/overlay.py`):
huy hieu bac tren moi the, vien o duoc khuyen, vong nut doi, vien huong duoi
the, widget ket luan. Mot ngon ngu hinh anh cho ca replay lan tran that.

Khac voi replay o mot cho: cua so trong suot khong co pixel game de lam mo
("kinh mo"), nen widget ket luan duoc dat tren mot nen toi ban trong.

Che do `preview`: ve khung hinh len chinh cua so (de thu vo live tren video
khi khong co game, va de chup anh kiem tra). Che do thuong: chi ve overlay.
"""

from __future__ import annotations

from typing import Any

from PyQt6 import QtCore, QtGui, QtWidgets

from ..replay import overlay, theme
from ..replay.viewmodel import build_plans, build_view


class LiveOverlay(QtWidgets.QWidget):
    """Lop ve loi khuyen. Nhan su kien LiveSession qua `on_event` (luong Qt)."""

    def __init__(self, regions: Any, preview: bool = False) -> None:
        super().__init__()
        self.regions = regions
        self.preview = preview
        self._advice: tuple[list, Any, list] | None = None
        # Chi ve loi khuyen khi man chon loi DANG HIEN; man an tam thi giu du
        # lieu (de hien lai ngay khi mo lai) nhung khong ve len ban co.
        self.visible = False
        self._frame: QtGui.QImage | None = None
        self.status = "đang chờ màn chọn lõi"
        flags = (QtCore.Qt.WindowType.FramelessWindowHint
                 | QtCore.Qt.WindowType.WindowStaysOnTopHint
                 | QtCore.Qt.WindowType.Tool)
        if not preview:
            # Click xuyen qua: nguoi choi thao tac voi game nhu khong co overlay.
            self.setWindowFlags(flags | QtCore.Qt.WindowType.WindowTransparentForInput)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating)
        else:
            self.setWindowTitle("TFT Advisor — live (mô phỏng)")

    # -- du lieu -----------------------------------------------------------

    def on_event(self, event: Any, visible: bool | None = None) -> None:
        from ..live.events import AdviceReady, Cleared, Status  # noqa: PLC0415

        if visible is not None and visible != self.visible:
            self.visible = visible
            self.update()

        if isinstance(event, AdviceReady):
            strip, verdict, slots = build_view(event)
            self._advice = (slots, verdict, build_plans(event))
            held = len(strip.held)
            self.status = f"{event.stage} · đã cầm {held} lõi" if held else f"{event.stage}"
        elif isinstance(event, Cleared):
            self._advice = None
            self.status = "đã rời màn chọn lõi"
        elif isinstance(event, Status):
            self.status = event.message
        elif isinstance(event, Exception):
            self.status = f"lỗi: {event}"
        self.update()

    def set_frame(self, image_bgr) -> None:
        """Chi dung o che do preview."""
        import cv2  # noqa: PLC0415

        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        self._frame = QtGui.QImage(rgb.data, w, h, w * 3, QtGui.QImage.Format.Format_RGB888).copy()
        self.update()

    # -- ve ----------------------------------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        if self.preview and self._frame is not None:
            painter.drawImage(QtCore.QRect(0, 0, w, h), self._frame)

        if self._advice is not None and self.visible:
            lay = overlay.layout(self.regions, w, h)
            slots, verdict, plans = self._advice
            if verdict.action:
                left, top, right, bottom = lay.verdict
                painter.setPen(QtCore.Qt.PenStyle.NoPen)
                painter.setBrush(QtGui.QColor(10, 13, 19, 215))
                painter.drawRoundedRect(QtCore.QRectF(left, top, right - left, bottom - top), 8, 8)
            overlay.paint(painter, lay, slots, verdict, plans)
        self._paint_status(painter, h)
        painter.end()

    def _paint_status(self, painter: QtGui.QPainter, h: int) -> None:
        """Vien nho goc trai tren: ten ung dung + trang thai. Khong che UI game."""
        text = f"TFT ADVISOR  ·  {self.status}"
        font = QtGui.QFont("Chakra Petch")
        font.setPixelSize(max(11, int(h * 0.013)))
        font.setBold(True)
        painter.setFont(font)
        tw = painter.fontMetrics().horizontalAdvance(text)
        ph = int(h * 0.026)
        rect = QtCore.QRectF(int(h * 0.075), int(h * 0.012), tw + ph, ph)
        painter.setPen(QtGui.QPen(QtGui.QColor(theme.ACCENT), 1))
        painter.setBrush(QtGui.QColor(10, 13, 19, 200))
        painter.drawRoundedRect(rect, ph / 2, ph / 2)
        painter.setPen(QtGui.QColor(theme.ACCENT))
        painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, text)
