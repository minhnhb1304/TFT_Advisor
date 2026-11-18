# Patch Data

Mỗi video được chấm bằng dữ liệu của **đúng bản nó được chơi**. Chốt 2026-11-10, khi chuyển
từ 18.5b sang 18.6.

## Vì sao

15 video trong [split.json](../../data/eval/split.json) quay 16–25/09, nhưng `data/` đã lên
18.5b hôm 26/10. 6 ván development chạy replay hôm 06/11 bị chấm bằng tier và comp của một patch
mà người chơi chưa từng chơi. Chuyển sang 18.6 mà không tách theo patch thì độ lệch càng lớn.

## Video thuộc bản nào

| Nhóm | Ngày quay | `game_patch` | `data_patch` |
|---|---|---|---|
| minh_01–03, dat_01–05 | 16–21/09 | 18.2 (ra 10/09) | 18.2 |
| minh_04–10 | 24–25/09 | 18.3 (ra 23/09) | **18.2**: repo chưa từng có dữ liệu 18.3 |
| Video mới (mọi người chơi); maris_01–08 (VOD giải, 2026-11-15) | từ 11/2026 | 18.6 | 18.6 |

`game_patch` suy từ ngày quay trong tên file gốc. 18.3 chỉ buff vài lõi chiến đấu và tướng, nên
dùng 18.2 là xấp xỉ gần nhất; phải ghi giới hạn này trong chương đánh giá.

## Cái gì theo patch, cái gì dùng chung

| Theo patch (`PATCH_KEYS` trong `src/utils/settings.py`) | Dùng chung |
|---|---|
| tier lõi (TFT Academy, MetaTFT), `augment_stats.csv`, meta comp (2 nguồn), `item_stats`, `patch_state` | bảng đặc trưng lõi (nhãn tay), công thức đồ, giá tướng, `name_index` |

Bảng dùng chung là **cơ chế**, và là tập cha của bản cũ: lõi bị bỏ vẫn giữ nhãn qua
`data/augment_overrides.json`, tên cũ vẫn tra được qua alias.

Giới hạn còn lại: cờ `live` (pool đổi lõi) theo bản hiện tại, không theo patch của video.

## Cách dùng

| Việc | Lệnh / API |
|---|---|
| Replay một video | `run_replay.py --video minh_05.mp4`: `--patch auto` tra `split.json` theo tên file |
| Trong code | `Settings.load().for_patch(data_patch_for(video_id))` (`src/eval/dataset_split.py`) |
| Thêm snapshot | `data/patches/<patch>/` chứa đủ file của `PATCH_KEYS`; thiếu file là **báo lỗi ngay** |
| Bản 18.5b | git tag `data-18.5b` (không có video nào dùng) |

## Quy tắc chia tập cho 18.6

- **Mọi video 18.6 → held-out**, của mọi người chơi. 9 video development (minh_01–08, dat_01) giữ nguyên.
- **18.6 là patch cuối cùng**: không đưa patch mới vào bộ đánh giá, kể cả khi Riot ra 18.7.
- Quy tắc nằm ở `patch_rule` trong `split.json`, ghi trước khi quay video 18.6 đầu tiên.
- **2026-11-18: Riot ra 18.7. `data/` đóng băng ở 18.6**, không cập nhật theo nữa, kể cả cho demo live (bạn chốt). Không chạy lại các script kéo dữ liệu mạng: `crawl_tftacademy_guides.py`, `crawl_datatft_augments.py`, `fetch_*_icons.py`, và các client trong `src/knowledge/` (CDragon, MetaTFT, tactics.tools, TFT Academy, lolchess). Đường live chỉ đọc file local nên không tự kéo 18.7.
- Hệ quả: không quay thêm được ván 18.6. Held-out 18.6 = `maris_01`–`08` + các ván bạn đã quay trên 18.6 (`minh_11`–`14`, `chien_01`, chờ ghi vào `split.json`); nếu cần thêm thì **chỉ lấy VOD streamer 18.6**. Chạy live trên client 18.7 chỉ dùng để đo độ trễ và độ đọc; lõi/đồ mới của 18.7 không có trong dữ liệu nên sẽ ra "chưa rõ" hoặc trung tính.

## Related

- [Dataset split](dataset-split.md) · [Recording protocol](recording-protocol.md)
- [Next steps](../next-steps.md)
