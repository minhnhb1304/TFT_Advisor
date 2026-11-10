"""Doc data/eval/split.json: vai tro va patch du lieu cua tung video."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_SPLIT = "data/eval/split.json"


def data_patch_for(video_id: str, split_path: str | Path = DEFAULT_SPLIT) -> str | None:
    """Patch du lieu dung de cham video nay, None neu video khong co trong split.

    None nghia la dung du lieu hien tai - dung cho video demo hoac ban ghi moi
    chua vao bo danh gia, KHONG dung cho video da co trong split.
    """
    path = Path(split_path)
    if not path.exists():
        return None
    for video in json.loads(path.read_text(encoding="utf-8"))["videos"]:
        if video["video_id"] == video_id:
            return video["data_patch"]
    return None
