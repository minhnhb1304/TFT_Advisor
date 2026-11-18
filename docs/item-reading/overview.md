# Item Reading

Kế hoạch 2026-11-17: đọc đồ từ pixel để **ItemFit trong điểm lõi có dữ liệu thật**. Giữ phạm vi 2026-10-31: không có advisor đồ riêng, không có panel đồ trên overlay.

## Vì sao

`ItemFit` (`src/decision/scoring/item_fit.py`) và `ItemAdvisor` đã có code nhưng **chưa từng chạy với dữ liệu thật**: không có bộ đọc nào, nên trong `LiveSession` thì `item_components`, `completed_items`, `board` luôn rỗng và ItemFit luôn trung tính.

## Phạm vi

| Trong | Ngoài |
|---|---|
| Đồ trên tướng mình (3 icon dưới thanh máu xanh) | Panel "ghép gì" trên overlay |
| **Chỉ đồ thường**: 10 mảnh, đồ ghép, ấn (65 món trong `item_recipes.json`) | Đồ ánh sáng, đồ tạo tác, đồ đặc biệt khác: bộ đọc để "chưa rõ" (bạn chốt 2026-11-17) |
| Mảnh đồ trên băng ghế đồ | Nhận diện tên tướng trên bàn (để Future Work) |
| Bảng đồ core theo tướng (có nhóm thay thế), 4 vai carry/tank chính/phụ | Đồ trên tướng địch |
| ItemFit dùng "mảnh đang thiếu để ghép core cho vai ưu tiên nhất" | Chọn đồ ở băng chuyền / kho đồ |

## Các bước

| # | Việc | Tài liệu | Tuần | Trạng thái 2026-11-18 |
|---|---|---|---|---|
| I0 | Sửa lệch tên đồ giữa ItemFit/BoardFit và `item_recipes.json` | [core-items](core-items.md) | 7 | Xong |
| I1 | Đọc đồ trên tướng, neo theo thanh máu | [unit-items](unit-items.md) | 7–8 | Bộ đọc + gắn vào live xong; chờ nhãn để đo |
| I2 | Đọc mảnh trên băng ghế (tìm mẫu trước, có thể gần như luôn trống) | [bench-components](bench-components.md) | 9–10 | Xong 2026-11-18: thanh dọc mép trái, 10 ô cố định; 15/15 màn dev đọc được đồ |
| I3 | Bảng đồ core 18.6 + suy carry + thưởng core theo hướng | [core-items](core-items.md) · [plan-item-fit](plan-item-fit.md) | 9 | Bảng sinh xong (chờ duyệt), CoreFit + chấp lõi đã gắn |
| I4 | Gắn nhãn, đo, báo số | [evaluation](evaluation.md) | 8–11 | Có số dev đầu tiên; precision chờ nhãn |

Tuần 7 = 2026-11-16. **Tuần 12 (từ 2026-12-21) đóng băng số**: mọi ngưỡng phải chốt trước đó.

## Thứ tự và lý do

- **I0 trước tiên**: rẻ, và nếu không sửa thì mọi thứ đọc được đều không khớp.
- **I1 trước I2**: bạn thường lắp đồ ngay khi nhận. Đồ trên tướng mới là nguồn dữ liệu chính.
- **I3 cần I1**: muốn biết "carry đang thiếu gì" thì phải biết carry đang cầm gì.

## Kết luận nghiên cứu (2026-11-17)

- Hai repo Set 18 độc lập (TFT-Copilot, Agente-TFT) cùng đo icon đồ dưới tướng là 23 px, neo theo thanh máu. Video của mình xác nhận vị trí và kích thước này.
- **Không repo nào công bố độ chính xác trên ván thật.** Số đo trên client VN sẽ là đóng góp riêng.
- Băng ghế đồ trên client này là các ô 3D trong sàn đấu, khác hẳn mô tả của các repo khác. Phải tự đo.
- Nguồn đồ core 18.6: TFT Academy comps (đồ từng tướng theo hướng) là nguồn chính; tactics.tools (thống kê theo tướng) để đối chiếu. `mainChampion` không phải lúc nào cũng là carry.
- Chi tiết: [research/261117-tft-item-recognition/](../../research/261117-tft-item-recognition/en-recognition.md).

## Quyết định cần bạn chốt

1. ~~Suy carry từ đồ + tộc hay chỉ theo loại AD/AP?~~ **Chốt 2026-11-17:** không suy từ tộc (người chơi xoay đội hình). Carry suy **theo từng hướng**: hướng → cấp → giá carry, lọc bằng đồ đang cầm. Không cần tên tướng trên bàn. Đội hình có 4 vai (carry chính/phụ, tank chính/phụ). Xem [core-items](core-items.md).
2. ~~Ngưỡng "core" theo thống kê~~ **Chốt:** core theo (tướng, vai), có nhiều bộ thay thế (Aphelios: Guinsoo hoặc IE + Kraken; Ahri: Găng + Shojin, Găng + Nashor vẫn đúng). Tank không có core, dùng bậc đồ TFT Academy (Gargoyle là đồ quá mạnh, không phải core). Các tướng nêu tên chỉ là ví dụ: bảng core **sinh bằng thuật toán cho mọi tướng** từ TFT Academy + CDragon, ví dụ thành test. Bạn duyệt bảng sinh ra (~1 giờ). Hướng "Thiếu tiền" **để sau**.
3. ~~Patch, lõi tặng đồ, thời điểm đọc, nhãn carry~~ **Chốt 2026-11-17:** bảng core 18.6 dùng cho dev (đồ hợp tướng không đổi theo bản, chỉ mạnh/yếu đổi); mảnh nào cũng dùng được, chỉ thưởng khi đúng core, lò rèn nhỉnh hơn một mảnh; đọc đồ đầu mỗi vòng; vai chính/phụ lấy từ comp TFT Academy, không cần nhãn carry. Ứng viên mỗi hướng là **comp TFT Academy** (mẫu chuẩn), lọc theo style + đồ đã ghép; không khớp thì lùi về tướng theo giá và báo tỷ lệ lùi.
4. Gắn nhãn ~60 khung đồ trên tướng (máy điền trước, bạn sửa), ước tính 1–2 giờ, song song với gắn nhãn held-out tuần 9–11.

## Rủi ro

| Rủi ro | Ứng phó |
|---|---|
| Đọc đồ chậm làm chậm vòng live | Chỉ đọc đầu mỗi vòng, ngoài màn chọn lõi; đo `item_ms` |
| Endpoint tactics.tools / TFT Academy đổi hoặc chặn | Crawl một lần cho 18.6, lưu file vào repo; 18.6 là patch cuối nên không cần crawl lại |
| ItemFit có dữ liệu nhưng không đổi thứ tự khuyên | Vẫn báo số thật; đó là kết quả, không phải lỗi |
| Riot cấm overlay hiển thị thông tin làm thay đổi lối chơi ngay lập tức | Đồ chỉ vào điểm lõi, không có panel đồ riêng |

## Related

- [unit-items](unit-items.md) · [bench-components](bench-components.md) · [core-items](core-items.md) · [plan-item-fit](plan-item-fit.md) · [evaluation](evaluation.md)
- [Kế hoạch đã duyệt](../../local_docs/ke-hoach-do-an-da-duyet.md) — hàng 4 có tư vấn đồ
- [next-steps](../next-steps.md)
