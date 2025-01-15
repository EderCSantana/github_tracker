# GitHub Activity Tracker

## Descrição
Uma aplicação para monitorar atividades em repositórios do GitHub, gerando estatísticas como o tempo médio entre eventos. Os dados são armazenados localmente e expostos por uma REST API.

---

## Requisitos

- Python 3.9 ou superior
- Biblioteca `Flask`
- Biblioteca `requests`

---

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/github-tracker.git
   cd github-tracker

Instale as dependências:

pip install -r requirements.txt

export GITHUB_TOKEN=<SEU_GITHUB_TOKEN>    # Linux/Mac
set GITHUB_TOKEN=<SEU_GITHUB_TOKEN>      # Windows


Inicie o servidor:
python main.py

Acesse os endpoints da API:
-Atualizar eventos (POST):
curl -X POST http://127.0.0.1:5000/api/update

-Consultar eventos (GET):
curl "http://127.0.0.1:5000/api/events?days=7&max_events=10"

-Estatísticas (GET):
curl http://127.0.0.1:5000/api/stats


