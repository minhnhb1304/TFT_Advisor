# Core Items

Bước I0 + I3.1: thống nhất tên đồ, bảng đồ core, suy vai trò. Cách ItemFit dùng bảng: [plan-item-fit](plan-item-fit.md). Thuộc [item-reading](overview.md).

## Luật chia đồ (ý của bạn, 2026-11-17 — coi là chuẩn)

- Đồ mỗi ván có hạn, nên một đội hình bình thường có **4 vai**: **carry chính, carry phụ, tank chính, tank phụ**. Nhiều đồ và nhiều nguồn sát thương thì mới có 3–4 carry.
- Dồn đồ đẹp nhất cho **carry chính**; carry phụ dùng món thừa. Tank cũng vậy.
- **Carry phụ thường cầm đồ hiệu ứng**: giảm hồi máu (Red Buff, Morello), trừ giáp (Last Whisper), trừ kháng phép (Void Staff). Aphelios phụ cầm Last Whisper + Red Buff (3/3 comp TFT Academy); Morgana cầm Morello + Void Staff (9/9).
- **Core gắn với (tướng, vai)** và có thể có **nhiều bộ thay thế**, vì tính chất đội hình đổi thì bộ mạnh nhất đổi. Một bộ có thể **đúng nhưng không tối ưu** ở meta hiện tại.

Các tướng dưới đây chỉ là **ví dụ minh hoạ** luật. Luật phải áp cho **mọi tướng và mọi bộ đồ**, nên bảng core được **sinh bằng thuật toán** (I3.1), không gõ tay theo ví dụ. Các ví dụ này dùng làm **test** cho thuật toán:

| Ví dụ (vai carry chính) | Thuật toán phải ra |
|---|---|
| Tristana, Kayle | Một bộ: Guinsoo |
| Aphelios | Hai bộ thay thế: Guinsoo / IE + Kraken |
| Ahri | Găng + Shojin. Nếu Nashor có trong dữ liệu (TFT Academy không có, tactics.tools có thể có) thì Găng + Nashor xếp dưới |
| Aphelios carry phụ | Last Whisper + Red Buff (đồ hiệu ứng) |

- **Tank không có core.** Đồ tank chọn theo độ mạnh của meta. Gargoyle Stoneplate đứng đầu bậc S ở bảng đồ TFT Academy nên tank nào cũng lắp: đó là đồ quá mạnh, **không phải core**. Trong 79 tướng cầm ≥ 2 đồ tank ở `finalComp`: Warmog 66, Gargoyle 44 (trên 16 tướng tank khác nhau).

## I0. Sửa lệch tên trước (lỗi có sẵn)

`ItemFit` và `BoardFit` dùng tên rút gọn (`BFSword`), còn `item_recipes.json` dùng `DA_Component_BFSword`. Bộ đọc trả apiName CDragon nên **ItemFit sẽ không bao giờ khớp** nếu không sửa. Gom về một hàm chuẩn hoá (đã có `comp_signals.component_type`). Kiểm bằng test hiện có + test mới với tên `DA_…`.

## I3.1. Dữ liệu

**`data/core_items.json`**: mỗi (tướng, vai) là danh sách **bộ thay thế**; đủ một bộ là đủ core. `weight` < 1 cho bộ đúng nhưng không tối ưu ở meta này.

```json
{"DA_18_Aphelios": {"carry": [{"items": ["DA_GuinsoosRageblade"]},
                              {"items": ["DA_InfinityEdge", "DA_KrakensFury"]}],
                    "secondary": [{"items": ["DA_LastWhisper", "DA_RedBuff"]}]},
 "DA_18_Ahri":     {"carry": [{"items": ["DA_JeweledGauntlet", "DA_SpearOfShojin"]},
                              {"items": ["DA_JeweledGauntlet", "DA_NashorsTooth"], "weight": 0.7}]}}
```

**`data/item_tiers.json`**: bậc S/A/B/C của đồ ghép từ `https://tftacademy.com/api/tierlist/items?set=18` (cập nhật 2026-11-16). Dùng cho tank và để loại "đồ quá mạnh" khỏi core.

**Thuật toán sinh bảng** (`scripts/build_core_items.py`, chạy cho mọi tướng):

| Bước | Cách |
|---|---|
| 1. Loại đồ | Gắn nhãn mỗi đồ ghép từ **dữ liệu CDragon** (chỉ số + từ khoá hiệu ứng trong mô tả), không liệt kê tay: phòng thủ (Giáp/Kháng phép/Máu), tấn công (Sát thương/Tốc đánh/Chí mạng/SMPT/Năng lượng), hiệu ứng (Vết thương sâu, Xé giáp, Phá giáp phép...) |
| 2. Vai | Mỗi tướng trong `finalComp` của mỗi comp: phần lớn đồ phòng thủ → tank; chỉ đồ hiệu ứng → carry phụ; còn lại → carry chính. **Không** dùng `mainChampion` (5/74 là tank) |
| 3. Đồ meta | Món có mặt ở phần lớn tướng **khác nhau** cùng vai (kiểu Gargoyle, Warmog cho tank) → đồ meta, loại khỏi core |
| 4. Bộ thay thế | Với mỗi (tướng, vai): phủ tập các comp bằng **ít bộ đồ nhỏ nhất** (phủ tập tham lam: chọn bộ 1–2 món phủ nhiều comp nhất, lặp lại với comp chưa phủ). Bộ chỉ phủ 1 comp thì bỏ (nhiễu) |
| 5. Trọng số | `weight` của bộ theo số comp phủ + hạng trung bình tactics.tools 18.6. Bộ đúng nhưng yếu ở meta (Găng + Nashor) có weight thấp, không bị loại |
| 6. Tank | Không có core; chấm theo bậc trong `item_tiers.json` |

**Duyệt**: bạn xem bảng sinh ra, chỉ sửa chỗ sai (không viết lại từ đầu). Các ví dụ ở trên được khoá bằng test.

Crawler `scripts/crawl_tftacademy_comps.py` đã có nhưng parser bỏ mất đồ từng tướng, `style`, `earlyComp`, `carousel`: sửa để giữ lại. Bảng duyệt tay không trái quy tắc "không curate tay" của SPEC: 18.6 là patch cuối, mỗi dòng có số liệu đi kèm.

## Patch: đồ theo tướng dùng chung, mạnh/yếu theo bản (bạn chốt 2026-11-17)

Bộ đồ hợp với một tướng **gần như không đổi** giữa 18.2 và 18.6. Thứ thay đổi giữa các bản là tướng nào mạnh, nghĩa là tướng nào xuất hiện làm carry. Vì vậy:

- Bảng core 18.6 **dùng được trên video dev 18.2/18.3**. Không vi phạm quy tắc "chấm bằng dữ liệu patch của nó", vì bảng mô tả đồ hợp tướng chứ không mô tả độ mạnh.
- Ứng viên carry của một hướng lấy **mọi tướng** có giá hợp hướng trong `champion_costs.json`, không chỉ tướng có mặt ở comp 18.6.
- Tướng không có dòng nào trong bảng (ở 18.6 không ai chơi làm carry) thì không có core. ItemFit với tướng đó giữ cách chấm cũ. Báo số tướng như vậy trên dev.
- `weight` chỉ so các bộ **của cùng một tướng**, không so giữa các tướng.

Carry chính và carry phụ xác định từ comp mẫu TFT Academy (bước 2 ở trên), không cần nhãn tay.

## Related

- [overview](overview.md) · [plan-item-fit](plan-item-fit.md) · [unit-items](unit-items.md) · [evaluation](evaluation.md)
- [Phân tích TFT Academy](../../research/261117-tftacademy-comp-items.md) · [Nguồn đồ core](../../research/261117-tft-item-recognition/en-core-items.md)
