# "type": Indica o tipo de evento, como PushEvent, PullRequestEvent, etc.
# "actor": Informações sobre quem realizou a ação (ex.: login do usuário).
# "repo": Detalhes sobre o repositório onde aconteceu o evento.
# "created_at": Data e hora do evento (padrão UTC).
# "payload": Informações adicionais específicas do tipo de evento (ex.: commits em um PushEvent).

from app.github_api import fetch_events, filter_recent_events
from app.db import save_events, load_events

# Substitua pelos valores reais
# GITHUB_TOKEN = "<SEU_TOKEN>"
GITHUB_TOKEN = "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"
OWNER = "EderCSantana"
# REPO = "Beecrowd"
# REPO = "forrozeiros-cz "
# REPO = "All_42"
REPO = "Sync_task"
MAX_EVENTS = 500
N_DAYS = 100

# events = fetch_events(OWNER, REPO, GITHUB_TOKEN)

# recent_events = filter_recent_events(events, days=N_DAYS)

# for event in events[:MAX_EVENTS]:  # Mostra os primeiros 5 eventos
#     print(f"ID: {event['id']}, Tipo: {event['type']}, Data: {event['created_at']}")
#     print(event)
# for event in recent_events[:5]:  # Mostra os 5 primeiros eventos para revisão
#     print(f"ID: {event['id']}, Tipo: {event['type']}, Data: {event['created_at']}")

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

# Salvar os eventos filtrados
save_events(filtered_events)

# Mostrar resultado
print(f"Número total de eventos armazenados: {len(filtered_events)}")