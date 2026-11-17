# Unit Items

Bước I1: đọc đồ trên tướng (3 icon dưới thanh máu). Thuộc [item-reading](overview.md).

## Quan sát trên video của mình (`minh_06`, 1080p, 2026-11-17)

- Icon là ô phẳng, nền tối, **khoảng 23 px**, 3 ô liền nhau ngay dưới thanh máu. Đọc rõ ở cả lúc giao tranh (khung giây 1085, vòng 4-1).
- Tướng mình có thanh máu **xanh**, tướng địch có thanh **đỏ**. Chỉ đọc thanh xanh.
- Khớp với số đo của hai repo Set 18 độc lập (TFT-Copilot, Agente-TFT): icon 23×23, bước 25–26 px, góc trên trái hàng icon lệch khoảng (−5, +11) so với góc trên trái thanh máu. Nguồn: [en-recognition](../../research/261117-tft-item-recognition/en-recognition.md).

## Cách làm

| Bước | Nội dung | Kiểm bằng |
|---|---|---|
| I1.1 | `scripts/fetch_item_icons.py`: chép logic `fetch_augment_icons.py`, tải icon 10 mảnh + đồ ghép + ấn + đồ tạo tác của Set 18 từ CDragon vào `data/item_icons/` | Đủ icon cho mọi `apiName` trong `item_recipes.json` |
| I1.2 | `src/vision/unit_items.py` · `find_health_bars(frame)`: mặt nạ màu xanh (`G>110 & G>1.65R & G>1.5B`), lọc theo kích thước thanh (~62–70 × 2–6 px) và viền tối | Unit test trên khung cắt từ `minh_06`: đếm đúng số tướng trên bàn |
| I1.3 | Cắt hàng 3 ô theo neo thanh máu, kiểm ô trống (độ lệch chuẩn xám thấp), phân loại ô có icon | Unit test: ô trống / 1 / 2 / 3 đồ |
| I1.4 | Phân loại: **thử rẻ trước** — NCC 23×23 với icon CDragon thu nhỏ, lấy argmax, ngưỡng + khoảng cách top-1/top-2. Chỉ khi đo thấy không đủ mới chuyển sang embedding (ResNet18 cosine, không cần huấn luyện) | Bảng nhầm lẫn trên bộ nhãn ở [evaluation](evaluation.md) |
| I1.5 | `LiveSession`: đọc đồ **ở đầu mỗi vòng** (khi HUD báo đổi vòng, vào pha chuẩn bị), vì vòng nào cũng có thể nhận thêm đồ từ lõi / sự kiện. Thanh máu chồng nhau thì đọc lại vài khung sau trong cùng pha. Giữ lần đọc gần nhất cho màn chọn lõi (màn này che bàn cờ) | Test máy trạng thái; log `item_ms` trong `data/live_logs` |
| I1.6 | Điền `Champion(items=…, position=…)` vào `state.board`. Tên tướng để trống: không cần, vì carry suy theo hướng ([plan-item-fit](plan-item-fit.md) I3.2) | `state.carries` không còn rỗng trên dev |

## Quy tắc

- **Không chắc thì không đoán**: thanh máu chồng nhau, thiếu thanh, ô bị hiệu ứng đè → đánh dấu "chưa rõ", không ghi "không có đồ".
- Tên đồ dùng **apiName CDragon** (`TFT_Item_…` / `DA_…` đúng như `item_recipes.json`). Không đặt tên rút gọn mới.
- Toạ độ qua `ScreenRegions` (phân số), không hardcode pixel.

## Rủi ro

| Rủi ro | Ứng phó |
|---|---|
| Đồ ánh sáng / đồ cộng dồn có số đè lên icon (TFT-Copilot báo đọc trượt) | Giữ ngưỡng chặt; ghi thành "chưa rõ" |
| Lúc **xem bàn người khác** thanh xanh vẫn là tướng của mình nhưng vị trí khác | Không phụ thuộc vị trí: neo theo thanh máu |
| Tướng trên hàng chờ cũng có thanh máu | Đồ trên tướng hàng chờ **vẫn tính** là đồ đang cầm. Chỉ ghi thêm vị trí (bàn / hàng chờ) theo vùng `bench` |

## Related

- [overview](overview.md) · [bench-components](bench-components.md) · [core-items](core-items.md) · [evaluation](evaluation.md)
