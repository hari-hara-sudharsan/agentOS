"""
Discord Tool - Send messages via Discord webhook or bot token
"""
from registry.tool_registry import tool_registry
from security.auth0_client import check_mfa_and_consent
import requests


def post_discord_message(user_context, params):
    """Post a message to Discord channel."""
    check_mfa_and_consent(user_context, params, tool="post_discord_message")
    
    from database.db import SessionLocal
    from database.models import Integration
    
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.user_id == user_context["sub"],
            Integration.service == "discord"
        ).first()
        
        webhook_url = integration.token_reference if integration else None
    finally:
        db.close()

    if not webhook_url:
        return {
            "error": "discord_not_connected",
            "message": "Discord is not connected. Add a webhook URL in the Integrations page.",
            "steps": [
                "1. In Discord, go to Server Settings → Integrations → Webhooks",
                "2. Create a new webhook or copy existing webhook URL",
                "3. Paste the webhook URL in the Integrations page"
            ]
        }

    message = params.get("message", "Hello from AgentOS!")
    channel = params.get("channel", "")  # For display purposes only with webhooks

    # Discord webhook format
    payload = {
        "content": message,
        "username": "AgentOS Bot"
    }

    response = requests.post(webhook_url, json=payload)
    
    if response.status_code in [200, 204]:
        return {
            "status": "success",
            "message": f"Message sent to Discord{f' ({channel})' if channel else ''}"
        }
    else:
        return {
            "error": "discord_api_error",
            "status_code": response.status_code,
            "message": response.text
        }


tool_registry.register("post_discord_message", post_discord_message)
