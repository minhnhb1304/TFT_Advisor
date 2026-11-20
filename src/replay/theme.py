"""Token mau/chu cua vo replay (docs/playtest-fixes/ui-tokens.md).

MOT NOI DUY NHAT chua mau. Widget khong duoc viet hex roi rac - sua mot mau ma
phai di tim sau cho la cach mot bang mau chet.

Co HAI bang mau de doi chieu (`apply("amber")` / `apply("blitz")`):

  amber - ban dau: nen nga am, mot mau nhan vang, tier tu vang -> lam -> xam.
  blitz - do thang tu CSS that cua blitz.gg: nen hue 222 gan den (#14171f),
          the chi sang hon nen mot chut va VIEN moi la thu tach khoi, tier chay
          vang -> ngoc lam -> nhat dan roi chim han vao nen o bac cuoi.

Nen khong bao gio den thuan; chu dung do mo, khong dung hex dac.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- token ---------------------------------------------------------------

PALETTES: dict[str, dict[str, object]] = {
    # MAC DINH tu 2026-11-14 (ui-ux-pro-max + mau Blitz): nen than lanh gan den,
    # be mat tach bang do sang + vien 6% trang, ngoc = so cua minh / hanh dong
    # CHON, vang = bac va canh bao/DOI. Khong neon, khong tim.
    "arena": {
        "BG": "#0a0d13", "SURFACE_1": "#10141c", "SURFACE_2": "#151b26", "SURFACE_3": "#1d2533",
        "BORDER": "#222b3a", "BORDER_STRONG": "#303c51",
        "ACCENT": "#2ee6c5", "WARN": "#f5b544", "DANGER": "#ff6b81", "OK": "#5ee09a",
        "TIER_COLORS": {"S": "#f5b544", "A": "#2ee6c5", "B": "#7aa2ff", "C": "#9aa4b2",
                        "D": "#5c6676", "": "#5c6676"},
    },
    # --- nhom "song dong": mau nhan bao hoa cao tren nen gan trung tinh -------
    # Tim dien + hong: nang luong cao nhat, nen van giu bao hoa thap de mau nhan
    # khong bi nen tranh cho.
    "neon": {
        "BG": "#0c0c0e", "SURFACE_1": "#121217", "SURFACE_2": "#181821", "SURFACE_3": "#23232e",
        "BORDER": "#272733", "BORDER_STRONG": "#3b3b4c",
        "ACCENT": "#a855f7", "WARN": "#fbbf24", "DANGER": "#fb5c7d", "OK": "#4ade80",
        "TIER_COLORS": {"S": "#f472b6", "A": "#a78bfa", "B": "#60a5fa", "C": "#94a3b8",
                        "D": "#64748b", "": "#94a3b8"},
    },
    # Do rua (kieu Valorant) tren nen den am: manh, dut khoat, khong dinh navy.
    "ember": {
        "BG": "#101013", "SURFACE_1": "#16161a", "SURFACE_2": "#1c1c21", "SURFACE_3": "#26262d",
        "BORDER": "#2a2a31", "BORDER_STRONG": "#3f3f49",
        "ACCENT": "#ff4655", "WARN": "#ffb020", "DANGER": "#ff6b6b", "OK": "#4ade80",
        "TIER_COLORS": {"S": "#ff4655", "A": "#ff9f1c", "B": "#ffd166", "C": "#9aa0a6",
                        "D": "#5f6368", "": "#9aa0a6"},
    },
    # Chanh dien: mau nhan sang nhat trong nhom, hop voi nen rat toi.
    "citrus": {
        "BG": "#0c0d0c", "SURFACE_1": "#121412", "SURFACE_2": "#181a18", "SURFACE_3": "#232622",
        "BORDER": "#272a26", "BORDER_STRONG": "#3b403a",
        "ACCENT": "#a3e635", "WARN": "#fbbf24", "DANGER": "#f87171", "OK": "#4ade80",
        "TIER_COLORS": {"S": "#a3e635", "A": "#fbbf24", "B": "#60a5fa", "C": "#9ca3af",
                        "D": "#6b7280", "": "#9ca3af"},
    },
    # Hong canh sen: hiem gap trong cong cu game nen de nho, van du sang de doc.
    "magenta": {
        "BG": "#0f0d11", "SURFACE_1": "#161219", "SURFACE_2": "#1b1620", "SURFACE_3": "#26202c",
        "BORDER": "#2b2432", "BORDER_STRONG": "#3f3548",
        "ACCENT": "#ff4d9d", "WARN": "#fbbf24", "DANGER": "#fb7185", "OK": "#4ade80",
        "TIER_COLORS": {"S": "#ff4d9d", "A": "#c084fc", "B": "#60a5fa", "C": "#a1a1aa",
                        "D": "#6b6b75", "": "#a1a1aa"},
    },

    # Radix slate (toi) + xanh ngoc hextech cua Riot. Vang chi con la mau trang
    # thai, khong phai mau thuong hieu -> tranh cap navy+vang cua esports doi cu.
    "hextech": {
        "BG": "#111113", "SURFACE_1": "#18191b", "SURFACE_2": "#212225", "SURFACE_3": "#292b2e",
        "BORDER": "#2b2d30", "BORDER_STRONG": "#43484e",
        "ACCENT": "#0ac8b9", "WARN": "#e3ae28", "DANGER": "#e84057", "OK": "#5ad0ac",
        "TIER_COLORS": {"S": "#e3ae28", "A": "#41c8f6", "B": "#5ad0ac", "C": "#acb9c3",
                        "D": "#6b7075", "": "#6b7075"},
    },
    # Vercel Geist: thang xam bao hoa 0% o CA 10 buoc, toan bo mau nam o mau nhan.
    "geist": {
        "BG": "#0a0a0a", "SURFACE_1": "#111111", "SURFACE_2": "#171717", "SURFACE_3": "#222222",
        "BORDER": "#282828", "BORDER_STRONG": "#3d3d3d",
        "ACCENT": "#0070f3", "WARN": "#f5a623", "DANGER": "#e5484d", "OK": "#45d483",
        "TIER_COLORS": {"S": "#0070f3", "A": "#45d483", "B": "#f5a623", "C": "#8f8f8f",
                        "D": "#5c5c5c", "": "#8f8f8f"},
    },
    # Linear: nen sau nhat trong nhom (#08090a), mau nhan tim cham (iris).
    "linear": {
        "BG": "#08090a", "SURFACE_1": "#0f1011", "SURFACE_2": "#16181a", "SURFACE_3": "#1f2124",
        "BORDER": "#24282c", "BORDER_STRONG": "#2a2e33",
        "ACCENT": "#5e6ad2", "WARN": "#f2b25c", "DANGER": "#eb5757", "OK": "#4cb782",
        "TIER_COLORS": {"S": "#7c8aff", "A": "#4cb782", "B": "#f2b25c", "C": "#8a8f98",
                        "D": "#5b6068", "": "#8a8f98"},
    },
    # Semi Design (ByteDance): con mot hoi lanh (8% bao hoa), xanh sang.
    "semi": {
        "BG": "#16161a", "SURFACE_1": "#1c1d22", "SURFACE_2": "#232429", "SURFACE_3": "#35363c",
        "BORDER": "#2f3036", "BORDER_STRONG": "#4f5159",
        "ACCENT": "#54a9ff", "WARN": "#f7c034", "DANGER": "#f54e4e", "OK": "#30c9c9",
        "TIER_COLORS": {"S": "#54a9ff", "A": "#30c9c9", "B": "#f7c034", "C": "#7b7c85",
                        "D": "#5a5b63", "": "#7b7c85"},
    },
    # Arco (ByteDance) + xanh ngoc lam: mau chua bi esports-vang hay SaaS-xanh chiem.
    "teal": {
        "BG": "#17171a", "SURFACE_1": "#1d1d20", "SURFACE_2": "#232326", "SURFACE_3": "#2e2e30",
        "BORDER": "#303033", "BORDER_STRONG": "#48484a",
        "ACCENT": "#30c9c9", "WARN": "#f7c034", "DANGER": "#f54e4e", "OK": "#57d675",
        "TIER_COLORS": {"S": "#30c9c9", "A": "#6bb7ff", "B": "#f7c034", "C": "#7a7a7d",
                        "D": "#5a5a5d", "": "#7a7a7d"},
    },
    # Ant Design nen den sau + tim (mau ByteDance danh cho boi canh AI).
    "violet": {
        "BG": "#0d0d0f", "SURFACE_1": "#141416", "SURFACE_2": "#1b1b1f", "SURFACE_3": "#26262b",
        "BORDER": "#2a2a2f", "BORDER_STRONG": "#424247",
        "ACCENT": "#9f7aea", "WARN": "#f7c034", "DANGER": "#f54e4e", "OK": "#4ade9b",
        "TIER_COLORS": {"S": "#9f7aea", "A": "#54a9ff", "B": "#f7c034", "C": "#77777e",
                        "D": "#56565c", "": "#77777e"},
    },
    # DOI CHUNG: bang mau cu, do tu blitz.gg. Giu lai de so sanh chu khong de dung:
    # nen bao hoa 22% (chuan hien dai <= 8%) va vang nam dung o cho cua mau CANH BAO.
    "blitz": {
        "BG": "#14171f", "SURFACE_1": "#171a21", "SURFACE_2": "#1a1d23", "SURFACE_3": "#23262d",
        "BORDER": "#31343a", "BORDER_STRONG": "#43464d",
        "ACCENT": "#f4af25", "WARN": "#e8935c", "DANGER": "#e84057", "OK": "#30d9d3",
        "TIER_COLORS": {"S": "#f4af25", "A": "#30d9d3", "B": "#9dd5d7", "C": "#c0d4d8",
                        "D": "#585c65", "": "#585c65"},
    },
}

ACTIVE = "arena"

BG = SURFACE_1 = SURFACE_2 = SURFACE_3 = BORDER = BORDER_STRONG = ""
ACCENT = WARN = DANGER = OK = ""
ACCENT_FILL = ""
TIER_COLORS: dict[str, str] = {}

TEXT = "rgba(255,255,255,0.92)"
TEXT_2 = "rgba(255,255,255,0.62)"
TEXT_MUTED = "rgba(255,255,255,0.42)"
TEXT_FAINT = "rgba(255,255,255,0.28)"

# Do hiem cua loi trong game. "Ngoc sac" khong co mau don nao dung -> dai chuyen mau.
RARITY = {
    1: ("bạc", "#a6acb9", "#a6acb9"),
    2: ("vàng", "#ffbf50", "#ffbf50"),
    3: ("ngọc sắc", "#9b8cff", "#5ecfd6"),
}

# Mau theo HUONG di (directional). Co dinh qua moi bang mau: nguoi choi hoc mau
# cua huong mot lan roi nhan ra no o panel, overlay tren video va overlay trong
# tran. Vang = giu tien, do = danh ngay, ngoc = reroll, xanh la = thieu tien.
PLAN_COLORS = {
    "fast9": "#ffb547", "fast8": "#ff6b81", "reroll": "#3fd5ff", "cash": "#9be15d",
}
PLAN_FALLBACK = "#a6acb9"


def plan_color(key: str) -> str:
    return PLAN_COLORS.get(key, PLAN_FALLBACK)


def apply(name: str) -> str:
    """Doi bang mau dang dung. Tra ve ten da ap dung."""
    global ACTIVE, ACCENT_FILL, TIER_COLORS
    palette = PALETTES[name]
    ACTIVE = name
    for key, value in palette.items():
        globals()[key] = dict(value) if isinstance(value, dict) else value
    ACCENT_FILL = _alpha(str(palette["ACCENT"]), 0.12)
    return name


def toggle() -> str:
    names = list(PALETTES)
    return apply(names[(names.index(ACTIVE) + 1) % len(names)])


# Be Vietnam Pro: chu than, thiet ke cho tieng Viet. Chakra Petch: tieu de, so,
# nhan viet hoa - kieu esports, co dau tieng Viet. Dong goi o assets/fonts (OFL),
# nap bang `load_fonts()`; thieu file thi roi ve Segoe UI.
FONT = "'Be Vietnam Pro', 'Segoe UI', sans-serif"
DISPLAY = "'Chakra Petch', 'Segoe UI', sans-serif"
MONO = DISPLAY
# Ban dung TRONG rich text: style='...' bao bang nhay don, nen ten font phai dung nhay kep.
DISPLAY_HTML = DISPLAY.replace("'", '"')
FONT_HTML = FONT.replace("'", '"')
FONT_DIR = __import__("pathlib").Path(__file__).resolve().parents[2] / "assets" / "fonts"


def load_fonts() -> list[str]:
    """Dang ky font dong goi voi Qt. Goi sau khi co QApplication. Tra ve ho font da nap."""
    from PyQt6 import QtGui  # noqa: PLC0415

    families: list[str] = []
    for path in sorted(FONT_DIR.glob("*.ttf")):
        font_id = QtGui.QFontDatabase.addApplicationFont(str(path))
        families += QtGui.QFontDatabase.applicationFontFamilies(font_id) if font_id >= 0 else []
    return sorted(set(families))
# Blitz chi dung 7 co chu trong toan bo UI du lieu, khong co gi lon hon 22px.
SIZES = {"xs": 11, "sm": 12, "md": 13, "base": 14, "lg": 16, "xl": 20, "xxl": 24}
SPACE = (4, 8, 12, 16, 20)
RADIUS = 10

# Danh dau lua chon nen chon: nen accent 15% + chu accent, hoac vien 2px.
# Blitz KHONG dung thanh ben trai, khong sao, khong vien day.
ACCENT_SELECT = 0.15
# Than the nhuom mau tier 8%, hover 10%, vien 20% - mot token dung o bon do manh.
TIER_BODY = 0.08
TIER_RAIL = 0.50
DISABLED_OPACITY = 0.38


@dataclass(frozen=True)
class TierStyle:
    """Mot bac tier = ba gia tri: chu, vien, nen."""

    text: str
    border: str
    fill: str


def tier_style(tier: str) -> TierStyle:
    color = TIER_COLORS.get((tier or "").upper(), TIER_COLORS[""])
    return TierStyle(text=color, border=_alpha(color, 0.88), fill=_alpha(color, 0.12))


def rarity_style(tier: int | None) -> tuple[str, str, str]:
    """(ten, mau trai, mau phai) - hai mau bang nhau tru 'ngoc sac'."""
    return RARITY.get(int(tier or 0), ("", BORDER, BORDER))


def _alpha(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha:.2f})"


# --- stylesheet -------------------------------------------------------------


def qss() -> str:
    """QSS goc cua cua so. Widget rieng tu bo sung style cuc bo."""
    return f"""
QWidget {{ background: {BG}; color: {TEXT}; font-family: {FONT}; font-size: {SIZES['base']}px; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
QFrame#card {{ background: {SURFACE_2}; border: 1px solid {BORDER}; border-radius: {RADIUS}px; }}
QFrame#bar {{ background: {SURFACE_1}; border: 1px solid {BORDER}; border-radius: {RADIUS}px; }}
QFrame#header {{ background: {SURFACE_1}; border: 1px solid {BORDER}; border-radius: {RADIUS}px; }}
QLabel {{ background: transparent; }}
QLabel[role="mono"] {{ font-family: {MONO}; }}
QLabel[role="muted"] {{ color: {TEXT_MUTED}; font-size: {SIZES['sm']}px; }}
QLabel[role="secondary"] {{ color: {TEXT_2}; font-size: {SIZES['md']}px; }}
QLabel[role="warn"] {{ color: {WARN}; font-size: {SIZES['sm']}px; }}
QPushButton {{
    background: transparent; color: {TEXT_2}; border: 1px solid {BORDER_STRONG};
    border-radius: 8px; padding: 7px 14px; font-family: {DISPLAY}; font-weight: 600;
    font-size: {SIZES['md']}px; letter-spacing: 0.3px;
}}
QPushButton:hover {{ background: {SURFACE_3}; color: {TEXT}; border-color: {_alpha(ACCENT, 0.5)}; }}
QPushButton:pressed {{ background: {_alpha(ACCENT, 0.12)}; }}
QPushButton:disabled {{ color: {TEXT_FAINT}; border-color: {BORDER}; }}
QPushButton[role="primary"] {{
    background: {ACCENT}; color: #06110f; border: 1px solid {ACCENT};
}}
QPushButton[role="primary"]:hover {{ background: {_alpha(ACCENT, 0.85)}; color: #06110f; }}
QPushButton[role="marker"] {{
    font-family: {MONO}; padding: 5px 12px; border-radius: 14px; color: {TEXT_2};
    background: {SURFACE_2}; border-color: {BORDER};
}}
QPushButton[role="marker"]:hover {{ color: {ACCENT}; border-color: {_alpha(ACCENT, 0.6)}; }}
QComboBox {{
    background: {SURFACE_2}; color: {TEXT_2}; border: 1px solid {BORDER_STRONG};
    border-radius: 8px; padding: 5px 10px; font-family: {MONO};
}}
QComboBox QAbstractItemView {{ background: {SURFACE_2}; color: {TEXT}; selection-background-color: {SURFACE_3}; }}
QSlider::groove:horizontal {{ height: 4px; background: {SURFACE_3}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    width: 14px; background: {TEXT}; border: 3px solid {ACCENT}; border-radius: 7px; margin: -6px 0;
}}
QScrollBar:vertical {{ background: transparent; width: 8px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {BORDER_STRONG}; border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QToolTip {{ background: {SURFACE_3}; color: {TEXT}; border: 1px solid {BORDER_STRONG};
    padding: 6px 8px; border-radius: 6px; }}
"""


apply(ACTIVE)
