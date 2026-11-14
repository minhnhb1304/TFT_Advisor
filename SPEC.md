# 🎮 TFT Advisory Agent — Project Specification (v4)

> **Repository**: [github.com/minhnhb1304/TFT_Agent](https://github.com/minhnhb1304/TFT_Agent)  
> **Author**: minhnhb1304  
> **Created**: 2026-08-06  
> **Updated**: 2026-11-14 (v4 — khớp với code tại `84ccbb3`; v3 Thesis Edition 2026-08-29)  
> **Status**: 🛠️ Đang triển khai — kế hoạch hiện hành ở [`docs/next-steps.md`](docs/next-steps.md)  
> **Loại dự án**: **Đồ án tốt nghiệp** — chạy cục bộ, single-user, **KHÔNG phát hành** (§11)  
> **Language**: Python 3.11+  
> **Platform**: Windows (PC — League Client)  
> **Target Set**: Set 18 — Enchanted Wilds (**ĐÃ LIVE từ 2026-08-26**, patch 18.1 / Unreal)  
> **Game Language**: Tiếng Việt  
> **LLM Provider**: Gemini Flash (`google-genai` SDK)  
> **Resolution**: 1920×1080

---

## 0. Changelog v4 (2026-11-14) — Khớp SPEC với code

v4 **không đổi hướng đồ án**. Nó sửa các chỗ SPEC v3 mô tả một kiến trúc dự kiến mà code thực tế đã đi
khác, sau ba lần rà soát đối chiếu SPEC với code (commit `84ccbb3`). Chỗ nào v3 còn giá trị tra cứu
thì giữ lại và đánh dấu *(lịch sử)*.

| # | Thay đổi v3 → v4 | Mục |
|---|---|---|
| 1 | Lõi dùng chung `src/live/LiveSession`: `Frame` → `LiveEvent` (`Idle` / `Status` / `AdviceReady` / `Cleared`), không Qt. Hai vỏ: replay (`run_replay.py` + `src/replay/`) và panel trong trận (mới chạy qua `scripts/demo_overlay.py`). **Vỏ live trong ván thật chưa có**; chụp WGC mới ở `tools/` | §2.1, §2.2, §3.6 |
| 2 | Không có `preflight.py`, `session_detector.py`, `economy.py`, `pool_tracker.py`, `template_matcher.py`, `board_reader.py`, `shop_reader.py`, `item_guide.py`, `screen_capture.py`, `region_detector.py`. Màn chọn lõi được nhận ra bằng **bộ đọc nút đổi** (`reroll_buttons.py`, `screen_present`) | §3.0–§3.4, §5 |
| 3 | Bộ đọc thẻ `src/live/card_reader.py`: OCR / Gemini / Hybrid. Replay mặc định `hybrid` (OCR trước, Gemini cho ô OCR không chắc); Gemini **không còn** là primary | §3.2, §9.3 |
| 4 | Đọc **lõi đã chọn** từ dải icon (`src/vision/held_augments.py`) → `state.augments` | §2.2, §3.2, §3.3 |
| 5 | **Gợi ý theo hướng**: `PlanFitScorer` + `AugmentAdvisor.rank_by_plan()`, 4 hướng trong `tuning.plan_fit`, `AdviceBundle.plans`. `rank()` không đổi | §3.5.6 (mới) |
| 6 | Bảng đặc trưng: **258** lõi; trích tất định → LLM chỉ sửa 4 trường → duyệt tay; schema thêm `econ_type`, `trait_count_reward`, `live`, `tier`, `extraction_method`, `confidence` | §3.4.1 |
| 7 | `Base`: lõi không có trong bảng tier nhận `unknown_score` 0,35, không phải trung tính. `BoardFit` không đọc `CompSelector`. Pool đổi lõi theo bậc **và** lượt chào | §3.4.2, §3.5, §3.5.4, §3.5.5 |
| 8 | Thước đo thực tế: `eval_playtest.py`, `eval_held_augments.py`, `eval_plan_advice.py`; scenario schema 3 | §12 |
| 9 | §7 là lịch sử; kế hoạch hiện hành ở `docs/next-steps.md` | §7 |

Tài liệu chi tiết của các thay đổi 4–5: [plan-conditioned-advice](docs/directional-augment/plan-conditioned-advice.md),
[implementation-plan](docs/directional-augment/implementation-plan.md), [`dev_log.md`](dev_log.md) §16–§18.

> ✅ **Không đổi tuyệt đối**: §1.3. v4 chỉ sửa mô tả cho đúng code, không nới lỏng dòng nào.

### Changelog v3 — Đổi Hướng Thành Đồ Án Nghiên Cứu *(lịch sử)*

v2 thiết kế quanh **Riot TFT developer policy**. v3 xác định lại: đây là **đồ án tốt nghiệp cá nhân,
chạy cục bộ, không phát hành**. Developer policy ràng buộc sản phẩm *đăng ký và phân phối* — đồ án này
không thuộc cả hai. **Riot ToS + Vanguard vẫn ràng buộc đầy đủ** (§11) — đây là hai trục độc lập.

| # | Thay đổi v2 → v3 | Lý do |
|---|---|---|
| 1 | **Augment Advisor thành tính năng số 1** — xếp hạng đầy đủ theo board state | Thể hiện năng lực thiết kế thuật toán Decision-Making. v2 §11 cấm đúng điều này |
| 2 | §11 "Compliance Contract" → **"Phạm vi, Đạo đức & Giới hạn Nghiên cứu"** | Policy không còn là design constraint; phạm vi + đạo đức thì có |
| 3 | Xoá `src/compliance/gate.py` → thêm `tests/test_readonly_invariant.py` | Biến §1.3 từ lời hứa thành **thuộc tính kiểm chứng được** bằng test |
| 4 | Thêm `data/augment_features.json` + `scripts/build_augment_features.py` | Metadata augment của CDragon **không dùng được** để chấm điểm — xem §3.4.1 |
| 5 | Thêm `stats_provider.py` — interface cắm-rút nhiều nguồn stats | Nguồn số liệu sẽ chốt sau; scoring engine không được phụ thuộc nguồn cụ thể |
| 6 | Thêm `ScenarioLogger` (Phase 3, **sớm**) + `src/eval/` | 3 trong 4 phương pháp đánh giá dùng **chung một dataset** — logger ra muộn = không có dữ liệu để đánh giá |
| 7 | Thêm §12 Phương pháp đánh giá | Đồ án cần bằng chứng đo được, không chỉ demo |
| 8 | `GameState.opponents` + `contest_score` quay lại (Phase 7, feature-flag) | Không còn bị policy cấm; hoãn lại vì khối lượng CV |
| 9 | Overwolf GEP: **loại bỏ** | Cần runtime Electron/JS và làm mất chính phần đóng góp CV của đồ án |

**Giữ nguyên từ v2.1** (đã re-verify 2026-08-28, xem [`research/`](research/overview.md)):
`dxcam>=0.3.0` · `google-genai` · `rapidocr` PP-OCRv6 · Set 18 live dùng `/latest/` · tier augment tra từ
`apiName`/`name` · 5 cặp augment không phân biệt được · đọc `icon` nguyên văn · `tft-match-v1`.

> ✅ **Không đổi tuyệt đối**: danh sách cấm ở §1.3. Đổi hướng đồ án **không** nới lỏng bất kỳ dòng nào.

---

## 1. Tổng Quan Dự Án

### 1.1 Mục Tiêu

Xây dựng một **hệ hỗ trợ ra quyết định (decision-support system)** cho Teamfight Tactics: đọc trạng thái
bàn cờ **chỉ bằng thị giác máy tính**, rồi **xếp hạng và giải thích** lựa chọn tốt nhất cho người chơi.

Đóng góp học thuật của đồ án nằm ở ba chỗ, không phải ở việc "làm được overlay":

| # | Đóng góp | Đo bằng |
|---|---|---|
| 1 | **Pipeline nhận diện** trạng thái game tiếng Việt từ pixel, không đọc memory | Precision / Recall / F1 + latency (§12.1) |
| 2 | **Thuật toán xếp hạng Augment** có điều kiện theo board state, có giải thích | Tương quan với kết quả thật + đồng thuận chuyên gia (§12.2, §12.3) |
| 3 | **Phương pháp trích đặc trưng offline** từ mô tả augment bằng LLM, cache lại và audit được | Ablation study (§12.4) |

### 1.2 Phạm Vi

| Có | Không |
|---|---|
| Overlay tư vấn (augment, đội hình, item, vị trí) | Auto-play (bot tự chơi hộ) |
| Đọc trạng thái game qua screen capture + CV | Đọc game memory (vi phạm Vanguard) |
| **Augment Advisor đầy đủ — xếp hạng theo board state, kèm lý do** | Tự động điều khiển mouse/keyboard |
| Kết hợp meta data từ nhiều nguồn (§3.4.2) | Inject code vào game process |
| Gemini Vision multimodal (nhận diện augment từ ảnh) | Train custom model (không cần) |
| Trích đặc trưng augment offline bằng LLM, cache lại | **Phát hành / phân phối cho người khác (§11)** |
| Hỗ trợ game tiếng Việt | Chơi hộ, boosting, chia sẻ tài khoản |
| Scouting đối thủ + `contest_score` — **Phase 7, mặc định tắt** | |

### 1.3 Nguyên Tắc An Toàn (Riot Vanguard) — **BẤT BIẾN KIẾN TRÚC**

> Đổi hướng sang đồ án nghiên cứu (§11) **không nới lỏng một dòng nào ở đây.**
> Mục này được **thi hành bằng test**, không phải bằng lời hứa: [`tests/test_readonly_invariant.py`](tests/).

> ⚠️ **Riot Vanguard** là anti-cheat kernel-level (Ring-0). Vi phạm = **ban vĩnh viễn + HWID ban**.

**✅ An toàn** (research xác nhận — Riot định nghĩa pixelbot là *"a computer vision cheat that **injects
player input**"*, tức **injection** mới là dấu hiệu định danh):
- Screen capture (đọc pixel từ desktop/DWM)
- Overlay window (`WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE`, không inject)
- OCR trên screenshots
- Web scraping public data / API công khai

**❌ Cấm tuyệt đối** (giữ nguyên từ v1 — research xác nhận danh sách này đúng):
- `ReadProcessMemory` trên game process
- DLL injection vào `League of Legends.exe`
- DirectX/Direct3D render hooking
- Gửi input tự động vào game (`SendInput`, `pyautogui`, `PyDirectInput`)

**⚠️ Riot Official API** — **chỉ post-game**. Không tồn tại live TFT state API: Live Client Data API
(`127.0.0.1:2999`) chỉ phục vụ Summoner's Rift; request cho TFT mở từ 2020-09-24 chưa được trả lời.

**⚠️ Đánh đổi cần biết — global hotkey**: thư viện `keyboard` cài hook `WH_KEYBOARD_LL` và cần quyền admin.
Đây đúng là loại hành vi anti-cheat heuristics để ý. Hotkey hoạt động *bên trong* cửa sổ game thì bắt buộc
phải có low-level hook, nên đây là đánh đổi thật, không phải lỗi. Nếu chấp nhận hotkey chỉ hoạt động khi
overlay được focus → dùng `RegisterHotKey` qua Qt, **không cần hook**. Mặc định v2: ưu tiên `RegisterHotKey`.

> ✅ **Đã giải quyết (2026-09-04) — đánh đổi này không còn tồn tại.** `src/utils/hotkeys.py` chứng minh
> `RegisterHotKey(NULL, ...)` + `QAbstractNativeEventFilter` đọc `WM_HOTKEY` hoạt động **kể cả khi game
> đang focus** — vì nó chặn ở tầng OS chứ không phải tầng cửa sổ. Không hook, không cần admin.
>
> Vì thế `keyboard` giờ **bị cấm hoàn toàn** trong `FORBIDDEN_MODULES`, không chỉ cấm các hàm gửi input.
> Trước đây `import keyboard; keyboard.add_hotkey(...)` vẫn qua được test trong khi nó cài
> `WH_KEYBOARD_LL` thật — tức là mục này gọi tên đúng mối nguy nhưng test lại không chặn. Đã bịt:
> `SetWindowsHookEx{,A,W}`, `SetWinEventHook`, `WH_KEYBOARD_LL`, `WH_MOUSE_LL` nằm trong
> `FORBIDDEN_SYMBOLS`, và test quét thêm cả file `.py` ở gốc repo (entry point tương lai).

---

## 2. Kiến Trúc Hệ Thống

### 2.1 Sơ Đồ Tổng Thể

```
┌──────────────────────────────────────────────────────────────────┐
│                       TFT Advisory Agent                          │
├──────────────────────────────────────────────────────────────────┤
│  Nguồn khung hình (src/capture/)        Knowledge (src/knowledge/)│
│  ▸ VideoFrameSource — bản record ✅      CDragon · bảng tier ·    │
│  ▸ chụp WGC theo cửa sổ — CHỈ ở tools/   augment_features.json ·  │
│    probe, chưa thành FrameSource ⏳       name_index · meta comps  │
│                 │ Frame                                           │
│  ┌──────────────▼─────────────────────────────────────────────┐  │
│  │  LiveSession (src/live/) — LÕI DÙNG CHUNG, không Qt         │  │
│  │  ▸ RerollButtonReader → screen_present: có màn chọn lõi?    │  │
│  │  ▸ ngoài màn: HudReader → GameStateTracker;                 │  │
│  │               HeldAugmentTracker (dải icon lõi đã chọn)     │  │
│  │  ▸ trong màn: AugmentScreenTracker → CardReader             │  │
│  │               (Ocr / Gemini / Hybrid) → AugmentChoice       │  │
│  └──────────────┬─────────────────────────────────────────────┘  │
│  ┌──────────────▼─────────────────────────────────────────────┐  │
│  │  Advisor (src/decision/advisor.py) → AdviceBundle           │  │
│  │  ▸ AugmentAdvisor.rank()          — 5 thành phần (§3.5.4)   │  │
│  │  ▸ AugmentAdvisor.rank_by_plan()  — theo hướng (§3.5.6)     │  │
│  │  ▸ reroll_policy (§3.5.5) · Comp · Economy · Item · Position│  │
│  │  ▸ LLM Reasoner — TÙY CHỌN, sau hard timeout                │  │
│  └──────┬───────────────────────────────────────┬─────────────┘  │
│         │ LiveEvent: Idle/Status/AdviceReady/Cleared             │
│  ┌──────▼───────────────────────────┐  ┌────────▼─────────────┐  │
│  │ Vỏ replay ✅ run_replay.py +      │  │ ScenarioLogger (§12) │  │
│  │   src/replay/ (panel + overlay   │  │ schema 3 →           │  │
│  │   vẽ trên video)                 │  │ data/scenarios/      │  │
│  │ Panel trong trận ⏳ augment_panel │  └──────────────────────┘  │
│  │   (chỉ qua scripts/demo_overlay) │                            │
│  │ Vỏ live trong ván thật ❌ chưa có │                            │
│  └──────────────────────────────────┘                            │
└──────────────────────────────────────────────────────────────────┘

        ┌──────────────── OFFLINE, chạy 1 lần mỗi patch ──────────────┐
        │ scripts/build_augment_features.py                            │
        │   258 lõi: tất định → Gemini sửa 4 trường → duyệt tay        │
        │   ──▶ data/augment_features.json (commit, audit được §3.4.1) │
        └──────────────────────────────────────────────────────────────┘
```

> *(lịch sử)* Sơ đồ v3 có các khối **Preflight**, **Session/Phase Detector**, **Template Match**,
> **Board/Shop Reader**, **Economy Tracker**, **Pool Tracker** và overlay bật
> `WDA_EXCLUDEFROMCAPTURE`. Không khối nào trong số đó tồn tại trong code: việc "có đang ở màn chọn
> lõi không" do bộ đọc nút đổi đảm nhận, chưa có bộ đọc bàn cờ/cửa hàng, và capture protection mặc
> định tắt (§3.6).

### 2.2 Luồng Dữ Liệu

Luồng thực tế trong `LiveSession.step(frame)` (`src/live/session.py`), giống hệt nhau trên bản record
và trong trận — hai vỏ chỉ khác nguồn khung hình và cách hiện:

```
1. Frame (VideoFrameSource khi replay; ~5 lần đọc/giây video, `--analysis-fps`)
             │
             ▼
2. RerollButtonReader (src/vision/reroll_buttons.py) — đọc 3 nút đổi thẻ
      └── `screen_present` = False → nhánh NGOÀI màn chọn lõi:
            ├── HudReader (có cổng "HUD có đổi không") → GameStateTracker
            │     gold / level / xp / xp_needed / hp / stage / streak
            ├── HeldAugmentTracker.observe → lõi vừa chọn → state.augments
            └── trả Idle hoặc Cleared (vừa rời màn)
             │ screen_present = True
             ▼
3. AugmentScreenTracker — chờ thẻ ổn định (`stable_frames`), chỉ đọc lại ô vừa đổi
             │
             ▼
4. CardReader (src/live/card_reader.py) — đọc TỪNG Ô: Ocr / Gemini / Hybrid
      → AugmentChoice(api_names, confidence, slot); không đọc được ô nào → Status
             │
             ▼
5. GameStateTracker.state() + state.augments (HeldAugmentTracker.known)
             │
             ▼
6. Advisor.advise → AdviceBundle
      ├── ranking  = AugmentAdvisor.rank()          (§3.5.4)
      ├── plans    = AugmentAdvisor.rank_by_plan()  (§3.5.6, khi plan_fit.enabled)
      ├── reroll   = advise_reroll()                 (§3.5.5)
      ├── comp / economy / items / position (mỗi cái được phép hỏng riêng)
      └── ScenarioLogger ghi data/scenarios/ (§12.0)
             │
             ▼
7. AdviceReady(state, cards, bundle, rerolls, card_icons, latency_ms) → vỏ hiển thị
```

> *(lịch sử)* Luồng dự kiến của v3, giữ để đối chiếu — bước 0 (Preflight) và bước 2 (Session/Phase
> Detector) chưa từng được viết; Template Matching cho champion/item/trait cũng chưa có:

```
0. Preflight (1 lần khi khởi động)
      ├── Capture 1 frame → assert KHÔNG đen hoàn toàn
      ├── Assert display mode = borderless (từ chối fullscreen-exclusive)
      ├── Assert OS build ≥ Win10 2004 (cho WDA_EXCLUDEFROMCAPTURE)
      └── Assert vi_vn.json Last-Modified còn mới
             │
             ▼
1. Screen Capture (~5 FPS, hoặc trigger theo hotkey/phase)
             │
             ▼
2. Session/Phase Detector — đang ở trận? lobby? carousel? alt-tab?
      └── Nếu KHÔNG in-game → dừng pipeline, không đọc gì cả
             │
             ▼
3. Image Preprocessing (crop ROIs, threshold, denoise)
      ├──▶ OCR → Gold, HP, Level, Stage
      ├──▶ Template Matching → Champions, Items, Traits
      └──▶ Augment Detection (Gemini Vision — xem §9.3)
             │
             ▼
4. Game State Object → State/Economy/Pool Tracker
             │
             ▼
5. Decision Engine
      ├── Màn hình chọn augment? → Augment Scoring Engine (§3.5.4)
      │     └── Score(a|S) cho cả 3 → xếp hạng + lý do từng thành phần
      └── Ngược lại → Comp / Economy / Item / Position advisor
             │
             ├──────────────▶ Overlay (hiển thị xếp hạng + LÝ DO)
             └──────────────▶ ScenarioLogger (ghi ra đĩa, §12)
```

> **Vì sao LÝ DO là bắt buộc, không phải trang trí**: overlay chỉ hiện "chọn cái số 2" là hộp đen,
> không bảo vệ được trước hội đồng. Mỗi thành phần điểm phải trả về kèm một câu giải thích —
> đó cũng chính là thứ mà ablation study (§12.4) mổ xẻ.

> **Lưu ý nhịp độ**: TFT là turn-based, planning phase ~30 s. **Không** cần loop 10 FPS liên tục.
> Prior art dùng poll 200 ms sau một aHash gate, hoặc chỉ chạy khi bấm hotkey.

---

## 3. Module Specifications

### 3.0 Preflight — **chưa có module runtime; phần thăm dò nằm ở `tools/`**

> 🔄 **v4**: `src/utils/preflight.py` **không tồn tại**. Các câu hỏi môi trường dưới đây được trả lời
> một lần bằng công cụ thăm dò chạy tay — `tools/probe_environment.py` (Q1–Q7 của
> [phase-0-spike](docs/live-mode/phase-0-spike.md): WGC có chạy, khung có đen, cửa sổ, OS build…) và
> `tools/probe_quick.py` — ghi kết quả ra `data/live_probe/<timestamp>/` (xem `dev_log.md` §14). Kiểm
> độ mới dữ liệu chạy trong `src/knowledge/data_freshness.py` (Advisor gắn `stale_data`), không phải
> trong preflight. Bảng dưới là thiết kế v2 *(lịch sử)*, giữ làm danh sách việc cho vỏ live.

Mọi giả định của v1 về môi trường đều **chưa được kiểm chứng**. Preflight biến chúng thành runtime check
fail loudly, thay vì để pipeline im lặng trả về rác.

| Check | Fail thì sao |
|---|---|
| Frame capture không phải toàn đen | Riot có thể đã bật capture protection → báo lỗi rõ ràng, thoát |
| Display mode = borderless windowed | Fullscreen-exclusive bypass DWM compositor → overlay không hiện |
| OS build ≥ Win10 2004 (19041) | Dưới mức này `WDA_EXCLUDEFROMCAPTURE` degrade thành `WDA_MONITOR`, **vẽ ô trắng đè lên chính ROI đang đọc** |
| `vi_vn.json` `Last-Modified` còn mới | Bẫy `vn_vn.json` (đóng băng 2023-05-03) trả HTTP 200 im lặng |
| `mDefaultSet` == set đang target | Chặn việc chạy nhầm data set khác |

### 3.1 Screen Capture Module (`src/capture/`)

| File | Mô tả |
|---|---|
| `frame_source.py` | Hợp đồng giữa capture và vision: `Frame` (ảnh numpy BGR, `t`, `ref`) + Protocol `FrameSource`. Mọi nguồn khung hình đều trả về `Frame` |
| `video_source.py` | `VideoFrameSource` — đọc file video qua ffmpeg. **Nguồn duy nhất đang dùng** (replay, eval, gán nhãn) |
| `regions.py` | `ScreenRegions` — đọc `config/screen_regions.yaml`; ROI lưu **tỉ lệ 0..1**, mỗi vùng có **điểm neo** `stretch` / `left` / `center` / `right` để chạy đúng trên khung khác 16:9 (đo trên record 16:10, 1728×1080) |

> 🔄 **v4**: `screen_capture.py` và `region_detector.py` **không tồn tại**. Chụp WGC theo cửa sổ mới
> chạy trong `tools/probe_environment.py` (~49,9 fps, không hộp thoại, `dev_log.md` §14), **chưa**
> được bọc thành một `FrameSource` trong `src/capture/`. Phần dưới đây là quyết định thiết kế cho vỏ
> live, vẫn còn hiệu lực.

> 🔄 **Đổi quyết định (2026-09-04) — chụp THEO CỬA SỔ, không chụp desktop.** Cờ
> `capture.window_scoped` trong `settings.yaml`. Hai lý do độc lập cùng chỉ về một hướng:
>
> 1. **Đã có sẵn từ research trước:** [`research/overview.md`](research/overview.md) đã ghi `dxcam` là
>    *desktop*-scoped và đề xuất `windows-capture` 2.0.1 (WGC, window-scoped, non-hooking).
> 2. **Mới từ đánh giá rủi ro:** chụp theo cửa sổ không lấy overlay của tiến trình khác → vòng lặp
>    tự chụp không hình thành, nên §3.6 không cần `WDA_EXCLUDEFROMCAPTURE` nữa. Đồng thời tránh
>    `NtGdiDdDDIOutputDuplGetFrameInfo` — syscall của Desktop Duplication mà `vgk.sys` có hook.
>    Không có bằng chứng hook đó dùng để phát hiện; cũng không có lý do phải đi qua nó.
>
> ROI của OCR **phải không giao** với vùng overlay. `tools/calibrate.py` sẽ assert điều này
> (`capture.assert_roi_disjoint_from_overlay`) — lớp phòng thủ thứ hai nếu có lúc phải rơi về
> desktop capture. Chi tiết: [`research/vanguard/capture-design.md`](research/vanguard/capture-design.md).

**Yêu cầu kỹ thuật:**
- Game phải chạy **Borderless Windowed** (Fullscreen exclusive → không overlay được)
- Capture rate: ~5 FPS hoặc theo trigger — throughput **không** phải bottleneck, OCR mới là
- Output: numpy array (BGR/BGRA)
- Định vị bằng `GetClientRect` + `ClientToScreen`, **không** dùng `GetWindowRect`

**Ứng viên đáng đánh giá**: `windows-capture>=2.0.1` (WGC) capture theo **window** thay vì desktop — nếu
dùng được thì bài toán overlay tự chụp chính mình biến mất hoàn toàn.

**ROI (Region of Interest)** — toạ độ chuẩn 1920×1080 *(lịch sử — ROI thật ở `config/screen_regions.yaml`, dạng tỉ lệ, xem `src/capture/regions.py`)*:

> ⚠️ **TẤT CẢ toạ độ dưới đây là tạm thời và thuộc thời Set 17 (Hextech engine).**
> Chúng **không sống sót** qua 2026-08-26. Không hardcode — sinh ra bằng `tools/calibrate.py` (§5).

| Vùng | Toạ độ (left, top, right, bottom) | Mô tả |
|---|---|---|
| Gold | (870, 882, 920, 902) | Số gold hiện tại |
| Level | (30, 880, 60, 900) | Level player |
| HP | *chưa đo* | Health bar player |
| Shop | (480, 920, 1440, 1080) | 5 champion cards |
| Board | (340, 340, 1580, 770) | Bàn cờ hex grid |
| Bench | (420, 775, 1500, 870) | Bench (9 slots) |
| Items | *chưa đo* | Item components |
| Stage | (760, 5, 850, 25) | Stage indicator |
| Traits | (0, 200, 130, 700) | Active traits panel |
| Augments | (400, 250, 1520, 650) | Augment selection popup |

### 3.2 Vision Module (`src/vision/`)

| File | Mô tả |
|---|---|
| `ocr_engine.py` | **RapidOCR** (PP-OCRv6). Đọc chữ số tốt; **không** sinh được phần lớn ký tự tiếng Việt chồng dấu (`dev_log.md` §10) |
| `preprocess.py` | Tiền xử lý trước OCR (Otsu cho ô số nhỏ, vd `stage`) + đọc đầu ra OCR an toàn |
| `hud_reader.py` | Đọc HUD: `stage`, `gold`, `level`, `xp` (kèm `xp_needed` từ cùng thanh XP), `hp`, `streak`. Có cổng "thanh HUD có hiện không"; sai khoảng giá trị thì trả `None` kèm lý do, **không** clamp |
| `player_row.py` | Tìm dòng của người chơi trong bảng 8 người (vòng tròn vàng quanh avatar) để đọc máu đúng người |
| `reroll_buttons.py` | `RerollButtonReader` — trạng thái 3 nút đổi thẻ → `RerollState`; thuộc tính `screen_present` là **bộ phát hiện màn chọn lõi** của cả hệ thống |
| `augment_reader.py` | `AugmentReader` — đọc thẻ bằng Gemini Vision (cache aHash), trả `CardRead`. Được bọc bởi `GeminiCardReader` |
| `held_augments.py` | Đọc **lõi đã chọn** từ dải icon ~37 px ở hướng 10 giờ (x≈511, y≈245 ở 1080p): `find_strip` đếm icon, `classify` so icon mới nhất **chỉ với các lõi vừa chào** (mẫu cắt từ chính thẻ, icon CDragon ở `data/augment_icons/` là dự phòng). `HeldAugmentTracker` → `state.augments`; không chắc thì ghi `None`, không đoán |
| `frame_reader.py` | Bộ đọc hợp nhất HUD + thẻ + nút đổi cho script/eval; một chân hỏng chỉ ghi vào `degraded` |

Bộ đọc **tên thẻ** dùng trong vòng lặp nằm ở `src/live/card_reader.py` (cùng một giao diện `read_slot`):

| Lớp | Cách đọc |
|---|---|
| `OcrCardReader` (`ocr`) | OCR → chuẩn hoá (bỏ dấu) → khớp `data/name_index.json`: chính xác → theo gốc → **gần đúng** `difflib` với ngưỡng chặt `FUZZY_CUTOFF = 0.82`. Chạy cục bộ, không mạng |
| `GeminiCardReader` (`gemini`) | Bọc `AugmentReader` (Gemini Vision) |
| `HybridCardReader` (`hybrid`) | OCR trước; chỉ gọi Gemini khi OCR không ra đúng **một** apiName; Gemini lỗi thì giữ kết quả OCR |

Mặc định: `run_replay.py --card-reader` = **`hybrid`**; `src/replay/window.build_session(card_reader=…)` = **`ocr`**.

> 🔄 **v4**: `template_matcher.py`, `board_reader.py`, `shop_reader.py` **không tồn tại** — hệ thống
> chưa đọc champion, item, bàn cờ hay cửa hàng. Trong `LiveSession`, `state.board` / `bench` / `shop` /
> `item_components` vì thế luôn rỗng; `active_traits` lấy từ `CardReader.read_traits` (bảng tộc).

**Quy tắc matching bắt buộc** (chi tiết: [`research/vision-stack/ocr.md`](research/vision-stack/ocr.md)):

| Rule | Chi tiết |
|---|---|
| Normalize cả 2 phía | NFD + bỏ Mn + `đ→d`, lowercase, **trước** mọi so sánh |
| Tách tier token trước | Bỏ hậu tố `I`/`II`/`III`/`+`/`++`, fuzzy match phần **gốc** |
| Tier tra từ `apiName`/`name` | ⚠️ **ĐẢO so với v2**: icon art dùng lại giữa các tier — **19/254** icon path mâu thuẫn với tên augment. Icon chỉ là fallback. Regex phải bắt cả `_` lẫn `-`: `[-_](i{1,3})\.tex$`. Ladder đầy đủ: [augments](research/vision-stack/augments.md) |
| Chấp nhận nhập nhằng | **5 cặp augment trùng tên** (sau chuẩn hoá, trên 258 lõi — `data/name_index.json` `meta.ambiguous_group_counts`, cả EN lẫn VI) — tên không tách được. Hiển thị cả hai, gắn nhãn, **không đoán** |
| Giới hạn charset | Chỉ nhận ký tự xuất hiện trong tên của set hiện tại |

> ⚠️ **Không copy threshold của prior art.** `jfd02` dùng `SequenceMatcher >= 0.85` cho item. Áp lên
> augment thì **97% cặp ≥0.85 là cùng một augment khác tier** — đúng thứ cần phân biệt nhất.

**Challenges & Solutions:**
| Challenge | Solution |
|---|---|
| Resolution dependency | Normalize ROI theo tỉ lệ client rect, không hardcode pixel |
| Animation/VFX obstructions | Multi-frame sampling (3-5 frames), majority vote |
| Champion skins khác icon | Match bằng border color (cost-tier) + icon shape |
| Dark/bright scene variations | Adaptive thresholding |
| OCR misread | Allowlist characters, validation rules (gold < 999, level 1-10) |
| Số nhỏ cố định (gold/level/stage) | Cân nhắc per-digit template thay vì full OCR — nhanh và chính xác hơn |

### 3.3 Game State Module (`src/game_state/`)

| File | Mô tả |
|---|---|
| `models.py` | Data classes cho game entities (`GameState`, `Champion`, `OpponentBoard`, `GameEvent`) |
| `state_tracker.py` | `GameStateTracker` — gộp các lần đọc HUD qua thời gian, giữ giá trị tốt gần nhất (`stale` / `never_seen`), xuất `GameState` |

> 🔄 **v4**: `session_detector.py`, `economy.py`, `pool_tracker.py` **không tồn tại**. Câu hỏi "có
> đang ở màn chọn lõi không" do `RerollButtonReader.screen_present` trả lời (§3.2); còn phân biệt
> lobby / carousel / alt-tab thì chưa có module nào làm. Hai trường `round_phase` và `session_state`
> vẫn nằm trong `GameState` nhưng **không được gán khi chạy** — luôn là giá trị mặc định
> (`"planning"`, `"in_game"`). Lõi đã chọn (`augments`) do `HeldAugmentTracker` điền (§3.2).
>
> *(lịch sử)* Lý do v2 đặt `session_detector` là bắt buộc — "mọi reader đều ngầm giả định có board
> sống" — vẫn đúng; trong code nó được giải bằng cổng `screen_present` và cổng "thanh HUD có hiện".

**Core Data Models:**
```python
@dataclass
class Champion:
    name: str
    cost: int                        # 1-5
    star_level: int                  # 1, 2, 3
    items: list[str]                 # max 3 items
    position: tuple[int, int] | None # hex (row, col) or None if bench
    traits: list[str]
    role: str | None = None          # ADCarry, APCaster, APTank... (từ CDragon khi Riot cập nhật Set 18)

@dataclass
class GameState:
    gold: int
    level: int
    hp: int
    xp: int
    xp_needed: int | None            # mẫu số thanh XP ("12/56" → 56); None = chưa đọc được
    stage: str                       # e.g. "3-2"
    streak: int

    board: list[Champion]
    bench: list[Champion]
    shop: list[Champion | None]

    item_components: list[str]
    completed_items: list[str]
    active_traits: dict[str, int]
    augments: list[str]              # lõi đã chọn — HeldAugmentTracker (dải icon)

    timestamp: float
    round_phase: str                 # mặc định "planning" — chưa được gán khi chạy
    session_state: str               # mặc định "in_game" — chưa được gán khi chạy

    # Phase 7, feature-flag `enable_scouting` — MẶC ĐỊNH TẮT
    opponents: list["OpponentBoard"] = field(default_factory=list)

@dataclass
class OpponentBoard:
    slot: int                        # 1-7
    units: list[str]                 # champion names đọc từ scoreboard/tab
    level: int | None
    hp: int | None
    confidence: float                # đọc đối thủ nhiễu hơn đọc board mình — luôn kèm confidence
```

> 🔄 **Quay lại ở v3**: `opponents` từng bị bỏ ở v2 vì Riot liệt kê scouting vào danh sách không được
> duyệt. Đồ án không phát hành nên ràng buộc đó không áp dụng (§11). Nó cho phép tính `contest_score` —
> bao nhiêu người đang tranh comp của mình — một yếu tố quyết định thật trong TFT.
>
> ⚠️ **Nhưng để ở Phase 7 và mặc định tắt**: đọc board 7 người khác qua scoreboard là khối lượng CV
> đáng kể và độ nhiễu cao. Làm sớm sẽ nuốt mất thời gian của Augment Advisor — thứ mới là trọng tâm
> đồ án. Mọi code đọc `state.opponents` phải chịu được list rỗng.

**State Tracker Events:**
```python
class GameEvent(Enum):
    ROUND_START = "round_start";        ROUND_END = "round_end"
    SHOP_REFRESH = "shop_refresh";      CHAMPION_BOUGHT = "champion_bought"
    CHAMPION_SOLD = "champion_sold";    ITEM_EQUIPPED = "item_equipped"
    LEVEL_UP = "level_up";              AUGMENT_SELECTION = "augment_selection"
    COMBAT_RESULT = "combat_result";    CAROUSEL_ROUND = "carousel_round"
    GAME_START = "game_start";          GAME_END = "game_end"
```

### 3.4 Knowledge Base (`src/knowledge/`)

| File | Mô tả |
|---|---|
| `cdragon_client.py` | CommunityDragon — champions/traits/items/locale (`/latest/`) |
| `augment_features.py` | **MỚI v3** — loader cho `data/augment_features.json` (§3.4.1) |
| `stats_provider.py` | **MỚI v3** — interface stats cắm-rút + các implementation (§3.4.2) |
| `comp_database.py` | Comp tier list & database |
| `roll_odds.py` | Roll probability tables (có gate, xem dưới) |
| `riot_api.py` | Riot API client — `tft-match-v1`, **chỉ** dùng cho crawl meta comp offline. Back-fill placement đã bỏ (2026-09-30, xem §12.0) |
| `augment_catalog.py` | Catalog lõi: giải tier, chuẩn hoá tên, đánh dấu cặp mập mờ |
| `name_index.py` | Tên hiển thị (OCR) → `apiName`, đọc `data/name_index.json` |
| `data_freshness.py` · `data_refresh.py` | Dữ liệu còn khớp patch không (→ `AdviceBundle.stale_data`) · logic của `scripts/refresh_data.py` |
| `tftacademy.py` · `metatft.py` | Bảng tier lõi (TFT Academy; MetaTFT dự phòng) |
| `tftacademy_comps.py` · `metatft_comps.py` · `tactics_tools.py` | Đội hình meta + stats unit/trait/item |
| `lolchess_guide.py` | Cơ chế game Set 18 (XP, thu nhập, chuỗi, vòng đấu…) → `data/lolchess_guide.json` |

> 🔄 **v4**: `item_guide.py` **không tồn tại**. Công thức ghép đồ nằm ở `data/item_recipes.json`
> (sinh bởi `scripts/build_game_tables.py` từ CDragon), `Advisor` nạp rồi truyền cho `CompSelector`.

#### 3.4.1 Bảng đặc trưng Augment — **vì sao phải sinh offline**

Đã đo trực tiếp metadata augment Set 18 của CDragon (n = **254**) để xem có chấm điểm bằng rule được không:

| Field | Có dữ liệu | Dùng được? |
|---|---|---|
| `associatedTraits` | **20 / 254** | ❌ Chỉ augment gắn trait mới có |
| `incompatibleTraits`, `composition`, `unique` | **0 / 254** | ❌ Rỗng hoàn toàn |
| `tags` | 254 / 254 | ❌ **Giá trị bị băm** (`{ce1fd21c}`…), chỉ 3 giá trị phân biệt |
| `effects` | 223 / 254 | ⚠️ Nhiều key bị băm; chỉ **47%** placeholder `@Var@` resolve được |
| `desc` | **254 / 254**, cả EN lẫn VI, không băm | ✅ **Tín hiệu đầy đủ duy nhất** |

> **Kết luận: KHÔNG thể xây scorer bằng rule từ field có cấu trúc của CDragon.** Chỉ 40% augment
> resolve đủ số. Đặc trưng phải trích từ **văn bản `desc`**.

> *(lịch sử)* Bảng đo trên là metadata CDragon lúc n = 254 (đầu Set 18). Bảng đặc trưng hiện tại có
> **258** lõi (`meta.n`): 253 lõi của CDragon 18.5b + 5 lõi CDragon đã bỏ nhưng client live vẫn có, giữ
> lại qua `data/augment_overrides.json` (xem `docs/next-steps.md`). Cờ `live` cho biết lõi còn trong game.

**Giải pháp — trích đặc trưng offline, ba tầng, cache lại, audit được:**

```
scripts/build_augment_features.py   (chạy offline khi set/patch đổi, không phải mỗi trận)
  input : 258 × {apiName, name, tier, desc_en}  (CDragon + data/augment_overrides.json)
  output: data/augment_features.json   ← COMMIT vào repo, sửa tay được

  Tầng 1 — TẤT ĐỊNH (mặc định, không cần key): luật trên `desc` → mọi trường
  Tầng 2 — LLM (--llm, Gemini): CHỈ được sửa 4 trường LLM_REFINABLE
           = carry_type, tempo, econ_value, board_condition; ghi `extraction_method = "llm:…"`
  Tầng 3 — DUYỆT TAY (scripts/review_augment_features.py → apply_manual_review.py):
           ghi `extraction_method = "manual-audit:<trường,…> (from <method gốc>)"`;
           build lại (--write / --migrate) GIỮ các dòng duyệt tay
  Hiện tại (meta 2026-11-13): manual-audit 169 · llm 67 · deterministic-v2 22

  mỗi augment →
    api_name, name  : định danh
    tier            : bậc lõi (1/2/3) — xem §9.3
    categories      : 1-3 nhãn ⊂ {econ, combat, trait, item, utility, reroll}, nhãn chính đầu tiên
    category        : = categories[0] (giữ cho chỗ đọc cũ)
    carry_type      : AD | AP | both | none   (carry SÁT THƯƠNG; chống chịu nằm ở frontline)
    frontline       : bool — giá trị chủ yếu là chống chịu (máu, giáp, kháng, khiên, hồi máu)
    trait_affinity  : [trait_id, ...]
    trait_count_reward : vertical | wide | null — thưởng theo SỐ tộc, tách khỏi trait_affinity
    econ_value      : 0-3 (chỉ vàng/XP/reroll; item nằm ở item_grants)
    econ_type       : ⊂ {gold, xp, reroll} — loại tài nguyên lõi kinh tế cho (dùng ở §3.5.6)
    tempo           : immediate | scaling   (xét TẠI LƯỢT lõi được chào; nhiều lượt → lượt muộn nhất)
    offer_rounds    : ⊂ {2-1, 3-2, 4-2} — lượt lõi được chào; rỗng = chưa biết. Nguồn datatft (máy chủ CN), sửa tay được
    item_grants     : [component, ...]
    board_condition : điều kiện board cần có để augment phát huy
    live            : true | false | null — còn trong client live; pool reroll chỉ lấy true
    extraction_method, confidence : xuất xứ của dòng (tầng nào ghi) và độ tin
```

| Vì sao thiết kế thế này | |
|---|---|
| **LLM không nằm trên critical path** | Runtime chỉ đọc JSON — deterministic, nhanh, không tốn quota |
| **Audit được** | 258 dòng JSON, người đọc và sửa tay được; mỗi dòng ghi tầng nào sinh ra nó. Hội đồng kiểm tra được |
| **Tái sinh mỗi set** | Per-set churn là thứ đã giết mọi TFT overlay open-source. Sinh tự động thì sống |
| **Là đóng góp phương pháp** | Không phải workaround — đây là cách hợp lệ để cấu trúc hoá dữ liệu phi cấu trúc |

#### 3.4.2 Stats Provider — interface cắm-rút

Nguồn số liệu thống kê augment (avg placement / top-4) **sẽ chốt sau**. Vì vậy scoring engine
**không được** phụ thuộc nguồn cụ thể:

```python
class AugmentStatsProvider(Protocol):
    def get(self, api_name: str) -> AugmentStats | None: ...

@dataclass
class AugmentStats:
    avg_place: float; top4_rate: float; win_rate: float
    sample_n: int                    # cỡ mẫu — luôn hiển thị kèm
    source: str                      # provenance — luôn hiển thị kèm
```

| Implementation | Ghi chú |
|---|---|
| `NullProvider` | Không trả số liệu nào. **Cho phép chạy toàn hệ thống trước khi có bất kỳ số liệu nào**. ⚠️ v4: khi provider trả `None`, `Base` **không** trung tính 0,5 mà nhận `tuning.base.unknown_score` = **0,35** (dưới bậc B) — xem §3.5.4 |
| `CsvProvider` | Nạp file CSV tự chuẩn bị — mặc định hiện tại |
| `RiotApiProvider` | ❌ **Bất khả thi cho Set 18** — đo 2026-09-01 với key thật: participant của `tft-match-v1` **không còn trường `augments`**, cả payload không có chuỗi `"augment"` nào. Lớp code vẫn giữ (có test) và sẽ chạy ngay khi Riot trả trường này về. Xem [set-data](research/set-data.md) |
| `OpggMcpProvider` | `https://mcp-api.op.gg/mcp`. Nhanh nhưng là hộp đen — xem [prior-art](research/prior-art.md) |
| `ExpertTierListProvider` | **Nguồn chính của w₁ từ 2026-09-07.** Bảng S/A/B/C/D do người chơi giỏi xếp → `avg_place` là **mã hoá đơn điệu** của bậc. `sample_n` luôn 0, `is_ordinal` luôn True, nên `is_evidence` **luôn False** |
| `CompositeProvider` | Gộp nhiều nguồn theo thứ tự ưu tiên, **giữ nguyên provenance** |

> **Thêm nguồn mới = thêm 1 file, KHÔNG sửa scoring engine.** Mọi số hiển thị trên overlay phải kèm
> `source` và `sample_n` — không có cỡ mẫu thì không phải bằng chứng.

**Chuyển hướng 2026-09-07 — w₁ đứng trên tiên nghiệm chuyên gia**

Không còn nguồn **đo được** nào ở bất kỳ mức rank nào (Riot gỡ trường; `d3.tft.tools` trả
`{"singles": []}` trên mọi patch Set 18; datatft hardcode trong JS; tftacademy Disallow). Vì vậy
w₁ chuyển sang bảng tier do người xếp, với `ordinal_trust: 0.65` thay cho co ngót theo cỡ mẫu.

Phát biểu đúng là *"không còn nguồn đo được nên dùng tiên nghiệm thứ tự có ký tên, kèm hệ số co
ngót tường minh"* — **không phải** *"bảng tier tốt hơn placement thô"*. Cách chuẩn xử lý nhiễu kỹ
năng (kiểu `Cruel Pact`) là **lọc theo nhóm rank**, không phải bỏ phép đo; đường đó đóng vì thiếu
dữ liệu, chứ không phải vì nó sai.

> ⚠️ `default_provider(..., allow_fabricated=False)` là **mặc định**. Bộ số giả lập bịa `sample_n`
> trên 200 nên `is_evidence` trả True cho nó, và vì nó phủ đủ 254 augment nên nó **che hết** bảng
> tier — thả một bảng tier thật vào repo cũng không đổi được gì mà không có gì báo. Xem
> [docs/expert-prior/](docs/expert-prior/overview.md).

**⚠️ Roll Odds / Pool Size — CHƯA XÁC MINH CHO SET 18**

Bảng dưới đây là chuẩn của các set **trước**. Scan PBE `map22.bin.json` (72.6 MB) cho Set 18:
`ShopOdds` / `TierOdds` / `ChampionTierOdds` / `LevelXP` = **0 hit**.

```
Level │ 1-cost │ 2-cost │ 3-cost │ 4-cost │ 5-cost
──────┼────────┼────────┼────────┼────────┼───────
  1-2 │  100%  │   0%   │   0%   │   0%   │   0%
  3   │   75%  │  25%   │   0%   │   0%   │   0%
  4   │   55%  │  30%   │  15%   │   0%   │   0%
  5   │   45%  │  33%   │  20%   │   2%   │   0%
  6   │   30%  │  40%   │  25%   │   5%   │   0%
  7   │   19%  │  30%   │  35%   │  15%   │   1%
  8   │   18%  │  25%   │  32%   │  22%   │   3%
  9   │   10%  │  20%   │  25%   │  30%   │  15%
 10   │    5%  │  10%   │  20%   │  30%   │  35%
```

> **Bắt buộc**: Economy Advisor phải **gate** sau khi verify số 18.1, hoặc hiển thị nhãn "chưa xác minh".
> Không ship số cứng. Pool size cũng vậy — hằng số duy nhất tìm được trong PBE là
> `Common_TierBagSizes_For_CharacterWizard` = 29/22/18/11/10, một default của dev tool, **mâu thuẫn** với
> bảng cộng đồng đang lan truyền (29/22/16/12/10).

**Meta Data Schema:** giữ nguyên `MetaComp` từ v1 (name, tier, avg_placement, win_rate, top4_rate,
play_rate, core_units, flex_units, core_items, best_augments, level_timing, early_game, positioning_notes).

### 3.5 Decision Engine (`src/decision/`)

| File | Mô tả | Ưu tiên v3 |
|---|---|---|
| `augment_advisor.py` | **Xếp hạng đầy đủ theo board state + lý do** (§3.5.4) | **1 — trọng tâm đồ án** |
| `scoring/plan_fit.py` | **v4** — `PlanFitScorer`: độ hợp của lõi với MỘT hướng đi (§3.5.6). Không nằm trong `AugmentAdvisor.scorers` | 1 |
| `reroll_policy.py` | Đổi hay chốt, đổi ô nào (§3.5.5) | 1 |
| `margin.py` · `state_effect.py` | Vì sao #1 hơn #2 (hiện trên panel) · đo trạng thái trận có đổi được xếp hạng không | — |
| `comp_selector.py` · `comp_signals.py` | Comp selection algorithm (§3.5.2). ⚠️ v4: **`BoardFit` không đọc `CompSelector`** — `BoardFit` chỉ nhìn `state.active_traits` và carry suy từ item; `CompSelector` chỉ cấp `AdviceBundle.comp` | **2** |
| `rules_engine.py` | Economy, leveling, rolling | 3 |
| `item_advisor.py` | Item crafting recommendations | 4 |
| `position_advisor.py` | Unit positioning | 5 |
| `contest_analyzer.py` | `contest_score` từ `state.opponents` — Phase 7, feature-flag | 6 |
| `llm_reasoner.py` | **Tùy chọn** — tinh chỉnh câu giải thích, sau hard timeout | — |
| `advisor.py` | Orchestrator — tổng hợp rồi đẩy sang Overlay **và** ScenarioLogger | — |

> 🔄 **Đảo ngược so với v2.** v2 xếp Augment Advisor cuối cùng và giới hạn ở "stats tĩnh, không xếp
> hạng" vì §11. v3 đưa nó lên số 1 với đầy đủ khả năng xếp hạng — đây chính là phần thuật toán
> Decision-Making mà đồ án cần thể hiện.
>
> ❌ **Xoá `src/compliance/gate.py`** — thay bằng `tests/test_readonly_invariant.py` (§11).

#### 3.5.1 Rules Engine — Economy

```
Stage 1 (1-1 → 1-4):   Mua units strong board · Không roll/level · Ưu tiên pairs
Stage 2 (2-1 → 2-7):   Econ tới 50 gold · Chỉ mua nếu free upgrade hoặc 2-star · Level 5 tại 2-5
Stage 3 (3-1 → 3-7):   Giữ 50 gold · Level 6 tại 3-2 (hoặc 3-5 nếu save) · Xác định comp direction
Stage 4 (4-1 → 4-7):   Level 7 tại 4-1/4-2 · Slow Roll 7 (cần 3-cost 3★) vs Fast 8 (cần 4/5-cost carry)
                       · Roll down nếu HP < 50
Stage 5+ (5-1 →):      Level 8/9 · All-in roll nếu HP < 30 · Tìm 5-cost

INTEREST: 10/20/30/40/50 gold → +1/2/3/4/5 mỗi round
STREAK (win hoặc loss): 2/3/4+ → +1/2/3 gold mỗi round
```

> ⚠️ Các mốc trên là chuẩn TFT nhiều set. Verify lại với patch 18.1 trước khi tin tuyệt đối.

#### 3.5.2 Comp Selection Algorithm

```
INPUT:  GameState (board + bench + items + augments)
OUTPUT: top 3 comp directions

1. MATCH SCORING — với mỗi MetaComp:
     unit_score  = |player_units ∩ comp.core_units| / |comp.core_units|
     item_score  = item_compatibility(player_items, comp.core_items)
     meta_score  = normalize(comp.top4_rate)
     augment_score = augment_synergy(player_augments, comp.best_augments)

     total = unit_score*0.40 + item_score*0.25 + meta_score*0.23 + augment_score*0.12

     🔄 contest_score QUAY LẠI ở v3 — nhưng chỉ khi enable_scouting = true (Phase 7).
        contest_score = -(số đối thủ đang dùng >=2 core_units của comp này) / 7
        Khi scouting tắt → contest_score = 0, các trọng số trên giữ nguyên.
        Trọng số thật nằm ở config/scoring_weights.yaml, KHÔNG hardcode.

2. DIRECTION STABILITY
     - Trùng recommendation trước với score > 0.6  → +0.15 (tránh pivot vô cớ)
     - Pivot phải bán > 3 units                    → −0.10

3. OUTPUT — sort theo score, trả top 3 kèm transition guide.
   Flag pivot nếu comp hiện tại < 0.3
```

> 🔄 **Trọng số theo kiểu đội hình × giai đoạn** (`comp_selector.adaptive: true`, `src/decision/comp_signals.py`).
> Trọng số cố định ở trên sai với cách người chơi hạng cao chốt bài: fast 8/9 cố tình giữ board tạm
> tới lúc xoay bài, nên tỉ lệ tướng lõi = 0 ở stage 3 là **đúng kế hoạch**. Bộ cố định được giữ làm
> dòng đối chứng cho ablation, và làm fallback cho comp không có nhãn kiểu đội hình.
>
> | Kiểu (nhãn TFT Academy) | Trước xoay bài | Sau xoay bài |
> |---|---|---|
> | `reroll` (carry 1–3 vàng) | tướng lõi là tín hiệu thật: `unit` 0.40 | như trước |
> | `fast8` / `fast9` | `unit` = 0; hướng nằm ở **loại đồ** (0.40) + **ấn** (0.15) | `unit` 0.35 |
>
> - **Đã xoay** = lên cấp mục tiêu, hoặc tới hạn chót (fast8 `4-5`, fast9 `5-1`). Tiền (lên cấp + mua
>   tướng; **không** tính tiền roll) chỉ để hiển thị thời điểm, **không** đổi xếp hạng — đã thử nội suy
>   theo tiền và xếp hạng bị ngược (comp càng thiếu tiền càng ít bị trừ vì thiếu tướng).
> - **Loại đồ** suy từ công thức ghép CDragon (`data/item_recipes.json`), không đoán theo tên. Đồ tank
>   **không** chỉ hướng. Ấn tính khi trait nằm trong comp, mạnh yếu theo top4 của tactics.tools.
> - Fast 8/9 **không** bị phạt khi đổi hướng phải bán board.
> - Đầu ra thêm **mức chốt bài**: *chưa nên chốt / nghiêng về / chốt*, dựa trên bằng chứng từ board
>   (không tính meta) và khoảng cách điểm giữa hướng #1 và #2.
> - Kiểu đội hình **chỉ** lấy từ nhãn nguồn. Suy từ giá tướng đã đo trên 51 comp có nhãn: đúng 26,
>   **sai 7**, không kết luận 18. Board reroll vẫn có 2–4 tướng 4–5 vàng để tròn form.
>
> Mọi con số là **giả định tiên nghiệm** từ kinh nghiệm người chơi, chưa fit trên dữ liệu.

#### 3.5.3 LLM Reasoner — hai vai trò, cả hai đều NGOÀI critical path

| Vai trò | Khi nào chạy | Vì sao an toàn |
|---|---|---|
| **A. Trích đặc trưng augment** (§3.4.1) | **Offline**, 1 lần mỗi set | Kết quả cache vào `augment_features.json`. Runtime không gọi LLM |
| **B. Tinh chỉnh câu giải thích** | Runtime, **tùy chọn**, sau hard timeout | Rules engine đã trả lời xong rồi; LLM chỉ làm câu chữ mượt hơn |

```python
# Vai trò A — offline, chạy bởi scripts/build_augment_features.py
EXTRACT_PROMPT = """
Cho mô tả một Augment trong Teamfight Tactics, trả về JSON PHẲNG:
{carry_type, econ_value, tempo, board_condition}   # category/categories/frontline: tất định, LLM không ghi

Chỉ dựa vào mô tả được cung cấp. Không suy đoán chỉ số không có trong text.
Nếu không xác định được một trường, trả về null — KHÔNG bịa.
"""

# Vai trò B — runtime, tùy chọn
REFINE_PROMPT = """
Bạn là người chơi TFT trình độ Challenger. Dưới đây là xếp hạng augment đã được
tính bằng thuật toán, kèm điểm từng thành phần. Viết lại phần lý do cho tự nhiên,
NGẮN GỌN (1 câu mỗi augment). KHÔNG được đổi thứ tự xếp hạng.
"""
```

> **Ràng buộc kiến trúc (giữ nguyên từ v2)**: LLM **không bao giờ** nằm trên critical path của một
> quyết định có hạn giờ. Augment chỉ có ~30 s để chọn. Scoring engine trả lời tức thì bằng số học đóng;
> LLM đến sau như refinement, sau hard timeout, và **không được phép đổi thứ hạng**.
>
> Vì sao vai trò B bị cấm đổi thứ hạng: nếu LLM đổi được kết quả thì ablation study (§12.4) mất ý
> nghĩa — không còn biết điểm số nào thực sự tạo ra khuyến nghị.

#### 3.5.4 Augment Scoring Engine — **lõi thuật toán của đồ án**

```
Score(a | S) = w₁·Base(a)        stats tĩnh, từ StatsProvider (§3.4.2)
             + w₂·BoardFit(a,S)  trùng trait / khớp carry type
             + w₃·EconFit(a,S)   giá trị econ × độ hợp stage
             + w₄·ItemFit(a,S)   component được tặng vs item đang thiếu
             + w₅·TempoFit(a,S)  greed theo HP (HP thấp → ưu tiên sức mạnh tức thì)
```

| Thành phần | Nguồn dữ liệu | Trả về |
|---|---|---|
| `Base` | `StatsProvider.get(api_name)` | Điểm chuẩn hoá + `source` + `sample_n`. Không có stats (lõi không có trong bảng tier) → **`unknown_score` = 0,35**, *không* phải trung tính 0,5: dưới bậc B (0,37) để phạt rủi ro thiếu thông tin và tạo động cơ đổi thẻ (`tuning.base.unknown_score`) |
| `BoardFit` | `augment_features.trait_affinity` ∩ `state.active_traits`; `carry_type` suy từ item (fallback: `Champion.role`) vs carry hiện tại | Điểm + *"khớp 2/3 unit Thần Rừng đang có"* |
| `EconFit` | `augment_features.econ_value` × hệ số theo `state.stage` | Điểm + *"augment econ ở 2-1 còn kịp sinh lời"* |
| `ItemFit` | `augment_features.item_grants` vs `state.item_components` | Điểm + *"cho 1 Kiếm, đang thiếu đúng Kiếm"* |
| `TempoFit` | `augment_features.tempo` × `state.hp` | Điểm + *"HP 22 — cần sức mạnh ngay, không scaling"* |

**Mỗi thành phần BẮT BUỘC trả về `(score: float, reason: str)`.** Đây không phải tính năng phụ:

- Overlay hiển thị *xếp hạng kèm lý do* → là advisor, không phải hộp đen.
- Ablation study (§12.4) tắt từng `wᵢ` → đo đóng góp thật của từng thành phần.
- Khi 2 augment điểm sát nhau, lý do là thứ giúp người chơi tự quyết.

**Xử lý 5 cặp augment không phân biệt được** (5 nhóm trùng tên sau chuẩn hoá trên 258 lõi, cả EN lẫn VI — `data/name_index.json` `meta.ambiguous_group_counts`; xem [augments](research/vision-stack/augments.md)):
khi nhận diện ra một cặp mập mờ → **chấm điểm và hiển thị CẢ HAI, gắn nhãn "không phân biệt được"**,
tuyệt đối không đoán bừa một tier. Đây là giới hạn dữ liệu có thật, phải báo cáo trong đồ án chứ
không giấu đi.

> Trọng số `w₁..w₅` nằm ở `config/scoring_weights.yaml`. **Không hardcode** — ablation study cần
> tắt/bật được từng cái từ file config.

#### 3.5.5 Chính sách reroll augment (`src/decision/reroll_policy.py`)

§3.5.4 trả lời *"thẻ nào tốt nhất trong ba thẻ đang hiện"*. Set 18 cho **mỗi ô một nút đổi riêng**
(đã đối chiếu trên frame VOD thật), nên còn một câu hỏi thứ hai: *đổi hay chốt, và đổi ô nào*.

Đây là bài toán **dừng tối ưu hữu hạn có nhớ** (McCall sequential search — **không** phải secretary
problem, cũng **không** phải Cayley–Moser; cả hai đều là mô hình *không* nhớ lại). Nó sụp xuống còn
một phép so sánh:

```
REROLL  ⟺  g(R) − c > B          g(R) = E[max(R, σ)] trên pool cùng bậc
```

Ba kết quả chứng minh được, đều bị khoá bằng test:

| | Nội dung |
|---|---|
| **T1** | Đổi ô **tệ nhất** trong các ô còn lượt là tối ưu |
| **T2** | `c = 0` và còn ≥2 lượt ⟹ REROLL **trội hơn yếu** PICK — dừng sớm là lỗ EV |
| **T3** | Vế phải giảm đơn điệu theo `B` ⟹ vùng dừng liên thông ⟹ **luật một bước là luật tối ưu** |

**Ràng buộc kiến trúc:**

- `rank()` và `score_one()` **không đổi**. Module này chỉ **cộng thêm**.
- 🔄 **v4 — pool của `F_S`**: `reroll_policy.pool_by_offer_round: true` (mặc định từ 2026-10-06) —
  pool là lõi **cùng bậc VÀ được chào ở lượt hiện tại** (2-1 / 3-2 / 4-2, trường `offer_rounds`), chỉ
  lấy lõi `live: true`. Pool theo lượt nhỏ hơn `min_round_pool` (12) thì lùi về pool cùng bậc.
  `false` = pool "mọi lõi cùng bậc" như trước, giữ làm nhánh đối chứng ablation
  ([offer-round-pool](docs/augment-reroll/offer-round-pool.md)).
- `F_S` là hàm phân bố thực nghiệm **có trọng số tailoring** của cả một bậc, dựng **một lần**
  mỗi màn chọn (đo được: 2,18 ms p95 cho bậc lớn nhất), sau đó mỗi quyết định là `O(log N)`.
  **Không bao giờ chấm cả bảng lõi** — đo lúc bảng có 254 lõi: 12,24 ms p95, vỡ ngân sách §3.5.3.
- Số lượt đổi còn lại **không hiển thị trên màn hình**, nên `RerollState` là tham số truyền vào.
- Mức độ tin cậy của số liệu **KHÔNG chặn hành động**: `B` và `F_S` cùng sinh từ một hàm điểm nên
  phép so sánh bất biến qua mọi hiệu chỉnh đơn điệu. Trường `evidence` hạ giọng *câu chữ*, không
  hạ *hành động*.

> Tham số nằm ở khối `reroll_policy:` trong `config/scoring_weights.yaml`, cùng lý do với `w₁..w₅`.
> Phân tích đầy đủ + trạng thái kiểm chứng cơ chế: [docs/augment-reroll/](docs/augment-reroll/overview.md).

#### 3.5.6 Gợi ý theo hướng (`src/decision/scoring/plan_fit.py`) — **MỚI v4**

Đóng góp #3 (directional augment). Hệ thống **không đoán** người chơi đi hướng nào — chưa có bộ đọc
bàn cờ, và ở 4-2 fast8 với fast9 trông giống hệt nhau trên HUD. Thay vào đó, **từ 2-1**, mỗi màn chọn
lõi được chấm **một lần cho mỗi hướng**, và người chơi tự chọn dòng của mình.

```
Score(a | φ) = Score(a | S) + w · (plan_fit(a, φ) − 0,5)        w = tuning.plan_fit.weight = 0,15
```

`Score(a | S)` là tổng của `rank()` (§3.5.4). Cộng **độ lệch khỏi trung tính** thay vì thêm một trọng
số mới: hướng không có ý kiến (0,5) thì thứ tự y như `rank()`.

| Thành phần | Nội dung |
|---|---|
| Hướng (`config/scoring_weights.yaml` → `tuning.plan_fit.plans`) | `fast9` "Muốn lên 9" · `fast8` "Mạnh ngay, chơi ở 8" (gồm route `standard`) · `reroll` (reroll1/2/3) · `cash` "Thiếu tiền lên cấp". Mỗi hướng có `eco`, `power`, `econ_type` (gold/xp/reroll), tuỳ chọn `min_hp`, `by_stage`. Thêm hướng = thêm một khối config, không sửa code |
| Loại lõi | eco = `econ_value > 0` hoặc có nhãn `econ`/`reroll`; power = có `combat`/`item`/`trait`. Loại lõi **trực giao** với hướng |
| `plan_fit` | 0,5 + `eco` × sức mạnh (`max(econ_value,1)/3`) + tổng `econ_type` của hướng × sức mạnh + `power` + phần cân bằng, kẹp [0, 1] |
| Cân bằng **hai chiều** theo lõi đã cầm (`state.augments`) | `debt` = số lõi chỉ-eco − số lõi chỉ-combat đã cầm. Lệch eco → lõi chỉ-combat được + `debt_bonus` × lệch; lệch combat → lõi chỉ-eco được cộng tương tự (`debt_bonus` = 0,05) |
| `by_stage` | Một hướng đổi trọng số từ một stage. `reroll` từ stage 4: eco −0,10, power +0,20 (bài reroll đã roll xong) |
| Cảnh báo máu | `hp < min_hp` (fast9: 40) → dòng kèm cảnh báo, **không đổi điểm** |
| Gộp dòng | Các hướng ra cùng một lõi gộp thành một `PlanLine` ("Muốn lên 9 / Thiếu tiền lên cấp → …") |
| Bật/tắt | `tuning.plan_fit.enabled: true` (từ 2026-11-14). `Advisor.advise` gọi `rank_by_plan()` qua `_safe` → `AdviceBundle.plans` (`PlanAdvice`); hỏng thì bảng xếp hạng vẫn hiện |

**Ràng buộc kiến trúc:** `PlanFitScorer` **không** nằm trong `AugmentAdvisor.scorers` và **không**
nằm trong `weights`. `rank()` và `score_one()` không đổi một byte — đó chính là dòng đối chứng
(tắt) của phép đo. Mọi số trong `tuning.plan_fit` là **giả định tiên nghiệm** từ luật của người chơi,
chưa fit trên dữ liệu.

> Kết quả trên dev (5 ván, 15 màn, **số trong mẫu**, chỉ để chỉnh): top-1 khớp lựa chọn người chơi,
> tắt 6/15 → bật 9/15 (`scripts/eval_plan_advice.py`). Số báo cáo lấy từ held-out (video 18.6).
> Thiết kế: [plan-conditioned-advice](docs/directional-augment/plan-conditioned-advice.md) ·
> kế hoạch: [implementation-plan](docs/directional-augment/implementation-plan.md) · nhật ký:
> [`dev_log.md`](dev_log.md) §16–§18. Còn mở: bảng combo lõi (việc B).

### 3.6 Overlay UI (`src/overlay/`)

| File | Mô tả |
|---|---|
| `overlay_window.py` | **2 cửa sổ**: một click-through, một nhận click (`create_windows(capture_protection=False)`) |
| `widgets/augment_panel.py` | Panel trong trận: xếp hạng lõi **kèm lý do** + khuyến nghị đổi thẻ + **các dòng theo hướng** (`build_plan_rows`, viên màu theo hướng, cảnh báo máu). Nền kính tối, cùng bảng màu `arena` với replay. `build_rows()` tách khỏi Qt để test |
| `styles.py` | UI theme & styling |

> 🔄 **v4**: `widgets/advice_panel.py`, `comp_tracker.py`, `econ_widget.py`, `item_widget.py`
> **không tồn tại**; `augment_panel.py` là widget duy nhất. Panel này **mới chạy qua
> `scripts/demo_overlay.py`** (các tình huống dựng sẵn, phím `1`/`2`/`3`/`Esc`), **chưa** được nối vào
> một vòng lặp đọc game thật — vỏ live trong ván thật chưa có (§2.1).

**Vỏ replay (`run_replay.py` + `src/replay/`) — vỏ duy nhất đang chạy trên dữ liệu thật**

`python run_replay.py --video <file> [--card-reader ocr|gemini|hybrid] [--palette arena] [--patch auto]`.
Phát lại bản record, chạy **cùng `LiveSession`** với vỏ live tương lai (`build_session`), nên hành vi
trên record bằng hành vi trong trận. Chỉ đọc file video — không chạy cùng game.

| File | Vai trò |
|---|---|
| `window.py` | `ReplayWindow` + `build_session()`: dựng `LiveSession` (card reader, `HudReader`, `RerollButtonReader`, `Advisor`, `HeldAugmentTracker` luôn bật) |
| `worker.py` · `scan.py` | Chạy session ngoài luồng UI · quét trước video để tìm các màn chọn lõi (mốc tua) |
| `viewmodel.py` | `LiveEvent` → view model (`SlotVM`, `VerdictVM`, `StripVM`, `PlanLineVM`) — không Qt |
| `widgets.py` | Dải trạng thái (VÒNG / CẤP / VÀNG / MÁU / CHUỖI / ĐỔI THẺ + hàng lõi đã cầm), thẻ kết luận, cột từng ô, khối **THEO HƯỚNG ĐI** (`PlanPanel`) |
| `overlay.py` | Vẽ đè lên khung video: huy hiệu từng ô, viên hướng neo dưới ô chữ của thẻ được chọn cho hướng đó |
| `theme.py` · `icons.py` | Bảng màu (mặc định **`arena`**; màu hướng cố định qua mọi bảng màu) + font **Chakra Petch** (tiêu đề, số) và **Be Vietnam Pro** (chữ thân), đóng gói ở `assets/fonts/` (OFL), nạp bằng `load_fonts()` · icon lõi: CDragon (`data/augment_icons/`) → icon cắt từ thẻ → chữ cái |

Ảnh và chi tiết UI: [`dev_log.md`](dev_log.md) §18.

> ❌ **Bỏ `widgets/minimap_widget.py`** — nó tồn tại để hiển thị scouting info. Riot cấm (§11).
> Ngoài ra minimap đã bị **deprecated** trong bản Unreal.

**Cơ chế Win32 bắt buộc:**

```python
# PyQt6 expose sẵn, KHÔNG cần SetWindowLong thủ công:
#   FramelessWindowHint | WindowStaysOnTopHint | Tool | WindowTransparentForInput
#   + WA_TranslucentBackground + WA_ShowWithoutActivating

# MẶC ĐỊNH TẮT kể từ 2026-09-04 — xem hộp cảnh báo bên dưới:
SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)   # 0x00000011
#   · hwnd phải là top-level và thuộc chính process này
#   · cần DWM compositing
#   · dưới Win10 2004 → degrade thành WDA_MONITOR, vẽ ô trắng đè lên ROI (xem §3.0)

SetProcessDpiAwareness(2)   # TRƯỚC khi khởi tạo QApplication
```

> 🔄 **Đổi quyết định (2026-09-04)** — `create_windows(capture_protection=False)`, cờ
> `capture.overlay_capture_protection` trong `settings.yaml`. Đánh giá rủi ro:
> [`research/vanguard/capture-design.md`](research/vanguard/capture-design.md).
>
> Vấn đề "overlay tự lọt vào ảnh nó chụp" là **có thật**, nhưng cách chữa nhắm vào triệu chứng.
> Chụp **theo cửa sổ game** thay vì chụp cả desktop (§3.1) khiến vòng lặp đó **không hình thành được
> về mặt cấu trúc** — không cần gọi API nào để chặn. Đồng thời loại bỏ lời gọi duy nhất trong stack
> có *hình dạng* giống né tránh: `GetWindowDisplayAffinity` đọc được *"from any process"* không cần
> quyền gì, `vgk.sys` có hook ở `NtUserGetWindowDisplayAffinity`, và một anti-cheat cùng ngành (TAC
> của Activision) thu thập rồi gửi giá trị này về server.
>
> Riot xác nhận (05-2024) họ **chụp vùng màn hình mà client chiếm**, để tìm ESP hack. Một panel tư vấn
> **hiện ra** bị đánh giá theo *nội dung* — vô hại. Một cửa sổ **cố tình ẩn** khỏi đúng bức ảnh đó bị
> đánh giá theo *hành vi*. Hiện ra là lựa chọn đúng với chuẩn trung thực của §11.5.
>
> `apply_capture_protection()` **giữ nguyên và vẫn test đầy đủ** — nó là đường lui cho máy không chụp
> theo cửa sổ được. Chỉ mặc định đổi, và `tests/test_overlay.py` khoá mặc định đó lại.

> **Hai cửa sổ, ngay từ đầu**: `WS_EX_TRANSPARENT` là all-or-nothing — một cửa sổ không thể vừa
> click-through vừa có widget bấm được. Retrofit sau rất đau.

**Hotkey Controls** *(thiết kế — chưa gắn)*:

> 🔄 **v4**: các phím F1–F4 / Ctrl+Q dưới đây **chưa được gắn vào vỏ nào**. `src/utils/hotkeys.py`
> (`RegisterHotKey`, §1.3) đã có và có test, nhưng chưa vỏ nào dùng. Vỏ replay chỉ có phím cục bộ
> của cửa sổ Qt (vd `F3` = "Đọc lại thẻ", gọi `LiveSession.force_refresh()`), không phải hotkey toàn cục.

| Hotkey | Action |
|---|---|
| `F1` | Toggle overlay visibility |
| `F2` | Toggle click-through (interactive mode) |
| `F3` | Force refresh game state |
| `F4` | Toggle detailed/compact mode |
| `Ctrl+Q` | Quit agent |

---

## 4. Tech Stack

| Component | Technology | Lý do chọn |
|---|---|---|
| Language | **Python 3.11+** | Rich AI/ML ecosystem |
| Screen Capture | **dxcam 0.3.x** (DXGI + WinRT) / mss | Nhanh nhất trên Windows; ứng viên: `windows-capture` (WGC, window-scoped) |
| Computer Vision | **OpenCV 4.x** | Template matching, image processing |
| OCR | **RapidOCR** (PP-OCRv6) | Không cần torch; PP-OCRv6 là model duy nhất list `vi` |
| Overlay UI | **PyQt6** | Transparency/click-through tốt nhất |
| LLM | **Gemini Flash** (`google-genai`) | Multimodal, latency thấp |
| Meta Data | **OP.GG MCP** (MIT) | API chính thức thay cho scraping |
| Static Data | **CommunityDragon** | Champions/traits/items/locale, cập nhật mỗi patch |
| Config | **PyYAML** | Human-readable |
| Logging | **loguru** | Structured logging |
| Hotkeys | **Qt `RegisterHotKey`** (mặc định) / `keyboard` (nếu cần in-game, xem §1.3) | Tránh `WH_KEYBOARD_LL` khi có thể |
| Windows API | **pywin32** | `SetWindowDisplayAffinity`, client rect |

---

## 5. Cấu Trúc Thư Mục

> 🔄 **v4**: cây dưới đây liệt kê theo `git ls-files` tại `84ccbb3` (rút gọn; bỏ `__init__.py`,
> `__pycache__`). Cây dự kiến của v3 có `src/main.py`, `utils/preflight.py`, `capture/screen_capture.py`,
> `vision/{template_matcher,board_reader,shop_reader}.py`, `game_state/{session_detector,economy,pool_tracker}.py`,
> `knowledge/item_guide.py`, `overlay/widgets/{advice_panel,comp_tracker,econ_widget,item_widget}.py`,
> `scripts/sync_assets.py` — **không file nào trong số đó tồn tại**.

```
TFT_Agent/
├── SPEC.md · README.md · dev_log.md · requirements.txt · .env.example
├── run_replay.py                # vỏ replay — entry point duy nhất ở gốc repo (§3.6)
│
├── research/                    # báo cáo research — mục lục: research/overview.md
├── docs/                        # thiết kế chi tiết; kế hoạch hiện hành: docs/next-steps.md
│   ├── directional-augment/     # §3.5.6 — plan-conditioned-advice.md, implementation-plan.md
│   ├── augment-reroll/ · offer-rounds/ · expert-prior/ · category-multilabel/
│   └── live-mode/ · playtest-fixes/ · vision/
├── reports/                     # augment-classification.{html,json}
│
├── config/
│   ├── settings.yaml            # đường dẫn dữ liệu, enable_scouting (mặc định false), capture.*
│   ├── scoring_weights.yaml     # weights w₁..w₅ + tuning (gồm tuning.plan_fit) + comp_selector + reroll_policy
│   ├── data_sources.yaml
│   └── screen_regions*.yaml     # ROI tỉ lệ + anchor; bản theo video được commit, bản chính bị gitignore
│
├── tools/                       # chạy tay, không nằm trong vòng lặp
│   ├── calibrate.py · build_frame_labels.py · bench_hud_latency.py · ui_prototype.py
│   └── probe_environment.py · probe_quick.py    # thăm dò máy game, chụp WGC (§3.0, §3.1)
│
├── scripts/
│   ├── build_augment_features.py · review_augment_features.{py,html} · apply_manual_review.py  # §3.4.1
│   ├── build_name_index.py · build_game_tables.py · fetch_locale.py · fetch_augment_icons.py
│   ├── crawl_*.py · import_augment_tiers.py · refresh_data.py · build_mock_*.py
│   ├── eval_playtest.py · eval_held_augments.py · eval_plan_advice.py · run_evaluation.py   # §12
│   ├── draft_playtest_labels.py · review_playtest_labels.{py,html} · directional_baseline.py
│   ├── scan_vod.py · qualify_vod.py · extract_frames.py · evaluate_recognition.py
│   ├── advise_from_frame.py · read_reroll_buttons.py · build_reroll_template.py · demo_overlay.py
│   └── state_effect_report.py · reason_quality_report.py · measure_offer_round_pool.py · compare_metatft_tags.py
│
├── src/
│   ├── capture/                 # frame_source.py · video_source.py · regions.py (§3.1)
│   ├── vision/                  # ocr_engine · preprocess · hud_reader · player_row · reroll_buttons
│   │                            # augment_reader · held_augments · frame_reader (§3.2)
│   ├── live/                    # session.py (LiveSession) · events.py · card_reader.py · screen_tracker.py
│   ├── replay/                  # window · worker · scan · viewmodel · widgets · overlay · theme · icons (§3.6)
│   ├── game_state/              # models.py · state_tracker.py (§3.3)
│   ├── knowledge/               # cdragon_client · augment_catalog · augment_features · name_index
│   │                            # stats_provider · comp_database · roll_odds · riot_api · data_freshness
│   │                            # data_refresh · tftacademy(_comps) · metatft(_comps) · tactics_tools · lolchess_guide
│   ├── decision/
│   │   ├── advisor.py · augment_advisor.py · reroll_policy.py · margin.py · state_effect.py
│   │   ├── comp_selector.py · comp_signals.py · rules_engine.py · item_advisor.py
│   │   ├── position_advisor.py · contest_analyzer.py · llm_reasoner.py
│   │   └── scoring/             # types · base · board_fit · econ_fit · item_fit · tempo_fit · plan_fit
│   ├── eval/                    # scenario_logger · recognition · correlation · expert_study · ablation
│   │                            # reroll_ablation · dataset_split · playtest_{labels,metrics,draft,review} · metatft_tags
│   ├── overlay/                 # overlay_window.py · styles.py · widgets/augment_panel.py
│   └── utils/                   # env.py · settings.py · hotkeys.py
│
├── assets/fonts/                # Chakra Petch + Be Vietnam Pro (OFL) — font của replay/panel
│
├── data/
│   ├── augment_features.json    # 258 lõi, COMMIT, audit tay được (§3.4.1)
│   ├── augment_icons/           # icon CDragon (172 file) — mẫu dự phòng cho held_augments + icon replay
│   ├── augment_overrides.json · augment_tier_overrides.json · augment_tiers*.json · augment_rounds.datatft.json
│   ├── name_index.json · item_recipes.json · champion_costs.json · lolchess_guide.json
│   ├── meta_comps*.json · tactics_tools_stats.json · augment_stats.csv (MOCK) · patch_state.json
│   ├── patches/<patch>/         # dữ liệu theo patch để chấm video bằng đúng patch của nó
│   ├── templates/               # reroll_glyph.{png,json} cho reroll_buttons
│   ├── eval/                    # split.json · playtest/*.json (nhãn) · nhãn duyệt lõi · runs/ (gitignore)
│   ├── live_probe/ · vod_index/ · cdragon_cache/ (gitignore)
│   └── scenarios/               # dataset do ScenarioLogger sinh (§12.0) — gitignore
│
└── tests/                       # test_*.py (gồm test_readonly_invariant.py — §1.3, §11.4) + fixtures/
```

> **Nguyên tắc**: `config/screen_regions.yaml` và `assets/` đều là **sản phẩm sinh ra**, không phải
> nguồn. Per-set churn là thứ đã giết mọi TFT overlay open-source trước đây — asset curate tay đảm bảo
> chết theo cách y hệt.
>
> 🔄 **v4**: nguyên tắc vẫn giữ, nhưng chỗ áp dụng đã đổi. `assets/` giờ chỉ chứa font (commit kèm giấy
> phép OFL); dữ liệu sinh ra theo set/patch nằm ở `data/` (`augment_icons/` do
> `scripts/fetch_augment_icons.py` sinh, `name_index.json`, `item_recipes.json`, `augment_features.json`…)
> và được sinh lại bằng script (riêng bảng đặc trưng có tầng duyệt tay, được giữ lại qua mỗi lần sinh
> lại — §3.4.1). `scripts/sync_assets.py` không tồn tại.

---

## 6. Dependencies

```txt
# Core - Screen Capture & Vision
dxcam>=0.3.0
mss>=9.0.0
opencv-python>=4.8.0
rapidocr>=3.9.2          # pin PP-OCRv6 model (model duy nhất hỗ trợ 'vi')
numpy>=1.24.0
Pillow>=10.0.0
comtypes                 # pin để tránh dxcam issue #139

# UI - Overlay
PyQt6>=6.5.0

# AI - LLM Reasoning
google-genai>=2.20.0     # THAY google-generativeai (EOL 2025-11-30)

# Data
requests>=2.31.0
beautifulsoup4>=4.12.0   # chỉ cho fallback scraper
pyyaml>=6.0.0

# Utils
loguru>=0.7.0

# Windows
pywin32>=306

# Đánh giá (chưa commit)
# windows-capture>=2.0.1   # WGC, capture theo window — xem §3.1
# keyboard>=0.13.5         # CHỈ nếu cần hotkey in-game; đọc §1.3 trước
```

**Verify**: `pip install --dry-run -r requirements.txt` phải chạy sạch, không có
"No matching distribution found".

---

## 7. Kế Hoạch Phát Triển

> 📌 **v4 — mục này là LỊCH SỬ.** Kế hoạch hiện hành (trạng thái, việc tiếp theo, hạn) nằm ở
> [`docs/next-steps.md`](docs/next-steps.md); kế hoạch directional augment ở
> [implementation-plan](docs/directional-augment/implementation-plan.md). Các ô đánh dấu dưới đây
> không được cập nhật thêm.

> ⏱️ **Số tuần là ước lượng, thứ tự mới là thứ quan trọng.** Thứ tự dưới đây được sắp theo **phụ
> thuộc**: không có bước nào cần kết quả của bước sau nó.

### Phase 0: De-risk (Tuần 1) 🚨 — **chặn mọi thứ khác**
- [ ] Chụp 1 frame trên **live Unreal build (18.1)** → assert không đen hoàn toàn
- [ ] Xác nhận Unreal build còn hỗ trợ **Borderless Windowed** (chưa nguồn nào trả lời)
- [ ] **Ghi lại process name / executable / window class hiện tại** — mốc so sánh cho client 2026-10-09
- [ ] Test capture ở fullscreen-exclusive
- [ ] Benchmark RapidOCR PP-OCRv6 trên frame 1080p **khi game đang chạy** (mọi số latency hiện có đều đo trên máy rảnh)
- [ ] `GET 127.0.0.1:2999/liveclientdata/allgamedata` trong trận TFT thật
- [ ] ~~Ticket Riot DevRel~~ — **bỏ**, không còn liên quan (§11)
- [ ] ~~Spike Overwolf GEP~~ — **bỏ**, xem §9 quyết định #5

### Phase 1: Foundation (Tuần 1–2) 🏗️
- [ ] Project setup, virtualenv, `pip install --dry-run` sạch
- [ ] `preflight.py` — toàn bộ self-check ở §3.0
- [ ] Screen capture (dxcam DXGI → WinRT → mss)
- [ ] `tools/calibrate.py` + sinh `screen_regions.yaml` **trên HUD Unreal**
- [ ] `session_detector.py` — in-game / lobby / occluded
- [ ] Basic OCR (Gold, HP, Level, Stage)
- [ ] Game state data models (kèm `OpponentBoard`, chưa dùng)
- [ ] Basic overlay (2 cửa sổ + `WDA_EXCLUDEFROMCAPTURE`)
- [ ] **`tests/test_readonly_invariant.py`** — thi hành §1.3 ngay từ đầu

### Phase 2: Knowledge + Feature Table (Tuần 2–3) 📚
- [ ] `cdragon_client.py` — roster, traits, locale `vi_vn` (assert `Last-Modified`)
- [ ] `scripts/sync_assets.py` — sinh icon templates tự động từ `/latest/`
- [ ] Bảng join 4 cột: `trait_id` → EN → icon file → VI
- [ ] Tier ladder 254/254 + xử lý 5 cặp mập mờ (§3.5.4)
- [ ] **`scripts/build_augment_features.py` → `data/augment_features.json`** + audit tay
- [ ] `stats_provider.py` — Protocol + `NullProvider` + `CsvProvider`
- [ ] Roll odds / pool size — **vẫn gate**, 18.1 chưa public số

### Phase 3: Recognition + Logger (Tuần 3–5) 👁️
- [ ] **Augment screen detection + recognizer** (Gemini Vision → RapidOCR fallback) — làm TRƯỚC
- [ ] Champion recognition (shop + board + bench)
- [ ] Item recognition · Star level detection · Trait panel reading
- [ ] **`eval/scenario_logger.py` — SHIP Ở ĐÂY, không để cuối**

> ⚠️ **Vì sao logger phải ra sớm**: §12.2, §12.3 và §12.4 đều ăn **chung một dataset** do logger sinh.
> Nếu logger ra ở Phase cuối thì không có dữ liệu để đánh giá, và deadline đồ án không tha cho việc đó.
> Logger chạy sớm = dataset tự tích luỹ trong lúc bạn vẫn đang code phần khác.

### Phase 4: Augment Advisor (Tuần 5–7) 🤖 — **TRỌNG TÂM ĐỒ ÁN**
- [x] `config/scoring_weights.yaml` — cả `weights` (ablation) lẫn `tuning` (hành vi component)
- [x] 5 thành phần điểm — mỗi cái trả `(score, reason)` (§3.5.4)
- [x] `augment_advisor.py` — tổng hợp, xếp hạng, xử lý cặp mập mờ
- [x] `widgets/augment_panel.py` — hiển thị xếp hạng **kèm lý do**; `build_rows()` tách khỏi Qt để test được
- [x] `test_scoring.py` — unit test từng thành phần
- [x] `scripts/build_augment_features.py` → `data/augment_features.json` (254/254, tầng 1 không cần key)

### Phase 5: Advisor phụ trợ (Tuần 7–8) 🎨
- [x] Comp Selector (cấp dữ liệu cho `BoardFit`) · Economy rules · Item · Position
- [x] LLM refinement (tùy chọn, sau hard timeout, **không đổi thứ hạng** — khoá bằng `assert_order_preserved`)
- [x] `advisor.py` — điều phối, mỗi advisor phụ được phép hỏng riêng
- [x] `overlay_window.py` + `styles.py` + loader `settings.yaml`
- [ ] Hotkey system + settings UI — **hoãn**: cần quyết định ở §1.3 về thư viện nghe phím, và cần desktop thật

> ⚠️ `roll_odds.py` **có gate**: `get_odds()` ném `UnverifiedDataError` chừng nào 18.1 chưa xác minh.
> Economy Advisor vì thế không dùng bảng xác suất — chỉ dùng interest/streak (đo được trong trận).

### Phase 6: Đánh giá (Tuần 8–10) 📊 — **§12**
- [x] `eval/scenario_logger.py` — ghi đủ `GameState` để chấm điểm lại được
- [x] `eval/recognition.py` — P/R/F1 theo thực thể + latency p50/p95, tách riêng 5 cặp mập mờ
- [x] `eval/correlation.py` — Spearman (có xử lý hạng đồng hạng) + p-value hoán vị
- [x] `eval/expert_study.py` — export **không kèm** xếp hạng advisor, tính Cohen's κ
- [x] `eval/ablation.py` — tắt từng `wᵢ`, lập bảng delta, có dòng "chỉ `w₁`"
- [x] `scripts/run_evaluation.py` — chạy cả 4 phương pháp, sinh bảng cho chương kết quả
- [ ] Gán nhãn 200–500 frame — **cần Track B**, harness đã sẵn sàng
- [ ] Viết chương kết quả — **cần dataset thật**

### Phase 7: Scouting + contest_score (tuỳ chọn) 🔍
- [x] `contest_analyzer.py` → `contest_score` vào §3.5.2, bỏ qua board đọc dưới ngưỡng tin cậy
- [x] `enable_scouting` trong `settings.yaml` — **mặc định `false`**, có test cho cả hai trạng thái
- [ ] Đọc `OpponentBoard` qua scoreboard/tab — **cần Track B** (đây là phần khối lượng CV)

> Hoãn có chủ đích. Chỉ làm khi Phase 4 + 6 đã xong — không được ăn vào thời gian của Augment Advisor.

### Phase 8: Standalone Client (2026-10-09) 🔄 — **deadline bên ngoài**
- [ ] So sánh process name / window class / title với mốc ghi ở Phase 0
- [ ] Sửa window targeting + overlay owner-window logic
- [ ] Kiểm tra CommunityDragon còn feed dữ liệu TFT không

> ⚠️ Mốc này do Riot đặt, **có thể rơi vào giữa đồ án**. Đó là lý do Phase 0 phải ghi lại
> process/window class ngay hôm nay — sau khi client đổi thì không truy ngược được nữa.

### Phase 9: Polish ✨
- [ ] Integration testing, accuracy tuning, README, hướng dẫn chạy lại toàn bộ pipeline

---

## 8. TFT Set Information

### Trạng thái Set 18 — Enchanted Wilds

> ✅ **Set 18 ĐÃ LIVE** từ 2026-08-26 (patch 18.1, Unreal). Verify 2026-08-28: live
> `mDefaultSet.SetName` = `TFTSet18` / `"Enchanted Wilds"`. `/pbe/` và `/latest/` hiện **giống hệt**.

| Mốc | Ngày | Ảnh hưởng |
|---|---|---|
| Set 18 live + **Unreal engine** | **2026-08-26** ✅ xong | Mọi ROI, icon template, star-border heuristic Set 17 thành rác. Minimap deprecated. Min spec: Win10 19041+, DX11 FL4.3, SM5. **macOS bị bỏ** ở 18.1. Client vẫn khởi động từ League/Riot client — chưa đổi process |
| **Standalone TFT PC client** | **2026-10-09** | Có thể đổi process name / executable / window class → vỡ window targeting và overlay owner logic |

**Chiến lược**: build trực tiếp trên **Set 18 live**, data từ `/latest/`. **Không xóa** switch nhánh —
nó cần lại khi standalone client lên PBE (~2026-09-09). Luôn đọc `mDefaultSet.SetName` lúc chạy,
không hardcode tên set.

> ⚠️ Set 18 đổi tên hệ thống augment: `SetAugmentName` = **`"Boombox Augment"`** (Set 17: `"Hexcore
> Augments"`). Mọi chỗ hardcode chuỗi "Hexcore" sẽ vỡ ở 18.1.

### Data Sources — URL chính xác

| Mục đích | URL |
|---|---|
| Champion roster (**authoritative**) | `raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tftchampions-teamplanner.json` — 65 champs, tier `{1:14,2:13,3:14,4:14,5:10}` |
| Active sets / default set | `…/latest/…/v1/tftsets.json` → key gốc `LCTFTModeData`, đọc `.mDefaultSet.SetName` |
| Localized text (VI) | `raw.communitydragon.org/latest/cdragon/tft/vi_vn.json` — assert `Last-Modified` |
| Trait art / augment art | Đọc field `icon` **nguyên văn**, đổi `.tex`→`.png`, prefix `raw.communitydragon.org/latest/game/` — **36/36 OK**. ⚠️ Pattern ghép chuỗi `trait_icon_18_<en_name>.png` chỉ đúng **34/36** |
| Meta decks / augments / items | `https://mcp-api.op.gg/mcp` (MIT) |
| Match history (post-game) | `tft-match-v1` — [developer.riotgames.com/apis](https://developer.riotgames.com/apis) |
| Cơ chế game (XP, thu nhập, chuỗi, tỉ lệ shop, pool, vòng đấu, vai trò) + patch notes | `lolchess.gg/guide/{exp,reroll,rounds,role,patch-notes}` → `data/lolchess_guide.json` qua `scripts/crawl_lolchess_guide.py`. Có **AWS WAF**: bị chặn thì lưu trang bằng trình duyệt, chạy `--from-dir`, **không** giả User-Agent. XP khớp patch notes 18.2; giá tướng khớp CDragon 65/65; tỉ lệ shop chỉ có một nguồn, vẫn gate |
| ~~Data Dragon~~ | **Bỏ** — không có key Set 18 |
| ~~Live TFT state API~~ | **Không tồn tại** |

### 4 cái bẫy im lặng

| Bẫy | Quy tắc |
|---|---|
| `vn_vn.json` (đóng băng 2023-05-03) trả HTTP 200 như `vi_vn.json` | Dùng `vi_vn.json`, assert `Last-Modified` |
| `cdragon/tft/{lang}.json` `sets['18']` chỉ là **stub** (19 PvE entries) | Đọc roster từ `tftchampions-teamplanner.json` |
| Set 18 tái dùng tên asset **Set 10** (`EOG_AugmentProp_Set10.png`) | Key theo `mutator`/`number`, **không bao giờ** theo `name` |
| `character_id` không còn bắt đầu `TFT18_` — 65/65 bắt đầu bằng `DA`; casing khác nhau trong cùng path | **Không** tự ghép URL. Đọc `squareIconPath` nguyên văn |

Chi tiết đầy đủ: [`research/set-data.md`](research/set-data.md).

---

## 9. Quyết Định Thiết Kế

| # | Câu hỏi | Quyết định v3 |
|---|---|---|
| 1 | Resolution? | ✅ **1920×1080** |
| 2 | LLM Provider? | ✅ **Gemini Flash** qua `google-genai` — offline extraction + refinement tuỳ chọn |
| 3 | Riot API Key? | 🔄 **Chỉ còn một việc: crawl meta comp offline.** Augment stats **không lấy được** (trường `augments` đã bị gỡ ở Set 18). Back-fill placement cho §12.2 **đã bỏ hẳn** (2026-09-30, §12.0) — placement gắn tay từ lời khai người chơi. Còn lại đúng `units`/`traits`/`placement` cho `data/meta_comps.json` |
| 4 | Feature ưu tiên? | 🔄 **Augment Advisor → Comp → Economy → Item → Position → Contest** |
| 5 | Overwolf SDK? | ❌ **Loại bỏ.** Cần runtime Electron/JS, và nó thay thế đúng phần CV vốn là đóng góp của đồ án. Dùng GEP thì không còn gì để đánh giá ở §12.1 |
| 6 | Target Set? | ✅ **Set 18 (live)** — data từ `/latest/`. Giữ switch nhánh cho client 2026-10-09 |
| 7 | Game language? | ✅ **Tiếng Việt** — dấu đã đo và bác bỏ; rủi ro thật là trùng tên (§9.2) |
| 8 | Model training? | ✅ **Không cần** — prompt engineering + bảng đặc trưng cache sẵn |
| 9 | Nguồn stats? | 🔄 **Interface cắm-rút** (§3.4.2). Mặc định `Csv` + `Null`; nguồn cụ thể chốt sau |
| 10 | Scouting? | 🔄 **Có, Phase 7, mặc định tắt** — không còn bị policy cấm, nhưng tốn CV |
| 11 | Đánh giá thế nào? | ✅ **Cả 4 phương pháp** — xem §12 |

### 9.1 Chiến Lược LLM

```python
from google import genai   # google-genai — KHÔNG phải google-generativeai (EOL)

client = genai.Client(api_key=...)
response = client.models.generate_content(
    model="gemini-2.5-flash-lite",   # ⚠️ verify lại model ID hiện hành trước khi implement
    contents=[SYSTEM_PROMPT, game_state_context, augment_crop],
    config={"response_mime_type": "application/json", "response_schema": AdviceSchema},
)
```

| Điểm | Ghi chú |
|---|---|
| Model ID | Verify tại [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models) — `gemini-1.5-flash` và `gemini-2.0-flash` đều đã shut down |
| Quota | ❌ **Không** ghi "15 RPM / 1M tokens/day" — Google không còn công bố free-tier limits. Xem quota thật trong AI Studio |
| Kiến trúc quota | Backpressure + hard cap + deterministic local fallback |
| Privacy | Free tier: *"Used to improve our products: Yes"*. Rủi ro thật nằm **trong khung hình** — 8 tên summoner là pixel. **Crop về đúng ROI augment/shop trước khi upload**, và dùng paid tier |
| Structured output | Giữ schema **phẳng**: list của `{name, verdict_enum, one_line_reason}`. Schema sâu có thể bị từ chối |
| Latency | Chưa đo cho crop nhỏ. **Tự benchmark** trước khi cam kết ngân sách/frame |

### 9.2 Chiến Lược Ngôn Ngữ — Tiếng Việt

| Thành phần | Phương pháp | Phụ thuộc ngôn ngữ? |
|---|---|---|
| Champion / Item / Trait recognition | Template matching (icon) | ❌ Không |
| Gold / HP / Level / Stage | OCR allowlist `0123456789-` | ❌ Không |
| Augment recognition | OCR + khớp tên bỏ dấu; Gemini cho ô OCR không chắc (§9.3) | ⚠️ Có — đã xử lý |

> ✅ **Rủi ro dấu tiếng Việt đã được ĐO và BÁC BỎ.** Re-verify 2026-08-28 trên `/latest/`: bỏ
> **toàn bộ** dấu (NFD + Mn + `đ→d`) vẫn cho **0 collision** trên 36 traits và 249 augment names.
> Điều kiện duy nhất: normalize **cả hai phía** trước khi so sánh.
>
> ⚠️ **Nhưng rủi ro ngôn ngữ KHÔNG bằng 0.** Dấu thì hết, nhưng **trùng tên thì không**: 254
> augment chỉ còn **249** tên VI duy nhất (EN: 250) — tiếng Việt **tệ hơn** EN một chút.
> Xem [augments](research/vision-stack/augments.md).

### 9.3 Augment Recognition — OCR + khớp danh mục trước, Gemini cho ô không chắc

> 🔄 **v4 — Gemini KHÔNG còn là primary.** Đọc tên thẻ giờ là `src/live/card_reader.py` (§3.2):
>
> | Bằng chứng | Số đo |
> |---|---|
> | OCR **không** sinh được ký tự chồng dấu (`dev_log.md` §10) | Vẫn đúng: 33/35 ký tự thiếu trong charset PP-OCRv6 |
> | Nhưng OCR **không cần** đọc đúng dấu: chuẩn hoá bỏ dấu cả hai phía rồi khớp `data/name_index.json` (chính xác → theo gốc → gần đúng `difflib`, ngưỡng **0,82**) | — |
> | `LiveSession` + `OcrCardReader`, 2 ván / 33 ô có nhãn (2026-09-18) | `card_acc` **1,00**, `wrong_silent` 0 ([eval-dataset](docs/playtest-fixes/eval-dataset.md)) |
> | OCR + khớp danh mục trên 111 thẻ development (2026-11-07, docstring `HybridCardReader`) | đúng 107, **sai 0**, ~15 ms/dòng |
> | Gemini trên 6 ván dev (`dev_log.md` §15) | trung vị 2,2 s, p90 2,9 s; khoá free hay dính 503/429 |
>
> Vì vậy: replay mặc định **`hybrid`** (OCR trước, chỉ gọi Gemini khi OCR không ra đúng một
> `apiName`, Gemini lỗi thì giữ OCR); `build_session` mặc định `ocr` (không mạng). Dòng `Fallback` bên
> dưới ("không dùng RapidOCR đoán bừa") là kết luận cũ khi OCR còn đọc tên thô, **trước** khi có bước
> khớp danh mục.
>
> *(lịch sử)* Phần dưới là thiết kế v3. Ladder tier, luật cặp mập mờ và ranh giới trách nhiệm
> recognizer/scorer vẫn còn hiệu lực.

> 🔄 **Đổi so với v1**: Approach A (Gemini Vision) từ fallback lên **primary**.

**Lý do**: template matching cho augment **không khả thi** — 345 item `DA_*` dùng chung một sprite
(`set18_mechanicicon.tex`), và 48/254 entry `isAugment` mang placeholder `missing-t1/t2/t3.tex`.
Không có template để match.

```
Primary:  Crop ROI augment → Gemini Vision → tên + tier
Verify:   Normalize + fuzzy match phần GỐC (đã tách tier token) vào DB CommunityDragon
Tier:     Ladder icon → 1) missing-t(N)  2) [-_](i{1,3}).tex  3) (digit).tex   = 254/254
          rồi luật cấp catalog: `+`/`++` cùng tier bản gốc; số La Mã tăng ngặt trong họ;
          cuối cùng data/augment_tier_overrides.json (7 lõi, người dùng xác nhận).
          → Tên KHÔNG cho tier tuyệt đối (sửa 2026-10-06, 38 lõi đổi; 70/115/69).
            Xem docs/offer-rounds/tier-mismatch.md.
Ambiguous: 5 cặp trùng cả tên lẫn icon → hiển thị CẢ HAI, gắn nhãn, KHÔNG đoán (số đo thực tế 5 cặp)
Fallback: Từ chối và báo lỗi có lý do, KHÔNG dùng RapidOCR đoán bừa (thực nghiệm đo được 82% tên lõi Set 18 chứa ký tự dấu tổ hợp thiếu trong charset PP-OCRv6 (33/35 thiếu), gây sai ngay cả trên ảnh 96px sạch)
Output:   3 apiName + confidence → đẩy sang Augment Scoring Engine (§3.5.4)
          → XẾP HẠNG đầy đủ theo board state, kèm lý do từng thành phần
```

> 🔄 **Đổi ở v3**: output không còn là "stats tĩnh, không xếp hạng" (ràng buộc §11 cũ). Nhận diện chỉ
> là **đầu vào** của scoring engine — phần xếp hạng mới là trọng tâm đồ án.
>
> **Ranh giới trách nhiệm**: recognizer trả `apiName` + confidence, **không** chấm điểm.
> Scoring engine nhận `apiName`, **không** chạm tới pixel. Tách bạch để §12.1 (độ chính xác nhận diện)
> và §12.2–12.4 (chất lượng tư vấn) đo được **độc lập** — nhận diện sai và tư vấn dở là hai lỗi khác nhau.

---

## 10. Tham Khảo

### Research nội bộ
- [`research/overview.md`](research/overview.md) — verdict + bảng thay đổi spec
- [`research/vanguard-risk.md`](research/vanguard-risk.md) — Riot policy nguyên văn
- [`research/set-data.md`](research/set-data.md) — Set 18 timeline, data URLs, các bẫy
- [`research/vision-stack/overview.md`](research/vision-stack/overview.md) — capture + overlay
- [`research/vision-stack/ocr.md`](research/vision-stack/ocr.md) — OCR + matching rules
- [`research/vision-stack/augments.md`](research/vision-stack/augments.md) — **MỚI** tier ladder, cặp không phân biệt được
- [`research/prior-art.md`](research/prior-art.md) — project đã chết, overlay UI, LLM layer
- [`research/open-questions.md`](research/open-questions.md) — việc cần tự kiểm chứng

### Open-Source Projects
- [jfd02/TFT-OCR-BOT](https://github.com/jfd02/TFT-OCR-BOT) — archived 2026-04-09. Tham khảo `ocr.py`;
  **không** lấy `requirements.txt` (chứa PyDirectInput)
- [Kyrluckechuck/TFT-Bot](https://github.com/Kyrluckechuck/TFT-Bot) — archived; cảnh báo Vanguard gốc
- [TeamFightTacticsBots/Alune](https://github.com/TeamFightTacticsBots/Alune) — active, chuyển sang emulator
- [ra1nty/DXcam](https://github.com/ra1nty/DXcam) — capture, hồi sinh 2026

### APIs & Data
- [Riot Developer Portal](https://developer.riotgames.com/) · [TFT policy](https://developer.riotgames.com/docs/tft)
- [CommunityDragon](https://www.communitydragon.org/) · [OP.GG MCP](https://github.com/opgginc/opgg-mcp)
- [Overwolf TFT GEP](https://dev.overwolf.com/ow-native/live-game-data-gep/supported-games/teamfight-tactics/)

### Libraries
- [PyQt6](https://doc.qt.io/qtforpython-6/) · [OpenCV](https://docs.opencv.org/) · [RapidOCR](https://rapidai.github.io/RapidOCRDocs/)
- [Gemini API](https://ai.google.dev/gemini-api/docs) · [SetWindowDisplayAffinity](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowdisplayaffinity)

---

## 11. Phạm Vi, Đạo Đức & Giới Hạn Nghiên Cứu

> Thay thế "Compliance Contract" của v2. Hội đồng **sẽ hỏi** đồ án này có hợp lệ không — mục này là
> câu trả lời, viết thẳng, không né.

### 11.1 Phạm vi tự ràng buộc

| Cam kết | Chi tiết |
|---|---|
| Chạy cục bộ, single-user | Chỉ trên máy tác giả, phục vụ đúng tài khoản của tác giả |
| **Không phát hành** | Không build installer, không publish, không chia sẻ binary |
| Không thương mại hoá | Không bán, không nhận tài trợ, không quảng cáo |
| Không chơi hộ / boosting | Không dùng trên tài khoản người khác, không chia sẻ tài khoản |
| Repo công khai chỉ để chấm | Mã nguồn + đồ án; **không** kèm hướng dẫn triển khai cho người dùng cuối |

### 11.2 Vì sao Riot developer policy nằm ngoài phạm vi

Policy ràng buộc sản phẩm **phục vụ người chơi**, tức được **đăng ký và phân phối**:
*"If your product serves players, you must register it with us…"*

Đồ án này **không phục vụ ai ngoài chính tác giả** và **không được phân phối**, nên không rơi vào phạm
vi điều chỉnh đó. Đây là quyết định có ý thức của tác giả, không phải sơ suất — và nó chỉ đúng **chừng
nào §11.1 còn được giữ**.

### 11.3 Cái VẪN ràng buộc đầy đủ — và đây là hai trục độc lập

> ⚠️ **Bỏ developer policy KHÔNG có nghĩa là bỏ luật chơi.** Riot ToS §7.1(11) và Vanguard áp dụng cho
> **mọi** phần mềm chạy cùng game, phát hành hay không. Đây là lý do §1.3 không đổi một dòng nào.

| Trục | Trạng thái ở v3 |
|---|---|
| **Developer policy** (đăng ký, phân phối, tính năng) | ❌ Ngoài phạm vi — không phát hành |
| **Riot ToS §7.1(11) + Vanguard** (memory, injection, hook, input) | ✅ **Ràng buộc đầy đủ, thi hành bằng test** |

### 11.4 Thi hành bằng test, không bằng lời hứa

`src/compliance/gate.py` của v2 đã bị **xoá** — nó gác *policy*, thứ giờ không còn áp dụng.
Thay bằng một thứ mạnh hơn: kiểm tra tĩnh rằng **kiến trúc thực sự read-only**.

```python
# tests/test_readonly_invariant.py — chạy trong CI, fail thì build đỏ
FORBIDDEN = [
    "pyautogui", "pydirectinput", "pynput",        # synthetic input
    "SendInput", "keybd_event", "mouse_event",      # Win32 input injection
    "WriteProcessMemory", "ReadProcessMemory",      # memory access
    "OpenProcess", "CreateRemoteThread",            # injection
    "d3d11.dll", "Present", "detours",              # render hooking
]

def test_no_forbidden_symbol_in_import_graph():
    """§1.3 phải là thuộc tính KIỂM CHỨNG ĐƯỢC của source, không phải lời hứa trong doc."""
    for symbol in FORBIDDEN:
        assert symbol not in scan_all_source_and_imports("src/")
```

> 💡 **Vì sao đây là điểm cộng cho đồ án**: "tôi hứa không đọc memory" là lời khẳng định.
> "Đây là test chứng minh không dòng nào trong source chạm tới memory API" là **bằng chứng**.
> Hội đồng verify được trong 5 giây.

### 11.5 Rủi ro còn lại — nói thật

| Điều | Trạng thái |
|---|---|
| Ban vì overlay read-only | Tìm 4 ngôn ngữ: **0 ca được xác nhận** — nhưng cũng **0 tuyên bố nào của Riot nói là an toàn** |
| Kết luận trung thực | Rủi ro thực nghiệm **thấp**, rủi ro pháp lý **chưa được giải quyết**. Đây là *absence of evidence*, không phải *evidence of absence* |
| Giảm thiểu | Kiến trúc read-only + không phát hành + không boosting |

### 11.6 Điều kiện kích hoạt lại ràng buộc cũ

**Nếu đồ án này từng được phát hành**, toàn bộ corridor §11 của v2 áp dụng lại đầy đủ: augment chỉ được
hiện stats tĩnh không xếp hạng, không scouting, phải đăng ký với Riot.
[`research/vanguard-risk.md`](research/vanguard-risk.md) được **giữ nguyên** làm cơ sở bằng chứng cho
tình huống đó — nghiên cứu đó vẫn đúng, chỉ là hiện không áp dụng.

---

## 12. Phương Pháp Đánh Giá

Đồ án cần **bằng chứng đo được**, không chỉ demo chạy được. Bốn phương pháp, bổ trợ nhau.

> ⚠️ **Phụ thuộc quan trọng**: §12.2, §12.3, §12.4 dùng **chung một dataset** do
> `eval/scenario_logger.py` sinh ra. Vì thế logger **phải ship ở Phase 3**, không phải Phase cuối.

> 🔄 **v4 — thước đo đang dùng thực tế.** Bốn phương pháp dưới đây vẫn là khung của chương kết quả,
> nhưng số đang được đo hằng ngày đến từ các script chạy trên **nhãn playtest đã duyệt**
> (`data/eval/playtest/*.json`, chia dev/held-out cố định ở `data/eval/split.json`; mỗi video chấm
> bằng dữ liệu patch của chính nó):
>
> | Script | Đo gì | Chỉ số |
> |---|---|---|
> | `scripts/eval_playtest.py` | Cả vòng đọc (`--mode session` = `LiveSession`) so với nhãn | `card_acc`, `wrong_silent`, `missing`, `reroll_recall`, `hud_acc[gold/level/xp/xp_needed/hp/streak]`, latency p95 |
> | `scripts/eval_held_augments.py` | Bộ đọc dải icon lõi đã chọn (ứng viên lấy từ nhãn) | đúng / chưa rõ / sai so với `picked` |
> | `scripts/eval_plan_advice.py` | Gợi ý theo hướng (§3.5.6) | top-1 khớp `picked`: tắt (`rank()`) vs bật (dòng của `plan.route`) |
>
> `picked` là lựa chọn của **một** người chơi → đây là độ khớp với chuyên gia, không phải độ chính xác.
> Dev chỉ để chỉnh; số báo cáo lấy từ held-out (video 18.6).

### 12.0 ScenarioLogger — nền của ba phương pháp sau

Mỗi lần màn hình chọn augment xuất hiện, ghi 1 file JSON vào `data/scenarios/` (hiện là
**`schema_version` 3**: schema 2 thêm `game_id`, schema 3 thêm khuyến nghị đổi thẻ của §3.5.5; file
schema cũ vẫn đọc được — xem `src/eval/scenario_logger.py`). Ví dụ rút gọn:

```json
{
  "ts": "...", "frame_ref": "frames/0001.png",
  "recognized": [{"api_name": "...", "confidence": 0.94, "ambiguous": false}, ...],
  "game_state": { "...GameState đầy đủ..." },
  "component_scores": {"DA_X": {"base": 0.7, "board_fit": 0.9, "...": "..."}},
  "ranking": ["DA_X", "DA_Y", "DA_Z"],
  "player_pick": "DA_Y",
  "final_placement": null
}
```

`final_placement` do **người chơi tự khai** sau ván, gắn tay vào file nhãn
([recording protocol](docs/playtest-fixes/recording-protocol.md)).

> 🔄 **Đổi quyết định (2026-09-30) — bỏ hẳn đường back-fill qua Riot API.** v3 dự tính lấy
> `final_placement` từ `tft-match-v1`. Ba lý do độc lập cùng loại bỏ nó:
>
> 1. **Personal Key hết hạn 24 giờ** — mỗi lần back-fill phải lấy key mới.
> 2. **Cần PUUID của người chơi**, tức danh tính tài khoản của người tham gia khác. Trái với
>    cam kết dữ liệu cá nhân ở §11.
> 3. **Trận tuỳ chỉnh không lên `tft-match-v1`** (đo 2026-09-06, xem `dev_log` §9).
>
> Và lợi ích duy nhất của nó — tự điền placement — đã không cần nữa vì bộ nhãn gắn tay.
> `ScenarioLogger.back_fill_placement()` **giữ nguyên**: nó nhận một số nguyên và không quan tâm
> số đó từ đâu. Chỉ nguồn đổi, không phải cơ chế.
>
> `riot_api.py` **vẫn dùng** — cho việc crawl meta comp thật (`units`/`traits`/`placement` còn
> nguyên, `data/meta_comps.json` = 249 trận). Bỏ Riot API khỏi đường *placement của scenario*
> không có nghĩa là bỏ nó khỏi dự án.

### 12.1 Độ chính xác nhận diện (CV/OCR)

| Mục | Chi tiết |
|---|---|
| Dataset | **200–500 frame** gán nhãn tay, phủ đủ các stage và cả 5 cặp augment mập mờ |
| Chỉ số | Precision / Recall / **F1** theo từng loại thực thể (augment, champion, item, gold, level, HP, stage) |
| Latency | p50 / p95, đo **khi game đang chạy** — không đo trên máy rảnh |
| Ghi chú | Báo cáo riêng độ chính xác trên 5 cặp mập mờ; đây là **giới hạn dữ liệu**, không phải lỗi model |

> 🔄 **v4**: hệ thống **chưa có bộ đọc champion / item** (§3.2), nên mục tiêu P/R/F1 cho champion và
> item **chưa áp dụng**. Phần đo được hiện nay: thẻ lõi (`card_acc`, `wrong_silent`), HUD (`hud_acc`),
> nút đổi (`reroll_recall`), lõi đã chọn (`eval_held_augments.py`) — trên nhãn playtest, không phải
> bộ 200–500 frame. `src/eval/recognition.py` (P/R/F1 + latency) vẫn có và dùng được khi có nhãn frame.

### 12.2 Tương quan với kết quả thật

Trên N trận đã log: tính **Spearman ρ** giữa *thứ hạng advisor gán cho augment người chơi đã chọn* và
*thứ hạng cuối trận*. Giả thuyết: chọn augment mà advisor xếp cao → placement tốt hơn.

> ⚠️ **Giới hạn phải nêu trong báo cáo**: đây là dữ liệu quan sát, **không phải thí nghiệm có đối
> chứng**. Augment chỉ là một trong rất nhiều yếu tố quyết định placement. Nêu rõ cỡ mẫu và không
> tuyên bố quan hệ nhân quả.

### 12.3 Đồng thuận chuyên gia

| Mục | Chi tiết |
|---|---|
| Cách làm | Export ~50 scenario (ảnh + tóm tắt state) → người chơi rank cao xếp hạng độc lập |
| Chỉ số | **Top-1 agreement** + **Brennan–Prediger S** giữa advisor và chuyên gia |
| Đối chứng | So thêm với baseline "chỉ dùng stats tĩnh" để thấy phần board-state đóng góp gì |

> ⚠️ **Sửa 2026-09-06 — mục này trước đây ghi Cohen's κ và đã sai.** Cohen's κ ước lượng đồng thuận
> ngẫu nhiên từ phân phối biên trên **một** không gian nhãn chung. Ở đây mỗi tình huống chào 3
> augment **khác nhau**, gần như rời nhau, nên không gian đó không tồn tại: với `n = 18` và
> `p_o = 0,60`, công thức cũ trả 0,577 ("khá") trong khi giá trị đúng là 0,40 ("trung bình").
> Code đã thay bằng **Brennan–Prediger S** (`p_e` = trung bình của `1/kᵢ`) — xem
> `src/eval/expert_study.py:12-29`. Với không gian nhị phân ĐỔI/CHỌN của §3.5.5 thì `k = 2` nên
> `p_e = 0,5`; vẫn là S, không phải κ.

### 12.4 Ablation study

Tắt lần lượt từng `wᵢ` trong `config/scoring_weights.yaml`, chấm lại **toàn bộ dataset đã log**, đo
delta ở §12.2 và §12.3.

| Cấu hình | Câu hỏi trả lời |
|---|---|
| Full model | Baseline |
| `w₂ = 0` (bỏ BoardFit) | Nhận thức board thực sự đóng góp bao nhiêu? |
| `w₃ = 0` (bỏ EconFit) | — |
| `w₄ = 0` (bỏ ItemFit) | — |
| `w₅ = 0` (bỏ TempoFit) | — |
| **Chỉ `w₁`** (chỉ stats tĩnh) | **Quan trọng nhất** — chứng minh v3 thực sự hơn v2 |

> 🔄 **v4**: `src/eval/ablation.py` chấm lại bằng `rank()` và **chưa có trục `plan_fit`** — gợi ý
> theo hướng nằm ngoài `weights` (§3.5.6). Bật/tắt theo hướng hiện được đo riêng bằng
> `scripts/eval_plan_advice.py` (cờ `tuning.plan_fit.enabled`). Ngoài các `wᵢ`, config còn các trục
> ablation khác: `comp_selector.adaptive`, `reroll_policy.pool_by_offer_round`, `tailoring_beta`,
> `ordinal_trust` (`src/eval/reroll_ablation.py` cho §3.5.5).

> Dòng cuối chính là câu trả lời định lượng cho câu hỏi "vì sao phải làm advisor động thay vì bảng
> stats tĩnh". Nếu delta ≈ 0 thì đó cũng là **một kết quả nghiên cứu hợp lệ** và phải báo cáo trung
> thực, không được giấu.
