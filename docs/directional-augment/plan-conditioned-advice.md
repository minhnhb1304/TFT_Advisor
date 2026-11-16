# Plan-conditioned Advice

Chốt 2026-11-13. Thay cách "suy hướng rồi chấm" bằng **gợi ý có điều kiện theo hướng**: hệ thống
không đoán người chơi đi hướng nào, mà đưa ra lõi tốt nhất **cho từng hướng**, người chơi tự chọn
dòng của mình.

## Vì sao đổi

| Cách cũ | Vướng |
|---|---|
| Lấy hướng từ `CompSelector` | Không có bộ đọc bàn cờ → `state.board` rỗng → `evidence = 0` → luôn tắt |
| Suy hướng từ HUD ở mốc 3-2/3-6/4-2 | Ở 4-2, fast8 và fast9 giống nhau (cấp 7, trên 50 vàng). Điểm phân biệt là **roll ở cấp 8 hay cấp 9**, chỉ thấy sau 4-2 |

Người chơi luôn biết mình đang đi hướng nào; hệ thống thì không. Nên để người chơi chọn.
Đây chính là `Score(a|φ)` ở [architecture.md](architecture.md) bước 4, nhưng **hiện từng φ** thay
vì gộp bằng belief, nên không cần ước lượng `b(φ)` và tránh luôn bẫy maximax.

## Quyết định của bạn

| Điểm | Chốt |
|---|---|
| Từ màn nào | **Từ 2-1.** Chốt hướng sớm thì dễ đánh và dễ tìm đường lui dự phòng |
| Bổ trợ | 3 lõi bổ trợ nhau thì càng mạnh → điểm ở 3-2/4-2 tính cả lõi **đã cầm** (`state.augments`) |
| Phạt ở 2-1 | **Không phạt** lõi cam kết hướng |
| Lõi chỉ gold | Thiết kế cũ (EconFit) coi là trung tính. Theo hướng thì **không** trung tính: fast9/cash cộng, fast8 trừ (`eco` × sức mạnh) |
| Game state | Để hiểu cách game vận hành và cảnh báo, **không** dùng để chọn hộ hướng |

## Màn hình mẫu (4-2)

```
Muốn lên 9          → Lấy A   (giữ lợi tức tới khi lên 9)
Mạnh ngay, chơi ở 8 → Lấy B   (sức mạnh ngay, kinh tế gần như không tính)
Thiếu tiền lên cấp  → Lấy C   (vàng/XP ngay để hoàn thành đội hình)
```

Nếu nhiều hướng cùng ra một lõi thì gộp dòng: *"Lấy A — hợp mọi hướng"*.

## Danh sách hướng (đã chốt trong `tuning.plan_fit.plans`: fast9 / fast8 / reroll / cash)

Bạn nói có thêm "vài hướng điển hình, không quá nhiều". Nháp dựa trên `PLANS` của nhãn và
[luật nhịp cấp](../../research/261113-tft-leveling-rules.md):

| Hướng | Ưu tiên khi chấm | Nhãn `plan.route` ánh xạ vào |
|---|---|---|
| Reroll (1/2/3 vàng) | `econ_type` reroll, gold; phạt nhẹ xp | `reroll1/2/3` |
| Fast 8, mạnh ngay | tempo, sức mạnh; kinh tế thấp | `fast8`, `standard` |
| Fast 9 | gold/lợi tức, xp; chấp nhận mất máu stage 4; combat vẫn hợp nếu đủ tiền/máu | `fast9` |
| Thiếu tiền / chuỗi thua | vàng và XP **ngay** | (tình huống, không có nhãn riêng) |

## Hiểu biết về game (dùng để đặt trọng số, không để suy hướng)

- fast9 **giữ lợi tức**, lên 8 bằng phần vàng dư trên 50, rồi lên thẳng 9 thường sau 4-4; fast8 lên 8 rồi roll ở 8.
- Lên 9 ngay ở 4-2 cần 2 lõi kinh tế rất mạnh + chuỗi dài.
- Tempo phải tính cả XP còn thiếu: phần lớn vàng dùng để mua cấp.

### Lõi combat vs lõi eco: trần sức mạnh (bạn, 2026-11-14)

| Khái niệm | Nghĩa |
|---|---|
| **Full form** | Đủ form đội hình, tướng 1 sao, chưa chạm trần |
| **Full bài** | Chạm trần: core 2 sao (fast 8/9) hoặc core 3 sao (reroll) |

- Mạnh nhất: **3 lõi combat + full bài**.
- **3 lõi combat chỉ cần full form** là mạnh; **3 lõi eco phải full bài** mới mạnh (eco cho tài
  nguyên, không cho sức mạnh, nên phải đổi tài nguyên thành trần).
- **3 lõi combat vẫn fast 9 được** nếu đủ tiền và máu (vd `minh_03`: fast9, cả 3 lõi `econ_value 0`).

Hệ quả cho chấm điểm: loại lõi (combat/eco) **trực giao** với hướng. Lõi eco không bắt buộc cho
fast 9; nó đổi *cách* đi tới trần. Gợi ý nên nói rõ cái giá: *"lấy eco → phải lên full bài mới
mạnh; lấy combat → full form là đủ"*. Lõi đã cầm cho biết người chơi còn "nợ" bao nhiêu sức mạnh
phải trả bằng bàn cờ.

### Giải thích hai màn trượt (bạn, 2026-11-14)

| Màn | Lý do thật | Luật rút ra |
|---|---|---|
| `minh_04` 4-2 | Đã full core 3 sao; 2 lõi trước nặng eco → đủ eco, thiếu combat. Thiếu đồ tank; Baron's Lair là lõi combat mạnh, vượt hẳn 2 lõi kia | Eco của reroll **hết giá trị sau khi roll xong** → trọng số theo stage. Nợ sức mạnh đúng hướng nhưng `debt_bonus` quá nhỏ |
| `minh_06` 4-2 | Lõi 1 combat mạnh làm bàn đạp → cần eco để lên full bài ở 8 (top 3–4). Booster Pack++ trả quà bằng orb; Bonus Gifts+ (lõi 2) cho thêm orb 3 vàng khi nhận orb | **Cân bằng hai chiều**: cầm combat → eco đáng giá hơn. **Combo lõi** là lý do chính |

## Trạng thái (2026-11-14)

| Việc | Trạng thái |
|---|---|
| `PlanFitScorer` + `rank_by_plan()` + 4 hướng trong `tuning.plan_fit` | Xong, `rank()` không đổi |
| `scripts/eval_plan_advice.py` trên dev | Vòng 1: tắt 6/15 → bật 8/15 ([dev_log §16](../../dev_log.md)) |
| Overlay hiện các dòng theo hướng | Xong 2026-11-14 (`tuning.plan_fit.enabled: true`), [dev_log §18](../../dev_log.md) |
| Cân bằng hai chiều + `by_stage` (reroll từ stage 4) | Xong: 9/15, số trong mẫu |
| Ghi lõi đã chọn (dải icon 10 giờ) | Xong 2026-11-14, 15/15 dev ([dev_log §17](../../dev_log.md)) |
| Bảng combo lõi | Chưa |

## Đo lường

- Mỗi màn: lấy dòng của **hướng thật** (`plan.route`) và so với lõi người chơi chọn; báo top-1 /
  top-3 khớp, bật vs tắt (cờ `tuning.plan_fit.enabled`, giữ ràng buộc ablation).
- Dev có 5 ván / 15 màn — chỉ để chỉnh; số báo cáo lấy từ held-out (video 18.6).
- Hạn chế phải ghi: ván đổi hướng giữa chừng cần `plan.since`/`plan.notes`.

## Related

- [Overview](overview.md) · [Architecture](architecture.md) · [Explainability](explainability.md)
- [Luật nhịp cấp](../../research/261113-tft-leveling-rules.md) · [Encounter](../../research/261113-tft-set18-maps.md)
