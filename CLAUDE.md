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
- **Hand tiles**: Exactly 13 tiles
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

## Critical: Shanten Calculation and Problem Accuracy

**The most important aspect of problem generation is correctly understanding and representing the hand state**:

1. **Calculate shanten accurately**:
   - Determine if the hand is tenpai (0-shanten), iishanten (1-shanten), ryanshanten (2-shanten), etc.
   - Any shanten level is valid for problems - not just tenpai or iishanten
   - Example valid problems: "How to proceed from ryanshanten?", "Which tile to discard in this iishanten position?"

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

4. **Validation checks** (automated in `scripts/generate_question.py`):
   - Hand tile count = exactly 13
   - Each tile type ≤ 4 (across hand + all rivers + dora indicator)
   - River counts match turn number (allowing ±2 for calls)
   - **Shanten calculation matches problem description**
   - **Tile addition claims are verified** (e.g., "drawing X gives tenpai")

## Solution Generation: Critical Validation Points

**When generating solutions, always verify these points**:

1. **Accurate tile identification**:
   - Use the Unicode tile reference table above to correctly identify tiles
   - Do NOT confuse similar-looking tiles (🀠 8p vs 🀡 9p, 🀎 8m vs 🀏 9m)
   - Verify you're reading the 13-tile hand correctly from the problem

2. **Independent shanten calculation**:
   - Do NOT trust the problem description blindly (Problem 001 had errors!)
   - Calculate the actual shanten of the 13-tile hand yourself
   - If the problem says "tenpai" but it's actually iishanten, use the correct calculation
   - Describe the actual state in your solution

3. **Accurate tile counting**:
   - Count visible tiles: hand (13) + all rivers + dora indicator + any calls
   - Calculate remaining tiles for each type (max 4 of each)
   - When stating "X tiles remaining" or "waiting on Y tiles", verify the count
   - Example: If 🀇 appears 2 times in hand + 1 in rivers = 3 visible, then 1 remaining

4. **Validate recommended discard**:
   - The tile you recommend discarding MUST be in the actual 13-tile hand
   - Do NOT recommend discarding a tile that doesn't exist in the hand

5. **Validation checks** (automated in `scripts/generate_solution.py`):
   - Recommended discard is in the hand
   - Shanten claims match actual calculation
   - Tile counts are accurate

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
