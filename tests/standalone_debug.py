#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime, timedelta

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# パス設定（reminder_schedule.pyと同じ）
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(PROJECT_ROOT, "db")
PERSIST_DIRECTORY = os.path.join(DB_DIR, "chroma_store")

print(f"[DEBUG] PERSIST_DIRECTORY: {PERSIST_DIRECTORY}")
print(f"[DEBUG] ChromaDB exists: {os.path.exists(PERSIST_DIRECTORY)}")

# ChromaDB接続
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vector_db = Chroma(
    persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings_model
)

# 日付設定
today = datetime.now().date()
target_date_range = [(today + timedelta(days=i)) for i in range(1, 2)]  # 明日のみ

print(f"[DEBUG] 今日: {today}")
print(f"[DEBUG] 対象日付範囲: {target_date_range}")

# ノート検索
notes = vector_db.similarity_search("[ノート]", k=50)
print(f"[DEBUG] Found {len(notes)} notes with '[ノート]' search")

upcoming_notes = []

for i, note in enumerate(notes):
    content = note.page_content
    if "[ノート]" not in content:
        continue

    print(f"\n[DEBUG] Note {i+1}: {content[:100]}...")

    # 'テストイベント'を含むかチェック
    if "テストイベント" in content:
        print(f"[DEBUG] Found テストイベント in note {i+1}")
        print(f"[DEBUG] Full content: {content}")

    # 日付パターンを検索
    date_patterns = [
        r"(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)",  # 2025/10/27(月)形式 - 優先
        r"(\d{4})/(\d{1,2})/(\d{1,2})",  # 2024/12/25形式
        r"(\d{1,2})月(\d{1,2})日",  # 12月25日形式
        r"(\d{1,2})/(\d{1,2})",  # 12/25形式
    ]

    found_dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"[DEBUG] Pattern '{pattern}' found matches: {matches}")
        for match in matches:
            try:
                if len(match) == 3:  # 年/月/日形式（曜日付きも含む）
                    year, month, day = map(int, match)
                    note_date = datetime(year, month, day).date()
                    print(f"[DEBUG] Parsed date (year/month/day): {note_date}")
                elif len(match) == 2:
                    if "月" in pattern:  # 月日形式
                        month, day = map(int, match)
                        year = today.year
                        # 過去の月の場合は翌年とする
                        if month < today.month or (
                            month == today.month and day < today.day
                        ):
                            year += 1
                        note_date = datetime(year, month, day).date()
                        print(f"[DEBUG] Parsed date (month/day): {note_date}")
                    else:  # MM/DD形式
                        month, day = map(int, match)
                        year = today.year
                        if month < today.month or (
                            month == today.month and day < today.day
                        ):
                            year += 1
                        note_date = datetime(year, month, day).date()
                        print(f"[DEBUG] Parsed date (MM/DD): {note_date}")

                found_dates.append(note_date)
            except ValueError as e:
                print(f"[DEBUG] Date parsing error: {e}")
                continue

    # 期限内の日付があるかチェック
    print(f"[DEBUG] Found dates for this note: {found_dates}")
    for note_date in found_dates:
        if note_date in target_date_range:
            print(f"[DEBUG] Note date {note_date} is in target range!")
            upcoming_notes.append(
                {
                    "content": content,
                    "date": str(note_date),
                    "days_until": (note_date - today).days,
                }
            )
            break

print(f"\n=== 最終結果 ===")
print(f"Found {len(upcoming_notes)} upcoming deadline notes")
for note in upcoming_notes:
    print(f"  日付: {note['date']}, 残り: {note['days_until']}日")
    print(f"  内容: {note['content'][:200]}...")
