import requests
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from db import load_events, save_events

GITHUB_API = "https://api.github.com/repos"

# Version for one repo
# #get the token in https://github.com/settings/personal-access-tokens
# def fetch_events(owner, repo, token):
#     """
#     Get events from a github repository as long we have their details
    
#     Args:
#         owner (str): Name of the owner. 
#         repo (str): Name the repository.
#         token (str): Github access token.

#     Returns:
#         list: Lista de eventos do repositório.
#     """
    
#     url = f"{GITHUB_API}/{owner}/{repo}/events" #concatenate the owner and repository in the url
#     headers = {"Authorization": f"token {token}"} #create header to our GET 
    
#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()  #gives error if the answer has some error
#         return response.json()  # Return list of events in a json format
#     except requests.exceptions.RequestException as e:
#         print(f"Error to access the API. Check if the requirements are ok: {e}")
#         return []

# For more repo
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
    headers = {"Authorization": f"token {github_token}"}
    all_events = []

    for repo in repo_list:
        url = f"https://api.github.com/repos/{repo}/events?per_page={per_page}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            all_events.extend(response.json())
        else:
            print(f"Error fetching events for {repo}: {response.status_code} {response.text}")

    return all_events

def filter_recent_events(events, days, max_events):
    """
    Restrict the events to include the last N days (last 7 days in our case) and max M events (500 in our case)

    Args:
        events (list): List of events from github
        days (int): Number of days for the filter
        max_events (int): Max number of events

    Returns:
        list: Events from the given list that happened on the last days (seven)
    """
    recent_events = [] #start an empty list to store the relevant events
    date_cleaner = datetime.now(timezone.utc) - timedelta(days=days) #takes the time of a moment N(seven) days ago

    for event in events:
        
        if len(recent_events) >= max_events:
            break
        #converts date string in a date format
        event_date = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        if event_date >= date_cleaner: 
            #add to events to the list
            recent_events.append(event)

    return recent_events


# def calculate_event_avg_time(events):
#     """
#     Calculate avg time between events group by type and repository

#     Args:
#         events (list): List with events.

#     Returns:
#         dict: Avg time between eventd by type and repository
#     """
#     avg_time = defaultdict(list)
    
#     # Order events by date
#     events.sort(key=lambda e: datetime.strptime(e['created_at'], "%Y-%m-%dT%H:%M:%SZ"))
    
#     # CaCalculate time between events
#     for i in range(1, len(events)):
#         event = events[i]
#         prev_event = events[i - 1]
        
#         # CCalculate time difference (current and previous time)
#         curr_time = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
#         prev_time = datetime.strptime(prev_event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
#         time_diff = (curr_time - prev_time).total_seconds()
        
#         # list and group by type and repository (cictionary of tuples and numnber (time diff))
#         avg_time[(event['type'], event['repo']['name'])].append(time_diff)
    
#     # Calculate and return avg. key[0] is type, key[1] is repository
#     # it get the sum of all times, and the number of evnts, take the averege
    
#     return {
#         f"{key[0]} - {key[1]}": sum(times) / len(times) if times else 0
#         for key, times in avg_time.items()
#     }

# version 1 repo
# def calculate_event_avg_time(events):
#     """
#     Calculate average time between events grouped by type and repository.

#     Args:
#         events (list): List of events from multiple repositories.

#     Returns:
#         dict: Statistics as { "EventType - RepoName": AverageTimeInSeconds }.
#     """
#     grouped_events = {}
#     for event in events:
#         key = f"{event['type']} - {event['repo']['name']}"
#         if key not in grouped_events:
#             grouped_events[key] = []
#         grouped_events[key].append(event)

#     avg_time = {}
#     for key, group in grouped_events.items():
#         sorted_group = sorted(group, key=lambda x: x['created_at'])
#         time_differences = []
#         for i in range(1, len(sorted_group)):
#             time_diff = datetime.strptime(sorted_group[i]['created_at'], "%Y-%m-%dT%H:%M:%SZ") - \
#                         datetime.strptime(sorted_group[i - 1]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
#             time_differences.append(time_diff.total_seconds())

#         avg_time[key] = sum(time_differences) / len(time_differences) if time_differences else 0

#     return avg_time

def calculate_event_avg_time(events):
    """
    Calculate the average time between events grouped by type and repository.

    Args:
        events (list): List of events from multiple repositories.

    Returns:
        dict: Statistics as { "EventType - RepoName": AverageTimeInSeconds }.
    """
    grouped_events = defaultdict(list)

    # Agrupar os eventos por tipo de evento e nome do repositório
    for event in events:
        repo_name = event['repo']['name']
        event_type = event['type']
        key = f"{event_type} - {repo_name}"
        grouped_events[key].append(event)

    # Calcular o tempo médio entre os eventos por cada combinação tipo de evento/repositório
    avg_time = {}
    for key, group in grouped_events.items():
        sorted_group = sorted(group, key=lambda x: x['created_at'])
        time_differences = []
        
        for i in range(1, len(sorted_group)):
            time_diff = datetime.strptime(sorted_group[i]['created_at'], "%Y-%m-%dT%H:%M:%SZ") - \
                        datetime.strptime(sorted_group[i - 1]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            time_differences.append(time_diff.total_seconds())

        avg_time[key] = sum(time_differences) / len(time_differences) if time_differences else 0

    return avg_time


def update_events(repo_list, latest_event_date, github_token):
    """
    Atualiza os eventos no JSON com base no evento mais recente armazenado.

    Args:
        repo_list (list): Lista de repositórios no formato "owner/repo".
        latest_event_date (datetime): Data do evento mais recente salvo.
        github_token (str): Token de acesso ao GitHub.

    Returns:
        dict: Resumo da operação de atualização.
    """
    new_events = []
    for repo in repo_list:
        try:
            owner, repo_name = repo.split('/')
        except ValueError:
            return {"message": f"Formato de repositório inválido: {repo}. Use 'owner/repo'.", "new_events_count": 0, "repositories_updated": 0}

        # Buscar eventos novos do repositório, mas apenas depois do evento mais recente
        repo_events = fetch_events([repo], github_token)

        # Filtrar os eventos novos após a data mais recente
        if latest_event_date:
            repo_new_events = [
                event for event in repo_events
                if datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) > latest_event_date
            ]
        else:
            # Se não houver evento salvo, pegar todos os eventos do repositório
            repo_new_events = repo_events

        print(f"Repositório {repo} tem {len(repo_new_events)} novos eventos.")  # Debugging

        # Adicionar eventos novos à lista
        new_events.extend(repo_new_events)

    # Carregar os eventos salvos e adicionar os novos
    saved_events = load_events()
    all_events = saved_events + new_events

    # Garantir que eventos duplicados não sejam armazenados
    unique_events = {event['id']: event for event in all_events}.values()

    # Salvar os eventos atualizados
    save_events(list(unique_events))

    return {
        "message": "Eventos atualizados com sucesso.",
        "new_events_count": len(new_events),
        "repositories_updated": len(repo_list)
    }
