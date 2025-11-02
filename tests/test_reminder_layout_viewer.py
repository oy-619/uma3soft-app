#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReminderFlexCustomizerのレイアウト・文面確認テストクラス
様々なシナリオでのFlex Messageの表示内容を詳しく確認
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ReminderLayoutViewer:
    """リマインダーFlexメッセージのレイアウト確認用テストクラス"""

    def __init__(self):
        """初期化"""
        try:
            from reminder_flex_customizer import ReminderFlexCustomizer
            from weather_flex_template import WeatherFlexTemplate

            self.customizer = ReminderFlexCustomizer()
            self.weather_template = WeatherFlexTemplate()
            print("✅ ReminderLayoutViewer初期化成功")
        except ImportError as e:
            print(f"❌ インポートエラー: {e}")
            raise

    def create_test_scenarios(self) -> List[Dict]:
        """様々なテストシナリオを作成"""
        base_date = datetime.now()

        scenarios = [
            {
                "name": "本日締切（緊急）",
                "note": {
                    "content": """東京都小学生男子ソフトボール秋季大会
場所：東京都立川市総合運動場
集合時間：17:45（試合開始18:00）
持ち物：グローブ、バット、飲み物、タオル
注意事項：雨天の場合は中止
連絡先：田中太郎""",
                    "date": base_date,
                    "days_until": 0,
                    "is_input_deadline": True
                },
                "description": "本日が参加回答期限の緊急案件"
            },
            {
                "name": "明日締切（警告）",
                "note": {
                    "content": """神奈川県少年野球リーグ戦
会場：横浜スタジアム第2球場
時間：午前9時開始
持参物：ユニフォーム、スパイク、弁当
費用：参加費2000円（当日徴収）
担当：佐藤花子""",
                    "date": base_date + timedelta(days=1),
                    "days_until": 1,
                    "is_input_deadline": True
                },
                "description": "明日が期限の参加回答依頼"
            },
            {
                "name": "3日後締切（通常）",
                "note": {
                    "content": """千葉県夏季大会予選
開催地：千葉市美浜区海浜公園野球場
集合：午後2時30分
試合開始：午後3時
雨天時：翌日同時刻に順延
問い合わせ：山田次郎""",
                    "date": base_date + timedelta(days=3),
                    "days_until": 3,
                    "is_input_deadline": True
                },
                "description": "3日後期限の余裕のある回答依頼"
            },
            {
                "name": "本日開催（当日）",
                "note": {
                    "content": """埼玉県親善試合
場所：さいたま市営球場A面
時間：10:00〜15:00
持ち物：ユニフォーム、グローブ、昼食
注意：駐車場は先着順
連絡先：鈴木一郎""",
                    "date": base_date,
                    "days_until": 0,
                    "is_input_deadline": False
                },
                "description": "本日開催のイベント最終確認"
            },
            {
                "name": "明日開催（直前）",
                "note": {
                    "content": """大阪府秋季トーナメント
会場：大阪ドーム第3グラウンド
開始：朝8時受付、9時試合開始
持参：ユニフォーム、道具一式、保険証
駐車場：有料（1日500円）
主催：大阪野球連盟""",
                    "date": base_date + timedelta(days=1),
                    "days_until": 1,
                    "is_input_deadline": False
                },
                "description": "明日開催の準備確認"
            },
            {
                "name": "1週間後開催",
                "note": {
                    "content": """愛知県選手権大会
場所：名古屋ドーム練習場
日時：来週土曜日 午後1時〜
参加費：1人1500円
締切：今週金曜日まで
連絡：名古屋野球クラブ事務局""",
                    "date": base_date + timedelta(days=7),
                    "days_until": 7,
                    "is_input_deadline": False
                },
                "description": "1週間後開催の余裕のある案内"
            },
            {
                "name": "調整さんURL含む（除外テスト）",
                "note": {
                    "content": """福岡県春季大会
場所：福岡ドーム第2球場
調整さんURL: https://chouseisan.com/s?h=example123
↑必ずご入力ください
時間：午前10時集合
持ち物：ユニフォーム、グローブ
連絡先：福岡太郎""",
                    "date": base_date + timedelta(days=5),
                    "days_until": 5,
                    "is_input_deadline": True
                },
                "description": "調整さん関連情報の除外機能テスト"
            }
        ]

        return scenarios

    def generate_weather_flex(self, location: str = "東京都") -> Dict:
        """天気Flexメッセージを生成"""
        try:
            return self.weather_template.create_current_weather_flex(location)
        except Exception as e:
            print(f"⚠️ 天気Flex生成エラー: {e}")
            # モック天気データを使用
            return self._create_mock_weather_flex(location)

    def _create_mock_weather_flex(self, location: str) -> Dict:
        """モック天気Flexを作成"""
        return {
            "type": "flex",
            "altText": f"{location}の天気情報",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"📍 {location}",
                            "size": "lg",
                            "weight": "bold"
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "🌡️ 気温",
                                            "size": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "22℃",
                                            "size": "sm",
                                            "weight": "bold"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "💧 湿度",
                                            "size": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "65%",
                                            "size": "sm",
                                            "weight": "bold"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "☔ 降水確率",
                                            "size": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "20%",
                                            "size": "sm",
                                            "weight": "bold"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "text": "💡 過ごしやすい天候です。軽い上着があると良いでしょう。",
                            "size": "xs",
                            "wrap": True,
                            "margin": "md"
                        }
                    ]
                }
            }
        }

    def run_layout_test(self, save_files: bool = True) -> None:
        """レイアウトテストを実行"""
        print("=" * 80)
        print("🎨 ReminderFlexCustomizer レイアウト・文面確認テスト")
        print("=" * 80)

        scenarios = self.create_test_scenarios()
        results = []

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📋 シナリオ {i}: {scenario['name']}")
            print(f"📝 説明: {scenario['description']}")
            print("-" * 60)

            try:
                # 天気情報を生成
                note = scenario['note']
                location = self._extract_location_for_weather(note['content'])
                weather_flex = self.generate_weather_flex(location)

                # リマインダーFlexを生成
                reminder_flex = self.customizer.customize_weather_flex_for_reminder(
                    weather_flex, note
                )

                # レイアウト情報を解析
                layout_analysis = self._analyze_flex_layout(reminder_flex)

                # 文面情報を抽出
                text_content = self._extract_text_content(reminder_flex)

                # 結果を表示
                self._display_scenario_result(scenario, layout_analysis, text_content)

                # 結果を保存用に記録
                result = {
                    "scenario": scenario,
                    "layout_analysis": layout_analysis,
                    "text_content": text_content,
                    "flex_message": reminder_flex
                }
                results.append(result)

                # ファイル保存
                if save_files:
                    filename = f"layout_test_{i}_{scenario['name'].replace('（', '_').replace('）', '')}.json"
                    self._save_flex_to_file(reminder_flex, filename)
                    print(f"💾 保存ファイル: {filename}")

            except Exception as e:
                print(f"❌ エラー発生: {e}")
                import traceback
                traceback.print_exc()

        # 総合分析レポート
        self._generate_comprehensive_report(results, save_files)

        print("\n" + "=" * 80)
        print("🎉 レイアウトテスト完了！")
        print("=" * 80)

    def _extract_location_for_weather(self, content: str) -> str:
        """イベント内容から天気取得用の場所を抽出"""
        import re

        # 都道府県パターンを検索
        prefecture_patterns = [
            r'(東京都)', r'(神奈川県)', r'(千葉県)', r'(埼玉県)',
            r'(大阪府)', r'(愛知県)', r'(福岡県)', r'(北海道)'
        ]

        for pattern in prefecture_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

        return "東京都"  # デフォルト

    def _analyze_flex_layout(self, flex_message: Dict) -> Dict:
        """Flexメッセージのレイアウトを分析"""
        analysis = {
            "structure": {
                "type": flex_message.get("type"),
                "altText": flex_message.get("altText"),
                "bubble_size": None,
                "sections": []
            },
            "colors": [],
            "fonts": [],
            "spacing": []
        }

        try:
            contents = flex_message.get("contents", {})
            if contents.get("size"):
                analysis["structure"]["bubble_size"] = contents["size"]

            # ヘッダー分析
            if "header" in contents:
                header_info = self._analyze_section(contents["header"], "header")
                analysis["structure"]["sections"].append(header_info)

            # ボディ分析
            if "body" in contents:
                body_info = self._analyze_section(contents["body"], "body")
                analysis["structure"]["sections"].append(body_info)

            # フッター分析
            if "footer" in contents:
                footer_info = self._analyze_section(contents["footer"], "footer")
                analysis["structure"]["sections"].append(footer_info)

        except Exception as e:
            analysis["error"] = str(e)

        return analysis

    def _analyze_section(self, section: Dict, section_name: str) -> Dict:
        """セクションを分析"""
        info = {
            "name": section_name,
            "layout": section.get("layout"),
            "background_color": section.get("backgroundColor"),
            "padding": section.get("paddingAll"),
            "elements_count": 0,
            "text_elements": []
        }

        def count_elements(obj):
            if isinstance(obj, dict):
                if obj.get("type") == "text":
                    info["text_elements"].append({
                        "text": obj.get("text", "")[:50] + "...",
                        "size": obj.get("size"),
                        "color": obj.get("color"),
                        "weight": obj.get("weight")
                    })
                    info["elements_count"] += 1

                for value in obj.values():
                    if isinstance(value, (list, dict)):
                        count_elements(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_elements(item)

        count_elements(section)
        return info

    def _extract_text_content(self, flex_message: Dict) -> Dict:
        """Flexメッセージからテキスト内容を抽出"""
        text_content = {
            "header_texts": [],
            "body_texts": [],
            "footer_texts": [],
            "all_texts": []
        }

        def extract_texts(obj, section_key=""):
            if isinstance(obj, dict):
                if obj.get("type") == "text":
                    text = obj.get("text", "")
                    text_info = {
                        "text": text,
                        "section": section_key,
                        "size": obj.get("size"),
                        "color": obj.get("color"),
                        "weight": obj.get("weight"),
                        "align": obj.get("align")
                    }

                    text_content["all_texts"].append(text_info)

                    if section_key == "header":
                        text_content["header_texts"].append(text_info)
                    elif section_key == "body":
                        text_content["body_texts"].append(text_info)
                    elif section_key == "footer":
                        text_content["footer_texts"].append(text_info)

                for key, value in obj.items():
                    new_section = section_key if section_key else key
                    extract_texts(value, new_section)

            elif isinstance(obj, list):
                for item in obj:
                    extract_texts(item, section_key)

        try:
            contents = flex_message.get("contents", {})
            if "header" in contents:
                extract_texts(contents["header"], "header")
            if "body" in contents:
                extract_texts(contents["body"], "body")
            if "footer" in contents:
                extract_texts(contents["footer"], "footer")
        except Exception as e:
            text_content["error"] = str(e)

        return text_content

    def _display_scenario_result(self, scenario: Dict, layout: Dict, texts: Dict) -> None:
        """シナリオ結果を表示"""
        note = scenario['note']

        print(f"📊 基本情報:")
        print(f"   日付: {note['date'].strftime('%Y年%m月%d日')}")
        print(f"   残り日数: {note['days_until']}日")
        print(f"   入力期限: {'はい' if note['is_input_deadline'] else 'いいえ'}")

        print(f"\n🎨 レイアウト構造:")
        print(f"   バブルサイズ: {layout['structure'].get('bubble_size', 'デフォルト')}")
        print(f"   altText: {layout['structure'].get('altText', 'なし')}")

        for section in layout['structure']['sections']:
            print(f"   📍 {section['name'].upper()}:")
            print(f"      レイアウト: {section['layout']}")
            print(f"      背景色: {section.get('background_color', 'なし')}")
            print(f"      要素数: {section['elements_count']}")

        print(f"\n📝 主要テキスト内容:")

        # ヘッダーテキスト
        if texts['header_texts']:
            print("   🔸 ヘッダー:")
            for text in texts['header_texts'][:2]:  # 最初の2つだけ表示
                print(f"      ・{text['text'][:40]}{'...' if len(text['text']) > 40 else ''}")

        # ボディの重要テキスト（緊急度メッセージなど）
        if texts['body_texts']:
            print("   🔸 メインメッセージ:")
            important_texts = [t for t in texts['body_texts']
                             if any(keyword in t['text'] for keyword in
                                   ['参加・欠席', '開催予定', '確認', '期限', '本日', '明日'])]
            for text in important_texts[:3]:  # 最初の3つだけ表示
                print(f"      ・{text['text'][:40]}{'...' if len(text['text']) > 40 else ''}")

        # フッターテキスト
        if texts['footer_texts']:
            print("   🔸 フッター:")
            for text in texts['footer_texts']:
                print(f"      ・{text['text'][:40]}{'...' if len(text['text']) > 40 else ''}")

        print()

    def _save_flex_to_file(self, flex_message: Dict, filename: str) -> None:
        """FlexメッセージをJSONファイルに保存"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(flex_message, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ ファイル保存エラー: {e}")

    def _generate_comprehensive_report(self, results: List[Dict], save_file: bool = True) -> None:
        """総合分析レポートを生成"""
        print("\n" + "=" * 80)
        print("📊 総合分析レポート")
        print("=" * 80)

        # シナリオ別サマリー
        print("\n🎯 シナリオ別特徴:")
        for i, result in enumerate(results, 1):
            scenario = result['scenario']
            layout = result['layout_analysis']

            urgency_level = "🚨 緊急" if scenario['note']['days_until'] == 0 and scenario['note']['is_input_deadline'] else \
                          "⚠️ 警告" if scenario['note']['days_until'] == 1 and scenario['note']['is_input_deadline'] else \
                          "📅 通常"

            section_count = len(layout['structure']['sections'])

            print(f"   {i}. {scenario['name']} [{urgency_level}]")
            print(f"      セクション数: {section_count}, 要素数: {sum(s['elements_count'] for s in layout['structure']['sections'])}")

        # 使用されている色分析
        print("\n🎨 使用色パターン分析:")
        all_colors = set()
        color_usage = {}

        for result in results:
            for section in result['layout_analysis']['structure']['sections']:
                if section.get('background_color'):
                    all_colors.add(section['background_color'])
                for text_elem in section.get('text_elements', []):
                    if text_elem.get('color'):
                        color = text_elem['color']
                        all_colors.add(color)
                        color_usage[color] = color_usage.get(color, 0) + 1

        print(f"   使用色数: {len(all_colors)}色")
        for color, count in sorted(color_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   ・{color}: {count}回使用")

        # メッセージパターン分析
        print("\n💬 メッセージパターン分析:")
        message_patterns = {
            "緊急系": 0,
            "確認系": 0,
            "案内系": 0,
            "天候系": 0
        }

        for result in results:
            all_text = " ".join([t['text'] for t in result['text_content']['all_texts']])

            if any(word in all_text for word in ["緊急", "期限が迫", "本日"]):
                message_patterns["緊急系"] += 1
            if any(word in all_text for word in ["確認", "回答", "参加可否"]):
                message_patterns["確認系"] += 1
            if any(word in all_text for word in ["開催", "予定", "案内"]):
                message_patterns["案内系"] += 1
            if any(word in all_text for word in ["天候", "気温", "降水"]):
                message_patterns["天候系"] += 1

        for pattern, count in message_patterns.items():
            print(f"   ・{pattern}メッセージ: {count}件")

        # レポートファイル保存
        if save_file:
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "total_scenarios": len(results),
                "color_analysis": {
                    "total_colors": len(all_colors),
                    "color_usage": color_usage
                },
                "message_patterns": message_patterns,
                "detailed_results": results
            }

            try:
                with open("layout_analysis_report.json", 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
                print(f"\n💾 詳細レポート: layout_analysis_report.json")
            except Exception as e:
                print(f"\n⚠️ レポート保存エラー: {e}")


def main():
    """メイン実行関数"""
    try:
        viewer = ReminderLayoutViewer()
        viewer.run_layout_test(save_files=True)
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
