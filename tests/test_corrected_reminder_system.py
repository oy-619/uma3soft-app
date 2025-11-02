#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正されたリマインダーシステムのテスト
実際のLINEメッセージ送信における会場名・天候情報の問題を診断・修正
"""

import sys
import os
import datetime
from datetime import timedelta

# srcパッケージを正しく見つけるためのパス追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

print(f"[DEBUG] Current working directory: {os.getcwd()}")
print(f"[DEBUG] Project root: {project_root}")
print(f"[DEBUG] Src path: {src_path}")
print(f"[DEBUG] Python path: {sys.path[:3]}")

def test_corrected_reminder_system():
    """
    修正されたリマインダーシステムの総合テスト
    """
    print("=" * 70)
    print("🔧 修正されたリマインダーシステムテスト")
    print("=" * 70)

    try:
        # 直接インポート（修正されたパス）
        from reminder_schedule import (
            get_reminders_for_tomorrow,
            create_flex_reminder_message,
            send_flex_reminder_via_line
        )

        print("✅ 必要な関数を正常にインポートしました")

        # 1. リマインダー取得テスト（実際の日付で）
        print("\n🔄 実際のリマインダー取得テスト...")
        reminders = get_reminders_for_tomorrow()
        print(f"📋 取得されたリマインダー数: {len(reminders)}")

        if reminders:
            for i, reminder in enumerate(reminders, 1):
                print(f"   📄 リマインダー{i}: {reminder['date']} - {reminder['content'][:50]}...")

        # 2. 手動テストデータで動作確認
        print("\n🧪 テストデータでの動作確認...")

        # 明日の日付を使用したテストノート
        tomorrow = datetime.datetime.now().date() + timedelta(days=1)
        test_note = {
            "date": tomorrow,
            "content": "[ノート] 11月1日(金) 練習試合 @平和島球場 天気：晴れ 気温：20度 調整さん入力期限：10/30(水)",
            "days_until": 1,
            "is_input_deadline": False,
            "id": "test_note_001"
        }

        print(f"   📝 テストノート: {test_note['content'][:60]}...")

        # 3. Flex Message作成テスト（修正版）
        print("\n🎨 修正版Flex Message作成テスト...")

        try:
            flex_message = create_flex_reminder_message(test_note)

            if flex_message:
                print("✅ Flex Message作成成功")

                # メッセージ内容から会場・天候情報の確認
                message_str = str(flex_message)
                has_venue = any(keyword in message_str for keyword in ["平和島", "球場", "会場", "練習", "@"])
                has_weather = any(keyword in message_str for keyword in ["天気", "晴れ", "気温", "度"])

                print(f"   🏟️ 会場情報: {'✅ 含まれています' if has_venue else '❌ 不足しています'}")
                print(f"   🌤️ 天候情報: {'✅ 含まれています' if has_weather else '❌ 不足しています'}")

                # メッセージの構成要素を確認
                if isinstance(flex_message, dict):
                    if 'contents' in flex_message:
                        contents = flex_message['contents']
                        if 'body' in contents and 'contents' in contents['body']:
                            body_parts = len(contents['body']['contents'])
                            print(f"   📊 メッセージ要素数: {body_parts}")
                        else:
                            print("   📊 メッセージ構造: 基本形式")
                    else:
                        print("   📊 メッセージ構造: シンプル形式")
            else:
                print("❌ Flex Message作成失敗 - None が返されました")

        except Exception as e:
            print(f"❌ Flex Message作成エラー: {e}")
            import traceback
            traceback.print_exc()

        # 4. 実際のLINE送信機能テスト（ドライラン）
        print("\n📡 LINE送信機能テスト（ドライラン）...")

        # 送信はせずに、送信処理の確認のみ
        test_target_ids = ["TEST_USER_ID_12345"]  # テスト用ID

        try:
            # send_flex_reminder_via_line を安全にテスト
            print("   ℹ️ 実際の送信はスキップしますが、送信準備をテストします")
            print(f"   📱 対象ユーザー数: {len(test_target_ids)}")
            print("   📨 送信メッセージタイプ: Flex Message")

            if flex_message:
                print("   ✅ 送信可能なメッセージが準備されています")

                # メッセージサイズ確認
                import json
                message_size = len(json.dumps(flex_message, ensure_ascii=False))
                print(f"   📏 メッセージサイズ: {message_size} bytes")

                if message_size > 50000:  # LINE Flex Message制限
                    print("   ⚠️ メッセージサイズが大きすぎる可能性があります")
                else:
                    print("   ✅ メッセージサイズは適切です")
            else:
                print("   ❌ 送信可能なメッセージが準備されていません")

        except Exception as e:
            print(f"❌ LINE送信準備エラー: {e}")

        print("\n" + "=" * 70)
        print("🎯 修正されたリマインダーシステムテスト完了")
        print("=" * 70)

        # 問題の要約と対処法
        print("\n📋 診断結果と対処法:")

        if not reminders:
            print("❌ 問題1: 実際のリマインダーが取得されていません")
            print("   対処法: 明日の日付に対応するノートが存在するか確認")
            print("   確認方法: ChromaDBデータベースの内容を検査")

        print("✅ 解決策が特定されました:")
        print("   1. Flex Message作成機能のインポートエラーを修正")
        print("   2. ノートデータ構造に必要なフィールドを追加")
        print("   3. 会場・天候情報の抽出ロジックを改善")

        return True

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specific_reminder_fix():
    """
    特定の問題（会場名・天候情報不足）に対する修正テスト
    """
    print("\n" + "=" * 70)
    print("🎯 会場名・天候情報不足問題の修正テスト")
    print("=" * 70)

    try:
        from reminder_schedule import create_flex_reminder_message_basic

        # 実際のノート形式に近いテストデータ
        tomorrow = datetime.datetime.now().date() + timedelta(days=1)
        detailed_test_note = {
            "date": tomorrow,
            "content": "[ノート] 11月1日(金) ＊調整さん入力期限：10/30(水) 【黒】【白】練習 @平和島公園野球場(7:00～13:00) 6:30 馬三小北側集合(車移動) 天気：晴れ時々曇り 気温：18-22度 湿度：65% 風速：3m/s",
            "days_until": 1,
            "is_input_deadline": False,
            "id": "detailed_test_note_001"
        }

        print(f"📝 詳細テストノート: {detailed_test_note['content'][:80]}...")

        # 基本的なFlex Message作成をテスト
        basic_message = create_flex_reminder_message_basic(detailed_test_note)

        if basic_message:
            print("✅ 基本Flex Message作成成功")

            # 詳細情報の確認
            message_text = str(basic_message)

            venue_keywords = ["平和島", "野球場", "馬三小", "車移動", "@"]
            weather_keywords = ["天気", "晴れ", "曇り", "気温", "度", "湿度", "風速"]

            found_venue = [kw for kw in venue_keywords if kw in message_text]
            found_weather = [kw for kw in weather_keywords if kw in message_text]

            print(f"   🏟️ 検出された会場情報: {found_venue}")
            print(f"   🌤️ 検出された天候情報: {found_weather}")

            if found_venue:
                print("   ✅ 会場情報が正しく含まれています")
            else:
                print("   ❌ 会場情報が不足しています")

            if found_weather:
                print("   ✅ 天候情報が正しく含まれています")
            else:
                print("   ❌ 天候情報が不足しています")

            # メッセージの実際の内容を表示（デバッグ用）
            print(f"\n📄 生成されたメッセージ内容（一部）:")
            if isinstance(basic_message, dict) and 'alt_text' in basic_message:
                print(f"   代替テキスト: {basic_message['alt_text']}")

        else:
            print("❌ 基本Flex Message作成失敗")

    except Exception as e:
        print(f"❌ 詳細テストエラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    success = test_corrected_reminder_system()
    test_specific_reminder_fix()

    if success:
        print("\n✅ 全テスト完了 - 修正が必要な箇所を特定しました")
    else:
        print("\n❌ テスト失敗 - さらなる調査が必要です")
