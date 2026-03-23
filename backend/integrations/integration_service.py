import os
import requests
from database.db import SessionLocal
from database.models import Integration

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

def get_token_from_vault(user_context, connection_name):
    """
    Job 2 & 3: Token Retrieval and Auto-Refresh.
    SDK mock that infers userId from session and retrieves the latest active token from Auth0 Vault.
    """
    user_id = user_context["sub"]
    
    mgmt_token = get_management_token()
    if not mgmt_token:
        return None
        
    domain = os.getenv("AUTH0_DOMAIN")
    url = f"https://{domain}/api/v2/users/{user_id}"
    res = requests.get(url, headers={"Authorization": f"Bearer {mgmt_token}"})
    
    if res.status_code == 200:
        user_data = res.json()
        identities = user_data.get("identities", [])
        for identity in identities:
            if identity.get("connection") == connection_name:
                return identity.get("access_token")
    return None

def revoke_token_from_vault(user_context, connection_name):
    """
    Job 6: Token Revocation & Management.
    """
    user_id = user_context["sub"]
    mgmt_token = get_management_token()
    if not mgmt_token:
        return False
        
    domain = os.getenv("AUTH0_DOMAIN")
    provider = connection_name.split("-")[0]
    
    # Auth0 Management API to remove linked identity
    # user_id is the primary ID, we need the secondary user_id from the identity
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
    connection_map = {
        "gmail": "google-oauth2",
        "drive": "google-oauth2",
        "calendar": "google-oauth2",
        "slack": "slack"
    }
    connection_name = connection_map.get(service, service)
    
    # 1. Primary: Try fetching securely from Auth0 Token Vault (Job 2 & 3)
    vault_token = get_token_from_vault(user_context, connection_name)
    if vault_token:
        return vault_token

    # 2. Fallback: Local database if vault is unconfigured
    user_id = user_context["sub"]
    db = SessionLocal()
    integration = db.query(Integration)\
        .filter(
            Integration.user_id == user_id,
            Integration.service == service
        ).first()
    db.close()

    if integration:
        return integration.token_reference

    return None

def save_integration(user_id, service, access_token):
    db = SessionLocal()
    integration = Integration(
        user_id=user_id,
        service=service,
        token_reference=access_token
    )
    db.add(integration)
    db.commit()
    db.close()