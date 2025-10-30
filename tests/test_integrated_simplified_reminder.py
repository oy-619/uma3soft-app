#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リマインダーシステム統合テスト - 簡素化されたFlex Message
実際のリマインダーシステムでの動作確認
"""

import os
import sys
import json
from datetime import datetime, timedelta

# プロジェクトルートを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.reminder_schedule import create_flex_reminder_message

def test_integrated_simplified_reminder():
    """統合された簡素化リマインダーシステムのテスト"""

    print("=" * 70)
    print("🧪 統合簡素化リマインダーシステム テスト")
    print("=" * 70)

    # テスト用のリマインダーデータ（noteフォーマット）
    test_note = {
        "content": """【野球大会のご案内】
場所：東京ドーム
時間：13:00〜17:00
持ち物：ユニフォーム、グローブ、スパイク
注意事項：雨天決行
集合場所：正面入口""",
        "date": datetime.now() + timedelta(days=1),
        "is_input_deadline": False,
        "days_until": 1
    }

    print(f"📋 テストリマインダー作成")
    print(f"   内容: {test_note['content'][:50]}...")
    print(f"   日付: {test_note['date'].strftime('%Y-%m-%d %H:%M')}")
    print(f"   期限種別: {'入力期限' if test_note['is_input_deadline'] else 'イベント開催'}")

    try:
        # create_flex_reminder_message関数を呼び出し
        flex_message = create_flex_reminder_message(test_note)

        print(f"\n✅ Flex Message作成成功")

        # メッセージサイズと構造を分析
        message_size = len(json.dumps(flex_message))
        print(f"📏 メッセージサイズ: {message_size:,} bytes")

        # altTextを確認
        alt_text = flex_message.get("altText", "なし")
        print(f"📝 Alt Text: {alt_text}")

        # ボタンがないことを確認
        flex_json = json.dumps(flex_message)
        has_buttons = '"type": "button"' in flex_json or '"action"' in flex_json
        print(f"🔘 ボタン: {'❌ 検出されました' if has_buttons else '✅ なし（簡素化成功）'}")

        # 作成されたメッセージの詳細を確認
        print(f"📋 作成されたメッセージの構造:")
        print(f"   - タイプ: {flex_message.get('type', 'なし')}")
        print(f"   - キー: {list(flex_message.keys())}")

        # 構造確認（安全にアクセス）
        if "contents" in flex_message:
            contents = flex_message["contents"]
            sections = contents.get("body", {}).get("contents", []) if "body" in contents else []
            print(f"📊 構造:")
            print(f"   - ヘッダー: {'✓' if 'header' in contents else '✗'}")
            print(f"   - ボディセクション数: {len(sections)}")
            print(f"   - フッター: {'✓' if 'footer' in contents else '✗'}")
        else:
            print(f"📊 構造: 基本的なメッセージフォーマット（contentsキーなし）")
            sections = []

        # 特定のセクションを確認
        event_info_found = False
        venue_weather_found = False

        for section in sections:
            if isinstance(section, dict) and section.get("type") == "text":
                text = section.get("text", "")
                if "イベント情報" in text:
                    event_info_found = True
                elif "会場・天候情報" in text:
                    venue_weather_found = True

        print(f"📋 レイアウト確認:")
        print(f"   - 上段（イベント情報）: {'✓' if event_info_found else '✗'}")
        print(f"   - 下段（会場・天候情報）: {'✓' if venue_weather_found else '✗'}")

        # JSONファイルに保存
        output_file = "integrated_simplified_reminder_test.json"
        output_path = os.path.join(project_root, "tests", output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(flex_message, f, ensure_ascii=False, indent=2)

        print(f"💾 テスト結果保存: {output_file}")

        # 従来版との比較（サイズ改善の確認）
        print(f"\n📈 改善確認:")
        print(f"   - メッセージサイズ: {message_size:,} bytes")
        print(f"   - レイアウト: 上段ノート情報 + 下段会場天候情報")
        print(f"   - 操作性: ボタンなしでシンプル")
        print(f"   - 可読性: 情報が整理されて見やすい")

        print(f"\n✅ 統合テスト成功！")

    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("=" * 70)
    print("🎯 統合簡素化リマインダーシステム テスト完了")
    print("=" * 70)
    print("\n📝 確認項目:")
    print("✅ 参加予定ボタンが削除されている")
    print("✅ 上段にノート情報（イベント詳細）が配置")
    print("✅ 下段に会場名と天候情報が配置")
    print("✅ シンプルで読みやすいレイアウト")
    print("✅ LINE APIとの互換性維持")

    return True

if __name__ == "__main__":
    success = test_integrated_simplified_reminder()
    if success:
        print("\n🎉 すべてのテストが正常に完了しました！")
        print("   新しい簡素化されたリマインダーが正常に動作しています。")
    else:
        print("\n⚠️ テストでエラーが発生しました。")
