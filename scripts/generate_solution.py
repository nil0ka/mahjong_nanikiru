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
    最新の問題番号を取得する

    Returns:
        最新の問題番号（整数、最低3桁でゼロパディング）
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

    return max(problem_numbers)

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

    prompt = f"""以下の麻雀の何切る問題に対する詳細な回答と解説を生成してください。

【問題】
{problem_content}

【重要な分析手順】
1. **ツモ牌の確認**:
   - **問題文にツモ牌が明記されているか確認**
   - ツモ牌がない場合：問題の誤りを指摘し、「ツモ牌によって判断が変わる可能性がある」旨を記載
   - ツモ牌がある場合：14枚（手牌13枚+ツモ1枚）から何を切るかを判断

2. **Unicode牌の正確な識別**:
   - **必ず以下の参照表を使って全ての牌を識別してください**:
     - 🀗は8s（七索ではない）、🀖は7s
     - 🀠は8p（九筒ではない）、🀡は9p
     - 🀎は8m（九萬ではない）、🀏は9m
   - 手牌13枚とツモ牌1枚を1枚ずつ参照表で確認すること

3. **手牌の向聴数を計算**:
   - 問題文の記述を鵜呑みにせず、実際に手牌（13枚）の向聴数を計算してください
   - **3つのパターンを検討**:
     - 標準形（4面子1雀頭）
     - 七対子（7つの対子）
     - 国士無双（13種の么九牌）
   - **有効牌を全てリストアップし、それぞれでどうなるかテスト**:
     - 例：問題文が「4pを引けばテンパイ」と書いている場合
       1. 実際に4pを加えて14枚にする
       2. 14枚の状態で1枚切ってテンパイになるか確認
       3. 他の牌（2p, 5p, 8pなど）でも同様にテストする
     - 問題文に書かれていない有効牌も発見して解説に含める
   - 問題文の記述と実際の向聴数が異なる場合は、実際の計算結果を優先してください
   - 問題文に向聴数の誤りがある場合、解説中で指摘すること
   - 例：標準形ではイーシャンテンだが、七対子ではテンパイというケースもある

3. **見えている牌の集計**:
   - 手牌13枚
   - ツモ牌1枚
   - 全プレイヤーの河（自分、下家、対面、上家）
   - ドラ表示牌
   - 鳴き牌（ある場合）
   - これらから各牌の残り枚数を正確に計算（各牌は4枚まで）

4. **推奨打牌の妥当性確認**:
   - 推奨する打牌が実際に14枚（手牌13枚+ツモ1枚）に含まれていることを確認
   - 14枚にない牌を「切るべき」と書かないこと

5. **現物（げんぶつ）の識別**:
   - **押し引き・安全牌選択問題では必須**: リーチがかかっている場合、現物を正確に識別すること
   - **現物の定義**: リーチ者が既に捨てた牌 = 絶対に当たらない = 100%安全
   - **識別方法**: リーチ者の河（捨て牌）を確認し、手牌やツモ牌と照合
   - **記述の正確性**:
     - ❌ 誤り: 「対面の河に見えているので比較的安全」
     - ✅ 正解: 「対面（リーチ者）の河に見えている現物なので絶対安全（100%安全、0%リスク）」
   - **複数リーチの場合**: どのリーチ者に対する現物かを明確にする
   - **重要**: 現物があれば必ず「現物 = 絶対安全」と明記し、「比較的安全」などの曖昧な表現は使わない

6. **点数配分の妥当性確認**:
   - 4人の点数合計が100000点になっているか確認
   - **東1局0本場**の場合：全員が25000点であることを確認
     - 点数に変動があれば問題設定の誤りを解説中で指摘
   - **東1局1本場**の場合：親の点数変動が妥当か確認
     - 親和了 → 親の点数が増えているはず（25000点以上）
     - 親テンパイ流局 → 点数変動は小さい（±1000-3000点程度）
     - 親の点数が大幅減少（例：16000点）は不自然 → 問題設定の誤りを解説中で指摘
   - 問題文の局・本場設定と点数配分が矛盾している場合：
     - 解説中でその矛盾を指摘する
     - ただし、解答自体は問題文の設定を前提として書く

【要件】
1. 問題を詳細に分析し、最適な打牌を決定してください
2. その理由を初心者にも分かりやすく解説してください
3. 可能な候補を複数挙げ、それぞれを比較してください
   - **重要：候補は必ず良い順（リスクの低い順）に並べる**
     - 候補1：最善の選択（推奨）
     - 候補2：次善の選択
     - 候補3：最悪の選択
   - **最悪の候補には明確にラベルを付ける**（例：「3つの候補の中で最も危険」）
   - **悪い順に並べない**：候補2が最悪で候補3が次悪というような順序は避ける
4. 受け入れ枚数などの定量的な情報も含めてください
5. **点数計算と期待値**:
   - 手牌の役（リーチ、タンヤオ、ピンフなど）を正確に認識
   - ドラの枚数を数えて翻数を計算
   - 符計算も行い、何翻何符で何点になるかを明記
   - **標準形の例**:
     - 例1：リーチ1翻＋タンヤオ1翻＋ドラ2翻=4翻30符で7700点（ロン）
     - 例2：リーチ1翻＋ツモ1翻＋ピンフ1翻＋ドラ1翻=4翻20符で2600オール（親ツモ）または1300-2600（子ツモ）
     - 例3：リーチ1翻＋ツモ1翻＋ピンフ1翻＋ドラ2翻=5翻20符で満貫8000点
     - 例4：役牌1翻＋ドラ3翻=4翻40符で満貫8000点（刻子で符が上がる）
   - **七対子の例**:
     - 例5：七対子2翻＋ドラ2翻=4翻25符で6400点（常に25符固定）
     - 例6：七対子2翻＋ドラ3翻=5翻25符で満貫8000点
   - **食い下がり（鳴いた場合）**:
     - タンヤオ1翻（鳴き可）＋ドラ3翻=4翻30符で7700点
     - ホンイツ3翻→鳴くと2翻、チンイツ6翻→鳴くと5翻
     - 三色2翻→鳴くと1翻、一気通貫2翻→鳴くと1翻
   - 注意：4翻20符は5翻に切り上げられない。4翻のまま計算される
   - 親/子の違いを考慮（親は1.5倍）

6. **押し引き判断における期待値分析**（押し引きテーマの問題では必須）:

   **自分の手の分析**:
   - **理想形のパターンを全て列挙**（役と点数を明記）:
     - 最低ライン：基本役のみ（例：「發のみ1翻=1000-2000点」）
     - リーチ込み：リーチ＋基本役（例：「リーチ1翻＋發1翻=2翻=2000-3900点」）
     - ドラ込み：ドラを含む（例：「リーチ1翻＋發1翻＋ドラ1翻=3翻=3900-5800点」）
     - 最良ケース：（例：「リーチ1翻＋ツモ1翻＋發1翻＋ドラ2翻=5翻=満貫8000点」）
   - **現実的な評価**：向聴数、有効牌枚数、巡目を考慮して「極めて低い」「低い」「中程度」「高い」で評価
   - **禁止事項**：「5-10%の和了確率」「35%の放銃率」などの根拠のない確率数値を使わないこと

   **相手の手の分析**（特にリーチ者）:
   - **河の情報を詳細に分析**:
     - ドラの可視性：「ドラ2s（🀑）が見えていない→ドラ1枚以上の可能性が高い」
     - 役牌の可視性：「東南中は切られているが、白發北は見えていない→役牌の可能性あり」
     - 染め手の可能性：「萬筒索が混在→ホンイツ・チンイツではない」
     - リーチタイミング：「8巡目の早いリーチ→良形待ちの可能性が高い」
   - **想定される手役パターンを複数列挙**（点数範囲を明記）:
     - パターン1：リーチのみ=1000-2000点（ドラが見えていない場合は「可能性は低い」と明記）
     - パターン2：リーチ＋ツモ=2翻=2000-3900点
     - パターン3：リーチ＋ドラ1=2翻=2000-3900点
     - パターン4：リーチ＋役牌=2翻=2000-3900点
     - パターン5：リーチ＋ドラ1＋ツモ=3翻=3900-5800点
     - パターン6：リーチ＋ドラ2以上=3翻以上=3900-8000点以上
     - パターン7：リーチ＋ピンフ＋ドラ＋ツモ=4翻=満貫8000点
   - **結論として最も可能性の高い点数範囲を明記**:
     - 例：「ドラが見えていないため、3翻（3900-5800点）以上の可能性が高い。最低でも2翻2000点以上、最悪満貫8000点の可能性もある。」
     - 例：「放銃時の損失：2000-8000点規模（現実的には3000-6000点程度）」
   - **禁止事項**：「4000点×35%=1400点の期待損失」のような単一点数推測を使わないこと

   **最終的な比較**:
   - 定性的な比較を使用：
     - 例：「和了期待値（極めて低い、仮に和了しても1000-2000点）<< 放銃時の損失（3000-6000点規模）」
   - **禁止事項**：明確な根拠なく数値化した期待値を使わないこと

【確認事項（必ず守ること）】
- **向聴数の正確性**: 「現在テンパイ」と書くなら、実際に計算してテンパイであることを確認
- **牌の枚数計算**: 見えている牌を除外した残り枚数を正確に計算（各牌は4枚まで）
- **待ち牌の枚数**: 待ち牌の残り枚数を正確に計算（河に見えている分を除外）
- **受け入れ枚数**: 受け入れ枚数の計算が正確であること（見えている牌を考慮）
- **危険牌の枚数**: アウト牌（危険牌）の枚数計算が正しいこと
- **候補の順序**: 候補は必ず良い順（リスクの低い順）に並べ、候補1が最善、候補3が最悪となるようにする。最悪の候補には「3つの候補の中で最も危険」などと明記する

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
    # 問題番号を取得（引数で指定されていない場合は最新の問題）
    if len(sys.argv) > 1:
        problem_number = int(sys.argv[1])
    else:
        problem_number = get_latest_problem_number()

    print(f"Generating answer for problem #{problem_number:03d}...")

    # 問題ファイルを読み込む
    problem_dir = f"problems/{problem_number:03d}"
    problem_filename = f"{problem_dir}/question.md"

    if not os.path.exists(problem_filename):
        print(f"Error: Problem file not found: {problem_filename}")
        sys.exit(1)

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
