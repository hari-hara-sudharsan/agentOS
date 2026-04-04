from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
import requests


from security.auth0_client import check_mfa_and_consent

def send_slack_message(user_context, params, memory=None):
    check_mfa_and_consent(user_context, params, tool="send_slack_message")

    # For Slack, we need to get the direct token from our database
    # (it's stored as xoxb-xxx or xoxp-xxx directly)
    from database.db import SessionLocal
    from database.models import Integration
    
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.user_id == user_context["sub"],
            Integration.service == "slack"
        ).first()
        
        token = integration.token_reference if integration else None
    finally:
        db.close()

    if not token:
        return {
            "error": "slack_not_connected",
            "message": "Slack is not connected. Go to Integrations page and add your Slack Bot Token.",
            "steps": [
                "1. Go to api.slack.com/apps and create an app (or use existing)",
                "2. Go to OAuth & Permissions → Bot Token Scopes → add 'chat:write'",
                "3. Install to workspace and copy 'Bot User OAuth Token' (starts with xoxb-)",
                "4. Paste token in the Integrations page"
            ]
        }

    channel = params.get("channel", "#general")
    message = params.get("message")
    
    if not message and memory:
        message = memory.get("summarize_text")
        
    if not message:
        message = "AgentOS message"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "channel": channel,
        "text": message
    }

    url = "https://slack.com/api/chat.postMessage"

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    if result.get("ok"):
        return {
            "status": "success",
            "channel": channel,
            "message": f"Message sent to {channel}"
        }
    else:
        return {
            "error": "slack_api_error",
            "slack_error": result.get("error"),
            "message": f"Slack API error: {result.get('error')}"
        }


tool_registry.register("send_slack_message", send_slack_message)