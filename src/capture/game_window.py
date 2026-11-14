"""Tim cua so game TFT va vung client cua no tren man hinh (vo live).

Lay tu tools/probe_environment.py (da chay voi client standalone 2026-10-13):
tieu de that la 'TFT  ' (co khoang trang duoi), lop `UnrealWindow`. Khop ca
tieu de lan lop truoc de mot game Unreal khac dang mo khong bi nhan nham.

`pick_window` thuan Python de test duoc; `find_game_window` goi Win32.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

WINDOW_CANDIDATES: tuple[tuple[str, str | None], ...] = (
    ("TFT", "UnrealWindow"),
    ("League of Legends (TM) Client", "RiotWindowClass"),
    ("Teamfight Tactics", None),
)
# Cua so nho hon muc nay la cua so phu cung ten (launcher, splash), khong phai game.
MIN_GAME_PX = 400 * 300


@dataclass(frozen=True)
class GameWindow:
    hwnd: int
    title: str
    cls: str
    x: int          # goc trai tren cua vung CLIENT, toa do man hinh
    y: int
    w: int
    h: int

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return self.x, self.y, self.w, self.h


def pick_window(
    windows: Sequence[dict], candidates: Iterable[tuple[str, str | None]] = WINDOW_CANDIDATES
) -> dict | None:
    """Chon cua so game. `windows`: dict co `title`, `class`, `w`, `h`."""
    for want, cls in candidates:
        for need_class in ((True, False) if cls else (False,)):
            for win in windows:
                if win["title"].strip() != want.strip():
                    continue
                if need_class and win["class"] != cls:
                    continue
                if win["w"] * win["h"] < MIN_GAME_PX:
                    continue
                return win
    return None


def find_game_window(title: str | None = None) -> GameWindow | None:
    """Cua so game dang hien, hoac None. `title` ep mot tieu de cu the."""
    import win32gui  # noqa: PLC0415 - chi co tren Windows

    visible: list[dict] = []

    def collect(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            text = win32gui.GetWindowText(hwnd)
            if text.strip():
                _, _, w, h = win32gui.GetClientRect(hwnd)
                visible.append({"hwnd": hwnd, "title": text,
                                "class": win32gui.GetClassName(hwnd), "w": w, "h": h})

    win32gui.EnumWindows(collect, None)
    candidates = (((title, None),) if title else ()) + WINDOW_CANDIDATES
    match = pick_window(visible, candidates)
    if match is None:
        return None
    x, y = win32gui.ClientToScreen(match["hwnd"], (0, 0))
    return GameWindow(int(match["hwnd"]), match["title"], match["class"], x, y,
                      match["w"], match["h"])
