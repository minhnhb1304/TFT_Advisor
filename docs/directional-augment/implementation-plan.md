# Implementation Plan

Kế hoạch 2026-11-14 cho phần còn lại của [plan-conditioned advice](plan-conditioned-advice.md).
Mốc cứng: **tuần 12 (từ 2026-12-16) đóng băng số**, tuần 9–11 gắn nhãn held-out.

## Thứ tự và lý do

| # | Việc | Vì sao ở vị trí này |
|---|---|---|
| A | Ghi lõi đã chọn khi chơi thật | Không có A thì luật cân bằng và combo **không chạy trên overlay**: hiện `state.augments` chỉ được điền trong script đánh giá |
| D | Overlay hiện các dòng theo hướng | Để bạn chạy thử trên máy kia càng sớm càng tốt |
| B | Bảng combo lõi | Cần bạn cung cấp combo, làm song song được |
| E | Đánh giá held-out + viết chương | Cần video 18.6 đã gắn `plan.route` |

## A. Ghi lõi đã chọn (tuần 7) — xong 2026-11-14, 15/15 trên dev

Mẫu so sánh chính là icon **cắt từ thẻ lõi** ngay trước khi màn đóng; icon CDragon chỉ dự phòng vì có lõi lệch icon (Bonus Gift+). Chi tiết: [dev_log §17](../../dev_log.md).

Dải icon ~37 px ở hướng 10 giờ (x≈511, y≈245 ở 1080p), xếp trái sang phải theo thứ tự chọn.

| Bước | Nội dung | Kiểm bằng |
|---|---|---|
| A1 | `scripts/fetch_augment_icons.py`: tải icon từ đường dẫn `icon` trong CDragon (`.tex` → `.png` trên raw.communitydragon.org) vào `data/augment_icons/` | Đủ icon cho mọi lõi `live` |
| A2 | `src/vision/held_augments.py`: cắt dải, tách từng ô icon (nền đen vuông), **đếm** số icon, phân loại icon mới bằng cách so với **3 lõi cuối được chào** (không phải 250 lõi) | Unit test trên ảnh cắt từ `minh_06` |
| A3 | `LiveSession`: ngoài màn chọn lõi, khi số icon tăng từ n lên n+1 trong cửa sổ ~90 s sau màn chọn lõi thì ghi lõi đó vào `state.augments`. Reset khi sang ván mới | Test máy trạng thái |
| A4 | `scripts/eval_held_augments.py` trên 5 ván dev | **Khớp `picked` ở 15/15 màn**, kể cả `dat_01` (16:10) |

Rủi ro đã biết:
- **Xem bàn người khác** thì dải icon là của họ. Chặn bằng: chỉ nhận khi số icon tăng đúng 1, trong cửa sổ ngay sau màn của mình, và độ khớp vượt ngưỡng.
- **Bản +/++ có thể chung icon**, chỉ khác màu khung (bậc). 3 lõi được chào thường khác nhau; nếu trùng thì xét màu khung, vẫn mơ hồ thì ghi cả hai và gắn nhãn, không đoán.
- **Bố cục 16:10:** toạ độ phải đi qua `ScreenRegions`, không hardcode.
- **Không chắc thì ghi "chưa rõ"**, không đoán.

## D. Overlay theo hướng (tuần 8) — xong 2026-11-14, kèm nâng UI kiểu Blitz

Chi tiết và ảnh: [dev_log §18](../../dev_log.md). Còn D4: bạn chạy thử live.

| Bước | Nội dung | Kiểm bằng |
|---|---|---|
| D1 | `Advisor.advise()` gọi `rank_by_plan()` khi `plan_fit.enabled`, đặt vào `AdviceBundle.plans` | Tắt cờ thì bundle không đổi |
| D2 | `augment_panel`: mỗi dòng `<hướng> → <lõi> (<cái giá>)` + cảnh báo máu; tối đa 4 dòng; các dòng trùng lõi đã gộp sẵn | Test `render_text` |
| D3 | Replay viewer hiện cùng panel | Bạn chạy trên video dev |
| D4 | Bật `enabled: true`, bạn chạy thử live | Phản hồi của bạn |

## B. Combo lõi (tuần 8, song song)

| Bước | Nội dung |
|---|---|
| B1 | Nguồn: (1) **bạn liệt kê** combo bạn biết; (2) research EN + ZH (`lead-researcher`) về combo lõi Set 18; (3) trích cặp ứng viên từ mô tả, ví dụ lõi sinh orb × lõi khuếch đại orb |
| B2 | `data/augment_combos.json`: `{a, b, bonus, reason, source}`; `a`, `b` là **họ lõi** (bỏ +/++) |
| B3 | Trang duyệt (theo mẫu `review_augment_features.py`) để bạn chốt từng cặp; chỉ cặp đã duyệt mới được dùng |
| B4 | `PlanFitScorer`: lõi ứng viên tạo combo với lõi đã cầm thì được cộng `combo_bonus`, lý do ghi *"combo với X"*. Test: `minh_06` 4-2 → Booster Pack++ |

## E. Đánh giá và luận văn (tuần 9–12)

- Bạn quay và gắn nhãn video 18.6 kèm `plan.route` (cùng `encounter`, `plan.since`).
- Chạy `eval_plan_advice.py` **một lần** trên held-out ở tuần 12: top-1 và top-3 khi tắt và khi bật.
- Ghi rõ trong luận văn: số dev là số trong mẫu; trọng số là giả định từ luật chuyên gia; phép đo là độ khớp với một chuyên gia.

## Việc của bạn

| Khi nào | Việc |
|---|---|
| Ngay | Quay video 18.6 (đang trễ so với kế hoạch tuần 6) |
| Tuần 8 | Liệt kê combo lõi; duyệt cặp combo trên trang review; chạy thử overlay |
| Tuần 9–11 | Gắn nhãn held-out, có `plan.route` |

## Related

- [Plan-conditioned advice](plan-conditioned-advice.md) · [Overview](overview.md)
- [dev_log §16](../../dev_log.md) · [Next steps](../next-steps.md)
