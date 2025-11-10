from datetime import datetime, timezone

# Get the current time in UTC
now_utc = datetime.now(timezone.utc)

print(f"Python's current UTC time is: {now_utc}")