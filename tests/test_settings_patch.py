"""Settings.for_patch: video cu duoc cham bang du lieu cua dung patch no duoc choi."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.utils.settings import PATCH_KEYS, Settings


def _settings(root: Path, current: str = "18.6") -> Settings:
    (root / "data").mkdir()
    (root / "data" / "patch_state.json").write_text(json.dumps({"current_patch": current}), encoding="utf-8")
    return Settings(Settings().data, root)


def _write_patch(root: Path, patch: str, skip: str = "") -> Path:
    folder = root / "data" / "patches" / patch
    folder.mkdir(parents=True)
    s = Settings()
    for key in PATCH_KEYS:
        name = Path(s.get("paths", key)).name
        if name != skip:
            (folder / name).write_text("{}", encoding="utf-8")
    return folder


def test_current_patch_and_none_keep_the_live_data(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    assert s.for_patch(None) is s
    assert s.for_patch("18.6") is s


def test_old_patch_points_patch_keys_into_its_folder(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    folder = _write_patch(tmp_path, "18.2")
    old = s.for_patch("18.2")
    for key in PATCH_KEYS:
        assert old.path(key).parent == folder
    # Co che dung chung moi patch: bang dac trung loi khong doi.
    assert old.path("augment_features") == s.path("augment_features")
    assert s.path("augment_tiers").parent == tmp_path / "data"


def test_missing_file_fails_loud_instead_of_using_live_data(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    _write_patch(tmp_path, "18.2", skip="augment_tiers.json")
    with pytest.raises(FileNotFoundError, match="18.2"):
        s.for_patch("18.2")


def test_repo_ships_the_18_2_snapshot() -> None:
    old = Settings.load().for_patch("18.2")
    tiers = json.loads(old.path("augment_tiers").read_text(encoding="utf-8"))
    assert tiers["meta"]["patch"] == "18.2"


def test_split_gives_each_recorded_video_its_data_patch() -> None:
    from src.eval.dataset_split import data_patch_for

    assert data_patch_for("minh_05") == "18.2"
    assert data_patch_for("dat_01") == "18.2"
    assert data_patch_for("not_in_split") is None
