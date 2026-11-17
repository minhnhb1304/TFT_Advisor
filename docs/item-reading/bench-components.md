# Bench Components

Bước I2: đọc mảnh đồ chưa lắp trên băng ghế đồ. Thuộc [item-reading](overview.md).

## Quan sát trên video của mình (`minh_06`, 2026-11-17)

- Băng ghế đồ **không phải ô UI phẳng** như các repo khác mô tả. Đây là một dãy ô **3D trong sàn đấu**, ở mép trái bàn cờ (x khoảng 420–560, y khoảng 250–560 ở 1080p), và hình dáng ô đổi theo skin sàn đấu (sàn kính viễn vọng, sàn dung nham...).
- Trong `minh_06`, các khung đã xem (giây 70, 95, 115, 200, 400, 1085) đều có băng ghế **trống**: bạn lắp đồ ngay khi nhận. Vì vậy chưa có mẫu icon mảnh đồ đặt trên ô.
- Hệ quả: số đo của TFT-Copilot (lưới 2×10 ở x=8) và Hextech (cột 10 ô ở mép trái) **không áp dụng** cho client này. Phải tự đo.

## Cách làm

| Bước | Nội dung | Kiểm bằng |
|---|---|---|
| I2.0 | **Tìm mẫu trước khi code**: quét các video dev (cả `dat_*`, vì người khác có thể giữ mảnh lâu hơn) lấy khung có mảnh đồ trên băng ghế (đầu ván sau vòng quái, sau băng chuyền). Ghi giây + số mảnh vào `data/eval/items/bench_frames.json` | Có ≥ 30 khung, ≥ 3 skin sàn |
| I2.1 | Đo vị trí từng ô trên ≥ 3 skin. Nếu vị trí ô **giống nhau** giữa các skin → toạ độ cố định trong `screen_regions.yaml`. Nếu khác → phát hiện icon trong một dải ROI rộng | Ghi kết luận vào file này |
| I2.2 | `src/vision/bench_items.py`: phát hiện ô có icon, phân loại bằng cùng bộ phân loại ở [unit-items](unit-items.md) (chỉ 10 mảnh + vài vật phẩm đặc biệt → ít lớp hơn) | Bảng nhầm lẫn trên khung I2.0 |
| I2.3 | Điền `state.item_components` | `ItemFit` nhận dữ liệu thật trên dev |

## Phương án dự phòng

Nếu I2.0 cho thấy băng ghế gần như luôn trống trong lối chơi thật (lắp đồ ngay), thì `item_components` phần lớn bằng 0. Khi đó **đồ trên tướng (I1) mới là nguồn chính**: ItemFit tính "đang thiếu gì" từ đồ đã lắp + bảng đồ core, không cần mảnh trên băng ghế. Đây là lý do I1 làm trước I2.

## Rủi ro

| Rủi ro | Ứng phó |
|---|---|
| Ô 3D nghiêng theo phối cảnh, icon có thể bị xoay/co | Đo ở I2.1; nếu méo nhiều, so khớp bằng embedding thay vì NCC |
| Lúc ở bàn đối thủ, băng ghế của mình ở vị trí khác hoặc không thấy | Chỉ đọc khi camera ở bàn mình; giữ giá trị cũ khi không đọc được |

## Related

- [overview](overview.md) · [unit-items](unit-items.md) · [evaluation](evaluation.md)
