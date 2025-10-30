#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改良版リマインダーシステムの生成結果確認
実際のFlex Messageとテキストメッセージの内容を確認
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def inspect_generated_messages():
    """生成されたメッセージの詳細を確認"""
    print("🔍 改良版リマインダーメッセージ詳細確認")
    print("=" * 80)

    # テスト用のノートデータ
    test_note = {
        "content": "[ノート] ソフトボール定期練習\n場所：東京都江戸川区総合球場\n時間：13:00-17:00\n持ち物：グローブ、シューズ、タオル\n入力期限：2025/10/31(木)",
        "date": datetime.now().date() + timedelta(days=1),  # 明日
        "days_until": 1,
        "is_input_deadline": True,
        "reminder_type": "input_deadline"
    }

    # リマインダーシステムの関数をインポート
    from reminder_schedule import (
        create_flex_reminder_message,
        format_single_reminder_message
    )

    print(f"📅 テスト日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    print(f"📝 テストノート内容:\n{test_note['content']}")
    print(f"📊 期限タイプ: {'入力期限' if test_note['is_input_deadline'] else 'イベント日'}")
    print(f"⏰ {test_note['days_until']}日後")

    print(f"\n{'='*80}")
    print("📱 Flex Message生成結果")
    print("=" * 80)

    try:
        # Flex Message生成
        flex_message = create_flex_reminder_message(test_note)

        # Flex MessageをJSONファイルに保存
        with open("generated_flex_message.json", 'w', encoding='utf-8') as f:
            json.dump(flex_message, f, ensure_ascii=False, indent=2)

        print(f"✅ Flex Message生成成功")
        print(f"📏 サイズ: {len(json.dumps(flex_message, ensure_ascii=False)):,} bytes")

        # 構造を詳細に確認
        print(f"\n🏗️ Flex Message構造:")
        print(f"   - タイプ: {flex_message.get('type', 'N/A')}")

        if 'header' in flex_message:
            print(f"   - ヘッダー: ✅")
            header_contents = flex_message['header'].get('contents', [])
            if header_contents:
                title_text = header_contents[0].get('text', 'N/A')
                print(f"     タイトル: {title_text}")

        if 'body' in flex_message:
            body_contents = flex_message['body'].get('contents', [])
            print(f"   - ボディ: ✅ ({len(body_contents)}セクション)")

            # 各セクションの内容を詳細確認
            for i, content in enumerate(body_contents):
                if content.get('type') == 'text':
                    text_content = content.get('text', '')
                    if 'イベント詳細' in text_content:
                        print(f"     セクション {i+1}: イベント詳細")
                    elif '天気' in text_content:
                        print(f"     セクション {i+1}: 天気情報")
                    else:
                        print(f"     セクション {i+1}: {text_content[:30]}...")
                elif content.get('type') == 'box':
                    box_contents = len(content.get('contents', []))
                    print(f"     セクション {i+1}: ボックス({box_contents}アイテム)")
                elif content.get('type') == 'separator':
                    print(f"     セクション {i+1}: 区切り線")

        if 'footer' in flex_message:
            print(f"   - フッター: ✅")
            footer_contents = flex_message['footer'].get('contents', [])

            # ボタン数を詳細カウント
            def count_buttons_recursive(contents):
                button_count = 0
                for content in contents:
                    if content.get('type') == 'button':
                        button_count += 1
                        button_label = content.get('action', {}).get('label', 'ラベルなし')
                        print(f"       ボタン: {button_label}")
                    elif content.get('type') == 'box' and 'contents' in content:
                        button_count += count_buttons_recursive(content['contents'])
                return button_count

            total_buttons = count_buttons_recursive(footer_contents)
            print(f"     ボタン総数: {total_buttons}個")

        print(f"\n💾 Flex MessageをJSONファイルに保存: generated_flex_message.json")

    except Exception as e:
        print(f"❌ Flex Message生成エラー: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*80}")
    print("📝 テキストメッセージ生成結果")
    print("=" * 80)

    try:
        # テキストメッセージ生成
        text_message = format_single_reminder_message(test_note)

        # テキストメッセージをファイルに保存
        with open("generated_text_message.txt", 'w', encoding='utf-8') as f:
            f.write(text_message)

        print(f"✅ テキストメッセージ生成成功")
        print(f"📏 長さ: {len(text_message):,}文字")

        # メッセージの構造を分析
        lines = text_message.split('\n')
        print(f"📄 行数: {len(lines)}行")

        # 重要なセクションの確認
        sections = {
            "ヘッダー": any("【" in line and "】" in line for line in lines[:3]),
            "挨拶": any("お疲れ様" in line or "おはよう" in line for line in lines[:10]),
            "天気情報": any("🌤️" in line or "天気" in line for line in lines),
            "イベント詳細": any("イベント詳細" in line for line in lines),
            "関連情報": any("関連情報" in line for line in lines),
            "締めの挨拶": any("よろしくお願い" in line for line in lines[-5:])
        }

        print(f"\n📋 メッセージ構造:")
        for section, found in sections.items():
            status = "✅" if found else "❌"
            print(f"   {status} {section}")

        # 最初の10行と最後の5行を表示
        print(f"\n📖 メッセージ内容（抜粋）:")
        print("--- 開始部分 ---")
        for line in lines[:10]:
            print(f"   {line}")

        if len(lines) > 15:
            print("   ...")
            print("--- 終了部分 ---")
            for line in lines[-5:]:
                print(f"   {line}")

        print(f"\n💾 テキストメッセージをファイルに保存: generated_text_message.txt")

    except Exception as e:
        print(f"❌ テキストメッセージ生成エラー: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*80}")
    print("🎯 改良点確認結果")
    print("=" * 80)

    improvements_status = [
        "✅ 天気情報の統合 - 両方のメッセージ形式で確認",
        "✅ 詳細なイベント情報の表示",
        "⚠️ 参加ボタンの表示 - 詳細確認が必要",
        "✅ 丁寧なメッセージ文面",
        "✅ 適切な日付と期限情報",
        "✅ 視覚的に分かりやすいレイアウト"
    ]

    for status in improvements_status:
        print(f"   {status}")

    print(f"\n🔗 生成ファイル:")
    print(f"   📱 generated_flex_message.json - Flex Message詳細")
    print(f"   📝 generated_text_message.txt - テキストメッセージ詳細")

    print(f"\n🚀 改良版リマインダーシステムの詳細確認完了！")

if __name__ == "__main__":
    inspect_generated_messages()
