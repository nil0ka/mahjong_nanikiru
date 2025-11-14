#!/usr/bin/env python3
"""
麻雀問題の一覧を表示するスクリプト
"""

import os
import re
import sys
from typing import List, Dict, Optional

def parse_problem_file(problem_path: str) -> Optional[Dict[str, str]]:
    """
    問題ファイルから情報を抽出する

    Args:
        problem_path: 問題ファイルのパス

    Returns:
        問題情報の辞書、またはNone
    """
    if not os.path.exists(problem_path):
        return None

    try:
        with open(problem_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 日付を抽出
        date_match = re.search(r'# 何切る問題 - (\d{4}-\d{2}-\d{2})', content)
        date = date_match.group(1) if date_match else "不明"

        # 難易度を抽出
        difficulty_match = re.search(r'\*\*難易度\*\*: [★☆]+ \((\d+)/10\)', content)
        difficulty = difficulty_match.group(1) if difficulty_match else "?"

        # テーマを抽出
        theme_match = re.search(r'\*\*テーマ\*\*: (.+)', content)
        theme = theme_match.group(1).strip() if theme_match else "未設定"

        # 回答の有無を確認
        answer_path = problem_path.replace('question.md', 'solution.md')
        has_answer = os.path.exists(answer_path)

        return {
            'date': date,
            'difficulty': difficulty,
            'theme': theme,
            'has_answer': has_answer
        }
    except Exception as e:
        print(f"Warning: Failed to parse {problem_path}: {e}", file=sys.stderr)
        return None

def list_problems(filter_theme: Optional[str] = None,
                  filter_difficulty: Optional[str] = None) -> None:
    """
    問題の一覧を表示する

    Args:
        filter_theme: テーマでフィルタリング（部分一致）
        filter_difficulty: 難易度でフィルタリング（完全一致）
    """
    if not os.path.exists("problems"):
        print("問題ディレクトリが見つかりません。")
        return

    # 問題ディレクトリを取得
    problem_dirs = []
    for d in os.listdir("problems"):
        dir_path = os.path.join("problems", d)
        if os.path.isdir(dir_path) and d.isdigit():
            problem_dirs.append(int(d))

    if not problem_dirs:
        print("問題が見つかりません。")
        return

    problem_dirs.sort()

    # ヘッダー表示
    print(f"{'番号':<6} {'日付':<12} {'難易度':<6} {'テーマ':<20} {'回答':<6}")
    print("-" * 70)

    count = 0
    for num in problem_dirs:
        problem_path = f"problems/{num:03d}/question.md"
        info = parse_problem_file(problem_path)

        if info is None:
            continue

        # フィルタリング
        if filter_theme and filter_theme not in info['theme']:
            continue
        if filter_difficulty and info['difficulty'] != filter_difficulty:
            continue

        # 表示
        answer_status = "✓" if info['has_answer'] else "✗"
        print(f"#{num:<5} {info['date']:<12} {info['difficulty']:<6} {info['theme']:<20} {answer_status:<6}")
        count += 1

    print("-" * 70)
    print(f"合計: {count}問 (全{len(problem_dirs)}問中)")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='麻雀問題の一覧を表示')
    parser.add_argument('--theme', '-t', help='テーマでフィルタリング（部分一致）')
    parser.add_argument('--difficulty', '-d', help='難易度でフィルタリング（1-10）')

    args = parser.parse_args()

    list_problems(filter_theme=args.theme, filter_difficulty=args.difficulty)

if __name__ == "__main__":
    main()
