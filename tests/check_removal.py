#!/usr/bin/env python3
"""
調整さんURL削除確認テスト
"""

def check_reminder_code():
    """reminder_schedule.pyのコードから調整さん関連が削除されたか確認"""
    print("🔍 調整さんURL削除確認")
    print("=" * 40)

    try:
        # ファイルを読み込んで内容をチェック
        file_path = "src/reminder_schedule.py"

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 調整さん関連のキーワードをチェック
        keywords_to_check = [
            "chouseisan",
            "調整さん",
            "📊",
            "chouseisan_url"
        ]

        found_keywords = []
        for keyword in keywords_to_check:
            if keyword in content:
                # 行番号を取得
                lines = content.split('\n')
                line_numbers = []
                for i, line in enumerate(lines, 1):
                    if keyword in line:
                        line_numbers.append(i)

                if line_numbers:
                    found_keywords.append(f"{keyword}: 行 {', '.join(map(str, line_numbers))}")

        if found_keywords:
            print("❌ まだ調整さん関連のコードが残っています:")
            for found in found_keywords:
                print(f"  - {found}")
        else:
            print("✅ 調整さん関連のコードが完全に削除されました")

        print(f"\nファイルサイズ: {len(content)} 文字")
        print(f"総行数: {len(content.split())}")

    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    check_reminder_code()
