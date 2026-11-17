# zh-recognition

TFT item recognition from screen pixels: Chinese-language prior art (3 iterations, 2026-11-17).
Raw findings for the lead-researcher synthesis. The researcher agent returned them as a message; this file is the copy.

## Prior art

| Source | Target | Method | Geometry | Numbers | Caveats |
|---|---|---|---|---|---|
| [WJZ-P/TFT-Hextech-Helper](https://github.com/WJZ-P/TFT-Hextech-Helper) (748 stars, 2026-11) | (a) item bench | Crop the slot, resize to **24x24 `INTER_AREA`**, `TM_CCOEFF_NORMED` against 24x24 RGB templates. **Threshold 0.60**. Empty slot = gray stddev < 10, checked before matching (`TemplateMatcher.ts`) | Fixed 1024x768. Bench is 10 slots down the left edge, slot about 24x25 px, pitch about 36 px (`TFTProtocol.ts:161-186`). At 1080p that is about 34 px (our estimate) | none; author's anecdote only ([V2EX](https://www.v2ex.com/t/1186873)) | Returns the **first** template above threshold, in category order, not argmax |
| same | (b) items on units | **Does not read icons on the board.** It right-clicks each unit and reads 3 slots in the info panel (about 39 px), then right-clicks to close | n/a | none | Needs mouse input, so we can't use it |
| [CSDN "TFT 阵容顾问"](https://aicoding.csdn.net/6a69cf74662f9a54cb95e4cb.html) | champions; items via "局部规则" (local rules) | Old: hexagon border, HSV histogram shortlist, then zero-mean NCC; transparent areas filled with neutral gray. New: YOLO champions + CLIP | n/a | none | Author: still needs collected screenshots and training |
| zhouxingkong/LOL-yunding, jj199703/xiaokejinchanchan, yywwann/TacticsScript | shop and UI flags | `matchTemplate`, PaddleOCR | n/a | none | No item identification |
| [Jack0Chan/TFT_Spider](https://github.com/Jack0Chan/TFT_Spider) | icon scraping | n/a | n/a | n/a | Icon source only |

## Icon sources

- Tencent CDN: `https://game.gtimg.cn/images/lol/act/img/tft/equip/{equipId}.png`.
- Hextech templates are mostly 64x64 / 128x128 art downscaled to 24x24, plus a few real 24x25 screen crops. This suggests clean art alone doesn't match in-game crops perfectly.

## Takeaways

- Bench: 24x24 NCC plus a stddev empty-check is a proven cheap baseline. Use **argmax** over all templates, not the first hit.
- No Chinese source reads the icons above a unit's health bar, and none reports accuracy.

## Related

- [en-recognition.md](en-recognition.md)
