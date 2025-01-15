from flask import Flask, jsonify, request
from db import load_events, save_events
from github_api import fetch_events, filter_recent_events, calculate_event_avg_time, update_events
from datetime import datetime, timezone

app = Flask(__name__)

# settings for our 
GITHUB_TOKEN = "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"
# OWNER = "EderCSantana"
# # REPO = "Beecrowd"
# # REPO = "forrozeiros-cz "
# # REPO = "All_42"
# REPO = "Sync_task"

# version 1 repo
# @app.route('/api/update', methods=['POST'])
# def update_events():
#     """
#     Update the json with recent events
#     """
#     # Load the events we have saved
#     saved_events = load_events()

#     # find the most recent event
#     if saved_events:
#         latest_event_date = max(
#             datetime.strptime(e['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
#             for e in saved_events
#         )
#     else:
#         latest_event_date = None

#     # Find new (events made after the latest stored event) events on Github
#     if latest_event_date:
#         new_events = fetch_events(OWNER, REPO, GITHUB_TOKEN)
#         new_events = [
#             event for event in new_events
#             if datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) > latest_event_date
#         ]
#     else:
#         new_events = fetch_events(OWNER, REPO, GITHUB_TOKEN)

#     # Combine events and remove duplicates (converts in a dictionary adding an ID)
#     all_events = saved_events + new_events
#     unique_events = {event['id']: event for event in all_events}.values()

#     # Save the date in the json
#     save_events(list(unique_events))

#     return jsonify({"message": "Update worked well.", "new_events": len(new_events)})

@app.route('/api/update', methods=['POST'])
def update_events_api():
    """
    API endpoint to update events for multiple repositories.
    """
    request_data = request.get_json()
    repo_list = request_data.get("repositories", [])
    if not repo_list:
        return jsonify({"message": "No repositories provided in the request"}), 400

    # Carregar eventos já salvos
    saved_events = load_events()

    # Encontrar o evento mais recente armazenado
    latest_event_date = None
    if saved_events:
        latest_event_date = max(
            datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) 
            for event in saved_events
        )

    # Chamar a função de atualização de eventos
    result = update_events(repo_list, latest_event_date, GITHUB_TOKEN)

    # Retornar o resultado
    return jsonify(result)




# @app.route('/api/update', methods=['POST'])
# def update():
#     repositories = request.json.get("repositories", [])
#     if not repositories:
#         return jsonify({"status": "error", "message": "No repositories provided"}), 400
    
#     all_events = fetch_events(repositories, GITHUB_TOKEN)
#     save_events(all_events)
    
#     return jsonify({"status": "success", "message": "Events updated successfully.", "new_events": len(all_events)})


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

# @app.route('/api/avgtime', methods=['GET'])
# def get_event_avg_time():
#     """
#     Calculate avg time between events
#     """
#     all_events = load_events()
#     avg_time = calculate_event_avg_time(all_events)
#     return jsonify(avg_time)

@app.route('/api/avgtime', methods=['GET'])
def get_event_avg_time():
    """
    Calculate and return the average time between events, grouped by repository and event type.
    """
    # Carregar os eventos armazenados
    all_events = load_events()

    # Calcular a média de tempo entre eventos
    avg_time = calculate_event_avg_time(all_events)

    # Retornar os resultados como JSON
    return jsonify(avg_time)

@app.route('/api/fetch', methods=['POST'])
def fetch_events_api():
    """
    API endpoint to fetch events from GitHub repositories.

    Body (JSON):
        - repositories (list): List of repositories in "owner/repo" format.
        - per_page (int, optional): Number of events per page (default: 100).

    Returns:
        JSON: Fetched events for the given repositories.
    """
    # Parse the JSON body
    request_data = request.get_json()
    
    # Get repositories list
    repo_list = request_data.get("repositories", [])
    if not repo_list:
        return jsonify({"message": "No repositories provided in the request"}), 400
    
    # Get the optional "per_page" parameter
    per_page = request_data.get("per_page", 100)

    try:
        # Fetch events using the provided parameters
        fetched_events = fetch_events(repo_list, GITHUB_TOKEN, per_page=per_page)

        # Return the fetched events as a JSON response
        return jsonify({
            "message": "Events fetched successfully.",
            "repositories": repo_list,
            "event_count": len(fetched_events),
            "events": fetched_events
        })
    except Exception as e:
        # Handle errors and return a message
        return jsonify({"message": f"Error fetching events: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)



