"""Icon loi cho vo replay: `data/augment_icons/<apiName>.png` (scripts/fetch_augment_icons.py).

Nap luoi va cache theo apiName. Thieu file (CDragon 522, hoac loi chi co icon giu
cho `missing-t*`) thi vo nho icon CAT TU THE LOI tren khung dang xem (`remember`).
Khong co ca hai thi tra None - widget ve o chu cai, khong bao gio de trong.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6 import QtGui

ICON_DIR = Path(__file__).resolve().parents[2] / "data" / "augment_icons"
_cache: dict[str, QtGui.QPixmap | None] = {}


def augment_pixmap(api_name: str) -> QtGui.QPixmap | None:
    if not api_name:
        return None
    if api_name not in _cache:
        path = ICON_DIR / f"{api_name}.png"
        pixmap = QtGui.QPixmap(str(path)) if path.exists() else None
        _cache[api_name] = pixmap if pixmap is not None and not pixmap.isNull() else None
    return _cache[api_name]


def remember(api_name: str, image_bgr) -> None:
    """Giu icon cat tu the loi (BGR numpy) cho loi chua co file. Khong de file da co."""
    if not api_name or augment_pixmap(api_name) is not None or image_bgr is None:
        return
    import cv2  # noqa: PLC0415

    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB).copy()
    h, w = rgb.shape[:2]
    if h == 0 or w == 0:
        return
    qimg = QtGui.QImage(rgb.data, w, h, w * 3, QtGui.QImage.Format.Format_RGB888).copy()
    _cache[api_name] = QtGui.QPixmap.fromImage(qimg)
