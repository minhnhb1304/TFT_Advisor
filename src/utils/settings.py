"""Nap config/settings.yaml (SPEC 5).

Mot cho duy nhat doc file cau hinh. Moi module khac nhan gia tri qua tham so
constructor chu khong tu doc file - nho the test dung duoc cau hinh tong hop
ma khong phai ghi file tam, va khong module nao co the am tham bat mot co ma
cho con lai khong biet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import json

import yaml

DEFAULT_PATH = "config/settings.yaml"

# Du lieu PHU THUOC patch: tier, so lieu, doi hinh meta. Moi video duoc cham
# bang du lieu cua dung ban no duoc choi (data/eval/split.json `data_patch`).
# Bang dac trung loi, cong thuc do, ten loi KHONG o day: chung la co che, dung
# chung moi patch va la tap cha cua cac ban cu.
PATCH_KEYS = (
    "augment_stats_csv",
    "augment_tiers",
    "augment_tiers_backup",
    "meta_comps",
    "meta_comps_backup",
    "item_stats",
    # patch_state cua chinh snapshot: data_freshness so voi patch CUA VIDEO,
    # khong bao "18.2 < 18.6" moi lan cham video cu.
    "patch_state",
)
PATCHES_DIR = "data/patches"

DEFAULTS: dict[str, Any] = {
    "paths": {
        "augment_features": "data/augment_features.json",
        "augment_stats_csv": "data/augment_stats.csv",
        "augment_tiers": "data/augment_tiers.json",
        "augment_tiers_backup": "data/augment_tiers.metatft.json",
        "scoring_weights": "config/scoring_weights.yaml",
        "meta_comps": "data/meta_comps.tftacademy.json",
        "meta_comps_backup": "data/meta_comps.metatft.json",
        "item_recipes": "data/item_recipes.json",
        "core_items": "data/core_items.json",
        "augment_combos": "data/augment_combos.json",
        "champion_costs": "data/champion_costs.json",
        "item_stats": "data/tactics_tools_stats.json",
        "name_index": "data/name_index.json",
        "scenarios": "data/scenarios",
        "cdragon_cache": "data/cdragon_cache",
        "patch_state": "data/patch_state.json",
    },
    "locale": {"language": "vi_vn", "branch": "latest"},
    # Nguon crawl cho scripts/crawl_augment_stats.py. Chi dung OFFLINE luc
    # sinh du lieu - runtime khong bao gio goi Riot API (SPEC 3.5.3).
    "riot": {"platform": "vn2", "tiers": ["challenger", "grandmaster", "master"]},
    # Hotkey toan cuc. BAT BUOC di qua RegisterHotKey cua Win32 goi tu Qt
    # (SPEC 1.3): no la co che cap OS, KHONG cai hook WH_KEYBOARD_LL va
    # KHONG can quyen admin. Thu vien `keyboard` lam nguoc lai ca hai.
    "hotkeys": {
        "toggle_visibility": "F1",
        "toggle_click_through": "F2",
        "force_refresh": "F3",
        "toggle_detail": "F4",
        "quit": "Ctrl+Q",
    },
    "features": {
        "enable_scouting": False,
        "enable_llm_refinement": False,
        "llm_model": "gemini-3.5-flash-lite",
        "llm_hard_timeout_s": 2.0,
        "allow_unverified_roll_odds": False,
    },
    "logging": {"log_scenarios": True, "save_frames": False},
    "vision": {
        "gemini_model": "gemini-3.5-flash-lite",
        "gemini_timeout_s": 12.0,
        "enable_gemini_vision": True,
        "vote_window": 5,
    },
}


@dataclass
class Settings:
    """Cau hinh da nap, kem duong dan goc de resolve cac path tuong doi."""

    data: dict[str, Any] = field(default_factory=lambda: _deep_copy(DEFAULTS))
    root: Path = field(default_factory=Path)

    @classmethod
    def load(cls, path: str | Path = DEFAULT_PATH) -> "Settings":
        """Nap file, gop len tren gia tri mac dinh.

        Thieu file KHONG phai loi: toan bo mac dinh deu an toan (scouting tat,
        LLM tat, roll odds chua xac minh bi chan), nen he thong van chay dung.
        """
        p = Path(path)
        merged = _deep_copy(DEFAULTS)
        if p.exists():
            loaded = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            _deep_update(merged, loaded)
        root = p.resolve().parent.parent if p.exists() else Path.cwd()
        return cls(merged, root)

    def current_patch(self) -> str | None:
        """Patch cua du lieu o `data/` (do scripts/refresh_data.py ghi)."""
        path = self.path("patch_state")
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8")).get("current_patch")

    def for_patch(self, patch: str | None) -> "Settings":
        """Ban sao tro PATCH_KEYS vao `data/patches/<patch>/`.

        None hoac dung patch hien tai -> chinh no. Patch cu thieu file nao thi
        NO NGAY: am tham roi ve du lieu hien tai la cham video bang sai patch.
        """
        if patch is None or patch == self.current_patch():
            return self
        folder = self.root / PATCHES_DIR / patch
        merged = _deep_copy(self.data)
        for key in PATCH_KEYS:
            target = folder / Path(self.get("paths", key, "")).name
            if not target.exists():
                raise FileNotFoundError(f"Thiếu dữ liệu patch {patch}: {target}")
            merged["paths"][key] = str(target)
        return Settings(merged, self.root)

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return (self.data.get(section) or {}).get(key, default)

    def path(self, key: str) -> Path:
        """Duong dan trong muc `paths`, resolve theo goc du an."""
        raw = self.get("paths", key, "")
        p = Path(raw)
        return p if p.is_absolute() else self.root / p

    # Cac co duoc truy cap nhieu nhat, de o day cho goi ngan va de grep.

    @property
    def enable_scouting(self) -> bool:
        return bool(self.get("features", "enable_scouting", False))

    @property
    def enable_llm_refinement(self) -> bool:
        return bool(self.get("features", "enable_llm_refinement", False))

    @property
    def allow_unverified_roll_odds(self) -> bool:
        return bool(self.get("features", "allow_unverified_roll_odds", False))

    @property
    def log_scenarios(self) -> bool:
        return bool(self.get("logging", "log_scenarios", True))

    @property
    def enable_gemini_vision(self) -> bool:
        return bool(self.get("vision", "enable_gemini_vision", True))

    @property
    def gemini_model(self) -> str:
        return str(self.get("vision", "gemini_model", "gemini-3.5-flash-lite"))

    @property
    def gemini_timeout_s(self) -> float:
        return float(self.get("vision", "gemini_timeout_s", 6.0))

    @property
    def vote_window(self) -> int:
        return int(self.get("vision", "vote_window", 5))


def _deep_copy(data: dict[str, Any]) -> dict[str, Any]:
    return {k: (_deep_copy(v) if isinstance(v, dict) else v) for k, v in data.items()}


def _deep_update(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)
        else:
            target[key] = value
