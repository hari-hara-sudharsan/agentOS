from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
import requests


from security.auth0_client import check_mfa_and_consent

def send_slack_message(user_context, params, memory=None):
    check_mfa_and_consent(user_context, params, tool="send_slack_message")

    token = get_integration_token(
        user_context,
        "slack"
    )

    if not token:
        return {"error": "slack not connected"}

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

    return response.json()


tool_registry.register("send_slack_message", send_slack_message)