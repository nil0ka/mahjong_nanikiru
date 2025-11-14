#!/usr/bin/env python3
"""
麻雀の何切る問題を自動生成するスクリプト
Claude API を使用して問題を生成し、Markdown ファイルとして保存します。
"""

import os
import sys
import time
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError

def get_next_problem_number() -> int:
    """
    次に使用する問題番号を取得する

    Returns:
        次の問題番号（整数、最低3桁でゼロパディング）
    """
    if not os.path.exists("problems"):
        return 1

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
        return 1

    return max(problem_numbers) + 1

def parse_tiles(tiles_str: str) -> List[str]:
    """
    牌の文字列をパースして牌のリストに変換

    Args:
        tiles_str: Unicode麻雀牌の文字列

    Returns:
        牌のリスト
    """
    # Unicode麻雀牌のマッピング（🀇-🀏 萬子、🀙-🀡 筒子、🀐-🀘 索子、🀀-🀆 字牌）
    tile_map = {
        # 萬子 (Characters)
        '🀇': '1m', '🀈': '2m', '🀉': '3m', '🀊': '4m', '🀋': '5m',
        '🀌': '6m', '🀍': '7m', '🀎': '8m', '🀏': '9m',
        # 筒子 (Dots)
        '🀙': '1p', '🀚': '2p', '🀛': '3p', '🀜': '4p', '🀝': '5p',
        '🀞': '6p', '🀟': '7p', '🀠': '8p', '🀡': '9p',
        # 索子 (Bamboo)
        '🀐': '1s', '🀑': '2s', '🀒': '3s', '🀓': '4s', '🀔': '5s',
        '🀕': '6s', '🀖': '7s', '🀗': '8s', '🀘': '9s',
        # 字牌 (Honors)
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

def extract_mentsu(tiles: List[str], counts: Dict[str, int]) -> List[List[str]]:
    """
    面子（3枚1組）を抽出する
    順子（123など）と刻子（111など）を検出

    Args:
        tiles: 牌のリスト（ソート済み）
        counts: 各牌の枚数

    Returns:
        可能な面子のリスト
    """
    if not tiles:
        return [[]]

    # 牌をソート
    sorted_tiles = sorted(set(tiles))

    # 最初の牌を取得
    first_tile = sorted_tiles[0]

    results = []

    # 刻子を試す（同じ牌が3枚以上ある場合）
    if counts[first_tile] >= 3:
        new_counts = counts.copy()
        new_counts[first_tile] -= 3
        new_tiles = [t for t in tiles if t != first_tile or new_counts[first_tile] > 0]

        for rest in extract_mentsu(new_tiles, new_counts):
            results.append([[first_tile, first_tile, first_tile]] + rest)

    # 順子を試す（数牌の場合のみ）
    if first_tile[-1] in 'mps':  # 萬子、筒子、索子
        num = int(first_tile[0])
        suit = first_tile[1]

        if num <= 7:  # 7以下なら順子の可能性あり
            second_tile = f"{num+1}{suit}"
            third_tile = f"{num+2}{suit}"

            if second_tile in counts and third_tile in counts:
                if counts[second_tile] >= 1 and counts[third_tile] >= 1:
                    new_counts = counts.copy()
                    new_counts[first_tile] -= 1
                    new_counts[second_tile] -= 1
                    new_counts[third_tile] -= 1

                    new_tiles = []
                    for t in tiles:
                        if t == first_tile and new_counts[first_tile] >= 0:
                            new_counts[first_tile] += 1
                            continue
                        elif t == second_tile and new_counts[second_tile] >= 0:
                            new_counts[second_tile] += 1
                            continue
                        elif t == third_tile and new_counts[third_tile] >= 0:
                            new_counts[third_tile] += 1
                            continue
                        new_tiles.append(t)

                    new_counts[first_tile] -= 1
                    new_counts[second_tile] -= 1
                    new_counts[third_tile] -= 1

                    for rest in extract_mentsu(new_tiles, new_counts):
                        results.append([[first_tile, second_tile, third_tile]] + rest)

    # この牌を使わない（雀頭として残す）
    new_counts = counts.copy()
    new_counts[first_tile] -= 1
    new_tiles = [t for t in tiles if t != first_tile or new_counts[first_tile] >= 0]

    for rest in extract_mentsu(new_tiles, new_counts):
        results.append(rest)

    return results

def can_form_mentsu(tiles: List[str]) -> bool:
    """
    12枚の牌が4面子を構成できるかチェック

    Args:
        tiles: 12枚の牌リスト

    Returns:
        True: 4面子を構成可能、False: 不可能
    """
    if len(tiles) != 12:
        return False

    counts = count_tiles(tiles)

    def recursive_check(remaining_counts, mentsu_count):
        if mentsu_count == 4:
            return all(c == 0 for c in remaining_counts.values())

        # 最初の牌を見つける
        for tile in sorted(remaining_counts.keys()):
            if remaining_counts[tile] > 0:
                # 刻子を試す
                if remaining_counts[tile] >= 3:
                    new_counts = remaining_counts.copy()
                    new_counts[tile] -= 3
                    if recursive_check(new_counts, mentsu_count + 1):
                        return True

                # 順子を試す（数牌の場合のみ）
                if tile[-1] in 'mps':
                    num = int(tile[0])
                    suit = tile[1]
                    if num <= 7:
                        tile2 = f"{num+1}{suit}"
                        tile3 = f"{num+2}{suit}"
                        if tile2 in remaining_counts and tile3 in remaining_counts:
                            if remaining_counts[tile2] > 0 and remaining_counts[tile3] > 0:
                                new_counts = remaining_counts.copy()
                                new_counts[tile] -= 1
                                new_counts[tile2] -= 1
                                new_counts[tile3] -= 1
                                if recursive_check(new_counts, mentsu_count + 1):
                                    return True

                # この牌では面子が作れない
                return False

        return False

    return recursive_check(counts, 0)

def is_valid_complete_hand(tiles: List[str]) -> bool:
    """
    14枚の手牌が4面子1雀頭の完成形かチェック

    Args:
        tiles: 14枚の牌リスト

    Returns:
        True: 完成形、False: 完成形でない
    """
    if len(tiles) != 14:
        return False

    counts = count_tiles(tiles)

    # すべての可能な雀頭候補を試す
    for jantou_tile in set(tiles):
        if counts[jantou_tile] >= 2:
            # 雀頭を取り除く
            remaining_tiles = tiles.copy()
            remaining_tiles.remove(jantou_tile)
            remaining_tiles.remove(jantou_tile)

            # 残り12枚が4面子になるかチェック
            if can_form_mentsu(remaining_tiles):
                return True

    return False

def calculate_shanten(tiles: List[str]) -> int:
    """
    手牌の向聴数を計算

    Args:
        tiles: 手牌（13枚または14枚）

    Returns:
        向聴数（-1: 和了、0: テンパイ、1: イーシャンテン、...）
    """
    if len(tiles) == 14:
        # 14枚の場合は和了形かチェック
        return -1 if is_valid_complete_hand(tiles) else 0

    if len(tiles) != 13:
        return 99  # 異常値

    # 13枚の場合、すべての牌を加えてテンパイになるかチェック
    all_tiles = [
        '1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
        '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
        '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
        '1z', '2z', '3z', '4z', '5z', '6z', '7z',
    ]

    tenpai_tiles = []
    for tile in all_tiles:
        test_tiles = tiles + [tile]
        if is_valid_complete_hand(test_tiles):
            tenpai_tiles.append(tile)

    if tenpai_tiles:
        return 0  # テンパイ

    # イーシャンテン以上の判定（簡易版）
    # 各牌を加えてテンパイに近づくかチェック
    min_shanten = 99
    for tile in all_tiles:
        test_tiles_13 = tiles + [tile]
        # この14枚から1枚切ってテンパイになるかチェック
        for discard in set(test_tiles_13):
            remaining = test_tiles_13.copy()
            remaining.remove(discard)
            shanten = calculate_shanten(remaining)
            if shanten == 0:
                min_shanten = min(min_shanten, 1)
                break

    if min_shanten == 1:
        return 1  # イーシャンテン

    # さらに遠い向聴数の計算は複雑なので簡略化
    return 2  # リャンシャンテン以上

def validate_problem_content(content: str) -> Tuple[bool, str]:
    """
    生成された問題の内容を検証

    Args:
        content: 生成された問題のMarkdownテキスト

    Returns:
        (検証結果, エラーメッセージ)
    """
    # 手牌を抽出
    hand_match = re.search(r'## あなたの手牌\s*```\s*([🀀-🀡]+)\s*```', content)
    if not hand_match:
        return False, "手牌が見つかりません"

    hand_str = hand_match.group(1)
    hand_tiles = parse_tiles(hand_str)

    if len(hand_tiles) != 13:
        return False, f"手牌が13枚ではありません（{len(hand_tiles)}枚）"

    # 向聴数を計算
    shanten = calculate_shanten(hand_tiles)
    shanten_names = {-1: "和了", 0: "テンパイ", 1: "イーシャンテン", 2: "リャンシャンテン"}

    # 問題文から向聴数の記述を探す
    content_lower = content.lower()
    if 'テンパイ' in content or 'tenpai' in content_lower:
        if shanten != 0:
            actual = shanten_names.get(shanten, f"{shanten}シャンテン")
            return False, f"問題文に「テンパイ」と記載がありますが、実際は{actual}です"

    if 'イーシャンテン' in content or '1シャンテン' in content:
        if shanten != 1:
            actual = shanten_names.get(shanten, f"{shanten}シャンテン")
            return False, f"問題文に「イーシャンテン」と記載がありますが、実際は{actual}です"

    # 「○○を引けば××」のような記述を検証
    # 例：「🀓を引けばテンパイ」
    tile_addition_pattern = r'([🀀-🀡])を?[引ツモ].*?([テンパイイーシャンテン和了]+)'
    matches = re.finditer(tile_addition_pattern, content)

    for match in matches:
        tile_unicode = match.group(1)
        expected_state = match.group(2)

        tile_to_add = parse_tiles(tile_unicode)
        if not tile_to_add:
            continue

        test_tiles = hand_tiles + tile_to_add
        test_shanten = calculate_shanten(test_tiles)

        expected_shanten = None
        if 'テンパイ' in expected_state:
            expected_shanten = 0
        elif 'イーシャンテン' in expected_state:
            expected_shanten = 1
        elif '和了' in expected_state:
            expected_shanten = -1

        if expected_shanten is not None and test_shanten != expected_shanten:
            actual = shanten_names.get(test_shanten, f"{test_shanten}シャンテン")
            expected = shanten_names.get(expected_shanten, f"{expected_shanten}シャンテン")
            return False, f"{tile_unicode}を引いても{expected}になりません（実際は{actual}）"

    # 河を抽出
    rivers = {}
    for player in ['自分', '下家', '対面', '上家']:
        river_match = re.search(rf'\*\*{player}\*\*:\s*([🀀-🀡]+)', content)
        if river_match:
            rivers[player] = parse_tiles(river_match.group(1))
        else:
            rivers[player] = []

    # ドラ表示牌を抽出
    dora_match = re.search(r'ドラ表示牌:\s*([🀀-🀡])', content)
    dora_tiles = parse_tiles(dora_match.group(1)) if dora_match else []

    # すべての牌を集計
    all_tiles = hand_tiles.copy()
    for river in rivers.values():
        all_tiles.extend(river)
    all_tiles.extend(dora_tiles)

    # 各牌が4枚を超えていないかチェック
    tile_counts = count_tiles(all_tiles)
    for tile, count in tile_counts.items():
        if count > 4:
            return False, f"牌 {tile} が{count}枚使用されています（最大4枚）"

    # 巡目を抽出
    turn_match = re.search(r'巡目:\s*(\d+)巡目', content)
    if turn_match:
        turn = int(turn_match.group(1))
        # 河の枚数チェック（簡易版：鳴きを考慮しない）
        for player, river in rivers.items():
            expected_count = turn - 1
            # ±2枚程度の誤差は許容（鳴きや特殊な状況を考慮）
            if abs(len(river) - expected_count) > 2:
                return False, f"{player}の河の枚数が巡目と整合していません（{turn}巡目で{len(river)}枚）"

    return True, ""

def generate_question(date_str: str, max_retries: int = 3) -> str:
    """
    麻雀問題を生成する

    Args:
        date_str: YYYY-MM-DD 形式の日付文字列
        max_retries: 最大リトライ回数

    Returns:
        生成された問題の Markdown テキスト
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set your API key: export ANTHROPIC_API_KEY=your_api_key_here")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    prompt = f"""麻雀の何切る問題を1つ生成してください。

要件:
1. 難易度: 1〜10のランダムな数値を選択（1=最も簡単、10=最も難しい）
2. テーマ: 問題のテーマを選択（例：リーチ判断、手役選択、押し引き、待ち選択、形式テンパイ、鳴き判断、安全牌選択など）
3. 局面情報（場、自風、ドラ表示牌、巡目）を設定
4. 河（捨て牌）の情報を含める（自分、下家、対面、上家それぞれ2〜5枚程度）
5. Unicode麻雀牌（🀇-🀏 萬子、🀙-🀡 筒子、🀐-🀘 索子、🀀-🀆 字牌）を使用

**重要：手牌の作成手順**（この手順を必ず守ること）:
1. まず完成形（14枚＝4面子1雀頭）を作成する
   - 例：🀈🀉🀊🀛🀜🀝🀔🀕🀖🀕🀕🀖🀗🀘（234m, 345p, 456s, 66s, 789s）
2. 完成形が正しいか検証：4面子1雀頭が成立するか確認
3. 問題のテーマに応じて1枚抜いて13枚にする
   - テンパイ問題なら：待ち牌を1枚抜く（例：🀖を抜いて🀖待ちのテンパイ）
   - イーシャンテン問題なら：面子の一部を崩す
4. 最終確認：作成した13枚の手牌が問題として成立するか確認

確認事項（必ず守ること）:
- **手牌の妥当性**: 上記の手順で作成し、完成形から逆算して構成すること
- **牌の枚数制限**: 各牌は4枚までしか存在しない。手牌+全プレイヤーの河+ドラ表示牌+鳴き牌で同じ牌が5枚以上にならないこと
- **河の枚数**: 鳴きなしの場合、各プレイヤーの河の枚数は（巡目 - 1）枚が基本。例：11巡目なら各プレイヤーの河は基本10枚

以下のMarkdown形式で出力してください。他の説明は不要です。

# 何切る問題 - {date_str}

**難易度**: ★★★★★☆☆☆☆☆ (5/10)
**テーマ**: リーチ判断

## 局面情報
- 場: [東1局/南2局など]
- 自風: [東/南/西/北]
- ドラ表示牌: [牌]
- 巡目: [X巡目]

## あなたの手牌
```
[13枚の牌をUnicodeで]
```

## 河（捨て牌）
**自分**: [2〜5枚の牌]
**下家**: [2〜5枚の牌]
**対面**: [2〜5枚の牌]
**上家**: [2〜5枚の牌]

## 状況
[必要に応じて追加の状況説明]

## 問題
この局面で何を切りますか？"""

    # リトライロジック
    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
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
    # 問題番号を取得（引数で指定されていない場合は自動採番）
    if len(sys.argv) > 1:
        problem_number = int(sys.argv[1])
    else:
        problem_number = get_next_problem_number()

    # 今日の日付を取得
    date_str = datetime.now().strftime("%Y-%m-%d")

    print(f"Generating problem #{problem_number:03d}...")

    # 問題を生成（検証が成功するまでリトライ）
    max_validation_attempts = 5
    for attempt in range(max_validation_attempts):
        problem_content = generate_question(date_str)

        # 問題の内容を検証
        is_valid, error_message = validate_problem_content(problem_content)

        if is_valid:
            print("✓ Validation passed")
            break
        else:
            print(f"✗ Validation failed (attempt {attempt + 1}/{max_validation_attempts}): {error_message}")
            if attempt == max_validation_attempts - 1:
                print("Warning: Using last generated content despite validation failures")
                # 最終的には保存するが、警告を表示

    # ディレクトリを作成
    problem_dir = f"problems/{problem_number:03d}"
    os.makedirs(problem_dir, exist_ok=True)

    # ファイルに保存
    filename = f"{problem_dir}/question.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(problem_content)

    print(f"Problem saved to {filename}")
    return filename

if __name__ == "__main__":
    main()
