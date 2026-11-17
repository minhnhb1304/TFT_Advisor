# TFT Academy Comp Items

Phân tích `https://tftacademy.com/api/tierlist/comps?set=18` (74 hướng dẫn, cập nhật 2026-11-16) để dựng bảng đồ core. Làm 2026-11-17.

## Trường có trong mỗi hướng dẫn

| Trường | Nội dung | Dùng cho |
|---|---|---|
| `style` | `1-Cost Reroll` 8, `2-Cost Reroll` 12, `3-Cost Reroll` 18, `4-Cost Fast 8` 27, `Fast 9` 7, khác 2 | Ánh xạ thẳng sang hướng (`plan_fit.plans`) |
| `mainChampion{apiName,cost}` | Tướng chủ đạo. **5/74 là tank** (Malphite, Fiddlesticks...), nên không đồng nghĩa với carry | Vai: phân loại bằng đồ |
| `finalComp[]{apiName,items,stars,boardIndex}` | Đội hình cuối, đồ từng tướng | Bảng đồ core theo tướng |
| `earlyComp[]{…items}` | Đội hình đầu ván, **ai cầm đồ hộ** | 48/74 có người cầm hộ |
| `carousel[]` | 4 món/mảnh ưu tiên ở băng chuyền | Danh sách "đồ cần" sẵn có |
| `altBuilds`, `augments`, `augmentTypes`, `tips[stage]`, `difficulty`, `tier` | Bộ đồ thay thế, lõi gợi ý, mẹo theo giai đoạn | Tham khảo, giải thích |

## Kiểm luật của chuyên gia (người dùng, Challenger)

**Hướng → giá carry: đúng.** `1-Cost Reroll` → carry 1 vàng 8/8; `2-Cost` → 2 vàng 11/12; `3-Cost` → 3 vàng 18/18; `Fast 8` → 4 vàng 25/27; `Fast 9` → 5 vàng 4/7 (còn lại 4 vàng 2, 3 vàng 1).

**Cấu trúc đồ:** số tướng cầm đồ trong đội hình cuối là 3 (36 comp), 4 (26), 5 (7). Tổng 8–11 món. Khớp "carry chính + carry phụ + tank chính (+ tank phụ)".

**Guinsoo theo hướng** (tướng cầm Guinsoo trong `finalComp`):

| Hướng | Tướng |
|---|---|
| Fast 9 | Draven, Aphelios, Brambleback, Ivern |
| Fast 8 | Aphelios, Azir, Ivern, Nidalee AP |
| 3-Cost Reroll | Tristana, Yi, Rengar, Azir, Nidalee AP, Crimson Raptor |
| 2-Cost Reroll | Kayle, Caitlyn, Elise, Xayah |
| 1-Cost Reroll | Xayah, Kayle |

**Độ ổn định của đồ theo tướng** (số comp tướng đó cầm ≥ 2 món không phải đồ tank):

| Tướng | Món có mặt nhiều nhất | Nhận xét |
|---|---|---|
| Ahri (7) | Găng Bảo Thạch 6, Shojin 6, Flail 5 | Khớp "Găng + món tích năng lượng". **Nashor không xuất hiện**, Flail thay vào |
| Kayle (4) | Guinsoo 4 | Core rõ |
| Xayah (5) | Guinsoo 4, Deathblade 4, Kraken 4 | Core rõ |
| Ashe (6) | Red Buff 6, Last Whisper 5, Shojin 5 | Core rõ |
| Sivir (8) | Infinity Edge 7 | Core rõ |
| Ezreal (6) | Shojin 6, Deathblade 5 | Core rõ |
| Morgana (9) | Morellonomicon 9, Void Staff 8 | **Vai "cầm đồ tiện ích"** (giảm kháng phép, thiêu đốt), không phải carry |
| **Aphelios (10)** | Kraken 6, **Guinsoo 4**, Last Whisper 4, Red Buff 4 | Tách theo vai (giải thích của người dùng): **carry phụ** (3 comp: Eclipse Kayle, Unrivaled Reroll, Fae Xayah) cầm đúng Last Whisper + Red Buff. **Carry chính** (8 comp): 4 có Guinsoo (Nidalee, Elderwood, Solar Eclipse, Trait Ladder), 4 không (Flex, Vanguards: Red Buff/Deathblade/Giant Slayer; Rapidfire: IE/Kraken/Flail; Afaelios: IE/Kraken/ấn). Người dùng xác nhận đều hợp lệ: core = Guinsoo **hoặc** IE + Kraken |

**Người cầm đồ hộ đầu ván:** đồ của carry thường nằm trên tướng khác lúc đầu (Murkwolf cầm Guinsoo của Brambleback; Karma cầm đồ của Alune; Varus cầm IE của Aphelios). Đồ trên bàn ở vòng 2–3 **không cho biết carry là ai**, nên càng không nên suy tên tướng từ đồ.

## Luật suy core đề xuất

Core của tướng X trong hướng P = món có mặt ở ≥ ~70% số comp thuộc P mà X cầm đồ tấn công. Không món nào đạt ngưỡng → X là carry "build linh hoạt", dùng `carousel` của từng comp.

## Related

- [en-core-items](261117-tft-item-recognition/en-core-items.md) · [docs/item-reading/core-items](../docs/item-reading/core-items.md)
