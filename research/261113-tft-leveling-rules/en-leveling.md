# TFT leveling / econ / HP rules per plan (EN sources)

Researcher: EN worker, 5 iterations. Date: 2026-11-13. Scope: level/gold/HP/streak rules only.

## Executive summary

- Best current source: **BunnyMuffins "TFT Leveling & Econ Guide Set 18"** (published 2026-09-04, modified 2026-09-10). Gives per-streak tables for standard/fast 8-9 and for 1/2/3-cost reroll. Verified via raw HTML.
- Mobalytics (Aug/Dec 2025, Set 15 era, verified via Wayback) gives the older "slower" standard curve: 7 at 4-1, **8 at 5-1**. BunnyMuffins Set 18 says **8 at 4-2** (win streak) / **4-1** (lose streak). Main conflict; Set 18 patch 18.2 (2026-09-09) cut 7->8 XP 60->56 and 8->9 68->64, which supports the earlier-8 curve.
- HP rules are old (Set 4, 2020) but stated as timeless: "bank as much gold as you have HP"; >70 HP roll to ~30g; <50 HP roll to ~10g; <20 HP abandon slow roll. Newer (metabot, Set 18, low-authority): >50 HP greedy, <30 HP roll.
- Reroll signature from HUD: under-leveled vs standard curve while holding ~50g. 1-cost = level 4 through 3-1 (no XP bought). 2-cost = level 6 from 3-2, stays 6 in stage 4. 3-cost = level 7 at 3-5/4-1, stays 7 past 4-2.

## Rule table

Legend: V = page fetched and text verified; S = search snippet / LLM-summarized fetch only.

| Plan | Stage | Level target | Gold rule | HP rule | Streak rule | Exact quote | Source | V/S |
|---|---|---|---|---|---|---|---|---|
| Standard / Fast 8-9, win streak (8+) | 2-1, 2-5, 3-1, 3-5, 4-2, 5-2 | 4, 5, 6, 7, 8, 9 | 3-5 level 7 only with 30g+ | "not allowed to take 20 damage a fight stage 4" | win streak 8+ | Table "Round 2-1 / 2-5 / 3-1 / 3-5 (30g+) / 4-2 / 5-2 -> Level 4/5/6/7/8/9"; "On 4-2 we are likely going to roll a little to stabilize... We aren't allowed to take 20 damage a fight stage 4, so you for sure roll a bit on level 8... go 9 on 5-2. Sometimes we have to roll deeper and delay our 9 till 5-5." | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| Fast 9, win streak + econ augment | 4-5 | 9 | econ augment needed | - | win streak | "If you are streaking with an econ augment, you can even consider 4-5 level 9." | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| Standard / Fast 8, lose streak (6+) | 2-3, 2-7, 3-2, 3-5, 4-1, 5-2 | 4, 5, 6, 7, 8, 9 | 2-3 needs 10g+; 3-5 level 7 needs 40g+ | ~50-60 HP deficit; lose a life every lost stage-4 fight | lose streak 6+ | Table "2-3 (10g+) / 2-7 / 3-2 / 3-5 (40g+) / 4-1 / 5-2 -> 4/5/6/7/8/9"; "we have to win out most of Stage 4, this means rolling a turn before tempo (4-1 on level 8)... off a loss streak, you are low health, playing at around a ~50-60 health deficit" | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| Fast 9, lose streak + econ augment | 4-5 | 9 | "broken econ augment" | - | lose streak | "If you have a broken econ augment, you should structure your curve around leveling to 9 on 4-5" | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| Standard, mixed streak | 2-1/2-3, 2-5/3-1, 3-2, 3-5/4-1, 4-2/4-5, 5-2/5-5 | 4, 5, 6, 7, 8, 9 | - | "HP preservation is extremely important" | mixed | "You somewhat live or die by your 4-2 rolldown and hitting reasonable upgrades to save lives on Stage 4." | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| Standard (older curve) | 2-1 opt, 2-5 opt, 2-7 latest 5, 3-1 min 5, 3-2, 4-1, 5-1, 6-1 | 4, 5, 5, 5, 6, 7, 8, 9 | 2-7 at ~25g can level and keep 20 interest | 3-1: stay 4 only "if you still feel healthy HP wise" | win streak -> level; lose -> still hit 6 at 3-2 | "2-1: Optional Level 4 to win streak / 2-5: Optional Level 5 to win streak / 2-7: Krugs, latest Level 5 / 3-2: Level 6 / 4-1: Level 7 / 5-1: Level 8 / 6-1: Potential Level 9" | [Mobalytics std, 2025-08-07](https://mobalytics.gg/blog/tft/guide-standard-leveling-strategy/) ([archive](http://web.archive.org/web/20251114001732/https://mobalytics.gg/blog/tft/guide-standard-leveling-strategy/)) | V |
| Aggressive leveling (fast 8) | 3-1, 3-5, 4-2..4-5 | 6, 7, 8 | - | - | win streak + upgrades | "Level 6 at 3-1 / Level 7 at 3-5 / Level 8 at 4-2 to 4-5" | [Mobalytics std](https://mobalytics.gg/blog/tft/guide-standard-leveling-strategy/) | V |
| Greedy leveling | 3-5, 4-2 | 6, 7 | build gold | "risky for your HP" | lose streak | "Level 6 at 3-5 / Level 7 at 4-2"; "greedy leveling is risky for your HP" | [Mobalytics std](https://mobalytics.gg/blog/tft/guide-standard-leveling-strategy/) | V |
| 1-cost reroll | stage 2 - 3-1 | stay 4 (no XP bought) | 3-1 roll to >=32g ("32g > 40g > 50g"); then slowroll | - | - | "Do not press the level button at all until you 3 star your 1 cost."; "I like rolling to at least 32 gold because 32g > 40g > 50g" | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| 1-cost reroll | 3-1, 3-2, 3-5, early 4 | 4 -> natural 5 at 3-2 -> 6 at 3-5 (solo carry) -> 7 early 4 | 3-1 hyper roll to ~20g | stage 2: "You don't want to fall to 60 HP to lose streak" | lose streak stage 2 | "At 3-1, most players will opt to Hyper Roll down to 20 or so gold... At 3-2, you will naturally hit level 5... No need to hit level 6 at this point"; "level up to 6 at 3-5 (after carousel) and hopefully hit level 7 in early Stage 4" | [Mobalytics reroll, 2025-12-17](https://mobalytics.gg/blog/tft/leveling-guide-how-to-play-reroll-comps/) ([archive](http://web.archive.org/web/20260314171945/https://mobalytics.gg/blog/tft/leveling-guide-how-to-play-reroll-comps/)) | V |
| 1-cost reroll | spikes | - | - | - | - | "1 cost rerolls tend to spike at 3-1, 3-5, and 4-1." | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| 1+2 hybrid reroll | 2-1/2-3, 2-7, 3-2, 4+, 5+, 6+ | 4, 4/5, 5, 6/7, 8, 9 | 2-5 level 5 "often too expensive" | - | 2-1 level 4 only if can win 3/5 stage-2 fights | "Our level of choice will be level 5"; "level to 6 and look for 2 costs, this will probably happen early stage 4" | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| 2-cost reroll, lose streak | 2-3, 2-7, 3-2, 4+, 5+, 6+ | 4, 5, 6, 7, 8, 9 | - | - | lose streak | Table "2-3 / 2-7 / 3-2 / 4+ / 5+ / 6+ -> 4/5/6/7/8/9" | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| 2-cost reroll, other | 2-1, 2-5, 3-2, 4-5, 5-2 | 4, 5, 6, 7, 8 | if weak at 2-5, "make econ (20)" | - | strong -> level | "Level to 6 on 3-2 and roll to stabilize. You just slowroll from here. / Level 7 by 4-5 if possible / Level 8 5-2 if possible" | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| 2-cost reroll (Moba) | 3-2 (greedy: 3-5), stage 4, 5-1 | 6 through stage 4; 7 by 5-1 | slow roll "staying above 50" | greedy 3-5 only "if you are ahead on life" | - | "Other players will level up to 7 at 4-1, but you'll spend this time losing fights to find your 3-star carry."; "5-1 is the point where you should at least have your 3-star carry and be Level 7. You should roll down aggressively at this point or you might lose too much HP." | [Mobalytics reroll](https://mobalytics.gg/blog/tft/leveling-guide-how-to-play-reroll-comps/) | V |
| 2-cost reroll | spikes | - | - | - | - | "2 cost rerolls tend to spike at 3-2, 4-1, and 4-5." | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| 3-cost reroll, lose streak | 2-3, 2-7, 3-2, 3-5, 5+, 6+ | 4, 5, 6, 7, 8, 9 | 3-5 level 7 needs 40g+ | - | lose streak | Table "2-3 / 2-7 / 3-2 / 3-5 (40g+) / 5+ / 6+ -> 4/5/6/7/8/9" | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| 3-cost reroll, other | 2-1, 2-5, 3-2, 3-5 or 4-1, 5+ | 4, 5, 6, 7, 8 | 3-5 only with econ augment | - | - | "Level to 7 3-5 If you have an econ Augment / Level to 7 4-1 and hit your carry 2-star to stabilize." | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| 3-cost reroll (Moba) | 3-2, 4-1/4-2 | 6 (roll at 3-2 to 2-star carry), 7 | 4-2 level "if you want some extra gold" | - | win streak -> level 4-1 | "you're also able to roll aggressively at 3-2 in order to 2-star your 3-cost carry"; "At Stage 4-1, you'll want to hit level 7... If you want some extra gold, you can wait until 4-2... If you have a win streak, though, you'll want to level at 4-1" | [Mobalytics reroll](https://mobalytics.gg/blog/tft/leveling-guide-how-to-play-reroll-comps/) | V |
| 3-cost reroll | spikes | - | - | - | - | "3 cost rerolls tend to spike 3-2, 3-5, 4-1, and 5-1." | [BM S18](https://bunnymuffins.lol/tft-leveling-guide/) | V |
| Slow roll (any reroll) | - | - | hold 50, spend interest | - | - | "Slow Roll: The process of rolling gold little by little while staying above 50 to maximize interest."; "Hyper Roll: ... (usually down to 20ish)" | [Mobalytics reroll](https://mobalytics.gg/blog/tft/leveling-guide-how-to-play-reroll-comps/) | V |
| Slow roll (Set 4, timeless HP rule) | stage 3+ | 5 at start of stage 3, no XP after | 50g, spend excess | >70 HP: roll to ~30g; <50 HP: roll to ~10g; <20 HP: abandon slow roll | - | "If you've kept your health relatively high (over 70 HP), you can be a bit greedier and only roll down to 30g or so."; "very low (sub 50 HP)... aggressively roll (like only leaving yourself 10g)"; "if you ever get to sub-20 HP... you have to abandon the slow roll" | [BlogOfLegends 2020](https://blogoflegends.com/2020/10/07/tft-guide-slow-roll-set-4/3) | S (LLM-summarized fetch) |
| Standard (Set 4, timeless HP rule) | stage 4-5 | 7 by 4-1, 8 at 5-1 | "bank as much gold as you have HP" | >50 HP econ; ~30 HP roll to 30g | - | "bank as much gold as you have HP... while you have over 50 HP, it's fine to build that econ up, but if you're down to 30 HP, you should probably spend and roll down to 30g." | [BlogOfLegends 2020](https://blogoflegends.com/2020/11/03/tft-guide-standard-leveling-econ-set-4/3) | S (LLM-summarized fetch) |
| Any (Set 18 generic) | - | 7 for 3-costs, 8 for 4-costs, 9 for 5-costs | ~50g before rolling | >50 HP greedy; <30 HP roll | - | "Above 50 HP: maintain greedy leveling"; "Below 30 HP: actively seek rolling" (paraphrase by fetch model) | [metabot.gg, upd. 2026-10-15](https://metabot.gg/en/TFT/guides/tft-when-to-roll-vs-level-up-shop-odds) | S (low authority, likely AI content) |
| Hyper roll (Set 18 generic) | stages 2-3 | 4-5 | roll to 0 | "above 60 health with a real board, that bet is fine. At 20 health it is a coin flip" | - | as left | [metabot.gg slow vs hyper](https://metabot.gg/en/TFT/guides/tft-slow-roll-vs-hyper-roll) | S |
| Stage-4 roll-down by HP (Set 16) | 4-1/4-2 | 8 | healthy (40+ HP): roll to ~40-50g; low HP: ~20-30g | 40 HP split | - | (snippet only, page 403) | [dtgre patch 16.3, 2026-01](https://www.dtgre.com/2026/01/tft-patch-16-3-meta-shift-fast-9-dead.html?m=1) | S (snippet only) |
| Older fast curve (2020) | 2-6, 3-2, 3-4, 4-3 | 5, 6, 7, 8 | slow roll: "hit 50 gold and then roll back down to 50" | - | - | "Level to 7 during round 3-4 / Level to 8 during round 4-3"; slow roll "Level to 6 normally around 4-3" | [Dignitas 2020-11-25](https://dignitas.gg/articles/a-complete-guide-to-leveling-in-tft) | S |
| Fast 8 / reroll (generic 2025) | 2-1, 2-5, 3-1, 3-5, 4-2 | 4,5,6,7,8 | 1-cost: roll at 4 on 3-1 with 50-60g; 3-cost: stabilize 7 at 3-5 with 40+g | - | lose streak: 4 at 2-3, 5 at 2-7, 8 at 4-1, 9 at 5-5 | (fetch summary) | [gamer.org 2025-08-22](https://www.gamer.org/tft-leveling-guide-fast-8-fast-9-rerolls-and-gold-management/) | S (looks derived from BM) |

## Patch context (Set 18)

- Patch 18.2 (2026-09-09): "Level 7 to Level 8: 60 ⇒ 56 / Level 8 to Level 9: 68 ⇒ 64 / Level 9 to Level 10: 68 ⇒ 64" — [Riot patch 18.2](https://teamfighttactics.leagueoflegends.com/en-sg/news/game-updates/teamfight-tactics-patch-18-2) (S, LLM-summarized fetch). Implication: earlier 8/9 than pre-18.2 guides. BunnyMuffins page was last modified 2026-09-10, i.e. one day after 18.2.

## "Which plan am I on" heuristics (HUD-derivable)

| Signal at checkpoint | Plan implied | Basis |
|---|---|---|
| 3-2: level 4 (no XP bought, or level 5 only via natural XP) and gold dropped from ~50 to ~20-32 at 3-1 | 1-cost reroll | BM "do not press the level button"; Moba "Hyper Roll down to 20 or so"/"naturally hit level 5" |
| 3-2: level 5, gold ~50 held, not leveling | 1+2 hybrid reroll (or greedy) | BM hybrid "level of choice will be level 5" |
| 3-6 / 4-2: level 6, gold hovering ~50, still 6 at 4-2 while standard is 7-8 | 2-cost reroll slow roll | Moba "Other players will level up to 7 at 4-1, but you'll spend this time losing fights"; BM "Level 7 by 4-5" |
| 3-6: level 7 at 3-5 with gold 40+ (lose streak) or econ augment; 4-2: still level 7 | 3-cost reroll | BM 3-cost table: 8 only at 5+ |
| 3-6: level 7 (win streak, 30g+) ; 4-2: level 8 | Standard / fast 8 (win streak) | BM win-streak table |
| 3-6: level 6-7 with 40g+ after lose streak; 4-1/4-2: level 8 and gold spent | Fast 8 off lose streak | BM lose-streak table |
| 4-2: level 8 with gold kept high (≥40-50 after leveling) | Fast 9 (9 at 4-5 w/ econ aug, else 5-2/5-5) | BM win/lose tables; snippet "Only do so if you have 40 or 50 gold leftover" (S, unverified source) |
| 3-6: level 6, 4-2: level 7, 8 at 5-1 | Standard (older/slower curve) | Mobalytics std |
| Low HP overrides plan | sub-20 HP: stop slow roll; <30 HP: roll; >50-70 HP: stay greedy | BlogOfLegends (2020), metabot (2026) |

Key discriminator: **level vs checkpoint relative to standard curve (6 @3-2, 7 @3-5/4-1, 8 @4-2) combined with gold held**. Under-leveled + ~50 gold held = reroll slow roll; on-curve/ahead + gold held = fast 8/9; on-curve + gold spent = standard roll-down.

## Conflicts

| Topic | Source A | Source B | Note |
|---|---|---|---|
| Level 8 timing (standard) | BM S18: 4-2 (win), 4-1 (lose), 4-2/4-5 (mixed) | Mobalytics 2025: 5-1; metabot: 5-1 | Patch 18.2 XP cut favours BM for Set 18 |
| Level 6 timing (win streak) | BM: 3-1 | Mobalytics std: 3-2 (aggressive = 3-1) | BM win-streak = Mobalytics "aggressive" |
| 1-cost 3-1 roll floor | BM: >=32g | Mobalytics: ~20g; gamer.org: start with 50-60g | BM gives the reason (32g keeps 3 interest) |
| 3-cost reroll level 7 | BM: 3-5 (lose streak 40g+ / econ aug) or 4-1 | Mobalytics: 4-1 (4-2 if greedy) | consistent at 4-1 |
| 2-cost reroll level 7 | BM: by 4-5 | Mobalytics: by 5-1 | minor |
| Stage-4 roll floor by HP | BlogOfLegends: gold ≈ HP; >70 HP -> 30g | dtgre (S16): 40+ HP -> 40-50g; low -> 20-30g | both monotone: more HP -> higher floor |
| Streak gold | metabot: 2-3 = +1, 4 = +2, 5+ = +3 | other snippet: 3-4 = +1, 5 = +2, 6+ = +3 | out of scope; verify in client if used |

## Sources

- BunnyMuffins, TFT Leveling & Econ Guide Set 18 (pub 2026-09-04, mod 2026-09-10): https://bunnymuffins.lol/tft-leveling-guide/ (verified via raw HTML)
- Mobalytics, Standard Leveling Strategy (2025-08-07): https://mobalytics.gg/blog/tft/guide-standard-leveling-strategy/ — archive http://web.archive.org/web/20251114001732/https://mobalytics.gg/blog/tft/guide-standard-leveling-strategy/
- Mobalytics, How to Play Reroll Comps (2025-12-17): https://mobalytics.gg/blog/tft/leveling-guide-how-to-play-reroll-comps/ — archive http://web.archive.org/web/20260314171945/https://mobalytics.gg/blog/tft/leveling-guide-how-to-play-reroll-comps/
- Riot, TFT patch 18.2 notes (2026-09-09): https://teamfighttactics.leagueoflegends.com/en-sg/news/game-updates/teamfight-tactics-patch-18-2
- BlogOfLegends, Slow Roll Set 4 (2020): https://blogoflegends.com/2020/10/07/tft-guide-slow-roll-set-4/3
- BlogOfLegends, Standard Leveling and Econ Set 4 (2020): https://blogoflegends.com/2020/11/03/tft-guide-standard-leveling-econ-set-4/3
- metabot.gg, Roll vs Level (Set 18, upd 2026-10-15): https://metabot.gg/en/TFT/guides/tft-when-to-roll-vs-level-up-shop-odds
- metabot.gg, Slow Roll vs Hyper Roll: https://metabot.gg/en/TFT/guides/tft-slow-roll-vs-hyper-roll
- metabot.gg, Economy explained: https://metabot.gg/en/TFT/guides/tft-economy-gold-interest-streaks-explained
- dtgre, Patch 16.3 Fast 9 dead (snippet only): https://www.dtgre.com/2026/01/tft-patch-16-3-meta-shift-fast-9-dead.html?m=1
- Dignitas leveling guide (2020): https://dignitas.gg/articles/a-complete-guide-to-leveling-in-tft
- gamer.org leveling guide (2025-08-22): https://www.gamer.org/tft-leveling-guide-fast-8-fast-9-rerolls-and-gold-management/

## Unresolved

- Mobalytics current (2026) pages incl. "set-18-how-to-play-fast-9" blocked (403, no Wayback copy). Not read.
- tftacademy, tactics.tools, metatft leveling guides not found / not fetched.
- No pro-sourced numeric HP threshold for Set 17/18 found from a high-authority site; HP rules rely on 2020 BlogOfLegends + low-authority metabot.
- Reddit r/CompetitiveTFT threads only via snippets; not verified.
- Fast 9 "40-50g left after leveling" rule: snippet only, source unclear.
