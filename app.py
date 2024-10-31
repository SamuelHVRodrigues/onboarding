import os
import json
import jwt
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Configurações do GitHub App
GH_APP_ID = ''
GH_PRIVATE_KEY = ''
GH_API_URL = 'https://api.github.com'

@app.route('/installations/<int:installation_id>/access_tokens', methods=['GET'])
def get_installation_token(installation_id):
    # Gera o JWT
    now = int(time.time())
    payload = {
        'iat': now,
        'exp': now + (10 * 60), # Expira em 10 minutos
        'iss': GH_APP_ID
    }
    jwt_token = jwt.encode(payload, GH_PRIVATE_KEY, algorithm='RS256')

    # Faz uma requisição para obter o token de instalação
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    response = requests.get(f'{GH_API_URL}/app/installations/{installation_id}/access_tokens', headers=headers)

    if response.status_code == 200:
        return response.json()['token']
    else:
        return jsonify({'error': 'Failed to get installation toeken'}), response.status_code
    
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.get_json()

    if 'action' in payload and payload['action'] == 'created':
        issue_title = '[1] Boas-vindas'
        issue_body = "Seja bem-vindo!"
        # Crie a issue aqui usando a API do GitHub
        installation_id = payload['repository']['id']
        token = get_installation_token(installation_id) # Obter o token

        repo_full_name = payload['repository']['full_name'] # Nome completo do repositório
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        issue_data = {
            'title': issue_title,
            'body': issue_body,
        }
        response = requests.post(f'{GH_API_URL}/repos/{repo_full_name}/issues', headers=headers, json=issue_data)

        if response.status_code == 201:
            print('Issue criada com sucesso.')
        else:
            print(f'Falha ao criar a issue: {response.content}')

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(port=5000)