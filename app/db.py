import json
import os
from collections import defaultdict

FILENAME = "events.json"  # Name of the file to store our event data

def save_events(events):
    """
    Save the list of events to a JSON file.

    Args:
        events (list): List of events.
    """
    with open(FILENAME, "w", encoding="utf-8") as file:
        json.dump(events, file, ensure_ascii=False, indent=4)


def load_events():
    """
    Load events from the JSON file.

    If the file doesn't exist or can't be loaded, returns an empty list.
    
    Returns:
        list: List of events loaded from the file or an empty list if an error occurred.
    """
    # If the file doesn't exist, returns an empty list
    if not os.path.exists(FILENAME):
        return []
    try:
        # Attempt to open the file and load the data
        with open(FILENAME, "r", encoding="utf-8") as file:
            data = json.load(file)
            # Check if the data is a list of dictionaries (data format we want)
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return data
            else:
                print("wrong format, check the file")
                return []
    except json.JSONDecodeError:
        # Handle JSON decoding errors and return an empty list
        print("Error decoding the json")
        return []
