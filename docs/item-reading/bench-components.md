# Bench Components

Bước I2: đọc mảnh đồ chưa lắp. Thuộc [item-reading](overview.md).

## Vật trên sàn cạnh mép trái bàn (bạn xác nhận 2026-11-18)

Các báo cáo trước (2026-11-17, I2.0 sơ bộ) gọi cột ô ở mép trái là "băng ghế đồ" và các vật trong đó là "quả cầu vàng / vật hồng". **Sai**: bạn xác nhận đó là những thứ sau:

| Vật (ảnh 3-1, 4-1 trên 4 skin sàn) | Thật ra là | Với bộ đọc đồ |
|---|---|---|
| Cột 4–5 ô ở mép trái (chậu cam, cầu vàng, vỏ sò…) | **Lợi tức**: mỗi ô = 10 vàng (5 ô = 50 vàng), hình đổi theo skin | Bỏ qua |
| Icon vuông nhỏ trên đầu cột | **Lõi đã chọn** | Không phải đồ; không gắn với thanh máu nên bộ đọc I1 không bắt |
| Thanh kiếm pha lê trên bệ | Đi kèm lõi đã chọn (lõi căn giữa theo nó), không có tác dụng | Bỏ qua |
| Vật hồng, khủng long, con ma to | Hiệu ứng sàn đấu / chưởng lực (skin) | Bỏ qua |

Kết luận cũ "băng ghế trống ở 2-1" vì vậy sai. Ở 2-1, trên **tướng** đúng là chưa có món nào.

## Thanh đồ chưa lắp (bạn chỉ chỗ 2026-11-18, đã làm)

Mảnh thừa nằm ở **thanh dọc sát mép trái màn hình, bên trái khung tộc hệ**. Đây là UI phẳng (không phải vật 3D), nên skin sàn không ảnh hưởng.

| Bước | Kết quả |
|---|---|
| I2.1 vị trí | 10 ô, toạ độ cố định theo chiều cao, neo mép trái: ô i ở (11, 263 + 54·i), cạnh 42 px tại 1080p. Khớp cả 1920×1080 lẫn 1728×1080 |
| I2.2 đọc | `src/vision/bench_items.py`: ô trong (bên trong đen phẳng) bỏ qua, ô có icon phân loại bằng `UnitItemReader.classify` (ngưỡng 0,70). Mảnh thật đạt 0,89–0,96 |
| I2.2 kiểm | 63 khung nhãn dev: 471 ô trống, **66 ô ra tên món, kiểm bằng mắt không thấy ô sai**; 93 ô "chưa rõ" là vật đặc biệt (ô đầu có số đếm, búa rèn, lá xanh, quả cầu xoay…) hoặc ô bị con trỏ chuột che. Chưa có nhãn riêng cho thanh này |
| I2.3 vào state | `ItemTracker` cộng đồ trên thanh vào `completed_items` / `item_components` (`held_items(units, bench)`). Khung không thấy tướng mình nào thì bỏ, để lần đọc chỉ có thanh đồ không đè mất đồ trên tướng |

Đồ có dấu đồng hồ chỉ tồn tại 1 vòng (bạn xác nhận) → không tính; bộ đọc đã ra "chưa rõ" với chúng.

Trên 15 màn dev: đọc được đồ **15/15** (trước 10/15). Ở 2-1 có 1–3 mảnh. Xem [evaluation](evaluation.md).

## Related

- [overview](overview.md) · [unit-items](unit-items.md) · [evaluation](evaluation.md)
