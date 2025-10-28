import sys

sys.path.append(".")
from datetime import datetime

from reminder_schedule import get_upcoming_deadline_notes

print("=== Debug: Tomorrow Schedule Search ===")
notes = get_upcoming_deadline_notes(days_ahead=1)
print(f"Found {len(notes)} notes for tomorrow")
for note in notes:
    print(f'- Date: {note["date"]}')
    print(f'- Content: {note["content"][:100]}...')
    print()
