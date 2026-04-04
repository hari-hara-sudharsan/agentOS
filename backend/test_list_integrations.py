import json
from database.db import SessionLocal
from database.models import Integration

def mock_list_integrations(user_sub):
    services = ["google", "github", "slack", "discord", "microsoft_azure", "salesforce", "linear", "gmail", "drive", "calendar", "pic_tools"]
    result = []
    
    scopes_map = {
        "google": {"name": "Google (Gmail/Drive/Calendar)", "scopes": ["gmail.readonly", "gmail.compose", "drive.file", "calendar.events"]},
        "github": {"name": "GitHub", "scopes": []},
        "slack": {"name": "Slack", "scopes": ["chat:write", "channels:read"]},
        "discord": {"name": "Discord", "scopes": []},
        "microsoft_azure": {"name": "Microsoft/Azure", "scopes": []},
        "salesforce": {"name": "Salesforce", "scopes": []},
        "linear": {"name": "Linear", "scopes": []},
        "gmail": {"name": "Gmail (Read & Send)", "scopes": ["gmail.readonly", "gmail.compose"]},
        "drive": {"name": "Google Drive", "scopes": ["drive.file"]},
        "calendar": {"name": "Google Calendar", "scopes": ["calendar.events"]},
        "pic_tools": {"name": "Pic Tools", "scopes": []}
    }

    db = SessionLocal()
    try:
        for s in services:
            info = scopes_map.get(s, {})
            integration = db.query(Integration).filter(Integration.user_id == user_sub, Integration.service == s).first()
            
            connected = integration is not None
            consent_timestamp = integration.connected_at.isoformat() if connected and integration.connected_at else None

            result.append({
                "service": s,
                "connected": connected,
                "name": info.get("name", s),
                "scopes": info.get("scopes", []),
                "granted_scopes": [], 
                "consent_timestamp": consent_timestamp,
                "description": info.get("description", "")
            })
        print(json.dumps(result, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    mock_list_integrations("google-oauth2|115860559711395850790")
