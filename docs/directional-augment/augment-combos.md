# Augment Combos

Luật combo lõi của người chơi (Thách Đấu VN), viết 2026-11-18 (nguồn gốc: `local_docs/combo lõi - augument.txt`). Đây là bước B của [implementation plan](implementation-plan.md).

| Thành phần | File |
|---|---|
| Bảng luật, giữ nguyên câu gốc ở `source` | `data/augment_combos.json` |
| Bộ áp luật | `src/decision/scoring/augment_combos.py` |
| Mức nhẹ / vừa / mạnh | `tuning.plan_fit.combo_strength` trong `config/scoring_weights.yaml` |
| Test | `tests/test_augment_combos.py` |

## Cách áp

- `PlanFitScorer` so lõi ứng viên với lõi đã cầm (`state.augments`).
- `rank_by_plan()` cộng `combo_delta` **thẳng vào tổng điểm hướng**, không nhân `weight` 0,15. Lý do: nhân 0,15 thì combo "mạnh" chỉ còn ~0,015, nhỏ hơn hẳn khoảng cách giữa các lõi.
- Đơn vị mức combo là tổng điểm:

| Mức | Điểm | Căn cứ |
|---|---|---|
| info | 0 | chỉ hiện lý do |
| light | 0,02 | ≈ ½ khoảng cách top-1/top-2 trung vị trên dev (0,039) |
| medium | 0,04 | ≈ 1 khoảng cách |
| strong | 0,08 | ≈ 2 khoảng cách |

- Nhóm lõi khai báo theo một trong ba cách: `apis` (danh sách), `category` (nhãn) hoặc `grant` (món được tặng).

## Luật đã chuyển

| Ý của bạn | Luật | Mức |
|---|---|---|
| 2 lõi chống chịu | `tank × tank` (cờ `frontline`) | nhẹ |
| Bonus Gifts + lõi trả orb | `bonus_gift → orb_payers`, một chiều (Missed Connections, One Two Five, Champ Delivery+/++, Booster Pack+/++, Pilfer) | mạnh |
| Sweet Treats ↔ lõi cho item | `sweet_treats × category item` | vừa |
| Flexible → lõi cho ấn | `flexible × grant Emblem` | vừa |
| 2 Verticality vàng + kim cương | `Verticality II/III × II/III` | vừa |
| Jeweled Lotus + găng đạo tặc | `Lotus I/II × Band of Thieves II(+/++), Lucky Gloves(+)` | mạnh |
| Makeshift Armor kị lõi item | `makeshift × category item` | trừ vừa |
| Slammin' kị Pandora's Items | `slammin × pandoras_items` | trừ vừa |
| 2 lõi kinh tế (tiền - xp): đừng reroll | ở dòng Reroll: cảnh báo; lõi tiền/XP thứ hai bị trừ | vừa |
| 1 eco – 1 item – 1 combat | lõi thứ 3 hoàn tất bộ | nhẹ |
| Birthday Reunion phải fast 9 | cảnh báo; trừ ở mọi hướng khác fast9 | vừa |
| Warpath, Coven Acolyte, Flexible, Speedy Double Kill, Call To Chaos, Trait Ladder | chỉ hiện cảnh báo | — |

## Câu trả lời của bạn (2026-11-18)

| Câu hỏi | Trả lời → đã làm |
|---|---|
| Nhóm `tank` | cờ `frontline` đã duyệt kỹ → nhóm = `{"frontline": true}` |
| Lucky Gloves II | đồng ý Lucky Gloves + Lucky Gloves+ |
| Champ Delivery / Booster Pack bản thường | chỉ có ở 2-1, luôn chọn trước Bonus Gifts+ (3-2); lõi trả orb chọn **trước** thì orb đã trả, không hưởng thêm → luật một chiều (`one_way`): Bonus Gifts cầm trước, lõi orb là ứng viên |
| Bộ 1 eco – 1 item – 1 combat | cộng nhẹ |
| Warpath, Coven Acolyte | lõi 2-1, chưa có chuỗi → chỉ cảnh báo |
| Warpath có phải lõi item? | không: item + tiền chỉ trả khi gây 80 sát thương lên người chơi (~10–11 trận thắng) → `triad.conditional`, không tính vào trục nào |
| Nhãn Warpath trong `augment_features.json` | `econ_value` 3 → 1, `board_condition` = phải thắng đủ 80 sát thương. Dev giữ 9/15; `minh_05` 2-1 Warpath 0,595 → 0,54, vẫn hạng 2 sau Hard Bargain |

"2 lõi kinh tế" chỉ đếm lõi **thuần eco có `econ_type` gold/xp**, đúng chữ "(tiền - xp)" (Expected Unexpectedness không tính).

## Kết quả trên dev (số trong mẫu)

`scripts/eval_plan_advice.py`, 15 màn, top-1 theo hướng thật:

| Bản | Khớp |
|---|---|
| Tắt hướng | 6/15 |
| Hướng, chưa combo | 9/15 |
| Combo, bộ 3 chỉ ghi lý do | 10/15 |
| Combo, bộ 3 cộng nhẹ, Warpath tính là item | 8/15 |
| **Combo, bộ 3 cộng nhẹ, Warpath có điều kiện (bản giữ)** | **9/15** |

Bộ 3 cộng nhẹ từng đổi hai màn 4-2:

- `minh_05` (Warpath + Slammin'+): Hold The Line và Lotus II 0,5332 vượt Invested++ 0,5207. Đã hết sau khi bạn duyệt lại Warpath.
- `minh_06` (Seraphim's Staff + Bonus Gifts+): Glass Cannon và Booster Pack++ **bằng điểm** 0,55, thua theo thứ tự tên.

Đây là luật chuyên gia, không chỉnh số để khớp dev. Chương kết quả ghi cả hai bản.

## Related

- [Plan-conditioned advice](plan-conditioned-advice.md) · [Implementation plan](implementation-plan.md)
- [Overview](overview.md)
