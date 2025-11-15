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
            "Genbutsu - Absolute Safe Tiles",
            "Point Distribution Validation",
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

def calculate_chiitoitsu_shanten(tiles: List[str]) -> int:
    """
    七対子の向聴数を計算

    Args:
        tiles: 手牌（13枚）

    Returns:
        向聴数（-1: 和了、0: テンパイ、1: イーシャンテン、...）
    """
    if len(tiles) != 13:
        return 99

    counts = count_tiles(tiles)
    pairs = 0  # 対子の数
    unique_tiles = len(counts)  # 異なる牌の種類数

    for tile, count in counts.items():
        if count >= 2:
            pairs += 1

    # 七対子は7種類の対子が必要
    # 向聴数 = 6 - pairs（ただし、同じ牌が3枚以上あると不利）
    if unique_tiles > 7:
        # 8種類以上の牌がある場合、最低でも1シャンテン
        return 6 - pairs
    else:
        return 6 - pairs


def calculate_kokushi_shanten(tiles: List[str]) -> int:
    """
    国士無双の向聴数を計算

    Args:
        tiles: 手牌（13枚）

    Returns:
        向聴数（-1: 和了、0: テンパイ、1: イーシャンテン、...）
    """
    if len(tiles) != 13:
        return 99

    # 么九牌（1, 9, 字牌）
    yaochuuhai = ['1m', '9m', '1p', '9p', '1s', '9s', '1z', '2z', '3z', '4z', '5z', '6z', '7z']

    counts = count_tiles(tiles)

    # 么九牌の種類数をカウント
    yaochu_types = 0
    has_pair = False

    for tile in yaochuuhai:
        if tile in counts:
            yaochu_types += 1
            if counts[tile] >= 2:
                has_pair = True

    # 国士無双の向聴数 = 13 - yaochu_types - (1 if has_pair else 0)
    if has_pair:
        return 13 - yaochu_types - 1
    else:
        return 13 - yaochu_types


def calculate_standard_shanten(tiles: List[str]) -> int:
    """
    4面子1雀頭の標準形の向聴数を計算（簡易版）

    Args:
        tiles: 手牌（13枚）

    Returns:
        向聴数
    """
    if len(tiles) != 13:
        return 99

    # すべての牌を加えてテンパイになるかチェック
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
    min_shanten = 99
    for tile in all_tiles:
        test_tiles_13 = tiles + [tile]
        # この14枚から1枚切ってテンパイになるかチェック
        for discard in set(test_tiles_13):
            remaining = test_tiles_13.copy()
            remaining.remove(discard)
            # 再帰を避けるため、テンパイチェックのみ
            for tile2 in all_tiles:
                test_tiles_14 = remaining + [tile2]
                if is_valid_complete_hand(test_tiles_14):
                    min_shanten = min(min_shanten, 1)
                    break
            if min_shanten == 1:
                break
        if min_shanten == 1:
            break

    if min_shanten == 1:
        return 1  # イーシャンテン

    # さらに遠い向聴数の計算は複雑なので簡略化
    return 2  # リャンシャンテン以上


def calculate_shanten(tiles: List[str]) -> Tuple[int, str]:
    """
    手牌の向聴数を計算（標準形、七対子、国士無双の最小値を返す）

    Args:
        tiles: 手牌（13枚または14枚）

    Returns:
        (向聴数, パターン名)
        向聴数: -1: 和了、0: テンパイ、1: イーシャンテン、...
        パターン名: "standard", "chiitoitsu", "kokushi"
    """
    if len(tiles) == 14:
        # 14枚の場合は和了形かチェック
        if is_valid_complete_hand(tiles):
            return -1, "standard"
        return 0, "standard"

    if len(tiles) != 13:
        return 99, "unknown"

    # 3つのパターンで向聴数を計算
    standard_shanten = calculate_standard_shanten(tiles)
    chiitoitsu_shanten = calculate_chiitoitsu_shanten(tiles)
    kokushi_shanten = calculate_kokushi_shanten(tiles)

    # 最小の向聴数を選択
    min_shanten = min(standard_shanten, chiitoitsu_shanten, kokushi_shanten)

    if min_shanten == standard_shanten:
        return min_shanten, "standard"
    elif min_shanten == chiitoitsu_shanten:
        return min_shanten, "chiitoitsu"
    else:
        return min_shanten, "kokushi"

def validate_problem_content(content: str) -> Tuple[bool, str]:
    """
    生成された問題の内容を検証

    Args:
        content: 生成された問題のMarkdownテキスト

    Returns:
        (検証結果, エラーメッセージ)
    """
    # ツモ牌を抽出
    tsumo_match = re.search(r'## ツモ牌\s*```\s*([🀀-🀡]+)\s*```', content)
    if not tsumo_match:
        return False, "ツモ牌が見つかりません。何を切るかの問題にはツモ牌の明記が必須です。"

    tsumo_str = tsumo_match.group(1)
    tsumo_tiles = parse_tiles(tsumo_str)

    if len(tsumo_tiles) != 1:
        return False, f"ツモ牌は1枚である必要があります（{len(tsumo_tiles)}枚）"

    # 手牌を抽出
    hand_match = re.search(r'## あなたの手牌[（(]13枚[)）]?\s*```\s*([🀀-🀡]+)\s*```', content)
    if not hand_match:
        return False, "手牌が見つかりません"

    hand_str = hand_match.group(1)
    hand_tiles = parse_tiles(hand_str)

    if len(hand_tiles) != 13:
        return False, f"手牌が13枚ではありません（{len(hand_tiles)}枚）"

    # 向聴数を計算
    shanten, pattern = calculate_shanten(hand_tiles)
    shanten_names = {-1: "和了", 0: "テンパイ", 1: "イーシャンテン", 2: "リャンシャンテン"}
    pattern_names = {"standard": "標準形", "chiitoitsu": "七対子", "kokushi": "国士無双"}

    # 問題文から向聴数の記述を探す
    content_lower = content.lower()
    if 'テンパイ' in content or 'tenpai' in content_lower:
        if shanten != 0:
            actual = shanten_names.get(shanten, f"{shanten}シャンテン")
            pattern_str = pattern_names.get(pattern, pattern)
            return False, f"問題文に「テンパイ」と記載がありますが、実際は{actual}です（{pattern_str}）"

    if 'イーシャンテン' in content or '1シャンテン' in content:
        if shanten != 1:
            actual = shanten_names.get(shanten, f"{shanten}シャンテン")
            pattern_str = pattern_names.get(pattern, pattern)
            return False, f"問題文に「イーシャンテン」と記載がありますが、実際は{actual}です（{pattern_str}）"

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
        test_shanten, test_pattern = calculate_shanten(test_tiles)

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
            test_pattern_str = pattern_names.get(test_pattern, test_pattern)
            return False, f"{tile_unicode}を引いても{expected}になりません（実際は{actual}、{test_pattern_str}）"

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
    all_tiles.extend(tsumo_tiles)  # ツモ牌を追加
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

    # 点数配分の妥当性チェック
    point_pattern = r'(\d+)点'
    point_matches = re.findall(point_pattern, content)
    if len(point_matches) >= 4:
        try:
            points = [int(p) for p in point_matches[:4]]
            total_points = sum(points)

            # 合計点数チェック
            if total_points != 100000:
                return False, f"点数の合計が100000点ではありません（{total_points}点）"

            # 場を抽出
            round_match = re.search(r'場:\s*(東|南)(\d+)局(\d+)本場', content)
            if round_match:
                wind = round_match.group(1)
                round_num = int(round_match.group(2))
                honba = int(round_match.group(3))

                # 親の位置を特定（東1局=東家、東2局=南家、東3局=西家、東4局=北家）
                round_to_dealer = {1: '東', 2: '南', 3: '西', 4: '北'}
                expected_dealer = round_to_dealer.get(round_num)

                # 問題文中の親の記載をチェック
                dealer_mention_match = re.search(r'(東家|南家|西家|北家).*親', content)
                if dealer_mention_match:
                    mentioned_dealer = dealer_mention_match.group(1).replace('家', '')
                    if expected_dealer and mentioned_dealer != expected_dealer:
                        return False, f"{wind}{round_num}局では{expected_dealer}家が親であるべきですが、{mentioned_dealer}家が親と記載されています"

                # テーマをチェック
                theme_match = re.search(r'\*\*テーマ\*\*:\s*(.+)', content)
                if theme_match:
                    theme = theme_match.group(1)
                    # 押し引き問題で東1局0本場をチェック
                    if '押し引き' in theme and wind == '東' and round_num == 1 and honba == 0:
                        return False, f"押し引き問題では点数状況が重要なため、東1局0本場を使用すべきではありません。東2局以降または南場を使用してください。"

                # 東1局0本場チェック
                if wind == '東' and round_num == 1 and honba == 0:
                    if not all(p == 25000 for p in points):
                        return False, f"東1局0本場では全員25000点であるべきです（実際: {points}）"

                # 東1局1本場チェック
                if wind == '東' and round_num == 1 and honba == 1:
                    # 親（東家）の点数を確認
                    # 自風を抽出して親を特定
                    self_wind_match = re.search(r'自風:\s*(東|南|西|北)', content)
                    if self_wind_match:
                        self_wind = self_wind_match.group(1)
                        wind_to_index = {'東': 0, '南': 1, '西': 2, '北': 3}

                        # プレイヤー名から点数を特定（自分、下家、対面、上家）
                        # 簡易チェック：親が大幅に点数を減らしていないか
                        if min(points) < 18000:  # 親が大幅に減っているケース
                            return False, f"東1局1本場で点数が大幅に減少しているプレイヤーがいます（{min(points)}点）。1本場は親が和了or親テンパイ流局の場合のみ発生します。"
        except (ValueError, IndexError):
            pass  # 点数の抽出に失敗した場合はスキップ

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

    # CLAUDE.mdから必要なルールセクションを読み込む
    claude_md_rules = load_claude_md_sections()

    prompt = f"""麻雀の何切る問題を1つ生成してください。

【重要なルール】
以下のルールに厳密に従ってください。これらはプロジェクトの公式ガイドライン（CLAUDE.md）から抽出されたものです。

{claude_md_rules}

【問題生成の基本要件】
1. 難易度: 1〜10のランダムな数値を選択（1=最も簡単、10=最も難しい）
2. テーマ: 問題のテーマを選択（例：リーチ判断、手役選択、押し引き、待ち選択、形式テンパイ、鳴き判断、安全牌選択など）
3. 局面情報（場、自風、ドラ表示牌、巡目）を設定
4. 河（捨て牌）の情報を含める（自分、下家、対面、上家それぞれ2〜5枚程度）
5. **点数状況**: テーマに応じて現在の点数・順位を設定
6. **ツモ牌の明記**: 必ず13枚の手牌とは別にツモ牌1枚を明記すること
7. 上記のCLAUDE.mdルールに厳密に従うこと（特に向聴数検証、点数配分、Unicode牌識別）

以下のMarkdown形式で出力してください。他の説明は不要です。

# 何切る問題 - {date_str}

**難易度**: ★★★★★☆☆☆☆☆ (5/10)
**テーマ**: リーチ判断

## 局面情報
- 場: [東1局/南2局など]
- 自風: [東/南/西/北]
- ドラ表示牌: [牌]
- 巡目: [X巡目]

## あなたの手牌（13枚）
```
[13枚の牌をUnicodeで]
```

## ツモ牌
```
[1枚の牌をUnicodeで]
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
