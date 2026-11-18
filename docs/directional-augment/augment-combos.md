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
| 2 lõi chống chịu | `tank × tank` | nhẹ |
| Bonus Gifts + lõi trả orb | `bonus_gift × orb_payers` (Missed Connections, One Two Five, Champ Delivery+/++, Booster Pack+/++, Pilfer) | mạnh |
| Sweet Treats ↔ lõi cho item | `sweet_treats × category item` | vừa |
| Flexible → lõi cho ấn | `flexible × grant Emblem` | vừa |
| 2 Verticality vàng + kim cương | `Verticality II/III × II/III` | vừa |
| Jeweled Lotus + găng đạo tặc | `Lotus I/II × Band of Thieves II(+/++), Lucky Gloves(+)` | mạnh |
| Makeshift Armor kị lõi item | `makeshift × category item` | trừ vừa |
| Slammin' kị Pandora's Items | `slammin × pandoras_items` | trừ vừa |
| 2 lõi kinh tế (tiền - xp): đừng reroll | ở dòng Reroll: cảnh báo; lõi tiền/XP thứ hai bị trừ | vừa |
| 1 eco – 1 item – 1 combat | chỉ ghi lý do, không cộng điểm | info |
| Birthday Reunion phải fast 9 | cảnh báo; trừ ở mọi hướng khác fast9 | vừa |
| Warpath, Coven Acolyte, Flexible, Speedy Double Kill, Call To Chaos, Trait Ladder | chỉ hiện cảnh báo | — |

"2 lõi kinh tế" chỉ đếm lõi **thuần eco có `econ_type` gold/xp**, đúng chữ "(tiền - xp)".

## Kết quả trên dev (số trong mẫu)

`scripts/eval_plan_advice.py`, 15 màn, top-1 theo hướng thật: **tắt 6/15 · trước combo 9/15 · có combo 10/15**. Màn đổi được là `minh_06` 4-2 (fast8): cầm Bonus Gifts+, nay ra Booster Pack++.

Hai cách hiểu được chốt **sau khi** thấy dev; phải ghi rõ điều này trong luận văn:

| Luật | Bản thử đầu | Trên dev | Bản giữ lại |
|---|---|---|---|
| 1 eco – 1 item – 1 combat | cộng nhẹ | làm sai `minh_05` 4-2 (Hold The Line vượt Invested++) và chặn `minh_06` 4-2 | info (chỉ lý do); bạn mô tả nó là combo *dễ chơi*, không phải cộng hưởng |
| 2 lõi kinh tế | đếm mọi lõi eco | trừ Missed Connections ở `minh_04` 3-2, đúng ván bạn reroll | chỉ đếm lõi tiền/XP; Expected Unexpectedness không tính |

## Cần bạn xác nhận

1. **Nhóm `tank`** lấy từ cờ `frontline`, bỏ lõi có nhãn econ/item. Cờ này còn nhiễu, nên bạn lọc giúp danh sách trong JSON.
2. **"Lucky Gloves II"** không có trong 18.6; mình lấy Lucky Gloves và Lucky Gloves+.
3. **Champ Delivery / Booster Pack bản thường** không tính là lõi trả orb, vì bạn chỉ ghi "+/++".
4. **Bộ 3 eco–item–combat:** có nên cộng điểm không?
5. **Warpath, Coven Acolyte:** cần thêm tín hiệu (chuỗi thắng/thua) mới chấm được, nên hiện chỉ cảnh báo.

## Related

- [Plan-conditioned advice](plan-conditioned-advice.md) · [Implementation plan](implementation-plan.md)
- [Overview](overview.md)
