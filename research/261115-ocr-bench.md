# Đo OCR Tên Thẻ Lõi

Đo thực nghiệm 2026-11-15 (máy Ryzen 9 8945H, 28 GB RAM, chỉ CPU). Bổ sung cho
[261107-chandra-modal.md](261107-chandra-modal.md), nơi indra-ocr và Chandra 2 bị loại chỉ dựa trên tài liệu.

## Kết luận

**Giữ RapidOCR + khớp danh mục.** Trên 225 lượt đọc thẻ (117 ô khác nhau, 7 video development),
RapidOCR đúng 225/225; indra-ocr đúng 222/225, nhanh hơn ~1,9 lần nhưng có **2 lỗi sai im lặng**
ở hậu tố số La Mã (`II` ↔ `III`) — đúng loại lỗi tệ nhất cho người chơi. Chandra 2 **chưa đo**:
dừng theo yêu cầu (lo tải máy) khi trọng số mới tải 8,2/10,6 GB → chuyển sang đo trên Modal.

## Kết quả

| Backend | Mọi offer (n = 225): đúng / sai / sót | Offer cuối (n = 63) | p50 | p95 |
|---|---|---|---|---|
| RapidOCR (det + cls + rec, như `OcrCardReader`) | **225 / 0 / 0** | 63 / 0 / 0 | 315 ms | 461 ms |
| indra-ocr 1.1.2 (`mode="ocr"`, 8 luồng) | 222 / **2** / 1 | 62 / 0 / 1 | **169 ms** | **266 ms** |
| chandra-ocr-2 | chưa đo | — | — | — |

Độ trễ = một ô thẻ (~280×185 px), đã bỏ lượt khởi động; không tính thời gian nạp model.
CSV chi tiết: `data/eval/runs/bench_card_titles_{rapidocr,indra}.csv`.

## Lỗi của indra-ocr

| Mẫu | Nhãn | indra đọc (dòng đầu) | Khớp ra | Loại |
|---|---|---|---|---|
| minh_02 3-2 offer 2 ô 3 | `DA_BronzeForLifeII` | `Tất Tay Bậc Đồng lI` | `DA_BronzeForLifeI` | **sai** — `l` thay `I`, khớp mờ chọn bậc I |
| minh_04 4-2 offer 1 ô 3 | `DA_VerticalityIII` | `Chi Một Con Đường II` | `DA_VerticalityII` | **sai** — rơi một `I` |
| minh_05 2-1 offer 4 ô 2 | `DA_Warpath` | `Đường` / `Ra` / `Ra` / `Trận` | — | sót — tên bị tách thành 4 dòng |

Dấu tiếng Việt của indra rất tốt (`Bài Học Sơ Khai`, `Hạ Đo Ván+`, `Đầu Tư++` đọc đúng nguyên văn);
lỗi nằm ở chữ hẹp `I`/`l` và cách tách dòng. Hậu tố `+`/`++` không thấy lỗi.

## Chandra 2 — đã làm gì

| Việc | Trạng thái |
|---|---|
| Cài `chandra-ocr[hf]` 0.2.0 + torch 2.15.0+cpu + transformers 5.23.0 vào `.venv-bench` | Xong |
| Tải `datalab-to/chandra-ocr-2` (`model.safetensors` 10,59 GB) | **Dừng ở 8,18 GB** (file `.incomplete` trong cache HF) |
| Phép thử khói 1 thẻ (trần 3 phút, RAM ≤ 18 GB) | Không chạy được: thiếu trọng số |
| Backend `chandra2` trong script | Có: `CHANDRA_URL` → endpoint vLLM (Modal) qua `chandra.model.vllm.generate_vllm`; không đặt → HF trên CPU |

Ước lượng (chưa đo): ô thẻ ~280×185 px nằm trên ngưỡng `min_size` của `scale_to_fit` nên
**không** bị phóng lên 1536 px → ít token ảnh; nhưng mỗi token sinh ra phải đọc ~10,6 GB trọng số bf16
qua RAM (≥ ~0,2 s/token theo băng thông DDR5), nên với ~100 token/thẻ là hàng chục giây mỗi thẻ.

## Giới hạn

- **Tập development, không phải held-out.** RapidOCR + danh mục đã được chỉnh trên chính các video này
  (minh_01/02 từ M0–M2), nên 225/225 có lợi thế sân nhà; indra thì chưa từng chỉnh gì.
- Mọi offer: ô không đổi sau reroll được đếm lại — 225 lượt nhưng chỉ 117 ô khác nhau, 94 lõi khác nhau.
- Ảnh là snapshot JPG nén từ video, không phải khung chụp trực tiếp.
- CPU, không GPU. RapidOCR dùng số luồng mặc định của onnxruntime; indra đặt 8 luồng.
- Cả hai backend đọc **toàn ô** rồi đưa mọi dòng vào cùng `resolve_name` (ngưỡng 0,82) — khác biệt chỉ
  từ bước đọc chữ.

## Cài đặt

| Model | Cách cài | Dung lượng tải |
|---|---|---|
| RapidOCR | đã có trong `.venv` | — |
| indra-ocr | `uv venv .venv-bench --python 3.11` → `uv pip install --python .venv-bench indra-ocr`; model tự tải lần đầu (tag `v1.1.0`) | ~76 MB |
| chandra-ocr-2 | `uv pip install --python .venv-bench "chandra-ocr[hf]" --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple --index-strategy unsafe-best-match` | 10,6 GB (đã tải 8,2 GB, dở) |

Chạy lại: xem docstring của `scripts/bench_card_titles.py`; `--report` in bảng trên giao các CSV.

## Gợi ý tiếp

- Đo Chandra 2 trên Modal với `CHANDRA_URL`, cùng tập 225 (hoặc mẫu `--sample 40 --seed 20261115`).
- indra chỉ đáng cân nhắc nếu cần nhanh hơn ~150 ms/thẻ; khi đó phải chặn khớp mờ lẫn bậc I/II/III.

## Related

- [261107-chandra-modal.md](261107-chandra-modal.md)
- [vision-stack/](vision-stack/)
- [overview.md](overview.md)
