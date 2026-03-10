from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
import requests


def send_slack_message(user_context, params, memory=None):

    user_id = user_context["sub"]

    token = get_integration_token(
        user_id,
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