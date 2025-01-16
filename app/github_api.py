import requests
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from db import load_events, save_events

#body of the github api
GITHUB_API = "https://api.github.com/repos"

# if exporting the token doesn't work, just add it here and in api.py
# GITHUB_TOKEN= <your_token_here>
def fetch_events(repo_list, github_token, per_page=100):
    """
    Fetch events from the GitHub API for multiple repositories.

    Args:
        repo_list (list): List of repositories in "owner/repo" format.
        github_token (str): GitHub API token.
        per_page (int): Number of events per page.

    Returns:
        list: Combined list of events for all repositories.
    """
    headers = {"authorization": f"token {github_token}"}
    all_events = []

    for repo in repo_list:
        url = f"https://api.github.com/repos/{repo}/events?per_page={per_page}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            all_events.extend(response.json())
        else:
            print(f"Error lookinf for events in {repo}: {response.status_code} {response.text}")

    return all_events

def filter_recent_events(events, days, max_events):
    """
    Restrict the events to include the last N days (last 7 days in our case) and max M events (500 in our case)

    Args:
        events (list): List of events from github
        days (int): Number of relevant days
        max_events (int): Max number of events

    Returns:
        list: Events from the given list that happened on the last days (seven)
    """
    recent_events = [] #start an empty list to store the relevant events
    date_cleaner = datetime.now(timezone.utc) - timedelta(days=days) #takes the time of a moment N(seven) days ago

    # add to recent_events only events in the date restriction 
    for event in events:
        
        if len(recent_events) >= max_events:
            break
        #converts date string in a date format
        event_date = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        if event_date >= date_cleaner: 
            #add to events to the list
            recent_events.append(event)

    return recent_events

def calculate_event_avg_time(events):
    """
    Calculate the average time between events grouped by type and repository.

    Args:
        events (list): List of events from multiple repositories.

    Returns:
        dict: Statistics as { "EventType - RepoName": AverageTimeInSeconds }.
    """
    grouped_events = defaultdict(list) #dictonary with values as lists. If a value doesn't exist, it gets an empty list

    # Group events by type and repository name
    for event in events:
        repo_name = event['repo']['name']
        event_type = event['type']
        key = f"{event_type} - {repo_name}" #string with type and name of repository
        grouped_events[key].append(event) #list of events identified by key

    # Calculate the average time between events for each grouped event type/repository
    avg_time = {} #dictionary for the avg time, so we know who has each time
    for key, group in grouped_events.items():
        sorted_group = sorted(group, key=lambda x: x['created_at'])
        time_differences = []
        
        #get the time difference between the events
        for i in range(1, len(sorted_group)):
            time_diff = datetime.strptime(sorted_group[i]['created_at'], "%Y-%m-%dT%H:%M:%SZ") - \
                        datetime.strptime(sorted_group[i - 1]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            time_differences.append(time_diff.total_seconds())
        #calculate the average (sum of all differences over the number of differences 
        avg_time[key] = sum(time_differences) / len(time_differences) if time_differences else 0

    return avg_time


def update_events(repo_list, latest_event_date, github_token):
    """
    Update the events stored in the JSON file, adding events that happened after the newest event.

    Args:
        repo_list (list): List of repositories in "owner/repo" format.
        latest_event_date (datetime): The date of the latest stored event.
        github_token (str): GitHub API token for authentication. (will be defined in the system, look on README)

    Returns:
        dict: Summary of the operation, with number of new events and repositories updated.
    """
    new_events = [] #define a empty list for new events
    for repo in repo_list:
        try:
            owner, repo_name = repo.split('/') #put owner and repository in a format
        except ValueError:
            return {"message": f"invalid format: {repo}. Use 'owner/repo'.", "new_events_count": 0, "repositories_updated": 0}

        # Fetch events from GitHub for the repository
        repo_events = fetch_events([repo], github_token)

        # Filter events based on the latest saved event date
        if latest_event_date:
            repo_new_events = [
                event for event in repo_events
                if datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) > latest_event_date
            ]
        else:
            # If no events are saved, get all events for the repository
            repo_new_events = repo_events

        print(f"Repository {repo} has {len(repo_new_events)} new events!")  

        # Add the new events to the list
        new_events.extend(repo_new_events)

    # Load the previously saved events and add the new events
    saved_events = load_events()
    all_events = saved_events + new_events

    # Remove duplicate events based on id as a key
    unique_events = {event['id']: event for event in all_events}.values()

    # save updates in the json
    save_events(list(unique_events))

    return {
        "message": "Events updates!",
        "new_events_count": len(new_events),
        "repositories_updated": len(repo_list)
    }
