import os
import re
import time
import requests
from datetime import datetime
from collections import deque
from requests.exceptions import RequestException
from database.db import SessionLocal
from database.models import Integration
from fastapi import HTTPException

TOKEN_VAULT_CALLS = deque()
MANAGEMENT_TOKEN_CACHE = None
MANAGEMENT_TOKEN_EXPIRY = 0

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
    "google": "google-oauth2",
    "gmail": "google-oauth2",
    "drive": "google-oauth2",
    "calendar": "google-oauth2",
    "slack": "slack"
}

SERVICE_SCOPE_MAP = {
    "google": "openid profile email offline_access https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/calendar.events",
    "gmail": "openid profile email offline_access https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose",
    "drive": "openid profile email offline_access https://www.googleapis.com/auth/drive",
    "calendar": "openid profile email offline_access https://www.googleapis.com/auth/calendar.events",
    "slack": "chat:write channels:read"
}

JWT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")

def _is_raw_token(token: str) -> bool:
    """Check if token is a direct provider token (ya29., xox.). JWTs are not 'raw' here."""
    if not token or token == "auth0-vault-linked":
        return False
    # Only treat direct third-party tokens as 'raw' to avoid vault exchange.
    # We do NOT treat JWTs as raw, because we need to EXCHANGE them.
    return token.startswith("ya29.") or token.startswith("xox")

@retry(tries=3, backoff=0.3)
def get_management_token():
    global MANAGEMENT_TOKEN_CACHE, MANAGEMENT_TOKEN_EXPIRY
    now = time.time()
    if MANAGEMENT_TOKEN_CACHE and now < MANAGEMENT_TOKEN_EXPIRY:
        return MANAGEMENT_TOKEN_CACHE

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
        data = res.json()
        MANAGEMENT_TOKEN_CACHE = data.get("access_token")
        MANAGEMENT_TOKEN_EXPIRY = now + 1800 
        return MANAGEMENT_TOKEN_CACHE
    return None

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

@retry(tries=3, backoff=0.3)
def get_token_from_vault(user_context, service):
    """Entry point for retrieving a usable access token."""
    db = SessionLocal()
    try:
        user_id = user_context["sub"]
        integration = db.query(Integration).filter(Integration.user_id == user_id, Integration.service == service).first()
        if integration and _is_raw_token(integration.token_reference):
            t = integration.token_reference
            print(f"DEBUG: Using local DB token for {service} (mask: {t[:4]}...{t[-4:]})")
            return t
    finally:
        db.close()

    # Step 1: Try Token Exchange (Federated)
    subject_token = user_context.get("auth0_access_token")
    if subject_token and not _is_raw_token(subject_token):
        token = exchange_token(user_context, service)
        if token:
            return token

    # Step 2: Try Auth0 Management API Identity Fallback
    # Note: Previously skipped for Google services due to stale tokens issue.
    # Re-enabled with fresh token exchange fix.

    token = fetch_token_from_identities(user_context, service)
    if token:
        # Before returning, try to save it as a local raw token for future use
        save_integration(user_context["sub"], service, token)
        return token

    return None

def exchange_token(user_context, service):
    """Attempt Auth0 Federated Token Exchange via Token Vault."""
    connection_name = SERVICE_CONNECTION_MAP.get(service, service)
    subject_token = user_context.get("auth0_access_token")
    scope = SERVICE_SCOPE_MAP.get(service)
    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    client_secret = os.getenv("AUTH0_CLIENT_SECRET")

    payload = {
        "grant_type": "urn:auth0:params:oauth:grant-type:token-exchange:federated-connection-access-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "requested_token_type": "http://auth0.com/oauth/token-type/federated-connection-access-token",
        "subject_token": subject_token,
        "connection": connection_name,
        "scope": scope
    }
    
    url = f"https://{domain}/oauth/token"
    print(f"DEBUG: Token Vault Exchange - URL={url} connection={connection_name} scope={scope[:50] if scope else 'None'}...")
    try:
        res = requests.post(url, json=payload, auth=(client_id, client_secret), timeout=10)
        print(f"DEBUG: Token Vault Exchange Response - status={res.status_code}")
        if res.status_code == 200:
            token = res.json().get("access_token")
            print(f"DEBUG: Token Vault Exchange SUCCESS - got token (len={len(token) if token else 0})")
            return token
        else:
            print(f"DEBUG: Token Vault Exchange FAILED - {res.status_code}: {res.text[:300]}")
    except Exception as e:
        print(f"DEBUG: Token Vault Exchange EXCEPTION - {str(e)}")
    return None

def fetch_token_from_identities(user_context, service):
    """Retrieve external provider token from Auth0 Management API."""
    mgmt_token = get_management_token()
    if not mgmt_token:
        return None

    domain = os.getenv("AUTH0_DOMAIN")
    user_id = user_context["sub"]
    url = f"https://{domain}/api/v2/users/{user_id}"
    res = requests.get(url, headers={"Authorization": f"Bearer {mgmt_token}"})
    
    if res.status_code == 200:
        connection_name = SERVICE_CONNECTION_MAP.get(service, service)
        for identity in res.json().get("identities", []):
            if identity.get("connection") == connection_name:
                t = identity.get("access_token")
                print(f"DEBUG: Found {service} token in Auth0 Identity (mask: {t[:4]}...{t[-4:]})")
                return t
    return None

def save_integration(user_id, service, token_ref):
    """Save an integration record. If token_ref is 'auth0-vault-linked', try to capture the raw token."""
    db = SessionLocal()
    try:
        # Step: If it's a vault link, try to upgrade it to a raw token immediately
        if token_ref == "auth0-vault-linked":
            user_context = {"sub": user_id}
            raw_token = fetch_token_from_identities(user_context, service)
            if raw_token:
                token_ref = raw_token
                print(f"DEBUG: Successfully upgraded vault-link to raw token for {service}")

        existing = db.query(Integration).filter(Integration.user_id == user_id, Integration.service == service).first()
        if existing:
            existing.token_reference = token_ref
            existing.connected_at = datetime.utcnow()
        else:
            new_item = Integration(user_id=user_id, service=service, token_reference=token_ref)
            db.add(new_item)
        db.commit()
    finally:
        db.close()
    return True

def revoke_token_from_vault(user_context, connection_name):
    """Unlink an identity from the user's Auth0 profile."""
    mgmt_token = get_management_token()
    if not mgmt_token:
        return False

    domain = os.getenv("AUTH0_DOMAIN")
    user_id = user_context["sub"]
    url = f"https://{domain}/api/v2/users/{user_id}"
    res = requests.get(url, headers={"Authorization": f"Bearer {mgmt_token}"})
    if res.status_code == 200:
        for identity in res.json().get("identities", []):
            if identity.get("connection") == connection_name:
                provider = identity.get("provider")
                ident_user_id = identity.get("user_id")
                del_url = f"https://{domain}/api/v2/users/{user_id}/identities/{provider}/{ident_user_id}"
                requests.delete(del_url, headers={"Authorization": f"Bearer {mgmt_token}"})
                return True
    return False

def get_integration_token(user_context, service):
    """High-level function for tools to get a token."""
    token = get_token_from_vault(user_context, service)
    return token
