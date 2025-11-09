#!/usr/bin/env python3
"""
現在のリマインダー実行状況をテストするスクリプト
実際のLINE送信処理をチェック
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
from datetime import datetime, date, timedelta
# 関数を直接インポート
from reminder_schedule import (
    get_reminders_for_tomorrow,
    create_flex_reminder_message,
    send_flex_reminder_via_line
)

def test_actual_reminder_execution():
    """実際のリマインダー実行をテスト"""
    print("=" * 70)
    print("🎯 現在のリマインダー実行状況テスト")
    print("=" * 70)

    try:
        # 翌日のリマインダーを直接取得
        print("\n🔄 翌日リマインダーの取得...")
        tomorrow = date.today() + timedelta(days=1)
        print(f"   対象日: {tomorrow}")

        # get_reminders_for_tomorrow関数を直接呼び出し
        reminders = get_reminders_for_tomorrow()

        print(f"\n📋 取得されたリマインダー数: {len(reminders)}")

        if reminders:
            print("\n📝 リマインダー詳細:")
            for i, reminder in enumerate(reminders, 1):
                print(f"   {i}. {reminder.get('content', 'N/A')[:100]}...")

                # 各リマインダーのFlex Message作成をテスト
                try:
                    flex_message = create_flex_reminder_message(reminder)
                    print(f"      ✅ Flex Message作成成功 ({len(json.dumps(flex_message, ensure_ascii=False))} bytes)")

                    # 会場・天候情報のチェック
                    flex_json = json.dumps(flex_message, ensure_ascii=False)
                    if "会場・天候情報" in flex_json or "🏟️" in flex_json:
                        print("      ✅ 会場・天候情報セクション確認")
                    else:
                        print("      ❌ 会場・天候情報セクションなし")

                except Exception as e:
                    print(f"      ❌ Flex Message作成エラー: {e}")
        else:
            print("   ⚠️ リマインダーが見つかりませんでした")

        print("\n✅ リマインダー取得テスト完了")        # 最近のログファイルを確認
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        if os.path.exists(logs_dir):
            print(f"\n📄 ログディレクトリ: {logs_dir}")
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
            if log_files:
                latest_log = max(log_files, key=lambda x: os.path.getctime(os.path.join(logs_dir, x)))
                print(f"   最新ログファイル: {latest_log}")

                # 最新ログの内容を表示（最後の20行）
                log_path = os.path.join(logs_dir, latest_log)
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"\n📝 最新ログ内容（最後の20行）:")
                        print("-" * 50)
                        for line in lines[-20:]:
                            print(f"   {line.rstrip()}")
                        print("-" * 50)

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

def test_flex_message_creation():
    """Flex Message作成の詳細テスト"""
    print("\n" + "=" * 70)
    print("🎯 Flex Message作成詳細テスト")
    print("=" * 70)

    try:
        # テスト用のノートデータ
        test_note = {
            'content': '[ノート] 11月2日(土) 練習試合 @東京ドーム 天気：晴れ 気温：20度 湿度：60% 風速：5m/s',
            'deadline_date': '2025-11-02'
        }

        print(f"\n📝 テスト用ノート: {test_note['content'][:100]}...")

        # create_flex_reminder_message関数を直接呼び出し
        flex_message = create_flex_reminder_message(test_note)

        print(f"\n✅ Flex Message作成成功")
        print(f"   サイズ: {len(json.dumps(flex_message, ensure_ascii=False))} bytes")
        print(f"   Alt Text: {flex_message.get('altText', 'なし')}")

        # 会場・天候情報の確認
        flex_json = json.dumps(flex_message, ensure_ascii=False)
        if '会場・天候情報' in flex_json or '🏟️' in flex_json:
            print("   ✅ 会場・天候情報セクション確認")

            # より詳細な会場・天候情報の検索
            if '東京ドーム' in flex_json:
                print("   ✅ 会場名「東京ドーム」確認")
            if '天気' in flex_json or '気温' in flex_json:
                print("   ✅ 天候情報確認")
        else:
            print("   ❌ 会場・天候情報セクションが見つかりません")

        # JSONファイルに保存
        output_file = os.path.join(os.path.dirname(__file__), 'current_reminder_execution_test.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(flex_message, f, ensure_ascii=False, indent=2)
        print(f"   💾 結果保存: {os.path.basename(output_file)}")

    except Exception as e:
        print(f"❌ Flex Message作成エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_actual_reminder_execution()
    test_flex_message_creation()

    print("\n" + "=" * 70)
    print("🎯 現在のリマインダー実行状況テスト完了")
    print("=" * 70)
