
from reminder_schedule import get_reminders_for_day_after_tomorrow
from datetime import datetime, timedelta

# テスト日付を設定（2025年10月25日に設定して、2日後の10月27日のイベントを取得）
test_date = datetime(2025, 10, 25)
print('テスト日付:', test_date.strftime('%Y-%m-%d'))  
print('2日後の日付（探すイベント日）:', (test_date + timedelta(days=2)).strftime('%Y-%m-%d'))

# get_reminders_for_day_after_tomorrowをテスト実行
reminders = get_reminders_for_day_after_tomorrow(test_date)
print()
print('2日後のリマインダー数:', len(reminders))
for reminder in reminders:
    print('イベント名:', reminder['title'])
    print('イベント日:', reminder['event_date'])

