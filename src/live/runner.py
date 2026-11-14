"""Vong phan tich cua vo live: lay khung moi nhat -> LiveSession.step -> su kien.

Khong Qt. Chay tren luong rieng; vo nhan su kien qua callback va tu chuyen ve
luong giao dien. Nguon khung chi can `latest() -> (seq, Frame | None)`:

    WgcFrameSource   (src/capture/wgc_source.py)  - cua so game that
    VideoClockSource (file nay)                    - video phat theo dong ho that,
                                                     de thu vo live khi khong co game

Khung cu bi bo: neu mot lan `step` mat 2 s thi lan sau lay khung MOI NHAT, khong
xu ly lan luot cac khung da troi qua. Dung voi tu van thoi gian thuc - loi khuyen
cho trang thai 2 s truoc khong co gia tri bang trang thai bay gio.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable

import cv2

from ..capture.frame_source import Frame, format_ref


class VideoClockSource:
    """Phat video theo dong ho that tu `start_s`, giong mot nguon song."""

    def __init__(self, path: str, start_s: float = 0.0, speed: float = 1.0, ref_prefix: str = "sim"):
        self.cap = cv2.VideoCapture(str(path))
        if not self.cap.isOpened():
            raise FileNotFoundError(f"không mở được video: {path}")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.start_s = start_s
        self.speed = speed
        self.ref_prefix = ref_prefix
        self.cap.set(cv2.CAP_PROP_POS_MSEC, start_s * 1000.0)
        self._t0 = time.perf_counter()
        self._pos = start_s
        self._seq = 0
        self._frame: Frame | None = None
        # Vo preview cung goi latest() tu luong Qt; bo giai ma ffmpeg cua OpenCV
        # khong an toan khi hai luong cung doc (assert async_lock trong libavcodec).
        self._lock = threading.Lock()

    def start(self) -> None:
        self._t0 = time.perf_counter()

    def stop(self) -> None:
        self.cap.release()

    def latest(self) -> tuple[int, Frame | None]:
        """Doc tuan tu toi thoi diem dong ho chi, bo qua khung trung gian (grab)."""
        with self._lock:
            return self._advance()

    def _advance(self) -> tuple[int, Frame | None]:
        target = self.start_s + (time.perf_counter() - self._t0) * self.speed
        image = None
        while self._pos + 1.0 / self.fps <= target:
            ok = self.cap.grab()
            if not ok:
                break
            self._pos += 1.0 / self.fps
            image = True
        if image:
            ok, img = self.cap.retrieve()
            if ok:
                self._seq += 1
                self._frame = Frame(img, self._pos, format_ref(self.ref_prefix, self._pos))
        return self._seq, self._frame


class AnalysisLoop:
    """Luong phan tich: toi da `fps` lan/giay, moi lan mot khung moi nhat."""

    def __init__(self, source: Any, session: Any, on_event: Callable[[Any], None], fps: float = 5.0):
        self.source = source
        self.session = session
        self.on_event = on_event
        self.period = 1.0 / max(0.5, fps)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.last_step_ms = 0.0
        self.steps = 0
        self.errors = 0

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="analysis", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout)

    def _run(self) -> None:
        last_seq = -1
        while not self._stop.is_set():
            began = time.perf_counter()
            seq, frame = self.source.latest()
            if frame is not None and seq != last_seq:
                last_seq = seq
                try:
                    event = self.session.step(frame)
                except Exception as exc:          # noqa: BLE001 - loi mot khung khong giet vong lap
                    self.errors += 1
                    event = exc
                self.last_step_ms = (time.perf_counter() - began) * 1000.0
                self.steps += 1
                self.on_event(event)
            self._stop.wait(max(0.0, self.period - (time.perf_counter() - began)))
