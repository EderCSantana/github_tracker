# GitHub Activity Tracker
This project tracks GitHub events for multiple repositories using the GitHub API. It provides functionality to fetch, update, filter, and calculate statistics about events, such as average time between events(now only avg, in the future new stats can be added). The system stores the events in a JSON file and allows updates based on new events fetched from GitHub.

# Explanation about choices:
1. The storage could be done in SQLite, in SQL with Python access, or with pandas in CSV... etc. As the data comes from GitHub in a JSON format I wanted to keep the format just as a personal preference
2. The data is stored to minimize the need to request from GitHub, for this reason, we have one API to update the stored data, and one API to get the data from the local storage
3. We can adapt the filters among the number of days and events allowed in the storage, I like it more than fixed values, but it has some default values
4. There's another API to fetch events from GitHub, it was used to debug during development, I prefer to keep it, but it's not really needed
5. The on_dev.py was used in the beggining of the development, I let it there so anyone can have an idea how I started checking if the values were correct

# Features
● Fetch Events : Fetch events from one or more GitHub repositories.
● Filter Events : Filter events from the last N days and limit the number of M events retrieved.
● Average Time Between Events : Calculate the average time between events grouped by repository and event type.
● Update Events : Update the locally stored events with new ones fetched after a given date.

# Requirements
● Python 3.9 or higher
● Required Python libraries: Flask (3.1.0), requests(2.32.3)
To install the necessary dependencies, run:
pip install Flask==3.1.0 requests==2.32.3

Setup
1. Create a GitHub API token :
○ Visit GitHub Personal Access Tokens to create a new token.
○ Select the necessary permissions (repo access is typically required).
○ Save the token securely, as it will be used for authentication when fetching events.
2. Steps to Create a GitHub Token :
○ Log in to your GitHub account.
○ Go to Developer settings > Personal access tokens.
○ Click "Generate new token".
○ Set the scope by selecting permissions (for public repositories, you can check "repo" scope).
○ Click "Generate token" and copy it immediately.
3. Store Your GitHub Token :
Export the token as an environment variable:
export GITHUB_TOKEN=<GITHUB_TOKEN> # Linux, or in my case I used WSL 
! If exporting the token doesn't work, just add it in the following code line in the files github_api.py and api.py
! GITHUB_TOKEN= <your_token_here>

4. Run the Application :
python app.py  # if it doesn't work properly, check if __init__.py has all it need, and you can run running python api.py, this will make the APIs working. If it fall, start again

# Project Structure
The project has the following structure:
─ app.py # Flask application for API endpoints.
─ db.py # Functions for saving and loading events from the JSON file.
─ github_api.py # Functions for interacting with the GitHub API and event
processing.
─ events.json # Stores the events fetched from GitHub.

# API Endpoints 
The following info and comments can be find in the document, I included the commands to access them
/api/update
● Method : POST
● Description : API endpoint to update event list for multiple repositories.
Request Body :
{
"repositories": ["owner/repo", "owner/repo2"...."owner/repoN"]
}

○ repositories (required): A list of repositories in owner/repo format.
● Response : Returns the success message, number of new events and repositories updated.
Example:
curl -X POST -H "Content-Type: application/json" -d '{"repositories": ["owner/repo"]}'
http://127.0.0.1:5000/api/update

/api/events
● Method : GET
● Description : Return events on our json with restrictions of days and number of events
● Query Parameters :
○ days (int): Number of recent days we want (in our case 7)
○ max_events (int): Max number of events we want(in our case 500).

● Response : A list of events filtered by the provided parameters.
Example:
curl "http://127.0.0.1:5000/api/events?days=7&max_events=10"

/api/avgtime
● Method : GET
● Description : Return the average time between events, grouped by repository and event type.
● Response :
○ Return results in a json format with the avg times
Example:
curl http://127.0.0.1:5000/api/avgtime

/api/fetch
● Method : POST
● Description : API endpoint to fetch events from GitHub repositories.
Request Body :
{
"repositories": ["owner/repo", "owner/repo2"],
"per_page": 100
}
●
○ repositories (required): List of repositories in "owner/repo" format.
○ per_page (optional): Number of events per page (I let it as 100, no need of that)
● Response :
○ Events for the given repositories
Example:
curl -X POST -H "Content-Type: application/json" -d '{"repositories": ["owner/repo"]}'
http://127.0.0.1:5000/api/fetch

