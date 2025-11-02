#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flex Message用のリマインダー作成機能
"""

def create_flex_reminder_message(note):
    """
    Flex Message形式のリマインダーメッセージを作成する

    Args:
        note (dict): ノート情報

    Returns:
        dict: Flex Message形式のメッセージデータ
    """
    days_until = note["days_until"]
    is_input_deadline = note.get("is_input_deadline", False)
    date_info = note["date"]

    # 日付を日本語形式でフォーマット
    formatted_date = date_info.strftime("%Y年%m月%d日")
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    weekday = weekdays[date_info.weekday()]
    date_with_weekday = f"{formatted_date}({weekday})"

    # タイトルとカラーを決定
    if is_input_deadline:
        if days_until == 0:
            title = "⚠️ 入力期限（本日）"
            color = "#FF6B6B"  # 赤色
            urgency = "本日期限"
        elif days_until == 1:
            title = "⏰ 入力期限（明日）"
            color = "#FFA726"  # オレンジ色
            urgency = "明日期限"
        else:
            title = f"📅 入力期限（{days_until}日後）"
            color = "#42A5F5"  # 青色
            urgency = f"{days_until}日後期限"
    else:
        if days_until == 0:
            title = "🎯 イベント開催（本日）"
            color = "#FF6B6B"  # 赤色
            urgency = "本日開催"
        elif days_until == 1:
            title = "⏰ イベント開催（明日）"
            color = "#FFA726"  # オレンジ色
            urgency = "明日開催"
        elif days_until == 2:
            title = "📅 イベント開催（明後日）"
            color = "#66BB6A"  # 緑色
            urgency = "明後日開催"
        else:
            title = f"📅 イベント開催（{days_until}日後）"
            color = "#42A5F5"  # 青色
            urgency = f"{days_until}日後開催"

    # イベント内容を整理（最初の2行を取得）
    content_lines = note['content'].split('\n')
    main_content = content_lines[0] if content_lines else "詳細未定"
    sub_content = content_lines[1] if len(content_lines) > 1 else ""

    # Flex Message JSON構造
    flex_message = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": title,
                    "weight": "bold",
                    "size": "md",
                    "color": "#FFFFFF"
                }
            ],
            "backgroundColor": color,
            "paddingAll": "15px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "📅 日時",
                            "size": "sm",
                            "color": "#666666",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": date_with_weekday,
                            "size": "lg",
                            "weight": "bold",
                            "color": color,
                            "margin": "xs"
                        }
                    ],
                    "margin": "none"
                },
                {
                    "type": "separator",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "📋 内容",
                            "size": "sm",
                            "color": "#666666",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": main_content,
                            "size": "md",
                            "wrap": True,
                            "margin": "xs"
                        }
                    ],
                    "margin": "md"
                }
            ],
            "paddingAll": "15px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": urgency,
                            "size": "sm",
                            "color": color,
                            "weight": "bold",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": "UMA3リマインダー",
                            "size": "xs",
                            "color": "#999999",
                            "align": "end",
                            "flex": 1
                        }
                    ]
                }
            ],
            "paddingAll": "10px"
        }
    }

    # サブコンテンツがある場合は追加
    if sub_content:
        flex_message["body"]["contents"].append({
            "type": "text",
            "text": sub_content,
            "size": "sm",
            "color": "#666666",
            "wrap": True,
            "margin": "sm"
        })

    return flex_message


def create_flex_reminder_carousel(notes):
    """
    複数のリマインダーをCarousel形式のFlex Messageで作成する

    Args:
        notes (list): ノートリスト

    Returns:
        dict: Carousel形式のFlex Message
    """
    if not notes:
        return None

    # 最大10件まで（LINEの制限）
    notes_to_show = notes[:10]

    bubbles = []
    for note in notes_to_show:
        bubble = create_flex_reminder_message(note)
        bubbles.append(bubble)

    carousel_message = {
        "type": "carousel",
        "contents": bubbles
    }

    return carousel_message


# テスト用関数
def test_flex_message_creation():
    """
    Flex Messageの作成テスト
    """
    from datetime import datetime, timedelta

    today = datetime.now().date()

    # テスト用のノートデータ
    test_notes = [
        {
            "date": today + timedelta(days=1),
            "days_until": 1,
            "content": "野球練習試合 vs Aチーム\n場所：公園グラウンド\n時間：13:00-17:00",
            "is_input_deadline": False
        },
        {
            "date": today + timedelta(days=1),
            "days_until": 1,
            "content": "出欠確認の締切\n来週の遠征について",
            "is_input_deadline": True
        },
        {
            "date": today,
            "days_until": 0,
            "content": "今日の試合 vs Bチーム\n場所：市営球場",
            "is_input_deadline": False
        }
    ]

    print("=== Flex Message作成テスト ===")

    # 単一メッセージのテスト
    for i, note in enumerate(test_notes, 1):
        print(f"\n--- テスト {i}: {note['content'][:20]}... ---")
        flex_msg = create_flex_reminder_message(note)
        print(f"✅ Flex Message作成完了")
        print(f"📊 タイプ: {flex_msg['type']}")
        print(f"🎨 ヘッダー色: {flex_msg['header']['backgroundColor']}")
        print(f"📝 タイトル: {flex_msg['header']['contents'][0]['text']}")

    # カルーセルメッセージのテスト
    print(f"\n--- カルーセルメッセージテスト ---")
    carousel_msg = create_flex_reminder_carousel(test_notes)
    print(f"✅ Carousel作成完了")
    print(f"📊 タイプ: {carousel_msg['type']}")
    print(f"🎠 バブル数: {len(carousel_msg['contents'])}")

    return flex_msg, carousel_msg


if __name__ == "__main__":
    test_flex_message_creation()
