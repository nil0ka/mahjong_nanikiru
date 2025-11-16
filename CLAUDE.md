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
  - **Difficulty criteria**:
    - **1-2 (Very Easy)**: Single obvious correct answer, no calculation needed, basic concepts only
      - Example: Discard an isolated honor tile with no yaku value
    - **3-4 (Easy)**: Correct answer is clear with basic analysis, 1-2 viable candidates
      - Example: Push/fold with genbutsu available and obvious danger tiles
      - Example: Simple tenpai decision with clear yaku and good wait
    - **5-6 (Medium)**: Requires analysis of multiple factors, 2-3 reasonable candidates
      - Example: Push/fold requiring river reading and opponent hand estimation
      - Example: Wait selection between different yaku patterns
    - **7-8 (Hard)**: Complex analysis required, multiple viable candidates with trade-offs
      - Example: Push/fold with no genbutsu, requiring deep probability analysis
      - Example: Hand development with multiple valid paths (honitsu vs tanyao vs speed)
    - **9-10 (Very Hard)**: Expert-level analysis, subtle differences between candidates
      - Example: Optimal tile efficiency in complex iishanten position
      - Example: Push/fold in oorasu with intricate ranking calculations
  - **Key difficulty factors**:
    - **Clarity of correct answer**: How obvious is the best choice?
    - **Number of viable candidates**: More candidates = higher difficulty
    - **Analysis depth required**: Simple counting vs complex probability/ranking analysis
    - **Trade-offs between candidates**: Subtle differences = higher difficulty
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

## Tile Notation Policy

**MANDATORY: Unicode + Numeric Notation (併記)**

To prevent misidentification errors (e.g., confusing 567s with "456s"), all problems and solutions must use **both Unicode and numeric notation**:

**Format**:
```markdown
## あなたの手牌（13枚）
\`\`\`
🀇🀈🀙🀚🀛🀜🀔🀕🀖🀃🀃🀃🀅
(1m2m1p2p3p4p5s6s7s北北北發)
\`\`\`

## ツモ牌
\`\`\`
🀝
(5p)
\`\`\`
```

**Why this format**:
- Unicode tiles (🀔🀕🀖) provide visual representation for mahjong players
- Numeric notation (5s6s7s) prevents misidentification and ensures accurate analysis
- Combining both maximizes readability and accuracy

**Internal analysis process**:
1. Read Unicode tiles using reference table (one by one)
2. **Convert to numeric notation** (e.g., 🀔🀕🀖 → `5s6s7s`)
3. Analyze hand structure using numeric notation
4. Verify sequences numerically (5-6-7 is continuous, NOT 4-5-6)

### Unicode Mahjong Tiles Reference

**CRITICAL**: Always refer to this table when reading or writing mahjong tiles to ensure correct tile identification.

**萬子 (Manzu)**: 🀇=1m 🀈=2m 🀉=3m 🀊=4m 🀋=5m 🀌=6m 🀍=7m 🀎=8m 🀏=9m

**筒子 (Pinzu)**: 🀙=1p 🀚=2p 🀛=3p 🀜=4p 🀝=5p 🀞=6p 🀟=7p 🀠=8p 🀡=9p

**索子 (Souzu)**: 🀐=1s 🀑=2s 🀒=3s 🀓=4s 🀔=5s 🀕=6s 🀖=7s 🀗=8s 🀘=9s

**字牌 (Honors)**: 🀀=東 🀁=南 🀂=西 🀃=北 🀆=白 🀅=發 🀄=中

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

   **Yakuman (役満) - 13+ han** (common types):
   - Kokushi musou (国士無双): All 13 types of terminals/honors (closed only)
   - Suuankou (四暗刻): Four closed triplets (closed only)
   - Daisangen (大三元): All three dragon triplets
   - Shousuushii (小四喜): Three wind triplets + one wind pair
   - Tsuuiisou (字一色): All honors only
   - Chuuren poutou (九蓮宝燈): 1112345678999 + any tile of same suit (closed only)
   - Other rare yakuman: Daisuushii, Ryuuiisou, Chinroutou, Suukantsu, Tenhou, Chiihou (32000 points child ron, 48000 dealer)

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
   - **2 han 30 fu**: 2000 ron / 500-1000 tsumo (dealer: 2900 / 1000 all)
   - **3 han 30 fu**: 3900 ron / 1000-2000 tsumo (dealer: 5800 / 2000 all)
   - **4 han 20 fu** (pinfu tsumo): N/A ron / 1300-2600 tsumo (dealer: 2600 all)
   - **4 han 30 fu**: 7700 ron / 2000-3900 tsumo (dealer: 11600 / 3900 all)
   - **4 han 40+ fu or 5+ han**: 8000+ ron / 2000-4000+ tsumo (dealer: 12000+ / 4000+ all) = **Mangan+ (満貫以上)**
   - **Chiitoitsu** (always 25 fu): 2 han = 1600, 3 han = 3200, 4 han = 6400 (ron, child)
   - **Named limits**: Mangan (満貫) 8000, Haneman (跳満) 12000, Baiman (倍満) 16000, Sanbaiman (三倍満) 24000, Yakuman (役満) 32000 (ron, child)

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

5. **Push/fold decision-making: Three strategies**:

   Push/fold problems should not be presented as a simple "attack/fold" binary choice. There are **three strategic options**:

   **IMPORTANT: Waiting strategy (様子見) is the DEFAULT strategy in most situations. Complete fold and full attack are only for extreme cases.**

   **1. Waiting strategy (様子見) - DEFAULT strategy for most situations**:
   - **Discard relatively safe tiles while keeping hand progression possible**
   - Risk: Low-Medium, Return: Keep option to attack if hand improves
   - **This is NOT the same as complete fold** - you still have the possibility to win
   - **Key characteristic**: Flexibility to change strategy based on next draws
   - **When to use** (most common situations):
     - You have genbutsu or safe tiles available
     - Hand is iishanten with some useful tiles remaining
     - Not in critical ranking situation (e.g., 2nd place with moderate point gap)
     - Opponent riichi but you're not desperately behind
     - Turn 8-12 (mid-game) with hand still having potential
   - **Relatively safe tiles for waiting strategy**:
     - Isolated honor tiles (especially non-yaku honors or single yaku honor tiles)
     - Genbutsu (absolute safe tiles from riichi player's river)
     - Suji of tiles discarded in early turns
     - Terminal tiles (1, 9) when many similar tiles are visible in rivers
   - **Example**: 14 tiles 1m2m1p2p3p4p5p5s6s7s北北北發 (2nd place, 5000 points behind 1st, turn 11, opponent riichi)
     - Discard 發: Genbutsu (absolute safety), isolated tile
     - Hand is iishanten with useful tiles (3m, 3p, 6p) still available
     - Cutting 發 allows many tiles to form jantou for tenpai
     - Next turn: If you draw useful tile (e.g., 3m) → shift to attack; if situation worsens → continue waiting or fold
     - **NOT complete fold** - maintains flexibility while avoiding unnecessary risk
   - **Strategy flow**:
     1. Discard safe tile (genbutsu or relatively safe) this turn
     2. Observe next draw
     3. If hand improves (draw useful tile) → consider shifting to attack
     4. If situation worsens or hand doesn't improve → continue waiting or shift to complete fold
   - **Key point**: Waiting strategy is about **maintaining flexibility**, not giving up completely

   **2. Complete fold (ベタ降り) - ONLY for extreme situations**:
   - Discard only genbutsu (absolute safe tiles) for multiple consecutive turns
   - **Explicitly abandon all winning possibility** for the rest of the hand
   - Risk: 0%, Return: Completely abandon winning possibility
   - **Critical difference from waiting strategy**: You commit to folding for ALL remaining turns, not just one turn
   - **When to use** (rare, extreme situations only):
     - Oorasu (all-last) with critical ranking (e.g., 2nd place, 3rd place would drop you out of top 3)
     - Large point gap that cannot be closed even with big win
     - Hand is 3+ shanten (extremely distant) with no realistic winning possibility
     - You have multiple genbutsu tiles available for remaining turns
     - **AND** preserving current ranking is absolutely critical
   - **Example**: Oorasu, you're in 2nd place with 18000 points, 1st has 35000, 3rd has 17000. Opponent riichi. Your hand is 3-shanten.
     - Complete fold is correct: Cannot catch 1st place, but 3rd place is very close
     - Must preserve 2nd place at all costs → fold completely with genbutsu
   - **Important**: Do NOT use complete fold when:
     - Hand is only iishanten with useful tiles
     - You're in non-critical round (East 2, not oorasu)
     - You don't have enough genbutsu for remaining turns
     - In these cases, use **waiting strategy** instead

   **3. Full attack (全力で攻める) - ONLY when winning is critical**:
   - Discard tiles that progress the hand even if dangerous
   - Risk: High, Return: Maximize winning possibility
   - **When to use** (rare situations):
     - Oorasu and you MUST win to improve ranking (e.g., 4th place needs big win)
     - Very good hand (tenpai or good iishanten) with high-value potential
     - Large point gap that requires winning to close
   - **Example**: Oorasu, you're in 4th place with 15000 points, need mangan to reach 3rd. Your hand is tenpai with mangan potential.
     - Full attack is correct: Only winning can save your ranking
     - Accept the risk of dealing in

   **Default decision tree for push/fold situations**:
   1. **Check if you have genbutsu or safe tiles** → If yes, proceed to step 2
   2. **Check hand distance** → If iishanten or better with useful tiles, proceed to step 3
   3. **Check ranking/point situation** → If not critical (e.g., 2nd place, moderate gap), proceed to step 4
   4. **DEFAULT: Use waiting strategy** → Discard safe tile this turn, keep flexibility for next turn
   5. **Only use complete fold if**: Oorasu + critical ranking + extremely distant hand + multiple genbutsu available
   6. **Only use full attack if**: Must win to improve ranking + good hand

   **In problem solutions**:
   - **Default to waiting strategy** for most push/fold situations
   - Clearly distinguish between "waiting strategy" (maintaining flexibility) and "complete fold" (abandoning winning possibility)
   - When describing waiting strategy, emphasize: "This turn we discard safe tile, but if we draw [useful tile] next turn, we can shift to attack"
   - Only recommend complete fold when the situation is truly extreme
   - Always analyze all three strategies as candidates, but recognize that waiting strategy is most common

## Genbutsu (現物) - Absolute Safe Tiles

**Genbutsu (現物)**: A tile that a riichi declarer has already discarded. Since a player cannot win on a tile they've already discarded, genbutsu is **100% safe (absolute safety)** - it will NEVER deal into that riichi player.

**Key points**:
- **Identifying**: Look at the riichi player's discard pile (河). Any tile visible in their discards is genbutsu.
- **Multiple riichi players**: Tile may be genbutsu against player A but NOT against player B - always check WHICH player's river.
- **Common mistake**: Never say "relatively safe" when it's genbutsu - it's ABSOLUTELY safe (0% risk). There's no such thing as "partial genbutsu".
- **Defense priority**: 1st: Genbutsu (100% safe) → 2nd: Safe honors → 3rd: Suji → 4th: Terminals
- **In analysis**: Always identify genbutsu clearly (e.g., "🀗 is genbutsu (対面の現物) = absolute safety")

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
   - If you state "現在テンパイ" (currently tenpai), the 14-tile hand must actually be tenpai
   - If you state "🀓を引けばテンパイ" (drawing 🀓 makes it tenpai), verify this by calculation
   - **Common error**: Stating shanten of 13-tile hand in problem text, when it should describe 14-tile hand (13 + tsumo)

3. **Recommended hand creation process**:
   - Start with a complete winning hand (14 tiles = 4 mentsu + 1 jantou)
   - Remove tiles according to desired shanten:
     - Tenpai: Remove one waiting tile
     - Iishanten: Break apart one mentsu partially
     - Ryanshanten+: Further deconstruct
   - Calculate actual shanten of the resulting 13-tile hand
   - Describe the hand state accurately in the problem text

4. **Critical: Verify shanten calculation thoroughly**:
   - **MANDATORY PROCESS: Convert Unicode to numeric notation first**:
     - Step 1: Read Unicode tiles using reference table (one by one)
     - Step 2: **Convert to numeric notation** (e.g., 🀔🀕🀖 → `5s6s7s`)
     - Step 3: Analyze structure using numeric notation
     - Step 4: Verify sequence continuity numerically (5-6-7 is continuous)
     - **Why**: Prevents visual misidentification errors (e.g., confusing 567s with "456s")
   - **CRITICAL: Verify tile sequence order when identifying sequences**:
     - 🀔🀕🀖 = `5s6s7s` = **567s sequence** (NOT 456s!)
     - 🀙🀚🀛 = `1p2p3p` = **123p sequence** (NOT 234p!)
     - Always convert to numbers first, then verify sequence
     - **Common error**: Relying on visual Unicode → misidentifying 567s as "456s" → completely wrong analysis
   - **Calculate the actual structure of 5+ consecutive tiles carefully**:
     - Example: 1p2p3p4p5p = 123p (sequence) + 45p (twoside wait)
       - OR: 234p (sequence) + 1p (isolated) + 5p (isolated)
       - OR: 345p (sequence) + 12p (edge wait)
     - Consider all possible interpretations and choose the one with best shape
   - **Calculate shanten from the 14-tile position** (13-tile hand + tsumo tile):
     - The problem asks "what to discard from these 14 tiles"
     - Calculate the shanten of the full 14-tile hand
     - This is what should be stated in the problem description
   - **Then calculate shanten for the base 13-tile hand** (before the tsumo):
     - This helps understand how the tsumo tile affects the hand
   - **Test EVERY useful tile** to see what happens when drawn:
     - Example: If you claim "drawing 4p makes it tenpai", actually add 4p to the hand and verify it becomes 14 tiles with only 1 tile away from winning
     - Check if drawing other tiles also leads to tenpai - if too many tiles lead to quick tenpai, the hand is not appropriate for push/fold problems
   - **For each useful tile, verify the resulting hand state**:
     - Does it become tenpai? (can discard 1 tile to reach 0-shanten)
     - Does it stay iishanten? (still 1-shanten)
     - What tiles can be discarded after the draw?
   - **Use correct terminology**:
     - ❌ Wrong: "北のポン" (pon implies a called set)
     - ✅ Correct: "北の暗刻" (closed triplet in hand)
     - ❌ Wrong: "456sの一盃口" (iipeikou means TWO identical sequences)
     - ✅ Correct: "456sの順子" (just a sequence)
     - Iipeikou example: 234m + 234m (same sequence twice)
   - **Critical: Understand isolated tiles vs useful tiles**:
     - ❌ Wrong: "發 is a useful tile" (when it's isolated and should be discarded)
     - ✅ Correct: "發 is an isolated tile that should be discarded. Cutting 發 allows many tiles to form jantou for tenpai"
   - **Example: Correct shanten calculation and hand evaluation**:
     - 13-tile hand: 🀇🀈🀙🀚🀛🀜🀔🀕🀖🀃🀃🀃🀅 (1m2m1p2p3p4p5s6s7s北北北發) = **ryanshanten (2-shanten)**
     - Tsumo tile: 🀝 (5p)
     - 14-tile hand: 🀇🀈🀙🀚🀛🀜🀝🀔🀕🀖🀃🀃🀃🀅 (1m2m1p2p3p4p5p5s6s7s北北北發) = **iishanten (1-shanten)**
     - Structure: 北北北 (ankou) + 567s (sequence) + 123p (sequence) + 12m (edge wait) + 45p (twoside wait) + 發 (isolated)
     - Useful tiles: 🀉 (3m), 🀛 (3p), 🀞 (6p) = **3 types** (發 is NOT useful, should be discarded)
     - Cutting 發 allows 1m/2m/1p/2p/4p/5p/3p/6p to form jantou → tenpai
     - **Common errors**: (1) Describing 13-tile shanten as "current" state (2) Misidentifying 567s as "456s" (3) Counting 發 as useful tile

5. **Match hand state to problem theme**:
   - **Push/fold problems** require hands far from tenpai: Iishanten with 2-3 useful tile types max, ryanshanten or further, low point potential (1-2 han)
   - **If 4+ tile types lead to quick tenpai, hand is TOO GOOD for push/fold**
   - **Riichi decision problems** require tenpai hands
     - **CRITICAL**: Check for 4-tile sequences (1234, 2345, ..., 6789) which create nobetan wait options
     - If 4-tile sequence exists, the problem becomes a **wait selection** problem, not just riichi yes/no
     - Example: 2m3m4m 1p2p3p4p 6s7s8s 發發發 3p + tsumo 1p
       - This creates choice between: 3p tanki (2 tiles) vs 1p4p nobetan (6 tiles)
       - Primary decision: Which wait? Secondary decision: Riichi or dama?
   - **Hand development problems** can be iishanten or ryanshanten
   - **Wait selection problems** require tenpai or near-tenpai hands with multiple wait options
     - Ideal: Hands with 4-tile sequences that create nobetan vs other wait trade-offs
     - Should have clear difference in tile acceptance (e.g., 6 tiles vs 2 tiles)

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
   - Do NOT trust the problem description blindly - always verify independently
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

   **Two valid approaches for organizing candidates**:

   **Approach A: Strategy-based classification (RECOMMENDED for push/fold problems)**:
   - Organize candidates by the three strategies: Waiting, Complete fold, Full attack
   - Present the BEST strategy first (usually waiting strategy)
   - **Example** (push/fold problem with genbutsu):
     - Candidate 1: Discard 發 - **Waiting strategy (BEST)** - Genbutsu (safe), keeps hand progression possible
     - Candidate 2: Discard 5p - **Complete fold strategy** - Also genbutsu, but cuts off useful tile (only use if extreme situation)
     - Candidate 3: Discard 1p - **Attack strategy (WORST)** - Not genbutsu, high risk, inappropriate for this situation
   - **Why this approach**: Clearly demonstrates the three strategic options and their appropriateness
   - **When to use**: Push/fold problems where demonstrating strategic thinking is important

   **Approach B: Risk-based ordering (GOOD for other problem types)**:
   - **Order candidates from best to worst** (lowest risk to highest risk)
   - Candidate 1 should be the BEST option (recommended choice)
   - Candidate 2 should be the second-best option
   - Candidate 3 should be the worst option among the candidates discussed
   - **Example** (riichi decision problem):
     - Candidate 1: Riichi with 3p discard (best wait) ← BEST
     - Candidate 2: Riichi with 6m discard (worse wait) ← Second-best
     - Candidate 3: Don't riichi (miss opportunity) ← WORST
   - **When to use**: Riichi decision, wait selection, hand development problems

   **General guidelines**:
   - **Clearly label each candidate** with its strategy or risk level
   - **Explain why each candidate is better or worse** than others
   - **Always label the worst candidate** explicitly: "最も危険" or "3つの候補の中で最悪"
   - **Avoid confusing ordering**: Do NOT put the worst option as Candidate 2 and second-worst as Candidate 3

9. **Tenpai wait selection validation** (for tenpai/riichi decision problems):

   **CRITICAL: Always check for multiple wait options when hand is tenpai or near-tenpai**

   When generating solutions for riichi decision or wait selection problems, you MUST:

   a. **Check for 4-tile sequences (四連形)**:
   - **MANDATORY**: Scan the hand for any 4-tile sequences: 1234, 2345, 3456, 4567, 5678, 6789
   - If found, ALWAYS consider **nobetan (延べ単 / 両端待ち)** - waiting for both ends
   - Example: 1234p can wait for 1p (forming 11p + 234p) OR 4p (forming 123p + 44p)
   - **Common mistake**: Missing nobetan and defaulting to tanki (single tile) wait

   b. **List ALL possible wait options**:
   - Do NOT assume the 13-tile tenpai form is fixed
   - With 14 tiles (13 + tsumo), consider ALL possible discards
   - For each discard candidate, determine the resulting wait
   - Example with 14 tiles (2m3m4m 1p2p3p4p 6s7s8s 發發發 3p):
     - Discard 1p → 3p tanki wait (2 tiles remaining)
     - Discard 3p → 1p4p nobetan wait (6 tiles remaining)

   c. **Calculate tile acceptance for each wait**:
   - Count remaining tiles for each wait option
   - Account for tiles already in hand and visible in rivers
   - Example:
     - 3p tanki: 4 total - 2 in hand = 2 remaining tiles
     - 1p4p nobetan: (4-1) + (4-1) = 3+3 = 6 remaining tiles

   d. **Compare wait options explicitly**:
   - State the comparison clearly: "Nobetan (6 tiles) vs Tanki (2 tiles) = 3x winning probability"
   - Recommend the wait with more acceptance unless there are strong compensating factors
   - If choosing worse wait, explain why (e.g., much higher point value, specific tactical reason)

   e. **Common complex wait patterns**:

   **Pattern 1: 4-tile sequences (四連形) - Nobetan**:
   - 1234 → wait 1 or 4 (nobetan)
   - 2345 → wait 2 or 5 (nobetan)
   - 3456 → wait 3 or 6 (nobetan)
   - 5678 → wait 5 or 8 (nobetan)
   - 6789 → wait 6 or 9 (nobetan)

   **Pattern 2: Ankou + consecutive tiles + pair (暗刻+連続牌+対子) - Multiple interpretations**:
   - **CRITICAL**: This pattern is even more complex than nobetan and easily missed
   - Example: **4445688s** (7 tiles) = 3-way wait (4s, 7s, 8s)
     - Interpretation A: **444 (ankou) + 56 (twoside wait for 4-7) + 88 (pair)** → **4s or 7s** wait
       - Draw 4s: 444-456-88 (4 ankou, 456 sequence, 88 jantou)
       - Draw 7s: 444-567-88 (4 ankou, 567 sequence, 88 jantou)
     - Interpretation B: **44 (pair) + 456 (sequence) + 88 (pair)** → **4s or 8s** wait (shanpon)
       - Draw 4s: 444-456-88 (444 ankou, 456 sequence, 88 jantou)
       - Draw 8s: 44-456-888 (44 jantou, 456 sequence, 888 ankou)
     - **Result**: 4s appears in BOTH interpretations, 7s in A only, 8s in B only → **4s, 7s, 8s all win**
   - Other examples: 2223566, 5556788, 1112344
   - **Key characteristic**: Ankou (XXX) followed by consecutive tiles (YZ) and a pair (WW)
   - **Why it's missed**: Multiple valid interpretations of the same tiles create overlapping waits
   - **Detection**: Look for patterns like "XXXYZWW" where XXX=ankou, YZ=consecutive, WW=pair

   f. **Why nobetan is easily missed**:
   - 4-tile sequences look "complete" at first glance
   - Players instinctively parse 1234p as "123p + 4p" (sequence + isolated)
   - The concept of "both ends become jantou" is less intuitive
   - Solution: **Always actively scan for 1234/2345/.../6789 patterns**

   f. **Validation checklist for tenpai problems**:
   - [ ] Did I check for any 4-tile sequences in the hand?
   - [ ] If 4-tile sequence exists, did I consider nobetan wait?
   - [ ] **Did I check for ankou + consecutive tiles + pair patterns (e.g., XXXYZWW)?**
   - [ ] **If ankou pattern exists, did I consider multiple interpretations and overlapping waits?**
   - [ ] Did I list ALL possible wait options (not just the obvious one)?
   - [ ] Did I calculate tile acceptance for each wait option?
   - [ ] Did I compare wait options explicitly (e.g., "X tiles vs Y tiles")?
   - [ ] Did I explain why complex waits might be missed (if applicable)?

   g. **Error prevention**:
   - ❌ **DO NOT**: Assume 13-tile tenpai form is the only option
   - ❌ **DO NOT**: Miss 4-tile sequences (scan systematically)
   - ❌ **DO NOT**: Miss ankou + consecutive + pair patterns (XXXYZWW)
   - ❌ **DO NOT**: Analyze only one interpretation when multiple are possible
   - ❌ **DO NOT**: Recommend worse wait without strong justification
   - ✅ **DO**: Always check for 4-tile sequences first
   - ✅ **DO**: Calculate and compare tile acceptance for all wait options
   - ✅ **DO**: Explain the trade-offs clearly in the solution

10. **Expected value calculation and push/fold analysis** (for push/fold theme problems):

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

   **For final comparison and strategy selection**:
   - **DO use qualitative comparison**:
     - Example: "Winning expectation (extremely low, even if winning only 1000-2000 points) << Deal-in loss (3000-6000 points scale)"
   - **DO NOT fabricate numeric expected values** without clear basis
   - **CRITICAL: Distinguish between "waiting strategy" and "complete fold"**:
     - ❌ Wrong: "This is a complete fold situation, discard genbutsu and abandon winning possibility"
       - (When hand is iishanten with useful tiles, NOT extreme situation)
     - ✅ Correct: "This is a waiting strategy situation. Discard genbutsu (發) this turn to stay safe, but if we draw useful tile (3m) next turn, we can shift to attack. Maintains flexibility."
     - **Default to waiting strategy** unless situation is extreme (oorasu + critical ranking + 3+ shanten)
   - **When recommending waiting strategy**:
     - Explicitly mention: "This is waiting strategy, NOT complete fold"
     - Explain: "We keep the possibility to win if hand improves next turn"
     - Describe next-turn flexibility: "If we draw [useful tile], we can shift to attack"
   - **When recommending complete fold**:
     - Explain why situation is extreme enough to abandon winning completely
     - Verify: Oorasu? Critical ranking? 3+ shanten? Multiple genbutsu for remaining turns?
     - If NOT all conditions met → use waiting strategy instead

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
