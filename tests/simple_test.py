print("Hello World - テスト実行中...")

import re
from datetime import datetime, timedelta

# 基本的な日付テスト
today = datetime.now().date()
print(f"今日の日付: {today}")

target_date = today + timedelta(days=1)
print(f"明日の日付: {target_date}")

# 正規表現テスト
test_text = "テストイベント: 2025/10/27(月) 15:00"
pattern = r"(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)"

matches = re.findall(pattern, test_text)
print(f"テストテキスト: {test_text}")
print(f"正規表現パターン: {pattern}")
print(f"マッチ結果: {matches}")

if matches:
    match = matches[0]
    year, month, day = map(int, match)
    parsed_date = datetime(year, month, day).date()
    print(f"パース結果: {parsed_date}")
    print(f"明日と一致するか: {parsed_date == target_date}")
else:
    print("マッチしませんでした")

print("テスト完了")
