#!/usr/bin/env python3
"""
麻雀の何切る問題に対する回答を自動生成するスクリプト
Claude API を使用して既存の問題を分析し、回答と解説を生成します。
"""

import os
import sys
import time
from datetime import datetime
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError

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

【要件】
1. 問題を詳細に分析し、最適な打牌を決定してください
2. その理由を初心者にも分かりやすく解説してください
3. 可能な候補を複数挙げ、それぞれを比較してください
4. 受け入れ枚数などの定量的な情報も含めてください

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

    # 回答を生成
    answer_content = generate_solution(problem_content)

    # ファイルに保存
    answer_filename = f"{problem_dir}/solution.md"
    with open(answer_filename, "w", encoding="utf-8") as f:
        f.write(answer_content)

    print(f"Answer saved to {answer_filename}")
    return answer_filename

if __name__ == "__main__":
    main()
