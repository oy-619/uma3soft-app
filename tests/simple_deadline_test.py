import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

print("Starting test...")
try:
    from reminder_schedule import get_upcoming_deadline_notes

    print("Import successful")

    notes = get_upcoming_deadline_notes(days_ahead=7)
    print(f"Found {len(notes)} notes")

    for note in notes:
        if "入力期限" in note["content"]:
            print(f"Found deadline note: {note['content'][:150]}...")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()

print("Test completed")
