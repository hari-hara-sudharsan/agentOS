#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()
from integrations.integration_service import get_integration_token

user_context = {
    'sub': 'google-oauth2|115860559711395850790',
    'auth0_access_token': 'test_token'
}

print('Testing Gmail token retrieval...')
token = get_integration_token(user_context, 'gmail')
print(f'Token: {token[:50] if token else None}...')
print(f'Is placeholder: {token == "auth0-vault-linked" if token else False}')
print(f'Token length: {len(token) if token else 0}')