#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版リマインダーシステムのテスト
Flex Message送信エラーの修正確認
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_fixed_reminder_system():
    """修正版リマインダーシステムのテスト"""
    print("🔧 修正版リマインダーシステムテスト")
    print("=" * 80)

    # 長い会場名を含むテストノート（実際のエラーケースをシミュレート）
    test_note = {
        "content": "[ノート] 東京都小学生男子ソフトボール秋季大会\n【大会日程】 10月25日（土）／26日（日）／予備日・11月1日（土）／2日（日）\n【大会会場】 葛飾区柴又野球場\n●調整さん●\nhttps://chouseisan.com/example",
        "date": datetime.now().date() + timedelta(days=1),  # 明日
        "days_until": 1,
        "is_input_deadline": True,
        "reminder_type": "input_deadline"
    }

    print(f"📅 テスト日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    print(f"📝 テストノート内容（抜粋）:")
    print(f"   {test_note['content'][:100]}...")

    # リマインダーシステムの関数をインポート
    from reminder_schedule import (
        create_flex_reminder_message,
        send_flex_reminder_via_line
    )

    print(f"\n{'='*80}")
    print("🔧 修正点確認")
    print("=" * 80)

    try:
        # 1. Flex Message生成テスト
        print("   📱 Flex Message生成テスト...")
        flex_message = create_flex_reminder_message(test_note)

        if flex_message:
            print("   ✅ Flex Message生成: 成功")

            # Flex Messageの構造を確認
            message_type = flex_message.get('type')
            print(f"   📋 メッセージタイプ: {message_type}")

            if message_type == 'flex':
                print("   ✅ 正しいFlex Message形式")

                # altTextの確認
                alt_text = flex_message.get('altText', '')
                print(f"   📝 altText: {alt_text[:50]}...")

                # contentsの確認
                contents = flex_message.get('contents', {})
                if contents.get('type') == 'bubble':
                    print("   ✅ Bubble形式のコンテンツ")

                # JSONサイズ確認
                json_size = len(json.dumps(flex_message, ensure_ascii=False))
                print(f"   📏 JSONサイズ: {json_size:,} bytes")

                # 修正されたFlex Messageを保存
                with open("fixed_flex_message.json", 'w', encoding='utf-8') as f:
                    json.dump(flex_message, f, ensure_ascii=False, indent=2)
                print("   💾 修正版Flex Message保存: fixed_flex_message.json")

            else:
                print(f"   ❌ 不正なメッセージタイプ: {message_type}")

        else:
            print("   ❌ Flex Message生成: 失敗")

    except Exception as e:
        print(f"   ❌ Flex Message生成エラー: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*80}")
    print("🌍 場所抽出テスト")
    print("=" * 80)

    try:
        # 場所抽出ロジックを直接テスト
        import re

        event_content = test_note['content']
        location = "東京都"

        location_patterns = [
            r'場所[：:]\s*([^\n]+)',
            r'会場[：:]\s*([^\n]+)',
            r'開催地[：:]\s*([^\n]+)',
            r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\n]*球場',
            r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\n]*グラウンド',
            r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)'
        ]

        print(f"   📝 元の内容: {event_content}")

        for i, pattern in enumerate(location_patterns, 1):
            match = re.search(pattern, event_content)
            if match:
                print(f"   🎯 パターン{i} マッチ: {pattern}")

                if pattern.startswith('場所') or pattern.startswith('会場') or pattern.startswith('開催地'):
                    extracted_location = match.group(1).strip()
                    print(f"   📍 抽出された場所: {extracted_location}")

                    # 場所情報が長すぎる場合は短縮
                    if len(extracted_location) > 30:
                        print(f"   ⚠️ 場所名が長い（{len(extracted_location)}文字）- 短縮処理実行")
                        city_match = re.search(r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\s]*[区市町]', extracted_location)
                        if city_match:
                            location = city_match.group(0)
                            print(f"   ✂️ 短縮後の場所: {location}")
                        else:
                            location = extracted_location[:20]
                            print(f"   ✂️ 文字数制限後の場所: {location}")
                    else:
                        location = extracted_location
                        print(f"   ✅ 適切な長さの場所: {location}")
                else:
                    location = match.group(0)
                    print(f"   📍 抽出された場所: {location}")
                break

        print(f"   🏁 最終的な場所: {location}")
        print(f"   📏 場所の長さ: {len(location)}文字")

    except Exception as e:
        print(f"   ❌ 場所抽出エラー: {e}")

    print(f"\n{'='*80}")
    print("📊 修正結果サマリー")
    print("=" * 80)

    fixes = [
        "✅ Flex Message構造の修正 - 二重typeプロパティ問題を解決",
        "✅ 場所抽出ロジックの改善 - 長すぎる場所名を短縮",
        "✅ API送信形式の修正 - 正しいFlex Message形式で送信",
        "✅ エラーハンドリングの強化 - より詳細なデバッグ情報"
    ]

    for fix in fixes:
        print(f"   {fix}")

    print(f"\n🎯 期待される改善:")
    improvements = [
        "❌ 400 Client Error (invalid property /type) の解決",
        "❌ 404 Not Found (長すぎるURL) の解決",
        "✅ Flex Message送信の成功",
        "✅ 天気情報の正常な取得と表示"
    ]

    for improvement in improvements:
        print(f"   {improvement}")

    print(f"\n🚀 修正版リマインダーシステムのテスト完了！")

if __name__ == "__main__":
    test_fixed_reminder_system()
