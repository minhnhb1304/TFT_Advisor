# Chandra OCR Host Trên Modal

Nghiên cứu 2026-11-07, mức low (3 agent: Chandra tiếng Anh, Chandra tiếng Trung, Modal tiếng Anh).
Nguồn tiếng Trung gần như chỉ là tin đăng lại; bằng chứng chính lấy từ model card HF, issue
GitHub và tài liệu Modal. **Chưa chạy thử**: máy không có GPU NVIDIA, chưa có tài khoản Modal.

## Kết luận

> **Cập nhật 2026-11-15:** đã đo thật — xem [261115-ocr-bench.md](261115-ocr-bench.md) (RapidOCR 225/225, indra-ocr 222/225 với 2 lỗi sai; Chandra 2 chuyển sang đo trên Modal).

**Không nên theo hướng này cho bài toán đọc tên lõi.** Chandra kém Gemini ở tiếng Việt, chưa
ai thử trên ô chữ nhỏ hoặc chữ trong game, và host trên Modal chỉ nhanh hơn 2,2 s nếu giữ GPU
nóng (tốn tiền mỗi giờ).

| Câu hỏi | Trả lời | Mức chắc |
|---|---|---|
| Chandra là gì | VLM OCR của Datalab. `datalab-to/chandra` (9B, nền Qwen3-VL, 10/2025) và `datalab-to/chandra-ocr-2` (~5,3B theo HF, Datalab nói "4B", nền Qwen 3.5, 3/2026) | Cao |
| Giấy phép | Code Apache-2.0; trọng số OpenRAIL-M sửa đổi: miễn phí cho nghiên cứu, cá nhân, startup < $2M; cấm cạnh tranh với API của Datalab | Cao |
| Tiếng Việt | Bảng 43 ngôn ngữ của chính Datalab, dòng `vi`: **Gemini 2.5 Flash 89,5%**, Chandra 1 81,6%, **Chandra 2 80,4%** | Cao (nhưng là trang tài liệu, không phải chữ trong game) |
| Ô chữ nhỏ | Nhận được, nhưng thư viện phóng cạnh ngắn lên 1536 px; chỉ có 2 prompt (`ocr`, `ocr_layout`), ra HTML | Cao về code; chưa rõ ảnh hưởng độ chính xác |
| Độ ổn định | Issue #116: chữ trong **khung có viền** làm model lặp token, ra rác — thẻ lõi có khung như vậy. #51, #71: lặp token, trả rỗng | Trung bình (chưa rõ đã sửa ở bản 2 chưa) |
| Tốc độ | RTX 3090 + vLLM: 3,27 s/trang khi gửi lẻ. Ô chữ nhỏ ra ít token nên có thể < 1 s — **chưa đo** | Trung bình |
| VRAM | Trọng số bf16 ~10,6 GB; script có preset từ T4 16 GB tới H100 | Trung bình |

## Modal

| Mục | Nội dung |
|---|---|
| Mẫu nên dùng | `vllm_low_latency.py` (GPU snapshot, `min_containers`, `routing_region`) và `vllm_snapshot` (Ministral 3, model có ảnh) trong `modal-labs/modal-examples` |
| Giá GPU | L4 $0,80/h · L40S $1,95/h · A100-80 $2,50/h · H100 $3,95/h; gói Starter tặng **$30/tháng** |
| Cold start | Không snapshot: vài chục giây tới ~2 phút (Ministral 3 ~118 s). Có GPU snapshot: ước ~10 s với model 8–10B. **Đều quá xa mục tiêu 2,2 s** |
| Giữ nóng | `min_containers=1`: ~$19/ngày (L4) tới ~$95/ngày (H100). Rẻ hơn: gửi request khởi động khi vào ván, `scaledown_window` 20 phút → ~$0,8 (L4) mỗi ván |
| Vùng | Không có điểm định tuyến ở Đông Nam Á; gần nhất `ap-south` (Mumbai). Mặc định đi qua us-east, RTT từ Việt Nam ước 220–280 ms. Ghim vùng nhân giá 1,15–1,75 |
| Mẫu OCR có sẵn | Chỉ có Marker chạy hàng đợi batch; không có mẫu Chandra/olmOCR |

## So với hiện tại

| Đường | Tên lõi đúng | Độ trễ | Chi phí, phụ thuộc |
|---|---|---|---|
| Gemini Flash Lite (đang dùng) | F1 0,986 | trung vị 2,2 s | API, có mạng |
| RapidOCR + khớp danh mục | 107/111, sai 0 | vài chục ms (chưa đo đủ) | Cục bộ, CPU |
| Chandra trên Modal | chưa đo; tiếng Việt kém Gemini trên trang tài liệu | ước 0,5–1,5 s khi nóng; 10 s–2 phút khi nguội | GPU trả theo giờ, có mạng |

Chandra vẫn cần mạng như Gemini, nên không giải quyết được nỗi lo "phụ thuộc online". Muốn chạy
cục bộ thì RapidOCR + danh mục đã mạnh hơn.

## Hướng phụ đáng thử hơn

`datalab-to/indra-ocr` (Datalab, 10/2026): **1,25M tham số, ONNX, chạy CPU, có `vi`**. Có thể đo
miễn phí trên máy này bằng `titles.py` như các model HF trước. Chưa kiểm định dạng vào/ra.

## Câu hỏi còn mở

- Chandra 2 thực sự 4B hay 5,3B; bản nhỏ chỉ bán qua sales.
- Độ chính xác và giữ hậu tố `+` trên ô chữ ~400×60 px sau khi phóng lên 1536 px.
- RTT thật từ Việt Nam tới `ap-south`; GPU có sẵn ở vùng AP không.
- Lỗi #116 còn ở Chandra 2 không.

## Nguồn

- https://huggingface.co/datalab-to/chandra-ocr-2 · https://github.com/datalab-to/chandra · https://www.datalab.to/blog/chandra-2
- https://github.com/datalab-to/chandra/issues/116 · /issues/51 · /issues/70
- https://huggingface.co/datasets/simonlesaumon/chandra-ocr-2-rtx3090-vllm-benchmark
- https://modal.com/pricing · https://modal.com/docs/guide/cold-start · https://modal.com/docs/guide/region-selection
- https://github.com/modal-labs/modal-examples/blob/main/06_gpu_and_ml/llm-serving/vllm_low_latency.py
- https://huggingface.co/datalab-to/indra-ocr

## Related

- [vision-stack/](vision-stack/): lựa chọn OCR và VLM trước đây
- [overview.md](overview.md)
