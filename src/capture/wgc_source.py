"""Nguon khung song: chup THEO CUA SO game bang Windows Graphics Capture.

Chup theo cua so (khong phai ca desktop) la cach SPEC 3.1 chon: khong lay
overlay cua chinh ta nen khong co vong lap tu doc lai loi khuyen, va khong can
WDA_EXCLUDEFROMCAPTURE (xem src/overlay/overlay_window.py). Chi doc pixel - khong
cham tien trinh game (SPEC 1.3).

WGC chi giao khung khi noi dung doi va chay tren luong rieng cua thu vien. Lop
nay giu MOT khung moi nhat; luong phan tich lay no khi ranh (`latest`), khung
cu bi bo - phan tich cham khong duoc keo tre ca hang doi.
"""

from __future__ import annotations

import threading
import time

import numpy as np

from .frame_source import Frame, format_ref


class WgcFrameSource:
    """Khung moi nhat cua mot cua so, qua `windows-capture`."""

    def __init__(self, hwnd: int, ref_prefix: str = "live", client_size: tuple[int, int] | None = None):
        self.hwnd = int(hwnd)
        self.ref_prefix = ref_prefix
        # (w, h) vung client: o che do cua so co vien, WGC tra ca khung vien.
        self.client_size = client_size
        self._lock = threading.Lock()
        self._latest: Frame | None = None
        self._seq = 0
        self._t0 = time.perf_counter()
        self._control = None
        self._thread: threading.Thread | None = None
        self.error: Exception | None = None
        self.frames = 0

    # -- vong doi -----------------------------------------------------------

    def start(self) -> None:
        from windows_capture import WindowsCapture  # noqa: PLC0415

        capture = WindowsCapture(cursor_capture=False, draw_border=False, window_hwnd=self.hwnd)

        @capture.event
        def on_frame_arrived(frame, capture_control):  # noqa: ANN001
            self._control = capture_control
            self._store(frame.frame_buffer)

        @capture.event
        def on_closed():
            pass

        def run() -> None:
            try:
                capture.start()          # chan den khi stop()
            except Exception as exc:     # noqa: BLE001 - bao len vo, khong nuot
                self.error = exc

        self._thread = threading.Thread(target=run, name="wgc", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._control is not None:
            try:
                self._control.stop()
            except Exception:            # noqa: BLE001
                pass

    # -- du lieu ------------------------------------------------------------

    def _store(self, bgra: np.ndarray) -> None:
        image = bgra[..., :3]
        if self.client_size:
            w, h = self.client_size
            image = crop_client(image, w, h)
        t = time.perf_counter() - self._t0
        frame = Frame(image=np.ascontiguousarray(image), t=t, ref=format_ref(self.ref_prefix, t))
        with self._lock:
            self._latest = frame
            self._seq += 1
            self.frames += 1

    def latest(self) -> tuple[int, Frame | None]:
        """(so thu tu, khung moi nhat). So thu tu doi = co khung moi."""
        with self._lock:
            return self._seq, self._latest


def crop_client(image: np.ndarray, w: int, h: int) -> np.ndarray:
    """Cat vien cua so: vien hai ben va day bang nhau, phan du con lai la thanh tieu de."""
    H, W = image.shape[:2]
    if W <= w and H <= h:
        return image
    side = max(0, (W - w) // 2)
    top = max(0, H - h - side)
    return image[top:top + h, side:side + w]
