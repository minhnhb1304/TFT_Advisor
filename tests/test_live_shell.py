"""Vo live: tim cua so game, cat vien cua so, vong phan tich, co man dang hien."""

from __future__ import annotations

import threading
import time

import numpy as np

from src.capture.frame_source import Frame
from src.capture.game_window import MIN_GAME_PX, pick_window
from src.capture.wgc_source import crop_client
from src.live.runner import AnalysisLoop


def win(title, cls, w=1920, h=1080):
    return {"title": title, "class": cls, "w": w, "h": h}


def test_picks_the_unreal_tft_window_with_trailing_spaces():
    windows = [win("Discord", "Chrome"), win("TFT  ", "UnrealWindow")]
    assert pick_window(windows)["class"] == "UnrealWindow"


def test_title_and_class_beat_title_only():
    other_unreal_named_tft = win("TFT", "SomeOtherClass")
    real = win("TFT", "UnrealWindow")
    assert pick_window([other_unreal_named_tft, real]) is real


def test_small_window_with_the_game_title_is_skipped():
    splash = win("TFT", "UnrealWindow", w=300, h=200)
    assert 300 * 200 < MIN_GAME_PX
    assert pick_window([splash]) is None


def test_no_game_window_returns_none():
    assert pick_window([win("Explorer", "CabinetWClass")]) is None


def test_crop_client_removes_border_and_title_bar():
    framed = np.zeros((1080 + 31 + 8, 1920 + 16, 3), np.uint8)
    framed[31:31 + 1080, 8:8 + 1920] = 255
    client = crop_client(framed, 1920, 1080)
    assert client.shape[:2] == (1080, 1920) and client.min() == 255


def test_crop_client_keeps_borderless_frames():
    frame = np.zeros((1080, 1920, 3), np.uint8)
    assert crop_client(frame, 1920, 1080) is frame


class FakeSource:
    def __init__(self, frames):
        self.frames = frames
        self.i = 0

    def latest(self):
        self.i = min(self.i + 1, len(self.frames))
        return self.i, self.frames[self.i - 1]


class FakeSession:
    def __init__(self, fail_at=None):
        self.seen = []
        self.fail_at = fail_at

    def step(self, frame):
        self.seen.append(frame.t)
        if frame.t == self.fail_at:
            raise RuntimeError("boom")
        return f"event@{frame.t}"


def run_loop(source, session, seconds=0.5):
    events, done = [], threading.Event()
    loop = AnalysisLoop(source, session, events.append, fps=50)
    loop.start()
    time.sleep(seconds)
    loop.stop()
    done.set()
    return loop, events


def frame(t):
    return Frame(np.zeros((4, 4, 3), np.uint8), t, f"test@{t}")


def test_loop_steps_each_new_frame_once():
    loop, events = run_loop(FakeSource([frame(0.0), frame(1.0), frame(2.0)]), FakeSession())
    assert events[:3] == ["event@0.0", "event@1.0", "event@2.0"]
    assert len(events) == 3                         # khong lap lai khung cu


def test_a_failing_frame_is_reported_and_the_loop_keeps_going():
    session = FakeSession(fail_at=1.0)
    loop, events = run_loop(FakeSource([frame(0.0), frame(1.0), frame(2.0)]), session)
    assert isinstance(events[1], RuntimeError) and events[2] == "event@2.0"
    assert loop.errors == 1


def test_session_reports_whether_the_screen_is_visible_now():
    from tests.test_live_session import session

    s, reroll, _, _ = session()
    reroll.present = True
    s.step(__import__("tests.test_live_session", fromlist=["frame"]).frame(0.0))
    assert s.screen_visible is True
    reroll.present = False
    s.step(__import__("tests.test_live_session", fromlist=["frame"]).frame(1.0))
    assert s.screen_visible is False
