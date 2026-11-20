"""Widget cua vo replay: dai trang thai, dai ket luan, cot the, dai thoi gian.

Widget chi VE du lieu da dung san trong `viewmodel.py`. Khong widget nao tu tinh
diem hay tu doc man hinh - de con doi giao dien ma khong dong den phan quyet dinh.

NGU PHAP TRINH BAY hoc tu CSS that cua blitz.gg (research/260918-gamer-ui-palette):

  - Bac tier la MOT token dung o nhieu cuong do: ray doc 50%, than the nhuom 8%,
    chu nhan. Khong phai mot chu cai to mau me.
  - So KHONG to hon ten va KHONG sang hon ten. Chi so chinh duoc danh dau bang
    VI TRI va mot dai cham 6 o ben canh. Ten la thu de nhan dien, so de so sanh.
  - Lua chon nen chon = nen accent 15% + chu accent + vien 2px. Blitz khong dung
    thanh ben trai, khong ngoi sao, khong do bong.
  - So dung font dang khoang - cot so khong nhay khi doi khung.

Mau lay tu `theme.py`, khong viet hex o day.
"""

from __future__ import annotations

import re
from typing import Sequence

from PyQt6 import QtCore, QtGui, QtWidgets

from . import theme
from .icons import augment_pixmap
from .viewmodel import PlanLineVM, SlotVM, StripVM, VerdictVM

# Dung cham tron thay cho dau tick: Segoe UI khong co glyph ✓/✗, se ra o vuong.
REROLL_LABELS = {
    "available": ("● còn đổi", theme.OK),
    "used": ("○ đã đổi", theme.TEXT_MUTED),
    "unknown": ("● chưa rõ", theme.WARN),
}
DOTS = 6


def _label(text: str, *, size: int, color: str, weight: int = 400, mono: bool = False,
           wrap: bool = True, spacing: float = 0.0) -> QtWidgets.QLabel:
    lbl = QtWidgets.QLabel(text)
    family = theme.MONO if mono else theme.FONT
    lbl.setStyleSheet(
        f"color: {color}; font-size: {size}px; font-weight: {weight}; font-family: {family};"
        f" letter-spacing: {spacing}px; background: transparent;"
    )
    lbl.setWordWrap(wrap)
    return lbl


def _overline(text: str) -> QtWidgets.QLabel:
    """Nhan nhom: 11px / 600 / hoa / gian chu - nhu `.type-overline` cua Blitz."""
    lbl = _label(text.upper(), size=theme.SIZES["xs"], color=theme.TEXT_MUTED,
                 weight=600, wrap=False, spacing=1.2)
    lbl.setStyleSheet(lbl.styleSheet() + f" font-family: {theme.DISPLAY};")
    return lbl


class Chip(QtWidgets.QLabel):
    """Nhan nho: chu nhan viet hoa nhat + gia tri dam, nen be mat 3, bo goc."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTextFormat(QtCore.Qt.TextFormat.RichText)

    def set_data(self, label: str, value: str, color: str = "", warn: bool = False) -> None:
        tone = theme.WARN if warn else (color or theme.TEXT)
        self.setText(
            f"<span style='color:{theme.TEXT_MUTED}; font-size:{theme.SIZES['xs']}px;"
            f" font-weight:600; letter-spacing:1px; font-family:{theme.DISPLAY_HTML}'>{label.upper()}</span>"
            f"&nbsp;&nbsp;<span style='color:{tone}; font-size:{theme.SIZES['lg']}px;"
            f" font-weight:700; font-family:{theme.DISPLAY_HTML}'>{value}</span>"
        )
        self.setStyleSheet(
            f"background: {theme.SURFACE_2}; border: 1px solid {theme.BORDER};"
            f" border-radius: 8px; padding: 4px 12px;"
        )


class StateStrip(QtWidgets.QFrame):
    """Chip stage/cap/vang/HP/chuoi + loi da cam; cau chung va canh bao gon mot dong."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("bar")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(6)
        self.chips = {k: Chip(self) for k in ("stage", "level", "gold", "hp", "streak")}
        for chip in self.chips.values():
            top.addWidget(chip)
        top.addStretch()
        self.rerolls = Chip(self)
        top.addWidget(self.rerolls)
        layout.addLayout(top)

        held = QtWidgets.QHBoxLayout()
        held.setSpacing(6)
        held.addWidget(_overline("lõi đã cầm"))
        self.held_icons = [IconTile(self, size=26) for _ in range(3)]
        for icon in self.held_icons:
            held.addWidget(icon)
        self.held_empty = _label("chưa ghi nhận", size=theme.SIZES["sm"], color=theme.TEXT_FAINT,
                                 wrap=False)
        held.addWidget(self.held_empty)
        held.addStretch()
        layout.addLayout(held)

        self.econ = _label("", size=theme.SIZES["md"], color=theme.TEXT_2)
        layout.addWidget(self.econ)
        self.warn = _label("", size=theme.SIZES["sm"], color=theme.WARN, wrap=False)
        layout.addWidget(self.warn)

    def set_data(self, strip: StripVM, status: str = "") -> None:
        unknown = set(strip.unknown)
        self.chips["stage"].set_data("vòng", strip.stage, theme.ACCENT, "stage" in unknown)
        self.chips["level"].set_data("cấp", f"{strip.level} · {strip.xp}", "",
                                     bool({"level", "xp"} & unknown))
        self.chips["gold"].set_data("vàng", strip.gold, theme.PLAN_COLORS["fast9"], "gold" in unknown)
        self.chips["hp"].set_data("máu", strip.hp, "", "hp" in unknown)
        self.chips["streak"].set_data("chuỗi", strip.streak, "", "streak" in unknown)
        self.rerolls.set_data("đổi thẻ", "—/3" if strip.rerolls_left is None
                              else f"{strip.rerolls_left}/3")

        for i, icon in enumerate(self.held_icons):
            api = strip.held[i] if i < len(strip.held) else ""
            icon.setVisible(bool(api))
            if api:
                icon.set_data(api, None, api_name=api)
                icon.setToolTip(api)
        self.held_empty.setVisible(not strip.held)

        lines = [strip.econ] + strip.shared
        self.econ.setText(" · ".join(x for x in lines if x))
        self.econ.setVisible(bool(self.econ.text()))
        # Canh bao gon MOT dong: cai dau tien + so con lai; du ca o tooltip.
        warnings = list(strip.warnings) + list(strip.sources) + ([status] if status else [])
        if warnings:
            more = f"  (+{len(warnings) - 1})" if len(warnings) > 1 else ""
            self.warn.setText(f"▲ {warnings[0]}{more}")
            self.warn.setToolTip("\n".join(warnings))
        self.warn.setVisible(bool(warnings))


def brief(text: str, limit: int = 140) -> str:
    """Cau dau cua ly do, bo phan chu thich nguon trong [...] - cho the ket luan."""
    text = re.sub(r"\s*\[[^\]]*\]", "", text or "").strip()
    first = re.split(r"(?<=[.;])\s", text, maxsplit=1)[0]
    return first if len(first) <= limit else first[:limit - 1].rstrip() + "…"


class VerdictBar(QtWidgets.QFrame):
    """The ket luan: icon lon + nhan HANH DONG + ten loi + chenh lech; dong ly do o duoi.

    Mau theo hanh dong: ngoc = CHON, vang = DOI. Nen la gradient rat nhe cua mau
    do tren be mat - noi bat ma khong phat sang.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("verdict")
        outer = QtWidgets.QHBoxLayout(self)
        outer.setContentsMargins(16, 14, 18, 14)
        outer.setSpacing(16)
        self.icon = IconTile(self, size=64)
        outer.addWidget(self.icon, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

        body = QtWidgets.QVBoxLayout()
        body.setSpacing(4)
        top = QtWidgets.QHBoxLayout()
        top.setSpacing(10)
        self.action = QtWidgets.QLabel()
        top.addWidget(self.action)
        self.slot = _overline("")
        top.addWidget(self.slot)
        top.addStretch()
        self.delta = _label("", size=theme.SIZES["md"], color=theme.TEXT_2, wrap=False)
        top.addWidget(self.delta)
        body.addLayout(top)
        self.headline = _label("", size=theme.SIZES["xxl"], color=theme.TEXT, weight=700, wrap=False)
        body.addWidget(self.headline)
        self.edge = _label("", size=theme.SIZES["md"], color=theme.TEXT_2)
        body.addWidget(self.edge)
        outer.addLayout(body, stretch=1)
        self.restyle()

    def restyle(self, color: str | None = None) -> None:
        c = color or theme.ACCENT
        self.setStyleSheet(
            f"QFrame#verdict {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            f" stop:0 {theme._alpha(c, 0.16)}, stop:0.6 {theme.SURFACE_1}, stop:1 {theme.SURFACE_1});"
            f" border: 1px solid {theme._alpha(c, 0.45)}; border-radius: {theme.RADIUS}px; }}"
        )
        self.headline.setStyleSheet(
            f"color: {theme.TEXT}; font-size: {theme.SIZES['xxl']}px; font-weight: 700;"
            f" font-family: {theme.DISPLAY}; background: transparent;"
        )
        self.delta.setStyleSheet(
            f"color: {c}; font-size: {theme.SIZES['md']}px; font-weight: 600;"
            f" font-family: {theme.DISPLAY}; background: {theme._alpha(c, 0.10)};"
            f" border-radius: 8px; padding: 3px 10px;"
        )

    def set_data(self, verdict: VerdictVM, api_name: str = "") -> None:
        reroll = verdict.action == "ĐỔI"
        color = theme.WARN if reroll else theme.ACCENT
        self.restyle(color)
        self.icon.setVisible(bool(api_name))
        if api_name:
            self.icon.set_data(verdict.name, None, api_name=api_name)
        self.action.setText(verdict.action or "CHỜ")
        self.action.setStyleSheet(
            f"color: #0a0d13; background: {color if verdict.action else theme.BORDER_STRONG};"
            f" border-radius: 6px; padding: 2px 10px; font-family: {theme.DISPLAY};"
            f" font-weight: 700; font-size: {theme.SIZES['sm']}px; letter-spacing: 1px;"
        )
        self.slot.setText(f"Ô {verdict.slot + 1}" if verdict.slot is not None else "")
        self.headline.setText(verdict.name or "chưa có khuyến nghị")
        self.delta.setText(verdict.delta_text)
        self.delta.setVisible(bool(verdict.delta_text))
        detail = (verdict.note or verdict.edge) if reroll else (verdict.edge or verdict.note)
        short = brief(detail)
        self.edge.setText(short)
        self.edge.setVisible(bool(short))
        # Ban day du (ca chu thich nguon) o tooltip: gon tren man, khong giau.
        self.setToolTip("\n\n".join(x for x in (verdict.note, verdict.edge) if x))


class ScoreBar(QtWidgets.QWidget):
    """Thanh diem lien, bo tron - de do bang mat hon 6 cham."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(6)
        self._value = 0.0
        self._color = theme.TEXT_2

    def set_data(self, value: float | None, color: str) -> None:
        self._value = max(0.0, min(1.0, value or 0.0))
        self._color = color
        self.update()

    def paintEvent(self, _event) -> None:                    # noqa: N802
        if self.width() <= 0:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(theme.SURFACE_3))
        painter.drawRoundedRect(QtCore.QRectF(0, 0, self.width(), self.height()), 3, 3)
        painter.setBrush(QtGui.QColor(self._color))
        painter.drawRoundedRect(QtCore.QRectF(0, 0, self.width() * self._value, self.height()), 3, 3)


class DotScale(QtWidgets.QWidget):
    """Dải 6 chấm cạnh con số — cách Blitz đánh dấu chỉ số chính mà không phóng to nó."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(4)
        self.setMinimumWidth(DOTS * 8)
        self._value = 0.0
        self._color = theme.TEXT_2

    def set_data(self, value: float | None, color: str) -> None:
        self._value = max(0.0, min(1.0, value or 0.0))
        self._color = color
        self.update()

    def paintEvent(self, _event) -> None:                    # noqa: N802
        if self.width() <= 0 or self.height() <= 0:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        gap = 2
        width = max(2.0, (self.width() - gap * (DOTS - 1)) / DOTS)
        lit = round(self._value * DOTS)
        for i in range(DOTS):
            rect = QtCore.QRectF(i * (width + gap), 0, width, self.height())
            painter.setBrush(QtGui.QColor(self._color) if i < lit else QtGui.QColor(theme.SURFACE_3))
            painter.drawRoundedRect(rect, 1, 1)


class IconTile(QtWidgets.QWidget):
    """Icon loi that (CDragon) trong khung bo goc, vien theo do hiem, khien bac o goc.

    Thieu icon thi ve chu cai dau - khong bao gio de o trong. Khien bac la mau
    huy hieu cua Blitz: chu cai tren nen mau bac, day nhon.
    """

    SIZE = 44

    def __init__(self, parent=None, size: int = SIZE) -> None:
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self._letter = "?"
        self._ring = self._ring2 = theme.BORDER
        self._pixmap: QtGui.QPixmap | None = None
        self._tier = ""

    def set_data(self, name: str, rarity: int | None, api_name: str = "", tier: str = "") -> None:
        self._letter = (name or "?").strip()[:1].upper()
        _, self._ring, self._ring2 = theme.rarity_style(rarity)
        self._pixmap = augment_pixmap(api_name)
        self._tier = (tier or "").upper()
        self.update()

    def paintEvent(self, _event) -> None:                    # noqa: N802
        if self.width() <= 2 or self.height() <= 2:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        n = self._size
        box = QtCore.QRectF(1, 1, n - 2, n - 2)
        radius = max(4.0, n * 0.16)

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor("#0b0c0f"))
        painter.drawRoundedRect(box, radius, radius)
        if self._pixmap is not None:
            clip = QtGui.QPainterPath()
            clip.addRoundedRect(box, radius, radius)
            painter.save()
            painter.setClipPath(clip)
            inset = box.adjusted(n * 0.06, n * 0.06, -n * 0.06, -n * 0.06)
            painter.drawPixmap(inset.toRect(), self._pixmap)
            painter.restore()
        else:
            painter.setPen(QtGui.QColor(theme.TEXT_2))
            font = painter.font()
            font.setPixelSize(max(10, int(n * 0.38)))
            font.setWeight(QtGui.QFont.Weight.DemiBold)
            painter.setFont(font)
            painter.drawText(box, QtCore.Qt.AlignmentFlag.AlignCenter, self._letter)

        gradient = QtGui.QLinearGradient(box.left(), box.top(), box.right(), box.bottom())
        gradient.setColorAt(0, QtGui.QColor(self._ring))
        gradient.setColorAt(1, QtGui.QColor(self._ring2))
        painter.setPen(QtGui.QPen(QtGui.QBrush(gradient), 1.5))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(box, radius, radius)

        if self._tier and n >= 36:
            self._paint_shield(painter, n)

    def _paint_shield(self, painter: QtGui.QPainter, n: int) -> None:
        w, h = n * 0.36, n * 0.42
        x, y = n - w - 1, n - h - 1
        path = QtGui.QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h * 0.62)
        path.lineTo(x + w / 2, y + h)
        path.lineTo(x, y + h * 0.62)
        path.closeSubpath()
        painter.setPen(QtGui.QPen(QtGui.QColor("#0b0c0f"), 1.5))
        painter.setBrush(QtGui.QColor(theme.tier_style(self._tier).text))
        painter.drawPath(path)
        painter.setPen(QtGui.QColor("#0b0c0f"))
        font = painter.font()
        font.setPixelSize(max(9, int(h * 0.6)))
        font.setWeight(QtGui.QFont.Weight.Black)
        painter.setFont(font)
        painter.drawText(QtCore.QRectF(x, y, w, h * 0.8), QtCore.Qt.AlignmentFlag.AlignCenter, self._tier)


class TierRail(QtWidgets.QWidget):
    """Ray dọc màu bậc tier ở mép trái cột — token tier ở cường độ 50%."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedWidth(5)
        self._color = theme.TIER_COLORS[""]

    def set_tier(self, tier: str) -> None:
        self._color = theme.tier_style(tier).text
        self.update()

    def paintEvent(self, _event) -> None:                    # noqa: N802
        if self.height() <= 6:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        color = QtGui.QColor(self._color)
        color.setAlphaF(theme.TIER_RAIL)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(QtCore.QRectF(0, 0, 4, self.height()), 2, 2)


class SlotColumn(QtWidgets.QFrame):
    """Một ô trên màn chọn lõi. Thứ tự cột = thứ tự ô trong game."""

    MAX_REASONS = 2

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumWidth(200)
        body = QtWidgets.QVBoxLayout(self)
        body.setContentsMargins(14, 14, 14, 12)
        body.setSpacing(8)

        head = QtWidgets.QHBoxLayout()
        head.setSpacing(10)
        self.icon = IconTile(self, size=56)
        head.addWidget(self.icon, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        side = QtWidgets.QVBoxLayout()
        side.setSpacing(4)
        self.slot_label = _overline("ô 1")
        side.addWidget(self.slot_label)
        self.rank = QtWidgets.QLabel()
        side.addWidget(self.rank, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        side.addStretch()
        head.addLayout(side, stretch=1)
        body.addLayout(head)

        self.name = _label("", size=theme.SIZES["lg"], color=theme.TEXT, weight=700)
        body.addWidget(self.name)

        metric = QtWidgets.QHBoxLayout()
        metric.setSpacing(8)
        self.score = _label("", size=theme.SIZES["md"], color=theme.TEXT, weight=700, wrap=False)
        metric.addWidget(self.score)
        self.bar = ScoreBar(self)
        metric.addWidget(self.bar, stretch=1, alignment=QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.tier = _label("", size=theme.SIZES["xs"], color=theme.TEXT_MUTED, weight=700, wrap=False)
        metric.addWidget(self.tier)
        body.addLayout(metric)

        self.reasons = _label("", size=theme.SIZES["sm"], color=theme.TEXT_2)
        body.addWidget(self.reasons, stretch=1)
        self.footer = _label("", size=theme.SIZES["sm"], color=theme.TEXT_MUTED, weight=500, wrap=False)
        body.addWidget(self.footer)

    def set_data(self, vm: SlotVM) -> None:
        tier = theme.tier_style(vm.tier)
        self.slot_label.setText(f"Ô {vm.slot + 1}")
        rank_color = theme.ACCENT if vm.recommended else theme.TEXT_2
        self.rank.setText(f"#{vm.rank}" if vm.rank else "—")
        self.rank.setStyleSheet(
            f"color: {rank_color}; font-family: {theme.DISPLAY}; font-weight: 700;"
            f" font-size: {theme.SIZES['xl']}px; background: transparent;"
        )
        self.name.setText(vm.name)
        self.name.setStyleSheet(
            f"color: {theme.ACCENT if vm.recommended else theme.TEXT}; font-weight: 700;"
            f" font-size: {theme.SIZES['lg']}px; font-family: {theme.DISPLAY}; background: transparent;"
        )
        self.icon.set_data(vm.name, vm.rarity, api_name=vm.api_name, tier=vm.tier)
        self.tier.setText(f"BẬC {vm.tier}" if vm.tier else "CHƯA XẾP")
        self.tier.setStyleSheet(
            f"color: {tier.text}; font-size: {theme.SIZES['xs']}px; font-weight: 700;"
            f" letter-spacing: 1px; font-family: {theme.DISPLAY}; background: transparent;"
        )
        self.score.setText(vm.score_text)
        self.score.setStyleSheet(
            f"color: {theme.TEXT}; font-family: {theme.DISPLAY}; font-weight: 700;"
            f" font-size: {theme.SIZES['md']}px; background: transparent;"
        )
        self.bar.set_data(vm.score, theme.ACCENT if vm.recommended else tier.text)

        notes = list(vm.reasons)
        if vm.ambiguous:
            notes.append("không phân biệt được với lõi cùng tên")
        if vm.low_confidence:
            notes.append("đọc tên chưa chắc chắn")
        if vm.unread:
            notes = [vm.raw_text or "chưa đọc được thẻ này"]
        shown = notes[:self.MAX_REASONS]
        self.reasons.setText("\n".join(f"• {r}" for r in shown))
        # Ly do bi cat van doc duoc o tooltip - khong giau.
        self.reasons.setToolTip("\n".join(f"• {r}" for r in notes) if len(notes) > len(shown) else "")
        self.reasons.setStyleSheet(
            f"color: {theme.WARN if vm.unread else theme.TEXT_2}; background: transparent;"
            f" font-size: {theme.SIZES['sm']}px; font-family: {theme.FONT}; line-height: 140%;"
        )

        text, color = REROLL_LABELS[vm.reroll]
        self.footer.setText(text)
        self.footer.setStyleSheet(
            f"color: {color}; font-size: {theme.SIZES['sm']}px; font-weight: 600;"
            f" font-family: {theme.DISPLAY}; background: transparent;"
        )
        self._paint_frame(vm, tier)

    def _paint_frame(self, vm: SlotVM, tier: theme.TierStyle) -> None:
        # Than the: gradient rat nhe mau bac tu tren xuong; o duoc khuyen: vien ngoc 2px.
        top = theme._alpha(tier.text, 0.10) if vm.tier else theme.SURFACE_2
        border, width, style = theme.BORDER, 1, "solid"
        if vm.recommended:
            top = theme._alpha(theme.ACCENT, 0.16)
            border, width = theme.ACCENT, 2
        elif vm.unread:
            border, style = theme.WARN, "dashed"
        self.setStyleSheet(
            f"QFrame#card {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {top},"
            f" stop:0.45 {theme.SURFACE_1}, stop:1 {theme.SURFACE_1});"
            f" border: {width}px {style} {border}; border-radius: {theme.RADIUS}px; }}"
        )


class PlanRow(QtWidgets.QFrame):
    """Mot dong: chip huong (mau co dinh) -> icon + ten loi, o, cai gia, canh bao."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("planrow")
        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(10, 8, 10, 8)
        row.setSpacing(10)
        # Moi huong mot vien rieng, xep doc: dong da gop nhieu huong van doc ro tung cai.
        chips = QtWidgets.QWidget(self)
        chips.setFixedWidth(170)
        chips.setStyleSheet("background: transparent;")
        self.chip_box = QtWidgets.QVBoxLayout(chips)
        self.chip_box.setContentsMargins(0, 0, 0, 0)
        self.chip_box.setSpacing(4)
        self.chips = [QtWidgets.QLabel(chips) for _ in range(4)]
        for chip in self.chips:
            self.chip_box.addWidget(chip, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        row.addWidget(chips)
        self.icon = IconTile(self, size=32)
        row.addWidget(self.icon)
        text = QtWidgets.QVBoxLayout()
        text.setSpacing(2)
        self.name = _label("", size=theme.SIZES["base"], color=theme.TEXT, weight=700, wrap=False)
        self.name.setStyleSheet(self.name.styleSheet() + f" font-family: {theme.DISPLAY};")
        text.addWidget(self.name)
        self.cost = _label("", size=theme.SIZES["sm"], color=theme.TEXT_2, wrap=False)
        text.addWidget(self.cost)
        row.addLayout(text, stretch=1)
        self.warn = _label("", size=theme.SIZES["sm"], color=theme.WARN, wrap=False)
        row.addWidget(self.warn)

    def set_data(self, vm: PlanLineVM) -> None:
        labels = [part.strip() for part in vm.label.split("/")]
        for i, chip in enumerate(self.chips):
            visible = i < len(labels)
            chip.setVisible(visible)
            if not visible:
                continue
            color = theme.plan_color(vm.plans[i] if i < len(vm.plans) else "")
            chip.setText(labels[i])
            chip.setStyleSheet(
                f"color: {color}; background: {theme._alpha(color, 0.12)};"
                f" border: 1px solid {theme._alpha(color, 0.45)}; border-radius: 10px;"
                f" padding: 2px 10px; font-size: {theme.SIZES['sm']}px; font-weight: 700;"
                f" font-family: {theme.DISPLAY};"
            )
        self.icon.set_data(vm.name, None, api_name=vm.api_name)
        where = f"Ô {vm.slot + 1} · " if vm.slot is not None else ""
        self.name.setText(f"{where}{vm.name}")
        pill = {"eco": ("KINH TẾ", theme.PLAN_COLORS["fast9"]),
                "combat": ("COMBAT", theme.PLAN_COLORS["fast8"])}.get(vm.kind)
        self.cost.setText(
            f"<span style='color:{pill[1]}; font-weight:600; letter-spacing:0.6px'>{pill[0]}</span>"
            f"&nbsp; {vm.cost}" if pill else ""
        )
        self.warn.setText("▲ " + "; ".join(vm.warnings) if vm.warnings else "")
        self.warn.setVisible(bool(vm.warnings))
        lead = theme.plan_color(vm.plans[0] if vm.plans else "")
        self.setStyleSheet(
            f"QFrame#planrow {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            f" stop:0 {theme._alpha(lead, 0.10)}, stop:0.5 {theme.SURFACE_2}, stop:1 {theme.SURFACE_2});"
            f" border: 1px solid {theme.BORDER}; border-radius: 8px; }}"
        )


class PlanPanel(QtWidgets.QFrame):
    """Theo huong di: moi dong mot huong (da gop huong cung loi). An khi khong co."""

    MAX_ROWS = 4

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("bar")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        head = QtWidgets.QHBoxLayout()
        head.addWidget(_overline("theo hướng đi"))
        head.addStretch()
        head.addWidget(_label("chọn dòng hợp hướng của bạn", size=theme.SIZES["sm"],
                              color=theme.TEXT_MUTED, wrap=False))
        layout.addLayout(head)
        self.rows = [PlanRow(self) for _ in range(self.MAX_ROWS)]
        for row in self.rows:
            layout.addWidget(row)
        self.set_data([])

    def set_data(self, lines: Sequence[PlanLineVM]) -> None:
        for i, row in enumerate(self.rows):
            if i < len(lines):
                row.set_data(lines[i])
            row.setVisible(i < len(lines))
        self.setVisible(bool(lines))


class Timeline(QtWidgets.QWidget):
    """Dải thời gian: ● vòng chọn lõi, ▲ lần reroll, ▍vị trí đang xem."""

    seek = QtCore.pyqtSignal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.duration = 1.0
        self.position = 0.0
        self.rounds: list[float] = []
        self.rerolls: list[float] = []

    def set_data(self, duration: float, rounds: Sequence[float], rerolls: Sequence[float]) -> None:
        self.duration = max(1.0, duration)
        self.rounds, self.rerolls = list(rounds), list(rerolls)
        self.update()

    def set_position(self, t: float) -> None:
        self.position = t
        self.update()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:   # noqa: N802
        self.seek.emit(max(0.0, event.position().x() / max(1, self.width()) * self.duration))

    def paintEvent(self, _event) -> None:                    # noqa: N802
        if self.width() <= 0 or self.height() <= 0:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        mid = self.height() / 2

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(theme.SURFACE_3))
        painter.drawRoundedRect(QtCore.QRectF(0, mid - 2, self.width(), 4), 2, 2)

        for t in self.rerolls:
            self._marker(painter, t, QtGui.QColor(theme.TEXT_MUTED), triangle=True)
        for t in self.rounds:
            self._marker(painter, t, QtGui.QColor(theme.ACCENT), triangle=False)

        x = self._x(self.position)
        painter.setBrush(QtGui.QColor(theme.TEXT))
        painter.drawRoundedRect(QtCore.QRectF(x - 1, mid - 9, 2, 18), 1, 1)

    def _x(self, t: float) -> float:
        return max(0.0, min(1.0, t / self.duration)) * self.width()

    def _marker(self, painter: QtGui.QPainter, t: float, color: QtGui.QColor, *, triangle: bool) -> None:
        x, mid = self._x(t), self.height() / 2
        painter.setBrush(color)
        if triangle:
            path = QtGui.QPainterPath()
            path.moveTo(x, mid - 7)
            path.lineTo(x - 4, mid - 1)
            path.lineTo(x + 4, mid - 1)
            path.closeSubpath()
            painter.drawPath(path)
        else:
            painter.drawEllipse(QtCore.QPointF(x, mid), 4.5, 4.5)
