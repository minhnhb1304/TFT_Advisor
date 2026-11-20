# Admin Hub Phases

Tổng khoảng 3,5 ngày, dự kiến 22–26/11/2026, trên nhánh `feat/admin-hub`. Mỗi phase một commit, `pytest` xanh trước khi sang phase sau.

## P1 · Lõi server dùng chung + feature đầu tiên (0,75 ngày)

| Việc | File |
|---|---|
| Server dùng chung: bảng route theo tiền tố, `send`/`json`, phục vụ `file/<relpath>` có chặn thoát khỏi repo, `atomic_write_json`, mở trình duyệt, vòng `serve_forever` | `src/admin_hub/server.py` (mới) |
| Giao diện feature: `name`, `html_path`, `state()`, `save(payload)`, `extra_routes` | `src/admin_hub/feature.py` (mới) |
| Chuyển **review_core_items** (trang đơn giản nhất) sang feature; script cũ thành vỏ mỏng, giữ nguyên cổng 8767 và tham số | `src/admin_hub/features/core_items.py`, `scripts/review_core_items.py` |
| HTML đổi `/api/…`, `/file/…` sang đường dẫn tương đối | `scripts/review_core_items.html` |

**Test** `tests/test_admin_hub_server.py`: định tuyến theo tiền tố; `file/../..` bị chặn; ghi nguyên tử không để lại `.tmp`. Test có sẵn `tests/test_core_items.py` vẫn xanh.

## P2 · Chuyển 3 trang còn lại (0,75 ngày)

| Trang | Lưu ý |
|---|---|
| `review_augment_features` | Giữ khoá ghi và ghi nguyên tử sẵn có; `migrate_review` vẫn import được, vì `apply_manual_review.py` dùng nó |
| `review_item_labels serve` | Chỉ gộp phần `serve`; `build`/`templates` giữ nguyên; cổng mặc định khi chạy riêng đổi 8766 → **8768** để hết trùng |
| `review_playtest_labels` | File nhãn chọn theo URL `/review/playtest/<stem>/`, chỉ nhận file trong `data/eval/playtest/`; giữ route `api/snapshot` |

Ghi file của 3 trang này chuyển sang `atomic_write_json`.

**Test:** `tests/test_review_augment_features.py`, `tests/test_playtest_eval.py` vẫn xanh; thêm test `stem` có `..` hoặc file ngoài thư mục bị từ chối. **Kiểm tay:** chạy riêng từng script cũ, lưu 1 thay đổi rồi hoàn tác, `git diff data/` sạch.

## P3 · Hub + tab Tổng quan (0,5 ngày)

- `scripts/admin_hub.py` (cổng 8770) gắn cả 4 feature và các API của hub. `scripts/admin_hub.html` có 4 tab.
- Hàm thuần `build_overview(root)`:
  - `meta`/`_meta` của từng `data/*.json` (`generated_at` hoặc `fetched_at`, `patch`, `source`), `patch_state.json`;
  - đếm `split.json` theo `role`, đếm file nhãn video;
  - đếm `extraction_method` theo nguồn, verdict của file duyệt;
  - cảnh báo: số bản sửa trường định danh chưa áp (lấy từ phần đếm của `apply_manual_review.py`), dòng chưa duyệt.
- Lệnh cập nhật dữ liệu chỉ hiện ra để copy.

**Test** `tests/test_admin_hub.py`: `build_overview` trên thư mục tạm (file có `meta`, `_meta`, không có meta) trả đúng các trường.

## P4 · Bảng đặc trưng chỉ đọc (0,5 ngày)

- `GET /api/features`: tên, `api_name`, `categories`, `econ_type`, `econ_value`, `tempo`, `carry_type`, `offer_rounds`, nguồn nhãn rút gọn, verdict. Lọc và tìm trên trình duyệt; bấm một dòng thì hiện mô tả tiếng Anh (`cdragon_cache/en_us.json`).

**Test:** `manual-audit:tempo (from llm:…)` rút gọn thành `duyệt tay · tempo`.

## P5 · Job: đánh giá + áp bản duyệt (0,5 ngày)

| Job | Lệnh | Timeout |
|---|---|---|
| `plan_advice` | `eval_plan_advice.py` + tập dev từ `split.json` | 60 s |
| `item_reading` | `eval_item_reading.py` | 60 s |
| `offline_eval` | `run_evaluation.py` (không `--with-augment`, không `--export-experts`) | 120 s |
| `apply_review_dry` / `apply_review_write` | `apply_manual_review.py` / thêm `--write`, chỉ chạy khi có `confirm: true` | 60 s |

Mỗi lần chỉ chạy một job (`threading.Lock`), qua `subprocess.run` với Python của `.venv`. Stdout ghi vào `.cache/admin_hub/<job>-<thời gian>.txt`.

**Test:** job lạ bị từ chối; `apply_review_write` thiếu `confirm` bị từ chối; dòng lệnh của từng job dựng đúng.

## P6 · Hoàn thiện + tài liệu (0,5 ngày)

- `.gitignore` thêm `.cache/`. Ghi lệnh mở hub vào `next-steps.md`.
- Chụp 2–3 ảnh (Tổng quan, Bảng đặc trưng, Đánh giá) vào `local_docs/bao-cao/hinh/chuong-3/`.
- Kiểm tay toàn luồng: mở hub → dùng cả 4 trang duyệt → chạy 3 job → áp bản duyệt ở chế độ chạy thử → `git diff data/` sạch.

## Tiêu chí xong

- [ ] `.venv\Scripts\python scripts\admin_hub.py` mở đủ 4 tab, 4 trang duyệt chạy trong hub, console không lỗi.
- [ ] 4 script cũ vẫn chạy riêng được; không còn hai trang trùng cổng.
- [ ] Demo được UC-05, UC-06, UC-09 chỉ bằng chuột.
- [ ] Không file `data/` nào bị đổi nếu người dùng không bấm lưu hoặc "Áp bản duyệt (ghi)".
- [ ] `pytest` xanh; test mới không bật server thật.

## Related

- [overview.md](overview.md)
