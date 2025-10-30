#!/usr/bin/env python3
"""
URL削除後のリマインダーメッセージ確認テスト
"""

def check_url_removal():
    """reminder_schedule.pyからURL関連が削除されたか確認"""
    print("🔍 URL削除確認テスト")
    print("=" * 40)

    try:
        # ファイルを読み込んで内容をチェック
        file_path = "src/reminder_schedule.py"

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # URL関連のキーワードをチェック
        url_keywords = [
            "🔗 ノートURL:",
            "🔗 詳細:",
            "🔗 **ノート詳細URL**",
            "上記URLで",
            "note_url_detected",
        ]

        found_keywords = []
        for keyword in url_keywords:
            if keyword in content:
                # 行番号を取得
                lines = content.split('\n')
                line_numbers = []
                for i, line in enumerate(lines, 1):
                    if keyword in line:
                        # HTML部分は除外
                        if not any(html_tag in line for html_tag in ['<h3>', '<li>', '</li>', '<strong>']):
                            line_numbers.append(i)

                if line_numbers:
                    found_keywords.append(f"{keyword}: 行 {', '.join(map(str, line_numbers))}")

        if found_keywords:
            print("❌ まだURL関連のコードが残っています:")
            for found in found_keywords:
                print(f"  - {found}")
        else:
            print("✅ URL関連のコードが完全に削除されました")

        # 残っているべき要素をチェック
        expected_elements = [
            "📋 **イベント詳細**",
            "🌤️ **天気情報**",
            "📋 **関連するノート**",
            "📝"
        ]

        print(f"\n残存確認:")
        for element in expected_elements:
            if element in content:
                print(f"✅ {element} - 正常に残存")
            else:
                print(f"❌ {element} - 削除されている可能性")

    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    check_url_removal()
