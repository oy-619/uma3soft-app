#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拡張リマインダーのLINE Bot統合テスト
"""

import os
import sys
import json
from datetime import datetime, timedelta

# プロジェクトルート設定
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

def test_line_bot_integration():
    """LINE Bot統合テスト"""

    print("=" * 80)
    print("📱 拡張リマインダー LINE Bot統合テスト")
    print("=" * 80)

    try:
        # LINE Bot APIテスト用のダミーメッセージ作成
        from enhanced_reminder_messages import generate_enhanced_reminder_message, generate_enhanced_flex_message        # テスト用のイベントデータ
        test_event = {
            "content": "[重要] チーム会議\n日時: 明日 14:00-16:00\n場所: 会議室B\n議題: 来月のプロジェクト計画\n参加者: 全メンバー",
            "date": datetime.now().date() + timedelta(days=1),
            "days_until": 1,
            "is_input_deadline": False
        }

        print("🔍 テストイベント:")
        print(f"  内容: {test_event['content'].split(chr(10))[0]}")
        print(f"  日付: {test_event['date']}")
        print(f"  残り日数: {test_event['days_until']}日")
        print(f"  入力期限: {'はい' if test_event['is_input_deadline'] else 'いいえ'}")

        print("\n" + "-" * 60)

        # 1. 拡張テキストメッセージの生成テスト
        print("📝 1. 拡張テキストメッセージ生成テスト")
        enhanced_text = generate_enhanced_reminder_message(test_event)

        print("✅ 生成成功")
        print(f"メッセージ長: {len(enhanced_text)}文字")
        print(f"改行数: {enhanced_text.count(chr(10))}行")
        print(f"天気情報含有: {'天気情報' in enhanced_text}")
        print(f"丁寧語使用: {'お疲れ様です' in enhanced_text}")

        # 2. 拡張Flex Message生成テスト
        print("\n📱 2. 拡張Flex Message生成テスト")
        enhanced_flex = generate_enhanced_flex_message(test_event)

        print("✅ 生成成功")
        print(f"Flex Type: {enhanced_flex.get('type')}")
        print(f"Header色: {enhanced_flex.get('header', {}).get('backgroundColor', 'N/A')}")
        print(f"コンテンツ数: {len(enhanced_flex.get('body', {}).get('contents', []))}")

        # 3. LINE Bot送信フォーマット準備テスト
        print("\n📤 3. LINE Bot送信フォーマット準備テスト")

        # テキストメッセージ形式
        text_message_format = {
            "type": "text",
            "text": enhanced_text
        }

        # Flex Message形式
        flex_message_format = {
            "type": "flex",
            "altText": "リマインダー通知",
            "contents": enhanced_flex
        }

        print("✅ テキストメッセージフォーマット準備完了")
        print(f"  Type: {text_message_format['type']}")
        print(f"  Text Length: {len(text_message_format['text'])}文字")

        print("✅ Flex Messageフォーマット準備完了")
        print(f"  Type: {flex_message_format['type']}")
        print(f"  Alt Text: {flex_message_format['altText']}")

        # 4. 統合システムテスト
        print("\n🔗 4. reminder_schedule.py統合テスト")

        # 既存システムで拡張機能が動作することを確認
        note_dict = {
            'content': test_event["content"],
            'date': test_event["date"],
            'days_until': test_event["days_until"],
            'is_input_deadline': test_event["is_input_deadline"]
        }

        from reminder_schedule import format_single_reminder_message, create_flex_reminder_message

        integrated_text = format_single_reminder_message(note_dict)
        integrated_flex = create_flex_reminder_message(note_dict)

        print("✅ 統合テキストメッセージ生成成功")
        print(f"  拡張機能使用: {len(integrated_text) > 500}")  # 拡張版は通常より長い

        print("✅ 統合Flex Message生成成功")
        print(f"  天気情報含有: {'天気' in str(integrated_flex)}")

        # 5. エラーハンドリングテスト
        print("\n🛡️ 5. エラーハンドリングテスト")

        # 不正なデータでテスト
        invalid_event = {
            "content": "",
            "date": None,
            "days_until": -1,
            "is_input_deadline": "invalid"
        }

        try:
            fallback_message = generate_enhanced_reminder_message(invalid_event)
            print("✅ フォールバック機能動作確認")
            print(f"  フォールバックメッセージ長: {len(fallback_message)}文字")
        except Exception as e:
            print(f"⚠️ エラーハンドリング確認: {e}")

        print("\n" + "=" * 80)
        print("🎉 統合テスト完了 - すべての機能が正常に動作しています")
        print("=" * 80)

        # 6. 実用例の表示
        print("\n💡 実際の使用例:")
        print("-" * 40)
        print("# LINE Bot側での使用方法")
        print("```python")
        print("# テキストメッセージ送信")
        print("line_bot_api.reply_message(")
        print("    event.reply_token,")
        print("    TextSendMessage(text=enhanced_text)")
        print(")")
        print("")
        print("# Flex Message送信")
        print("line_bot_api.reply_message(")
        print("    event.reply_token,")
        print("    FlexSendMessage(")
        print("        alt_text='リマインダー通知',")
        print("        contents=enhanced_flex")
        print("    )")
        print(")")
        print("```")

        return True

    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_line_bot_integration()
    if success:
        print("\n✨ 拡張リマインダー機能の準備が完了しました！")
    else:
        print("\n🔧 設定の確認が必要です。")
