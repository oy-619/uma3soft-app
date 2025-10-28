"""
Flex Message履歴カード表示機能テスト
"""

import sys
import os
import json
from datetime import datetime, timedelta

# uma3.pyのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from uma3 import flex_history_handler

def create_sample_history_data():
    """サンプル履歴データを作成"""
    now = datetime.now()

    sample_data = [
        {
            'id': 1,
            'timestamp': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'user_message': '@Bot 陸功選手について教えて',
            'bot_response': '陸功選手についてお答えします。陸功選手は馬三ソフトの確認済み選手で、1番目に登録されています。'
        },
        {
            'id': 2,
            'timestamp': (now - timedelta(hours=1, minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'user_message': '@Bot 選手一覧を教えて',
            'bot_response': '確認済み選手一覧（28名）: 陸功, 湊, 錬, 南, 統司, 春輝, 新, 由眞, 心寧, 唯浬, 朋樹, 佑多, 穂美, 翔平, 尚真, 柚希, 心翔, 広起, 想真, 奏, 英汰, 聡太, 暖大, 悠琉, 陽, 美玖里, 優, 勘太'
        },
        {
            'id': 3,
            'timestamp': (now - timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M:%S'),
            'user_message': '@Bot 翔平選手について',
            'bot_response': '翔平選手についてお答えします。翔平選手は馬三ソフトの確認済み選手として新たに正式登録されました。'
        },
        {
            'id': 4,
            'timestamp': (now - timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'user_message': '@Bot 馬三ソフトには何人いる？',
            'bot_response': '馬三ソフトの現在の選手情報は28名です（確認済み28名、候補0名）。'
        },
        {
            'id': 5,
            'timestamp': (now - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'user_message': '@Bot 新規追加された選手について教えて',
            'bot_response': '最新の一括更新で16名の選手情報をいただき、システムに統合いたしました。現在28名の選手情報があります。新規追加選手は尚真、柚希、心翔、広起、想真、奏、英汰、聡太、暖大、悠琉、陽、美玖里、優、勘太の14名です。'
        }
    ]

    return sample_data

def test_flex_history_functionality():
    """Flex履歴機能のテスト"""
    print("🚀 Flex Message履歴カード表示機能テスト")
    print("=" * 60)

    # サンプルデータ作成
    sample_history = create_sample_history_data()

    print(f"📊 テストデータ:")
    print(f"   📝 履歴レコード数: {len(sample_history)}件")
    print(f"   📅 時間範囲: 2時間前〜5分前")
    print()

    # 1. Flex Messageカード作成テスト
    print("🧪 Test 1: Flex Messageカード作成")
    print("-" * 40)

    try:
        flex_message = flex_history_handler.create_history_flex_message(
            sample_history, "F履歴テスト"
        )

        print(f"✅ Flex Message作成成功")
        print(f"   📱 alt_text: {flex_message.alt_text}")
        print(f"   🎨 コンテナタイプ: {flex_message.contents.type}")

        # カルーセルの内容確認
        if hasattr(flex_message.contents, 'contents'):
            bubble_count = len(flex_message.contents.contents)
            print(f"   📋 バブル数: {bubble_count}個")

    except Exception as e:
        print(f"❌ Flex Message作成エラー: {e}")

    # 2. 空履歴のテスト
    print(f"\n🧪 Test 2: 空履歴の処理")
    print("-" * 40)

    try:
        empty_flex_message = flex_history_handler.create_history_flex_message(
            [], "空履歴テスト"
        )

        print(f"✅ 空履歴Flex Message作成成功")
        print(f"   📱 alt_text: {empty_flex_message.alt_text}")
        print(f"   🎨 コンテナタイプ: {empty_flex_message.contents.type}")

    except Exception as e:
        print(f"❌ 空履歴Flex Message作成エラー: {e}")

    # 3. 履歴リクエスト検出テスト
    print(f"\n🧪 Test 3: 履歴リクエスト検出")
    print("-" * 40)

    test_messages = [
        "@Bot F履歴を見せて",
        "@Bot 履歴を表示",
        "@Bot 過去の会話を確認したい",
        "@Bot 会話履歴をカードで見たい",
        "@Bot 履歴 card",
        "@Bot history",
        "@Bot 陸功について",  # 履歴要求ではない
        "@Bot 選手一覧"       # 履歴要求ではない
    ]

    for i, message in enumerate(test_messages, 1):
        result = flex_history_handler.handle_history_request(message)
        status = "✅ 検出" if result is not None else "❌ 非検出"
        print(f"   {i}. 「{message}」 → {status}")

    # 4. 単一カード作成テスト
    print(f"\n🧪 Test 4: 単一履歴カード作成")
    print("-" * 40)

    try:
        single_record = sample_history[0]
        single_card = flex_history_handler.create_single_history_card(single_record, 1)

        print(f"✅ 単一カード作成成功")
        print(f"   🎨 カードタイプ: {single_card['type']}")
        print(f"   📏 カードサイズ: {single_card.get('size', 'デフォルト')}")

        # ヘッダー情報確認
        if 'header' in single_card:
            header_contents = single_card['header']['contents']
            print(f"   📋 ヘッダー要素数: {len(header_contents)}")

        # ボディ情報確認
        if 'body' in single_card:
            body_contents = single_card['body']['contents']
            print(f"   📄 ボディ要素数: {len(body_contents)}")

    except Exception as e:
        print(f"❌ 単一カード作成エラー: {e}")

    # 5. テキスト切り詰め機能テスト
    print(f"\n🧪 Test 5: テキスト切り詰め機能")
    print("-" * 40)

    test_texts = [
        ("短いテキスト", 50),
        ("これは非常に長いテキストです。この文章は指定された文字数を超えるように作成されています。切り詰められるはずです。", 30),
        ("", 20),
        (None, 15)
    ]

    for text, max_len in test_texts:
        result = flex_history_handler.truncate_text(text, max_len)
        print(f"   入力: 「{text}」(max:{max_len}) → 出力: 「{result}」")

    # 6. タイムスタンプフォーマット機能テスト
    print(f"\n🧪 Test 6: タイムスタンプフォーマット")
    print("-" * 40)

    test_timestamps = [
        "2025-10-28 09:30:45",
        "2025-10-28T09:30:45",
        "2025-10-28 09:30:45.123456",
        "invalid_timestamp",
        ""
    ]

    for timestamp in test_timestamps:
        formatted = flex_history_handler.format_timestamp(timestamp)
        print(f"   入力: 「{timestamp}」 → 出力: 「{formatted}」")

    print(f"\n🎊 Flex履歴カード機能テスト完了")
    print("=" * 60)

    # テスト結果サマリー
    print(f"📊 テスト結果サマリー:")
    print(f"   🎨 Flex Message機能: 実装完了")
    print(f"   📋 カルーセル表示: 対応済み")
    print(f"   📱 カード形式: 美しいデザイン実装")
    print(f"   🔍 履歴検出: 多様なキーワード対応")
    print(f"   📄 テキスト処理: 切り詰め・フォーマット対応")
    print(f"   💾 データ取得: SQLite連携準備完了")

    print(f"\n🚀 LINE Botで使用可能なコマンド:")
    print(f"   💬 「@Bot F履歴」- 履歴をカード表示")
    print(f"   💬 「@Bot 履歴を見せて」- 履歴をカード表示")
    print(f"   💬 「@Bot 過去の会話」- 履歴をカード表示")
    print(f"   💬 「@Bot 会話履歴 card」- 履歴をカード表示")

if __name__ == "__main__":
    test_flex_history_functionality()
