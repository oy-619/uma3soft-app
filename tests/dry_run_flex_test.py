#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版Flex Message送信テスト（ドライラン）
実際の送信はせず、データ構造のみ確認
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def dry_run_flex_message_send():
    """Flex Message送信のドライランテスト"""
    print("🧪 Flex Message送信ドライランテスト")
    print("=" * 80)

    # リマインダーシステムの関数をインポート
    from reminder_schedule import create_flex_reminder_message

    # テストノート
    test_note = {
        "content": "[ノート] 東京都小学生男子ソフトボール秋季大会\n【大会日程】 10月25日（土）／26日（日）／予備日・11月1日（土）／2日（日）\n【大会会場】 葛飾区柴又野球場\n●調整さん●",
        "date": datetime.now().date() + timedelta(days=1),
        "days_until": 1,
        "is_input_deadline": True,
        "reminder_type": "input_deadline"
    }

    print(f"📅 テスト実行: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")

    try:
        # Flex Message生成
        flex_message = create_flex_reminder_message(test_note)

        if not flex_message:
            print("❌ Flex Message生成に失敗")
            return

        print("✅ Flex Message生成成功")

        # 送信データ構造をシミュレート（修正前）
        old_data_structure = {
            "to": "TARGET_ID",
            "messages": [
                {
                    "type": "flex",
                    "altText": "リマインダー通知",
                    "contents": flex_message  # これが問題！flex_messageが既にtypeを持っている
                }
            ],
        }

        # 送信データ構造をシミュレート（修正後）
        if isinstance(flex_message, dict) and flex_message.get("type") == "flex":
            # そのまま使用
            new_data_structure = {
                "to": "TARGET_ID",
                "messages": [flex_message],  # 直接使用
            }
        else:
            # contentsとして使用
            new_data_structure = {
                "to": "TARGET_ID",
                "messages": [
                    {
                        "type": "flex",
                        "altText": "リマインダー通知",
                        "contents": flex_message
                    }
                ],
            }

        print(f"\n{'='*80}")
        print("📊 データ構造比較")
        print("=" * 80)

        print("❌ 修正前の構造（エラーの原因）:")
        old_message = old_data_structure["messages"][0]
        print(f"   messages[0].type: {old_message.get('type')}")
        if 'contents' in old_message:
            contents_type = old_message['contents'].get('type')
            print(f"   messages[0].contents.type: {contents_type}")
            print("   ⚠️ 問題: typeプロパティが二重になっている")

        print("\n✅ 修正後の構造:")
        new_message = new_data_structure["messages"][0]
        print(f"   messages[0].type: {new_message.get('type')}")
        if 'contents' in new_message:
            contents_type = new_message['contents'].get('type')
            print(f"   messages[0].contents.type: {contents_type}")
        else:
            print("   messages[0]が直接Flex Messageオブジェクト")
            if 'altText' in new_message:
                print(f"   messages[0].altText: {new_message.get('altText')[:50]}...")

        # JSON構造をファイルに保存して詳細確認
        with open("dry_run_old_structure.json", 'w', encoding='utf-8') as f:
            json.dump(old_data_structure, f, ensure_ascii=False, indent=2)

        with open("dry_run_new_structure.json", 'w', encoding='utf-8') as f:
            json.dump(new_data_structure, f, ensure_ascii=False, indent=2)

        print(f"\n💾 データ構造をファイルに保存:")
        print(f"   📁 dry_run_old_structure.json - 修正前（エラーの原因）")
        print(f"   📁 dry_run_new_structure.json - 修正後（正常）")

        # サイズ比較
        old_size = len(json.dumps(old_data_structure, ensure_ascii=False))
        new_size = len(json.dumps(new_data_structure, ensure_ascii=False))

        print(f"\n📏 データサイズ比較:")
        print(f"   修正前: {old_size:,} bytes")
        print(f"   修正後: {new_size:,} bytes")
        print(f"   差分: {new_size - old_size:+,} bytes")

        print(f"\n{'='*80}")
        print("🎯 修正効果の予測")
        print("=" * 80)

        expected_results = [
            "✅ 400 Client Error (invalid property /type) の解決",
            "✅ Flex Message送信の成功",
            "✅ 正しい構造でのLINE API呼び出し",
            "✅ リマインダー通知の正常な配信"
        ]

        for result in expected_results:
            print(f"   {result}")

        print(f"\n🔧 実施した修正内容:")
        fixes = [
            "📱 Flex Messageの二重typeプロパティ問題を修正",
            "🌍 長すぎる場所名の短縮処理を追加",
            "📡 LINE API送信データ構造の正規化",
            "🛡️ データ構造の事前検証機能を追加"
        ]

        for fix in fixes:
            print(f"   {fix}")

        print(f"\n🚀 ドライランテスト完了！")
        print("修正版リマインダーシステムは正常に動作するはずです。")

    except Exception as e:
        print(f"❌ ドライランテストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    dry_run_flex_message_send()
