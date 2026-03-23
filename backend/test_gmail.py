import os
from database.db import SessionLocal
from database.models import Integration
import requests

def test_gmail():
    db = SessionLocal()
    integration = db.query(Integration).filter(Integration.service == "gmail").first()
    if not integration:
        print("No gmail integration found in DB!")
        return
        
    token = integration.token_reference
    headers = {"Authorization": f"Bearer {token}"}
    
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    print("Fetching top 50 emails...")
    response = requests.get(url, headers=headers, params={"maxResults": 50, "labelIds": "INBOX"})
    
    data = response.json()
    messages = data.get("messages", [])
    
    print(f"Found {len(messages)} messages.")
    for i, m in enumerate(messages):
        msg_id = m["id"]
        msg_resp = requests.get(f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=metadata", headers=headers)
        if msg_resp.status_code == 200:
            headers_list = msg_resp.json().get("payload", {}).get("headers", [])
            subject = "No Subject"
            sender = "Unknown Sender"
            for h in headers_list:
                if h["name"] == "Subject": subject = h["value"]
                elif h["name"] == "From": sender = h["value"]
            print(f"[{i+1}] {sender} | {subject[:50]}")
        else:
            print(f"[{i+1}] Failed fetch")

if __name__ == "__main__":
    test_gmail()
