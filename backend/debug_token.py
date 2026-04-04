import os
import sys

# ensure we import from backend
sys.path.append(os.getcwd())

from database.db import SessionLocal
from database.models import User, Integration
from integrations.integration_service import get_management_token
import requests

db = SessionLocal()
users = db.query(User).all()

for u in users:
    print(f"User: {u.id} {u.email}")
    ints = db.query(Integration).filter(Integration.user_id == u.id).all()
    for i in ints:
        print(f"  Integration: {i.service} -> {i.token_reference}")

print("Checking Auth0...")
token = get_management_token()
print("Auth0 Management token length:", len(token) if token else "None")

if token:
    domain = os.environ.get("AUTH0_DOMAIN")
    print(f"Checking Google connection scopes on {domain}...")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"https://{domain}/api/v2/connections", headers=headers)
    if res.status_code == 200:
        conns = res.json()
        for c in conns:
            if c.get("name") == "google-oauth2":
                print("Google OAuth2 scopes:", c.get("options", {}).get("scope", []))
                print("Allowed scopes on connection:", c.get("options", {}).get("allowed_scopes", "Not restricted"))
    else:
        print(f"Error fetching connections: {res.status_code} {res.text}")
