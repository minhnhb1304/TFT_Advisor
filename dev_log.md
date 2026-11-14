# Nhật Ký Phát Triển

> Lịch sử dự án. Checkbox trong [`SPEC.md §7`](SPEC.md) đã lỗi thời ở vài chỗ.
> Kế hoạch hiện hành và việc tồn đọng giữa các phiên:
> [`docs/next-steps.md`](docs/next-steps.md).
>
> Cập nhật: **2026-11-14** · 1135 test xanh. Mục 1–13 và "Dự kiến triển khai"
> viết lúc 2026-09-07, giữ làm lịch sử.

---

## Tổng quan

| | |
|---|---|
| **Track A** — lõi offline, không cần game | ✅ **Xong** |
| **Track B** — cần máy đang chạy TFT | ✅ Đường ống vision chạy trên VOD (09-09). Probe client standalone xong (10-13, 10-15), xem [mục 14](#14-probe-client-standalone-wgc-chạy-hud-chậm-khi-game-chạy) |
| Nút thắt hiện tại | Tập đánh giá tự quay chưa có: mọi số nhận diện vẫn đo trên tập phát triển. Đọc HUD khi game chạy mất 15–26 s |

---

## Nhật ký theo mốc

| Ngày | Commit | Nội dung |
|---|---|---|
| 08-06 → 08-14 | `0efe27e`…`3d2dc8b` | SPEC v1→v2, báo cáo research đa ngôn ngữ |
| 08-29 → 08-31 | `c712ae8` | **Lõi Track A**: knowledge · scoring · advisor · eval harness · 155 test |
| 09-01 | `7f473c1` | Sửa bẫy `setData[0]` |
| 09-01 | `2ed54f4` | Tier 1 + Tier 3 của `claude_feedback.md` |
| 09-01 | `a5a88a6` | Tài liệu hoá cảnh báo dữ liệu giả lập |
| 09-01 | `160fdf8` | Nạp key từ `.env` |
| 09-01 | `96dda89` | Tinh chỉnh đặc trưng bằng Gemini |
| 09-01 | `c3ddd6c` | Crawl đội hình meta thật; augment thì **không lấy được** |
| 09-02 | — | Nguồn tactics.tools + bảng tier do người xếp; **xác nhận augment tắc ở mọi nguồn** |
| 09-04 | — | Đánh giá rủi ro Vanguard (8 agent, EN+ZH+RU). Bịt 4 lỗ ở test read-only; chốt chụp theo cửa sổ; bỏ `WDA_EXCLUDEFROMCAPTURE` |
| 09-07 | `8044aac`…`61ad56b` | Capture VOD + quét khung; chính sách reroll tuần tự + Monte-Carlo; chặn nguồn giả lập; banner reroll trên overlay (mục 9–13) |
| 09-08 → 09-09 | `015a5de`…`cdd0a95` | Bảng tier TFT Academy + MetaTFT; reader nút reroll (105/105), HUD reader, Gemini augment reader; 60 khung gán nhãn. **Track B đóng** |
| 09-14 → 09-15 | `fb6e9b1`…`0b7371d` | Công thức trang bị, giá tướng; cơ chế Set 18 từ lolchess.gg; kinh tế Set 18 (chuỗi, thu nhập, XP); chọn đội hình theo archetype; báo dữ liệu cũ khi đổi patch; dữ liệu patch 18.2 |
| 09-16 → 09-19 | `fd6b54d`…`347f5d1` | Trình phát replay + live dùng chung lõi; gán nhãn và chấm bản ghi playtest; đọc máu, chuỗi, HUD mờ; gold/chuỗi/cấp đổi thứ hạng |
| 10-01 → 10-02 | `3549aa7`…`8237ae1` | Khoá khối theo ván cho tập đánh giá; bỏ đường placement từ Riot; đo khối lượng hoà điểm; runbook probe |
| 10-05 | `771689e`…`ba11239` | Audit bảng đặc trưng theo tag MetaTFT (`tempo`, `econ_value`, `trait_count_reward`); trang duyệt tay cục bộ |
| 10-08 | `410af32`…`e982018` | `categories` đa nhãn, `carry_type` both, `frontline`; `offer_rounds` từ datatft; pool reroll theo lượt chào; duyệt tay 254/254 |
| 10-11 → 10-12 | `463de63`…`4446f40` | Duyệt vòng 2 (47/47); áp nhãn tay vào bảng đặc trưng (122 dòng đổi) |
| 10-13 → 10-15 | `4153624`…`b2b7544` | Probe client standalone: dò cửa sổ, WGC, độ trễ HUD; kết quả ván đấu máy và ván Normal (mục 14) |

---

## Đã làm

### Nền tảng dữ liệu

| Hạng mục | Kết quả |
|---|---|
| CDragon client | 6 cái bẫy im lặng thành assert runtime |
| Locale đầy đủ | `fetch_locale.py` → `data/cdragon_cache/` (en_us 23.6 MB + vi_vn 24.2 MB) |
| Bảng đặc trưng augment | 254/254, tầng 1 tất định + tầng 2 LLM (175 dòng tinh chỉnh) |
| Ánh xạ tên → `apiName` | `name_index.json` — 254 augment · 36 trait · 65 champion, VI + EN |
| Đội hình meta | **Đo thật** — 249 trận, 1988 participant, 12 đội hình |
| Đội hình meta (bên thứ ba) | tactics.tools — 456.572 ván, 12 đội hình, cỡ mẫu 819–46.091. Ghi ra **file riêng** |
| Stats unit/trait/item | tactics.tools — 74 unit · 91 trait · 131 item. **Chưa nối vào scoring engine** |
| Bảng tier augment | **Nguồn chính của w₁** (mục 13). Khung + importer đã có, `ordinal_trust: 0.65`. **Repo không kèm dữ liệu — đang chờ bảng thật** |
| Stats augment | ⚠️ **Không có** — mọi nguồn đo được đều đóng. w₁ chuyển sang tiên nghiệm chuyên gia (mục 13); bộ giả lập nay bị `default_provider` chặn |

### Thuật toán (trọng tâm đồ án)

5 thành phần điểm `w₁..w₅` (SPEC §3.5.4), mỗi cái trả `(score, reason)`. Trọng số nằm ở
`config/scoring_weights.yaml` để ablation tắt/bật được mà không sửa code.

Phụ trợ: comp selector · economy rules · item · position · contest score · LLM refinement
(khoá bằng `assert_order_preserved`, không được đổi thứ hạng).

### Đánh giá (SPEC §12)

Harness đủ 4 phương pháp — logger, P/R/F1, Spearman, **Brennan–Prediger S** (không phải Cohen's κ,
xem mục 8b), ablation. **Chạy được nhưng `n = 0`**: chưa có dataset thật.

Ngoại lệ: đối chứng phản thực cho chính sách reroll (mục 12) **chạy được ngay** ở cỡ mẫu tuỳ ý —
nó đo chính sách so với chính sách trên cùng hàm điểm nên không cần nhãn của người chơi.

### An toàn (SPEC §1.3)

`tests/test_readonly_invariant.py` quét AST toàn bộ `src/`, `scripts/`, `tools/`. Hotkey đi qua
`RegisterHotKey` + Qt native event filter — **không** `WH_KEYBOARD_LL`, không cần admin.

---

## Phát hiện đã đổi kế hoạch

Bốn thứ chỉ lộ ra khi chạy thật, không phải khi đọc tài liệu.

### 1. `setData[0]` không phải Set 18

Locale đầy đủ có **35 khối `setData`** không theo thứ tự; khối đầu là `TFTSet14`, còn khối Set 18
có `name = "Set10"`. Lấy nhầm thì bảng trait thành của Set 14, `trait_affinity` rỗng sạch,
`BoardFit` trung tính cho **mọi** augment — **hỏng hoàn toàn im lặng**.

> Fixture trimmed chỉ giữ một khối, nên bug này xanh hết test cho đến ngày gặp file thật.
> **Bài học**: fixture là tập con có thể giấu cái bẫy nằm ở *hình dạng* dữ liệu.

### 2. Riot đã gỡ trường `augments` — và không nguồn nào khác lấp được

Participant Set 18 của `tft-match-v1` **không còn `augments`**; cả payload không có chuỗi
`"augment"` nào (kiểm tra 3 trận ranked, vn2).

SPEC §3.4.2 gọi `RiotApiProvider` là *"bảo vệ tốt nhất trước hội đồng"* cho stats augment.
**Đường đó đã đóng** — không do rate limit hay công sức. Đã sửa SPEC thay vì để nó treo.

Nhưng `units` / `traits` / `placement` còn nguyên → **đội hình meta đo thật được**. Đó là lý do
`meta_comps.json` là thật còn `augment_stats.csv` vẫn giả.

**Kiểm chứng ngoài (09-02).** tactics.tools có sẵn bốn trường augment và **cả bốn đều rỗng** ở mọi
rank group, kể cả nhóm `all` với 1.752.735 ván. datatft nhúng bảng tier **hardcode trong bundle JS**
do ba người chơi xếp; tftacademy chỉ có S/A/B/C, không con số nào. Nghĩa là câu trả lời cho hội đồng
đổi từ *"chúng tôi không crawl được"* thành *"trang thống kê công khai lớn nhất cũng không có"* —
mạnh hơn hẳn. `augment_row_count()` đo lại điều này sau mỗi lần crawl.

### 3. `gemini-2.5-flash-lite` đã bị gỡ

API trả 404 kèm chỉ dẫn dùng `gemini-3.5-flash-lite`. Trước đó handler chỉ in tên kiểu lỗi nên
nuốt mất câu này — giờ in cả nội dung.

### 4. LLM phá dữ liệu đúng nếu không chặn

```
trait_affinity: ['DA_Riftbeast18'] -> []
item_grants:    ['AnyComponent'] -> ['component','component',...]
```

Hai trường đó chứa apiName suy từ dữ liệu có cấu trúc; LLM không thể biết chuỗi đó là gì.
**Nguyên tắc rút ra**: LLM chỉ được dùng cho phần *phán đoán đọc từ văn bản*; phần *định danh*
luôn lấy từ dữ liệu có cấu trúc.

### 5. Riot Champion Roles: cơ chế có sẵn nhưng Set 18 bị rỗng 63/65 tướng

Riot có trường `role` phân loại tướng (`ADCarry`, `APCaster`, `ADFighter`, `APTank`,...). Đo đạc
Set 14–17: **74/88** tướng có role đầy đủ. Nhưng ở **Set 18 live**: chỉ có **11/91** thực thể có
role (9 quái PvE/dummy, 2 tướng chơi được là `Kobuko` và `Alune`; 63 tướng còn lại là `None`).

- **Hiện tại**: Vẫn ưu tiên suy luận carry type từ trang bị (`infer_carry_type`), vì trang bị phản
  ánh đúng ý đồ thực tế của người chơi.
- **Sẵn sàng cho tương lai**: Đã thêm thuộc tính `Champion.role` vào data model và cơ chế fallback
  trong `infer_carry_type` để tự động kích hoạt ngay khi Riot đồng bộ dữ liệu Set 18 vào CDragon.

---

### 6. Test read-only gọi đúng tên mối nguy nhưng lại không chặn nó

`SPEC §1.3` gọi `WH_KEYBOARD_LL` là *"đúng loại hành vi anti-cheat heuristics để ý"*. Nhưng
`tests/test_readonly_invariant.py` **không có** `SetWindowsHookEx` trong danh sách cấm, và chỉ cấm các
hàm *gửi input* của `keyboard` chứ không cấm cả module. Nghĩa là:

```python
import keyboard                      # qua
keyboard.add_hotkey('f1', ...)       # qua — mà nó cài WH_KEYBOARD_LL thật
```

vẫn xanh hết 333 test. Hàng rào an toàn có lỗ ngay chỗ tài liệu chỉ tay vào.

> **Bài học**: một bất biến được "thi hành bằng test" chỉ mạnh bằng đúng danh sách trong test đó.
> Viết ra mối nguy ở tài liệu và cấm nó trong code là **hai việc khác nhau** — dễ tưởng đã làm cả hai
> khi mới làm một. Giờ mỗi ký hiệu mới đều có test riêng chứng minh scanner bắt được, chứ không chỉ nằm
> trong `frozenset`.

Cũng đã bịt: file `.py` ở gốc repo không được quét (entry point tương lai kiểu `main.py` sẽ lọt), và
giới hạn `getattr` động giờ được ghi thành test tài liệu hoá thay vì để người sau tưởng không có.

### 7. Vanguard không phải mối lo chính — nhưng lý do thì đã đổi

Đánh giá lại toàn diện (8 agent, EN+ZH+RU): [`research/vanguard/`](research/vanguard/overview.md).
Ba điều làm đổi thiết kế:

- **Nguồn Riot chính chủ mà pass trước bỏ sót.** [Vanguard FAQ for Third Party
  Applications](https://www.riotgames.com/en/DevRel/vanguard-faq): *"Overlays… should continue to
  function"*, *"External tools reading memory will no longer work"*, *"There is absolutely no allow list
  for Vanguard."* Đây là bằng chứng mạnh nhất cho dự án và nó **đã nằm sẵn trên web** suốt thời gian qua.
- **`vgk.sys` có hook ngay tại syscall ta định dùng.** `NtGdiDdDDIOutputDuplGetFrameInfo` (Desktop
  Duplication) và `NtUserGetWindowDisplayAffinity`. Người RE **chưa mở ra xem hook làm gì**. Không phải
  bằng chứng bị phát hiện — nhưng đủ để đổi câu nói từ *"không có bằng chứng"* thành *"Vanguard ngồi
  ngay đó và chưa ai nhìn vào"*.
- **Riot xác nhận họ chụp vùng client, để tìm ESP.** Tuyên bố 05-2024. Ta chạy borderless, overlay nằm
  trong đúng vùng đó. Đây là vector rủi ro trực tiếp nhất tìm được — và nó không nằm ở nội tại driver
  mà ở một câu Riot nói công khai.

Hai hàng trong `research/vanguard-risk.md` bị **nói quá** và đã sửa: overlay style và DXGI đều từng ghi
"Confirmed" trong khi thực tế chỉ là *chưa có bằng chứng*, và pass trước tìm nhầm loại tài liệu —
tìm **blocking list** trong khi thứ cần tìm là **enumeration heuristic**.

> **Bài học**: tìm không thấy ở đúng một loại nguồn không có nghĩa là không tồn tại. Ghi rõ *đã tìm ở
> đâu*, để lần sau biết chỗ nào chưa tìm.

---

### 8. Ba lỗi trong bộ đánh giá — đều thổi phồng kết quả theo hướng có lợi

Phát hiện 2026-09-06 khi rà `src/eval/` trước lúc đưa dữ liệu thật vào. Cả ba đều **chưa từng
làm test đỏ**, vì chưa có dataset nào chạy qua chúng.

**8a. `export_scenarios` giấu khoá nhưng không giấu thứ tự.** Bản xuất cho chuyên gia ghi
`candidates = list(scenario.ranking)` — tức giữ **đúng thứ tự advisor đã xếp**, nên lựa chọn số 1
của advisor luôn nằm đầu danh sách. Docstring của chính hàm đó viết giấu xếp hạng là *"yêu cầu
phương pháp, không phải tuỳ chọn"*.

> Test `test_export_hides_advisor_ranking_to_avoid_anchoring` chỉ assert khoá `"ranking"` vắng
> mặt, nên nó **xanh trong khi lỗi còn nguyên** — cùng loại thất bại với [mục 6](#6-test-read-only-gọi-đúng-tên-mối-nguy-nhưng-lại-không-chặn-nó).
> **Bài học lặp lại**: test phải kiểm chứng *tính chất*, không phải *hình dạng bề mặt* của nó.

Đã sửa: xáo trộn tất định theo `scenario_id`, ghi kèm `candidate_seed` để tái lập.

**8b. Cohen's kappa tính sai đồng thuận kỳ vọng — và sai theo hướng thổi phồng.** Kappa gộp mọi
`apiName` vào **một** không gian nhãn chung, nhưng mỗi tình huống chào **ba augment khác nhau**,
gần như rời nhau. Với n = 18, mỗi nhãn chỉ còn tần suất ~1/18 nên `p_e ≈ 0.055` thay vì 1/3.

| p_o | Công thức cũ | Đúng |
|---|---|---|
| 0.60 | κ = **0.577** → *"khá"* | S = **0.40** → *"trung bình"* |

Docstring cũ đã nói đúng ý định — *"với 3 lựa chọn, đoán bừa đã trúng 33% rồi"* — nhưng cái được
cài đặt lại không làm điều đó. Đã thay bằng **Brennan–Prediger S** (`p_e` = trung bình của `1/kᵢ`),
đúng bằng con số docstring hứa.

**8c. `permutation_p_value` hoán vị tự do trên dữ liệu có cụm.** `final_placement` là đại lượng
của **một ván**: ba quyết định trong cùng ván mang đúng một giá trị Y. 18 scenario vì thế là
**6 cụm**, không phải 18 quan sát độc lập. Hoán vị tự do dựng nên phân phối null hẹp hơn thật →
p-value **dễ dãi**, tức là có thể bịa ra ý nghĩa thống kê không tồn tại.

Đo trên fixture 6 ván: `p_tự_do = 0.0005` vs `p_theo_khối = 0.0020` — **gấp 4 lần**. `rho` không đổi.

Đã sửa: thêm `Scenario.game_id` (**schema 1 → 2**, file cũ vẫn đọc được), hoán vị theo khối cấp ván.
Thiếu `game_id` thì `n_games = None` và `report()` **in cảnh báo** thay vì lặng lẽ coi là độc lập.

**8d (kèm theo). Cỡ mẫu nhỏ thì không được in nhận định bậc.** Với n = 18, KTC 95% của S là
`[0.167, 0.833]` — trải từ *"không đáng kể"* đến *"rất cao"*. `report()` giờ chỉ in bậc
Landis–Koch khi khoảng tin cậy nằm gọn trong **một** bậc; ngược lại in `CHUA KET LUAN DUOC`.

> Cả ba lỗi đều lệch **cùng một hướng**: làm kết quả trông tốt hơn thực tế. Không có lỗi nào
> lệch ngược lại. Đó là dấu hiệu nên rà tiếp phần còn lại của `src/eval/` với cùng thái độ.

Test: 341 → **353** (12 test mới, trong đó có test hồi quy cho đúng ba lỗi trên).

### 9. VOD giải tỏa Track B một phần — và bảng toạ độ SPEC §3.1 đúng là đã chết

Ngày 2026-09-06 nhận được VOD 5h03 của YBY1 (RRQ) đánh 6 ván giải APAC TPC 1, stream cá nhân,
1920×1080@60, H.264 Main 3,74 Mbps. Đây là **frame Set 18 thật đầu tiên** dự án có.

**Vai trò: tập PHÁT TRIỂN, không phải tập đánh giá.** [`research/vanguard/testing-protocol.md`](research/vanguard/testing-protocol.md)
bước 3 đã chốt tập cho §12.1 là bản ghi **tự quay**. Lấy chính VOD này vừa để đo ROI, chỉnh
ngưỡng, vừa để báo cáo P/R/F1 thì con số đó đo "đã vặn bao nhiêu núm", không đo độ chính xác
nhận diện — và giữ lại một ván làm held-out **không** cứu được, vì cả 6 ván dùng chung một bộ
toạ độ ROI, đúng thứ dễ sai nhất. `timeline.json` ghi sẵn `role: development`.

**Đo được gì.**

| Hạng mục | Kết quả |
|---|---|
| Toàn màn hình khi chơi | ✅ 1920×1080 — chỉ **sảnh chờ** mới ở chế độ cửa sổ. Không gian toạ độ SPEC dùng được |
| Bảng ROI SPEC §3.1 | ❌ **Sai thật** cho Set 18. Bảng panel tộc thực tế `y 258..792`, không phải `200..700` |
| Va chạm overlay | ⚠️ Khung chat với tới `x=890`, ô stage ở `x 768..815` → **chat che ô stage** không lường trước được |
| Ranked API back-fill | ❌ Sảnh là `ĐTCL Tiêu Chuẩn Tùy Chỉnh` — trận tuỳ chỉnh **không lên `tft-match-v1`**. §12.0 nói back-fill `final_placement` từ Riot API; đường đó **không tồn tại** với VOD giải. Chỉ còn đọc từ màn kết trận |
| GOP | 1,000s (18.224 I-frame). Nhưng PTS thật **lệch tới 0,5s** so với giả định 1 giây — phải đối chiếu ffprobe, không được suy ra |

**Phân đoạn ván: đi đường vòng lại đúng hơn.** Ảnh mẫu chụp màn kết trận hoá ra khớp với **cả**
màn sảnh chờ — ở 128×72 thì cả hai đều là "cửa sổ client trên nền desktop". Ban đầu tưởng nhầm,
nhưng đó mới là tín hiệu ổn định hơn vì nó **không phụ thuộc hình vẽ riêng từng ván**. Nghịch đảo
lại: đoạn nào *không* khớp là đang toàn màn hình, tức đang trong trận.

Kết quả: **đúng 6 ván**, dài 33,3–38,1 phút. Đã kiểm mắt ranh giới ván 1 (t=410 sảnh → t=440 màn
loading → t=2620 trong trận → t=2660 desktop).

**Set 18 CÓ màn chọn augment.** Điều này cần nói rõ vì [mục 2](#2-riot-đã-gỡ-trường-augments--và-không-nguồn-nào-khác-lấp-được)
dễ bị đọc thành "Set 18 bỏ augment": không phải. Màn `Chọn Một` vẫn còn, ba thẻ, có nút reroll
riêng từng thẻ, tên + mô tả tiếng Việt **đọc được** (vd `Nhân Bản`, `Cắm Rễ Phân Tán`, `Bừa Bộn`).
Riot chỉ gỡ **trường dữ liệu** khỏi API, không gỡ cơ chế. Đây đúng là thứ `NameIndex.resolve()`
cần.

Dò bằng tương quan chéo (ngưỡng 0,85, gộp 45s): **18 sự kiện, đều tăm tắp 3 mỗi ván** — khớp
đúng giả định của SPEC §12. Kiểm chéo này giờ là một bước trong `scan_vod.py`, in bảng và kêu
lên khi lệch.

**Đã trích:** 90 ảnh PNG (5 ảnh/sự kiện, 214 MB) + crop ROI + manifest. 18/18 sự kiện có ít nhất
một ảnh đã lật bài đọc được — lấy 2 ảnh/sự kiện thì trượt vài cái, vì người chơi chuyên nghiệp
bấm rất nhanh (có sự kiện chỉ dài 1 giây).

**Còn thiếu để có `Scenario` thật:** tầng nhận diện (`augment_reader` qua Gemini Vision theo
§9.3), đọc `player_pick`, đọc `final_placement` từ màn kết trận. Và cỡ mẫu: 18 quyết định là
**6 cụm độc lập** — xem [mục 8c](#8-ba-lỗi-trong-bộ-đánh-giá--đều-thổi-phồng-kết-quả-theo-hướng-có-lợi).

### 10. RapidOCR PP-OCRv6 **không đọc được tiếng Việt có dấu** — và bitrate thì vô can

Đo ngày 2026-09-07 khi trả lời câu hỏi "3,74 Mbps có đủ cho OCR không". Câu trả lời hoá ra
không nằm ở bitrate.

**Bằng chứng quyết định: charset của chính model.** `PP-OCRv6_rec_small.onnx` nhúng bảng ký tự
trong metadata (`character`, 18.709 ký tự). Đối chiếu:

| Lớp ký tự | Có trong charset |
|---|---|
| Nguyên âm biến đổi `ăâêôơưđ` | **7/7** ✅ |
| Thanh điệu đơn `àáảãạ…` | **14/25** — thiếu *toàn bộ* dạng hỏi (`ả`) và nặng (`ạ`) |
| **Chồng tầng** `ắ ầ ễ ộ ừ…` | **2/35** ❌ |

Model **không thể sinh ra** 33/35 ký tự chồng tầng. Mà **82% trong 254 tên augment Set 18**
chứa ít nhất một ký tự như vậy (`data/name_index.json`).

**Đối chứng loại trừ nén.** Render chữ **sạch, không nén**, cỡ 18→96px, rồi cho OCR đọc:
`0/5` tên đúng ở **mọi** cỡ chữ. Ở 96px vẫn ra `Nhân Bån` (thay `Nhân Bản`) và `Ba Bn`
(thay `Bừa Bộn`). Vậy đây **không phải** vấn đề độ phân giải, cũng không phải vấn đề nén.

**Còn chữ số thì bitrate thừa sức.** Trên chính VOD 3,74 Mbps:

| Vùng | Kết quả |
|---|---|
| `gold` | **42/43 = 98%** khung *có thanh HUD hiện* đọc đúng (57/57 ở lần đo đầu) |
| `xp` | đọc đúng `10/60` ở mọi mức phóng |
| `stage` | thô thì trượt; **Otsu → 3/3 đúng**. Đây là vấn đề tương phản (chữ kem trên nền lam), không phải nén |
| `level` | ra `Cp 7` — mất `ấ`, nhưng **con số 7 vẫn đúng**, đủ dùng |

> Khung "trượt" khi lấy mẫu ngẫu nhiên hầu hết là khung **không có thanh HUD** (vòng carousel,
> đang xem board người khác, màn loading) — kiểm bằng mắt 12/12 khung trượt. Đừng tính chúng
> vào tỉ lệ lỗi OCR.

**Hệ quả với SPEC.**
- §9.3 chọn Gemini Vision làm **primary** cho augment: quyết định này giờ có bằng chứng định
  lượng, không chỉ là lập luận về sprite trùng.
- `research/vision-stack/ocr.md` chọn PP-OCRv6 vì *"model duy nhất có `vi` trong danh sách ngôn
  ngữ"*. Có `vi` trong danh sách **không đồng nghĩa** với đọc được dấu tiếng Việt. RapidOCR
  **không phải fallback** cho tên augment — nó là **không dùng được** cho việc đó.
- RapidOCR vẫn tốt cho `gold`/`xp`/`stage`/`level` (chữ số). Giữ lại đúng phạm vi đó.
- Cần thêm bước tiền xử lý **Otsu** trước khi OCR các ô số nhỏ — rẻ và biến `stage` từ trượt
  thành 3/3.

**Chroma 4:2:0 không ảnh hưởng tới bậc augment.** Bậc mã hoá bằng **màu icon** (vàng vs bạc),
không phải viền mảnh. Đo trên vùng icon: lệch chroma của nhóm vàng 73,6–80,4; nhóm bạc 6,7–13,7
→ **khoảng cách +59,9**. Hạ chroma thêm 32 lần nữa vẫn còn cách +32. Không có rủi ro nào ở đây.
(Chỉ quan sát được hai bậc vàng/bạc trong mẫu; chưa gặp prismatic.)

Công cụ: [`scripts/qualify_vod.py`](scripts/qualify_vod.py) đóng các ngưỡng này thành cổng kiểm
tự động cho VOD tiếp theo.

### 11. Rà soát tầng ingestion: 15 lỗi, trong đó 2 lỗi **im lặng báo ĐẠT**

Rà 2026-09-07 trên `scripts/{qualify_vod,scan_vod,extract_frames}.py`, `src/capture/*`,
`tools/calibrate.py`. Mọi lỗi dưới đây đều đã sửa kèm test hồi quy. **405 → 501 test.**

#### Hai lỗi nguy hiểm nhất: cổng kiểm tra báo ĐẠT *vì* nó không kiểm được gì

**11a. `all([])` là `True`.** Mục "không viền đen" viết `all(c == want for c in crops if c)`.
Khi ffmpeg không chạy được thì cả ba lần dò trả `None`, biểu thức thành `all([])` → **True**.
Nghĩa là **một máy không cài ffmpeg sẽ báo "không viền đen: ĐẠT"**. Cổng chất lượng cho kết quả
tốt nhất đúng vào lúc nó mù hoàn toàn.

> Sửa: `letterbox_check` phân biệt *không đo được* với *đo được và sạch*. Thiếu dữ liệu ⇒ HỎNG,
> kèm lý do. Đo được 2/3 mốc cũng là HỎNG — đừng đoán nốt mốc còn lại.

**11b. `_cropdetect` không bắt `FileNotFoundError`.** Thiếu ffmpeg ⇒ traceback thô, và thông báo
nói về "file không tìm thấy" khiến người đọc tưởng là nói về file **video**.

#### Lỗi làm đánh trượt oan mọi bản tải VP9

**11c. WebM/VP9 không khai báo `bit_rate` ở mức stream.** Đo thật trên một file vp9: `streams[0]`
chỉ có `codec_name` và `avg_frame_rate`; bitrate chỉ có ở `format`. Bản cũ đọc mỗi stream ⇒
`0.0000 bpp` ⇒ **trượt**. Mà VP9/AV1 lại đúng là định dạng [mục 10](#10-rapidocr-pp-ocrv6-không-đọc-được-tiếng-việt-có-dấu--và-bitrate-thì-vô-can)
khuyên dùng — tức là cổng kiểm sẽ loại đúng những VOD tốt nhất.

> Sửa: `stream` → `format` → tự tính `size×8/duration`, và **ghi rõ nguồn** trong báo cáo.

#### Lỗi im lặng theo schema thư viện

**11d. `getattr(out, "txts", None)` đọc thẳng một schema.** `requirements.txt` ghim
`rapidocr>=3.9.2` **không chặn trên**. Bản 3.x trả `RapidOCROutput.txts`; bản 1.x/2.x trả tuple
`(result, elapse)`. Đọc thẳng một kiểu thì khi thư viện đổi schema, kết quả thành **rỗng im lặng**
— không lỗi, chỉ là tỉ lệ nhận diện tụt về 0 mà không ai biết vì sao.

> Thêm bẫy: `bool(RapidOCROutput)` là **False** khi không có chữ, nên `if out:` bỏ qua cả trường
> hợp hợp lệ. Sửa: `src/vision/preprocess.ocr_texts()` chịu được 7 dạng đầu ra đã biết.

#### Còn lại

| # | Chỗ | Vấn đề |
|---|---|---|
| 11e | `video_source._run` | `FileNotFoundError` khi thiếu ffmpeg → thông báo sai đối tượng |
| 11f | `video_source.meta` | File rác / chỉ có âm thanh → lỗi ffprobe thô, không nói được gì |
| 11g | `video_source.video_id` | Tên `"[]"` cho ra `""` → **mọi VOD đổ chung một thư mục** |
| 11h | `frame_source.format_ref` | Mốc âm cho ra `-1:59:59` — chuỗi *trông* hợp lệ, dẫn người đọc tới sai chỗ |
| 11i | `video_source._parse_fps` | `"60"` (không có dấu `/`) → `0.0` |
| 11j | `regions.to_pixels` | Vùng tỉ lệ nhỏ làm tròn về 0px → crop rỗng → cv2 ném lỗi khó hiểu ở tận sau |
| 11k | `regions.load` | YAML hỏng / thiếu khoá → `TypeError` trần, không nói vùng nào sai |
| 11l | `scan_vod.cmd_detect` | Chỉ kiểm `thumbs.npy`, không kiểm `times.npy`; lệch độ dài không ai bắt |
| 11m | `scan_vod` | Ảnh mẫu ở mốc ngoài video → `argmin` lặng lẽ lấy khung đầu/cuối |
| 11n | `extract_frames._rel` | `relative_to` **ném** khi `--out-dir` nằm ngoài repo — sập sau khi đã ghi file |
| 11o | `extract_frames`, `calibrate` | Bỏ qua giá trị trả về của `cv2.imwrite` → đĩa đầy = mất ảnh im lặng |

#### Tách phần dùng lại

Otsu + phóng to 6× (thứ biến `stage` từ trượt thành 3/3) đang nằm cứng trong `qualify_vod.py`.
Đã tách ra **`src/vision/preprocess.py`**: `binarize_for_ocr`, `hud_bar_present`, `ocr_texts`,
`ocr_join`, `has_digit` — mọi HUD reader về sau dùng chung một đường.

#### Một lưu ý cho người viết test sau

Nạp script bằng `importlib` mà script có `@dataclass` thì **phải** đăng ký vào `sys.modules`
*trước* `exec_module`: `dataclasses` tra cứu `sys.modules[cls.__module__]` và sẽ ném
`AttributeError: 'NoneType' object has no attribute '__dict__'`.

### 12. Chính sách reroll augment: bài toán dừng tối ưu, và ba con số suýt sai

Set 18 cho **mỗi ô augment một nút đổi riêng** — đã đối chiếu trên frame VOD thật
(`s7h-jHMpFmQ`, chặng 3-2): ba nút riêng, ba thẻ **cùng một bậc**, và **không có bộ đếm số**
nào trên màn hình. Điều cuối quyết định kiến trúc: số lượt còn lại phải được **truyền vào**,
không suy ra được từ một khung hình.

Toàn bộ phần "optimal stopping" sụp xuống còn **một phép so sánh** `g(R) − c > B`. Ba định lý
(đổi ô tệ nhất; đổi miễn phí thì trội hơn yếu; vùng dừng liên thông nên luật một bước là luật
tối ưu) nằm ở [docs/augment-reroll/](docs/augment-reroll/overview.md). Hệ quả: mọi độ khó thật
nằm ở hàm `Score`, **không** ở luật dừng.

**Ba chỗ suýt sai, đều bị phép đo bắt được:**

**(a) Bảng `c` lệch thang đo ~10×.** Các số 0,08 / 0,01 được đặt ra mà chưa đối chiếu với
thang đo thật của `Score`. Đo ra: `sd(Score)` trên một bậc chỉ **~0,05**, và tích phân đuôi
với thẻ dẫn đầu thực tế chỉ 0,002–0,009. Đọc bảng như **tuyệt đối** thì mọi ô đều lớn hơn mọi
lợi ích có thể có → **không bao giờ đổi thẻ**, trái hẳn ý đồ. Đọc như **bội của σ** thì đúng
những con số ấy lại rơi vào chỗ: gold dừng ở ~q97 (gần như luôn đổi), prismatic 2-1 dừng ở
~q85 (dừng khi đã có thẻ mạnh). Thêm `cost_unit: sigma`; nhờ vậy bảng **không phải hiệu chỉnh
lại** khi số liệu thật thay cho `MOCK-NOT-REAL`.

**(b) `evidence` suýt chặn hành động.** Bản thiết kế đầu định: số liệu chưa đáng tin thì
không phát ngưỡng, lui về xếp hạng thuần. Sai. `B` và `F_S` cùng sinh từ **một** hàm điểm,
nên phép so sánh giữa chúng **bất biến qua mọi hiệu chỉnh đơn điệu** — nó vẫn đúng khi `Base`
trung tính ở cả 254 augment. Từ chối trả lời là vứt đi một so sánh hợp lệ chỉ vì thiếu một
phép hiệu chuẩn tuyệt đối. Giờ `evidence` hạ giọng *câu chữ*, không hạ *hành động*.
Kèm theo: bộ số giả lập bịa `sample_n > 200` nên `is_evidence` trả True cho nó — phải nhìn
thêm tên nguồn (`is_fabricated`).

**(c) Vét hết lượt đổi KHÔNG hơn gì không đổi lần nào.** Đo n = 20.000: `exhaust_all`
+0,00010 với KTC ôm lấy 0. Lượt thứ ba bắt buộc đổi chính ô đang giữ thẻ tốt nhất, nên nó trả
lại gần hết phần lợi của hai lượt đầu. Chính sách tuần tự: **+0,01791** (gold), lấy được
**89,6%** khoảng cách tới trần biết trước.

**Còn một bẫy nhỏ đáng ghi:** nhánh tailoring chạy hai lần ra số **giống hệt nhau** vì trạng
thái thử dùng tên trait của set cũ (`Ravager`) — không khớp augment Set 18 nào. Hai kết quả
giống hệt là dấu hiệu của **nhánh chết**, không phải tham số vô hại. Với trait thật
(`DA_Primal18`): β=1 đổi 2,36 lần vs β=0 đổi 2,22 — đúng hướng đã dự đoán. Nhưng chỉ **20/254**
augment có `trait_affinity` (19 trong đó là gold), nên tailoring gần như không chạm silver và
prismatic.

Độ trễ: dựng pool 1,77 ms p95 (bậc lớn nhất), mỗi quyết định 0,014 ms p95 — **không cần** viết
lại bằng NumPy. Chấm cả 254 augment là 12,24 ms p95, vỡ ngân sách; luôn lọc theo bậc trước.

`ScenarioLogger` lên **schema 3** (thêm `reroll`). 501 → **575 test**.

### 13. w₁ chuyển sang tiên nghiệm chuyên gia — và cái bẫy khiến nó suýt vô hiệu

Chốt hướng: **bỏ hẳn** việc đi tìm số liệu placement thô. Không còn nguồn đo được nào (mục 2),
nên w₁ đứng trên **bảng tier do người chơi giỏi xếp**, với `ordinal_trust` nâng **0,35 → 0,65**.

**Cái bẫy — thả bảng tier vào repo cũng không đổi được gì.** `default_provider` xếp CSV → tier →
Null, và `CompositeProvider` trả về nguồn ĐẦU TIÊN có augment đó. Bộ số giả lập bịa sẵn
`sample_n > 200` nên `is_evidence` trả **True** cho nó, và nó phủ đủ **254/254** augment. Kết quả:
`ExpertTierListProvider` **không bao giờ được hỏi tới**, ở bất kỳ augment nào. Đo trực tiếp:

```
có mock CSV:  DA_18_BigGrabBag  source=MOCK-NOT-REAL            tier=-  is_ordinal=False
bỏ mock CSV:  DA_18_BigGrabBag  source=expert-tierlist:.../18.1 tier=S  is_ordinal=True
```

Không có gì báo. Test cũ chỉ hỏi *"file có tồn tại không"*, nên nó vẫn xanh.

Đã sửa: `default_provider(..., allow_fabricated=False)` là **mặc định** — dòng nào tự khai báo là
giả thì bị bỏ ngay lúc nạp; cả file đều giả thì nguồn đó không được tính là một nguồn. Công tắc,
không phải xoá file: `build_mock_stats.py` vẫn có lý do tồn tại.

> **Bài học**: `is_evidence` chỉ nhìn `sample_n`. Một con số bịa vẫn qua được cổng đó. Khi phải
> **xếp hạng các nguồn với nhau** thì phải nhìn cả `source` — nếu không, một cái giả sẽ thắng một
> ý kiến có người ký tên.

**Một phát biểu phải nói cho đúng.** Bảng tier được chọn vì **không còn nguồn đo được**, không phải
vì nó *ưu việt hơn* placement thô. Nhiễu kỹ năng (kiểu `Cruel Pact` bị dìm placement vì người chơi
kém hay lấy) là có thật, nhưng cách xử lý chuẩn là **lọc theo nhóm rank**, không phải bỏ phép đo.
Nói quá tay ở đây thì không bảo vệ được trước hội đồng. Vì thế `is_ordinal` / `is_evidence` giữ
nguyên, và `ordinal_trust` **không** đặt 1,0.

**Nguy cơ tự xác nhận ở §12.3.** Nếu w₁ *là* bảng tier của cao thủ mà §12.3 lại nhờ cao thủ đánh
giá advisor, thì một phần đồng thuận là **tạo ra sẵn**. Luận điểm chính chuyển sang dòng
`only("base")` của §12.4 — *"ngữ cảnh bàn cờ có đánh bại một bảng tier chuyên nghiệp không"* — vì
nó miễn nhiễm với vấn đề này, và vì lần đầu tiên nó là một câu hỏi thật thay vì *"context có hơn
nhiễu giả lập không"*.

Đo được: có bảng tier thì σ bậc gold 0,0546 → 0,0590 và `evidence` chuyển `uncalibrated` → `ordinal`;
`c` **tự co giãn** theo σ nên không phải hiệu chỉnh tay. 573 → **579 test**.

⏳ **Đang chờ**: `data/augment_tiers.json` chưa tồn tại. Đường ống xong, thiếu dữ liệu — xem
[docs/expert-prior/ingestion.md](docs/expert-prior/ingestion.md). *(Đã nạp 2026-09-15: TFT Academy,
patch 18.2, 246 lõi.)*

### 14. Probe client standalone: WGC chạy, HUD chậm khi game chạy

Client TFT standalone: cửa sổ `'TFT  '`, lớp `UnrealWindow`, borderless 1920×1080. Probe phải dò
cửa sổ bằng liệt kê (`bd6e3bf`) và gắn thread vào desktop `Default` khi chạy trong shell sandbox
(`33200ed`). Kết quả ở `data/live_probe/20261013_*`, `20261015_*`.

| Mục | Kết quả |
|---|---|
| WGC | Không hộp thoại, không viền vàng, ~49,9 fps, khung đầu 0,4–0,9 s |
| HUD ván Normal, máy rảnh (10-13) | Đúng cả 7 trường, ~1,1 s |
| Màn chọn lõi ván đấu máy (10-13) | Nút đổi lõi đúng; stage, máu rỗng vì bố cục khác (lõi ở 1-5, 2-5) |
| Màn chọn lõi 4-2 ván Normal (10-15) | Stage `4-2` đúng; nút `disabled / active / active` đúng với ảnh. Thanh HUD ẩn nên vàng, cấp, máu rỗng |
| HUD khi game chạy (10-15) | **15–26 s** ở các lần đọc sau khi OCR đã nạp; CPU 97% trong ảnh. Mất stage hoặc máu ở 2 lần |

Màn chọn lõi 2-1, 3-2, 4-2 cùng bố cục, nên probe 4-2 thay cho 2-1. Hai việc còn mở: độ trễ HUD
khi game chạy, và giữ vàng/cấp/máu từ khung trước khi màn chọn lõi ẩn thanh HUD.

### 15. Replay trên 6 ván development: 4 lỗi sửa, 2 thứ trông như lỗi nhưng không phải

2026-11-06. Đổi tên 10 video tự quay thành `minh_01`…`minh_10` (tên gốc ở `rename_log.tsv`) và
chốt `data/eval/split.json` **trước** khi chạy bất cứ thứ gì: seed `20260930` bốc 6 development
`minh_03`–`minh_08`; held-out = `minh_01, 02, 09, 10` + `dat_02–05`; `dat_01` sang development
(ghi `note`). Rồi chạy replay + overlay (Gemini) không cửa sổ trên 6 ván development, 18 màn chọn lõi.

| # | Triệu chứng | Nguyên nhân | Sửa |
|---|---|---|---|
| 1 | Overlay khoanh ô 1 "U.R.F" nhưng lý do nói đổi Seraphim (ô 2); có lúc "CHỌN Ô 1 · chưa đọc được" | `LiveSession` bỏ ô chưa đọc khỏi `choices` → chỉ số bị dồn; `choice_index`, lượt đổi theo ô và `target_slot` đều theo danh sách dồn, overlay hiểu là ô màn hình | `AugmentChoice.slot`; `rank()` dùng nó làm `choice_index` |
| 2 | Stage 2-1 ở màn 3-2 (3/18 màn), vàng/cấp của màn trước | (a) tracker bỏ phiếu đa số cho cả stage — màn mở ngay đầu vòng nên lịch sử toàn vòng cũ; (b) HUD chỉ đọc ngoài màn, mà nút mốc tua tới `open_s − 1 s` (đã ở trong màn); (c) tua tới xa vẫn giữ HUD của 10 phút trước | Stage lấy giá trị mới nhất; vào màn thì đọc **riêng stage** (màn che vàng/cấp/máu, không che stage); tua tới > `grace_s` thì xoá HUD (giữ số ván); nút mốc tua `open_s − 10 s` (5 s rơi vào hiệu ứng chuyển vòng, HUD ẩn — `minh_07` 4-2) |
| 3 | Máu 8 khi thật là 87 | `HP_BOX` mép phải 0,945 (x=1814) cắt nửa chữ số thứ hai (kết thúc x≈1818) | 0,950. Quét 0,945/0,950/0,955 trên 607 khung (7 ván dev, mỗi 20 s): đọc một chữ số 48/14/16, máu "tăng" vô lý 17/4/8 |
| 4 | Gemini 3,3 s trung vị, **20,9 s** tối đa dù timeout 12 s | `with ThreadPoolExecutor` → `shutdown(wait=True)` chờ lượt gọi treo xong; mỗi lần gọi tạo `genai.Client` mới (lần đầu 3,07 s, các lần sau ~1,9 s) | Bỏ `with`, `shutdown(wait=False)`; giữ client. `thinking_level=minimal` không đổi gì (1,95 s vs 1,98 s); `thinking_budget=0` bị API từ chối |

| Chỉ số (6 ván, 18 màn) | Trước | Sau |
|---|---|---|
| Stage đúng | 15/18 | 18/18 |
| Máu < 10 (sai) | 3 | 1 |
| Khuyến nghị trỏ vào ô chưa đọc | 9 | 0 |
| Gemini đọc lõi: trung vị / p90 / max | 3,3 / 4,2 / 20,9 s | 2,2 / 2,9 / 4,2 s |

Số "sau" đo với mốc tua 10 s (bản 5 s để `minh_07` 4-2 ra vàng 0, cấp 1; giờ 56, 7, máu 69).

Máu vẫn chưa ổn: `minh_08` 3-2 đọc 2; `minh_04` và `minh_06` 4-2 đọc 100 sau khi màn trước đã là
73 và 87 — máu không bao giờ tăng, nên có thể chặn bằng luật đơn điệu, chưa làm. `dat_01` (16:10)
4-2 vẫn đọc stage `4-1`: lỗi chữ tối đã biết ở 16:10, không phải lỗi bỏ phiếu.

**Không phải lỗi:**

- **Khuyên ĐỔI 42/64 lần với lợi +0,00.** Đúng thiết kế: đổi ô *kém nhất* không bao giờ làm mất lõi
  tốt nhất ([dominance-theorem](docs/augment-reroll/dominance-theorem.md)), và `cost_matrix` ở
  stage 2–3 chỉ 0,01σ. Lỗi là cách hiện: lợi 0,004 làm tròn thành "+0,00". Giờ hiện
  `không mất gì · lợi kỳ vọng +0.004` khi lợi < 0,01.
- **Nhiều lõi đúng 0,50.** `base` lấy từ bảng tier (bậc A = 0,50) vì `augment_stats.csv` vẫn là
  `MOCK-NOT-REAL` (xem Nợ kỹ thuật); lõi không gắn tộc, không kinh tế, không trang bị thì bốn thành
  phần còn lại cũng trung tính. Hệ quả: các lõi bậc A không phân biệt được với nhau — giới hạn dữ
  liệu, phải nói rõ trong báo cáo.

Còn mở: phần `body` trong JSON Gemini chiếm phần lớn token đầu ra nhưng chỉ được truyền qua — bỏ
đi có thể nhanh hơn, chưa đo. Test 1043 → 1067.

### 16. Directional augment đổi thiết kế: gợi ý theo từng hướng, không đoán hướng

2026-11-13 → 11-14. Thiết kế: [plan-conditioned-advice](docs/directional-augment/plan-conditioned-advice.md).

**Hai ngõ cụt trước khi chốt.**

| Cách | Vì sao bỏ |
|---|---|
| Lấy hướng từ `CompSelector` | Chưa có bộ đọc bàn cờ → `state.board` rỗng → `evidence = 0` → directional luôn tắt, delta held-out = 0 |
| Suy hướng từ HUD ở mốc 3-2/3-6/4-2 | Ở 4-2 cả 5 ván dev đều cấp 7, 53–80 vàng. fast8 và fast9 khác nhau ở chỗ **roll ở cấp 8 hay cấp 9**, mà điều đó chỉ thấy được sau 4-2 |

Bảng "vàng sau khi lên 8" ghi ở next-steps hôm 11-13 là số giả định: lấy vàng trừ thẳng phần XP còn thiếu. Nó sai với cách chơi thật. fast9 giữ lợi tức: lên 8 bằng phần vàng dư trên 50, rồi lên thẳng 9, thường sau 4-4. Lên 9 ngay ở 4-2 cần 2 lõi kinh tế rất mạnh và một chuỗi dài.

**Quyết định (người chơi, từng Thách Đấu VN ~#400).**
- Hệ thống không đoán hướng. Mỗi màn, **từ 2-1**, hiện lõi tốt nhất cho từng hướng, và người chơi tự chọn dòng của mình.
- Chốt hướng sớm, kèm một đường lui dự phòng, là chiến thuật đáng hỗ trợ. Ba lõi bổ trợ nhau thì càng mạnh.
- 2-1 không phạt. Game state chỉ để hiểu game và để cảnh báo.

Luật combat/eco do người chơi đưa ra:
- Mạnh nhất là **3 lõi combat cộng full bài** (core 2 sao, hoặc 3 sao với bài reroll).
- 3 lõi combat chỉ cần **full form** (đủ đội hình, 1 sao). 3 lõi eco thì phải full bài mới mạnh.
- 3 lõi combat vẫn fast 9 được nếu đủ tiền và máu. `minh_03` là ví dụ: fast9, cả 3 lõi `econ_value 0`.
- Hệ quả: loại lõi **trực giao** với hướng.

**Triển khai.** Không thêm trường mới. Ban đầu tôi đề xuất trường `kind`, người chơi chỉ ra `categories` (econ/combat/trait/item/utility/reroll) đã có sẵn và đã duyệt tay, nên bỏ đề xuất đó.

| Phần | Nội dung |
|---|---|
| `scoring/plan_fit.py` | `PlanFitScorer(a, state, plan, held)`. eco = `econ_value > 0` hoặc có `econ`/`reroll`; power = có `combat`/`item`/`trait`. Điểm = 0,5 + `eco`×sức mạnh + tổng `econ_type` theo hướng + `power` + **nợ sức mạnh**: mỗi lõi chỉ-eco đã cầm cộng `debt_bonus` 0,05 cho lõi chỉ-combat. Câu lý do nêu cái giá: *"lõi kinh tế: phải lên full bài mới mạnh"* / *"lõi combat: full form là đủ"*. Dưới `min_hp` chỉ cảnh báo, không đổi điểm |
| `AugmentAdvisor.rank_by_plan()` | Mỗi hướng: tổng `rank()` + w × (plan_fit − 0,5). Các hướng ra cùng một lõi được gộp thành một dòng (`PlanLine`). **`rank()` không đổi một byte**, đó là dòng đối chứng ablation |
| `config/scoring_weights.yaml` `tuning.plan_fit` | 4 hướng: `fast9`, `fast8` (gồm route `standard`), `reroll` (reroll1/2/3), `cash` (thiếu tiền). Mọi số là giả định tiên nghiệm, chưa fit. `enabled: false` cho tới khi nối overlay |
| `scripts/eval_plan_advice.py` | Lấy offer cuối mỗi màn verified, lõi đã cầm đưa vào `state.augments`, dữ liệu theo `data_patch` của video. So top-1 khi tắt (`rank()`) và khi bật (dòng của `plan.route`) với `picked` |

**Kết quả trên dev (5 ván, 15 màn; chỉ để chỉnh, không báo cáo).** Top-1 khớp lựa chọn người chơi: **tắt 6/15 → bật 8/15**. Cả hai lần tăng đều ở `minh_05` (fast9): 3-2 Slammin'+ (gold+xp) và 4-2 Invested++. Không có màn nào đang khớp mà bật thành sai.

Các màn vẫn trượt cho thấy luật còn thiếu. Chưa sửa vì 15 màn quá ít, chỉnh theo chúng là overfit:

| Màn | Thấy gì | Câu hỏi cho người chơi |
|---|---|---|
| 2-1, 4/5 ván | Mọi hướng ra cùng lõi, và trượt | 2-1 do `base` (bảng tier) quyết. plan_fit không tách được lõi combat với lõi combat |
| `minh_04` 4-2 (reroll1) | Dòng Reroll → Money Monsoon (eco). Người chơi lấy Baron's Lair (combat) | Ở 4-2 bài reroll 1 vàng đã roll xong, nên eco hết giá trị. Trọng số hướng có nên đổi theo stage không? |
| `minh_06` 4-2 (fast8) | Dòng fast8 → Glass Cannon. Người chơi lấy Booster Pack++ (gold) | fast8 lấy eco ở 4-2 vì cần tiền để roll ở 8? |
| `minh_03` 2-1 (fast9) | Dòng fast8 ra đúng Seraphim, dòng fast9 thì không | Đúng luật #2: lõi combat vẫn fast 9 được. Nhãn `route` là hướng của cả ván, không phải của màn đó |

**Vòng 2 (11-14), sau khi người chơi giải thích hai màn trượt.**
- `minh_04` 4-2: đã full core 3 sao, hai lõi trước nặng eco nên đủ eco mà thiếu combat. Lúc đó còn thiếu đồ tank, và Baron's Lair là lõi combat mạnh.
- `minh_06` 4-2: lõi 1 là combat mạnh làm bàn đạp, nên cần eco để lên full bài ở 8. Lý do lớn hơn là **combo**: Booster Pack++ trả quà bằng orb, còn Bonus Gifts+ (lõi 2) có tỉ lệ cho thêm orb 3 vàng.

Hai luật thêm vào:
- **Cân bằng hai chiều.** `debt` = số lõi chỉ-eco đã cầm − số lõi chỉ-combat đã cầm. Lệch về eco thì lõi combat được cộng; lệch về combat thì lõi eco được cộng.
- **`by_stage`**: một hướng có thể đổi trọng số từ một stage nào đó. Hướng reroll từ stage 4 dùng eco −0,10, power +0,20.

Kết quả: **tắt 6/15 → bật 9/15**. `minh_04` 4-2 ra đúng Baron's Lair. Đây là **số trong mẫu**: luật `by_stage` được rút ra từ chính màn này, nên con số chỉ cho thấy luật chạy đúng, không phải bằng chứng nó tổng quát được.

`minh_06` 4-2 vẫn trượt, như dự đoán: luật chung không biết combo. Cần một **bảng combo lõi** (việc B). Kiểm cũng lộ ra một lỗ hổng: lúc chơi thật **không gì ghi `state.augments`**, chỉ script đánh giá điền từ nhãn. Như vậy luật cân bằng và combo chưa chạy trên overlay. Lõi đã chọn có hiện trên client: một dải icon khoảng 37 px ở hướng 10 giờ so với tâm màn hình (x≈511, y≈245 ở 1080p), xếp trái sang phải theo thứ tự chọn và nở ra hai bên. Cách đọc dự kiến (việc A): khi màn chọn lõi đóng, so icon mới nhất trong dải với icon CDragon của 3 lõi cuối được chào. Test → 1105.

Giới hạn phải ghi trong báo cáo: `picked` là lựa chọn của **một** người chơi, nên phép đo là độ khớp với chuyên gia, không phải độ chính xác. Số báo cáo lấy từ held-out (video 18.6). Test 1092 → 1103 (`tests/test_plan_fit.py`, 11 ca).

### 17. Đọc lõi đã chọn từ dải icon: 15/15 trên dev, nhờ icon cắt từ chính thẻ lõi

2026-11-14. Việc A của [implementation-plan](docs/directional-augment/implementation-plan.md). Trước bản này, khi chơi thật `state.augments` luôn rỗng. Luật cân bằng và combo của §16 chỉ chạy được trong script đánh giá, vì script tự điền lõi từ nhãn.

**Dải icon.** Người chơi chỉ ra vị trí: hướng 10 giờ so với tâm màn hình. Các thông số đo trên 15 màn dev:
- Mỗi icon khoảng 37 px trên nền đen. Cả dải canh giữa quanh x≈511, y≈245 ở 1080p, xếp trái sang phải theo thứ tự chọn, nở ra hai bên khi có thêm icon.
- Bản 16:10 (`dat_01`) lệch trái khoảng 100 px so với phép neo giữa, nên vùng tìm được đặt rộng.
- Vị trí giữ nguyên cả khi camera đang ở bàn người khác. Lúc đó dải hiện là của **họ**.

| Phần | Nội dung |
|---|---|
| `src/vision/held_augments.py` | `find_strip`: lọc pixel tối (≤ 40), đóng hình thái, rồi tìm khối cao 0,026–0,044×H, tỉ lệ ≈ số nguyên, độ lấp ≥ 0,70. Icon bạc đo được 0,82–0,84, nên ngưỡng 0,85 ban đầu làm trượt `minh_04` và `dat_01`. `classify`: tương quan chuẩn hoá trên ảnh xám 32 px, cắt viền 10%, **chỉ giữa các lõi vừa chào**. Cần khớp ≥ 0,35 và cách ứng viên kế tiếp ≥ 0,08 |
| `HeldAugmentTracker` | `offer_seen` (trong màn: ứng viên, stage, icon thẻ) → `observe` (ngoài màn: số icon **tăng** và icon mới nhất khớp thì ghi). Lọc ứng viên theo `offer_rounds` của stage để tách bản +/++, như người chơi gợi ý. Bỏ lỡ đoạn trước (mở app giữa ván, tua video) thì các ô trước ghi `None`. Hết 120 s mà chưa chắc cũng ghi `None`, không đoán |
| `LiveSession` | Trường tuỳ chọn `held_tracker`, đưa `known` vào `state.augments`, reset khi sang ván mới. Replay luôn bật |
| `scripts/fetch_augment_icons.py` | Tải icon CDragon về `data/augment_icons/` (dự phòng). CDragon trả 403 với User-Agent mặc định, mỗi request mất khoảng 20 s, chạy song song thì bị 522. Kết quả: 213/252 icon (1,7 MB); 39 lõi lần nào cũng 522, 6 lõi không có trường `icon`. Thiếu không sao, vì đây chỉ là dự phòng |
| `scripts/eval_held_augments.py` | Mô phỏng vòng đời trên video. Ứng viên lấy từ nhãn, nên script chỉ đo bộ đọc dải icon |

**Kết quả trên 5 ván dev, 15 màn:**

| Nguồn mẫu so sánh | Đúng | Chưa rõ | Sai |
|---|---|---|---|
| Chỉ icon CDragon | 11 | 3 | **1** (`dat_01` 3-2 → Healing Orbs II, khớp 0,40) |
| Icon cắt từ thẻ, lấy ở `at_s` của lần chào cuối | 9 | 6 | 0 |
| **Icon cắt từ thẻ ngay trước khi màn đóng, lấy điểm cao hơn giữa thẻ và CDragon** | **15** | 0 | 0 |

- **Icon CDragon không trùng với icon trong game.** Bonus Gift+ trên CDragon là chữ "T", trong game là đồng xu "?". Invested++ cũng lệch, điểm khớp chỉ 0,26. Icon cắt từ chính thẻ lõi trên màn chọn (`card_icon`, đo trên 1080p, 16:10 và thẻ kim cương) khắc phục được việc này: ví dụ trên khớp 0,83 và cách lõi kế tiếp 0,52.
- **Lấy mẫu ở `at_s` thì rơi vào hiệu ứng lật thẻ sau khi đổi lõi.** Trong live, mỗi lần đọc thẻ đều đã chờ thẻ ổn định (`stable_frames`), nên lần cắt cuối nằm ngay trước khi màn đóng.
- Màn khó nhất là `dat_01` 3-2: khớp 0,62, cách lõi kế tiếp 0,215. Lõi được ghi nhận khoảng 2 s sau khi màn đóng.

Giới hạn: đây là 15 màn dev, ứng viên lấy từ nhãn. Khi chơi thật, nếu đọc thẻ sai thì bộ đọc dải sẽ chỉ ra "chưa rõ", không ra sai, vì icon không khớp ứng viên nào. Chưa kiểm trường hợp đầu ván chỉ được chọn 1 trong 2 thẻ. Test 1105 → 1119.

### 18. Hiện gợi ý theo hướng: replay, overlay trên video, panel trong trận; nâng UI kiểu Blitz

2026-11-14. Việc D của [implementation-plan](docs/directional-augment/implementation-plan.md). Người chơi đề nghị: "nâng cấp UI replay và cả HUD, đẹp như Blitz". Ảnh: [trước](docs/directional-augment/img/replay-before.png) · [sau](docs/directional-augment/img/replay-plan-advice.png) · [panel trong trận](docs/directional-augment/img/ingame-panel.png).

| Phần | Thay đổi |
|---|---|
| `Advisor.advise` | `plan_fit.enabled` (nay là **true**) thì gọi `rank_by_plan` và gắn vào `AdviceBundle.plans`. Gọi qua `_safe`, hỏng thì bảng xếp hạng vẫn hiện |
| `AdviceReady.card_icons` | Icon cắt từ thẻ ngay ở khung vừa đọc thẻ (thẻ đã ổn định). Dùng làm mẫu cho dải lõi đã chọn và làm icon để vẽ |
| Replay: dải trạng thái | Chip (VÒNG / CẤP / VÀNG / MÁU / CHUỖI / ĐỔI THẺ): nhãn viết hoa nhạt, giá trị đậm, số chưa đọc tô màu cảnh báo. Thêm hàng **LÕI ĐÃ CẦM** bằng icon. Cảnh báo gộp **một dòng** "▲ cái đầu (+n)", đủ danh sách nằm ở tooltip |
| Replay: khối mới **THEO HƯỚNG ĐI** | Mỗi dòng: viên màu theo hướng (gộp nhiều hướng thì xếp dọc) → icon + "Ô n · tên" + nhãn **KINH TẾ** "cần full bài" / **COMBAT** "full form là đủ" + cảnh báo máu |
| Replay: icon | `IconTile` vẽ icon thật, bo góc, viền theo độ hiếm, **khiên bậc** góc dưới (mẫu huy hiệu Blitz). Nguồn: CDragon, thiếu thì lấy icon cắt từ thẻ, thiếu nữa thì chữ cái |
| Overlay trên video | Viên hướng **neo ngay dưới ô chữ của thẻ** được chọn cho hướng đó (mẫu Blitz: đặt thông tin trên thứ nó giải thích) |
| Panel trong trận (`augment_panel`) | Nền kính tối bo góc 10 px, viền sáng mảnh; dòng theo hướng kèm viên màu; lý do dài thì cắt "…" |
| Màu hướng | Cố định qua mọi bảng màu, trùng nhau ở replay và panel trong trận: vàng = lên 9, đỏ = đánh ngay ở 8, ngọc = reroll, xanh lá = thiếu tiền |

**CDragon có icon giữ chỗ.** 41 lõi trỏ về `hexcore/missing-t1|t2|t3.tex`, một hình chữ "T" dùng chung, ví dụ Bonus Gift+ và Là Ta Đây. `fetch_augment_icons.py` giờ bỏ qua và xoá các icon này, còn 172 icon thật. Đọc lõi đã chọn vẫn 15/15, vì mẫu chính là icon cắt từ thẻ.

**Vòng 2 của UI (người chơi: "vẫn xấu lắm", đề nghị dùng skill ui-ux-pro-max).**
- Skill gợi ý style và typography cho gaming. Lấy Chakra Petch (kiểu esports, có dấu tiếng Việt) cho tiêu đề và số. Bỏ gợi ý tím neon và 3D, vì kiểu đó dành cho trang landing, không hợp overlay dữ liệu.
- Chữ thân dùng Be Vietnam Pro. Cả hai font đóng gói ở `assets/fonts` kèm giấy phép OFL, nạp bằng `theme.load_fonts()`.

| Phần | Thay đổi |
|---|---|
| Bảng màu `arena` (mặc định) | Nền than lạnh `#0a0d13`; ngọc `#2ee6c5` cho số liệu và CHỌN; vàng `#f5b544` cho bậc S và ĐỔI; viền 6% trắng; bo góc 10 px |
| Thẻ kết luận | Icon 64 px; nhãn hành động đặc (CHỌN/ĐỔI) và "Ô n"; tên lõi 24 px Chakra Petch; viên chênh lệch. Lý do rút còn câu đầu, bỏ chú thích nguồn `[...]`; bản đầy đủ ở tooltip |
| Thẻ ô | Icon 56 px có khiên bậc; hạng `#n` lớn; thanh điểm liền thay 6 chấm; tối đa 2 lý do, phần còn lại ở tooltip; nền gradient nhẹ theo màu bậc |
| Khung cửa sổ | Thanh đầu có chữ "TFT ADVISOR"; nút viền mảnh; nút Phát đặc màu ngọc; slider ngọc; panel phải cuộn được |
| Panel trong trận | Cùng bảng màu và font; dòng hành động có viền theo màu hành động; dòng hạng bo góc với điểm canh phải |

Lỗi gặp khi làm: tên font có dấu nháy đơn làm vỡ thuộc tính `style='...'` trong rich text, nên font không áp dụng. Sửa bằng `theme.DISPLAY_HTML`.

Chưa kiểm: ảnh chụp chỉ ở một màn (`minh_06` 4-2), tua thẳng tới đó nên hàng lõi đã cầm còn trống. Panel trong trận mới chạy qua `demo_overlay.py`, chưa chạy trong một ván thật. Test 1119 → 1126 (`tests/test_plan_display.py`).

### 19. Vỏ live: overlay ngay trong trận (`run_live.py`)

2026-11-14, bắt đầu hàng 4 của kế hoạch đã duyệt ("nhận diện và gợi ý thời gian thực, overlay"). Trước đó mọi thứ chỉ chạy trên video replay; panel trong trận mới chạy qua `demo_overlay.py` với tình huống viết tay.

| Phần | Nội dung |
|---|---|
| `src/capture/game_window.py` | Tìm cửa sổ game (tiêu đề `TFT  ` + lớp `UnrealWindow`, rút từ probe 10-13), toạ độ vùng client trên màn hình |
| `src/capture/wgc_source.py` | Chụp **theo cửa sổ game** bằng WGC (`windows-capture`, `window_hwnd`), chỉ giữ khung mới nhất, cắt viền khi game chạy ở chế độ có cửa sổ. Không lấy overlay của chính ta, nên không cần `WDA_EXCLUDEFROMCAPTURE` |
| `src/live/runner.py` | `AnalysisLoop`: luồng riêng, tối đa `fps` lần/giây, mỗi lần lấy khung mới nhất cho `LiveSession.step`; khung cũ bị bỏ; lỗi một khung không làm chết vòng lặp. `VideoClockSource` phát video theo đồng hồ thật để thử khi không có game |
| `src/overlay/live_window.py` | Cửa sổ trong suốt, click xuyên qua, phủ khít vùng client. Dùng **cùng bộ vẽ** với overlay trên video của replay (huy hiệu, viền ô, viên hướng, widget kết luận), cộng nền tối sau widget kết luận vì không có pixel game để làm mờ |
| `LiveSession.screen_visible` | Màn chọn lõi có đang hiện ở khung vừa xử lý không. `LiveSession` chờ 30 s mới coi là rời màn (để giữ lượt đổi khi người chơi ẩn màn), nên trước khi có cờ này overlay vẫn vẽ huy hiệu lên bàn cờ sau khi màn đã đóng |
| Log độ trễ | `data/live_logs/<phiên>.jsonl`: thời gian từng bước, đọc thẻ, đọc HUD. In tóm tắt khi thoát |

Lỗi gặp khi làm: luồng phân tích và luồng giao diện cùng đọc video OpenCV, gây `Assertion fctx->async_lock failed` (libavcodec). Sửa bằng khoá trong `VideoClockSource`.

Thử trên `minh_06` 4-2 ở chế độ mô phỏng: overlay đúng vị trí, tắt khi màn đóng; đọc HUD trung vị 41 ms sau lần đầu (1,5 s, do nạp OCR) trên máy rảnh. **Chưa chạy với game thật**: cần chạy trên máy chơi để đo độ trễ HUD khi game chạy (trước đây 15–26 s), kiểm toạ độ khi Windows scale ≠ 100%, và xem Vanguard có phản ứng gì không. Test 1126 → 1135 (`tests/test_live_shell.py`).

## Dự kiến triển khai

### Chặn mọi thứ — Track B, Phase 0 (§7)

Phải chạy trên máy đang mở TFT thật. *(Trạng thái 2026-10-15: #1–#3 đã chạy, xem mục 14; #0, #4
chưa có ghi nhận.)*

| # | Việc | Chi phí | Quyết định điều gì |
|---|---|---|---|
| **0** | **Kiểm tra đủ điều kiện Vanguard On-Demand** — Win11 25H2+, Secure Boot, TPM 2.0, IOMMU, VBS, HVCI | 10', **không cần mở game** | Nếu đủ → driver chỉ nạp lúc chơi, không nằm thường trú từ lúc boot. Là biện pháp giảm phơi nhiễm duy nhất có sẵn, và Riot chính chủ cho phép. Chỉ ~35% máy đủ điều kiện. **Làm trước mọi thứ khác** ([testing-protocol](research/vanguard/testing-protocol.md)) |
| 1 | `tools/probe_environment.py` — build Windows, process/window class, borderless | 30' viết + 10' chạy | Mốc so sánh cho client 2026-10-09. **Không ghi bây giờ thì mất vĩnh viễn**. Chạy lúc game ĐÓNG trước, mở sau |
| 2 | Chụp 1 frame → assert không đen | 10' | Riot có bật capture protection không. Chưa ai chạy trên 18.1 |
| 3 | Benchmark RapidOCR khi game đang chạy | 30' | Mọi số latency hiện có đều đo trên máy rảnh |
| 4 | `GET 127.0.0.1:2999/liveclientdata` trong trận | 5' | Có bỏ được level/HP khỏi pipeline vision không |

### Phase 1–3 — Vision (sau Phase 0)

`preflight.py` → `screen_capture.py` → `tools/calibrate.py` → `session_detector.py` →
`augment_reader.py` (Gemini Vision primary) → champion/item/trait recognition.

> Recognizer trả `apiName` + confidence và **không chấm điểm**. Cầu nối OCR → `apiName` đã có sẵn
> (`name_index.py`), scoring engine không phải đổi một dòng.

### Phase 6 — Kết quả (cần dataset)

Gán nhãn 200–500 frame → chạy `run_evaluation.py` → viết chương kết quả. Harness sẵn sàng, chỉ
thiếu dữ liệu. **Tier 5**: nhờ 3–5 người chơi rank khá đánh giá ~50 scenario lấy Cohen's κ.

> 💡 **Việc này KHÔNG cần game chạy.** Quay vài ván bằng OBS **Display Capture** (tuyệt đối không
> Game Capture — nó inject hook DLL và đã có tiền lệ hỏng với League), rồi gán nhãn toàn bộ trên bản
> ghi. Đây là phần việc lớn nhất còn lại của dự án và nó chạy hoàn toàn offline.
>
> ⚠️ **Cảnh báo phương pháp cho §12.1**: frame từ bản ghi *hoặc* từ capture card đều bị chroma
> subsampling + nén lại — làm hỏng đúng thứ chữ nhỏ mà OCR cần. Số đo trên đó sẽ **thấp hơn có hệ
> thống** so với chụp cửa sổ trực tiếp. Phải ghi rõ mỗi số đo lấy từ đường nào, nếu không luận văn sẽ
> lẫn *"OCR của ta yếu"* với *"bàn thử của ta nhiễu"*. Điều này có lợi khi bảo vệ: rig an toàn nhất
> cho ra con số **thấp hơn thực tế**, tức là sàn chứ không phải ước lượng.

### Deadline bên ngoài — 2026-10-09

Client TFT standalone. Khả năng đổi process name / window class → vỡ window targeting và overlay
owner-window. PBE báo cáo ~09-09. **Đây là lý do việc #1 ở trên phải làm sớm.**
*(Đã qua. Client mới đổi cửa sổ thành `'TFT  '` / `UnrealWindow`; probe đã sửa theo, xem mục 14.)*

---

## Nợ kỹ thuật đã biết

| Vấn đề | Ảnh hưởng |
|---|---|
| `augment_stats.csv` giả lập | Không trích được vào báo cáo. Đã loại trừ ba nguồn ngoài (09-02) — chỉ còn chờ Riot trả lại trường |
| `tactics_tools_stats.json` chưa có ai đọc | Số unit/trait/item đã đo được nhưng chưa nối vào `item_advisor` / `board_fit`. Nối vào là thêm một đường ảnh hưởng chưa đo được trong ablation |
| Cỡ mẫu vn2 nhỏ (2 challenger / 160 apex) | Số đội hình mang bất định. Crawl lại gần deadline sẽ tốt hơn |
| Riot Personal Key hết hạn 24h | Mỗi lần crawl phải lấy key mới |
| `roll_odds.py` chưa có importer nào | Đã gắn nhãn `Unverified Data (Set 18.1)` nhưng chưa nối vào `rules_engine` |
| `styles.py` không ai import | `augment_panel` hardcode lại cùng giá trị — theme bị nhân đôi |
| `role` tướng CDragon Set 18 bị rỗng 63/65 tướng | **Đã tìm được nguồn thay thế (2026-09-18):** datatft.com công bố đủ 12 role cho cả 65 tướng. Chưa nạp — xem [`research/unit-roles.md`](research/unit-roles.md) để biết cách crawl và ba việc cần làm |
| Checkbox SPEC §7 lỗi thời | Nhiều mục Phase 1–3 đã xong nhưng chưa tick |

---

## Liên quan

[`SPEC.md`](SPEC.md) — đặc tả v3 · [`README.md`](README.md) — cài đặt & cảnh báo dữ liệu ·
[`research/`](research/overview.md) — báo cáo nghiên cứu ·
[`research/vanguard/`](research/vanguard/overview.md) — đánh giá rủi ro Vanguard + quy trình test ·
[`claude_feedback.md`](claude_feedback.md) — quyết định Tier 1–5
