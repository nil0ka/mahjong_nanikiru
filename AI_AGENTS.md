# AI Agent Guide - Mahjong Nanikiru Problem Generator

This guide explains how to use various AI coding agents (Cline, Cursor, GitHub Copilot, Claude Code) to generate Mahjong "What to discard" (nanikiru) problems and solutions.

## Supported AI Agents

| Agent | Custom Commands | Rules File | Auto-load |
|-------|----------------|------------|-----------|
| **Claude Code** | ✅ `/create-question`, `/create-solution` | `CLAUDE.md` | ✅ |
| **Cline / Roo-Cline** | ❌ (use natural language) | `.clinerules` | ✅ |
| **Cursor** | ❌ (use natural language) | `.cursorrules` | ✅ |
| **GitHub Copilot** | ❌ (use natural language) | `AI_AGENTS.md` (this file) | ⚠️ Manual |

## Quick Start by Agent

### Claude Code (Recommended for this project)

```bash
# Generate new problem
/create-question

# Generate solution for latest problem
/create-solution
```

**Custom commands are already configured in `.claude/commands/`**

### Cline / Roo-Cline

Rules are automatically loaded from `.clinerules`.

**Example prompts:**
- "作問して" → Generates next numbered problem
- "問題005の解答を生成して" → Generates solution for problem 005
- "リーチ判断の問題を作って" → Generates riichi decision problem
- "難易度7の押し引き問題を作って" → Generates difficulty 7 push/fold problem

### Cursor

Rules are automatically loaded from `.cursorrules`.

**Example prompts:**
- "麻雀の何切る問題を生成して" → Generates a nanikiru problem
- "最新の問題の解答を作成して" → Generates solution for latest problem
- "難易度5の待ち選択問題を作って" → Generates difficulty 5 wait selection problem

### GitHub Copilot

Copilot doesn't auto-load project rules. You may need to:
1. Open this file (`AI_AGENTS.md`) in your editor
2. Reference it in your prompt: "Follow the rules in AI_AGENTS.md and generate a problem"
3. Or manually include key rules in your prompt

**Example prompts:**
- "AI_AGENTS.mdのルールに従って麻雀の何切る問題を生成して"
- "scripts/generate_question.pyを実行して新しい問題を作って"

## How to Generate Problems/Solutions

All agents use the same Python scripts:

```bash
# Generate a new problem (auto-numbered)
python scripts/generate_question.py

# Generate a problem with specific number
python scripts/generate_question.py 5

# Generate solution for latest problem
python scripts/generate_solution.py

# Generate solution for specific problem
python scripts/generate_solution.py 5

# List all problems
python scripts/list_problems.py

# Filter by theme
python scripts/list_problems.py --theme "リーチ判断"

# Filter by difficulty
python scripts/list_problems.py --difficulty 5
```

**When using AI agents:**
1. Ask the agent to run the appropriate Python script
2. The agent will execute the script and create the markdown files
3. Review the generated problem/solution
4. If needed, ask the agent to regenerate or fix issues

## Critical Rules for Problem Generation

### 1. Tile Notation Policy (MANDATORY)

**ALL problems and solutions MUST use both Unicode and numeric notation:**

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

**Why:**
- Unicode tiles (🀔🀕🀖) provide visual representation
- Numeric notation (5s6s7s) prevents misidentification
- Combined format ensures accuracy

### 2. Unicode Mahjong Tiles Reference

**Always use this table when reading or writing tiles:**

**萬子 (Manzu)**: 🀇=1m 🀈=2m 🀉=3m 🀊=4m 🀋=5m 🀌=6m 🀍=7m 🀎=8m 🀏=9m

**筒子 (Pinzu)**: 🀙=1p 🀚=2p 🀛=3p 🀜=4p 🀝=5p 🀞=6p 🀟=7p 🀠=8p 🀡=9p

**索子 (Souzu)**: 🀐=1s 🀑=2s 🀒=3s 🀓=4s 🀔=5s 🀕=6s 🀖=7s 🀗=8s 🀘=9s

**字牌 (Honors)**: 🀀=東 🀁=南 🀂=西 🀃=北 🀆=白 🀅=發 🀄=中

### 3. Shanten Calculation (CRITICAL)

**Process:**
1. Read Unicode tiles using reference table (one by one)
2. **Convert to numeric notation** (e.g., 🀔🀕🀖 → `5s6s7s`)
3. Analyze hand structure using numeric notation
4. Verify sequences numerically (5-6-7 is continuous, NOT 4-5-6)

**Calculate shanten for ALL winning patterns:**
- Standard (4 mentsu + 1 jantou)
- Chiitoitsu (七対子) - 7 pairs
- Kokushi musou (国士無双) - 13 orphans
- **Take the minimum shanten**

**Validation:**
- 14-tile hand (13 + tsumo) shanten matches problem description
- Test ALL useful tiles to verify claims (e.g., "drawing 4p makes it tenpai")
- Never trust problem description blindly - always verify independently

### 4. Problem Format

Required elements:

1. **Difficulty**: ★☆☆☆☆☆☆☆☆☆ 1/10 to ★★★★★★★★★★ 10/10
   - 1-2: Very Easy (obvious answer)
   - 3-4: Easy (basic analysis)
   - 5-6: Medium (multiple factors)
   - 7-8: Hard (complex analysis)
   - 9-10: Very Hard (expert-level)

2. **Theme**: リーチ判断, 手牌選択, 押し引き, 待ち選択, 形式テンパイ, 鳴き判断, 安全牌選択

3. **Game state**: Round (東1局, etc.), seat wind, dora indicator, turn number

4. **Hand tiles**: 14 tiles total (13 in hand + 1 tsumo)
   - **MUST specify tsumo tile separately**

5. **Discards (河)**: For all four players

### 5. Scoring and Yaku

**Common yaku:**
- 1 han: Riichi, Tanyao, Pinfu, Yakuhai
- 2 han: Chiitoitsu (always 25 fu), Sanshoku, Toitoi
- 3 han: Honitsu (2 han if open), Junchan (2 han if open)
- 6 han: Chinitsu (5 han if open)

**Point calculation (child ron):**
- 1 han 30 fu: 1000
- 2 han 30 fu: 2000
- 3 han 30 fu: 3900
- 4 han 30 fu: 7700
- 5+ han: 8000+ (Mangan or above)

**Chiitoitsu (always 25 fu):**
- 2 han: 1600
- 3 han: 3200
- 4 han: 6400

### 6. Push/Fold Analysis (押し引き)

**Three strategies (NOT just attack/fold binary):**

1. **Waiting strategy (様子見) - DEFAULT:**
   - Discard relatively safe tiles while keeping hand progression possible
   - Maintains flexibility
   - NOT complete fold - still has winning possibility

2. **Complete fold (ベタ降り) - RARE:**
   - Discard only genbutsu for multiple turns
   - Abandon all winning possibility
   - Only use in extreme situations (Oorasu + critical ranking + 3+ shanten)

3. **Full attack (全力で攻める) - RARE:**
   - Progress hand even if dangerous
   - Only when must win to improve ranking

**Analysis methodology:**
- Analyze YOUR hand: List ideal forms with yaku and point values
- Analyze OPPONENT's hand: Check dora visibility, yakuhai, suit distribution
- Compare risk vs reward: Use qualitative comparison ("extremely low", "low", "moderate", "high")
- Default to waiting strategy for most situations

### 7. Genbutsu (現物) - Absolute Safe Tiles

**Genbutsu**: A tile that riichi declarer already discarded = **100% safe**

- Check riichi player's discard pile (河)
- Never say "relatively safe" when it's genbutsu - it's ABSOLUTELY safe (0% risk)

### 8. Wait Selection (Multiple Waits)

**4-tile sequences (四連形) - Nobetan:**
- 1234 → wait 1 or 4
- 2345 → wait 2 or 5
- 6789 → wait 6 or 9

**Complex 7-tile multi-way waits:**
- Pattern: 3+ identical + consecutive + pair
- Example: 4445688s = 3-way wait (4s, 7s, 8s)

**Always:**
- Check for 4-tile sequences
- Consider nobetan wait
- Calculate tile acceptance for each wait
- Compare waits explicitly

### 9. Point Distribution Validation

**東1局0本場**: All players MUST have exactly 25000 points
- No exceptions - this is the first hand
- DO NOT use for push/fold problems

**東1局1本場**: Only possible if dealer won or dealer tenpai draw
- Dealer's points should have increased

**Always verify:**
- Sum of points = 100000
- Dealer position matches round
- 本場 count matches point distribution

## Solution Generation Checklist

When generating solutions, ALWAYS verify:

1. ✅ **Accurate tile identification** - Use Unicode reference table
2. ✅ **Independent shanten calculation** - Don't trust problem blindly
3. ✅ **Accurate tile counting** - Count visible tiles, calculate remaining
4. ✅ **Identify genbutsu correctly** - Check riichi player's river
5. ✅ **Validate recommended discard** - Tile must be in actual hand
6. ✅ **Point distribution consistency** - Sum = 100000, matches round/honba
7. ✅ **Wait selection** - Check for nobetan and multi-way waits
8. ✅ **Push/fold analysis** - List ideal forms, analyze river, qualitative comparison

## File Structure

```
problems/
  001/
    question.md   # Problem
    solution.md   # Solution
  002/
    question.md
    solution.md
  ...
  1000/          # Supports unlimited digits
    question.md
    solution.md

scripts/
  generate_question.py   # Problem generation
  generate_solution.py   # Solution generation
  list_problems.py       # List all problems

.claude/
  commands/
    create-question.md   # Claude Code custom command
    create-solution.md   # Claude Code custom command

.clinerules              # Rules for Cline/Roo-Cline
.cursorrules             # Rules for Cursor
AI_AGENTS.md            # This file - generic guide
CLAUDE.md               # Detailed rules for Claude Code (70KB+)
```

## Detailed Documentation

For comprehensive documentation (70KB+ detailed rules), see:
- **`CLAUDE.md`**: Full specifications for Claude Code (includes all edge cases, validation rules, etc.)

The `.clinerules`, `.cursorrules`, and this `AI_AGENTS.md` are simplified versions of `CLAUDE.md` for easier consumption by various AI agents.

## Troubleshooting

**Problem: Agent generates incorrect tile notation**
- Remind agent to use Unicode + numeric notation (併記)
- Point to Unicode reference table in this file

**Problem: Shanten calculation is wrong**
- Ask agent to show step-by-step calculation
- Verify using numeric notation (e.g., 567s not 456s)

**Problem: Point distribution doesn't sum to 100000**
- Check for 東1局0本場 (must be 25000 × 4)
- Verify dealer position matches round

**Problem: Missing nobetan wait option**
- Ask agent to check for 4-tile sequences (1234, 2345, etc.)
- Request explicit comparison of all wait options

**Problem: Push/fold analysis too simplistic**
- Remind agent of three strategies (waiting, complete fold, full attack)
- Request river analysis and ideal form listing

## Contributing

When adding new problems:
1. Use Python scripts (not manual markdown creation)
2. Follow tile notation policy (Unicode + numeric)
3. Verify shanten calculation independently
4. Check point distribution validity
5. Test with multiple AI agents if possible

For questions or issues, see README.md or CLAUDE.md.
