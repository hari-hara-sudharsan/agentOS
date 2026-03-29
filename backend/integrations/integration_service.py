import os
import re
import time
import requests
from requests.exceptions import RequestException
from database.db import SessionLocal
from database.models import Integration
from fastapi import HTTPException


from collections import deque

TOKEN_VAULT_CALLS = deque()


def rate_limited(max_per_minute=30):
    def decorator(func):
        def wrapper(*args, **kwargs):
            now = time.time()
            while TOKEN_VAULT_CALLS and TOKEN_VAULT_CALLS[0] < now - 60:
                TOKEN_VAULT_CALLS.popleft()
            if len(TOKEN_VAULT_CALLS) >= max_per_minute:
                raise HTTPException(429, detail="Token Vault call rate limit exceeded")
            TOKEN_VAULT_CALLS.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def retry(tries=3, backoff=0.3, allowed_exceptions=(RequestException,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as exc:
                    attempts += 1
                    if attempts >= tries:
                        raise
                    sleep_time = backoff * (2 ** (attempts - 1))
                    time.sleep(sleep_time)
        return wrapper
    return decorator


SERVICE_CONNECTION_MAP = {
    "gmail": "google-oauth2",
    "drive": "google-oauth2",
    "calendar": "google-oauth2",
    "slack": "slack"
}

SERVICE_SCOPE_MAP = {
    "gmail": "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose",
    "drive": "https://www.googleapis.com/auth/drive.file",
    "calendar": "https://www.googleapis.com/auth/calendar.events",
    "slack": "chat:write channels:read"
}

JWT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


@rate_limited(max_per_minute=30)
@retry(tries=3, backoff=0.3)
def get_management_token():
    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    client_secret = os.getenv("AUTH0_CLIENT_SECRET")

    if not all([domain, client_id, client_secret]):
        return None

    url = f"https://{domain}/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": f"https://{domain}/api/v2/",
        "grant_type": "client_credentials"
    }
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json().get("access_token")
    return None


def _is_raw_token(value: str) -> bool:
    if not value or not isinstance(value, str):
        return False
    if JWT_PATTERN.match(value):
        return True
    if len(value.split(".")) > 2:
        return True
    return False


@rate_limited(max_per_minute=30)
@retry(tries=3, backoff=0.3)
def get_connection_reference(user_context, service):
    """Return non-sensitive provider linkage reference from Auth0 identity."""
    connection_name = SERVICE_CONNECTION_MAP.get(service, service)
    user_id = user_context["sub"]

    mgmt_token = get_management_token()
    if not mgmt_token:
        return None

    domain = os.getenv("AUTH0_DOMAIN")
    url = f"https://{domain}/api/v2/users/{user_id}"
    res = requests.get(url, headers={"Authorization": f"Bearer {mgmt_token}"})
    if res.status_code != 200:
        return None

    for identity in res.json().get("identities", []):
        if identity.get("connection") == connection_name:
            provider = identity.get("provider")
            provider_user_id = identity.get("user_id")
            if provider and provider_user_id:
                return f"{provider}:{provider_user_id}"
    return None


@rate_limited(max_per_minute=30)
@retry(tries=3, backoff=0.3)
def get_token_from_vault(user_context, service):
    """Token Vault exchange path (no raw tokens from local DB)."""
    connection_name = SERVICE_CONNECTION_MAP.get(service, service)
    subject_token = user_context.get("auth0_access_token")

    if not subject_token or _is_raw_token(subject_token) is False:
        # auth0 session token is required for token exchange
        return None

    scope = SERVICE_SCOPE_MAP.get(service)
    if not scope:
        return None

    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    client_secret = os.getenv("AUTH0_CLIENT_SECRET")

    exchange_payload = {
        "grant_type": "urn:auth0:params:oauth:grant-type:token-exchange:federated-connection-access-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "subject_token": subject_token,
        "connection": connection_name,
        "scope": scope,
        "audience": scope
    }

    token_url = f"https://{domain}/oauth/token"
    res = requests.post(token_url, json=exchange_payload, auth=(client_id, client_secret))

    if res.status_code == 200:
        token = res.json().get("access_token")
        if token:
            return token
        raise HTTPException(502, detail="Token Vault exchange succeeded but payload missing access_token")

    if res.status_code == 400:
        print(f"Token Vault exchange invalid request: {res.text}")
    if res.status_code in [401, 403]:
        print(f"Token Vault exchange denied: {res.text}")
    if res.status_code == 429:
        raise HTTPException(429, detail="Token Vault rate limit exceeded")

    # Fallback to explicit identity retrieval from Auth0 vault (management API) only if exchange fails.
    # This path is last-resort and kept for compatibility when Auth0 token exchange is misconfigured.
    mgmt_token = get_management_token()
    if not mgmt_token:
        return None

    user_id = user_context["sub"]
    url = f"https://{domain}/api/v2/users/{user_id}"
    res = requests.get(url, headers={"Authorization": f"Bearer {mgmt_token}"})
    if res.status_code == 200:
        for identity in res.json().get("identities", []):
            if identity.get("connection") == connection_name:
                return identity.get("access_token")

    return None


@rate_limited(max_per_minute=30)
@retry(tries=3, backoff=0.3)
def revoke_token_from_vault(user_context, connection_name):
    """Revoke linked identity from Auth0 to remove any provider tokens."""
    user_id = user_context["sub"]
    mgmt_token = get_management_token()
    if not mgmt_token:
        return False

    domain = os.getenv("AUTH0_DOMAIN")
    provider = connection_name.split("-")[0]

    url = f"https://{domain}/api/v2/users/{user_id}"
    res = requests.get(url, headers={"Authorization": f"Bearer {mgmt_token}"})
    if res.status_code == 200:
        for identity in res.json().get("identities", []):
            if identity.get("connection") == connection_name:
                sec_provider = identity.get("provider")
                sec_user_id = identity.get("user_id")
                del_url = f"https://{domain}/api/v2/users/{user_id}/identities/{sec_provider}/{sec_user_id}"
                requests.delete(del_url, headers={"Authorization": f"Bearer {mgmt_token}"})
                return True
    return False


def get_integration_token(user_context, service):
    token = get_token_from_vault(user_context, service)
    if not token:
        db = SessionLocal()
        user_id = user_context["sub"]
        integration = db.query(Integration).filter(
            Integration.user_id == user_id,
            Integration.service == service
        ).first()
        db.close()
        if integration and integration.token_reference:
            return "auth0-vault-linked"
    return token


def save_integration(user_id, service, connection_reference):
    if not connection_reference or _is_raw_token(connection_reference):
        raise HTTPException(400, detail="Raw tokens are not allowed in integration references")

    db = SessionLocal()
    integration = db.query(Integration).filter(
        Integration.user_id == user_id,
        Integration.service == service
    ).first()

    if integration:
        integration.token_reference = connection_reference
    else:
        integration = Integration(
            user_id=user_id,
            service=service,
            token_reference=connection_reference
        )
        db.add(integration)

    db.commit()
    db.close()
