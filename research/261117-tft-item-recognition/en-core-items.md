# en-core-items

Core items per carry for Set 18 / 18.6: machine-readable sources (EN, 3 iterations, every endpoint curl-checked 2026-11-17).
The researcher agent returned this as a message; this file is the copy. Raw samples were kept in that session's scratchpad.

## Sources

| Source | Endpoint | Per-unit item fields | Carry vs tank | 18.6 fresh | Access |
|---|---|---|---|---|---|
| tactics.tools per unit | `https://d3.tft.tools/stats2/unit/1100/{unitApiName}/{patch}/1` | `base{count,place,top4,won}`; `items[]{items,count,place,top4,won,adjDelta}`; `itemPairs[]`; `itemTrios[]`; `itemCountData` | No | Yes, patch code **16220** (repo's `SET18_PATCH=16170` is stale) | Open, no Cloudflare, ToS not found |
| tactics.tools all units | `https://d3.tft.tools/stats2/general/1100/{patch}/1` | `units[name]{count,place,top4,won,topItems[≤5]}` | No | Yes | Same |
| tactics.tools patch code | `"patch":{"_0":16220}` in `__NEXT_DATA__` of tactics.tools/units | n/a | n/a | Patch codes step by 10 | n/a |
| MetaTFT per unit | `https://api-hc.metatft.com/tft-stat-api/unit_detail_items?unit=…&queue=1100&patch=current&days=3` | `items[]{itemName:"X-1", places[8]}`; `builds[]{buildNames, places[8], total}` | No | Yes | `ACAO: *`, no public docs |
| MetaTFT bulk | `https://api-hc.metatft.com/tft-comps-api/unit_items_processed` | top 10 item names per unit, no stats | No | Yes | Same |
| TFT Academy | `https://tftacademy.com/api/tierlist/comps?set=18` | `finalComp[]{apiName,items[],stars}`, **`mainChampion`** | **Partly**: `mainChampion` marks the carry | Updated 2026-11-16 | Open, editorial (no sample size) |
| op.gg | `op.gg/tft/meta-trends/champion/{unit}?version=18.6` | SSR HTML: top builds, games | No | Yes | HTML only |
| lolchess | `lolchess.gg/champions/set18/{key}` | `recommendItems[5]`, `role` (e.g. `ADFighter`, `APTank`) | Through `role` | Unknown | `/meta` behind AWS WAF |
| Mobalytics | n/a | n/a | n/a | n/a | 403 |

## Core-item definitions

| Definition | Source | Quantified |
|---|---|---|
| Carries need 1–2 core items; the last slot is flexible | tacter guide (search snippet only) | No |
| Main carry takes the first 2 offensive items; tank takes defensive items for the lobby; others get leftovers | metabot / mobalytics summaries | No |
| **Necessity**: how much avg placement worsens without the item; > 0.1 important, about 0.01 not core | [TFTable](https://tftable.cc/blog/introducing-tftable) | **Yes, 0.1** |

## Feasibility check (Tristana, tactics.tools 16220)

181,175 games, avg 4.70. Guinsoo in 44% of games, Gunblade 23%, IE 16%, Kraken 15%; all `adjDelta` between −0.11 and −0.19. Frequency and delta rank items differently, so "core" needs both (suggested: frequency ≥ ~35–40% **and** necessity ≥ 0.1; **not from any source**, needs calibration).

## Caveats

- No public API contract. Endpoints were reverse-engineered from site JS and can change.
- Names use the `DA_` prefix (`DA_18_Tristana`), same as the repo. Strip MetaTFT's `-N` suffix.
- `adjDelta` is undocumented.

## Related

- [en-recognition.md](en-recognition.md) · [zh-recognition.md](zh-recognition.md)
