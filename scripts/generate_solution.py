#!/usr/bin/env python3
"""
麻雀の何切る問題に対する回答を自動生成するスクリプト
Claude API を使用して既存の問題を分析し、回答と解説を生成します。
"""

import os
import sys
import time
import re
from datetime import datetime
from typing import List, Dict, Tuple
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError

def load_claude_md_sections() -> str:
    """
    CLAUDE.mdから必要なセクションを読み込む

    Returns:
        CLAUDE.mdの関連セクションの内容
    """
    try:
        with open("CLAUDE.md", "r", encoding="utf-8") as f:
            claude_md = f.read()

        # 必要なセクションを抽出
        sections_to_extract = [
            "Unicode Mahjong Tiles Reference",
            "Critical: Shanten Calculation and Problem Accuracy",
            "Scoring and Expected Value Calculations",
            "Genbutsu - Absolute Safe Tiles",
            "Point Distribution Validation",
            "Candidate discard ordering and presentation",
            "Solution Generation: Critical Validation Points",
        ]

        extracted_content = []
        for section in sections_to_extract:
            # セクションの開始と終了を見つける
            start_marker = f"## {section}"
            if start_marker in claude_md:
                start_idx = claude_md.find(start_marker)
                # 次のセクション（##で始まる行）を見つける
                next_section_idx = claude_md.find("\n## ", start_idx + len(start_marker))
                if next_section_idx == -1:
                    section_content = claude_md[start_idx:]
                else:
                    section_content = claude_md[start_idx:next_section_idx]

                extracted_content.append(section_content.strip())

        return "\n\n".join(extracted_content)
    except FileNotFoundError:
        print("Warning: CLAUDE.md not found. Using embedded rules.")
        return ""

# generate_question.py から関数をインポート（同じディレクトリにある前提）
# 実行時のパスを調整
sys.path.insert(0, os.path.dirname(__file__))
try:
    from generate_question import parse_tiles, count_tiles, calculate_shanten
except ImportError:
    # インポートできない場合は関数を再定義（重複を避けるため）
    def parse_tiles(tiles_str: str) -> List[str]:
        """牌の文字列をパースして牌のリストに変換"""
        tile_map = {
            '🀇': '1m', '🀈': '2m', '🀉': '3m', '🀊': '4m', '🀋': '5m',
            '🀌': '6m', '🀍': '7m', '🀎': '8m', '🀏': '9m',
            '🀙': '1p', '🀚': '2p', '🀛': '3p', '🀜': '4p', '🀝': '5p',
            '🀞': '6p', '🀟': '7p', '🀠': '8p', '🀡': '9p',
            '🀐': '1s', '🀑': '2s', '🀒': '3s', '🀓': '4s', '🀔': '5s',
            '🀕': '6s', '🀖': '7s', '🀗': '8s', '🀘': '9s',
            '🀀': '1z', '🀁': '2z', '🀂': '3z', '🀃': '4z',
            '🀆': '5z', '🀅': '6z', '🀄': '7z',
        }
        tiles = []
        for char in tiles_str:
            if char in tile_map:
                tiles.append(tile_map[char])
        return tiles

    def count_tiles(tiles: List[str]) -> Dict[str, int]:
        """牌の枚数をカウント"""
        counts = {}
        for tile in tiles:
            counts[tile] = counts.get(tile, 0) + 1
        return counts

    # calculate_shantenは複雑なので省略（必要に応じて実装）
    def calculate_shanten(tiles: List[str]) -> Tuple[int, str]:
        """向聴数計算（簡易版）"""
        return 0, "standard"  # 仮実装

def validate_solution_content(problem_content: str, solution_content: str) -> Tuple[bool, str]:
    """
    生成された解答の内容を検証

    Args:
        problem_content: 問題のMarkdownテキスト
        solution_content: 解答のMarkdownテキスト

    Returns:
        (検証結果, エラーメッセージ)
    """
    # 問題から手牌を抽出
    hand_match = re.search(r'## あなたの手牌[（(]13枚[)）]?\s*```\s*([🀀-🀡]+)\s*```', problem_content)
    if not hand_match:
        return True, ""  # 手牌が見つからない場合はスキップ

    hand_str = hand_match.group(1)
    hand_tiles = parse_tiles(hand_str)

    if len(hand_tiles) != 13:
        return True, ""  # 手牌が13枚でない場合はスキップ

    # 問題からツモ牌を抽出
    tsumo_match = re.search(r'## ツモ牌\s*```\s*([🀀-🀡]+)\s*```', problem_content)
    tsumo_tiles = []
    if tsumo_match:
        tsumo_str = tsumo_match.group(1)
        tsumo_tiles = parse_tiles(tsumo_str)

    # 14枚（手牌13枚+ツモ1枚）の全体を作成
    all_14_tiles = hand_tiles + tsumo_tiles

    # 解答から推奨打牌を抽出
    discard_patterns = [
        r'\*\*切るべき牌\*\*:\s*([🀀-🀡])',
        r'([🀀-🀡])を切',
        r'打([🀀-🀡])',
    ]

    recommended_discard = None
    for pattern in discard_patterns:
        discard_match = re.search(pattern, solution_content)
        if discard_match:
            recommended_discard = parse_tiles(discard_match.group(1))
            if recommended_discard:
                recommended_discard = recommended_discard[0]
                break

    # 推奨打牌が14枚（手牌+ツモ）に含まれているか確認
    if recommended_discard and recommended_discard not in all_14_tiles:
        return False, f"推奨打牌 {recommended_discard} が手牌（13枚）またはツモ牌に含まれていません"

    # 解答で述べている向聴数が正しいか確認（簡易版）
    solution_lower = solution_content.lower()
    if 'テンパイ' in solution_content or 'tenpai' in solution_lower:
        try:
            shanten, pattern = calculate_shanten(hand_tiles)
            if shanten != 0:
                shanten_names = {-1: "和了", 0: "テンパイ", 1: "イーシャンテン", 2: "リャンシャンテン"}
                pattern_names = {"standard": "標準形", "chiitoitsu": "七対子", "kokushi": "国士無双"}
                actual = shanten_names.get(shanten, f"{shanten}シャンテン")
                pattern_str = pattern_names.get(pattern, pattern)
                return False, f"解答に「テンパイ」と記載がありますが、実際は{actual}です（{pattern_str}）"
        except:
            pass  # 向聴数計算に失敗した場合はスキップ

    # 点数配分の妥当性チェック（問題文から）
    point_pattern = r'(\d+)点'
    point_matches = re.findall(point_pattern, problem_content)
    if len(point_matches) >= 4:
        try:
            points = [int(p) for p in point_matches[:4]]
            total_points = sum(points)

            # 合計点数チェック
            if total_points != 100000:
                # 警告レベル（エラーとはしない）
                print(f"Warning: 点数の合計が100000点ではありません（{total_points}点）")

            # 場を抽出
            round_match = re.search(r'場:\s*(東|南)(\d+)局(\d+)本場', problem_content)
            if round_match:
                wind = round_match.group(1)
                round_num = int(round_match.group(2))
                honba = int(round_match.group(3))

                # 東1局0本場チェック
                if wind == '東' and round_num == 1 and honba == 0:
                    if not all(p == 25000 for p in points):
                        print(f"Warning: 東1局0本場では全員25000点であるべきです（実際: {points}）")

                # 東1局1本場チェック
                if wind == '東' and round_num == 1 and honba == 1:
                    if min(points) < 18000:
                        print(f"Warning: 東1局1本場で点数が大幅に減少しているプレイヤーがいます（{min(points)}点）")
        except (ValueError, IndexError):
            pass  # 点数の抽出に失敗した場合はスキップ

    return True, ""

def get_latest_problem_number() -> int:
    """
    solution が存在しない最初の問題番号を取得する
    （全ての問題に solution がある場合はエラーを出力して終了）

    Returns:
        solution が存在しない最初の問題番号（整数）
    """
    if not os.path.exists("problems"):
        print("Error: No problems directory found")
        sys.exit(1)

    # 既存のディレクトリを取得
    existing_dirs = [d for d in os.listdir("problems") if os.path.isdir(os.path.join("problems", d))]

    # 数字のみのディレクトリをフィルタリング
    problem_numbers = []
    for d in existing_dirs:
        try:
            problem_numbers.append(int(d))
        except ValueError:
            continue

    if not problem_numbers:
        print("Error: No problem directories found")
        sys.exit(1)

    # 問題番号を昇順にソート
    problem_numbers.sort()

    # solution が存在しない最初の問題を探す
    for num in problem_numbers:
        problem_dir = f"problems/{num:03d}"
        question_file = f"{problem_dir}/question.md"
        solution_file = f"{problem_dir}/solution.md"

        # question が存在し、solution が存在しない問題を見つける
        if os.path.exists(question_file) and not os.path.exists(solution_file):
            return num

    # 全ての問題に solution が存在する場合
    print("Error: All problems already have solutions. Please create a new question first.")
    print(f"Total problems: {len(problem_numbers)}")
    print(f"All have solutions: problems/001/solution.md through problems/{max(problem_numbers):03d}/solution.md")
    sys.exit(1)

def generate_solution(problem_content: str, max_retries: int = 3) -> str:
    """
    指定された問題に対する回答を生成する

    Args:
        problem_content: 問題の Markdown テキスト
        max_retries: 最大リトライ回数

    Returns:
        生成された回答の Markdown テキスト
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set your API key: export ANTHROPIC_API_KEY=your_api_key_here")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    # 今日の日付を取得
    date_str = datetime.now().strftime("%Y-%m-%d")

    # CLAUDE.mdから必要なルールセクションを読み込む
    claude_md_rules = load_claude_md_sections()

    prompt = f"""以下の麻雀の何切る問題に対する詳細な回答と解説を生成してください。

【問題】
{problem_content}

【重要なルール】
以下のルールに厳密に従ってください。これらはプロジェクトの公式ガイドライン（CLAUDE.md）から抽出されたものです。

{claude_md_rules}

【回答生成の要件】
1. 問題を詳細に分析し、最適な打牌を決定してください
2. その理由を初心者にも分かりやすく解説してください
3. **候補の整理**:
   - 押し引き問題: 戦略別分類を使用（様子見、完全降り、全力攻め）
   - その他の問題: リスク順に並べる（候補1=最善、候補2=次善、候補3=最悪）
   - **CRITICAL**: 様子見と完全降りを明確に区別すること
     - 様子見: 安全牌を切りつつ、次巡で手が進めば攻めに転じる柔軟性を保つ（デフォルト戦略）
     - 完全降り: 以降全ての巡で現物のみ切り、和了を完全放棄（極端な状況でのみ）
4. 受け入れ枚数などの定量的な情報も含めてください
5. 上記のCLAUDE.mdルールに厳密に従うこと（特に向聴数計算、現物識別、点数計算、押し引き分析）

【分析手順のチェックリスト】
- ✅ ツモ牌が問題文に明記されているか確認
- ✅ Unicode牌の識別（CLAUDE.md参照表を使用）
- ✅ 手牌の向聴数を計算（標準形・七対子・国士無双の3パターン）
- ✅ **テンパイ・リーチ判断問題の場合：複雑な待ちパターンの存在チェック**

  **パターン1: 4連形（1234, 2345, ..., 6789）のチェック**:
  - 4連形がある場合、ノベタン（延べ単・両端待ち）の可能性を必ず検討
  - 例: 1234p → 1p待ち（11p+234p）または4p待ち（123p+44p）

  **パターン2: 複雑な7枚形多面待ちのチェック**:
  - **CRITICAL**: ノベタンより更に複雑で見落としやすい
  - **一般パターン**: 7枚の中に「同じ牌3枚以上 + 連続する数牌 + 対子」

  **タイプA: XXXYZWW** (暗刻 + 連続2枚 + 対子):
  - 例: **4445688s** → **478s の3種待ち**
    - 解釈A: 444（暗刻）+ 56（47両面）+ 88（雀頭）→ 4sまたは7s待ち
    - 解釈B: 44（対子）+ 456（順子）+ 88（対子）→ 4sまたは8sシャボ待ち
    - 結果: 4s（両方）、7s（Aのみ）、8s（Bのみ）→ **4s, 7s, 8s全て当たり牌**
  - 他の例: 2223566, 5556788, 6667899

  **タイプB: AAABCXX** (暗刻 + 連続2枚 + 対子):
  - 例: **1112344s** → 多面待ち
  - 他の例: 3334566, 7778900

  **タイプC: ABCCCXX** (連続 + 暗刻 + 対子):
  - 例: **1233344s** → 多面待ち
  - 他の例: 3455566, 5677788

  **検出方法**:
  - 7枚グループで「3枚以上の同牌 + 連続数 + 対子」を探す
  - 全ての解釈（暗刻・順子・対子の組み合わせ）をテスト
  - 全解釈から重複する待ち牌を特定
  - **重要**: 3面待ち、4面待ち、5面待ち以上の可能性あり

  **共通手順**:
  - **全ての待ち選択肢をリストアップ**（13枚のテンパイ形に固執しない）
  - 各待ちの受け入れ枚数を計算し、明示的に比較（「X枚 vs Y枚 = Z倍」）
  - 複数解釈がある場合、全ての解釈を列挙し、重複する待ち牌を特定

- ✅ 見えている牌を集計し、残り枚数を計算
- ✅ 推奨打牌が14枚（手牌13枚+ツモ1枚）に含まれているか確認
- ✅ 現物の識別（押し引き・安全牌選択問題では必須）
- ✅ 点数配分の妥当性確認

以下のMarkdown形式で出力してください。他の説明は不要です。

# 何切る問題の回答 - {date_str}

## 問題の再掲
[元の問題から手牌と状況を引用]

## 正解
**切るべき牌**: [牌]

## 解説

### 手牌の分析
- 現在の形: [テンパイ/1シャンテン/2シャンテンなど]
- 有効牌: [何を引けば良い形になるか]

### 各候補の検討

#### [候補1]を切った場合
- メリット: [...]
- デメリット: [...]
- 受け入れ枚数: X枚

#### [候補2]を切った場合
- メリット: [...]
- デメリット: [...]
- 受け入れ枚数: Y枚

### 結論
[なぜこの牌を切るべきかの総括]

## 別解・補足
[状況によっては他の選択肢もありうる場合の説明]

## 学習ポイント
- [この問題から学べる麻雀の考え方や技術]"""

    # リトライロジック
    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text

        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limit error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error: Rate limit exceeded after {max_retries} attempts.")
                raise

        except APIConnectionError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Connection error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error: Connection failed after {max_retries} attempts.")
                raise

        except APIError as e:
            print(f"Error: API error occurred: {e}")
            raise

        except Exception as e:
            print(f"Error: Unexpected error occurred: {e}")
            raise

def main():
    # 問題番号を取得（引数で指定されていない場合は solution が存在しない最初の問題）
    if len(sys.argv) > 1:
        problem_number = int(sys.argv[1])
    else:
        problem_number = get_latest_problem_number()

    # 問題ファイルを読み込む
    problem_dir = f"problems/{problem_number:03d}"
    problem_filename = f"{problem_dir}/question.md"
    solution_filename = f"{problem_dir}/solution.md"

    if not os.path.exists(problem_filename):
        print(f"Error: Problem file not found: {problem_filename}")
        sys.exit(1)

    # 既に solution が存在する場合は警告を表示
    if os.path.exists(solution_filename):
        if len(sys.argv) > 1:
            # 引数で明示的に指定された場合は上書きを許可（警告付き）
            print(f"Warning: Solution already exists at {solution_filename}")
            print("Overwriting existing solution...")
        else:
            # 自動検索の場合はここには到達しないはず（念のためのチェック）
            print(f"Error: Solution already exists at {solution_filename}")
            print("This should not happen. Please report this as a bug.")
            sys.exit(1)

    print(f"Generating solution for problem #{problem_number:03d}...")

    with open(problem_filename, "r", encoding="utf-8") as f:
        problem_content = f.read()

    # 回答を生成（検証が成功するまでリトライ）
    max_validation_attempts = 3
    for attempt in range(max_validation_attempts):
        answer_content = generate_solution(problem_content)

        # 解答の内容を検証
        is_valid, error_message = validate_solution_content(problem_content, answer_content)

        if is_valid:
            print("✓ Validation passed")
            break
        else:
            print(f"✗ Validation failed (attempt {attempt + 1}/{max_validation_attempts}): {error_message}")
            if attempt == max_validation_attempts - 1:
                print("Warning: Using last generated content despite validation failures")
                # 最終的には保存するが、警告を表示

    # ファイルに保存
    answer_filename = f"{problem_dir}/solution.md"
    with open(answer_filename, "w", encoding="utf-8") as f:
        f.write(answer_content)

    print(f"Answer saved to {answer_filename}")
    return answer_filename

if __name__ == "__main__":
    main()
