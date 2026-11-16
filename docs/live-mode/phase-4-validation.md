# Phase 4 — Live Validation

The only phase that needs real matches. Timeboxed: one Normal game, run-and-exit, per the
[testing protocol](../../research/vanguard/testing-protocol.md).

## Before the match

- [ ] `git pull`; old agent-made `run_live.py` removed
- [ ] `pip install -r requirements.txt`, rồi `pip install windows-capture` (đang comment trong requirements)
- [ ] Game in **Borderless**; note resolution and Windows display scale
- [ ] `python tools/probe_environment.py` — all checks pass
- [ ] `python scripts/refresh_data.py --check` — no stale tables (or knowingly accepted)
- [ ] Replay smoke: `run_live.py --video <file> --start <s>` shows a ranking on screen

## During the match

| Check | Pass |
|---|---|
| Overlay visible over the game, top-right, not covering cards/HUD | Yes at 2-1, 3-2, 4-2 |
| Mouse passes through the overlay (click-through, không có hotkey) | Yes |
| Ranking appears within budget after screen opens | Đọc thẻ `hybrid` (OCR trước, không còn Gemini trước): ~1,6 s khi mô phỏng (1 màn); số game thật chưa có |
| Rerolling one card updates the ranking | New ranking after the card changes |
| Leaving the augment screen clears the panel | Within ~1 s |
| Game FPS impact | Note before/after, no stutter |

## Recorded output

`data/live_logs/*.jsonl` — dòng đầu là `Session` (nguồn game / mô phỏng, card reader, fps), sau đó
mỗi sự kiện kèm latency từng khâu. Tổng hợp p50/p95: `tools/live_latency_report.py --game-only`
(bỏ phiên mô phỏng video) để số §12.1 không lẫn với nguồn video.

## After the match

- [ ] Latency p50/p95 into `docs/next-steps.md` §7.2 (replaces idle-machine numbers)
- [ ] Wrong reads → label those frames, add to eval set (next-steps §7.1 held-out set)
- [ ] ROI misses (hp §7.3, stage §7.4) → fix `config/screen_regions.yaml`, re-run replay tests
- [ ] Note any WGC border / consent behaviour in `research/open-questions.md` (closes line 78)

## Done when

Three augment rounds in one game produce a visible, correct-slot ranking, and
`tools/live_latency_report.py --game-only` reports the session with p95 inside budget.

## Related

- [Overview](overview.md)
- [Risks](risks.md)
