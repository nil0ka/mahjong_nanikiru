# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a collection of "What to discard" (nanikiru) problems for Mahjong. Problems and answers are generated using Claude AI.

**Current Status**: Manual operation using Claude Code custom commands.

**Future Plan**: Automate daily problem/answer generation via GitHub Actions (requires Anthropic API key).

## Architecture

### Current Workflow (Manual)

Problems and answers are generated manually using:
- Claude Code custom commands (`/create-question`, `/create-solution`)
- Python scripts (`scripts/generate_question.py`, `scripts/generate_solution.py`)

### Future Automated Workflow (Planned)

Once Anthropic API key is obtained:

1. **Problem Generation (9:00 AM JST)**
   - GitHub Actions triggers `scripts/generate_question.py`
   - Problem saved as `problems/NNN/question.md`
   - GitHub Issue created with the problem

2. **Answer Generation (6:00 PM JST)**
   - GitHub Actions triggers `scripts/generate_solution.py`
   - Answer saved as `problems/NNN/solution.md`
   - Pull Request created with the answer
   - PR auto-merged and corresponding Issue closed

**Note**: Workflow files are currently in `.github/workflows-disabled/`. Move to `.github/workflows/` to enable automation.

### Directory Structure

- `problems/` - Generated problems and answers (Markdown format)
- `scripts/` - Python scripts for generating content via Claude API
- `.claude/commands/` - Custom commands for Claude Code CLI
- `.github/workflows-disabled/` - GitHub Actions workflows (currently disabled)

## Key Concepts

### Mahjong Problem Format

Problems use Unicode Mahjong tiles (🀇-🀏 萬子、🀙-🀡 筒子、🀐-🀘 索子、🀀-🀆 字牌) and include:
- **Difficulty level**: 10-point scale (★☆☆☆☆☆☆☆☆☆ 1/10 to ★★★★★★★★★★ 10/10)
- **Theme**: Problem category (e.g., Riichi decision, hand selection, push/fold, wait selection, formal tenpai, calling decision, safe tile selection)
- **Game state**: Round (東1局, etc.), seat wind, dora indicator, turn number
- **Hand tiles**: Exactly 14 tiles (13 tiles in hand + 1 drawn tile)
  - **CRITICAL**: Must specify the drawn tile (ツモ牌) separately from the 13-tile hand
  - The problem asks "what to discard from these 14 tiles"
  - Without specifying the drawn tile, the problem cannot be answered correctly
- **Discards (河)**: Discard piles for self, shimocha (下家), toimen (対面), and kamicha (上家)
- **Situation**: Additional context as needed

### Answer Format

Answers include:
- Problem recap
- Correct discard
- Detailed analysis of the hand
- Comparison of multiple candidate discards
- Quantitative analysis (tile acceptance, etc.)
- Learning points

### Unicode Mahjong Tiles Reference

**CRITICAL**: Always refer to this table when reading or writing mahjong tiles to ensure correct tile identification.

**萬子 (Manzu / Characters)**:
- 🀇 = 1m (一萬)
- 🀈 = 2m (二萬)
- 🀉 = 3m (三萬)
- 🀊 = 4m (四萬)
- 🀋 = 5m (五萬)
- 🀌 = 6m (六萬)
- 🀍 = 7m (七萬)
- 🀎 = 8m (八萬)
- 🀏 = 9m (九萬)

**筒子 (Pinzu / Dots)**:
- 🀙 = 1p (一筒)
- 🀚 = 2p (二筒)
- 🀛 = 3p (三筒)
- 🀜 = 4p (四筒)
- 🀝 = 5p (五筒)
- 🀞 = 6p (六筒)
- 🀟 = 7p (七筒)
- 🀠 = 8p (八筒)
- 🀡 = 9p (九筒)

**索子 (Souzu / Bamboo)**:
- 🀐 = 1s (一索)
- 🀑 = 2s (二索)
- 🀒 = 3s (三索)
- 🀓 = 4s (四索)
- 🀔 = 5s (五索)
- 🀕 = 6s (六索)
- 🀖 = 7s (七索)
- 🀗 = 8s (八索)
- 🀘 = 9s (九索)

**字牌 (Jihai / Honor tiles)**:
- 🀀 = 東 (East)
- 🀁 = 南 (South)
- 🀂 = 西 (West)
- 🀃 = 北 (North)
- 🀆 = 白 (White dragon)
- 🀅 = 發 (Green dragon)
- 🀄 = 中 (Red dragon)

**Important Notes**:
- When analyzing hands, discards, or generating problems/solutions, always verify tile identification using this reference
- Misidentifying tiles (e.g., confusing 🀠 8p with 🀡 9p) can lead to completely incorrect analysis
- When checking for "genbutsu" (現物 / safe tiles), verify the exact Unicode character against the discard pile

## Scoring and Expected Value Calculations

**Mahjong scoring is critical for push/fold decisions and problem quality**:

1. **Understanding yaku (役) and han (翻)**:

   **1 han yaku**:
   - Riichi (立直): 1 han (closed only)
   - Tanyao (断么九): 1 han (some rules allow open, some closed only)
   - Pinfu (平和): 1 han (closed only) - all sequences, two-sided wait, non-value pair
   - Ippatsu (一発): 1 han (closed only, must win within 1 turn of riichi)
   - Tsumo (門前清自摸和): 1 han (closed only)
   - Yakuhai (役牌): 1 han - honor triplet (ton/nan/sha/pei/haku/hatsu/chun)
   - Iipeikou (一盃口): 1 han (closed only) - two identical sequences
   - Rinshan kaihou (嶺上開花): 1 han - winning on kan draw
   - Chankan (槍槓): 1 han - robbing a kan
   - Haitei raoyue (海底撈月): 1 han - winning on last draw
   - Houtei raoyui (河底撈魚): 1 han - winning on last discard

   **2 han yaku**:
   - Chiitoitsu (七対子): 2 han (closed only, always 25 fu) - seven pairs
   - Double riichi (ダブル立直): 2 han (closed only) - riichi on first turn
   - Sanshoku doujun (三色同順): 2 han (1 han if open) - same sequence in all 3 suits
   - Ikkitsuukan (一気通貫): 2 han (1 han if open) - 123, 456, 789 in same suit
   - Toitoi (対々和): 2 han - all triplets/quads
   - Sanankou (三暗刻): 2 han - three closed triplets
   - Sanshoku doukou (三色同刻): 2 han - same triplet in all 3 suits
   - Sankantsu (三槓子): 2 han - three quads
   - Chanta (混全帯么九): 2 han (1 han if open) - all sets contain terminals/honors
   - Honroutou (混老頭): 2 han - all terminals and honors only
   - Shousangen (小三元): 2 han - two dragon triplets + one dragon pair

   **3 han yaku**:
   - Honitsu (混一色): 3 han (2 han if open) - one suit plus honors
   - Junchan (純全帯么九): 3 han (2 han if open) - all sets contain terminals (no honors)
   - Ryanpeikou (二盃口): 3 han (closed only) - two pairs of identical sequences (4 sequences total)

   **6 han yaku**:
   - Chinitsu (清一色): 6 han (5 han if open) - one suit only

   **Yakuman (役満) - 13+ han**:
   - Kokushi musou (国士無双): Yakuman (closed only) - all 13 types of terminals and honors
     - Kokushi 13-sided wait (国士無双13面待ち): Double yakuman in some rules
   - Suuankou (四暗刻): Yakuman (closed only) - four closed triplets
     - Suuankou tanki (四暗刻単騎): Double yakuman in some rules - waiting on the pair
   - Daisangen (大三元): Yakuman - all three dragon triplets (haku, hatsu, chun)
   - Shousuushii (小四喜): Yakuman - three wind triplets + one wind pair
   - Daisuushii (大四喜): Double yakuman - all four wind triplets
   - Tsuuiisou (字一色): Yakuman - all honors only
   - Ryuuiisou (緑一色): Yakuman - all green tiles (2,3,4,6,8 of bamboo + green dragon)
   - Chinroutou (清老頭): Yakuman - all terminals only (1,9 of each suit)
   - Chuuren poutou (九蓮宝燈): Yakuman (closed only) - 1112345678999 + any tile of same suit
     - Junsei chuuren (純正九蓮宝燈): Double yakuman in some rules - 9-sided wait
   - Suukantsu (四槓子): Yakuman - four quads
   - Tenhou (天和): Yakuman (dealer only) - winning on dealer's initial 14 tiles
   - Chiihou (地和): Yakuman (non-dealer only) - winning on first draw before any calls
   - Renhou (人和): Yakuman in some rules (often just mangan) - winning on another player's first discard

   **Dora**:
   - Dora (ドラ): 1 han per dora tile
   - Uradora (裏ドラ): 1 han per uradora (riichi only)
   - Akadora (赤ドラ): 1 han per red five (if using red fives)

   **Kuisagari (食い下がり) - Han reduction when open**:
   - **Lose 1 han when opened**: Sanshoku doujun (2→1), Ikkitsuukan (2→1), Chanta (2→1), Honitsu (3→2), Junchan (3→2), Chinitsu (6→5)
   - **Tanyao**: Some rules allow open (1 han), some require closed only
   - **CANNOT be made with open hand**: Riichi, Pinfu, Tsumo, Iipeikou, Ryanpeikou, Chiitoitsu, all Yakuman except those that allow open sets

   **Common combinations**:
     - Riichi (1) + Tanyao (1) + Dora (2) = 4 han 30 fu = 7700 points ron
     - Riichi (1) + Tsumo (1) + Pinfu (1) + Dora (1) = 4 han 20 fu = 2600 all (dealer tsumo) or 1300-2600 (child tsumo)
     - Chiitoitsu (2) + Dora (2) = 4 han 25 fu = 6400 points (always 25 fu)
     - Note: 4 han 20 fu does NOT round to 5 han; it stays at 4 han 20 fu
     - 5 han (any fu): Mangan 8000 points

2. **Point calculations** (子 child / 親 dealer):
   - **1 han 30 fu**: 1000 ron / 300-500 tsumo (dealer: 1500 / 500 all)
   - **2 han 25 fu** (chiitoitsu only): 1600 ron / 400-800 tsumo (dealer: 2400 / 800 all)
   - **2 han 30 fu**: 2000 ron / 500-1000 tsumo (dealer: 2900 / 1000 all)
   - **3 han 25 fu** (chiitoitsu): 3200 ron / 800-1600 tsumo (dealer: 4800 / 1600 all)
   - **3 han 30 fu**: 3900 ron / 1000-2000 tsumo (dealer: 5800 / 2000 all)
   - **3 han 60 fu**: 5800 ron / 1500-2900 tsumo (dealer: 8700 / 2900 all)
   - **4 han 20 fu** (pinfu tsumo only): N/A ron / 1300-2600 tsumo (dealer: 2600 all)
   - **4 han 25 fu** (chiitoitsu): 6400 ron / 1600-3200 tsumo (dealer: 9600 / 3200 all)
   - **4 han 30 fu**: 7700 ron / 2000-3900 tsumo (dealer: 11600 / 3900 all)
   - **4 han 40+ fu or 5 han**: 8000 ron / 2000-4000 tsumo (dealer: 12000 / 4000 all) = **Mangan (満貫)**
   - **6-7 han**: 12000 ron / 3000-6000 tsumo (dealer: 18000 / 6000 all) = **Haneman (跳満)**
   - **8-10 han**: 16000 ron / 4000-8000 tsumo (dealer: 24000 / 8000 all) = **Baiman (倍満)**
   - **11-12 han**: 24000 ron / 6000-12000 tsumo (dealer: 36000 / 12000 all) = **Sanbaiman (三倍満)**
   - **13+ han / Yakuman**: 32000 ron / 8000-16000 tsumo (dealer: 48000 / 16000 all) = **Yakuman (役満)**

   **Important fu calculations**:
   - **Pinfu tsumo: 20 fu** (only case where 20 fu exists; cannot ron with pinfu)
   - **Standard ron (no pinfu): 30 fu base**
   - **With terminal/honor pon**: +8 fu per closed pon of terminals/honors
   - **With kan**: +16 fu (closed), +8 fu (open)
   - **Closed wait (kanchan, penchan, tanki)**: +2 fu
   - **Common fu patterns**:
     - Pinfu tsumo: 20 fu
     - Open tanyao/honitsu with simple pons: 30 fu
     - Closed hand with terminal/honor pon: 40-50 fu
   - **4 han depends heavily on fu**: 20 fu = 2600 all / 1300-2600, 30 fu = 7700, 40+ fu = 8000 (mangan)
   - **5+ han**: Always mangan or above regardless of fu

3. **Push/fold (押し引き) decisions require**:
   - Current ranking and point differences
   - Expected value of your hand (probability × points)
   - Risk of dealing in (放銃リスク): potential loss if opponent wins
   - Turn number and tiles remaining
   - Opponent's riichi timing and visible tiles
   - Example: "You're in 2nd place, 8000 points behind. Opponent riichi. Your hand is 2-shanten, 3000 point potential. → Fold and preserve 2nd place"

   **Critical: Analysis methodology for push/fold problems**:

   a. **Analyze YOUR hand's potential (期待値分析)**:
   - Current shanten level and number of useful tiles
   - **List all possible ideal forms (理想形) with yaku and point values**:
     - Minimum: Basic yaku only (e.g., "Hatsu only: 1 han = 1000-2000 points")
     - With riichi: Riichi + base yaku (e.g., "Riichi(1) + Hatsu(1) = 2 han = 2000-3900 points")
     - With dora: Include dora scenarios (e.g., "Riichi(1) + Hatsu(1) + Dora(1) = 3 han = 3900-5800 points")
     - Maximum realistic: Best case scenario (e.g., "Riichi(1) + Tsumo(1) + Hatsu(1) + Dora(2) = 5 han = 8000 points (mangan)")
   - **Realistic evaluation**: Likelihood of reaching tenpai and winning, considering turn number and useful tiles
   - **AVOID speculative probability percentages** (e.g., "5-10% chance") unless you can provide clear calculation basis
   - **Use qualitative assessments** instead: "extremely low", "low", "moderate", "high"

   b. **Analyze OPPONENT's hand from river (河の読み)**:
   - **Dora visibility**: If dora is not visible in rivers, opponent likely has 1+ dora
   - **Yakuhai visibility**: Check which honor tiles (役牌) are visible/missing
   - **Suit distribution**: Check if染め手 (honitsu/chinitsu) is possible based on discards
   - **Kan dora**: Check if additional kan dora indicators exist
   - **Riichi timing**: Early riichi (≤8 turns) suggests good wait, late riichi (12+ turns) might be bad wait

   **List possible opponent hand patterns with point estimates**:
   - Pattern 1: Riichi only = 1000-2000 points (note: "possibility is low" if dora not visible)
   - Pattern 2: Riichi + Tsumo = 2 han = 2000-3900 points
   - Pattern 3: Riichi + Dora(1) = 2 han = 2000-3900 points
   - Pattern 4: Riichi + Yakuhai = 2 han = 2000-3900 points
   - Pattern 5: Riichi + Dora(1) + Tsumo(1) = 3 han = 3900-5800 points
   - Pattern 6: Riichi + Dora(2+) = 3+ han = 3900-8000+ points
   - Pattern 7: Riichi + Pinfu + Dora + Tsumo = 4 han = 8000 points (mangan)
   - (Add more patterns as relevant)

   **Conclusion on opponent's likely point range**: Based on river analysis, state which range is most likely
   - Example: "Since dora is not visible, 3 han (3900-5800 points) or higher is likely. Minimum 2 han 2000 points, worst case mangan 8000 points."
   - **AVOID speculative percentages** for deal-in probability unless clearly calculable
   - **Use realistic point range estimates** based on river analysis: "Deal-in loss: 2000-8000 points scale (realistically 3000-6000 points)"

   c. **Compare risk vs reward**:
   - Your winning expectation (very low / low / moderate / high) × your point range
   - Opponent's deal-in risk × opponent's likely point range
   - Ranking impact: Will winning change your rank? Will dealing in drop your rank?
   - **Use qualitative comparison**: "Winning expectation (extremely low, even if winning only 1000-2000 points) << Deal-in loss (3000-6000 points scale)"

   d. **Important notes**:
   - **DO NOT use fabricated probability percentages** (e.g., "35% deal-in rate", "5-10% winning rate") without clear basis
   - **DO use river information** to estimate opponent's hand strength (dora visibility, yakuhai, suit distribution)
   - **DO list ideal forms** of your hand with specific yaku combinations and point values
   - **DO use qualitative terms** for likelihood: "extremely low", "low", "moderate", "high", "very high"
   - **DO provide point ranges** based on yaku analysis, not single-point guesses

4. **When generating problems with scoring themes**:
   - Clearly state current scores and ranking
   - Calculate the exact han/fu and point value of the hand
   - Consider all possible yaku combinations
   - Factor in dora tiles for accurate calculations
   - For push/fold: State opponents' visible strength and point positions

## Genbutsu (現物) - Absolute Safe Tiles

**Genbutsu (現物) is one of the most important concepts in mahjong defense**:

1. **Definition**:
   - **Genbutsu (現物)**: A tile that a riichi declarer has already discarded
   - **Key rule**: A player cannot win on a tile they have already discarded
   - **Result**: Genbutsu is **100% safe (absolutely safe)** - it will NEVER deal into that riichi player

2. **Identifying genbutsu**:
   - Look at the riichi player's discard pile (河)
   - Any tile visible in their discards is genbutsu against that player
   - Example: If opponent (toimen) declared riichi and has 🀗 (8s) in their river, then 🀗 is genbutsu = absolute safety

3. **Common mistakes to avoid**:
   - ❌ Wrong: "The tile is in opponent's river, so it's relatively safe"
   - ✅ Correct: "The tile is in the riichi player's river, so it's genbutsu (absolute safety, 0% risk)"
   - ❌ Wrong: "It's not a complete genbutsu, but the risk is low"
   - ✅ Correct: "It IS genbutsu - there is no such thing as 'partial genbutsu'. Either it's genbutsu (100% safe) or it's not."

4. **Multiple riichi players**:
   - If player A declared riichi and has 🀗 in their river, 🀗 is genbutsu against player A
   - But if player B also declared riichi and does NOT have 🀗 in their river, 🀗 is NOT safe against player B
   - Always check WHICH riichi player's discard pile you're looking at

5. **Priority in defense**:
   - **1st priority: Genbutsu** (100% safe)
   - 2nd priority: Safe honor tiles (multiple copies visible)
   - 3rd priority: Suji tiles (safer but not 100%)
   - 4th priority: Terminal tiles (relatively safer)
   - When you have genbutsu available, ALWAYS use it when defending

6. **In problem analysis**:
   - When analyzing push/fold problems, clearly identify if any tiles are genbutsu
   - Example: "🀗 is genbutsu (対面の現物) = absolute safety"
   - Never describe genbutsu as "relatively safe" or "probably safe" - it's ABSOLUTELY safe

## Critical: Shanten Calculation and Problem Accuracy

**The most important aspect of problem generation is correctly understanding and representing the hand state**:

1. **Calculate shanten accurately for all winning patterns**:
   - **4 mentsu + 1 jantou (standard)**: Most common pattern
   - **Chiitoitsu (七対子)**: Seven pairs - calculate separately
   - **Kokushi musou (国士無双)**: 13 orphans (1/9/honors) - calculate separately
   - **Take the minimum shanten** among all three patterns
   - Determine if the hand is tenpai (0-shanten), iishanten (1-shanten), ryanshanten (2-shanten), etc.
   - Any shanten level is valid for problems - not just tenpai or iishanten
   - Example valid problems: "How to proceed from ryanshanten?", "Which tile to discard in this iishanten position?"
   - **Important**: A hand might be iishanten for standard but tenpai for chiitoitsu - always check all patterns

2. **Verify problem statements match reality**:
   - If you state "現在テンパイ" (currently tenpai), the 13-tile hand must actually be tenpai
   - If you state "🀓を引けばテンパイ" (drawing 🀓 makes it tenpai), verify this by calculation
   - **Problem 001 error example**: Stated "iishanten" and "drawing 🀓 makes it tenpai", but the hand was actually ryanshanten+

3. **Recommended hand creation process**:
   - Start with a complete winning hand (14 tiles = 4 mentsu + 1 jantou)
   - Remove tiles according to desired shanten:
     - Tenpai: Remove one waiting tile
     - Iishanten: Break apart one mentsu partially
     - Ryanshanten+: Further deconstruct
   - Calculate actual shanten of the resulting 13-tile hand
   - Describe the hand state accurately in the problem text

4. **Critical: Verify shanten calculation thoroughly**:
   - **ALWAYS use the Unicode tile reference table** to correctly identify each tile
   - **Calculate shanten for the base 13-tile hand** (before any draws)
   - **Test EVERY useful tile** to see what happens when drawn:
     - Example: If you claim "drawing 4p makes it tenpai", actually add 4p to the hand and verify it becomes 14 tiles with only 1 tile away from winning
     - Check if drawing other tiles also leads to tenpai - if too many tiles lead to quick tenpai, the hand is not appropriate for push/fold problems
   - **For each useful tile, verify the resulting hand state**:
     - Does it become tenpai? (can discard 1 tile to reach 0-shanten)
     - Does it stay iishanten? (still 1-shanten)
     - What tiles can be discarded after the draw?
   - **Example verification for problem 001 initial error**:
     - Base hand: 🀈🀉🀊🀙🀙🀛🀝🀔🀕🀖🀅🀅🀅 (13 tiles)
     - Drawing 🀜(4p): 🀈🀉🀊🀙🀙🀛🀜🀝🀔🀕🀖🀅🀅🀅 (14 tiles)
     - Analysis: 234m + 11p + 345p + 456s + hatsu-hatsu-hatsu = 5 groups complete! Can discard 1p to win immediately
     - **This is tenpai, NOT iishanten**! The problem statement was wrong.

5. **Match hand state to problem theme**:
   - **Push/fold problems** require hands that are far from tenpai:
     - Iishanten with limited useful tiles (2-3 types max)
     - Ryanshanten or further
     - Low point potential (1-2 han only)
     - If drawing ANY of 4+ different tile types leads to immediate or very quick tenpai, the hand is TOO GOOD for push/fold
   - **Riichi decision problems** require tenpai hands
   - **Hand development problems** can be iishanten or ryanshanten
   - **Wait selection problems** require tenpai or near-tenpai hands

6. **Validation checks** (automated in `scripts/generate_question.py`):
   - Hand tile count = exactly 13
   - Each tile type ≤ 4 (across hand + all rivers + dora indicator)
   - River counts match turn number (allowing ±2 for calls)
   - **Shanten calculation matches problem description**
   - **Tile addition claims are verified** (e.g., "drawing X gives tenpai")
   - **Problem theme matches hand state** (e.g., push/fold problems don't use hands that easily reach tenpai)

## Point Distribution Validation

**Point distributions must be realistic based on the round and honba (本場) count**:

1. **Starting points (配給原点)**:
   - Standard: 25000 points × 4 players = 100000 points total
   - **Always verify**: Sum of all four players' points = 100000 (or match your ruleset)

2. **Dealer position by round (場と親の位置関係)**:
   - **東1局 (East 1)**: 東家 (East seat) is dealer
   - **東2局 (East 2)**: 南家 (South seat) is dealer
   - **東3局 (East 3)**: 西家 (West seat) is dealer
   - **東4局 (East 4)**: 北家 (North seat) is dealer
   - **南1局 (South 1)**: 東家 (East seat) is dealer, then rotation continues
   - **Always verify**: The dealer mentioned in the problem matches the expected dealer for that round

3. **東1局0本場 (East 1, Round 0)**:
   - **Expected**: All players must have exactly 25000 points (starting points)
   - **Why**: This is the very first hand of the game - no wins or draws have occurred yet
   - **No exceptions**: Point deviations are not possible in East 1-0
   - **Constraints**:
     - If you want to vary point distributions, DO NOT use 東1局0本場
     - For push/fold (押し引き) problems, DO NOT use 東1局0本場 as point situations are critical to the decision

4. **東1局1本場 (East 1, Round 1)**:
   - **Only possible if**:
     - Dealer (東家) won the previous hand (East 1-0) → Dealer's points should have INCREASED
     - OR: Dealer was tenpai during ryuukyoku (流局) → Small point transfers (±1000-3000)
   - **NOT possible if**: Dealer's points decreased significantly (e.g., from 25000 to 16000)
   - **Why**: 1本場 means dealer retained their seat, which only happens on dealer win or dealer tenpai

5. **東2局以降 or 南場 (East 2+ or South round)**:
   - **Expected**: Larger point deviations are natural (multiple hands have been played)
   - **Verify**: Point distribution should reflect plausible game progression
   - Example: 東3局1本場 with points like (32000, 28000, 24000, 16000) is reasonable

6. **Validation rules for problem generation**:
   - ✅ **Always check**: Does the dealer position match the round? (Section 2 above)
   - ✅ **Always check**: Does the 本場 count match the point distribution story?
   - ✅ **Always check**: If using 1本場+, can you explain how the dealer retained their seat?
   - ✅ **Always check**: Sum of points = 100000 (standard ruleset)
   - ✅ **Red flag**: 東1局0本場 with non-standard points (anything other than 25000 × 4)
   - ✅ **Red flag**: Push/fold (押し引き) problem using 東1局0本場 (point situation is critical!)
   - ✅ **Red flag**: 東1局1本場 with dealer having fewer points than starting (25000)
   - ✅ **Red flag**: Large point swings (>10000 points) in early rounds (東1局-東2局)

7. **Recommended approach**:
   - For simple problems where point situation is NOT important: Use **東1局0本場** with starting points (25000 × 4)
   - For problems needing point pressure (push/fold, 押し引き, オーラス, etc.): Use **東2局+, 南場, or オーラス** with realistic point distributions
   - If using 1本場+: Write a brief explanation of how dealer retained their seat (e.g., "前局は親の2000点和了" or "前局は親テンパイ流局")

## Solution Generation: Critical Validation Points

**When generating solutions, always verify these points**:

1. **Accurate tile identification**:
   - **ALWAYS use the Unicode tile reference table above** to correctly identify every single tile
   - Do NOT confuse similar-looking tiles:
     - 🀗 = 8s (NOT 7s), 🀖 = 7s
     - 🀠 = 8p (NOT 9p), 🀡 = 9p
     - 🀎 = 8m (NOT 9m), 🀏 = 9m
   - Verify you're reading the 13-tile hand correctly from the problem (check each tile one by one using the reference table)

2. **Independent shanten calculation**:
   - Do NOT trust the problem description blindly (Problem 001 had errors!)
   - **ALWAYS use the Unicode tile reference table** to correctly identify each tile first
   - Calculate the actual shanten of the 13-tile hand yourself
   - **Test ALL useful tiles** to verify what happens when drawn:
     - Example: Problem says "drawing 4p makes it tenpai"
       1. Add 4p to the 13-tile hand to make 14 tiles
       2. Check if you can discard 1 tile to reach tenpai
       3. Test other tiles (2p, 5p, 8p, etc.) as well
     - Include ALL useful tiles in your solution, not just the ones mentioned in the problem
   - If the problem says "tenpai" but it's actually iishanten, use the correct calculation
   - If the problem has shanten errors, point them out in your solution
   - Describe the actual state in your solution

3. **Accurate tile counting**:
   - Count visible tiles: hand (13) + all rivers + dora indicator + any calls
   - Calculate remaining tiles for each type (max 4 of each)
   - When stating "X tiles remaining" or "waiting on Y tiles", verify the count
   - Example: If 🀇 appears 2 times in hand + 1 in rivers = 3 visible, then 1 remaining

4. **Identify genbutsu (現物) correctly**:
   - **Critical for push/fold problems**: Check if any tiles are genbutsu
   - **How to identify**: Look at riichi player's discard pile (河)
   - If a tile appears in the riichi player's river, it is **genbutsu = 100% safe**
   - **Common mistake**: "The tile is in opponent's river, so it's relatively safe" ❌
   - **Correct**: "The tile is in the riichi player's river, so it's genbutsu (絶対安全, 100% safe)" ✅
   - Example: Problem states "対面（リーチ）の河: ...🀗..." and you have 🀗 → This IS genbutsu
   - Never say "relatively safe" when it's actually genbutsu - it's ABSOLUTELY safe (0% risk)

5. **Validate recommended discard**:
   - The tile you recommend discarding MUST be in the actual 13-tile hand
   - Do NOT recommend discarding a tile that doesn't exist in the hand

6. **Validate point distribution consistency**:
   - Check that the sum of all four players' points equals 100000
   - **東1局0本場**: All players must have exactly 25000 points
     - If point distribution differs, the problem has an error - note this in your solution
   - **東1局1本場**: Dealer's points should reflect dealer win or dealer tenpai draw
     - Dealer win: Dealer's points should be > 25000
     - Dealer tenpai draw: Small point transfers (±1000-3000)
     - If dealer has significantly fewer points (e.g., 16000), the problem setup is inconsistent - note this in your solution
   - When you find inconsistencies, point them out in your solution explanation, but still answer the problem based on the given scenario

7. **Validation checks** (automated in `scripts/generate_solution.py`):
   - Recommended discard is in the hand
   - Shanten claims match actual calculation
   - Tile counts are accurate
   - Point distribution is consistent with round/honba

8. **Candidate discard ordering and presentation**:
   - **ALWAYS order candidates from best to worst** (lowest risk to highest risk)
   - Candidate 1 should be the BEST option (recommended choice)
   - Candidate 2 should be the second-best option
   - Candidate 3 should be the worst option among the candidates discussed
   - **Why this matters**: Readers naturally expect candidates to be presented in order of quality
   - **Example ordering** (push/fold problem):
     - Candidate 1: Discard genbutsu tile (safest, fold) ← BEST
     - Candidate 2: Discard terminal tile 9m (medium risk, attack) ← Second-best
     - Candidate 3: Discard 1p early tile (highest risk, attack) ← WORST
   - **Clearly label the worst candidate**: Add clarifying text like "最も危険" (most dangerous) or "3つの候補の中で最悪" (worst among the three candidates)
   - **Avoid confusing ordering**: Do NOT put the worst option as Candidate 2 and second-worst as Candidate 3

9. **Expected value calculation and push/fold analysis** (for push/fold theme problems):

   **For YOUR hand**:
   - **DO list all ideal forms** with specific yaku and point values:
     - Example: "Minimum: Hatsu only (1 han) = 1000-2000 points"
     - Example: "With riichi: Riichi(1) + Hatsu(1) = 2 han = 2000-3900 points"
     - Example: "With dora: Riichi(1) + Hatsu(1) + Dora(1) = 3 han = 3900-5800 points"
     - Example: "Maximum: Riichi(1) + Tsumo(1) + Hatsu(1) + Dora(2) = 5 han = 8000 points (mangan)"
   - **DO use qualitative likelihood assessment**: "extremely low", "low", "moderate", "high"
   - **DO NOT use fabricated probability percentages** like "5-10% winning rate", "35% deal-in rate" without clear calculation basis

   **For OPPONENT's hand** (especially riichi declarers):
   - **DO analyze river information systematically**:
     - Dora visibility: "Dora 2s (🀑) is not visible → opponent likely has 1+ dora"
     - Yakuhai visibility: "東南中 discarded, but 白發北 not visible → yakuhai possibility"
     - Suit distribution: "萬筒索 mixed → not honitsu/chinitsu"
     - Riichi timing: "8th turn riichi → likely good wait"
   - **DO list possible hand patterns with point ranges**:
     - Pattern 1: Riichi only = 1000-2000 points (note: "low possibility if dora not visible")
     - Pattern 2: Riichi + Tsumo = 2 han = 2000-3900 points
     - Pattern 3: Riichi + Dora(1) = 2 han = 2000-3900 points
     - Pattern 4: Riichi + Yakuhai = 2 han = 2000-3900 points
     - Pattern 5: Riichi + Dora(1) + Tsumo(1) = 3 han = 3900-5800 points
     - Pattern 6: Riichi + Dora(2+) = 3+ han = 3900-8000+ points
     - Pattern 7: Riichi + Pinfu + Dora + Tsumo = 4 han = 8000 points (mangan)
   - **DO provide conclusion on likely point range**:
     - Example: "Since dora is not visible, 3 han (3900-5800 points) or higher is likely. Minimum 2 han 2000 points, worst case mangan 8000 points."
     - Example: "Deal-in loss: 2000-8000 points scale (realistically 3000-6000 points)"
   - **DO NOT use single-point guesses** like "4000 points × 35% = 1400 points expected loss"

   **For final comparison**:
   - **DO use qualitative comparison**:
     - Example: "Winning expectation (extremely low, even if winning only 1000-2000 points) << Deal-in loss (3000-6000 points scale)"
   - **DO NOT fabricate numeric expected values** without clear basis

## Commands

### Claude Code Custom Commands

```bash
/create-question  # Generate a new daily problem
/create-solution  # Generate answer for today's problem
```

### Python Scripts

```bash
# Generate problem (auto-numbered)
python scripts/generate_question.py
# → creates problems/001/question.md

# Generate problem with specific number
python scripts/generate_question.py 5
# → creates problems/005/question.md

# Generate answer for latest problem
python scripts/generate_solution.py
# → creates problems/001/solution.md

# Generate answer for specific problem
python scripts/generate_solution.py 5
# → creates problems/005/solution.md

# List all problems
python scripts/list_problems.py

# Filter by theme
python scripts/list_problems.py --theme "リーチ判断"

# Filter by difficulty
python scripts/list_problems.py --difficulty 5
```

Scripts include error handling and automatic retry with exponential backoff for API failures.

### Enabling GitHub Actions (Future)

When ready to enable automation:

1. Obtain Anthropic API key from https://console.anthropic.com/
2. Add `ANTHROPIC_API_KEY` to GitHub Secrets (Settings > Secrets and variables > Actions)
3. Create GitHub labels:
   ```bash
   gh label create "daily-problem" --color "0E8A16" --description "Daily generated problem"
   gh label create "daily-answer" --color "1D76DB" --description "Daily generated answer"
   ```
4. Move workflow files:
   ```bash
   mv .github/workflows-disabled/*.yml .github/workflows/
   ```
5. Manually trigger workflows to test:
   ```bash
   gh workflow run create-question.yml
   gh workflow run create-solution.yml
   ```

## Environment Setup

For local development:
- `ANTHROPIC_API_KEY` - Claude API key (required for Python scripts)

## File Naming Convention

Problems are organized by sequential numbers in separate directories:
- Question: `problems/001/question.md`, `problems/002/question.md`, ..., `problems/1000/question.md`, etc.
- Solution: `problems/001/solution.md`, `problems/002/solution.md`, ..., `problems/1000/solution.md`, etc.

Numbers are zero-padded to at least 3 digits (001-999), but support unlimited digits (1000+).

The date is included in the problem content (markdown heading), not in the file/directory name.
