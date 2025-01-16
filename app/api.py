from flask import Flask, jsonify, request
from db import load_events, save_events # used to store and get data from our storage (json)
from github_api import fetch_events, filter_recent_events, calculate_event_avg_time, update_events
from datetime import datetime, timezone #used to fix data formats

# Initialize Flask application to access the api
app = Flask(__name__)

# if exporting the token doesn't work, just add it here and in github_api.py
# GITHUB_TOKEN= <your_token_here>

@app.route('/api/update', methods=['POST'])
def update_events_api():
    """
    API endpoint to update event list for multiple repositories.
    """
    # Parse JSON request
    request_data = request.get_json()
    # Extract the repositories list from the request
    repo_list = request_data.get("repositories", [])
    if not repo_list: #gives error if there are no repositories
        return jsonify({"message": "No repositories in the reques, provide them!"}), 400

    # load saved events
    saved_events = load_events()

    # Find the most recent event date among the saved events (if any)
    latest_event_date = None
    if saved_events:
        latest_event_date = max(
            datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) 
            for event in saved_events
        )

    # call function that updates events in the list
    result = update_events(repo_list, latest_event_date, GITHUB_TOKEN)

    return jsonify(result)


@app.route('/api/events', methods=['GET'])
def get_events():
    """
    Return events on our json with restrictions of days and number of events
    Query parameters:
        - days (int): Number of recent days we want (in our case 7).
        - max_events (int): Max number of events we want(in our case 500).
    """
    days = int(request.args.get('days', 7))
    max_events = int(request.args.get('max_events', 500))

    # Load the events stored in the json
    all_events = load_events()

    # Keep only relevant events considering restrictions (days and max of events)
    filtered_events = filter_recent_events(all_events, days=days, max_events=max_events)

    return jsonify(filtered_events)

@app.route('/api/avgtime', methods=['GET'])
def get_event_avg_time():
    """
    Return the average time between events, grouped by repository and event type.
    
    """
    # load the stored events
    all_events = load_events()

    # calls the function that calculate the average time between events
    avg_time = calculate_event_avg_time(all_events)

    # return results in a json format with the avg times
    return jsonify(avg_time)

# this api is just to check if the updated data is correct
@app.route('/api/fetch', methods=['POST'])
def fetch_events_api():
    """
    API endpoint to fetch events from GitHub repositories.

    Body (JSON):
        - repositories (list): List of repositories in "owner/repo" format.
        - per_page (int, optional): Number of events per page (I let it as 100, no need of that).

    Returns:
        JSON: Events for the given repositories.
    """
    # Parse the JSON body
    request_data = request.get_json()
    
    # Get the list of repositories, and give a message if there are none
    repo_list = request_data.get("repositories", [])
    if not repo_list:
        return jsonify({"message": "No repositories, try again"}), 400
    
    # Get the optional "per_page" parameter
    per_page = request_data.get("per_page", 100)

    try:
        # look for events using the provided parameters
        fetched_events = fetch_events(repo_list, GITHUB_TOKEN, per_page=per_page)

        # Return the fetched events in a json format
        return jsonify({
            "message": "Events found successfully!",
            "repositories": repo_list,
            "event_count": len(fetched_events),
            "events": fetched_events
        })
    except Exception as e:
        # Return message for error
        return jsonify({"message": f"Error fetching events: {str(e)}"}), 500

# keep the APIs above running
if __name__ == '__main__':
    app.run(debug=True)



