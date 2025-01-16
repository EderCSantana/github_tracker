# "type": Indicates the event type, such as PushEvent, PullRequestEvent, etc.
# "actor": Information about who performed the action (e.g., user login).
# "repo": Details about the repository where the event occurred.
# "created_at": Date and time of the event (in UTC).
# "payload": Additional information specific to the event type (e.g., commits in a PushEvent).

from app.github_api import fetch_events, filter_recent_events
from app.db import save_events, load_events


# GITHUB_TOKEN = "<YOUR_TOKEN>"
GITHUB_TOKEN = "token"
OWNER = "owner"
REPO = "repo"
MAX_EVENTS = 500
N_DAYS = 100

# events = fetch_events(OWNER, REPO, GITHUB_TOKEN)

# recent_events = filter_recent_events(events, days=N_DAYS)

# for event in events[:MAX_EVENTS]:  # Display the first 5 events
#     print(f"ID: {event['id']}, Type: {event['type']}, Date: {event['created_at']}")
#     print(event)
# for event in recent_events[:5]:  # Display the first 5 events for review
#     print(f"ID: {event['id']}, Type: {event['type']}, Date: {event['created_at']}")

# load the events we have stored
stored_events = load_events()
print(stored_events)

# fetch new events
new_events = fetch_events(OWNER, REPO, GITHUB_TOKEN)
print(new_events)
# group all events (old and new)
all_events = new_events + stored_events
print(all_events)

# Filter events by days and amount
filtered_events = filter_recent_events(all_events, days=N_DAYS, max_events=MAX_EVENTS)

# save filtered events
save_events(filtered_events)


print(f"Number of stored events: {len(filtered_events)}")
