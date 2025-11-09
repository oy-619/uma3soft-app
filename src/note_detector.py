#!/usr/bin/env python3
"""
LINE ノート投稿検出システム

ノート投稿時の通知メッセージやURLを検出・抽出し、
データベースに保存する機能を提供する。
"""

import re
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class NoteInfo:
    """ノート情報データクラス"""
    note_id: str
    note_url: str
    group_id: str
    user_id: str
    user_name: str
    title: str
    detected_at: str
    message_text: str

class NoteDetector:
    """LINE ノート投稿検出クラス"""

    def __init__(self, storage_file: str = "detected_notes.json"):
        """
        初期化

        Args:
            storage_file (str): ノート情報保存ファイル
        """
        self.storage_file = storage_file
        self.notes_db = []
        self.load_notes_db()

        # ノート投稿通知のパターン
        self.note_patterns = [
            # 標準的なノート投稿通知
            r'(.+)がノートを投稿しました',
            r'(.+) posted a note',
            r'(.+)さんがノートを投稿しました',
            r'📝\s*(.+)がノートを投稿しました',

            # ノートURL直接投稿
            r'https://line\.me/R/note/([^/]+)/([^/?]+)',
            r'https://line\.me/R/home/note/([^/]+)/([^/?]+)',
        ]

        # 調整さんURLパターン
        self.chouseisan_patterns = [
            r'https?://chouseisan\.com/s\?h=([\w\d]+)',
            r'https?://chouseisan\.com/s\?h=([\w\d]+)&acs=1',
        ]

        print(f"[NOTE_DETECTOR] 初期化完了 - 保存済みノート数: {len(self.notes_db)}")

    def load_notes_db(self):
        """保存されたノート情報を読み込み"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.notes_db = [NoteInfo(**item) for item in data]
                print(f"[NOTE_DETECTOR] ノート情報読み込み完了: {len(self.notes_db)}件")
            else:
                print(f"[NOTE_DETECTOR] 新規データベース作成")
        except Exception as e:
            print(f"[NOTE_DETECTOR] データベース読み込みエラー: {e}")
            self.notes_db = []

    def save_notes_db(self):
        """ノート情報をファイルに保存"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(note) for note in self.notes_db], f,
                         ensure_ascii=False, indent=2)
            print(f"[NOTE_DETECTOR] ノート情報保存完了: {len(self.notes_db)}件")
        except Exception as e:
            print(f"[NOTE_DETECTOR] データベース保存エラー: {e}")

    def detect_note_notification(self, message_text: str, user_id: str,
                                group_id: str = None, user_name: str = "Unknown") -> Optional[NoteInfo]:
        """
        メッセージからノート投稿通知を検出

        Args:
            message_text (str): メッセージテキスト
            user_id (str): ユーザーID
            group_id (str, optional): グループID
            user_name (str): ユーザー名

        Returns:
            Optional[NoteInfo]: 検出されたノート情報
        """
        print(f"[NOTE_DETECTOR] メッセージ検出開始: {message_text[:50]}...")

        # ノート投稿通知の検出
        for pattern in self.note_patterns:
            match = re.search(pattern, message_text)
            if match:
                print(f"[NOTE_DETECTOR] ノート投稿通知検出: パターン={pattern}")

                # ユーザー名を抽出（パターンに含まれる場合）
                if match.groups():
                    detected_user_name = match.group(1)
                else:
                    detected_user_name = user_name

                # ノートURLを同じメッセージから探す
                note_url = self.extract_note_url(message_text)

                if note_url:
                    note_id = self.extract_note_id_from_url(note_url)

                    note_info = NoteInfo(
                        note_id=note_id,
                        note_url=note_url,
                        group_id=group_id or user_id,
                        user_id=user_id,
                        user_name=detected_user_name,
                        title=self.extract_note_title(message_text),
                        detected_at=datetime.now().isoformat(),
                        message_text=message_text
                    )

                    # データベースに追加
                    self.add_note_to_db(note_info)

                    return note_info

        # 直接ノートURLが投稿された場合
        note_url = self.extract_note_url(message_text)
        if note_url:
            print(f"[NOTE_DETECTOR] ノートURL直接投稿検出: {note_url}")

            note_id = self.extract_note_id_from_url(note_url)

            note_info = NoteInfo(
                note_id=note_id,
                note_url=note_url,
                group_id=group_id or user_id,
                user_id=user_id,
                user_name=user_name,
                title=self.extract_note_title(message_text),
                detected_at=datetime.now().isoformat(),
                message_text=message_text
            )

            # データベースに追加
            self.add_note_to_db(note_info)

            return note_info

        return None

    def extract_note_url(self, text: str) -> Optional[str]:
        """テキストからノートURLを抽出"""
        patterns = [
            r'(https://line\.me/R/note/[^/]+/[^/?]+)',
            r'(https://line\.me/R/home/note/[^/]+/[^/?]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return None

    def extract_note_id_from_url(self, url: str) -> str:
        """ノートURLからノートIDを抽出"""
        patterns = [
            r'https://line\.me/R/note/[^/]+/([^/?]+)',
            r'https://line\.me/R/home/note/[^/]+/([^/?]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # URLからIDが抽出できない場合はURL全体をハッシュ化
        import hashlib
        return hashlib.md5(url.encode('utf-8')).hexdigest()[:16]

    def extract_note_title(self, text: str) -> str:
        """メッセージからノートタイトルを推測"""
        lines = text.split('\n')

        # 最初の行をタイトルとして使用（ノート投稿通知以外）
        for line in lines:
            line = line.strip()
            if line and 'がノートを投稿しました' not in line and 'https://' not in line:
                return line[:50]  # 最大50文字

        return "ノート"  # デフォルトタイトル

    def extract_chouseisan_url(self, text: str) -> Optional[str]:
        """テキストから調整さんURLを抽出"""
        for pattern in self.chouseisan_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return None

    def add_note_to_db(self, note_info: NoteInfo):
        """ノート情報をデータベースに追加（重複チェック付き）"""
        # 重複チェック
        for existing_note in self.notes_db:
            if existing_note.note_id == note_info.note_id:
                print(f"[NOTE_DETECTOR] 重複ノートをスキップ: {note_info.note_id}")
                return

        # 新規追加
        self.notes_db.append(note_info)
        self.save_notes_db()
        print(f"[NOTE_DETECTOR] 新規ノート登録: {note_info.title} ({note_info.note_id})")

    def get_latest_notes(self, limit: int = 5) -> List[dict]:
        """最新のノートを取得（辞書形式で返す）"""
        latest = sorted(self.notes_db, key=lambda x: x.detected_at, reverse=True)[:limit]
        return [asdict(note) for note in latest]

    def search_notes_by_title(self, keyword: str) -> List[dict]:
        """タイトルでノートを検索する（リマインダー関連付け用）"""
        keyword_lower = keyword.lower()
        results = []

        for note in self.notes_db:
            title = note.title.lower()

            if keyword_lower in title:
                results.append(asdict(note))

        # 日時でソート（新しいものから）
        results.sort(key=lambda x: x.get('detected_at', ''), reverse=True)
        return results

    def get_notes_by_group(self, group_id: str, limit: int = 10) -> List[NoteInfo]:
        """特定グループのノート情報を取得"""
        group_notes = [note for note in self.notes_db if note.group_id == group_id]
        return sorted(group_notes, key=lambda x: x.detected_at, reverse=True)[:limit]

    def get_chouseisan_urls(self, recent_only: bool = True) -> List[Tuple[str, str]]:
        """
        保存されたノートから調整さんURLを抽出

        Args:
            recent_only (bool): 最新のもののみ取得するか

        Returns:
            List[Tuple[str, str]]: (ノートタイトル, 調整さんURL) のリスト
        """
        chouseisan_urls = []

        if recent_only:
            notes_to_check = sorted(self.notes_db, key=lambda x: x.detected_at, reverse=True)[:20]
        else:
            notes_to_check = self.notes_db

        for note in notes_to_check:
            chouseisan_url = self.extract_chouseisan_url(note.message_text)
            if chouseisan_url:
                chouseisan_urls.append((note.title, chouseisan_url))

        return chouseisan_urls

    def generate_notes_summary(self) -> str:
        """ノート情報のサマリーを生成"""
        if not self.notes_db:
            return "📝 検出されたノートはありません。"

        latest_notes = self.get_latest_notes(5)

        summary = f"📝 **検出済みノート情報** (総数: {len(self.notes_db)}件)\n\n"

        for i, note in enumerate(latest_notes, 1):
            detected_date = datetime.fromisoformat(note.detected_at).strftime("%Y/%m/%d %H:%M")
            summary += f"{i}. **{note.title}**\n"
            summary += f"   👤 {note.user_name} | 📅 {detected_date}\n"
            summary += f"   🔗 {note.note_url}\n\n"

        # 調整さんURL情報
        chouseisan_urls = self.get_chouseisan_urls()
        if chouseisan_urls:
            summary += "📊 **調整さんURL** (最新):\n"
            for title, url in chouseisan_urls[:3]:
                summary += f"   - {title}: {url}\n"

        return summary

def main():
    """テスト用メイン関数"""
    detector = NoteDetector()

    # テストメッセージ
    test_messages = [
        "田中さんがノートを投稿しました\nhttps://line.me/R/note/C1234567890/NOTE123456",
        "次回の練習について\nhttps://chouseisan.com/s?h=abc123xyz",
        "📝 山田がノートを投稿しました\n練習試合の件\nhttps://line.me/R/home/note/C9876543210/NOTE789012",
    ]

    print("=" * 60)
    print("🔍 ノート検出システム テスト")
    print("=" * 60)

    for i, message in enumerate(test_messages, 1):
        print(f"\n--- テストメッセージ {i} ---")
        print(f"入力: {message}")

        result = detector.detect_note_notification(
            message_text=message,
            user_id=f"U{i:010d}",
            group_id="C1234567890",
            user_name=f"TestUser{i}"
        )

        if result:
            print(f"✅ 検出成功: {result.title}")
            print(f"   URL: {result.note_url}")
        else:
            print("❌ ノート検出されず")

    # サマリー表示
    print(f"\n{detector.generate_notes_summary()}")

if __name__ == "__main__":
    main()
