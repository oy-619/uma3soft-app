#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReminderFlexCustomizerの文面・デザインパターン詳細分析クラス
レイアウトの変化パターンや文言の使い分けを詳しく解析
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re

class ReminderDesignAnalyzer:
    """リマインダーFlexメッセージのデザインパターン分析クラス"""

    def __init__(self):
        """初期化"""
        try:
            from reminder_flex_customizer import ReminderFlexCustomizer
            from weather_flex_template import WeatherFlexTemplate

            self.customizer = ReminderFlexCustomizer()
            self.weather_template = WeatherFlexTemplate()
            print("✅ ReminderDesignAnalyzer初期化成功")
        except ImportError as e:
            print(f"❌ インポートエラー: {e}")
            raise

    def analyze_message_patterns(self) -> Dict:
        """メッセージパターンの詳細分析"""
        print("🔍 メッセージパターン詳細分析開始")

        # 日数と期限タイプの組み合わせパターンを作成
        test_patterns = [
            {"days_until": 0, "is_input_deadline": True, "name": "本日締切"},
            {"days_until": 0, "is_input_deadline": False, "name": "本日開催"},
            {"days_until": 1, "is_input_deadline": True, "name": "明日締切"},
            {"days_until": 1, "is_input_deadline": False, "name": "明日開催"},
            {"days_until": 3, "is_input_deadline": True, "name": "3日後締切"},
            {"days_until": 3, "is_input_deadline": False, "name": "3日後開催"},
            {"days_until": 7, "is_input_deadline": True, "name": "1週間後締切"},
            {"days_until": 7, "is_input_deadline": False, "name": "1週間後開催"},
        ]

        base_content = """テスト大会
場所：東京都テスト球場
時間：午後2時開始
持ち物：グローブ、バット
連絡先：テスト太郎"""

        pattern_analysis = {}

        for pattern in test_patterns:
            print(f"  📊 分析中: {pattern['name']}")

            # テストノート作成
            note = {
                "content": base_content,
                "date": datetime.now() + timedelta(days=pattern["days_until"]),
                "days_until": pattern["days_until"],
                "is_input_deadline": pattern["is_input_deadline"]
            }

            # モック天気データでFlex生成
            mock_weather = self._create_simple_weather_flex()
            flex_message = self.customizer.customize_weather_flex_for_reminder(mock_weather, note)

            # パターン分析
            analysis = self._analyze_single_pattern(flex_message, pattern)
            pattern_analysis[pattern['name']] = analysis

        return pattern_analysis

    def analyze_text_variations(self) -> Dict:
        """テキスト内容の変化パターン分析"""
        print("📝 テキスト変化パターン分析開始")

        variations = {}

        # 緊急度別のメッセージ分析
        urgency_levels = [
            {"days": 0, "deadline": True, "level": "最緊急"},
            {"days": 1, "deadline": True, "level": "緊急"},
            {"days": 3, "deadline": True, "level": "注意"},
            {"days": 7, "deadline": True, "level": "通常"},
            {"days": 0, "deadline": False, "level": "当日"},
            {"days": 1, "deadline": False, "level": "直前"}
        ]

        base_note = {
            "content": "テストイベント\n場所：テスト会場\n連絡先：テスト太郎",
            "date": datetime.now()
        }

        for urgency in urgency_levels:
            note = base_note.copy()
            note["days_until"] = urgency["days"]
            note["is_input_deadline"] = urgency["deadline"]

            mock_weather = self._create_simple_weather_flex()
            flex_message = self.customizer.customize_weather_flex_for_reminder(mock_weather, note)

            # テキスト抽出と分析
            texts = self._extract_all_texts(flex_message)
            variations[urgency["level"]] = {
                "header_message": self._find_header_message(texts),
                "main_message": self._find_main_message(texts),
                "urgency_indicators": self._find_urgency_indicators(texts),
                "footer_message": self._find_footer_message(texts)
            }

        return variations

    def analyze_color_scheme_patterns(self) -> Dict:
        """色使いパターンの分析"""
        print("🎨 色使いパターン分析開始")

        color_patterns = {}

        # 各緊急度での色使いを分析
        test_cases = [
            {"days_until": 0, "is_input_deadline": True, "case": "最緊急期限"},
            {"days_until": 1, "is_input_deadline": True, "case": "緊急期限"},
            {"days_until": 3, "is_input_deadline": True, "case": "通常期限"},
            {"days_until": 0, "is_input_deadline": False, "case": "当日開催"},
            {"days_until": 1, "is_input_deadline": False, "case": "明日開催"},
            {"days_until": 7, "is_input_deadline": False, "case": "予定案内"}
        ]

        for case in test_cases:
            note = {
                "content": "カラーテスト\n場所：テスト会場\n連絡先：テスト太郎",
                "date": datetime.now() + timedelta(days=case["days_until"]),
                "days_until": case["days_until"],
                "is_input_deadline": case["is_input_deadline"]
            }

            mock_weather = self._create_simple_weather_flex()
            flex_message = self.customizer.customize_weather_flex_for_reminder(mock_weather, note)

            colors = self._extract_color_scheme(flex_message)
            color_patterns[case["case"]] = colors

        return color_patterns

    def analyze_layout_structure_changes(self) -> Dict:
        """レイアウト構造の変化パターン分析"""
        print("🏗️ レイアウト構造分析開始")

        structure_patterns = {}

        # 異なるコンテンツ長での構造変化を分析
        content_variations = [
            {
                "type": "短文",
                "content": "短いイベント\n場所：A会場\n連絡先：太郎"
            },
            {
                "type": "標準",
                "content": """標準的なイベント
場所：東京都標準会場
時間：午後2時開始
持ち物：必要なもの一式
注意事項：雨天中止
連絡先：標準太郎"""
            },
            {
                "type": "長文",
                "content": """詳細なイベント情報
場所：東京都詳細情報テスト会場第一球場
開催時間：午後2時集合、2時30分受付、3時開始予定
持参物：ユニフォーム、グローブ、バット、飲み物、タオル、着替え
注意事項：雨天の場合は翌日同時刻に順延、駐車場利用不可
参加費：大人2000円、子供1000円（当日徴収）
その他：保険証のコピーを持参してください
連絡先：詳細情報管理担当者"""
            }
        ]

        for content_var in content_variations:
            note = {
                "content": content_var["content"],
                "date": datetime.now() + timedelta(days=3),
                "days_until": 3,
                "is_input_deadline": True
            }

            mock_weather = self._create_simple_weather_flex()
            flex_message = self.customizer.customize_weather_flex_for_reminder(mock_weather, note)

            structure = self._analyze_layout_structure(flex_message)
            structure_patterns[content_var["type"]] = structure

        return structure_patterns

    def generate_comparison_report(self) -> None:
        """比較分析レポートを生成"""
        print("\n" + "=" * 80)
        print("📋 ReminderFlexCustomizer 詳細デザイン分析レポート")
        print("=" * 80)

        # 各分析を実行
        message_patterns = self.analyze_message_patterns()
        text_variations = self.analyze_text_variations()
        color_patterns = self.analyze_color_scheme_patterns()
        layout_patterns = self.analyze_layout_structure_changes()

        # レポート出力
        self._display_message_pattern_report(message_patterns)
        self._display_text_variation_report(text_variations)
        self._display_color_pattern_report(color_patterns)
        self._display_layout_pattern_report(layout_patterns)

        # 総合レポートをファイルに保存
        comprehensive_report = {
            "generated_at": datetime.now().isoformat(),
            "analysis_results": {
                "message_patterns": message_patterns,
                "text_variations": text_variations,
                "color_patterns": color_patterns,
                "layout_patterns": layout_patterns
            },
            "summary": self._generate_summary_insights(message_patterns, text_variations, color_patterns, layout_patterns)
        }

        try:
            with open("comprehensive_design_analysis.json", 'w', encoding='utf-8') as f:
                json.dump(comprehensive_report, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n💾 詳細分析レポート保存: comprehensive_design_analysis.json")
        except Exception as e:
            print(f"\n⚠️ レポート保存エラー: {e}")

    # ヘルパーメソッド群
    def _create_simple_weather_flex(self) -> Dict:
        """シンプルな天気Flexを作成"""
        return {
            "type": "flex",
            "altText": "天気情報",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [{"type": "text", "text": "📍 東京都"}]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "🌡️ 気温"}]},
                                {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "22℃"}]}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "💧 湿度"}]},
                                {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "65%"}]}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "☔ 降水確率"}]},
                                {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "20%"}]}
                            ]
                        },
                        {"type": "text", "text": "💡 過ごしやすい天候です"}
                    ]
                }
            }
        }

    def _analyze_single_pattern(self, flex_message: Dict, pattern: Dict) -> Dict:
        """単一パターンの分析"""
        return {
            "altText": flex_message.get("altText", ""),
            "header_bg_color": self._get_header_bg_color(flex_message),
            "urgency_emoji": self._get_urgency_emoji(flex_message),
            "main_message_color": self._get_main_message_color(flex_message),
            "text_count": self._count_text_elements(flex_message),
            "pattern_info": pattern
        }

    def _extract_all_texts(self, flex_message: Dict) -> List[str]:
        """すべてのテキストを抽出"""
        texts = []

        def extract_recursive(obj):
            if isinstance(obj, dict):
                if obj.get("type") == "text":
                    texts.append(obj.get("text", ""))
                for value in obj.values():
                    extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)

        extract_recursive(flex_message)
        return texts

    def _find_header_message(self, texts: List[str]) -> str:
        """ヘッダーメッセージを特定"""
        for text in texts:
            if any(indicator in text for indicator in ["調整さん", "確認依頼", "🚨", "⏰", "📢", "📋"]):
                return text
        return texts[0] if texts else ""

    def _find_main_message(self, texts: List[str]) -> str:
        """メインメッセージを特定"""
        for text in texts:
            if any(keyword in text for keyword in ["参加・欠席", "開催予定", "期限が迫", "回答をお願い"]):
                return text
        return ""

    def _find_urgency_indicators(self, texts: List[str]) -> List[str]:
        """緊急度指標を抽出"""
        indicators = []
        urgency_keywords = ["緊急", "期限", "本日", "明日", "迫って", "お急ぎ"]

        for text in texts:
            if any(keyword in text for keyword in urgency_keywords):
                indicators.append(text)

        return indicators

    def _find_footer_message(self, texts: List[str]) -> str:
        """フッターメッセージを特定"""
        for text in texts:
            if "詳細は個別に" in text or "ご確認ください" in text:
                return text
        return ""

    def _extract_color_scheme(self, flex_message: Dict) -> Dict:
        """色スキームを抽出"""
        colors = {"header_bg": None, "text_colors": [], "bg_colors": []}

        def extract_colors(obj):
            if isinstance(obj, dict):
                if obj.get("backgroundColor"):
                    colors["bg_colors"].append(obj["backgroundColor"])
                if obj.get("color"):
                    colors["text_colors"].append(obj["color"])
                for value in obj.values():
                    extract_colors(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_colors(item)

        # ヘッダー背景色を特定
        try:
            header_bg = flex_message["contents"]["header"].get("backgroundColor")
            colors["header_bg"] = header_bg
        except:
            pass

        extract_colors(flex_message)
        return colors

    def _analyze_layout_structure(self, flex_message: Dict) -> Dict:
        """レイアウト構造を分析"""
        structure = {
            "total_sections": 0,
            "section_types": [],
            "nesting_depth": 0,
            "element_counts": {}
        }

        try:
            contents = flex_message["contents"]

            for section_name in ["header", "body", "footer"]:
                if section_name in contents:
                    structure["total_sections"] += 1
                    structure["section_types"].append(section_name)

                    # セクション内の要素数をカウント
                    element_count = self._count_elements_in_section(contents[section_name])
                    structure["element_counts"][section_name] = element_count

        except Exception as e:
            structure["error"] = str(e)

        return structure

    def _count_elements_in_section(self, section: Dict) -> int:
        """セクション内の要素数をカウント"""
        count = 0

        def count_recursive(obj):
            nonlocal count
            if isinstance(obj, dict):
                if obj.get("type") in ["text", "box", "separator"]:
                    count += 1
                for value in obj.values():
                    count_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_recursive(item)

        count_recursive(section)
        return count

    def _get_header_bg_color(self, flex_message: Dict) -> Optional[str]:
        """ヘッダー背景色を取得"""
        try:
            return flex_message["contents"]["header"].get("backgroundColor")
        except:
            return None

    def _get_urgency_emoji(self, flex_message: Dict) -> str:
        """緊急度絵文字を取得"""
        texts = self._extract_all_texts(flex_message)
        for text in texts:
            for emoji in ["🚨", "⚠️", "⏰", "📢", "🎯", "📅", "📋"]:
                if emoji in text:
                    return emoji
        return ""

    def _get_main_message_color(self, flex_message: Dict) -> Optional[str]:
        """メインメッセージの色を取得"""
        try:
            body = flex_message["contents"]["body"]
            # body内の最初のテキスト要素の色を取得
            return self._find_first_text_color(body)
        except:
            return None

    def _find_first_text_color(self, obj) -> Optional[str]:
        """最初のテキスト要素の色を見つける"""
        if isinstance(obj, dict):
            if obj.get("type") == "text" and obj.get("color"):
                return obj["color"]
            for value in obj.values():
                result = self._find_first_text_color(value)
                if result:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = self._find_first_text_color(item)
                if result:
                    return result
        return None

    def _count_text_elements(self, flex_message: Dict) -> int:
        """テキスト要素数をカウント"""
        count = 0

        def count_texts(obj):
            nonlocal count
            if isinstance(obj, dict):
                if obj.get("type") == "text":
                    count += 1
                for value in obj.values():
                    count_texts(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_texts(item)

        count_texts(flex_message)
        return count

    # レポート表示メソッド群
    def _display_message_pattern_report(self, patterns: Dict) -> None:
        """メッセージパターンレポート表示"""
        print("\n📊 メッセージパターン分析結果:")
        print("-" * 60)

        for pattern_name, analysis in patterns.items():
            print(f"\n🔸 {pattern_name}:")
            print(f"   altText: {analysis['altText']}")
            print(f"   ヘッダー背景色: {analysis['header_bg_color']}")
            print(f"   緊急度絵文字: {analysis['urgency_emoji']}")
            print(f"   テキスト要素数: {analysis['text_count']}")

    def _display_text_variation_report(self, variations: Dict) -> None:
        """テキスト変化レポート表示"""
        print("\n📝 テキスト変化パターン分析結果:")
        print("-" * 60)

        for level, analysis in variations.items():
            print(f"\n🔸 {level}レベル:")
            print(f"   ヘッダー: {analysis['header_message'][:40]}...")
            print(f"   メイン: {analysis['main_message'][:40]}...")
            print(f"   緊急指標数: {len(analysis['urgency_indicators'])}")

    def _display_color_pattern_report(self, patterns: Dict) -> None:
        """色パターンレポート表示"""
        print("\n🎨 色使いパターン分析結果:")
        print("-" * 60)

        for case, colors in patterns.items():
            print(f"\n🔸 {case}:")
            print(f"   ヘッダー背景: {colors['header_bg']}")
            print(f"   使用テキスト色数: {len(set(colors['text_colors']))}")
            print(f"   背景色数: {len(set(colors['bg_colors']))}")

    def _display_layout_pattern_report(self, patterns: Dict) -> None:
        """レイアウトパターンレポート表示"""
        print("\n🏗️ レイアウト構造分析結果:")
        print("-" * 60)

        for content_type, structure in patterns.items():
            print(f"\n🔸 {content_type}コンテンツ:")
            print(f"   セクション数: {structure['total_sections']}")
            print(f"   セクション構成: {', '.join(structure['section_types'])}")
            for section, count in structure['element_counts'].items():
                print(f"   {section}要素数: {count}")

    def _generate_summary_insights(self, messages, texts, colors, layouts) -> Dict:
        """サマリー洞察を生成"""
        return {
            "total_patterns_analyzed": len(messages),
            "color_variations": len(set([p['header_bg_color'] for p in messages.values() if p['header_bg_color']])),
            "text_element_range": {
                "min": min([p['text_count'] for p in messages.values()]),
                "max": max([p['text_count'] for p in messages.values()])
            },
            "common_urgency_indicators": ["🚨", "⚠️", "⏰", "📢", "🎯"],
            "layout_consistency": "構造は基本的に一貫している（header-body-footer）"
        }


def main():
    """メイン実行関数"""
    try:
        analyzer = ReminderDesignAnalyzer()
        analyzer.generate_comparison_report()
        print("\n🎉 詳細デザイン分析完了！")
    except Exception as e:
        print(f"❌ 分析実行エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
