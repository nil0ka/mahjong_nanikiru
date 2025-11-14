#!/usr/bin/env python3
"""
麻雀の何切る問題を自動生成するスクリプト
Claude API を使用して問題を生成し、Markdown ファイルとして保存します。
"""

import os
import sys
import time
from datetime import datetime
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
3. リアルな13枚の手牌を生成
4. 局面情報（場、自風、ドラ表示牌、巡目）を設定
5. 河（捨て牌）の情報を含める（自分、下家、対面、上家それぞれ2〜5枚程度）
6. Unicode麻雀牌（🀇-🀏 萬子、🀙-🀡 筒子、🀐-🀘 索子、🀀-🀆 字牌）を使用

確認事項（必ず守ること）:
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

    # 問題を生成
    problem_content = generate_question(date_str)

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
