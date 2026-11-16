# Đánh Giá

## Cái chạy được hôm nay: đối chứng phản thực

`src/eval/reroll_ablation.py`. Ba phương pháp còn lại của SPEC §12 đều cần dataset thật
có nhãn (đo ở tuần 12, xem dưới). Phương pháp này thì không: nó đo **một chính sách so với một
chính sách khác trên cùng một hàm điểm**. Không cần nhãn của người chơi, cỡ mẫu tuỳ ý.

```
python -m src.eval.reroll_ablation --tier 2 --stage 2 --trials 10000
```

Thiết kế **ghép cặp**: sáu thẻ được rút trước, rồi mọi chính sách gặp **cùng một tay bài**,
nên delta không lẫn nhiễu của việc chính sách này may hơn chính sách kia. Khoảng tin cậy là
bootstrap trên chênh lệch đã ghép cặp.

### Kết quả (bậc gold, chặng 2-1, n = 10.000)

| chính sách | điểm TB | số lần đổi | Δ so với mốc [KTC 95%] |
|---|---|---|---|
| không đổi (mốc) | 0,58391 | 0,00 | — |
| chọn bừa | 0,53597 | 0,00 | −0,04794 [−0,04907, −0,04679] |
| vét hết ba lượt | 0,58439 | 3,00 | +0,00048 [−0,00044, +0,00147] |
| **tuần tự** | **0,60113** | **2,20** | **+0,01722 [+0,01665, +0,01779]** |
| biết trước (trần) | 0,60301 | 0,91 | +0,01911 [+0,01854, +0,01969] |

Bậc prismatic: tuần tự +0,01130, và chỉ dùng **1,24** lượt đổi thay vì 2,20 — đúng chế độ
mà `cost_matrix` mô tả. Dòng **vét hết ba lượt** là kết quả đáng chú ý nhất: nó không phân
biệt được với việc không đổi lần nào, vì lượt thứ ba bắt buộc đổi chính ô đang giữ thẻ tốt
nhất nên trả lại gần hết phần lợi của hai lượt đầu.

> Bảng ba bậc, kiểm chứng trần bằng công thức đóng và nhánh β:
> [ablation-results.md](ablation-results.md), [tailoring-beta-sweep.md](tailoring-beta-sweep.md).
> Số ở đây chạy lại 2026-10-07: bậc đã sửa, pool theo lượt chào (N = 59), bảng tier patch 18.2.

### Trần và một đồng nhất thức

`oracle == max của cả sáu thẻ`, đúng từng tình huống một. Lý do: mốc 0 lần đổi phủ
`{v₁,v₂,v₃}` và mốc 3 lần đổi phủ `{r₁,r₂,r₃}`, nên hợp của các mốc khả dĩ chính là cả sáu
thẻ. Ban đầu tưởng "max của 6" chỉ là chặn trên lỏng lẻo vì thẻ bị đổi đi thì mất hẳn —
nhưng người biết trước bao giờ cũng dừng đúng lúc nên họ với tới được.

Đồng nhất thức này được kiểm tra như một **bất biến của bộ mô phỏng**
(`test_oracle_equals_the_max_of_all_six_cards`): nếu nó gãy thì tập mốc khả dĩ đã bị cài
sai — loại lỗi im lặng nhất có thể có, vì bảng số vẫn chạy, chỉ là trần đặt sai chỗ.

### Giới hạn phải nêu trong báo cáo

Đây là **chính sách so với chính sách trên chính hàm Score của hệ thống**. Nếu hàm Score
sai thì cả hai chính sách cùng sai và số delta này vẫn đẹp như thường. Nó **không** phải
bằng chứng về placement. Câu này được in ngay trong bảng kết quả, không chỉ nằm trong
docstring.

## Đồng thuận chuyên gia: chưa có số, đo một lần ở tuần 12

Các khâu từng chặn nay đã có:

- Đọc thẻ lõi: `src/vision/augment_reader.py`, và bộ đọc hybrid `src/live/card_reader.py`
- Lõi người chơi đã chọn: `src/vision/held_augments.py` (dải icon 10 giờ), 15/15 trên dev

Phép đo đồng thuận là `scripts/eval_plan_advice.py`, chạy **một lần** ở tuần 12 trên bản
held-out (`minh_09–10`, `dat_02–05`, `maris_01–08` trong `data/eval/split.json`). Bản
development chỉ để chỉnh, không lấy số báo cáo.

Giới hạn cỡ mẫu vẫn đứng nguyên:

- Mỗi ván tối đa 3 cửa sổ augment, mỗi cửa sổ tối đa 4 điểm quyết định (≤3 lần đổi
  + 1 lần chọn), nhưng số cụm độc lập vẫn chỉ là **số ván held-out**.
- Phải báo cáo **cả** `n_windows` **lẫn** `n_games`.
- `picked` là lựa chọn của **một** người chơi: đo độ khớp với chuyên gia, không phải độ chính xác.

### Thống kê: Brennan–Prediger S, không phải Cohen kappa

Giữ **S** làm chỉ số chính, kể cả cho không gian nhãn 3 thẻ. Cohen kappa ước lượng đồng
thuận ngẫu nhiên từ phân phối biên trên **một** không gian nhãn chung; ở đây mỗi tình
huống chào 3 augment **khác nhau**, gần như rời nhau. Với `n = 18` và `p_o = 0,60`, công
thức cũ trả 0,577 ("khá") trong khi giá trị đúng là 0,40 ("trung bình") —
`src/eval/expert_study.py:12-29`.

Với không gian nhị phân ĐỔI/CHỌN thì `k = 2` nên `p_e = 0,5`. Vẫn là **S**, không phải
kappa. Báo cáo cả hai không gian nhãn kèm `k` của chúng.

Dùng lại `expert_study.chance_corrected_agreement` và `correlation.permutation_p_value(groups=game_id)`.

> ⚠️ SPEC §12.3 vẫn ghi "Cohen kappa" và đã **lỗi thời**.

## Việc tiếp theo, theo thứ tự

1. Chạy **lệch pha** β: rút bài với β = 1 nhưng cho `decide()` tin là β = 0. Lần quét đã làm
   ([tailoring-beta-sweep.md](tailoring-beta-sweep.md)) đổi β ở **cả hai** chỗ nên chưa tách
   được thiên lệch sợ-reroll ra khỏi việc pool đổi.
2. Đo độ nhạy theo `cost_matrix` — thứ tự đã kiểm chứng, độ lớn thì chưa.
3. Đo độ trễ **khi game đang chạy** (SPEC §12.1), không đo trên máy rảnh.
4. Tuần 12: nhật ký `reroll_trace` → đồng thuận chuyên gia trên held-out.

## Related

- [ablation-results.md](ablation-results.md) — bảng kết quả D.2 đầy đủ
- [tailoring-beta-sweep.md](tailoring-beta-sweep.md) — nhánh β = 1 vs β = 0
- [overview.md](overview.md) — bảng kết quả tóm tắt
- [depletion-cost.md](depletion-cost.md) — tham số đang cần hiệu chỉnh
- [architecture.md](architecture.md) — ngân sách độ trễ
