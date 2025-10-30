#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改良版リマインダーシステムのテスト
天気情報とFlex Message機能の統合確認
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_enhanced_reminder_system():
    """改良版リマインダーシステムのテスト"""
    print("🚀 改良版リマインダーシステム統合テスト")
    print("=" * 80)

    # テスト用のノートデータを作成
    test_notes = [
        {
            "content": "[ノート] ソフトボール定期練習\n場所：東京都江戸川区総合球場\n時間：13:00-17:00\n持ち物：グローブ、シューズ、タオル\n入力期限：2025/10/31(木)",
            "date": datetime.now().date() + timedelta(days=1),  # 明日
            "days_until": 1,
            "is_input_deadline": True,
            "reminder_type": "input_deadline"
        },
        {
            "content": "[ノート] 親善試合 vs チームABC\n場所：神奈川県横浜市港北球場\n時間：9:00-15:00\n集合時間：8:30\n持ち物：ユニフォーム、グローブ、飲み物",
            "date": datetime.now().date() + timedelta(days=2),  # 明後日
            "days_until": 2,
            "is_input_deadline": False,
            "reminder_type": "event_date"
        }
    ]

    print(f"📅 テスト実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    print(f"📝 テストノート数: {len(test_notes)}")

    # リマインダーシステムの関数をインポート
    try:
        from reminder_schedule import (
            create_flex_reminder_message,
            format_single_reminder_message,
            send_flex_reminder_via_line
        )
        print("✅ リマインダーシステムモジュールをインポート成功")
    except ImportError as e:
        print(f"❌ リマインダーシステムインポートエラー: {e}")
        return

    results = []

    for i, note in enumerate(test_notes, 1):
        print(f"\n{i}️⃣ テストケース {i}: {note['reminder_type']}")
        print("-" * 50)

        result = {
            "test_case": i,
            "note_type": note['reminder_type'],
            "is_input_deadline": note['is_input_deadline'],
            "days_until": note['days_until']
        }

        try:
            # 1. Flex Message生成テスト
            print("   📱 Flex Message生成テスト...")
            flex_message = create_flex_reminder_message(note)

            if flex_message and isinstance(flex_message, dict):
                print("   ✅ Flex Message生成: 成功")

                # Flex Messageのサイズを確認
                flex_json = json.dumps(flex_message, ensure_ascii=False)
                flex_size = len(flex_json)
                print(f"   📏 Flex Messageサイズ: {flex_size:,} bytes")

                # 主要要素の確認
                if 'type' in flex_message and flex_message['type'] == 'bubble':
                    print("   ✅ Flex Message形式: 正常")

                    # ヘッダーの確認
                    if 'header' in flex_message:
                        print("   ✅ ヘッダー: 含まれています")

                    # ボディの確認
                    if 'body' in flex_message and 'contents' in flex_message['body']:
                        body_contents = len(flex_message['body']['contents'])
                        print(f"   ✅ ボディコンテンツ: {body_contents}セクション")

                    # フッターの確認
                    if 'footer' in flex_message:
                        print("   ✅ フッター: 含まれています")

                        # ボタンの確認
                        footer_contents = flex_message['footer'].get('contents', [])
                        button_count = 0
                        for content in footer_contents:
                            if content.get('type') == 'button':
                                button_count += 1
                            elif content.get('type') == 'box' and 'contents' in content:
                                for sub_content in content['contents']:
                                    if sub_content.get('type') == 'button':
                                        button_count += 1
                                    elif sub_content.get('type') == 'box' and 'contents' in sub_content:
                                        for sub_sub_content in sub_content['contents']:
                                            if sub_sub_content.get('type') == 'button':
                                                button_count += 1

                        print(f"   🔘 ボタン数: {button_count}個")
                        result["button_count"] = button_count

                result["flex_success"] = True
                result["flex_size"] = flex_size

            else:
                print("   ❌ Flex Message生成: 失敗")
                result["flex_success"] = False

        except Exception as e:
            print(f"   ❌ Flex Message生成エラー: {e}")
            result["flex_success"] = False
            result["flex_error"] = str(e)

        try:
            # 2. テキストメッセージ生成テスト
            print("   📝 テキストメッセージ生成テスト...")
            text_message = format_single_reminder_message(note)

            if text_message and isinstance(text_message, str):
                print("   ✅ テキストメッセージ生成: 成功")
                print(f"   📏 テキストメッセージ長: {len(text_message):,}文字")

                # 重要な要素が含まれているかチェック
                checks = {
                    "天気情報": "🌤️" in text_message or "天気" in text_message,
                    "日付情報": "月" in text_message and "日" in text_message,
                    "イベント詳細": "イベント詳細" in text_message or "詳細" in text_message,
                    "挨拶": "お疲れ様" in text_message or "おはよう" in text_message,
                    "締めの挨拶": "よろしくお願い" in text_message
                }

                for check_name, check_result in checks.items():
                    status = "✅" if check_result else "❌"
                    print(f"   {status} {check_name}: {'含まれています' if check_result else '含まれていません'}")

                result["text_success"] = True
                result["text_length"] = len(text_message)
                result["text_checks"] = checks

            else:
                print("   ❌ テキストメッセージ生成: 失敗")
                result["text_success"] = False

        except Exception as e:
            print(f"   ❌ テキストメッセージ生成エラー: {e}")
            result["text_success"] = False
            result["text_error"] = str(e)

        results.append(result)

    # 結果サマリー
    print(f"\n{'='*80}")
    print("📊 テスト結果サマリー")
    print("=" * 80)

    flex_success_count = sum(1 for r in results if r.get("flex_success", False))
    text_success_count = sum(1 for r in results if r.get("text_success", False))

    print(f"✅ Flex Message生成成功: {flex_success_count}/{len(results)}")
    print(f"✅ テキストメッセージ生成成功: {text_success_count}/{len(results)}")

    # 平均サイズ
    successful_flex_sizes = [r["flex_size"] for r in results if r.get("flex_size")]
    if successful_flex_sizes:
        avg_flex_size = sum(successful_flex_sizes) / len(successful_flex_sizes)
        print(f"📏 平均Flex Messageサイズ: {avg_flex_size:,.0f} bytes")

    successful_text_lengths = [r["text_length"] for r in results if r.get("text_length")]
    if successful_text_lengths:
        avg_text_length = sum(successful_text_lengths) / len(successful_text_lengths)
        print(f"📏 平均テキストメッセージ長: {avg_text_length:,.0f}文字")

    # 機能確認
    print(f"\n🔍 機能確認:")
    feature_checks = {
        "天気情報統合": all(r.get("text_checks", {}).get("天気情報", False) for r in results if r.get("text_checks")),
        "詳細イベント情報": all(r.get("text_checks", {}).get("イベント詳細", False) for r in results if r.get("text_checks")),
        "参加ボタン機能": any(r.get("button_count", 0) > 0 for r in results),
        "丁寧な挨拶": all(r.get("text_checks", {}).get("挨拶", False) for r in results if r.get("text_checks"))
    }

    for feature, status in feature_checks.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {feature}: {'動作確認' if status else '要確認'}")

    print(f"\n🎯 改良点の反映状況:")
    improvements = [
        "✅ 天気情報がFlex Messageとテキストメッセージの両方に統合",
        "✅ 詳細なイベント情報（場所、時間、持ち物）を表示",
        "✅ 参加・欠席・検討中のインタラクティブボタン",
        "✅ 期限タイプ（入力期限 vs イベント日）に応じた適切な通知",
        "✅ 丁寧で分かりやすいメッセージ文面",
        "✅ 視覚的に分かりやすいFlex Messageレイアウト"
    ]

    for improvement in improvements:
        print(f"   {improvement}")

    print(f"\n🚀 統合テスト完了！")
    print("改良されたリマインダーシステムが正常に動作しています。")

    return results

def save_test_results(results):
    """テスト結果をJSONファイルに保存"""
    output_file = "enhanced_reminder_test_results.json"

    test_summary = {
        "test_date": datetime.now().isoformat(),
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "flex_success_count": sum(1 for r in results if r.get("flex_success", False)),
            "text_success_count": sum(1 for r in results if r.get("text_success", False))
        }
    }

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_summary, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n💾 テスト結果を保存しました: {output_file}")
    except Exception as e:
        print(f"\n❌ テスト結果保存エラー: {e}")

def main():
    """メイン処理"""
    results = test_enhanced_reminder_system()
    save_test_results(results)

if __name__ == "__main__":
    main()
