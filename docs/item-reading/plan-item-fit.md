# Plan Item Fit

Bước I3.2 + I3.3: suy carry theo hướng và chấm lõi tặng đồ theo hướng. Thuộc [item-reading](overview.md), dùng bảng ở [core-items](core-items.md).

## I3.2. Carry theo hướng, không theo tộc

**Không suy đội hình từ tộc ở vòng 2–3**: người chơi giữ máu bằng một đội hình rồi xoay sang đội hình khác hẳn. Nguyên tắc giống [plan-conditioned advice](../directional-augment/plan-conditioned-advice.md): khuyên **cho từng hướng**, người chơi tự chọn.

| Hướng (`plan_fit.plans`) | Cấp | Giá carry | Ví dụ carry dùng Guinsoo |
|---|---|---|---|
| `fast9` Muốn lên 9 | 9 | 5 | Draven |
| `fast8` Mạnh ngay, chơi ở 8 | 8 | 4 | Aphelios |
| `reroll` | 7 / 6 / 5 | 3 / 2 / 1 (**gộp cả ba**) | Tristana, Yi, Rengar / Kayle, Caitlyn / Xayah |
| `cash` Thiếu tiền lên cấp | — | — | **Để sau**. ItemFit trên dòng này giữ cách chấm cũ |

TFT Academy xác nhận `style` → giá carry chính: 8/8, 11/12, 18/18, 25/27 comp; Fast 9 là 4/7.

**Ứng viên là comp mẫu TFT Academy, không phải từng tướng** (bạn chốt 2026-11-17: TFT Academy là mẫu chuẩn để theo đuổi). Đồ, hướng và đội hình đi kèm nhau khi chốt bài: mỗi thông tin loại bớt lựa chọn. Ví dụ cầm Guinsoo + chọn Fast 8 → còn Aphelios, Azir, Ivern, Nidalee AP.

```
ứng_viên(hướng) = comp TFT Academy có style khớp hướng
                  xếp theo số món ĐÃ GHÉP đang cầm có chỗ trong comp
                  (core carry chính, đồ carry phụ, hoặc đồ tank), giữ nhóm khớp nhiều nhất
chưa ghép món nào (đầu ván)  → giữ mọi comp của hướng
không comp nào khớp món nào  → lùi về tướng có giá hợp hướng + bộ core của tướng; ghi log "lùi"
```

- Mảnh lẻ **không** loại comp nào (mảnh nào cũng dùng được). Chỉ đồ đã ghép mới lọc.
- Chấm mức khớp chứ không cắt cứng, nên danh sách không bao giờ rỗng.
- Đồ tính cả tướng trên hàng chờ. Không cần tên tướng trên bàn, không suy từ tộc hệ.
- Comp là của 18.6. Trên video dev 18.2/18.3 có thể không khớp bài bạn chơi: dùng nhánh "lùi" và **báo tỷ lệ lùi** như một số liệu về độ phủ.
- Thưởng core, chấp lõi và câu giải thích đều suy từ các comp còn lại. Tên comp chỉ nằm trong câu giải thích của dòng hướng, không thêm panel (giữ phạm vi 2026-10-31).

## I3.3. Chấm lõi tặng đồ

Ý của bạn (2026-11-17): **mảnh nào cũng dùng được**. Ra mảnh core thì tốt, không thì vẫn lắp được đồ tank, đồ hiệu ứng, đồ cho carry phụ. Lò rèn (Anvil) nhỉnh hơn một mảnh một chút. Vì vậy chỉ cộng **thưởng** khi đúng mảnh core, không phạt mảnh khác. ItemFit hiện có đã có sàn 0,4 theo đúng ý này.

| Lõi tặng | Giá trị theo hướng |
|---|---|
| Mảnh cụ thể m | sàn + thưởng nếu m còn thiếu để ghép một bộ core của ứng viên (nhân `weight`, tỷ lệ ứng viên được giúp) |
| Mảnh bất kỳ | sàn + thưởng của mảnh tốt nhất (tự chọn được) |
| Lò rèn | như mảnh bất kỳ, cộng thêm một chút |
| Đồ hoàn chỉnh ngẫu nhiên | sàn; không thưởng core (không chọn được món) |
| Ấn | không đổi so với hiện tại |
| Không ứng viên / không đọc được đồ | giữ ItemFit cũ, không phạt |

Câu giải thích nêu món và tướng, ví dụ "Reroll: cho Kiếm, đang thiếu để ghép Guinsoo cho Tristana/Yi/Rengar". Carry phụ / tank nhận món thừa chỉ dùng cho câu giải thích, không cộng điểm riêng.

## Chấp lõi: lõi lệch hướng sát thương (bạn bổ sung 2026-11-17)

Đội hình đã chốt carry AD (core là đồ AD) thì **không chọn lõi gắn nhãn AP**, kể cả khi lõi đó cho mảnh đang thiếu. Chiều ngược lại cũng vậy. Lấy lõi lệch hướng thì phần chỉ số cộng thêm của lõi mất 80–90% giá trị, người chơi gọi là "chấp lõi". Ví dụ: đã đi Aphelios mà lấy Wand Overflow (bậc kim cương, cho mảnh Gậy).

Luật chung, áp cho mọi tướng và mọi lõi:

```
hướng_sát_thương(hướng) = loại đồ (AD/AP) trong core carry chính của các comp ứng_viên(hướng)
lõi có carry_type AD/AP ngược với hướng_sát_thương, và mọi comp còn lại cùng một loại
    → điểm theo hướng = khoảng 15% điểm gốc (chỉnh trong 10–20%), bỏ cả thưởng mảnh core
    → giải thích: "Chấp lõi: lõi AP, đội hình đang theo carry AD (Aphelios)"
comp còn lại lẫn AD và AP (đầu ván, chưa ghép đồ) → không phạt
lõi carry_type none / both → không phạt
```

- Loại AD/AP của bộ core lấy từ bước phân loại đồ CDragon ([core-items](core-items.md) bước 1), không gõ tay.
- Nhãn lõi dùng `carry_type` có sẵn trong `augment_features.json` (9 AD, 8 AP, 20 both). **Không** suy hướng từ mảnh được tặng, vì Nước Mắt dùng được cho cả carry AD (Shojin).
- Phạt nằm trong `rank_by_plan()` nên chỉ đổi thứ tự **trên dòng của hướng đó**, không đụng điểm chung.
- Test: Aphelios + Guinsoo trên dòng `fast8`, lõi Wand Overflow xếp dưới mọi lõi trung tính. Cùng lõi trên dòng `reroll` khi chưa cầm đồ thì không bị phạt.

## Gắn vào code

- `ItemFit` cũ **giữ nguyên** trong `rank()` (điểm chung, không theo hướng).
- Thêm số hạng **thưởng core theo hướng** vào `rank_by_plan()`, cộng giống `PlanFit`: `w_core * thưởng(hướng)`. Chỉ cộng phần thưởng nên không tính trùng phần sàn của ItemFit cũ.
- `w_core` đặt trong `config/scoring_weights.yaml`, chỉnh trên dev.

## Trạng thái 2026-11-18: đã gắn, chưa đổi kết quả dev

`src/decision/scoring/core_fit.py` + `config/scoring_weights.yaml` (`tuning.core_fit`: `weight` 0,10, `anvil_extra` 0,15, `off_damage_factor` 0,15, `plan_costs`). Chỉ chạy khi có `data/core_items.json` **và** đọc được ít nhất một món. Chấp lõi chỉ xét khi đã có đồ ghép (đầu ván không phạt). Lý do nằm trong `PlanLine.core_fit` (log, replay), chưa lên overlay. Đo bằng `scripts/eval_core_fit.py`: xem [evaluation](evaluation.md).

## Related

- [overview](overview.md) · [core-items](core-items.md) · [unit-items](unit-items.md) · [evaluation](evaluation.md)
