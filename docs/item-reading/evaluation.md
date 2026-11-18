# Evaluation

Đo phần đọc đồ và ảnh hưởng lên tư vấn lõi. Thuộc [item-reading](overview.md).

## Dữ liệu

Hiện **không có nhãn đồ nào**: nhãn playtest chỉ có HUD + thẻ lõi. `src/eval/recognition.py` đã có loại thực thể `"item"` (P/R/F1 + latency) nhưng chưa có gì sinh dự đoán.

| Bộ | Nguồn | Cỡ | Ai làm |
|---|---|---|---|
| Nhãn đồ trên tướng | Khung cắt từ video **development** ở vòng chuẩn bị trước 2-1, 3-2, 4-2 (lúc ItemFit được dùng) | ~60 khung, ~300 ô đồ | Bộ đọc điền trước, **bạn sửa** trong trang review local (mẫu `scripts/review_playtest_labels.py`) |
| Nhãn mảnh trên băng ghế | Khung tìm được ở [bench-components](bench-components.md) I2.0 | ≥ 30 khung | Như trên |
| Kiểm cuối | Cùng cách lấy, trên video **held-out** | ~30 khung | Chỉ chấm một lần sau khi đóng băng ngưỡng |

Công cụ: `scripts/review_item_labels.py` (`build` chọn khung + máy điền trước, `serve` mở trang 127.0.0.1, `templates` cắt ô đã kiểm làm mẫu). Nhãn ở `data/eval/items/unit_items.json`.

**Tránh rò rỉ:** mẫu icon cắt từ chính các khung dev. Khi đo precision trên dev thì đo chéo theo video: `templates --exclude <video>` rồi chấm video đó, lặp cho từng video.

Quy tắc split giữ như cũ: chỉnh ngưỡng chỉ trên development; held-out chỉ để báo số. Bảng core 18.6 dùng được trên dev 18.2/18.3 vì đồ hợp tướng không đổi theo bản (xem [core-items](core-items.md)).

## Chỉ số

| Chỉ số | Mục tiêu | Ghi chú |
|---|---|---|
| Precision đọc đồ | ≥ 0,95 | Đọc sai tệ hơn không đọc (cùng nguyên tắc với bộ đọc thẻ) |
| Recall đọc đồ | báo số, không đặt sàn | "Chưa rõ" được phép |
| Bộ đồ cuối ván có khớp `ứng_viên(plan.route)` không: ở vòng cuối, có tướng nào cầm đủ một bộ core của ứng viên hướng đã gắn nhãn | báo số | Không cần nhãn mới: dùng nhãn `plan` có sẵn + bộ đọc đồ. Vai chính/phụ lấy từ comp TFT Academy |
| Tỷ lệ lùi: số màn chọn lõi mà đồ đã ghép không khớp comp TFT Academy nào | báo số | Đo độ phủ của mẫu chuẩn 18.6 trên ván 18.2/18.3 |
| `item_ms` p50/p95 trong `data/live_logs` | p95 < 200 ms | Đọc ngoài màn chọn lõi nên không cộng vào độ trễ khuyên |
| Ảnh hưởng lên tư vấn lõi | báo số | Chạy `scripts/eval_plan_advice.py` có/không có đồ trên 15 quyết định dev. Có thể **không đổi** nếu ít lõi tặng đồ được chào — phải báo thật |

## Kết quả dev 2026-11-18 (`scripts/eval_core_fit.py`, chưa có mẫu cắt từ game)

| Đo | Số |
|---|---|
| Màn đọc được đồ trước khi mở màn chọn lõi | 10/15. **Cả 5 màn 2-1 không có đồ trên tướng**; mảnh chưa lắp chưa đọc được ([bench-components](bench-components.md)) |
| Tỷ lệ lùi (có đồ ghép nhưng không comp nào khớp) | 1/10 (`dat_01` 3-2) |
| CoreFit đổi top-1 của hướng thật | 0/15. Chấp lõi kích hoạt 0 màn |
| Top-1 khớp lựa chọn người chơi | tắt 9/15 · bật 9/15 |

Đúng như rủi ro đã ghi: ít lõi tặng đồ được chào ở các màn dev. Số trên vẫn gồm lỗi đọc đồ, vì precision chưa đo (chờ nhãn).

## Câu hỏi cần trả lời trong chương kết quả

1. Đọc đồ trên tướng từ pixel đạt precision bao nhiêu trên client VN?
2. Bao nhiêu % màn chọn lõi mà ItemFit có dữ liệu thật (không còn trung tính)?
3. Có màn nào thứ tự khuyên đổi nhờ biết đồ không, và đổi có đúng ý người chơi không?

## Related

- [overview](overview.md) · [unit-items](unit-items.md) · [bench-components](bench-components.md) · [core-items](core-items.md)
