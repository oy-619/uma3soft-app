import re

test_text = "テストイベント: 2025/10/27(月) 15:00"
pattern = r"(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)"

matches = re.findall(pattern, test_text)
print(f"Pattern: {pattern}")
print(f"Text: {test_text}")
print(f"Matches: {matches}")

# 実際のマッチを詳細確認
match_obj = re.search(pattern, test_text)
if match_obj:
    print(f"Match groups: {match_obj.groups()}")
    print(f"Full match: {match_obj.group(0)}")
else:
    print("No match found")
