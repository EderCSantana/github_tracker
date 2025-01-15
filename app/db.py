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


# def load_events():
#     """
#     Load events from a JSON file if it exists.

#     Returns:
#         list: The list of events loaded from the file, or an empty list if there's no file.
#     """
#     if not os.path.exists(FILENAME):
#         return []
    
#     with open(FILENAME, "r", encoding="utf-8") as file:
#         return json.load(file)
def load_events():
    if not os.path.exists(FILENAME):
        return []
    try:
        with open(FILENAME, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return data
            else:
                print("Formato inválido no arquivo JSON")
                return []
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON")
        return []
