import requests
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from db import load_events, save_events

GITHUB_API = "https://api.github.com/repos"

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
