# TFT Set 18 per-game modifiers (EN worker)

Scope: the per-game modifier that changes augment screens or grants items. Set 18 = "Enchanted Wilds", live since 2026-08-26, patch 18.1 ([gamewave](https://gamewave.fr/tft/tft-les-rencontres-d-ouverture-du-set-18-la-liste-detaillee/)).

## Official name

- EN: **Opening Encounters**. Patch 18.1 has an "OPENING ENCOUNTERS" section ([18.1 notes](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1)). VERIFIED
- VI (official vi-vn patch notes): **"Vòng Kỳ Ngộ Khai Cuộc"**, with the short form "Vòng Kỳ Ngộ" ([vi 18.1](https://teamfighttactics.leagueoflegends.com/vi-vn/news/game-updates/teamfight-tactics-patch-18-1), [vi 17.2](https://teamfighttactics.leagueoflegends.com/vi-vn/news/game-updates/teamfight-tactics-patch-17-2)). VERIFIED in the notes. Not checked against the client's own strings.
- The system carried over from Set 17 (Space Gods) and came back in 17.2. Each encounter is a champion that gives the same buff to all 8 players ([gamewave](https://gamewave.fr/tft/tft-les-rencontres-d-ouverture-du-set-18-la-liste-detaillee/)). VERIFIED
- Set 18 also has mid-game Encounters, such as Carousel variants ([18.1 notes](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1)). They are out of scope here.

## Set 18 Opening Encounter list

Base source: the gamewave FR list, which gives the champion, the effect and an odds %. I attached the EN names from search snippets that quote mobalytics. A name marked "inferred" comes from the Set 17 tft.tools name with the same effect and the same odds.

| Champion | EN name | Effect | Augment impact | Item impact | Odds | Status |
|---|---|---|---|---|---|---|
| Teemo | Scouting Party | "+1 Augment rerolls this game" (S17 text). Snippet: "reroll all your Augments an extra time this game" | **+1 reroll on every augment screen** | – | 4% | Effect + odds VERIFIED (gamewave: "une relance d'optimisation en plus"). Name inferred (S17 name, snippet) |
| Leona | Golden Gala | All augments offered this game are gold tier | All 3 screens forced to Gold | – | 6% | Effect VERIFIED. Name from snippet |
| Elder Dragon ("Dragon ancestral") | Prismatic Party | All augments are prismatic | All 3 screens forced to Prismatic | – | 2% | Effect VERIFIED. Name from snippet |
| Amumu | Golden Prelude | First augment is gold | Screen 1 forced to Gold | – | 4% | Effect VERIFIED. Name from snippet |
| Morgana | Prismatic Opener | First augment is prismatic | Screen 1 forced to Prismatic | – | 4% | Effect VERIFIED. Name from snippet (17.2 also lists "Prismatic Opener") |
| Ivern | Golden Finale | Last augment is gold | Screen 3 forced to Gold | – | 4% | Effect VERIFIED. Name from snippet |
| Karma | Prismatic Finale / "Finisher" | Last augment is prismatic | Screen 3 forced to Prismatic | – | 4% | Effect VERIFIED. Sources disagree on the name |
| Sivir | Component Anvils | Start with 2 component anvils | – | +2 component anvils at start | 6% | VERIFIED |
| Yunara | Completed Item Anvil Start | Start with 1 completed-item anvil | – | +1 completed anvil | 6% | VERIFIED (18.1 notes + gamewave) |
| Ornn | Item Forge | Start with 2 completed-item anvils | – | +2 completed anvils | 3% | VERIFIED (18.1 notes + gamewave) |
| Lux | Emblem Ensemble (inferred) | 3 random emblems | Some augments banned (S17 list) | +3 emblems | 2% | Effect VERIFIED. Name inferred |
| Kayle | Reroll Subscription | Gain shop rerolls at the start of each stage | No (shop rerolls) | – | 3% | VERIFIED |
| Kobuko | Gold Subscription (inferred) | Gold each stage | – | – | 4% | Effect VERIFIED |
| Ashe | Cheaper Levels (inferred) | Each level costs 2 less XP | – | – | 4% | Effect VERIFIED |
| Draven | Final Showdown (named in 18.1 bugfix; S17 called it "Silver Scrapes") | The last 2 players alive get 70 gold | – | – | 6% | VERIFIED |
| LeBlanc | Upgraded Champion/Start (inferred) | Start with a 2-star champion | – | – | 6% | Effect VERIFIED |
| Azir | Howling Abyss (inferred) | 5 random 1-cost champions | – | – | 6% | Effect VERIFIED |
| Warwick | 2-Cost Start (inferred) | Random 2-cost champion | – | – | 6% | Effect VERIFIED |
| Tristana | 3-Cost Start (inferred) | Random 3-cost champion | – | – | 3% | Effect VERIFIED |
| – | No Encounter | Nothing | – | – | 3% | VERIFIED |

**The odds add up to 86%, not 100%.** Either gamewave's list is incomplete or its odds are wrong. Treat the odds as approximate. Double Duplicators (S17, 4%) is missing from the list and might still be live. UNRESOLVED

## Removed and historical (for edge cases)

- Removed in 18.1: Loot Subscription, Artifact Anvil, Reroll Start ([18.1](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1)). VERIFIED
- "Stage Three Augments" moved augments to 3-1/3-2/3-3. It came in 17.2 and was removed in 17.5 ("LeBlanc's Stage 3 Augments Removed", [17.5](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-17-5)). No encounter in Set 18 changes augment round timing (inferred: none appears in the list).
- "Augment Round Swap" was removed in 17.2 ([17.2](https://teamfighttactics.leagueoflegends.com/en-au/news/game-updates/teamfight-tactics-patch-17-2)).
- The official 18.2–18.6 notes have no Opening Encounter changes. I grepped 18.3–18.6. VERIFIED (text grep)
- 17.3 notes: **each encounter bans augments that synergise with it from the offer pool**. Examples: Emblem Ensemble bans Trait Tree, Flexible and others. Reroll Opener banned Prismatic Ticket and others ([17.3](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-17-3)). Whether Set 18 still has per-encounter ban lists is UNRESOLVED.

## Augment-impact summary for the advisor model

| Encounter | Rerolls per screen | Screen 1 tier | Screen 2 tier | Screen 3 tier |
|---|---|---|---|---|
| Scouting Party (Teemo) | +1 (the in-game text says "+1"; the per-screen reading is inferred from the S16 snippet and the user's observation) | normal | normal | normal |
| Golden Gala (Leona) | normal | Gold | Gold | Gold |
| Prismatic Party (Elder Dragon) | normal | Prism | Prism | Prism |
| Golden Prelude (Amumu) | normal | Gold | normal | normal |
| Prismatic Opener (Morgana) | normal | Prism | normal | normal |
| Golden Finale (Ivern) | normal | normal | normal | Gold |
| Prismatic Finale (Karma) | normal | normal | normal | Prism |

The normal tier pattern odds come from 17.2 and are bonus context: P/G/G 2%, P/S/G 4%, P/G/P 1%, P/S/P 1%, G/G/G 22%, G/S/G 18% ([vi 17.2](https://teamfighttactics.leagueoflegends.com/vi-vn/news/game-updates/teamfight-tactics-patch-17-2)). These may have changed in Set 18. Item grants (Sivir/Yunara/Ornn) change the item state, not the augment screens.

## How to identify the active encounter

- At game start, the champion appears and gives its buff ([gamewave](https://gamewave.fr/tft/tft-les-rencontres-d-ouverture-du-set-18-la-liste-detaillee/)). VERIFIED in general terms only.
- An encounter icon sits next to the stage number in the top-left HUD. Hovering or clicking it shows the active encounter. This comes only from search snippets about Sets 11–13 and is NOT verified for the Set 18 Unreal client.
- Vietnamese names from the vi-vn notes. The name mapping is VERIFIED for the 18.1 additions. The 17.2 VI list is positionally aligned to the EN list, so those pairings are inferred:
  - Gói Đổi Lại = Reroll Subscription
  - Lò Rèn Trang Bị = Item Forge
  - Khởi Đầu Với Gói Trang Bị Hoàn Chỉnh = Completed Item Anvil Start
  - Gala Hoàng Kim = Golden Gala
  - Tổ Đội Lăng Kính = Prismatic Party
  - Mở Đầu Với Nâng Cấp Kim Cương = Prismatic Opener
  - Kết Thúc Tối Thượng = Prismatic Finale
  - Biệt Đội Trinh Sát = Scouting Party
  - Gói Trang Bị Thành Phần = Component Anvils
  - Bộ Sưu Tập Ấn = Emblem Ensemble
  - Không Có Vòng Kỳ Ngộ = No Encounter
  - The VI names for Golden Prelude and Golden Finale were not found.

## CommunityDragon

- `https://raw.communitydragon.org/latest/cdragon/tft/en_us.json` (keys `items`, `setData`, `sets`): latest content-metadata = 16.22 (LoL). It contains **no TFT18 apiNames**. Its newest entries are TFT17, for example `TFT17_MarketOffering_ExtraAugmentRolls` ("You get +@ExtraRolls@ Augment rerolls for all future augment choices"). `sets["18"]` is mislabelled "Set10" PvE data. The PBE endpoint returned 522. Conclusion: CDragon has no Set 18 (Unreal) encounter definitions, so I found no data-file URL. VERIFIED
- tft.tools `/info/set-18/encounters` returned HTTP 500. `/info/set-17/encounters` works and has names and odds.

## Unresolved

1. Exact Set 18 odds (the gamewave list sums to 86%). Is Double Duplicators still live?
2. Exact EN in-client names for Karma (Finale vs Finisher), Lux, Kobuko, Azir, LeBlanc, Draven.
3. Does Scouting Party add +1 to each slot's reroll or +1 per screen? Read the in-game tooltip.
4. Are Set 18 per-encounter augment ban lists published?
5. How the Set 18 Unreal HUD shows the encounter, and the VI client strings. Best checked from the user's own gameplay videos.

## Sources
- https://gamewave.fr/tft/tft-les-rencontres-d-ouverture-du-set-18-la-liste-detaillee/
- https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1
- https://teamfighttactics.leagueoflegends.com/vi-vn/news/game-updates/teamfight-tactics-patch-18-1
- https://teamfighttactics.leagueoflegends.com/en-au/news/game-updates/teamfight-tactics-patch-17-2
- https://teamfighttactics.leagueoflegends.com/vi-vn/news/game-updates/teamfight-tactics-patch-17-2
- https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-17-3
- https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-17-5
- https://tft.tools/info/set-17/encounters
- https://mobalytics.gg/tft/encounters (403; names seen in search snippets only)
- https://raw.communitydragon.org/latest/cdragon/tft/en_us.json
