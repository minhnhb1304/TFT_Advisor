# Bench Components

Bước I2: đọc mảnh đồ chưa lắp trên băng ghế đồ. Thuộc [item-reading](overview.md).

## Vật trên sàn cạnh mép trái bàn (bạn xác nhận 2026-11-18)

Các báo cáo trước (2026-11-17, I2.0 sơ bộ) gọi cột ô ở mép trái là "băng ghế đồ" và các vật trong đó là "quả cầu vàng / vật hồng". **Sai**: bạn xác nhận đó là những thứ sau:

| Vật (ảnh 3-1, 4-1 trên 4 skin sàn) | Thật ra là | Với bộ đọc đồ |
|---|---|---|
| Cột 4–5 ô ở mép trái (chậu cam, cầu vàng, vỏ sò…) | **Lợi tức**: mỗi ô = 10 vàng (5 ô = 50 vàng), hình đổi theo skin | Bỏ qua |
| Icon vuông nhỏ trên đầu cột | **Lõi đã chọn** | Không phải đồ; không gắn với thanh máu nên bộ đọc I1 không bắt |
| Thanh kiếm pha lê trên bệ | Đi kèm lõi đã chọn (lõi căn giữa theo nó), không có tác dụng | Bỏ qua |
| Vật hồng, khủng long, con ma to | Hiệu ứng sàn đấu / chưởng lực (skin) | Bỏ qua |

Hệ quả:
- Kết luận cũ "băng ghế trống ở 2-1" **không còn căn cứ**, vì vùng đã xem là ô lợi tức. Điều còn đúng: bộ đọc I1 và mắt đều thấy 0 món **trên tướng** ở 2-1 trong 5 ván.
- **Chưa biết mảnh đồ chưa lắp nằm ở đâu trên màn hình** → cần bạn chỉ chỗ (ảnh có mảnh chưa lắp) trước khi làm I2.0 lại. Số đo của TFT-Copilot / Hextech vẫn không áp dụng được.

## Cách làm

| Bước | Nội dung | Kiểm bằng |
|---|---|---|
| I2.0 | **Tìm mẫu trước khi code**: quét các video dev (cả `dat_*`, vì người khác có thể giữ mảnh lâu hơn) lấy khung có mảnh đồ trên băng ghế (đầu ván sau vòng quái, sau băng chuyền). Ghi giây + số mảnh vào `data/eval/items/bench_frames.json` | Có ≥ 30 khung, ≥ 3 skin sàn |
| I2.1 | Đo vị trí từng ô trên ≥ 3 skin. Nếu vị trí ô **giống nhau** giữa các skin → toạ độ cố định trong `screen_regions.yaml`. Nếu khác → phát hiện icon trong một dải ROI rộng | Ghi kết luận vào file này |
| I2.2 | `src/vision/bench_items.py`: phát hiện ô có icon, phân loại bằng cùng bộ phân loại ở [unit-items](unit-items.md) (chỉ 10 mảnh + vài vật phẩm đặc biệt → ít lớp hơn) | Bảng nhầm lẫn trên khung I2.0 |
| I2.3 | Điền `state.item_components` | `ItemFit` nhận dữ liệu thật trên dev |

## Phương án dự phòng

Nếu I2.0 cho thấy mảnh chưa lắp gần như không có trong lối chơi thật (lắp đồ ngay), thì `item_components` phần lớn bằng 0. Khi đó **đồ trên tướng (I1) mới là nguồn chính**: ItemFit tính "đang thiếu gì" từ đồ đã lắp + bảng đồ core, không cần mảnh trên băng ghế. Đây là lý do I1 làm trước I2.

## Rủi ro

| Rủi ro | Ứng phó |
|---|---|
| Ô 3D nghiêng theo phối cảnh, icon có thể bị xoay/co | Đo ở I2.1; nếu méo nhiều, so khớp bằng embedding thay vì NCC |
| Lúc ở bàn đối thủ, băng ghế của mình ở vị trí khác hoặc không thấy | Chỉ đọc khi camera ở bàn mình; giữ giá trị cũ khi không đọc được |

## Related

- [overview](overview.md) · [unit-items](unit-items.md) · [evaluation](evaluation.md)
