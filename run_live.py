"""TFT Advisor - vo LIVE: tu van chon loi ngay trong tran.

    .venv\\Scripts\\python run_live.py                       # tim cua so game, overlay de len
    .venv\\Scripts\\python run_live.py --card-reader ocr     # hybrid (mac dinh) | ocr | gemini
    .venv\\Scripts\\python run_live.py --video D:\\tft_record\\minh_06.mp4 --start 1090
                                                            # mo phong: phat video theo dong ho that

Dung CUNG LiveSession voi replay (src/live/session.py) - hanh vi tren record
bang hanh vi trong tran. Vo nay chi them ba thu:
  1. nguon khung: chup THEO CUA SO game bang WGC (src/capture/wgc_source.py);
  2. vong phan tich tren luong rieng (src/live/runner.py);
  3. cua so overlay trong suot, click xuyen qua (src/overlay/live_window.py).

AN TOAN (SPEC 1.3): chi doc pixel cua cua so game, khong doc bo nho, khong
gui phim/chuot vao game. Game phai o che do Borderless/Windowed.
Thoat: Ctrl+C o cua so lenh, hoac dong game (overlay tu tat sau vai giay).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import signal
import sys
import time

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tư vấn chọn lõi ngay trong trận (overlay)")
    ap.add_argument("--regions", default="config/screen_regions.yaml")
    # hybrid: OCR truoc, Gemini chi doc bu o OCR khong chac. Khong co khoa Gemini thi
    # loi goi do bi bat va giu ket qua OCR (test_card_reader) - chay duoc moi may.
    ap.add_argument("--card-reader", choices=("ocr", "gemini", "hybrid"), default="hybrid")
    ap.add_argument("--fps", type=float, default=4.0, help="số lần phân tích mỗi giây")
    ap.add_argument("--title", help="ép tiêu đề cửa sổ game nếu client đổi tên")
    ap.add_argument("--video", help="mô phỏng: phát video này thay cho game")
    ap.add_argument("--start", type=float, default=0.0, help="mô phỏng: giây bắt đầu")
    ap.add_argument("--shot", help="chụp overlay ra file PNG sau --after giây rồi thoát (kiểm tra)")
    ap.add_argument("--after", type=float, default=20.0)
    args = ap.parse_args(argv)

    from PyQt6 import QtCore, QtWidgets  # noqa: PLC0415

    from src.capture.regions import ScreenRegions  # noqa: PLC0415
    from src.knowledge.name_index import NameIndex  # noqa: PLC0415
    from src.live.runner import AnalysisLoop, VideoClockSource  # noqa: PLC0415
    from src.overlay.live_window import LiveOverlay  # noqa: PLC0415
    from src.replay import theme  # noqa: PLC0415
    from src.replay.window import build_session  # noqa: PLC0415
    from src.utils.settings import Settings  # noqa: PLC0415

    app = QtWidgets.QApplication(sys.argv)
    theme.load_fonts()
    theme.apply("arena")

    settings = Settings.load()
    regions = ScreenRegions.load(ROOT / args.regions)
    session = build_session(regions, settings, NameIndex.load(settings.path("name_index")),
                            args.card_reader, source_id=f"live-{time.strftime('%Y%m%d-%H%M%S')}")

    preview = bool(args.video)
    view = LiveOverlay(regions, preview=preview)

    if preview:
        source = VideoClockSource(args.video, start_s=args.start)
        view.resize(1600, 900)
        game = None
    else:
        from src.capture.game_window import find_game_window  # noqa: PLC0415
        from src.capture.wgc_source import WgcFrameSource  # noqa: PLC0415

        game = find_game_window(args.title)
        if game is None:
            print("Không tìm thấy cửa sổ game TFT. Mở game (Borderless) rồi chạy lại, "
                  "hoặc dùng --title nếu client đổi tên.")
            return 1
        print(f"Cửa sổ game: '{game.title.strip()}' {game.w}x{game.h} tại ({game.x}, {game.y})")
        source = WgcFrameSource(game.hwnd, client_size=(game.w, game.h))
        _place(view, game, app)

    # Su kien tu luong phan tich -> luong Qt qua tin hieu (an toan luong).
    class Bridge(QtCore.QObject):
        event = QtCore.pyqtSignal(object, bool)

    bridge = Bridge()
    bridge.event.connect(view.on_event)
    latest_frame: list = [None]

    # Log do tre de do NFR that trong tran (doc HUD khi game chay chua tung do).
    log_dir = ROOT / "data" / "live_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{session.source_id}.jsonl"
    log = log_path.open("a", encoding="utf-8")
    stats = {"advice": 0, "hud_ms": [], "cards_ms": [], "step_ms": []}

    def on_event(event) -> None:
        record = {"type": type(event).__name__, "t": round(getattr(event, "t", 0.0), 3),
                  "step_ms": round(loop.last_step_ms, 1), "visible": bool(session.screen_visible)}
        latency = getattr(event, "latency_ms", None) or {}
        if latency:
            record["latency_ms"] = {k: round(v, 1) for k, v in latency.items()}
            stats["cards_ms"] += [latency["cards"]] if "cards" in latency else []
        if type(event).__name__ == "AdviceReady":
            stats["advice"] += 1
            record["stage"] = event.stage
        hud_ms = getattr(session, "last_hud_ms", None)
        new_hud = bool(hud_ms) and hud_ms != stats.get("last_hud")
        if new_hud:
            stats["last_hud"] = hud_ms
            stats["hud_ms"].append(hud_ms)
            record["hud_ms"] = round(hud_ms, 1)
        if record["type"] != "Idle" or new_hud:
            log.write(json.dumps(record, ensure_ascii=False) + "\n")
            log.flush()
        bridge.event.emit(event, bool(session.screen_visible))

    loop = AnalysisLoop(source, session, on_event, fps=args.fps)
    source.start()
    loop.start()
    view.show()

    timer = QtCore.QTimer()
    timer.setInterval(500)

    def tick() -> None:
        if preview:
            _, frame = source.latest()
            if frame is not None and frame is not latest_frame[0]:
                latest_frame[0] = frame
                view.set_frame(frame.image)
        elif game is not None:
            from src.capture.game_window import find_game_window  # noqa: PLC0415

            now = find_game_window(args.title)
            if now is None:
                view.hide()
            else:
                _place(view, now, app)
                view.show()
            if getattr(source, "error", None):
                view.status = f"lỗi chụp: {source.error}"

    timer.timeout.connect(tick)
    timer.start()

    # Ctrl+C: Qt chan tin hieu Python neu khong co gi chay Python dinh ky.
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    if args.shot:
        def shoot() -> None:
            view.grab().save(args.shot)
            print(f"đã chụp {args.shot} · {loop.steps} lần phân tích, lần cuối {loop.last_step_ms:.0f} ms")
            app.quit()
        QtCore.QTimer.singleShot(int(args.after * 1000), shoot)

    code = app.exec()
    loop.stop()
    source.stop()
    log.close()
    hud = sorted(stats["hud_ms"])
    hud_txt = f" · đọc HUD trung vị {hud[len(hud) // 2]:.0f} ms ({len(hud)} lần)" if hud else ""
    print(f"Log độ trễ: {log_path} · {loop.steps} lần phân tích · {stats['advice']} lần khuyên"
          f"{hud_txt} · lỗi {loop.errors}")
    return code


def _place(view, game, app) -> None:
    """Dat overlay trung khit vung client game. Win32 tra pixel vat ly, Qt dung pixel logic."""
    screen = app.screenAt(__import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(game.x, game.y)) \
        or app.primaryScreen()
    ratio = screen.devicePixelRatio() if screen else 1.0
    view.setGeometry(int(game.x / ratio), int(game.y / ratio), int(game.w / ratio), int(game.h / ratio))


if __name__ == "__main__":
    raise SystemExit(main())
