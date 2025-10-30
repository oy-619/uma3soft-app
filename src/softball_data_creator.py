#!/usr/bin/env python3
"""
ソフトボールチーム学習データ作成モジュール

トーク履歴からソフトボール関連の情報を抽出し、
機械学習用の構造化データを生成する
"""

import os
import re
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd

@dataclass
class SoftballData:
    """ソフトボール関連データの構造"""
    timestamp: str
    user: str
    category: str  # 練習、試合、戦術、選手情報、スケジュール等
    content: str
    players_mentioned: List[str]
    keywords: List[str]
    metadata: Dict

class SoftballDataExtractor:
    """ソフトボール学習データ抽出クラス"""

    def __init__(self):
        """初期化"""
        # 確認済み選手（28名）
        self.confirmed_players = [
            "陸功", "湊", "錬", "南", "統司", "春輝", "新", "由眞", "心寧", "唯浬",
            "朋樹", "佑多", "穂美", "翔平", "尚真", "柚希", "心翔", "広起", "想真",
            "奏", "英汰", "聡太", "暖大", "悠琉", "陽", "美玖里", "優", "勘太"
        ]

        # ソフトボール関連キーワード
        self.softball_keywords = {
            "練習": ["練習", "トレーニング", "ランニング", "キャッチボール", "バッティング",
                   "守備", "ピッチング", "フィールディング", "基礎練習", "実戦練習"],
            "試合": ["試合", "ゲーム", "対戦", "リーグ戦", "トーナメント", "公式戦",
                   "練習試合", "県大会", "地区大会", "決勝", "準決勝"],
            "戦術": ["戦術", "作戦", "フォーメーション", "打順", "守備位置", "シフト",
                   "バント", "盗塁", "送りバント", "スクイズ", "代打", "代走"],
            "スケジュール": ["日程", "スケジュール", "予定", "時間", "集合", "解散",
                          "遅刻", "欠席", "参加", "不参加", "時間変更"],
            "成績": ["スコア", "得点", "失点", "勝利", "敗北", "引き分け", "打率",
                   "防御率", "エラー", "ヒット", "ホームラン", "三振"],
            "コンディション": ["怪我", "体調", "疲労", "回復", "リハビリ", "メンテナンス",
                           "ストレッチ", "アイシング", "テーピング"],
            "道具": ["グローブ", "バット", "ボール", "ヘルメット", "ユニフォーム",
                   "スパイク", "道具", "用具", "メンテナンス"],
            "感謝・応援": ["ありがとう", "感謝", "お疲れ様", "頑張って", "応援",
                        "励まし", "サポート", "チームワーク"]
        }

        # 時間・日付関連パターン
        self.time_patterns = [
            r'\d{1,2}:\d{2}',  # 14:30
            r'\d{1,2}時\d{0,2}分?',  # 14時30分
            r'午前|午後',
            r'\d{1,2}月\d{1,2}日',  # 10月22日
            r'今日|明日|昨日|来週|今週'
        ]

    def extract_players_from_text(self, text: str) -> List[str]:
        """テキストから選手名を抽出"""
        mentioned_players = []
        for player in self.confirmed_players:
            if player in text:
                mentioned_players.append(player)
        return mentioned_players

    def categorize_message(self, text: str) -> str:
        """メッセージのカテゴリを判定"""
        text_lower = text.lower()

        # カテゴリ別のスコア計算
        category_scores = {}
        for category, keywords in self.softball_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score

        # 最高スコアのカテゴリを返す
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]

        # デフォルトカテゴリ
        return "その他"

    def extract_keywords(self, text: str, category: str) -> List[str]:
        """テキストからキーワードを抽出"""
        keywords = []

        # カテゴリ別キーワードの抽出
        if category in self.softball_keywords:
            for keyword in self.softball_keywords[category]:
                if keyword in text:
                    keywords.append(keyword)

        # 時間・日付の抽出
        for pattern in self.time_patterns:
            matches = re.findall(pattern, text)
            keywords.extend(matches)

        return list(set(keywords))  # 重複除去

    def extract_metadata(self, text: str, user: str, timestamp: str) -> Dict:
        """メタデータの抽出"""
        metadata = {
            "message_length": len(text),
            "has_question": "？" in text or "?" in text,
            "has_exclamation": "！" in text or "!" in text,
            "has_emoji": bool(re.search(r'[😀-🙏]', text)),
            "word_count": len(text.split()),
            "is_weekend": self._is_weekend_from_timestamp(timestamp),
            "hour": self._extract_hour_from_timestamp(timestamp)
        }
        return metadata

    def _is_weekend_from_timestamp(self, timestamp: str) -> bool:
        """タイムスタンプから週末かどうか判定"""
        try:
            # タイムスタンプの解析を試行
            if "(" in timestamp and ")" in timestamp:
                day_match = re.search(r'\(([月火水木金土日])\)', timestamp)
                if day_match:
                    day = day_match.group(1)
                    return day in ['土', '日']
        except:
            pass
        return False

    def _extract_hour_from_timestamp(self, timestamp: str) -> Optional[int]:
        """タイムスタンプから時間を抽出"""
        try:
            time_match = re.search(r'(\d{1,2}):\d{2}', timestamp)
            if time_match:
                return int(time_match.group(1))
        except:
            pass
        return None

def extract_softball_data_from_chromadb(persist_directory: str) -> List[SoftballData]:
    """ChromaDBからソフトボール学習データを抽出"""

    extractor = SoftballDataExtractor()
    softball_data = []

    # ChromaDBに接続
    chroma_db_file = os.path.join(persist_directory, "chroma.sqlite3")

    if not os.path.exists(chroma_db_file):
        print(f"❌ ChromaDBファイルが見つかりません: {chroma_db_file}")
        return []

    try:
        conn = sqlite3.connect(chroma_db_file)
        cursor = conn.cursor()

        # documentsテーブルからデータを取得
        # ChromaDBの実際のテーブル構造に合わせて調整
        cursor.execute("""
            SELECT DISTINCT c0 as document
            FROM embedding_fulltext_search_content
            ORDER BY rowid DESC
        """)

        documents = cursor.fetchall()
        print(f"📊 取得されたドキュメント数: {len(documents)}")

        # メタデータの取得も試行
        cursor.execute("""
            SELECT id, key, string_value
            FROM embedding_metadata
            WHERE key IN ('user', 'timestamp', 'message_type')
        """)

        metadata_records = cursor.fetchall()
        metadata_dict = {}

        for record in metadata_records:
            doc_id, key, value = record
            if doc_id not in metadata_dict:
                metadata_dict[doc_id] = {}
            metadata_dict[doc_id][key] = value

        print(f"📊 メタデータレコード数: {len(metadata_records)}")

        # 各ドキュメントを処理
        for i, (document,) in enumerate(documents):
            if not document or not document.strip():
                continue

            # メタデータを取得（可能な場合）
            doc_metadata = metadata_dict.get(i, {})
            user = doc_metadata.get('user', 'unknown')
            timestamp = doc_metadata.get('timestamp', 'unknown')

            # ソフトボール関連の判定
            category = extractor.categorize_message(document)

            # ソフトボール関連でない場合はスキップ
            if category == "その他":
                # 選手名が含まれているかチェック
                players = extractor.extract_players_from_text(document)
                if not players:
                    continue

            # データ抽出
            players = extractor.extract_players_from_text(document)
            keywords = extractor.extract_keywords(document, category)
            metadata = extractor.extract_metadata(document, user, timestamp)

            # SoftballDataオブジェクトを作成
            softball_entry = SoftballData(
                timestamp=timestamp,
                user=user,
                category=category,
                content=document,
                players_mentioned=players,
                keywords=keywords,
                metadata=metadata
            )

            softball_data.append(softball_entry)

            # 進捗表示
            if (i + 1) % 100 == 0:
                print(f"📝 処理中: {i + 1}/{len(documents)} ({len(softball_data)}件のソフトボールデータ抽出)")

        conn.close()

    except Exception as e:
        print(f"❌ ChromaDB処理エラー: {e}")
        return []

    print(f"✅ ソフトボール学習データ抽出完了: {len(softball_data)}件")
    return softball_data

def save_softball_data_to_files(softball_data: List[SoftballData], output_dir: str):
    """ソフトボールデータを各種ファイル形式で保存"""

    os.makedirs(output_dir, exist_ok=True)

    # 1. JSON形式で保存
    json_file = os.path.join(output_dir, "softball_learning_data.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(data) for data in softball_data], f,
                 ensure_ascii=False, indent=2)
    print(f"📄 JSON保存完了: {json_file}")

    # 2. CSV形式で保存
    csv_file = os.path.join(output_dir, "softball_learning_data.csv")
    df_data = []

    for data in softball_data:
        row = {
            'timestamp': data.timestamp,
            'user': data.user,
            'category': data.category,
            'content': data.content,
            'players_mentioned': ','.join(data.players_mentioned),
            'keywords': ','.join(data.keywords),
            'message_length': data.metadata.get('message_length', 0),
            'has_question': data.metadata.get('has_question', False),
            'has_exclamation': data.metadata.get('has_exclamation', False),
            'has_emoji': data.metadata.get('has_emoji', False),
            'is_weekend': data.metadata.get('is_weekend', False),
            'hour': data.metadata.get('hour', None)
        }
        df_data.append(row)

    df = pd.DataFrame(df_data)
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"📊 CSV保存完了: {csv_file}")

    # 3. カテゴリ別統計
    stats_file = os.path.join(output_dir, "softball_statistics.json")

    category_stats = {}
    player_stats = {}
    keyword_stats = {}

    for data in softball_data:
        # カテゴリ統計
        category_stats[data.category] = category_stats.get(data.category, 0) + 1

        # 選手統計
        for player in data.players_mentioned:
            player_stats[player] = player_stats.get(player, 0) + 1

        # キーワード統計
        for keyword in data.keywords:
            keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1

    statistics = {
        "total_messages": len(softball_data),
        "category_distribution": dict(sorted(category_stats.items(), key=lambda x: x[1], reverse=True)),
        "top_mentioned_players": dict(sorted(player_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
        "top_keywords": dict(sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)[:20]),
        "generated_at": datetime.now().isoformat()
    }

    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(statistics, f, ensure_ascii=False, indent=2)
    print(f"📈 統計データ保存完了: {stats_file}")

    return statistics

def main():
    """メイン処理"""
    print("=" * 60)
    print("🥎 ソフトボールチーム学習データ作成")
    print("=" * 60)

    # 設定
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    persist_directory = os.path.join(project_root, "db", "chroma_store")
    output_dir = os.path.join(project_root, "softball_learning_data")

    print(f"📁 ChromaDB: {persist_directory}")
    print(f"📁 出力ディレクトリ: {output_dir}")

    # ソフトボールデータ抽出
    print("\n🔍 ChromaDBからソフトボールデータを抽出中...")
    softball_data = extract_softball_data_from_chromadb(persist_directory)

    if not softball_data:
        print("❌ ソフトボール関連データが見つかりませんでした")
        return

    # データ保存
    print(f"\n💾 学習データを保存中...")
    statistics = save_softball_data_to_files(softball_data, output_dir)

    # 結果表示
    print("\n" + "=" * 60)
    print("📊 ソフトボール学習データ作成完了!")
    print("=" * 60)
    print(f"✅ 総メッセージ数: {statistics['total_messages']}")
    print(f"✅ カテゴリ数: {len(statistics['category_distribution'])}")
    print(f"✅ 言及された選手数: {len(statistics['top_mentioned_players'])}")

    print(f"\n📋 主要なカテゴリ:")
    for category, count in list(statistics['category_distribution'].items())[:5]:
        print(f"   - {category}: {count}件")

    print(f"\n👥 よく言及される選手:")
    for player, count in list(statistics['top_mentioned_players'].items())[:5]:
        print(f"   - {player}: {count}回")

    print(f"\n📁 保存先: {output_dir}")
    print(f"   - softball_learning_data.json (詳細データ)")
    print(f"   - softball_learning_data.csv (表形式)")
    print(f"   - softball_statistics.json (統計情報)")

if __name__ == "__main__":
    main()
