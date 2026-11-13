# TFT Set 18: "map" mỗi ván = Opening Encounter

Research 2026-11-13, mode medium, EN + ZH + VI (3 agent). Chi tiết EN:
[261113-tft-set18-maps/en-map-modifiers.md](261113-tft-set18-maps/en-map-modifiers.md).

## Kết luận

- **Cơ chế người chơi gọi là "map" chính là Opening Encounter.**
  - Tên VN chính thức: **Vòng Kỳ Ngộ Khai Cuộc**. Tiếng Trung cộng đồng gọi là 奇遇.
  - Mỗi ván random **một** encounter gắn với một tướng, áp dụng cho **cả 8 người**.
  - Sàn đấu đổi skin theo encounter, nên người chơi thấy như "map".
- **Map +1 lượt đổi lõi là Teemo, "Scouting Party"** (VN suy ra: *Biệt Đội Trinh Sát*), tỉ lệ 4%.
  - Khớp với `minh_05`: ô 0 và ô 2 mỗi ô được đổi 2 lần, tức mặc định 1 lần/ô + 1.

## Encounter ảnh hưởng màn chọn lõi (~28% số ván)

| Tướng | Tên EN | Hiệu ứng | Tỉ lệ |
|---|---|---|---|
| Teemo | Scouting Party | +1 lượt đổi lõi cho mọi màn | 4% |
| Leona | Golden Gala (*Gala Hoàng Kim*) | Cả 3 màn là lõi vàng | 6% |
| Elder Dragon | Prismatic Party (*Tổ Đội Lăng Kính*) | Cả 3 màn là lõi kim cương | 2% |
| Amumu | Golden Prelude | Màn 1 vàng | 4% |
| Morgana | Prismatic Opener (*Mở Đầu Với Nâng Cấp Kim Cương*) | Màn 1 kim cương | 4% |
| Ivern | Golden Finale | Màn 3 vàng | 4% |
| Karma | Prismatic Finale (*Kết Thúc Tối Thượng*) | Màn 3 kim cương | 4% |

## Encounter cho trang bị

| Tướng | Tên | Hiệu ứng | Tỉ lệ |
|---|---|---|---|
| Sivir | Component Anvils (*Gói Trang Bị Thành Phần*) | 2 đe mảnh đồ | 6% |
| Yunara | Completed Item Anvil Start (*Khởi Đầu Với Gói Trang Bị Hoàn Chỉnh*) | 1 đe đồ hoàn chỉnh | 6% |
| Ornn | Item Forge (*Lò Rèn Trang Bị*) | 2 đe đồ hoàn chỉnh | 3% |
| Lux | Emblem Ensemble (*Bộ Sưu Tập Ấn*) | 3 ấn ngẫu nhiên | 2% |

## Encounter khác

| Tướng | Hiệu ứng | Tỉ lệ |
|---|---|---|
| Kayle (*Gói Đổi Lại*) | Đổi **shop** miễn phí đầu mỗi stage, không phải đổi lõi | 3% |
| Kobuko | Vàng mỗi stage | 4% |
| Ashe | Lên cấp rẻ hơn 2 XP | 4% |
| Draven | 2 người cuối nhận 70 vàng | 6% |
| LeBlanc | Tướng 2 sao | 6% |
| Azir | 5 tướng 1 vàng | 6% |
| Warwick | Tướng 2 vàng | 6% |
| Tristana | Tướng 3 vàng | 3% |
| — | Không có encounter | 3% |

## Độ tin cậy

| Mức | Nội dung |
|---|---|
| Đã xác minh | Hiệu ứng và tỉ lệ lấy từ [gamewave.fr](https://gamewave.fr/tft/tft-les-rencontres-d-ouverture-du-set-18-la-liste-detaillee/), nguồn đầy đủ duy nhất. Agent EN và ZH đến được trang này độc lập với nhau |
| Đã xác minh | Ba encounter mới của 18.1 lấy từ [patch 18.1 chính thức](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1). Patch 18.2–18.6 không đổi encounter |
| Suy ra | Phần lớn tên tiếng Việt, ghép từ patch notes 17.2 VI. Tên VN của Golden Prelude và Golden Finale không tìm được |
| Lỗ hổng | Tổng tỉ lệ chỉ **86%**. Thiếu ~14%, có thể còn Double Duplicators (4% ở Set 17) |
| Sai, đã kiểm lại | Agent EN báo "CDragon không có Set 18". Sai: cache dự án có `TFTSet18`. Nhưng file locale chỉ có encounter Set 11 (`TFT11_Encounter_*`) và `TFT17_MarketOffering_ExtraAugmentRolls`, **không có định nghĩa encounter Set 18** |

## Hệ quả cho đồ án

1. **Mô phỏng reroll** đang giả định 1 lượt đổi mỗi ô. Ván Teemo có 2 lượt mỗi ô, nên đó là trường hợp ngoài giả định.
2. **Chấm điểm lõi:** encounter ép bậc (vàng/kim cương) đổi pool lõi được chào. Encounter cho đồ làm đổi trạng thái `item_components`.
3. **Nhãn video** nên có trường `encounter` (gán tay khi xem đầu video) để:
   - lọc hoặc phân tầng khi đánh giá;
   - giải thích các màn có nhiều offer.
4. Set 17 có **cấm lõi theo encounter** (vd Emblem Ensemble cấm Trait Tree). Chưa rõ Set 18 còn cấm không.

## Câu hỏi mở

1. Encounter hiện thế nào trên client Unreal (banner, icon cạnh stage), và chữ tiếng Việt đúng là gì? Cần xem đầu một video.
2. Danh sách đủ 100%, và Double Duplicators còn trong Set 18 không.
3. Set 18 còn cấm lõi theo encounter không.

## Related

- [Augment reroll](../docs/augment-reroll/overview.md) · [Labeling guide](../docs/playtest-fixes/labeling-guide.md)
