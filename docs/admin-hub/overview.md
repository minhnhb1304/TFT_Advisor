# Admin Hub

Trang quản trị cục bộ cho actor **Người quản trị tri thức** (UC-04…UC-09, Hình 2.1). Kế hoạch lập 2026-11-20, làm sau buổi kiểm tra 21/11.

## Mục tiêu

- Gom các công cụ đang rời rạc (4 trang duyệt, khoảng 40 script dòng lệnh) vào **một trang** `http://127.0.0.1:8770/`.
- Demo được UC-05, UC-06, UC-09 trước hội đồng mà không cần gõ lệnh; có ảnh chụp cho chương 3.
- Làm lộ trạng thái dữ liệu (phiên bản, nguồn nhãn, cảnh báo) ở một chỗ.

**Không làm:** CSDL, đăng nhập/phân quyền, nút chạy script crawl/fetch (dữ liệu đã chốt 18.6), viết lại 4 trang duyệt.

## Hiện trạng (khảo sát 2026-11-20)

| Trang | Cổng | Ghi vào |
|---|---|---|
| `review_playtest_labels.py <labels>` | 8765 | file nhãn video |
| `review_augment_features.py` | 8766 | `data/eval/augment_feature_review.json` (ghi nguyên tử) |
| `review_core_items.py` | 8767 | `core_items.overrides.json` rồi sinh lại `core_items.json` |
| `review_item_labels.py serve` | **8766** (trùng) | `data/eval/items/unit_items.json` |

Cả 4 trang dùng `ThreadingHTTPServer` của thư viện chuẩn, cùng khuôn: `GET /`, `GET /api/state`, `POST /api/save`. Repo không có Flask/FastAPI, nên hub cũng dùng thư viện chuẩn.

## Thiết kế

**Một server, 4 trang duyệt gộp vào làm tính năng** (D1, chốt 2026-11-20).

```
admin_hub.py (8770) ──┬─ /api/overview            đọc meta các file data/, split.json, nguồn nhãn
                      ├─ /api/features            bảng đặc trưng (chỉ đọc)
                      ├─ /api/jobs                chạy script trong danh sách trắng, 1 job/lần, timeout
                      ├─ /review/playtest/<stem>/ ┐
                      ├─ /review/features/        │ 4 trang duyệt cũ, mỗi trang một "feature":
                      ├─ /review/core-items/      │ GET / · GET api/state · POST api/save · GET file/…
                      └─ /review/item-labels/     ┘
admin_hub.html ── 4 tab: Tổng quan · Duyệt & gắn nhãn · Bảng đặc trưng · Đánh giá
```

- Tách lõi xử lý của mỗi trang thành một **feature** dùng chung giao diện `state()`, `save(payload)`, `extra_routes`, nằm trong `src/admin_hub/`. Script cũ (`scripts/review_*.py`) chỉ còn là vỏ mỏng gắn đúng một feature vào server dùng chung, nên **chạy riêng như cũ vẫn được**.
- Trong 4 file HTML, đổi đường dẫn tuyệt đối (`/api/state`, `/api/save`, `/api/snapshot`, `/file/…`) sang **tương đối** (`api/state`…), để trang chạy được cả ở gốc `/` lẫn dưới tiền tố `/review/<tên>/`.
- Bỏ được 4 bản sao của đoạn khởi tạo server (`_send`, `_json`, `log_message`, vòng `serve_forever`). Mỗi feature có khoá ghi riêng, vì giờ 4 trang chạy chung một tiến trình.
- Ngoài phạm vi gộp: các lệnh `build`/`templates` của `review_item_labels.py` vẫn chạy bằng dòng lệnh như cũ.

| Tab | Use case | Nội dung |
|---|---|---|
| Tổng quan | UC-07, UC-08 | Phiên bản 18.6, `generated_at`/`fetched_at` từng file; số dòng theo nguồn nhãn (luật / LLM / duyệt tay); số video dev/held-out; **cảnh báo** (44 bản sửa `item_grants` chờ extractor v2, dòng chưa duyệt). Lệnh cập nhật chỉ **hiện để copy**, không chạy |
| Duyệt & gắn nhãn | UC-05, UC-06 | 4 trang duyệt ngay trong hub (chọn file nhãn video từ danh sách); nút **Áp bản duyệt**: chạy thử trước, xem báo cáo, xác nhận rồi mới `--write` |
| Bảng đặc trưng | UC-06 | Tìm theo tên; lọc theo loại, nguồn nhãn, vòng xuất hiện, `econ_type`; xem chi tiết một lõi |
| Đánh giá | UC-09 | Nút chạy `eval_plan_advice` (0,6 s), `eval_item_reading` (3,5 s), `run_evaluation` (9 s); hiện kết quả lần chạy gần nhất |

## Quyết định (chốt 2026-11-20)

| # | Câu hỏi | Chốt |
|---|---|---|
| D1 | Bật 4 trang con bằng subprocess, hay gộp vào một server? | **Gộp**: 4 trang thành 4 feature của hub |
| D2 | Có nút **ghi** "Áp bản duyệt" (`--write`) không? | Có, kèm bước xác nhận; script đã tự chặn khi vi phạm bất biến |
| D3 | Log các lần chạy đánh giá lưu ở đâu? | `.cache/admin_hub/` (thêm vào `.gitignore`), không lẫn vào `data/` |

## An toàn

- Chỉ bind `127.0.0.1`.
- Job lấy từ **danh sách trắng cố định**, không nhận tham số tự do từ trình duyệt.
- Đường dẫn file kiểm tra nằm trong repo, giống `GET /file/` của các trang hiện có.
- Ghi file theo kiểu nguyên tử (`.tmp` rồi `replace`) cho cả 4 feature. Hiện chỉ trang đặc trưng làm vậy.

## Related

- [phases.md](phases.md): các bước, test, tiêu chí xong
- [../next-steps.md](../next-steps.md): dòng 6 (`item_grants`)
